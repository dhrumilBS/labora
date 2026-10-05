// Build: minify CSS/JS and stamp a content hash on their URLs for safe long-term caching.
// Usage: npm install && npm run build
import { readFileSync, writeFileSync, existsSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import CleanCSS from 'clean-css';
import { minify } from 'terser';

const hash = (s) => createHash('sha256').update(s).digest('hex').slice(0, 10);

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

// Blog: its own small stylesheet and script, loaded only on blog pages
const blogCss = new CleanCSS({ level: 2 }).minify(readFileSync('assets/css/blog.css', 'utf8'));
if (blogCss.errors.length) throw new Error(blogCss.errors.join('\n'));
writeFileSync('assets/css/blog.min.css', blogCss.styles);
const blogJs = await minify(readFileSync('assets/js/blog.js', 'utf8'), { compress: true, mangle: true, format: { comments: /^!/ } });
writeFileSync('assets/js/blog.min.js', blogJs.code);

// Every page that loads built assets: homepage, 404, and all blog pages
const blogPages = existsSync('blog')
  ? readdirSync('blog', { recursive: true }).filter((f) => f.endsWith('index.html')).map((f) => join('blog', f))
  : [];
const cssV = hash(css.styles), jsV = hash(js.code), bcV = hash(blogCss.styles), bjV = hash(blogJs.code);
for (const file of ['index.html', '404.html', ...blogPages]) {
  const html = readFileSync(file, 'utf8')
    .replace(/styles\.min\.css(\?v=[a-f0-9]+)?/g, `styles.min.css?v=${cssV}`)
    .replace(/main\.min\.js(\?v=[a-f0-9]+)?/g, `main.min.js?v=${jsV}`)
    .replace(/blog\.min\.css(\?v=[a-f0-9]+)?/g, `blog.min.css?v=${bcV}`)
    .replace(/blog\.min\.js(\?v=[a-f0-9]+)?/g, `blog.min.js?v=${bjV}`);
  writeFileSync(file, html);
}
console.log(`CSS ${(css.styles.length / 1024).toFixed(1)} KB (v=${cssV}), JS ${(js.code.length / 1024).toFixed(1)} KB (v=${jsV}), ` +
  `blog CSS ${(blogCss.styles.length / 1024).toFixed(1)} KB, blog JS ${(blogJs.code.length / 1024).toFixed(1)} KB, pages ${2 + blogPages.length}`);
