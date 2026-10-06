"""Generate the blog hub and article pages from one template.

Shared chrome (icon sprite, floating header, mobile menu, footer) comes from scripts/site.py,
which copies it from index.html, so the blog always matches the homepage. Run after editing posts or the homepage chrome:
    python scripts/build-blog.py && npm run build
"""
import io, os, re, html, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_chrome as shared          # shared header/menu/footer/sprite for generated pages
ROOT, SITE = shared.ROOT, shared.SITE

# ---------------------------------------------------------------------------
# Posts (sample entries; every card links to the article template for now)
# ---------------------------------------------------------------------------
ARTICLE_SLUG = "how-to-cut-lab-turnaround-time"
POSTS = [
    dict(slug=ARTICLE_SLUG, topic="turnaround", label="Turnaround time", img="turnaround-tracking", tone="ink",
         title="How to cut turnaround time in a diagnostic lab",
         excerpt="A practical guide to measuring TAT the same way every time, finding where the hours really go, and catching delays before the doctor calls.",
         date="Oct 5, 2026", iso="2026-10-05", read=9),
    dict(slug="barcode-sample-tracking", topic="operations", label="Lab operations", img="sample-tracking", tone="mint",
         title="Barcode sample tracking, from front desk to rack slot",
         excerpt="What to scan, when to scan it, and how a single tube record ends the daily hunt for a missing sample.",
         date="Sep 29, 2026", iso="2026-09-29", read=7),
    dict(slug="home-collection-patients-trust", topic="home-collection", label="Home collection", img="home-collection", tone="cream",
         title="Home sample collection patients actually trust",
         excerpt="Live arrival times, clear prep instructions, and handoffs that keep samples moving from the doorstep to the bench.",
         date="Sep 22, 2026", iso="2026-09-22", read=6),
    dict(slug="pathology-and-radiology-in-one-system", topic="reporting", label="Reporting", img="pathology-imaging-reporting", tone="soft",
         title="Pathology and radiology in one system: what changes for reporting doctors",
         excerpt="Why one patient case across lab and imaging makes review, sign-off, and delivery faster for everyone involved.",
         date="Sep 15, 2026", iso="2026-09-15", read=8),
    dict(slug="revenue-by-center-and-referrer", topic="growth", label="Business growth", img="business-insights", tone="mint",
         title="Reading your revenue by center, day, and referring doctor",
         excerpt="The handful of numbers a lab owner should check every week, and what each one tells you to do next.",
         date="Sep 8, 2026", iso="2026-09-08", read=6),
    dict(slug="digital-signatures-for-lab-reports", topic="reporting", label="Reporting", img="pathology-imaging-reporting", tone="cream", right=True,
         title="Digital signatures for lab reports: what to set up first",
         excerpt="Roles, review steps, and release rules that let doctors sign with confidence and send reports in one click.",
         date="Sep 1, 2026", iso="2026-09-01", read=5),
    dict(slug="product-update-ultrasound-templates", topic="product", label="Product updates", img="dashboard", tone="soft",
         title="Product update: ultrasound templates and faster sign-off",
         excerpt="A tour of the new template library for ultrasound, X-ray, CT, and MRI, plus quicker review and signing.",
         date="Aug 25, 2026", iso="2026-08-25", read=3),
    dict(slug="choosing-laboratory-management-software", topic="guides", label="Buyer guides", img="dashboard", tone="cream", right=True,
         title="Choosing laboratory management software: a buyer checklist for 2026",
         excerpt="The questions to ask about sample tracking, reporting, integrations, data migration, and rollout before you sign.",
         date="Aug 18, 2026", iso="2026-08-18", read=10),
]
TOPICS = [("all", "All"), ("turnaround", "Turnaround time"), ("operations", "Lab operations"), ("home-collection", "Home collection"),
          ("reporting", "Reporting"), ("growth", "Business growth"), ("product", "Product updates"), ("guides", "Buyer guides")]

def img_tag(prefix, name, sizes, eager=False, alt=""):
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    # 480w/640w let phones and 1x laptops skip the 800w file; 1200w covers 2x screens
    srcset = ", ".join(f"{prefix}assets/img/screens/{name}-{w}.webp {w}w" for w in (480, 640, 800, 1200))
    return (f'<img src="{prefix}assets/img/screens/{name}-800.webp" srcset="{srcset}" sizes="{sizes}" width="800" height="690" alt="{html.escape(alt)}" {load}>')

