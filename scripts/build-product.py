"""Generate the Platform (feature) and Solutions (lab type) pages from one template each.

Every statement restates what the homepage, FAQ, Trust Center, or product screenshots already show.
Add a page by appending an entry to PLATFORM or SOLUTIONS, add its path to SITE_PAGES in site_chrome.py
if it is linked from the menu or footer, then run:
    python scripts/build-product.py && npm run build
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_chrome as shared
from site_chrome import esc, icon, screenshot

SITE = shared.SITE

# ---------------------------------------------------------------------------
# Platform: one page per module in the "Platform" menu
# shot = product screenshot in assets/img/screens (None = the connection diagram used for integrations)
# ---------------------------------------------------------------------------
PLATFORM = [
    dict(slug="pathology-lab", noun="pathology lab", name="Pathology lab", icon="flask", shot="pathology-imaging-reporting",
         title="Pathology lab software, from test order to validated result",
         lead="Register tests with the patient case, enter and validate results, and release reports only after an authorized doctor signs them. Every step is recorded against a named user.",
         meta="Pathology lab software for diagnostic labs: register tests, enter and validate results, track every sample, and release signed reports with a full audit trail.",
         features=["Tests registered with the patient case and bill", "Results entered by technicians and validated before release",
                   "Report templates for each test", "Barcode tracking for every tube", "Digital signature, then send to patient and doctor",
                   "Every edit kept with the user, time, and reason"],
         steps=[("Register", "The front desk adds the patient, the tests, and the payment in one screen."),
                ("Test and validate", "Technicians enter results; each case is validated before it moves to reporting."),
                ("Sign and send", "An authorized doctor signs, and the report goes to the patient and the referring doctor.")],
         related=["sample-tracking", "turnaround-tracking", "reports-e-signature"]),
    dict(slug="sample-tracking", noun="sample tracking", name="Sample tracking", icon="barcode", shot="sample-tracking",
         title="Every tube traced, from collection to rack to report",
         lead="Scan a barcode to match the tube to the right patient and test, see every step it has passed, and know exactly which rack and slot it sits in. No more searching refrigerators for a sample.",
         meta="Barcode sample tracking for diagnostic labs: match every tube to the patient and test, see each handoff, and find any sample by rack and slot.",
         features=["Barcode scan with instant patient match", "Timeline from registration to report", "Rack maps color-coded by tube type",
                   "Hold or reject with the reason recorded", "Urgent samples flagged", "Live accession queue"],
         steps=[("Label", "Each tube gets a barcode at the point of collection, matched to the patient and test."),
                ("Scan every handoff", "Registered, collected, received, in testing, reported: each step is recorded as it happens."),
                ("Find it in seconds", "Look up any sample to see its exact rack and slot, and who handled it last.")],
         related=["turnaround-tracking", "home-collection", "pathology-lab"]),
    dict(slug="turnaround-tracking", noun="turnaround tracking", name="Turnaround (TAT)", icon="clock", shot="turnaround-tracking",
         title="Catch turnaround delays before the doctor calls",
         lead="Every case carries a target time. Labora shows elapsed time against that target live, highlights what is at risk, and alerts the right people the moment a report runs late.",
         meta="Turnaround time (TAT) tracking for diagnostic labs: a target for every case, live elapsed time, at-risk alerts, delay reasons, and on-time rate.",
         features=["Target time for every case", "Elapsed vs. target, live", "At-risk and overshoot views",
                   "Automatic alerts when a target is missed", "A reason logged for every delay", "On-time delivery rate at a glance"],
         steps=[("Set targets", "Give each test or test group its own target, with a separate one for urgent priority."),
                ("Watch the clock", "Green is on time, amber is at risk, red is past target, so the team knows what to do next."),
                ("Review weekly", "See the on-time rate and the most common delay reasons, by test and by center.")],
         related=["sample-tracking", "reports-e-signature", "business-insights"], guide=True),
    dict(slug="radiology-reporting", noun="radiology reporting", name="Radiology reporting", icon="scan", shot="pathology-imaging-reporting",
         title="Radiology reporting for ultrasound, X-ray, CT, and MRI",
         lead="Report imaging studies from ready templates, next to the lab results for the same patient. Drafts save automatically, and doctors sign and send in one click.",
         meta="Radiology reporting software for imaging centers: templates for ultrasound, X-ray, CT, and MRI, automatic drafts, digital signature, and one patient case with lab results.",
         features=["Template library for each modality", "Drafts saved automatically", "Structured findings and impression",
                   "Preview before release", "Digital signature, then send", "Lab and imaging on the same patient case"],
         steps=[("Pick a template", "Choose the template for the study: ultrasound, X-ray, CT, or MRI."),
                ("Complete the findings", "Fill in structured findings and the impression; the draft saves as you go."),
                ("Sign and send", "Preview, sign, and deliver the report to the patient and the referring doctor.")],
         related=["reports-e-signature", "ecg-cardiology", "pathology-lab"]),
    dict(slug="ecg-cardiology", noun="cardiology reporting", name="ECG & cardiology", icon="activity", shot="pathology-imaging-reporting",
         title="ECG, 2D echo, and treadmill reports in the same patient case",
         lead="Cardiology studies are reported from templates in the same system as lab tests and imaging, so a patient has one record, one bill, and one place to find every report.",
         meta="ECG and cardiology reporting for clinics and labs: templates for ECG, 2D echo, and treadmill studies, digital signature, and one record with lab and imaging results.",
         features=["Templates for ECG, 2D echo, and treadmill studies", "Drafts saved automatically", "Structured findings and impression",
                   "Digital signature, then send", "One record and one bill with lab and imaging", "Every report traceable to the signing doctor"],
         steps=[("Register once", "The study is added to the patient case with any lab tests or scans."),
                ("Report from a template", "Complete the findings for the study type; the draft saves as you go."),
                ("Sign and deliver", "The signed report reaches the patient and the referring doctor right away.")],
         related=["radiology-reporting", "reports-e-signature", "pathology-lab"]),
    dict(slug="home-collection", noun="home collection", name="Home collection", icon="truck", shot="home-collection",
         title="Run home collection without the phone calls",
         lead="Assign bookings to phlebotomists, follow every visit on a live map, and keep patients updated automatically, so your front desk stops answering “where is the rider?” calls.",
         meta="Home sample collection software: assign bookings to phlebotomists, track visits on a live map, send patients automatic SMS updates, and move samples straight into tracking.",
         features=["Bookings by status: pending, en route, in progress, done", "Live phlebotomist location and ETA", "Automatic SMS updates to patients",
                   "Who is on duty, at a glance", "Address and tests on every visit card", "Collected samples move straight into tracking"],
         steps=[("Book and assign", "Bookings go to the right phlebotomist, with the address and tests on each visit card."),
                ("Track the visit", "Follow every visit on a live map while patients get automatic updates."),
                ("Hand off to the lab", "Collected samples move straight into sample tracking when they arrive.")],
         related=["sample-tracking", "centers", "turnaround-tracking"]),
    dict(slug="centers", noun="multi-center management", name="Centers & outsource labs", icon="building", shot="dashboard",
         title="Every branch, collection center, and partner lab in one system",
         lead="Branches, collection centers, and home collection run in one system. Switch between centers, compare activity and revenue across all of them, and keep partner and B2B work on the same record.",
         meta="Multi-center lab management: run branches, collection centers, and partner labs in one system, switch between centers, and compare activity and revenue.",
         features=["Switch between centers in one click", "Compare activity across every center", "Revenue by day and by center",
                   "Home collection and B2B revenue", "Dues by patient and partner lab", "The same roles and permissions everywhere"],
         steps=[("Add your centers", "Set up each branch and collection center with its own users and settings."),
                ("Work as one lab", "Samples, cases, and reports move between centers on the same patient record."),
                ("Compare and grow", "See which centers, days, and partners drive your business.")],
         related=["business-insights", "home-collection", "turnaround-tracking"]),
    dict(slug="reports-e-signature", noun="reports and e-signature", name="Reports & e-signature", icon="edit", shot="pathology-imaging-reporting",
         title="Sign and send reports in one click",
         lead="Reports are released only after an authorized doctor signs them. The signed PDF goes to the patient and the referring doctor the moment it is approved, with the signature recorded in the audit trail.",
         meta="Lab report e-signature and delivery: reports released only after an authorized doctor signs, then sent to the patient and referring doctor, with every signature recorded.",
         features=["Release only after an authorized signature", "Preview before release", "Signed PDF sent to patient and referring doctor",
                   "Templates for lab, imaging, and cardiology", "Every signature recorded with user and time", "Report status visible to the front desk"],
         steps=[("Review", "The doctor sees the completed report with the patient's history in one place."),
                ("Sign", "One click signs the report; the signature is recorded with the user and the time."),
                ("Deliver", "The signed PDF reaches the patient and the referring doctor right away.")],
         related=["pathology-lab", "radiology-reporting", "turnaround-tracking"]),
    dict(slug="business-insights", noun="business insights", name="Business insights", icon="chart", shot="business-insights",
         title="See what every center, day, and doctor brings in",
         lead="Track billing, collections, and outstanding dues across all your centers, compare this week with last, and see which referring doctors and partner labs drive your business.",
         meta="Lab business insights: billing, collections, and dues across centers, revenue by day and center, top referring doctors, and week-over-week comparison.",
         features=["Billed, collected, and outstanding", "Revenue by day and by center", "Home collection and B2B revenue",
                   "Dues by patient and partner lab", "Top referring doctors with trends", "Week-over-week comparison"],
         steps=[("Bill as you work", "Every case is billed at registration, so numbers update as the day goes on."),
                ("Compare", "See this week against last, center against center, and doctor against doctor."),
                ("Act", "Follow up on dues and invest in the referral relationships that grow your lab.")],
         related=["centers", "turnaround-tracking", "home-collection"]),
    dict(slug="integrations", noun="integrations and the API", name="Integrations & API", icon="plug", shot=None,
         title="Connect Labora with your instruments and systems",
         lead="Labora is designed to connect with lab instruments and other systems through its integration layer and API. Which connections are available depends on your analyzers and setup, so we review your equipment list with you.",
         meta="Lab software integrations: connect Labora with lab instruments and business systems through its integration layer and API. Review your setup with our team.",
         features=["Instrument readings and run files", "REST API for your own tools", "Identity and sign-in systems",
                   "Reporting and BI tools", "Cloud storage for files and archives", "Workflow and automation platforms"],
         steps=[("Share your equipment list", "Tell us your analyzers, instruments, and the systems you already use."),
                ("Plan the connections", "We map what Labora can connect to in your setup, and what each connection does."),
                ("Go live", "Connections are set up and tested as part of your rollout.")],
         related=["pathology-lab", "centers", "business-insights"]),
]

# ---------------------------------------------------------------------------
# Solutions: one page per lab type in the "Solutions" menu
# modules = platform slugs shown as "what you'll use most"
# ---------------------------------------------------------------------------
SOLUTIONS = [
    dict(slug="pathology-labs", name="Pathology labs", icon="flask", shot="sample-tracking",
         title="Laboratory software for independent pathology labs",
         lead="Register patients, track every tube, keep turnaround on target, and release signed reports, all in one patient case your whole team works in.",
         meta="Laboratory management software for pathology labs: registration, barcode sample tracking, turnaround targets, validated results, and signed reports in one system.",
         pains=[("Samples go missing between benches", "Barcode every tube and see its rack and slot in seconds."),
                ("Doctors call to ask if a report is ready", "Turnaround targets and alerts flag delays before anyone calls."),
                ("Results are retyped into reports", "Results flow into report templates, then signed and sent in one click.")],
         modules=["pathology-lab", "sample-tracking", "turnaround-tracking", "reports-e-signature"]),
    dict(slug="diagnostic-imaging-centers", name="Diagnostic & imaging centers", icon="scan", shot="pathology-imaging-reporting",
         title="One system for imaging and lab reporting",
         lead="Report ultrasound, X-ray, CT, and MRI from templates next to the lab results for the same patient. One record, one bill, and one place for every report.",
         meta="Software for diagnostic and imaging centers: radiology templates for ultrasound, X-ray, CT, and MRI, lab results on the same patient case, and signed report delivery.",
         pains=[("Imaging and lab live in separate systems", "Lab and imaging share the same patient case and the same bill."),
                ("Reports are typed from scratch", "A template library for each modality, with drafts saved automatically."),
                ("Delivery depends on the front desk", "Signed reports go to the patient and the referring doctor right away.")],
         modules=["radiology-reporting", "pathology-lab", "reports-e-signature", "ecg-cardiology"]),
    dict(slug="multi-center-lab-chains", name="Multi-center lab chains", icon="building", shot="business-insights",
         title="Run every center as one lab",
         lead="Branches, collection centers, and home collection in one system. Switch between centers, compare activity and revenue, and keep the same roles and permissions everywhere.",
         meta="Software for multi-center lab chains: run branches and collection centers in one system, compare revenue and turnaround, and keep one set of roles and permissions.",
         pains=[("Each branch runs its own way", "One setup for tests, price lists, templates, and roles across every center."),
                ("No single view of the business", "Revenue, dues, and referrals by center, day, and doctor."),
                ("Turnaround varies by location", "Compare on-time rates across centers and find where time is lost.")],
         modules=["centers", "business-insights", "turnaround-tracking", "home-collection"]),
    dict(slug="hospital-laboratories", name="Hospital laboratories", icon="hospital", shot="dashboard",
         title="Laboratory software for hospital labs",
         lead="Track every sample, keep urgent cases on target, and release reports only after an authorized doctor signs, with every action attributed and recorded.",
         meta="Laboratory management software for hospital labs: sample tracking, turnaround targets for urgent cases, signed report release, role-based access, and audit trails.",
         pains=[("Urgent samples wait in the same queue", "Urgent cases are flagged and carry their own, shorter targets."),
                ("Hard to answer who changed a result", "Every edit keeps the earlier value, the new value, the user, and the time."),
                ("Access is all or nothing", "Each role sees what it needs, by role and by center.")],
         modules=["sample-tracking", "turnaround-tracking", "reports-e-signature", "integrations"]),
    dict(slug="home-collection-services", name="Home collection services", icon="home", shot="home-collection",
         title="Software for home sample collection services",
         lead="Assign bookings, follow every visit on a live map, keep patients updated automatically, and move collected samples straight into tracking.",
         meta="Software for home sample collection services: bookings, phlebotomist live map and ETA, automatic patient SMS, and samples that move straight into tracking.",
         pains=[("Patients call to ask where the phlebotomist is", "Automatic SMS updates and a live ETA for every visit."),
                ("Dispatch runs on phone calls", "See who is on duty and assign bookings in a few clicks."),
                ("Samples lose their trail on the way", "Collected samples move straight into sample tracking.")],
         modules=["home-collection", "sample-tracking", "turnaround-tracking", "business-insights"]),
    dict(slug="cardiology-clinics", name="Cardiology & ECG clinics", icon="heart", shot="pathology-imaging-reporting",
         title="Reporting software for cardiology and ECG clinics",
         lead="Report ECG, 2D echo, and treadmill studies from templates, alongside any lab tests and scans for the same patient, and send signed reports in one click.",
         meta="Software for cardiology and ECG clinics: templates for ECG, 2D echo, and treadmill reports, one patient record with lab and imaging, and signed delivery.",
         pains=[("Cardiology reports are typed by hand", "Templates for each study type, with drafts saved automatically."),
                ("Patients have records in several places", "One patient case and one bill for cardiology, lab, and imaging."),
                ("Reports wait for someone to send them", "The signed report goes to the patient and the doctor right away.")],
         modules=["ecg-cardiology", "reports-e-signature", "radiology-reporting", "pathology-lab"]),
]

PLATFORM_BY_SLUG = {p["slug"]: p for p in PLATFORM}
CONNECT = [("cpu", "Lab instruments", "Readings and run files"), ("key", "Identity and access", "Sign-in and users"),
           ("bar", "BI and analytics", "Reporting tools"), ("cloud", "Cloud storage", "Files and archives"),
           ("flow", "Automation", "Workflow platforms"), ("code", "REST API", "Build your own")]

def visual(prefix, p, alt):
    if p["shot"]:
        return f'<figure class="pr-shot">{screenshot(prefix, p["shot"], alt, eager=True)}</figure>'
    rows = "".join(f'<li><span class="t-ic">{icon(ic)}</span><span><b>{esc(t)}</b><small>{esc(s)}</small></span></li>' for ic, t, s in CONNECT)
    return (f'<figure class="pr-shot pr-connect" aria-label="Labora connects with lab instruments and business systems">'
            f'<div class="pr-hub"><svg class="logo-mark" aria-hidden="true"><use href="#logo-mark-light"/></svg><b>Labora</b><small>Integration layer and API</small></div>'
            f'<ul>{rows}</ul></figure>')

def cta(prefix, title, text):
    return f'''<section class="page-section pr-cta-wrap" aria-labelledby="pr-cta-title">
  <div class="container">
    <div class="ab-cta-card reveal">
      <div>
        <h2 id="pr-cta-title">{esc(title)}</h2>
        <p>{esc(text)}</p>
      </div>
      <div class="ab-ctas">
        <a class="btn btn--primary btn--lg" href="{prefix}#demo">Book a demo</a>
        <a class="btn btn--ghost btn--lg" href="{prefix}pricing/">See pricing</a>
      </div>
    </div>
  </div>
</section>'''

def module_cards(prefix, slugs):
    return "".join(
        f'<a class="pr-mod reveal" href="{prefix}platform/{s}/"><span class="t-ic">{icon(PLATFORM_BY_SLUG[s]["icon"])}</span>'
        f'<span><b>{esc(PLATFORM_BY_SLUG[s]["name"])}</b><small>{esc(PLATFORM_BY_SLUG[s]["features"][0])}</small></span>{icon("arrow", "icon icon-sm")}</a>'
        for s in slugs)

def write_page(rel, prefix, current, title, desc, crumbs, body):
    url = f"{SITE}/{rel}"
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": title, "description": desc,
         "isPartOf": {"@id": f"{SITE}/#website"}, "about": {"@id": f"{SITE}/#organization"}},
        shared.breadcrumbs_ld([("Home", f"{SITE}/")] + crumbs)]}, indent=1, ensure_ascii=False)
    shared.write(rel + "index.html", shared.page(prefix, current, title, desc, url, f"{SITE}/assets/img/og-image.png", jsonld, body,
                                                 css=("pages.min.css",), js=("pages.min.js",)))

def build_platform(p):
    prefix = "../../"
    feats = "".join(f'<li>{icon("check")}<span>{esc(f)}</span></li>' for f in p["features"])
    steps = "".join(f'<li class="reveal"><span class="ab-step">{i:02d}</span><h3>{esc(t)}</h3><p>{esc(x)}</p></li>' for i, (t, x) in enumerate(p["steps"], 1))
    guide = (f'<p class="pr-guide reveal">{icon("book")}<span>Read our guide: <a href="{prefix}blog/how-to-cut-lab-turnaround-time/">How to cut turnaround time in a diagnostic lab</a></span></p>'
             if p.get("guide") else "")
    body = f'''<section class="pr-hero" aria-labelledby="pr-title">
  <div class="container">
    <nav class="pr-crumbs" aria-label="Breadcrumb"><a href="{prefix}">Home</a>{icon("chev", "icon")}<a href="{prefix}#platform">Platform</a>{icon("chev", "icon")}<span aria-current="page">{esc(p["name"])}</span></nav>
    <div class="pr-intro">
      <div>
        <p class="eyebrow"><span class="dot" aria-hidden="true"></span>{esc(p["name"])}</p>
        <h1 id="pr-title">{esc(p["title"])}</h1>
        <p class="lead">{esc(p["lead"])}</p>
        <div class="ab-ctas">
          <a class="btn btn--primary btn--lg" href="{prefix}#demo">Book a demo</a>
          <a class="btn btn--ghost btn--lg" href="{prefix}#product-tour">Watch the product tour</a>
        </div>
      </div>
    </div>
    {visual(prefix, p, f"Labora {p['name'].lower()} screen")}
  </div>
</section>

<section class="page-section" aria-labelledby="pr-feat-title">
  <div class="container ab-split">
    <div class="ab-side reveal">
      <p class="ab-label">What you get</p>
      <h2 id="pr-feat-title">Built into {esc(p["noun"])}</h2>
    </div>
    <div class="reveal">
      <ul class="pr-feats">{feats}</ul>
      {guide}
    </div>
  </div>
</section>

<section class="page-section" aria-labelledby="pr-how-title">
  <div class="container">
    <div class="ab-head reveal">
      <p class="ab-label">How it works</p>
      <h2 id="pr-how-title">Three steps, one patient case</h2>
    </div>
    <ol class="ab-track pr-track">{steps}</ol>
  </div>
</section>

<section class="page-section" aria-labelledby="pr-rel-title">
  <div class="container">
    <div class="ab-head reveal">
      <p class="ab-label">Works with</p>
      <h2 id="pr-rel-title">Connected to the rest of Labora</h2>
      <p>Every module shares the same data, so information entered once is available everywhere.</p>
    </div>
    <div class="pr-mods">{module_cards(prefix, p["related"])}</div>
  </div>
</section>

{cta(prefix, f"See {p['noun']} with your own setup", "Bring your test menu and price list. We will show you a patient case from registration to signed report, configured the way your team works.")}'''
    title = f"{p['name'].replace('Turnaround (TAT)', 'Turnaround Time (TAT) Tracking')} Software | Labora"
    write_page(f"platform/{p['slug']}/", prefix, None, title, p["meta"], [("Platform", f"{SITE}/#platform"), (p["name"], f"{SITE}/platform/{p['slug']}/")], body)

def build_solution(s):
    prefix = "../../"
    pains = "".join(f'<li class="reveal"><span class="ab-num">{i:02d}</span><h3>{esc(a)}</h3><p>{esc(b)}</p></li>' for i, (a, b) in enumerate(s["pains"], 1))
    others = "".join(f'<li><a href="{prefix}solutions/{o["slug"]}/">{icon(o["icon"])}<span>{esc(o["name"])}</span></a></li>' for o in SOLUTIONS if o is not s)
    body = f'''<section class="pr-hero" aria-labelledby="pr-title">
  <div class="container">
    <nav class="pr-crumbs" aria-label="Breadcrumb"><a href="{prefix}">Home</a>{icon("chev", "icon")}<a href="{prefix}#who-its-for">Solutions</a>{icon("chev", "icon")}<span aria-current="page">{esc(s["name"])}</span></nav>
    <div class="pr-intro">
      <div>
        <p class="eyebrow"><span class="dot" aria-hidden="true"></span>For {esc(s["name"].lower().replace("ecg", "ECG"))}</p>
        <h1 id="pr-title">{esc(s["title"])}</h1>
        <p class="lead">{esc(s["lead"])}</p>
        <div class="ab-ctas">
          <a class="btn btn--primary btn--lg" href="{prefix}#demo">Book a demo</a>
          <a class="btn btn--ghost btn--lg" href="{prefix}pricing/">See pricing</a>
        </div>
      </div>
    </div>
    {visual(prefix, s, f"Labora screen used by {s['name'].lower()}")}
  </div>
</section>

<section class="page-section" aria-labelledby="pr-pain-title">
  <div class="container ab-split">
    <div class="ab-side reveal">
      <p class="ab-label">What changes</p>
      <h2 id="pr-pain-title">The everyday problems Labora removes</h2>
    </div>
    <ol class="ab-list pr-pains">{pains}</ol>
  </div>
</section>

<section class="page-section" aria-labelledby="pr-mod-title">
  <div class="container">
    <div class="ab-head reveal">
      <p class="ab-label">Modules you will use most</p>
      <h2 id="pr-mod-title">The parts of Labora built for your lab</h2>
      <p>Start with the modules you need and add more as you grow. Every module shares the same patient case.</p>
    </div>
    <div class="pr-mods">{module_cards(prefix, s["modules"])}</div>
  </div>
</section>

<section class="page-section" aria-labelledby="pr-other-title">
  <div class="container ab-split">
    <div class="ab-side reveal">
      <p class="ab-label">Other labs</p>
      <h2 id="pr-other-title">Labora also runs</h2>
    </div>
    <ul class="ab-labs-list pr-others reveal">{others}</ul>
  </div>
</section>

{cta(prefix, f"See Labora set up for {s['name'].lower().replace('ecg', 'ECG')}", "Tell us how your lab works today. We will show you the same workflow in Labora, with your tests and price list.")}'''
    title = f"Software for {s['name'].replace('&', 'and')} | Labora"
    write_page(f"solutions/{s['slug']}/", prefix, None, title, s["meta"], [("Solutions", f"{SITE}/#who-its-for"), (s["name"], f"{SITE}/solutions/{s['slug']}/")], body)

if __name__ == "__main__":
    # Only the Solutions pages are live on main. The Platform pages stay on the feature/platform-solutions branch
    # until they are ready (their URLs show "coming soon" on the 404 page); run with --platform to build them too.
    import sys
    if "--platform" in sys.argv:
        for p in PLATFORM: build_platform(p)
    for s in SOLUTIONS: build_solution(s)
    print(f"wrote {len(SOLUTIONS)} solution pages" + (f" and {len(PLATFORM)} platform pages" if "--platform" in sys.argv else ""))
