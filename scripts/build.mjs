// Build: minify CSS/JS and stamp a content hash on their URLs for safe long-term caching.
// Usage: npm install && npm run build
import { readFileSync, writeFileSync } from 'node:fs';
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
writeFileSync('assets/js/main.min.js', js.code);

const cssV = hash(css.styles), jsV = hash(js.code);
for (const file of ['index.html', '404.html']) {
  const html = readFileSync(file, 'utf8')
    .replace(/styles\.min\.css(\?v=[a-f0-9]+)?/g, `styles.min.css?v=${cssV}`)
    .replace(/main\.min\.js(\?v=[a-f0-9]+)?/g, `main.min.js?v=${jsV}`);
  writeFileSync(file, html);
}
console.log(`CSS ${(css.styles.length / 1024).toFixed(1)} KB (v=${cssV}), JS ${(js.code.length / 1024).toFixed(1)} KB (v=${jsV})`);
