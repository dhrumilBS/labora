# Labora — Laboratory Management Software landing page

Production-ready static site. Vanilla HTML, CSS, and JavaScript. **Zero runtime dependencies and zero third-party requests**: the Mulish font is self-hosted.

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
assets/fonts/             Mulish variable font, Latin subset (30 KB woff2, preloaded)
assets/img/               og-image.png (1200×630), apple-touch-icon.png, icon-512.png
assets/img/screens/       Product screenshots: WebP at 800/1200/1600/2320 px, phone crops (-m-), JPEG fallback
assets/video/             Product tour: H.264 MP4 at 720p (3.3 MB) and 1080p (5.5 MB), posters (WebP 960/1600, JPEG 1280)
deploy/nginx.conf         Nginx server block: compression, caching, video delivery, security headers
favicon.svg, site.webmanifest, robots.txt, sitemap.xml
_headers                  Netlify / Cloudflare Pages: security + cache headers
vercel.json               Vercel: same headers
.htaccess                 Apache: same headers, compression, 404
scripts/build.mjs         Minifies CSS/JS and stamps content hashes (?v=) on asset URLs
```

## Deploy

The built files are already included, so you can deploy the folder as-is.

- **Netlify / Cloudflare Pages:** drag the folder in, or connect the repo. No build command is needed. `_headers` is picked up automatically.
- **Vercel:** import the folder with framework preset "Other" and no build command. `vercel.json` applies the headers.
- **Apache / cPanel:** upload everything, including `.htaccess`.
- **Nginx (current server):** use `deploy/nginx.conf`. It sets gzip (and Brotli if the module is installed), long-term caching for hashed CSS/JS and fonts, 30-day caching for images and video, efficient large-file delivery for the video, security headers including the CSP, and the 404 page. Do not upload `labora-product-video.mp4` (the 13.7 MB master), `node_modules/`, `scripts/` or `deploy/`.

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

The video section uses click-to-play: the page loads only a small poster image (lazy-loaded), and the video file starts downloading when someone presses play. Screens wider than 1280 physical pixels get 1080p; everything else, and visitors with Data Saver on, get 720p. H.264 MP4 plays in every browser; a VP9 WebM test came out larger for this screen-recording content, so it is not used.

To replace the video, export a 1080p master and re-encode with ffmpeg (`+faststart` lets playback begin before the file finishes downloading):

```
ffmpeg -i master.mp4 -an -vf scale=-2:1080 -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart assets/video/labora-product-1080.mp4
ffmpeg -i master.mp4 -an -vf scale=-2:720  -c:v libx264 -preset slow -crf 26 -pix_fmt yuv420p -movflags +faststart assets/video/labora-product-720.mp4
```

Drop `-an` if a future version has a voice-over, and remove `video.muted = true` in `main.js`. Update `duration` in the `VideoObject` JSON-LD if the length changes.

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
6. **Trusted brands and testimonials (placeholders):** the logo slider (`.brands`) and the `#customers` quotes use sample names and quotes. Replace them with approved customer logos (SVG, single color) and verified quotes with permission, or remove the sections before launch. Keep the two logo lists in the slider identical (the second is the seamless loop copy). Do not add Review or AggregateRating schema for these.
7. **Analytics (optional):** a successful demo request pushes `{ event: "demo_request_submitted" }` to `window.dataLayer` when it exists.

## Accessibility notes

- One H1 and a valid heading outline. Decorative product mockups are `aria-hidden`.
- Keyboard support: skip link, visible focus, dropdowns open with Enter or Space and close with Escape.
- The mobile menu traps focus, sets the page behind it to `inert`, and closes with Escape, returning focus to the toggle.
- Form errors are announced and linked to their fields with `aria-describedby`.
- `prefers-reduced-motion` disables reveal and loop animations. Looping animations pause when off-screen.