PER_PAGE = 12  # articles per hub page before pagination appears

def pager(n):
    # Every article fits on one page for now, so no pagination links (links to pages that don't exist hurt crawling).
    # When there are more than PER_PAGE articles, generate /blog/page/2/ etc. and link them here.
    if n <= PER_PAGE: return ""
    raise SystemExit(f"{n} articles: add paginated hub pages (/blog/page/N/) before publishing more than {PER_PAGE}")

def cover(prefix, p, sizes, eager=False, extra=""):
    right = " cover--right" if p.get("right") else ""
    return f'<div class="cover cover--{p["tone"]}{right}{extra}">{img_tag(prefix, p["img"], sizes, eager)}</div>'

def byline(read, date, iso):
    return (f'<span class="byline"><span class="avatar" aria-hidden="true"><svg><use href="#logo-mark"/></svg></span>'
            f'<span><strong>Labora Team</strong><span><time datetime="{iso}">{date}</time> · {read} min read</span></span></span>')

def card(prefix, p, href, sizes="(max-width: 720px) calc(100vw - 40px), (max-width: 1024px) 46vw, 380px"):
    return f'''<a class="post reveal" href="{href}" data-topic="{p["topic"]}">
          {cover(prefix, p, sizes)}
          <span class="meta"><span>{p["label"]}</span><span class="dot-sep" aria-hidden="true"></span><span>{p["read"]} min read</span></span>
          <h3>{html.escape(p["title"])}</h3>
          <p>{html.escape(p["excerpt"])}</p>
          {byline(p["read"], p["date"], p["iso"])}
        </a>'''

def newsletter():
    return '''<section class="newsletter reveal" aria-labelledby="nl-title">
      <div>
        <h2 id="nl-title">Lab operations, in your inbox</h2>
        <p>One practical email a month on turnaround, sample tracking, reporting, and growing a multi-center lab. No spam, unsubscribe anytime.</p>
      </div>
      <div>
        <!-- Set data-endpoint to your email platform's form handler. Without it, the form validates and confirms only. -->
        <form class="nl-form" data-newsletter data-endpoint="" novalidate>
          <label class="sr-only" for="nl-email">Work email</label>
          <input id="nl-email" name="email" type="email" autocomplete="email" placeholder="you@yourlab.com" required>
          <button class="btn btn--lg" type="submit">Subscribe</button>
        </form>
        <p class="nl-msg" role="status" aria-live="polite"></p>
        <p class="nl-note">By subscribing, you agree to our <a href="/privacy/" style="color:inherit">privacy policy</a>.</p>
      </div>
    </section>'''

def page(prefix, title, desc, canonical, og_image, jsonld, body, hub_href=None, og_alt=shared.OG_ALT):
    og_type = 'article' if 'BlogPosting' in jsonld and '"@type": "Blog"' not in jsonld else 'website'
    return shared.page(prefix, 'blog', title, desc, canonical, og_image, jsonld, body,
                       css=('blog.min.css',), js=('blog.min.js',), og_type=og_type, og_alt=og_alt)

