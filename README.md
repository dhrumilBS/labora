# Labora — Laboratory Management Software landing page

Production-ready static site. Vanilla HTML, CSS, and JavaScript. **Zero third-party requests**: the Figtree font is self-hosted, and the only bundled library is Lenis (smooth scrolling, MIT).

## Verified quality (Lighthouse, local server, uncompressed)

| | Performance | Accessibility | Best practices | SEO | LCP | TBT | CLS |
|---|---|---|---|---|---|---|---|
| Mobile | 99 | 100 | 100 | 100 | 1.8 s | 30 ms | 0 |
| Desktop | 100 | 100 | 100 | 100 | 0.5 s | 0 ms | 0 |

HTML passes `html-validate` (recommended rules). Expect faster numbers in production with gzip/brotli from your host.

## Structure

```
index.html                Page, SEO meta, Open Graph, JSON-LD (Organization, WebSite, WebPage, SoftwareApplication, FAQPage)
404.html                  Not-found page
assets/css/styles.css     Source styles (design tokens at the top)
assets/css/styles.min.css Built, minified (what the page loads)
assets/js/main.js         Source script
assets/js/main.min.js     Built, minified (what the page loads, deferred)
assets/fonts/             Figtree variable font (weights 300-900), subset to Latin-1 + typographic punctuation (17 KB woff2, preloaded)
assets/img/               og-image.png (1200×630), apple-touch-icon.png, icon-512.png
assets/img/screens/       Product screenshots: WebP only, at 800/1200/1600/2320 px plus phone crops (-m-); every current browser supports WebP
assets/video/             Product tour v3: original 1080p stream (9.6 MB, no re-encode) and 720p for phones (4.9 MB), posters
deploy/nginx.conf         Nginx server block (current server): compression, caching, video delivery, security headers
favicon.svg, site.webmanifest, robots.txt, sitemap.xml
_headers                  Netlify / Cloudflare Pages: security + cache headers
vercel.json               Vercel: same headers
.htaccess                 Apache: index, 404 (root or /labora/ subfolder), HTML no-cache, compression; production headers commented
scripts/build.mjs         Minifies CSS/JS and stamps content hashes (?v=) on asset URLs
```

## Deploy

The built files are already included, so you can deploy the folder as-is.

- **Netlify / Cloudflare Pages:** drag the folder in, or connect the repo. No build command is needed. `_headers` is picked up automatically.
- **Vercel:** import the folder with framework preset "Other" and no build command. `vercel.json` applies the headers.
- **Apache / cPanel:** upload everything, including `.htaccess`.
- **Nginx (current server):** use `deploy/nginx.conf`. It carries the same headers as `_headers`, plus gzip (Brotli if the module is installed), caching, and large-file settings for the video. Do not upload `node_modules/`, `scripts/`, `deploy/`, or `archive/`.

## Product screenshots

Each screenshot is served with `<picture>`: phones get a tighter crop of the key area so the UI stays readable, and larger screens get the full image at the right resolution. Only the hero image loads immediately; the rest load lazily as you scroll. To replace a screenshot, keep the same file names and sizes, or regenerate all the sizes and crops.

| Section | Screenshot | Phone crop shows |
|---|---|---|
| Hero | dashboard | KPI cards and patient-case trend |
| Step 1, Collect | home-collection | Visit cards with status and ETA |
| Step 2, Track | sample-tracking | Barcode match and sample timeline |
| Step 3, Monitor | turnaround-tracking | At-risk counts and elapsed vs. target |
| Step 4, Report | pathology-imaging-reporting | The drafted report with sign and send |
| Step 5, Grow | business-insights | Revenue by center |

## Product tour video

The tour plays muted, looped, and without browser controls; a single play/pause button sits in the corner (the video has no audio track, so there is no volume control). To protect page speed, only the lazy-loaded poster loads with the page. The video file is requested after the page has loaded, on the visitor's first scroll, tap, or key press (or 3.5 s after load), and only once the frame is on screen. It pauses when scrolled away. Desktop and tablet get the original 1080p stream untouched (full clarity); phone-width screens and Data Saver users get 720p. With reduced motion or Data Saver on, it does not autoplay; the button starts it.

All site assets live in `assets/` (css, js, fonts, img, video). `assets/video/labora-tour-v3-1080.mp4` is the original 1080p stream, so no separate master file is kept. To replace the video, encode a new 1080p master with ffmpeg (`+faststart` lets playback start before the download finishes):

