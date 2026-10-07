"""Generate the Pricing, Contact, and legal (Privacy, Terms, Cookies) pages.

    python scripts/build-company.py && npm run build

PLACEHOLDERS to confirm before launch (also listed in README):
- PLANS: plan names and what each includes are a proposed structure; no prices are shown (every quote is tailored).
- LEGAL_*: drafts for counsel. Bracketed items such as [Legal entity name] must be filled in, and the draft banner
  removed (LEGAL_DRAFT = False) only after legal review.
"""
import os, sys, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_chrome as shared
from site_chrome import esc, icon

SITE = shared.SITE
CONTACT_EMAIL = "wordpressdev@bigscal.com"   # general contact; swap for sales@ / hello@ your domain when it exists
SECURITY_EMAIL = "wordpressdev@bigscal.com"  # keep in sync with scripts/build-pages.py
LEGAL_UPDATED = ("Oct 6, 2026", "2026-10-06")
LEGAL_DRAFT = True                           # shows the "Draft for legal review" banner on the legal pages

# Modules a client can combine (slug matches /platform/<slug>/); "core" ones are in every plan
MODULES = [
    ("pathology-lab", "Pathology lab", True), ("sample-tracking", "Sample tracking", True),
    ("turnaround-tracking", "Turnaround (TAT)", True), ("reports-e-signature", "Reports & e-signature", True),
    ("radiology-reporting", "Radiology reporting", False), ("ecg-cardiology", "ECG & cardiology", False),
    ("home-collection", "Home collection", False), ("centers", "Centers & outsource labs", False),
    ("business-insights", "Business insights", False), ("integrations", "Integrations & API", False),
]
MODULE_NAME = {s: n for s, n, _ in MODULES}

# PLACEHOLDER structure: confirm names and contents with the business team before launch
PLANS = [
    dict(id="single-center", name="Single center", who="For one lab, imaging center, or clinic.",
         base=None, items=["Pathology lab and sample tracking", "Turnaround targets and alerts", "Reports and e-signature",
                           "Billing at registration", "Add radiology or ECG reporting"]),
    dict(id="multi-center", name="Multi-center", who="For labs with branches, collection centers, or home collection.", featured=True,
         base="Single center", items=["Centers and outsource labs", "Home collection with live map", "Business insights across centers",
                                      "One setup for every center", "Add modules center by center"]),
    dict(id="enterprise", name="Enterprise", who="For hospital laboratories and large lab chains.",
         base="Multi-center", items=["Integrations and API", "Workflows configured to your processes", "Rollout planned across all centers",
                                     "Roles and permissions by center", "Security review support"]),
]

EVERY_PLAN = [
    ("cloud", "Secure cloud hosting", "Secured, monitored infrastructure with regular backups."),
    ("shield", "Access control and audit trails", "Role-based access and a record of every action."),
    ("refresh", "Data migration", "Your tests, price lists, report templates, and referring doctors, moved for you."),
    ("users", "Training for every role", "Front desk, phlebotomists, technicians, and pathologists."),
    ("sliders", "Guided rollout", "One center at a time, so your team keeps working."),
    ("message", "A team that knows your setup", "Questions go to the people who set up your lab."),
]

PRICING_FAQ = [
    ("How is Labora priced?", "Pricing depends on the number of centers, users, and modules you need. Choose the modules above, or tell us about your lab, and we will put together a quote."),
    ("Can we start with one center and add more later?", "Yes. Many labs start with one center and add the rest once the team is comfortable. Your setup, tests, and templates carry over to each new center."),
    ("Can we change modules later?", "Yes. Plans are built from modules, so you can add one when you need it, for example home collection or radiology reporting, and your quote is updated to match."),
    ("What do I need for a quote?", "Your number of centers, the modules you are interested in, and roughly how many people will use Labora. A short demo call is the fastest way to get it right."),
]

def page_ld(url, name, desc, crumbs, extra=None):
    g = [{"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": name, "description": desc,
          "isPartOf": {"@id": f"{SITE}/#website"}}, shared.breadcrumbs_ld([("Home", f"{SITE}/")] + crumbs)]
    if extra: g.append(extra)
    return json.dumps({"@context": "https://schema.org", "@graph": g}, indent=1, ensure_ascii=False)

