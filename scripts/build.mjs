// Build: minify CSS/JS and stamp a content hash on their URLs for safe long-term caching.
// Usage: npm install && npm run build
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { join, dirname, normalize } from 'node:path';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import CleanCSS from 'clean-css';
import { minify } from 'terser';

const hash = (s) => createHash('sha256').update(s).digest('hex').slice(0, 10);
const fileHashes = new Map();
const fileHash = (f) => { if (!fileHashes.has(f)) fileHashes.set(f, hash(readFileSync(f)).slice(0, 8)); return fileHashes.get(f); };

const css = new CleanCSS({ level: 2 }).minify(readFileSync('assets/css/styles.css', 'utf8'));
if (css.errors.length) throw new Error(css.errors.join('\n'));
writeFileSync('assets/css/styles.min.css', css.styles);

const js = await minify(readFileSync('assets/js/main.js', 'utf8'), {
  compress: true, mangle: true, format: { comments: /^!/ }
});
// Lenis (smooth wheel scrolling, MIT) is bundled ahead of main.js so the page still makes one script request.
const lenisPkg = JSON.parse(readFileSync('node_modules/lenis/package.json', 'utf8'));
const lenis = readFileSync('node_modules/lenis/dist/lenis.min.js', 'utf8').replace(/\n?\/\/# sourceMappingURL=.*$/m, '');
js.code = `/*! Lenis ${lenisPkg.version} | MIT License | (c) darkroom.engineering */\n${lenis}\n${js.code}`;
writeFileSync('assets/js/main.min.js', js.code);

// Page bundles: a small stylesheet + script loaded only on the pages that need them
const bundles = {};
for (const name of ['blog', 'pages']) {
  const c = new CleanCSS({ level: 2 }).minify(readFileSync(`assets/css/${name}.css`, 'utf8'));
  if (c.errors.length) throw new Error(c.errors.join('\n'));
  writeFileSync(`assets/css/${name}.min.css`, c.styles);
  const j = await minify(readFileSync(`assets/js/${name}.js`, 'utf8'), { compress: true, mangle: true, format: { comments: /^!/ } });
  writeFileSync(`assets/js/${name}.min.js`, j.code);
  bundles[name] = { css: c.styles, js: j.code };
}

// Every page that loads built assets: homepage, 404, and every generated page folder
const sub = ['blog', 'security', 'faq'].flatMap((dir) => existsSync(dir)
  ? readdirSync(dir, { recursive: true }).filter((f) => f.endsWith('index.html')).map((f) => join(dir, f))
  : []);
const stamp = (html, file, v) => html.replace(new RegExp(file.replaceAll('.', '\\.') + '(\\?v=[a-f0-9]+)?', 'g'), `${file}?v=${v}`);
const cssV = hash(css.styles), jsV = hash(js.code);
for (const file of ['index.html', '404.html', ...sub]) {
  let html = stamp(stamp(readFileSync(file, 'utf8'), 'styles.min.css', cssV), 'main.min.js', jsV);
  for (const [name, b] of Object.entries(bundles)) {
    html = stamp(stamp(html, `${name}.min.css`, hash(b.css)), `${name}.min.js`, hash(b.js));
  }
  // Images and video get a content hash too, so the server can cache them for a year (see deploy/nginx.conf).
  // Only relative URLs are stamped; absolute ones (og:image, JSON-LD) stay stable for crawlers.
  html = html.replace(/(?<![\w/.-])((?:\.\.\/)*assets\/(?:img|video)\/[\w./-]+?\.(?:webp|png|jpe?g|svg|mp4))(?:\?v=[a-f0-9]+)?/g, (m, url) => {
    const disk = normalize(join(dirname(file), url));
    return existsSync(disk) ? `${url}?v=${fileHash(disk)}` : url;
  });
  writeFileSync(file, html);
}

// sitemap.xml: every indexable page, at its canonical URL, with the date it last changed
const today = new Date().toISOString().slice(0, 10);
const lastmod = (file) => {
  try {
    const dirty = execFileSync('git', ['status', '--porcelain', '--', file], { encoding: 'utf8' }).trim();
    return dirty ? today : execFileSync('git', ['log', '-1', '--format=%cs', '--', file], { encoding: 'utf8' }).trim() || today;
  } catch { return today; }
};
const urls = ['index.html', ...sub].map((file) => {
  const html = readFileSync(file, 'utf8');
  if (/<meta name="robots" content="[^"]*noindex/.test(html)) return '';
  const loc = html.match(/<link rel="canonical" href="([^"]+)"/)?.[1];
  return loc ? `  <url><loc>${loc}</loc><lastmod>${lastmod(file)}</lastmod></url>` : '';
}).filter(Boolean);
writeFileSync('sitemap.xml', `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`);
const kb = (s) => (s.length / 1024).toFixed(1) + ' KB';
console.log(`CSS ${kb(css.styles)} (v=${cssV}), JS ${kb(js.code)} (v=${jsV}), ` +
  Object.entries(bundles).map(([n, b]) => `${n} CSS ${kb(b.css)} / JS ${kb(b.js)}`).join(', ') + `, pages ${2 + sub.length}, sitemap ${urls.length} URLs`);