# ---------------------------------------------------------------------------
# Hub: /blog/
# ---------------------------------------------------------------------------
def build_hub():
    prefix = "../"
    art = f"{ARTICLE_SLUG}/"
    feat, rest = POSTS[0], POSTS[1:]
    chips = '\n          '.join(f'<button class="topic" type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{v}</button>' for k, v in TOPICS)
    cards = [card(prefix, p, art) for p in rest]
    most = '\n          '.join(f'<li><a href="{art}"><span>{html.escape(p["title"])}<small>{p["label"]} · {p["read"]} min</small></span></a></li>' for p in [POSTS[0], POSTS[1], POSTS[7], POSTS[3], POSTS[2]])
    most_read = f'''<aside class="most-read" aria-labelledby="mr-title">
          <h2 id="mr-title">Most read this month</h2>
          <ol>
          {most}
          </ol>
        </aside>'''
    grid_items = cards[:2] + [most_read] + cards[2:]
    grid = '\n        '.join(grid_items)
    body = f'''<section class="blog-hero" aria-labelledby="blog-title">
  <div class="container">
    <p class="eyebrow"><span class="dot" aria-hidden="true"></span>The Labora Journal</p>
    <h1 id="blog-title">Ideas for running a faster, calmer diagnostic lab</h1>
    <p class="lead">Practical guides on turnaround time, sample tracking, reporting, and growth, written for lab owners, managers, and reporting doctors.</p>
    <div class="blog-tools">
      <div class="topics" role="group" aria-label="Filter by topic">
          {chips}
      </div>
      <div class="search" role="search">
        <label class="sr-only" for="blog-search">Search articles</label>
        <svg class="icon" aria-hidden="true"><use href="#i-search"/></svg>
        <input id="blog-search" type="search" placeholder="Search articles" autocomplete="off">
        <kbd aria-hidden="true">/</kbd>
      </div>
    </div>
  </div>
</section>

<div class="container">
  <!-- Sample entries: every card links to the article template until the other posts exist. -->
  <a class="featured reveal" href="{art}" data-featured>
    {cover(prefix, feat, "(max-width: 1024px) calc(100vw - 40px), 640px", eager=True)}
    <div class="featured-body">
      <div class="chips"><span class="chip badge-new">Featured</span><span class="chip">{feat["label"]}</span></div>
      <h2>{html.escape(feat["title"])}</h2>
      <p>{html.escape(feat["excerpt"])}</p>
      {byline(feat["read"], feat["date"], feat["iso"])}
      <span class="link-arrow">Read the guide <svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow"/></svg></span>
    </div>
  </a>

  <section aria-labelledby="latest-title">
    <div class="posts-head">
      <h2 id="latest-title">Latest articles</h2>
      <span class="count" data-count aria-live="polite">{len(rest)} articles</span>
    </div>
    <div class="post-grid" data-posts>
        {grid}
    </div>
    <div class="empty" data-empty>
      <h3>No articles match that search</h3>
      <p>Try another word, or browse every topic.</p>
      <button class="btn btn--ghost" type="button" data-reset>Show all articles</button>
    </div>
    {pager(len(rest))}
  </section>

  {newsletter()}
</div>'''
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Blog", "@id": f"{SITE}/blog/#blog", "name": "The Labora Journal", "url": f"{SITE}/blog/",
             "description": "Guides on turnaround time, sample tracking, reporting, and growth for diagnostic labs.",
             "publisher": {"@type": "Organization", "name": "Labora", "url": f"{SITE}/"},
             "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "datePublished": p["iso"], "url": f"{SITE}/blog/{p['slug']}/"} for p in POSTS]},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"}]}]
    }, indent=1, ensure_ascii=False)
    out = page(prefix, "Lab Management Blog: Guides for Diagnostic Labs | Labora",
               "Practical guides on lab turnaround time, barcode sample tracking, pathology and radiology reporting, home collection, and growing a multi-center diagnostic lab.",
               f"{SITE}/blog/", f"{SITE}/assets/img/og-image.png", jsonld, body, "./")
    os.makedirs(os.path.join(ROOT, "blog"), exist_ok=True)
    io.open(os.path.join(ROOT, "blog", "index.html"), "w", encoding="utf-8", newline="").write(out)

# ---------------------------------------------------------------------------
# Article: /blog/how-to-cut-lab-turnaround-time/
# ---------------------------------------------------------------------------
SECTIONS = [
    ("why-tat-matters", "Why turnaround time matters"),
    ("measure-tat", "Measure TAT the same way every time"),
    ("set-targets", "Set targets by test, not one number"),
    ("find-delays", "Find where the hours actually go"),
    ("fix-handoffs", "Fix the handoffs"),
    ("catch-delays", "Catch delays before they happen"),
    ("deliver-faster", "Make sign-off and delivery instant"),
    ("review-weekly", "Review it every week"),
]