def faq_html(pairs):
    return "".join(f'<details class="faq-item"><summary><h3>{esc(q)}</h3><span class="plus" aria-hidden="true"><svg class="icon"><use href="#i-plus"/></svg></span></summary>'
                   f'<div class="faq-answer"><p>{esc(a)}</p></div></details>' for q, a in pairs)

# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------
def build_pricing():
    prefix = "../"
    cards = ""
    for p in PLANS:
        base = f'<p class="pc-base">Everything in {esc(p["base"])}, plus:</p>' if p["base"] else '<p class="pc-base">Includes:</p>'
        items = "".join(f'<li>{icon("check")}<span>{esc(i)}</span></li>' for i in p["items"])
        cls = " pc--featured" if p.get("featured") else ""
        cards += (f'<article class="pc{cls} reveal"><h3>{esc(p["name"])}</h3><p class="pc-who">{esc(p["who"])}</p>'
                  f'<p class="pc-price"><b>Tailored quote</b><span>Priced by centers, users, and modules</span></p>'
                  f'<a class="btn {"btn--primary" if p.get("featured") else "btn--ghost"}" href="{prefix}contact/?plan={p["id"]}">Get a quote</a>'
                  f'{base}<ul class="checks">{items}</ul></article>')
    mods = "".join(
        f'<label class="pb-mod"><input type="checkbox" name="modules[]" value="{s}"{" checked" if core else ""}>'
        f'<span>{esc(n)}{"<small>In every plan</small>" if core else ""}</span></label>' for s, n, core in MODULES)
    every = "".join(f'<li class="reveal"><span class="t-ic">{icon(ic)}</span><h3>{esc(t)}</h3><p>{esc(x)}</p></li>' for ic, t, x in EVERY_PLAN)
    body = f'''<section class="pr-hero pc-hero" aria-labelledby="pc-title">
  <div class="container">
    <p class="eyebrow"><span class="dot" aria-hidden="true"></span>Pricing</p>
    <h1 id="pc-title">A plan built around your lab, not the other way around</h1>
    <p class="lead">Start from the plan closest to your size, choose the modules your team needs, and we will send a quote for exactly that. Add centers and modules whenever you grow.</p>
  </div>
</section>

<!-- PLACEHOLDER: plan names and contents are a proposed structure; confirm before launch (PLANS in scripts/build-company.py) -->
<section class="pc-plans-wrap" aria-labelledby="pc-plans-title">
  <div class="container">
    <h2 class="sr-only" id="pc-plans-title">Plans</h2>
    <div class="pc-plans">{cards}</div>
  </div>
</section>

<section class="page-section" id="build" aria-labelledby="pb-title">
  <div class="container">
    <div class="pb reveal" data-plan-builder>
      <div class="pb-main">
        <p class="ab-label">Build your plan</p>
        <h2 id="pb-title">Choose what your lab needs</h2>
        <p class="pb-sub">Core modules come with every plan. Add the rest to match how your lab works.</p>
        <fieldset class="pb-group">
          <legend>Modules</legend>
          <div class="pb-mods">{mods}</div>
        </fieldset>
        <fieldset class="pb-group">
          <legend>Number of centers</legend>
          <div class="pb-seg">
            <label><input type="radio" name="centers" value="1" checked><span>1</span></label>
            <label><input type="radio" name="centers" value="2–5"><span>2–5</span></label>
            <label><input type="radio" name="centers" value="6–20"><span>6–20</span></label>
            <label><input type="radio" name="centers" value="More than 20"><span>20+</span></label>
          </div>
        </fieldset>
      </div>
      <aside class="pb-sum on-dark" aria-live="polite">
        <p class="ab-label">Your plan</p>
        <p class="pb-plan" data-pb-plan>Single center</p>
        <p class="pb-meta"><span data-pb-count>4 modules</span> · <span data-pb-centers>1 center</span></p>
        <ul class="pb-list" data-pb-list></ul>
        <a class="btn btn--primary btn--lg" href="{prefix}contact/" data-pb-quote>Get a quote for this plan</a>
        <p class="pb-note">No commitment. We reply by email to confirm the details.</p>
      </aside>
    </div>
  </div>
</section>

<section class="page-section" aria-labelledby="pc-every-title">
  <div class="container">
    <div class="ab-band on-dark">
      <div class="ab-head reveal">
        <p class="ab-label">Included in every plan</p>
        <h2 id="pc-every-title">The essentials are never an add-on</h2>
        <p>Security, migration, training, and rollout come with every Labora plan, whatever its size.</p>
      </div>
      <ul class="ab-commit pc-every">{every}</ul>
    </div>
  </div>
</section>

<section class="page-section faq-block" aria-labelledby="pc-faq-title">
  <div class="container faq-wrap">
    <div class="faq-aside reveal">
      <h2 id="pc-faq-title">Pricing questions</h2>
      <p>Still deciding? These come up in almost every first call.</p>
      <a class="link-arrow faq-more" href="{prefix}faq/#pricing">See all FAQs {icon("arrow", "icon icon-sm")}</a>
    </div>
    <div class="faq-list">{faq_html(PRICING_FAQ)}</div>
  </div>
</section>

<section class="page-section pr-cta-wrap" aria-labelledby="pc-cta-title">
  <div class="container">
    <div class="ab-cta-card reveal">
      <div>
        <h2 id="pc-cta-title">Not sure which plan fits?</h2>
        <p>Book a demo and tell us how your lab works. We will recommend the modules and send a quote after the call.</p>
      </div>
      <div class="ab-ctas">
        <a class="btn btn--primary btn--lg" href="{prefix}#demo">Book a demo</a>
        <a class="btn btn--ghost btn--lg" href="{prefix}contact/">Contact sales</a>
      </div>
    </div>
  </div>
</section>
<script type="application/json" id="pb-names">{json.dumps(MODULE_NAME, ensure_ascii=False, separators=(",", ":"))}</script>'''
    url, desc = f"{SITE}/pricing/", "Labora pricing for diagnostic labs: plans for single-center labs, multi-center chains, and hospital labs, built from the modules you need, with a tailored quote."
    faq_ld = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in PRICING_FAQ]}
    shared.write("pricing/index.html", shared.page(prefix, "pricing", "Pricing: Plans for Diagnostic Labs | Labora", desc, url,
        f"{SITE}/assets/img/og-image.png", page_ld(url, "Labora pricing", desc, [("Pricing", url)], faq_ld), body, css=("pages.min.css",), js=("pages.min.js",)))

# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------
def build_contact():
    prefix = "../"
    opts = lambda xs: "".join(f"<option>{esc(x)}</option>" for x in xs)
    body = f'''<section class="pr-hero ct-hero" aria-labelledby="ct-title">
  <div class="container ct-grid">
    <div class="ct-copy">
      <p class="eyebrow"><span class="dot" aria-hidden="true"></span>Contact</p>
      <h1 id="ct-title">Talk to our team</h1>
      <p class="lead">Questions about Labora, a quote for your lab, or a demo with your own tests: tell us a little about your lab and we will get back to you by email.</p>
    </div>
    <div class="ct-more">
      <ol class="ct-steps">
        <li><span class="ab-step">01</span><div><h2>We reply by email</h2><p>Someone from our team answers your message and suggests a time to talk.</p></div></li>
        <li><span class="ab-step">02</span><div><h2>A demo with your setup</h2><p>We walk through a patient case from registration to signed report, using your tests.</p></div></li>
        <li><span class="ab-step">03</span><div><h2>A tailored quote</h2><p>You get a quote for the modules and centers you need, with no commitment.</p></div></li>
      </ol>
      <ul class="ct-other">
        <li><span class="t-ic">{icon("mail")}</span><div><b>Email</b><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></div></li>
        <li><span class="t-ic">{icon("shield")}</span><div><b>Security reports</b><a href="mailto:{SECURITY_EMAIL}">{SECURITY_EMAIL}</a><small>See our <a href="{prefix}security/#disclosure">disclosure guidelines</a></small></div></li>
      </ul>
    </div>
    <div class="form-card ct-card" id="form">
      <form id="contact-form" novalidate data-endpoint="" data-thanks="{prefix}thank-you/" data-lead-form aria-describedby="ct-error">
        <h2>Send us a message</h2>
        <p>All fields are required unless marked optional.</p>
        <p class="ct-from" data-ct-from hidden></p>
        <div class="form-grid">
          <div class="field"><label for="c-name">Full name</label><input id="c-name" name="name" type="text" autocomplete="name" required><span class="err" id="c-name-err">Enter your name.</span></div>
          <div class="field"><label for="c-email">Work email</label><input id="c-email" name="email" type="email" autocomplete="email" required><span class="err" id="c-email-err">Enter a valid work email.</span></div>
          <div class="field"><label for="c-company">Lab or organization</label><input id="c-company" name="company" type="text" autocomplete="organization" required><span class="err" id="c-company-err">Enter your lab or organization.</span></div>
          <div class="field"><label for="c-phone">Phone <span class="opt">(optional)</span></label><input id="c-phone" name="phone" type="tel" autocomplete="tel"></div>
          <div class="field"><label for="c-topic">How can we help?</label>
            <select id="c-topic" name="topic" required><option value="">Select one</option>{opts(["Book a demo", "Pricing and a quote", "Partnership", "Something else"])}</select>
            <span class="err" id="c-topic-err">Choose a topic.</span></div>
          <div class="field"><label for="c-centers">Number of centers</label>
            <select id="c-centers" name="centers" required><option value="">Select one</option>{opts(["1", "2–5", "6–20", "More than 20"])}</select>
            <span class="err" id="c-centers-err">Choose the number of centers.</span></div>
          <div class="field field--full"><label for="c-msg">Message <span class="opt">(optional)</span></label><textarea id="c-msg" name="message" rows="4"></textarea></div>
        </div>
        <input type="hidden" name="plan" value="">
        <input type="hidden" name="modules" value="">
        <div class="hp" aria-hidden="true"><label for="c-website">Leave this field empty</label><input id="c-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
        <div class="form-submit"><button class="btn btn--primary btn--lg" type="submit">Send message</button></div>
        <p class="form-error" id="ct-error" role="alert"></p>
        <p class="form-note">By submitting, you agree to our <a href="{prefix}privacy/">privacy policy</a>.</p>
      </form>
      <div class="form-status" role="status" aria-live="polite" tabindex="-1" data-lead-status>
        <span class="ok-icon">{icon("check", "icon icon-lg")}</span>
        <h2>Message received</h2>
        <p>Thanks. We will reply by email to the address you gave us.</p>
      </div>
    </div>
  </div>
</section>'''
    url, desc = f"{SITE}/contact/", "Contact Labora: ask about laboratory management software for your lab, request a quote, or book a demo with your own tests."
    org = {"@type": "Organization", "@id": f"{SITE}/#organization", "name": "Labora", "url": f"{SITE}/",
           "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "email": CONTACT_EMAIL, "areaServed": "US", "availableLanguage": "English"}]}
    shared.write("contact/index.html", shared.page(prefix, "contact", "Contact Labora | Talk to Our Team", desc, url,
        f"{SITE}/assets/img/og-image.png", page_ld(url, "Contact Labora", desc, [("Contact", url)], org), body, css=("pages.min.css",), js=("pages.min.js",)))

# ---------------------------------------------------------------------------
# Legal drafts. Sections are (id, heading, html). Bracketed text = to be completed by counsel.
# ---------------------------------------------------------------------------
def P(*xs): return "".join(f"<p>{x}</p>" for x in xs)
def UL(*xs): return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
def C(x): return f'<span class="lg-confirm" title="To be confirmed by counsel">{x}</span>'

PRIVACY = [
    ("who-we-are", "Who we are", P(f"This privacy policy explains how Labora ({C('[Legal entity name]')}, {C('[registered address]')}) collects and uses personal information when you visit this website or contact us. In this policy, “Labora,” “we,” and “us” mean that company.")),
    ("scope", "What this policy covers", P("This policy covers this website and the information you send us through it, such as demo requests and contact messages.",
        f"It does not cover the patient and laboratory data that our customers store in the Labora service. That data belongs to the lab that collects it. We process it only on the lab's behalf and under our agreement with that lab, which {C('includes a Business Associate Agreement where HIPAA applies')}. Patients with questions about their records should contact their lab.")),
    ("collect", "Information we collect", P("<strong>Information you give us.</strong> When you request a demo, ask for a quote, or send a message, we collect what you enter: your name, work email, phone number if you add it, your lab or organization, the type of lab, the number of centers, the modules you are interested in, and your message.",
        "<strong>Information collected automatically.</strong> Like most websites, our servers record basic technical information for each request, such as your IP address, browser type, the page requested, and the date and time. We use it to keep the site running and secure.",
        'Cookies: this website sets one strictly necessary cookie to remember your cookie choices, and no advertising or analytics cookies. See our <a href="../cookies/">cookie policy</a>.')),
    ("use", "How we use it", UL("To answer your message and schedule demos", "To prepare quotes and proposals you ask for",
        "To run, protect, and improve this website", "To comply with law and enforce our terms")),
    ("share", "How we share it", P("We do not sell your personal information, and we do not share it for cross-context behavioral advertising.",
        "We share it only with service providers who help us run our business, such as hosting and email providers, under contracts that limit how they can use it; when the law requires it; or as part of a merger, acquisition, or sale of assets, in which case this policy continues to apply to your information.")),
    ("retention", "How long we keep it", P(f"We keep contact and demo-request information for as long as needed to respond and follow up, and then {C('[retention period, for example 24 months]')}, unless the law requires us to keep it longer.")),
    ("security", "How we protect it", P('We use administrative, technical, and physical safeguards appropriate to the information we hold. Read more in our <a href="../security/">Trust Center</a>.')),
    ("rights", "Your choices and rights", P(f"You can ask us to access, correct, or delete the personal information you have given us, and you can ask us to stop contacting you at any time. Depending on where you live, {C('including California and other US states with privacy laws')}, you may have additional rights, and we will not discriminate against you for using them.",
        f'To make a request, email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. We may need to confirm your identity before we act on it.')),
    ("children", "Children", P("This website is meant for healthcare businesses and is not directed to children under 16. We do not knowingly collect personal information from them.")),
    ("changes", "Changes to this policy", P("If we change this policy, we will update the date at the top of this page and, for significant changes, give notice on this website.")),
    ("contact", "Contact us", P(f'Questions about this policy: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>, or write to {C("[Legal entity name, postal address]")}.')),
]

TERMS = [
    ("agreement", "These terms", P(f"These terms govern your use of this website and, unless you have a separate signed agreement with us, the Labora service. They form an agreement between you and {C('[Legal entity name]')} (“Labora”). If you use Labora for an organization, you accept them on its behalf and confirm you are authorized to do so.",
        "If your organization has a signed order form or master agreement with Labora, that agreement controls where it differs from these terms.")),
    ("service", "The Labora service", P("Labora is laboratory management software provided as a subscription. The modules, number of centers, users, and fees for your organization are set out in your quote or order form. We may improve and update the service over time without reducing its core functionality during your subscription.")),
    ("accounts", "Accounts and access", P("You are responsible for deciding who in your organization gets an account and which role each person has, for removing access when someone leaves, and for keeping sign-in details private. Tell us right away if you believe an account has been used without permission.")),
    ("acceptable-use", "Acceptable use", UL("Use Labora only for your organization's lawful laboratory operations", "Do not try to access data or accounts you are not authorized to use",
        "Do not interfere with or disrupt the service, or test its security without our written permission (see our responsible disclosure guidelines)", "Do not copy, resell, or reverse engineer the service")),
    ("data", "Your data and patient information", P(f"Your organization owns the data it enters into Labora, including patient information. We use it only to provide and support the service for you, as described in your agreement and, where HIPAA applies, {C('our Business Associate Agreement')}. On request at the end of your subscription, we will make your data available for export {C('[export period and format to be confirmed]')}.")),
    ("clinical", "Clinical decisions", P("Labora is software for running a laboratory. It does not provide medical advice or make clinical decisions. Results, reports, and their release remain the responsibility of your qualified professionals.")),
    ("fees", "Fees and payment", P(f"Fees are set out in your quote or order form. Unless it says otherwise, fees are invoiced {C('[annually / monthly]')} in advance and are payable within {C('[30]')} days of the invoice date.")),
    ("ip", "Intellectual property", P("Labora and its software, design, and content are owned by Labora and protected by law. Your subscription gives your organization the right to use the service during its term; it does not transfer ownership.")),
    ("disclaimers", "Disclaimers", P(f"{C('[Warranty and disclaimer language to be drafted by counsel.]')}")),
    ("liability", "Limitation of liability", P(f"{C('[Limitation of liability language to be drafted by counsel.]')}")),
    ("termination", "Term and termination", P(f"Your subscription runs for the term in your order form and renews as stated there. Either party may end it for a material breach that is not fixed within {C('[30]')} days of written notice.")),
    ("law", "Governing law", P(f"These terms are governed by the laws of the State of {C('[State]')}, without regard to its conflict-of-laws rules, and disputes will be resolved in the courts located in {C('[County, State]')}.")),
    ("changes", "Changes to these terms", P("We may update these terms. If a change is significant, we will give notice on this website or by email before it takes effect.")),
    ("contact", "Contact us", P(f'Questions about these terms: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.')),
]

COOKIES = [
    ("what", "What cookies are", P("Cookies are small files a website stores in your browser. Similar technologies, such as local storage, work in a similar way. They can be needed for a site to work, or used for analytics and advertising.")),
    ("ours", "What this website uses today", P("This website sets one cookie: <code>labora_consent</code>, which remembers the choices you make in our cookie banner, for 6 months. It is strictly necessary and contains only those choices, not who you are.",
        "The site does not use advertising cookies or third-party analytics, and every file it loads comes from our own server. Analytics and marketing tools, if we ever add them, run only after you allow them.")),
    ("types", "Types of cookies", '<div class="lg-table"><table><thead><tr><th scope="col">Type</th><th scope="col">Purpose</th><th scope="col">Used on this site</th></tr></thead><tbody>'
        '<tr><td>Strictly necessary</td><td>Needed for the site to work, such as remembering your cookie choices</td><td><code>labora_consent</code> (6 months)</td></tr>'
        '<tr><td>Analytics</td><td>Understanding how visitors use the site</td><td>None</td></tr>'
        '<tr><td>Advertising</td><td>Showing ads based on your browsing</td><td>None</td></tr></tbody></table></div>'),
    ("choices", "Your choices", P("When you first visit, you can accept all cookies, deny all non-essential cookies, or choose by category. You can change your mind at any time:",
        ) + '<p><button class="btn btn--ghost" type="button" data-cookie-settings>Open cookie settings</button></p>'
        + P("If your browser sends a Global Privacy Control signal, we treat it as a choice to deny all non-essential cookies.")),
    ("future", "If this changes", P("If we add analytics or other cookies in the future, we will list them here first, and they will run only for visitors who allow that category.")),
    ("control", "How to control cookies", P("You can block or delete cookies in your browser settings. Blocking strictly necessary cookies may stop parts of a website from working.")),
    ("contact", "Contact us", P(f'Questions about this policy: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.')),
]

def build_legal(slug, title, h1, intro, sections, desc):
    prefix = "../"
    toc = "".join(f'<li><a href="#{i}">{esc(h)}</a></li>' for i, h, _ in sections)
    secs = "".join(f'<section id="{i}" aria-labelledby="{i}-h"><h2 id="{i}-h">{esc(h)}</h2>{x}</section>' for i, h, x in sections)
    banner = (f'<div class="lg-draft" role="note">{icon("alert")}<div><b>Draft for legal review.</b> This policy is not yet in effect. '
              f'Highlighted items are to be confirmed by counsel before launch.</div></div>') if LEGAL_DRAFT else ""
    others = [(s, t) for s, t in (("privacy", "Privacy policy"), ("terms", "Terms of service"), ("cookies", "Cookie policy")) if s != slug]
    body = f'''<section class="lg-hero" aria-labelledby="lg-title">
  <div class="container">
    <p class="eyebrow"><span class="dot" aria-hidden="true"></span>Legal</p>
    <h1 id="lg-title">{esc(h1)}</h1>
    <p class="lead">{esc(intro)}</p>
    <p class="lg-updated">Last updated <time datetime="{LEGAL_UPDATED[1]}">{LEGAL_UPDATED[0]}</time></p>
    {banner}
  </div>
</section>
<div class="container lg-layout">
  <nav class="lg-toc" aria-label="On this page">
    <p class="ab-label">On this page</p>
    <ol>{toc}</ol>
    <p class="lg-others">{"".join(f'<a href="{prefix}{s}/">{esc(t)}</a>' for s, t in others)}</p>
  </nav>
  <article class="lg-prose">{secs}</article>
</div>'''
    url = f"{SITE}/{slug}/"
    shared.write(f"{slug}/index.html", shared.page(prefix, slug, f"{title} | Labora", desc, url, f"{SITE}/assets/img/og-image.png",
        page_ld(url, title, desc, [(title, url)]), body, css=("pages.min.css",), js=("pages.min.js",)))

# ---------------------------------------------------------------------------
# Thank-you page: /thank-you/ (forms go here about 1.5s after a successful send)
# The form leaves {form, topic, name, ts} in sessionStorage (never in the URL); pages.js fills the page from it.
# Without it (a direct visit), the page reads as a general "message received".
# ---------------------------------------------------------------------------
TY_STEPS = {  # form: [(title, text, state)]
    "contact": [("Message received", "Your topic and number of centers came through with it.", "Received"),
                ("We reply by email", "Someone from our team answers and, if it helps, suggests a time to talk.", "Next"),
                ("A demo or a quote, if you want one", "Set up for the modules and centers you need, with no commitment.", "Then")],
    "demo": [("Request received", "Your lab type and number of centers came through with it.", "Received"),
             ("We email you to pick a time", "Someone from our team replies to the work email you gave us.", "Next"),
             ("A 20-minute walkthrough", "Set up with your tests, departments, and price list, so you see your own lab day.", "Then")],
}
TY_READING = [  # (title, text, href)
    ("Product tour", "From registration to a signed report.", "#product-tour"),
    ("Trust Center", "How patient data is protected.", "security/"),
    ("How to cut lab turnaround time", "A practical guide from our blog.", "blog/how-to-cut-lab-turnaround-time/"),
    ("Pricing", "How plans are put together for your lab.", "pricing/"),
]

def build_thanks():
    prefix = "../"
    def steps(kind):
        return (f'<ol class="ty-steps" data-ty-steps="{kind}"{" hidden" if kind != "contact" else ""}>' + "".join(
            f'<li class="{"is-done" if i == 0 else ""}"><span class="ty-num">{i + 1:02d}</span><div><h3>{esc(t)}</h3><p>{esc(x)}</p></div>'
            f'<span class="ty-state">{s}</span></li>' for i, (t, x, s) in enumerate(TY_STEPS[kind])) + '</ol>').replace(' class=""', '')
    reading = "".join(f'<li><a href="{prefix}{u}"><span class="nf-i-t">{esc(t)}</span><span class="nf-i-d">{esc(x)}</span>'
                      f'{icon("arrow", "icon icon-sm")}</a></li>' for t, x, u in TY_READING)
    body = f'''<section class="ty" aria-labelledby="ty-title">
  <div class="container">
    <div class="ty-head">
      <p class="hm-label" data-ty-label>Message received</p>
      <h1 id="ty-title"><span data-ty-hello>Thank you.</span> <span data-ty-title>Your message is with our team.</span></h1>
      <p class="ty-lead" data-ty-lead>We'll reply by email to the address you gave us. There's nothing else you need to do.</p>
    </div>
    <dl class="ty-meta">
      <div><dt>Request</dt><dd data-ty-kind>Message</dd></div>
      <div data-ty-sent hidden><dt>Sent</dt><dd><time data-ty-time></time></dd></div>
      <div><dt>Replies from</dt><dd><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></dd></div>
    </dl>
    <div class="ty-grid">
      <section aria-labelledby="ty-next">
        <h2 class="ty-h2" id="ty-next">What happens next</h2>
        {steps("contact")}
        {steps("demo")}
      </section>
      <nav class="nf-index ty-read" aria-labelledby="ty-wait">
        <h2 id="ty-wait">While you wait</h2>
        <ul>{reading}</ul>
        <p class="ty-back"><a class="nf-alt" href="{prefix}">Back to the homepage</a></p>
      </nav>
    </div>
  </div>
</section>'''
    url = f"{SITE}/thank-you/"
    out = shared.page(prefix, "thank-you", "Thank you | Labora", "Your message has reached the Labora team.", url,
                      f"{SITE}/assets/img/og-image.png", page_ld(url, "Thank you", "Your message has reached the Labora team.", [("Thank you", url)]),
                      body, css=("pages.min.css",), js=("pages.min.js",))
    # A confirmation page: keep it out of search results and the sitemap
    shared.write("thank-you/index.html", out.replace('content="index, follow, max-image-preview:large"', 'content="noindex, follow"'))

if __name__ == "__main__":
    build_pricing()
    build_contact()
    build_thanks()
    build_legal("privacy", "Privacy Policy", "Privacy policy", "How Labora collects, uses, and protects personal information on this website.", PRIVACY,
                "How Labora collects, uses, shares, and protects personal information on its website, and the choices and rights you have.")
    build_legal("terms", "Terms of Service", "Terms of service", "The terms for using this website and the Labora service.", TERMS,
                "The terms that govern use of the Labora website and laboratory management service.")
    build_legal("cookies", "Cookie Policy", "Cookie policy", "Which cookies this website uses, and how to control them.", COOKIES,
                "Which cookies and similar technologies the Labora website uses today, and how to control them.")
    print("wrote pricing, contact, privacy, terms, cookies")