```
ffmpeg -i master.mp4 -map 0:v:0 -c copy -an -movflags +faststart assets/video/labora-tour-v4-1080.mp4
ffmpeg -i master.mp4 -an -vf scale=-2:720 -c:v libx264 -preset slow -crf 20 -tune stillimage -pix_fmt yuv420p -movflags +faststart assets/video/labora-tour-v4-720.mp4
```

Then update the poster images and `duration` in the `VideoObject` JSON-LD. Because `/assets/*` is cached for a year as immutable, give replacement files new names (for example `-v2`) and update the references.

## Smooth scrolling

Desktop mouse and trackpad scrolling is eased with [Lenis](https://github.com/darkroomengineering/lenis) (MIT, ~5 KB gzipped). It is bundled into `main.min.js` by the build, so there is no extra request, and it starts after page load. Touch devices keep native scrolling, and it is off when the visitor prefers reduced motion. Anchor links honour the CSS `scroll-padding-top` that clears the sticky header.

## Blog

- `blog/index.html` is the hub: featured story, topic filters, search (press `/`), article grid, "Most read" list, newsletter, pagination.
- `blog/how-to-cut-lab-turnaround-time/index.html` is the article template: reading progress, sticky table of contents with the current section highlighted, takeaways, callouts, a data table, an inline demo CTA, author card, related articles, and BlogPosting + BreadcrumbList JSON-LD.
- Both pages are generated by `scripts/build-blog.py`, which copies the header, mobile menu, icon sprite, and footer from `index.html`, so the blog always matches the homepage. Edit posts in that script, then run `python scripts/build-blog.py && npm run build`.
- Blog-only assets: `assets/css/blog.css` and `assets/js/blog.js` (minified by the build into `blog.min.css` / `blog.min.js`).
- The newsletter form runs in demo mode until you set `data-endpoint` on `form[data-newsletter]`.
- Sample content: only the turnaround article exists; the other cards link to it until their pages are written. The author is "Labora Team" (no individual bylines are invented).

## Editing

1. Edit `assets/css/styles.css` or `assets/js/main.js`. Never edit the `.min` files by hand.
2. Run `npm install` once, then `npm run build`. This regenerates the minified files and updates the `?v=` hashes in the HTML, so the one-year immutable cache stays safe.
3. Optionally run `npm run validate` to check the HTML, and `npm run serve` to preview locally.

## Launch checklist

1. **Domain:** replace `https://www.labora.example` in `index.html` (canonical, Open Graph, JSON-LD), `robots.txt`, and `sitemap.xml`.
2. **Demo form:** set `data-endpoint` on `<form id="demo-form">` to your form handler. It POSTs `FormData` and expects a 2xx response. Without an endpoint it runs in demo mode and only shows the confirmation. Spam protection is a hidden honeypot field (`website`).
3. **CSP:** if the form endpoint or an analytics tool lives on another domain, add that domain to `connect-src` (and `script-src` for analytics) in `_headers`, `vercel.json`, or `.htaccess`. Otherwise the browser will block it. The inline `js` class script is allowed by its SHA-256 hash; if you change that one line, recompute the hash.
4. **Internal links:** `/platform/...`, `/solutions/...`, `/pricing/`, `/login/`, `/signup/`, `/contact/`, `/privacy/`, `/terms/`, and `/cookies/` must exist.
5. **Content truth check:** the page now follows what the product screenshots show. Still confirm the integration categories (analyzers, imaging systems, SMS, HIS/EMR, accounting) and security capabilities with the product team. The page claims no certifications, customer counts, or performance statistics. Dashboard numbers are illustrative product UI.
6. **Trusted brands and testimonials (placeholders):** the logo slider (`.brands`) uses invented lab names and the `#customers` quotes are sample text. Replace them with approved customer logos (single-color SVG) and verified quotes used with permission, or remove both sections before launch. Keep the two logo lists in the slider identical (the second is the seamless-loop copy). Do not add Review or AggregateRating schema for them.
7. **Analytics (optional):** a successful demo request pushes `{ event: "demo_request_submitted" }` to `window.dataLayer` when it exists.

## Accessibility notes

- One H1 and a valid heading outline. Decorative product mockups are `aria-hidden`.
- Keyboard support: skip link, visible focus, dropdowns open with Enter or Space and close with Escape.
- The mobile menu traps focus, sets the page behind it to `inert`, and closes with Escape, returning focus to the toggle.
- Form errors are announced and linked to their fields with `aria-describedby`.
- `prefers-reduced-motion` disables reveal and loop animations. Looping animations pause when off-screen.