def build_article():
    prefix = "../../"
    p = POSTS[0]
    toc = '\n          '.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in SECTIONS)
    related = [POSTS[1], POSTS[3], POSTS[4]]
    rel_cards = '\n        '.join(card(prefix, r, "./", "(max-width: 720px) calc(100vw - 40px), (max-width: 1024px) 46vw, 380px") for r in related)
    figure_img = (f'<img src="{prefix}assets/img/screens/turnaround-tracking-1200.webp" srcset="{prefix}assets/img/screens/turnaround-tracking-480.webp 480w, {prefix}assets/img/screens/turnaround-tracking-640.webp 640w, {prefix}assets/img/screens/turnaround-tracking-800.webp 800w, '
                  f'{prefix}assets/img/screens/turnaround-tracking-1200.webp 1200w" sizes="(max-width: 760px) calc(100vw - 40px), 720px" width="1200" height="1034" '
                  f'alt="Labora turnaround view: cases at risk and past target, with elapsed time against each target" loading="lazy" decoding="async" style="border-radius:20px">')
    body = f'''<div class="read-progress" aria-hidden="true"><span></span></div>

<article data-article>
  <header class="article-hero">
    <div class="container">
      <div class="wrap">
        <nav class="crumbs" aria-label="Breadcrumb">
          <a href="{prefix}">Home</a><svg class="icon" aria-hidden="true"><use href="#i-chev"/></svg>
          <a href="../">Blog</a><svg class="icon" aria-hidden="true"><use href="#i-chev"/></svg>
          <span aria-current="page">{p["label"]}</span>
        </nav>
        <span class="chip">{p["label"]}</span>
        <h1 style="margin-top:1rem">{html.escape(p["title"])}</h1>
        <p class="dek">{html.escape(p["excerpt"])}</p>
        <div class="article-bar">
          {byline(p["read"], p["date"], p["iso"])}
          <div class="share">
            <span class="share-label">Share</span>
            <a href="https://www.linkedin.com/sharing/share-offsite/?url={SITE}/blog/{p['slug']}/" target="_blank" rel="noopener" aria-label="Share on LinkedIn"><svg class="brand" aria-hidden="true"><use href="#b-linkedin"/></svg></a>
            <a href="https://x.com/intent/post?url={SITE}/blog/{p['slug']}/" target="_blank" rel="noopener" aria-label="Share on X"><svg class="brand" aria-hidden="true"><use href="#b-x"/></svg></a>
            <button type="button" data-copy-link aria-label="Copy link"><svg class="icon" aria-hidden="true"><use href="#i-link"/></svg></button>
          </div>
        </div>
      </div>
      <div class="article-cover">
        {cover(prefix, p, "(max-width: 1260px) calc(100vw - 40px), 1200px", eager=True)}
      </div>
    </div>
  </header>

  <div class="container article-layout">
    <details class="toc" open>
      <summary>On this page <svg class="icon icon-sm" aria-hidden="true"><use href="#i-chev"/></svg></summary>
      <ol>
          {toc}
      </ol>
      <div class="toc-cta">
        <strong>See TAT tracking live</strong>
        Watch elapsed time against target for every case in your lab.
        <a class="link-arrow" href="{prefix}#demo">Book a demo <svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow"/></svg></a>
      </div>
    </details>

    <div class="prose">
      <section class="takeaways" aria-labelledby="takeaways-title">
        <h2 id="takeaways-title"><svg class="icon" aria-hidden="true"><use href="#i-zap"/></svg>Key takeaways</h2>
        <ul>
          <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>Define one start and stop point for TAT, and split it into pre-analytical, analytical, and post-analytical time.</li>
          <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>Set a target per test and priority, not one number for the whole lab.</li>
          <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>Timestamp every handoff with a barcode scan so you can see where time is lost.</li>
          <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>Alert the team when a case is at risk, not after it is already late.</li>
          <li><svg class="icon" aria-hidden="true"><use href="#i-check"/></svg>Review on-time rate and delay reasons weekly, by test and by center.</li>
        </ul>
      </section>

      <h2 id="why-tat-matters">Why turnaround time matters</h2>
      <p>For a patient, turnaround time is how long they wait to hear what is wrong. For a referring doctor, it decides whether a treatment starts today or tomorrow. For your lab, it is one of the few numbers both groups notice without being told, and one of the first reasons a doctor sends samples somewhere else.</p>
      <p>The good news: most delays are not in the analyzer. They hide in the handoffs between the front desk, phlebotomy, the bench, review, and delivery. That makes turnaround one of the most fixable problems in a diagnostic lab, as long as you can see it.</p>

      <h2 id="measure-tat">Measure TAT the same way every time</h2>
      <p>If the front desk measures from registration and the lab measures from receipt, you will argue about numbers instead of fixing delays. Pick one definition, write it down, and measure every case against it.</p>
      <p>A common starting point is <strong>registration to signed report</strong>, split into three phases so you can see which one is slipping:</p>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th scope="col">Phase</th><th scope="col">Starts</th><th scope="col">Ends</th><th scope="col">Typical delays</th></tr></thead>
          <tbody>
            <tr><td>Pre-analytical</td><td>Patient registered</td><td>Sample received in lab</td><td>Collection queues, home visits, transport, labeling errors</td></tr>
            <tr><td>Analytical</td><td>Sample received</td><td>Result entered</td><td>Batching, reruns, instrument downtime, missing reagents</td></tr>
            <tr><td>Post-analytical</td><td>Result entered</td><td>Report signed and sent</td><td>Waiting for review, manual typing, sign-off, delivery</td></tr>
          </tbody>
        </table>
      </div>
      <div class="callout">
        <span class="c-icon" aria-hidden="true"><svg class="icon"><use href="#i-clock"/></svg></span>
        <div><strong>Tip: count calendar time, not working hours</strong>Patients and doctors experience the clock, not your shift schedule. Report calendar time, and track working-hours time separately if you need it for staffing.</div>
      </div>

      <h2 id="set-targets">Set targets by test, not one number</h2>
      <p>A single lab-wide target hides the problem. A routine lipid profile, an urgent troponin, and an ultrasound report have very different expectations, so give each test, or test group, its own target, with a separate target for urgent priority.</p>
      <ul>
        <li><strong>Start from what doctors expect today.</strong> Ask your top referrers what "on time" means for the tests they order most.</li>
        <li><strong>Separate routine from urgent.</strong> Urgent cases should carry their own, shorter target and move to the front of every queue.</li>
        <li><strong>Make targets visible.</strong> A target the bench cannot see on every case is a target nobody is working toward.</li>
      </ul>

      <h2 id="find-delays">Find where the hours actually go</h2>
      <p>You cannot fix what you cannot see. The fastest way to see it is to timestamp every handoff: registration, collection, receipt in the lab, rack placement, result entry, review, signature, and delivery. A barcode scan at each step does this automatically, without asking anyone to write down times.</p>
      <figure>
        {figure_img}
        <figcaption>Every case carries a target. Green is on time, amber is at risk, and red is past target, so the team knows what to do next.</figcaption>
      </figure>
      <p>Once the timestamps exist, sort cases by the longest phase. Patterns appear quickly: one collection center that batches transport twice a day, one test that waits for a weekly run, one reviewer who signs everything in the evening.</p>

      <aside class="inline-cta" aria-label="Book a demo">
        <div>
          <h3>See where your lab loses time</h3>
          <p>Book a 20-minute demo set up with your own tests, and see elapsed time against target for every case.</p>
        </div>
        <a class="btn btn--lg" href="{prefix}#demo">Book a demo</a>
      </aside>

      <h2 id="fix-handoffs">Fix the handoffs</h2>
      <p>With the delays visible, most fixes are operational, not technical. Work through the phases in order:</p>
      <ol>
        <li><strong>Label at the point of collection.</strong> Print the barcode when the sample is drawn, so tubes never arrive unlabeled or mismatched.</li>
        <li><strong>Move transport to a schedule.</strong> Fixed pickup times from each collection point beat "when the rider is free."</li>
        <li><strong>Give every tube a home.</strong> Scanning a sample into a rack slot ends the search through refrigerators when a doctor calls.</li>
        <li><strong>Record why samples are held or rejected.</strong> A reason on every rejection turns a recurring problem into something you can fix at the source.</li>
      </ol>
      <blockquote>The analyzer is rarely the bottleneck. The wait is almost always in the handoff between two people.</blockquote>

      <h2 id="catch-delays">Catch delays before they happen</h2>
      <p>A report that is already late can only be apologized for. A report that is at risk can still be saved. Set an alert when a case reaches a share of its target, for example three quarters of the way, and send it to the person who can act: the bench lead for analytical delays, the reviewer for sign-off delays.</p>
      <p>Keep the at-risk list short and visible on a shared screen. The goal is a team that clears amber cases before they turn red, not a dashboard that only reports how many went late yesterday.</p>

      <h2 id="deliver-faster">Make sign-off and delivery instant</h2>
      <p>Post-analytical time is often the easiest to cut, because it is mostly waiting and typing. Three changes make the biggest difference:</p>
      <ul>
        <li><strong>Report templates</strong> for each modality and test, so doctors complete findings instead of typing whole reports.</li>
        <li><strong>Digital signatures</strong> with clear review rules, so an approved report is released immediately.</li>
        <li><strong>Automatic delivery</strong> of the signed PDF to the patient and the referring doctor, so nobody has to call to ask whether it is ready.</li>
      </ul>

      <h2 id="review-weekly">Review it every week</h2>
      <p>Turnaround improves when someone owns the number. Put a 20-minute review on the calendar each week and walk through the same short checklist:</p>
      <ul class="checklist">
        <li>On-time rate overall, and for urgent cases on their own</li>
        <li>The five tests with the most late cases, and the phase where they slipped</li>
        <li>On-time rate by collection center and by reviewer</li>
        <li>The most common delay and rejection reasons this week</li>
        <li>One change to try before next week's review</li>
      </ul>
      <p>Small, steady changes compound. A lab that reviews turnaround weekly, and fixes one handoff at a time, gets faster month after month, and referring doctors notice.</p>

      <footer class="article-foot">
        <div class="tags"><span>Topics</span><a class="chip chip--soft" href="../">Turnaround time</a><a class="chip chip--soft" href="../">Lab operations</a><a class="chip chip--soft" href="../">Reporting</a></div>
        <div class="author-card">
          <span class="avatar" aria-hidden="true"><svg><use href="#logo-mark"/></svg></span>
          <div>
            <h3>Labora Team</h3>
            <div class="role">Product and lab operations</div>
            <p>We build Labora with pathology, imaging, and multi-center labs, and write about what we learn running faster, calmer labs.</p>
          </div>
        </div>
        <nav class="post-nav" aria-label="More articles">
          <a href="./"><small>Previous</small>{html.escape(POSTS[7]["title"])}</a>
          <a href="./"><small>Next</small>{html.escape(POSTS[1]["title"])}</a>
        </nav>
      </footer>
    </div>
  </div>
</article>

<div class="container">
  <section class="related" aria-labelledby="related-title">
    <div class="posts-head"><h2 id="related-title">Keep reading</h2><a class="link-arrow" href="../">All articles <svg class="icon icon-sm" aria-hidden="true"><use href="#i-arrow"/></svg></a></div>
    <div class="post-grid">
        {rel_cards}
    </div>
  </section>

  {newsletter()}
</div>

<div class="toast" role="status" aria-live="polite"></div>'''
    url = f"{SITE}/blog/{p['slug']}/"
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BlogPosting", "@id": f"{url}#article", "headline": p["title"], "description": p["excerpt"],
             "image": [f"{SITE}/assets/img/og/{p['slug']}.jpg", f"{SITE}/assets/img/screens/turnaround-tracking-1200.webp"], "datePublished": p["iso"], "dateModified": p["iso"],
             "author": {"@type": "Organization", "name": "Labora Team", "url": f"{SITE}/"},
             "publisher": {"@type": "Organization", "name": "Labora", "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/img/icon-512.png"}},
             "mainEntityOfPage": url, "articleSection": p["label"], "wordCount": 1250,
             "keywords": "lab turnaround time, TAT, diagnostic lab operations, laboratory management software"},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
                {"@type": "ListItem", "position": 3, "name": p["title"], "item": url}]}]
    }, indent=1, ensure_ascii=False)
    out = page(prefix, "How to Cut Lab Turnaround Time (TAT): A Practical Guide | Labora", p["excerpt"], url,
               f"{SITE}/assets/img/og/{p['slug']}.jpg", jsonld, body, "../",
               og_alt="Labora turnaround tracker showing on-time rate, average turnaround, and cases at risk")
    d = os.path.join(ROOT, "blog", p["slug"])
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="").write(out)

if __name__ == "__main__":
    build_hub()
    build_article()
    print("wrote blog/index.html and blog/%s/index.html" % ARTICLE_SLUG)
