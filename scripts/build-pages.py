"""Generate the Security (Trust Center) and FAQ pages.

Content lives in the data lists below, so adding a security section, a compliance item,
or a FAQ question is a one-entry edit. Then run:
    python scripts/build-pages.py && npm run build
Shared header/menu/footer/sprite come from scripts/site_chrome.py (copied from index.html).
"""
import io, os, re, html, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import site_chrome as shared
SITE, ROOT = shared.SITE, shared.ROOT

UPDATED = ("Oct 5, 2026", "2026-10-05")       # "Last updated" date shown on the Trust Center
SECURITY_EMAIL = "wordpressdev@bigscal.com"  # security contact; swap for a dedicated address (e.g. security@ your domain) when one exists

def esc(s): return html.escape(s, quote=True)
def icon(name, cls="icon"): return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'
def slug(s): return "q-" + re.sub(r"[^a-z0-9]+", "-", html.unescape(s).lower()).strip("-")[:60]

# ---------------------------------------------------------------------------
# FAQ content. Answers marked FROM_HOME are reused word for word from index.html
# so the homepage and the FAQ page always agree.
# ---------------------------------------------------------------------------
_home = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
HOME_FAQ = {html.unescape(q): a.strip() for q, a in re.findall(
    r'<details class="faq-item"><summary><h3>(.*?)</h3>.*?<div class="faq-answer">(.*?)</div></details>', _home, re.S)}
FROM_HOME = object()

def P(*paras): return "".join(f"<p>{p}</p>" for p in paras)

FAQ = [
    dict(id="general", label="General", icon="flask", intro="What Labora is and who it is for.", items=[
        ("What is laboratory management software?", FROM_HOME),
        ("What is the difference between LIMS, LIS, and laboratory management software?", FROM_HOME),
        ("Who is Labora built for?", P("Labora is built for diagnostic labs: independent pathology labs, imaging and diagnostic centers, multi-center lab chains, hospital laboratories, home collection services, and cardiology and ECG clinics.",
                                       "Front desk staff, phlebotomists, technicians, reporting doctors, and owners all work in the same patient case, each with access suited to their role.")),
        ("Can Labora handle both pathology and radiology?", FROM_HOME),
    ]),
    dict(id="product", label="Product & features", icon="layers", intro="Samples, turnaround, reporting, and home collection.", items=[
        ("How does Labora track samples?", FROM_HOME),
        ("How does turnaround time (TAT) tracking work?", FROM_HOME),
        ("Can doctors sign reports digitally?", P("Yes. Reports are released only after an authorized doctor signs them, and the signed report can be sent to the patient and the referring doctor right away. Every signature is recorded in the audit trail with the user and time.")),
        ("Does Labora support home sample collection?", P("Yes. You can assign bookings to phlebotomists, follow visits on a live map, and keep patients updated automatically, so collected samples move straight into tracking when they reach the lab.")),
        ("Can I manage multiple centers and collection points?", FROM_HOME),
        ("What business reports does Labora provide?", P("Labora shows billing, collections, and outstanding dues across your centers, compares periods, and highlights which referring doctors and partner labs drive your business.")),
    ]),
    dict(id="security", label="Security & privacy", icon="shield", intro="How Labora protects patient data and records every action.", items=[
        ("How does Labora protect patient data?", P("Access is role-based, every action is attributed to a named user and recorded in an audit trail, and reports are released only after an authorized doctor signs them. Records are structured, and changes are controlled, so results stay consistent.",
                                                      'Read the full overview in our <a href="../security/">Trust Center</a>.')),
        ("Who can see patient records?", P("Each user sees what their role needs. Front desk, technicians, doctors, and accounts teams can be given different access, and you decide which roles can view, edit, sign, or bill.")),
        ("Is every change to a record tracked?", P("Yes. Registrations, edits, signatures, and payments are recorded with the user and the time, so you can always answer who did what, and when.")),
        ("Is Labora HIPAA compliant?", P('We are building our compliance program for US healthcare customers. The current status of each part of the program is published in the <a href="../security/#compliance">Trust Center</a>, and our team can walk you through your specific requirements during a demo.')),
        ("How do I report a security issue?", P(f'Email <a href="mailto:{SECURITY_EMAIL}">{SECURITY_EMAIL}</a> with the details. We review every report and keep you updated. See our <a href="../security/#disclosure">responsible disclosure guidelines</a>.')),
    ]),
    dict(id="implementation", label="Implementation", icon="sliders", intro="Setup, data migration, integrations, and training.", items=[
        ("How long does it take to get started?", P("Rollout is guided, one center at a time, so your team keeps working while Labora is set up. Most of the work is configuring your tests, price list, and report templates, which we help with.")),
        ("Can you move our existing data?", P("Yes. We migrate your tests, price lists, report templates, and referring doctors for you, so you start with your own setup instead of a blank system.")),
        ("Do you train our team?", P("Yes. Training covers every role: front desk, phlebotomists, technicians, and pathologists, so each person learns the parts of Labora they use every day.")),
        ("Can Labora connect with lab analyzers and other systems?", FROM_HOME),
        ("Can Labora be configured for my lab's tests and workflows?", FROM_HOME),
    ]),
    dict(id="pricing", label="Pricing & billing", icon="dollar", intro="How plans are put together.", items=[
        ("How is Labora priced?", P('Pricing depends on the number of centers, users, and modules you need. <a href="../#demo">Book a demo</a> and we will put together a quote for your lab.')),
        ("Can we start with one center and add more later?", P("Yes. Many labs start with one center and add the rest once the team is comfortable. Your setup, tests, and templates carry over to each new center.")),
    ]),
    dict(id="support", label="Support", icon="message", intro="Getting help when you need it.", items=[
        ("How do I get help?", P('Contact our team from the <a href="/contact/">contact page</a>, or book a call. Implementation questions are handled by the team that set up your lab.')),
        ("Where can I learn more about running a faster lab?", P('Our <a href="../blog/">blog</a> has practical guides on turnaround time, sample tracking, reporting, and growing a multi-center lab.')),
    ]),
]

def answer_html(q, a):
    return HOME_FAQ[q] if a is FROM_HOME else a

def faq_item(q, a, tools=True):
    q_html = esc(q)
    tools_html = ('<div class="faq-tools"><button type="button" data-copy-q>' + icon("link") + 'Copy link</button>'
                  '<span class="sep" aria-hidden="true"></span><span>Was this helpful?</span>'
                  '<button type="button" data-helpful="yes" aria-pressed="false">Yes</button>'
                  '<button type="button" data-helpful="no" aria-pressed="false">No</button>'
                  '<span class="faq-thanks" aria-live="polite"></span></div>') if tools else ''
    return (f'<details class="faq-item" id="{slug(q)}"><summary><h3>{q_html}</h3><span class="plus" aria-hidden="true">'
            f'<svg class="icon"><use href="#i-plus"/></svg></span></summary><div class="faq-answer">{answer_html(q, a)}</div>{tools_html}</details>')

def faq_schema(pairs):
    def text(h): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text(answer_html(q, a))}} for q, a in pairs]}

# ---------------------------------------------------------------------------
# Trust Center content
# ---------------------------------------------------------------------------
NAV = [("overview", "Overview"), ("access", "Access control"), ("audit", "Audit trail"), ("protection", "Protection"),
       ("compliance", "Compliance"), ("shared", "Shared responsibility"), ("disclosure", "Disclosure"), ("security-faq", "FAQ")]

# Hero trust marks: (icon or short text, title, sub, is_text_mark, sub_class)
# Statuses for HIPAA and SOC 2 come from COMPLIANCE below, so they always agree.
MARKS = [
    ("users", "Role-based access", "Every user, every center"),
    ("history", "Full audit trail", "Who, what, and when"),
    ("edit", "Signed releases", "Authorized doctors only"),
    ("cloud", "Secured cloud", "Monitored, backed up"),
]

# Overview cards: a framed product visual with the caption below. kind = list | kv | checks | stack
OVERVIEW = [
    ("list", "Every action has a name on it",
     "Registrations, results, corrections, and signatures are recorded against a named user and a time, so every report can be traced from the front desk to the doctor.",
     [("SM", "Dr. S. Mitchell", "Signed and released report", "10:31 AM"),
      ("RK", "R. Kumar", "Corrected Hemoglobin · reason recorded", "10:12 AM"),
      ("AM", "A. Mehta", "Stored sample in Rack B-04", "9:24 AM"),
      ("JO", "J. Ortiz", "Registered CBC, Lipid Profile", "9:02 AM")]),
    ("kv", "Accountability at every step",
     "Each step in the life of a sample leaves a record, and nothing is overwritten silently.",
     [("Every action", "user + time"), ("Result edits", "old + new value"), ("Report release", "doctor signature"),
      ("Access", "role + center"), ("Records", "regular backups")]),
    ("checks", "Access built around roles",
     "Front desk, technicians, doctors, and accounts each see what their job needs. Your admins decide who gets which role.",
     ["Individual sign-in for every user", "Permissions by role", "Access by center", "Report release limited to doctors", "Full audit trail"]),
    ("stack", "Safeguards for patient results",
     "Results reach patients and referring doctors only after review and sign-off, with every change explained.",
     [("Controlled releases", "Reports go out only after an authorized doctor signs them."),
      ("Changes with a reason", "Edits keep the earlier value, the new value, and who made them."),
      ("Activity you can review", "Recent activity across users, centers, and cases in one place.")]),
]

# Example permission matrix (roles and permissions are configurable per lab)
ROLES = ["Front desk", "Technician", "Doctor", "Accounts", "Admin"]
PERMS = [
    ("Register patients and tests", [1, 0, 0, 0, 1]),
    ("Enter and validate results", [0, 1, 1, 0, 1]),
    ("Sign and release reports", [0, 0, 1, 0, 0]),
    ("View billing and dues", [1, 0, 0, 1, 1]),
    ("Manage users and roles", [0, 0, 0, 0, 1]),
]

TIMELINE = [  # (icon, who/what, meta, diff, time)
    ("file", "Front desk registered CBC, Lipid Profile", "J. Ortiz · Main Lab, Austin", None, "9:02:14 AM"),
    ("tube", "Sample stored in Rack B-04, slot B4", "A. Mehta · barcode scan", None, "9:24:19 AM"),
    ("edit", "Result corrected for Hemoglobin", "R. Kumar · reason: transcription error", ("13.1 g/dL", "13.6 g/dL"), "10:12:44 AM"),
    ("check", "Report signed and released", "Dr. S. Mitchell · pathologist", None, "10:31:08 AM"),
    ("send", "Signed PDF sent to patient and referring doctor", "Labora · automatic delivery", None, "10:31:09 AM"),
]

# Protection in practice: (icon, title, checklist). Only claims the product already makes.
PROTECTION = [
    ("lock", "Access", ["Individual sign-in for every user", "Permissions by role", "Access by center", "Report release limited to doctors"]),
    ("history", "Records", ["User and time on every action", "Earlier and new values kept on edits", "Structured, consistent records", "Signed releases you can trace"]),
    ("eye", "Visibility", ["Recent activity across users", "Activity across every center", "Full history for each case", "Review by the people responsible"]),
    ("cloud", "Infrastructure", ["Secured cloud hosting", "Monitored infrastructure", "Regular backups", "No servers to run in your lab"]),
]

# PLACEHOLDER STATUSES: confirm each item and its status with your security/compliance owner before launch.
# Never mark an item "live" until the certificate, report, or agreement actually exists.
COMPLIANCE = [  # (mark, title, status_key, status_label, text)
    ("HIPAA", "HIPAA program", "progress", "In progress", "Administrative, physical, and technical safeguards for protected health information."),
    ("SOC 2", "SOC 2 Type II", "planned", "Planned", "An independent audit of our security controls."),
    ("PT", "Independent penetration test", "planned", "Planned", "Regular testing by an outside security firm, with findings tracked to resolution."),
]
COMPLIANCE_SCOPE = [
    "Administrative safeguards for protected health information",
    "Physical and technical safeguards for systems that hold patient data",
    "An independent audit of our security controls",
    "Regular testing by an outside security firm",
    "Written policies your compliance team can review",
]

SHARED = (
    ["Securing the platform and the cloud infrastructure it runs on",
     "Recording every action in the audit trail",
     "Enforcing role-based permissions and report sign-off rules",
     "Backups of your lab's records",
     "Fixing reported vulnerabilities and keeping you informed"],
    ["Deciding who gets an account and which role each person has",
     "Removing access promptly when someone leaves",
     "Keeping sign-in details private and not sharing accounts",
     "Reviewing activity and audit trails for your centers",
     "Following your own policies for printing and sharing reports"],
)

STEPS = [
    ("Report", f"Email {SECURITY_EMAIL} with what you found and how to reproduce it."),
    ("Acknowledge", "We confirm receipt and keep you updated while we investigate."),
    ("Fix", "We validate the issue, fix it, and verify the fix."),
    ("Close", "We let you know when it is resolved and thank you for helping."),
]

SECURITY_FAQ = [
    "How does Labora protect patient data?",
    "Who can see patient records?",
    "Is every change to a record tracked?",
    "Is Labora HIPAA compliant?",
    "How do I report a security issue?",
]

def find_faq(q):
    for g in FAQ:
        for qq, a in g["items"]:
            if qq == q: return a
    raise KeyError(q)

def mock(kind, data):
    if kind == "list":
        return '<ol class="mock">' + "".join(
            f'<li><span class="m-av">{a}</span><span><b>{esc(n)}</b><small>{esc(t)}</small></span><span class="m-time">{tm}</span></li>' for a, n, t, tm in data) + '</ol>'
    if kind == "kv":
        return '<ul class="mock m-kv">' + "".join(f'<li><span>{esc(k)}</span><span class="mono">{esc(v)}</span></li>' for k, v in data) + '</ul>'
    if kind == "checks":
        return '<ul class="mock m-checks">' + "".join(f'<li>{icon("check")}{esc(x)}</li>' for x in data) + '</ul>'
    return '<ul class="mock m-stack">' + "".join(f'<li><b>{esc(t)}</b><small>{esc(x)}</small></li>' for t, x in data) + '</ul>'

# ---------------------------------------------------------------------------
# Trust Center page: /security/
# ---------------------------------------------------------------------------
def build_security():
    prefix = "../"
    comp = {c[0]: c for c in COMPLIANCE}
    marks = [(ic, t, s, False, "") for ic, t, s in MARKS] + [
        (m, t, lab, True, "is-progress" if k == "progress" else "") for m, t, k, lab, _ in (comp["HIPAA"], comp["SOC 2"])]
    marks_html = "".join(
        f'<li class="mark"><span class="mark-ic{" mark-ic--text" if txt else ""}" aria-hidden="true">{esc(ic) if txt else icon(ic)}</span>'
        f'<b>{esc(t)}</b><small{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{esc(s)}</small></li>'
        for ic, t, s, txt, cls in marks)
    nav = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in NAV)
    overview = "\n      ".join(
        f'<article class="vcard reveal"><div class="vpanel" aria-hidden="true">{mock(kind, data)}</div><h3>{esc(t)}</h3><p>{esc(x)}</p></article>'
        for kind, t, x, data in OVERVIEW)
    head_cells = "".join(f'<th scope="col">{r}</th>' for r in ROLES)
    rows = "".join(f'<tr><th scope="row">{esc(p)}</th>' + "".join(
        f'<td><span class="{"yes" if v else "no"}" role="img" aria-label="{"Allowed" if v else "Not allowed"}">{icon("check" if v else "x")}</span></td>' for v in vals) + '</tr>'
        for p, vals in PERMS)
    tl = "".join(
        f'<li><span class="tl-ic">{icon(ic)}</span><div><b>{esc(w)}</b><span class="tl-meta">{esc(m)}</span>'
        + (f'<span class="diff"><del>{d[0]}</del>{icon("arrow")}<ins>{d[1]}</ins></span>' if d else '') + f'</div><time>{t}</time></li>'
        for ic, w, m, d, t in TIMELINE)
    protection = "".join(
        f'<article class="pcard reveal"><h3>{icon(ic)}{esc(t)}</h3><ul>' + "".join(f'<li>{esc(x)}</li>' for x in items) + '</ul></article>'
        for ic, t, items in PROTECTION)
    scope = "".join(f'<li>{icon("check")}{esc(x)}</li>' for x in COMPLIANCE_SCOPE)
    status = "".join(
        f'<li><span class="badge-mark" aria-hidden="true">{m}</span><div><h3>{esc(t)}</h3><p>{esc(x)}</p></div><span class="status status--{k}">{lab}</span></li>'
        for m, t, k, lab, x in COMPLIANCE)
    shared_cols = "".join(
        f'<div class="shared-col{" shared-col--lab" if i else ""} reveal"><h3><span class="t-ic">{icon("shield" if not i else "building")}</span>{"Labora handles" if not i else "Your lab controls"}</h3>'
        f'<ul class="checks">' + "".join(f'<li>{icon("check")}{esc(x)}</li>' for x in col) + '</ul></div>'
        for i, col in enumerate(SHARED))
    steps = "".join(f'<li class="step reveal"><h3>{esc(t)}</h3><p>{esc(x)}</p></li>' for t, x in STEPS)
    sec_faq = "\n        ".join(faq_item(q, find_faq(q)) for q in SECURITY_FAQ)

    body = f'''<section class="trust-hero" aria-labelledby="trust-title">
  <div class="container">
    <p class="eyebrow"><span class="dot" aria-hidden="true"></span>Trust Center</p>
    <h1 id="trust-title">Security built for patient data</h1>
    <p class="lead">Every action in Labora is attributed and recorded, access follows each person's role, and every report is released by an authorized doctor. Here is how we protect your lab's data, and what we are building next.</p>
    <div class="trust-ctas">
      <a class="btn btn--primary btn--lg" href="#documentation">Request security details</a>
      <a class="btn btn--outline-light btn--lg" href="#disclosure">Report a vulnerability</a>
    </div>
    <ul class="marks">{marks_html}</ul>
    <p class="trust-updated">Last updated <time datetime="{UPDATED[1]}">{UPDATED[0]}</time></p>
  </div>
</section>

<nav class="trust-nav" aria-label="On this page"><div class="container"><ul>{nav}</ul></div></nav>

<section class="page-section trust-section" id="overview" aria-labelledby="overview-title">
  <div class="container">
    <div class="s-head reveal">
      <h2 id="overview-title">Security is part of the workflow, not an add-on</h2>
      <p>The controls are built into the screens your team already uses, from the front desk to the reporting doctor.</p>
    </div>
    <div class="vgrid">
      {overview}
    </div>
  </div>
</section>

<section class="page-section trust-section" id="access" aria-labelledby="access-title">
  <div class="container t-row">
    <div class="t-copy reveal">
      <p class="kicker">{icon("users")}Access control</p>
      <h2 id="access-title">Everyone sees what their role needs</h2>
      <p>Permissions follow each person's job, so the front desk can register patients without seeing results, and only authorized doctors can sign and release reports.</p>
      <ul class="checks">
        <li>{icon("check")}Roles for front desk, technicians, doctors, accounts, and admins</li>
        <li>{icon("check")}Access configured per role and per center</li>
        <li>{icon("check")}Report release limited to authorized doctors</li>
      </ul>
    </div>
    <div class="reveal">
      <div class="matrix-wrap">
        <table class="matrix">
          <caption class="sr-only">Example role permissions</caption>
          <thead><tr><th scope="col">Permission</th>{head_cells}</tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
      <p class="t-note">Example configuration. Roles and permissions are set up to match how your lab works.</p>
    </div>
  </div>
</section>

<section class="page-section trust-section" id="audit" aria-labelledby="audit-title">
  <div class="container t-row t-row--flip">
    <div class="t-copy reveal">
      <p class="kicker">{icon("history")}Audit trail</p>
      <h2 id="audit-title">Know who touched every record, and when</h2>
      <p>Every registration, result, correction, signature, and delivery is recorded against a named user and a time, so you can answer any question about a report from one place.</p>
      <ul class="checks">
        <li>{icon("check")}User and time on every action</li>
        <li>{icon("check")}Earlier and new values kept for every correction</li>
        <li>{icon("check")}Signed releases you can trace back to the doctor</li>
      </ul>
    </div>
    <ol class="timeline reveal">{tl}</ol>
  </div>
</section>

<section class="page-section trust-section" id="protection" aria-labelledby="protection-title">
  <div class="container">
    <div class="s-head reveal">
      <h2 id="protection-title">Protection in practice</h2>
      <p>How patient data stays accurate, attributable, and visible only to the right people, on infrastructure your lab does not have to run.</p>
    </div>
    <div class="pcards">{protection}</div>
  </div>
</section>

<!-- Compliance statuses are PLACEHOLDERS: confirm each with your compliance owner before launch (see COMPLIANCE in scripts/build-pages.py). -->
<section class="page-section trust-section" id="compliance" aria-labelledby="comp-title">
  <div class="container comp-hl">
    <div class="reveal">
      <div class="s-head">
        <h2 id="comp-title">Our compliance program</h2>
        <p>We are building our program for US healthcare customers and publish where each part stands, so your team never has to guess.</p>
      </div>
      <p class="comp-intro">The program covers:</p>
      <ul class="mock m-checks comp-list">{scope}</ul>
      <p class="comp-note">Reports will be shared with customers under NDA as each item is completed. Need details for a vendor review now? <a href="#documentation">Request security details</a>.</p>
    </div>
    <div class="comp-status reveal">
      <header><b>Program status</b><span>Updated <time datetime="{UPDATED[1]}">{UPDATED[0]}</time></span></header>
      <ul>{status}</ul>
    </div>
  </div>
</section>

<section class="page-section trust-section" id="shared" aria-labelledby="shared-title">
  <div class="container">
    <div class="s-head reveal">
      <h2 id="shared-title">Security is a shared responsibility</h2>
      <p>Labora secures the platform. Your lab controls who gets access and how reports are shared. Here is who does what.</p>
    </div>
    <div class="shared">{shared_cols}</div>
  </div>
</section>

<section class="page-section trust-section" id="disclosure" aria-labelledby="disc-title">
  <div class="container">
    <div class="s-head reveal">
      <h2 id="disc-title">Responsible disclosure</h2>
      <p>If you find a security issue in Labora, please tell us privately first so we can fix it before it affects any lab.</p>
    </div>
    <ol class="steps">{steps}</ol>
    <div class="disclose">
      <div class="disclose-card reveal">
        <h3>Guidelines for researchers</h3>
        <ul>
          <li>Only test accounts you own or have permission to use.</li>
          <li>Never access, change, or keep patient data that is not yours. Stop and report as soon as you see any.</li>
          <li>Do not run tests that could disrupt service, such as denial of service or heavy automated scanning.</li>
          <li>Give us reasonable time to fix the issue before sharing it publicly.</li>
        </ul>
      </div>
      <div class="contact-card reveal">
        <div><h3>Report a vulnerability</h3><p>Include the steps to reproduce, the affected page or feature, and how to reach you.</p></div>
        <a class="mail" href="mailto:{SECURITY_EMAIL}">{icon("mail")}{SECURITY_EMAIL}</a>
      </div>
    </div>
  </div>
</section>

<section class="page-section trust-section faq-block" id="security-faq" aria-labelledby="sfaq-title">
  <div class="container faq-wrap">
    <div class="faq-aside reveal">
      <h2 id="sfaq-title">Security questions</h2>
      <p>Common questions from lab owners and IT teams.</p>
      <a class="link-arrow faq-more" href="{prefix}faq/#security">See all FAQs {icon("arrow", "icon icon-sm")}</a>
    </div>
    <div class="faq-list">
        {sec_faq}
    </div>
  </div>
</section>

<section class="trust-cta" id="documentation" aria-labelledby="docs-title">
  <div class="container reveal">
    <h2 id="docs-title">Questions about security?</h2>
    <p>Our team can walk your IT or compliance lead through how Labora handles access, audit trails, and patient data, and help with your security questionnaire.</p>
    <div class="trust-ctas">
      <a class="btn btn--primary btn--lg" href="mailto:{SECURITY_EMAIL}?subject=Security%20details%20request">Request security details</a>
      <a class="btn btn--outline-light btn--lg mail-chip" href="{prefix}#demo">{icon("calendar")}Book a demo</a>
    </div>
  </div>
</section>

<div class="toast" role="status" aria-live="polite"></div>'''
    url = f"{SITE}/security/"
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": f"{url}#webpage", "url": url, "name": "Security and Trust Center | Labora",
         "description": "How Labora protects patient data: role-based access, audit trails, signed report releases, secured cloud infrastructure, and our compliance program.",
         "dateModified": UPDATED[1], "publisher": {"@type": "Organization", "name": "Labora", "url": f"{SITE}/"}},
        faq_schema([(q, find_faq(q)) for q in SECURITY_FAQ]),
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Security", "item": url}]}]}, indent=1, ensure_ascii=False)
    shared.write("security/index.html", shared.page(prefix, "security", "Security and Trust Center | Labora",
        "How Labora protects patient data for diagnostic labs: role-based access, audit trails, signed report releases, secured cloud infrastructure, and our compliance program.",
        url, f"{SITE}/assets/img/og-image.png", jsonld, body, css=("pages.min.css",), js=("pages.min.js",)))

# ---------------------------------------------------------------------------
# FAQ page: /faq/
# ---------------------------------------------------------------------------
def build_faq():
    prefix = "../"
    total = sum(len(g["items"]) for g in FAQ)
    cats = "".join(f'<li><a href="#{g["id"]}"><span>{icon(g["icon"])}{esc(g["label"])}</span><span class="n">{len(g["items"])}</span></a></li>' for g in FAQ)
    groups = "\n".join(f'''      <section class="faq-group" id="{g["id"]}" aria-labelledby="{g["id"]}-title">
        <div class="faq-group-head"><span class="t-ic">{icon(g["icon"])}</span><div><h2 id="{g["id"]}-title">{esc(g["label"])}</h2><p>{esc(g["intro"])}</p></div></div>
        <div class="faq-list">
          {"".join(faq_item(q, a) for q, a in g["items"])}
        </div>
      </section>''' for g in FAQ)
    body = f'''<section class="faq-hero" aria-labelledby="faq-title">
  <div class="container">
    <p class="eyebrow"><span class="dot" aria-hidden="true"></span>FAQ</p>
    <h1 id="faq-title">Questions, answered</h1>
    <p class="lead">Everything lab owners, managers, and IT teams ask us about Labora, from features and security to setup and pricing.</p>
    <div class="faq-search" role="search">
      <label class="sr-only" for="faq-search">Search questions</label>
      {icon("search")}
      <input id="faq-search" type="search" placeholder="Search {total} questions" autocomplete="off">
    </div>
    <p class="faq-results" aria-live="polite"></p>
  </div>
</section>

<div class="container faq-layout" data-faq>
  <nav class="faq-cats" aria-label="Question categories">
    <h2>Categories</h2>
    <ul>{cats}</ul>
    <div class="help"><strong>Can't find an answer?</strong>Our team replies to every question.<br><a class="link-arrow" href="/contact/">Contact us {icon("arrow", "icon icon-sm")}</a></div>
  </nav>
  <div>
{groups}
    <div class="faq-empty">
      <h3>No questions match that search</h3>
      <p>Try a different word, or ask our team directly.</p>
      <p style="margin-top:1.25rem"><button class="btn btn--ghost" type="button" data-faq-reset>Clear search</button></p>
    </div>
  </div>
</div>

<div class="container">
  <section class="help-cards" aria-label="More help">
    <a class="help-card help-card--dark reveal" href="{prefix}#demo"><span class="t-ic">{icon("calendar")}</span><h3>Book a demo</h3><p>See Labora set up with your own tests and price list.</p><span class="link-arrow">Book a demo {icon("arrow", "icon icon-sm")}</span></a>
    <a class="help-card reveal" href="{prefix}security/"><span class="t-ic">{icon("shield")}</span><h3>Trust Center</h3><p>How we protect patient data, and our compliance program.</p><span class="link-arrow">Visit the Trust Center {icon("arrow", "icon icon-sm")}</span></a>
    <a class="help-card reveal" href="{prefix}blog/"><span class="t-ic">{icon("book")}</span><h3>Guides and articles</h3><p>Practical advice on turnaround, sample tracking, and reporting.</p><span class="link-arrow">Read the blog {icon("arrow", "icon icon-sm")}</span></a>
  </section>
</div>

<div class="toast" role="status" aria-live="polite"></div>'''
    url = f"{SITE}/faq/"
    pairs = [(q, a) for g in FAQ for q, a in g["items"]]
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": [
        dict(faq_schema(pairs), **{"@id": f"{url}#faq", "url": url}),
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "FAQ", "item": url}]}]}, indent=1, ensure_ascii=False)
    shared.write("faq/index.html", shared.page(prefix, "faq", "Laboratory Management Software FAQ | Labora",
        "Answers to common questions about Labora: sample tracking, turnaround time, pathology and radiology reporting, security, setup, data migration, and pricing.",
        url, f"{SITE}/assets/img/og-image.png", jsonld, body, css=("pages.min.css",), js=("pages.min.js",)))

# ---------------------------------------------------------------------------
# 404 page: /404.html (served by the server for every missing URL)
# Planned pages that are linked from the menu and footer but not built yet get a "coming soon" note
# and a link to the closest content that exists today. Remove an entry once its page is live.
# ---------------------------------------------------------------------------
PLANNED = {  # path (no leading slash): (page name, closest existing URL, link label)
    "platform/pathology-lab/": ("Pathology lab", "#reporting", "See pathology and imaging reporting"),
    "platform/sample-tracking/": ("Sample tracking", "#sample-tracking", "See sample tracking"),
    "platform/turnaround-tracking/": ("Turnaround tracking", "#turnaround-tracking", "See turnaround tracking"),
    "platform/radiology-reporting/": ("Radiology reporting", "#reporting", "See pathology and imaging reporting"),
    "platform/ecg-cardiology/": ("ECG and cardiology", "#platform", "See the platform overview"),
    "platform/home-collection/": ("Home collection", "#home-collection", "See home collection"),
    "platform/centers/": ("Centers and outsource labs", "#platform", "See the platform overview"),
    "platform/reports-e-signature/": ("Reports and e-signature", "#reporting", "See reporting and sign-off"),
    "platform/business-insights/": ("Business insights", "#business-insights", "See business insights"),
    "platform/integrations/": ("Integrations and API", "#integrations", "See integrations"),
    "platform/sample-management/": ("Sample management", "#sample-management", "See sample management"),
    "platform/quality-compliance/": ("Quality and compliance", "security/", "Visit the Trust Center"),
    "platform/lims/": ("LIMS", "#platform", "See the platform overview"),
    "platform/eln/": ("ELN", "#platform", "See the platform overview"),
    "platform/inventory-management/": ("Inventory", "#platform", "See the platform overview"),
    "platform/workflow-automation/": ("Workflow automation", "#platform", "See the platform overview"),
    "platform/equipment-management/": ("Equipment", "#platform", "See the platform overview"),
    "platform/reporting-analytics/": ("Reporting and analytics", "#business-insights", "See business insights"),
    **{f"solutions/{k}/": (v, "#solutions", "See who Labora is built for") for k, v in [
        ("pathology-labs", "Pathology labs"), ("diagnostic-imaging-centers", "Diagnostic and imaging centers"),
        ("multi-center-lab-chains", "Multi-center lab chains"), ("hospital-laboratories", "Hospital laboratories"),
        ("home-collection-services", "Home collection services"), ("cardiology-clinics", "Cardiology and ECG clinics"),
        ("research-development", "Research and development"), ("clinical-laboratories", "Clinical laboratories"),
        ("quality-control", "Quality control"), ("pharmaceutical", "Pharmaceutical"), ("biotechnology", "Biotechnology"),
        ("contract-research", "Contract research"), ("manufacturing", "Manufacturing"), ("academic", "Academic laboratories")]},
    "resources/": ("Resource center", "blog/", "Read the blog"),
    "resources/guides/": ("Guides", "blog/", "Read the blog"),
    "docs/api/": ("API documentation", "#integrations", "See integrations"),
    "pricing/": ("Pricing", "faq/#q-how-is-labora-priced", "See how Labora is priced"),
    "contact/": ("Contact", "#demo", "Book a demo or ask a question"),
    "about/": ("About Labora", "#why-labora", "See why labs choose Labora"),
    "login/": ("Sign in", "#demo", "Book a demo to get access"),
    "signup/": ("Sign up", "#demo", "Book a demo to get started"),
    "privacy/": ("Privacy policy", "security/", "See how we protect data"),
    "terms/": ("Terms of service", "#demo", "Contact our team"),
    "cookies/": ("Cookie policy", "security/", "See how we protect data"),
}

# The page is served at any depth (/platform/lims/, /a/b/c), so every URL resolves against <base href="/">.
# For local previews in the /labora/ subfolder, the inline script moves the base before any asset loads.
# Its SHA-256 is allowed in the CSP (deploy/nginx.conf, _headers, vercel.json, .htaccess).
DEV_FOLDER = "/labora/"
BASE_FIX_JS = f"if(location.pathname.indexOf('{DEV_FOLDER}')===0)document.querySelector('base').href='{DEV_FOLDER}';"

LINKS_404 = [  # (icon, title, text, href, link label)
    ("play", "Product tour", "See Labora in action, from registration to signed report.", "#product-tour", "Watch the tour"),
    ("layers", "Platform overview", "Sample tracking, reporting, home collection, and billing.", "#platform", "Explore the platform"),
    ("shield", "Trust Center", "How we protect patient data, and our compliance program.", "security/", "Visit the Trust Center"),
    ("message", "FAQ", "Answers about features, security, setup, and pricing.", "faq/", "Read the FAQ"),
    ("book", "Blog", "Practical guides for running a faster diagnostic lab.", "blog/", "Read the blog"),
]

def build_404():
    prefix = "./"  # resolves against <base>, so it works at any depth; "./#demo" also skips same-page anchor scrolling
    h, m, f = shared.chrome(prefix)
    def href(u): return prefix + u
    cards = "".join(f'<a class="help-card" href="{href(u)}"><span class="t-ic">{icon(ic)}</span><h3>{esc(t)}</h3><p>{esc(x)}</p>'
                    f'<span class="link-arrow">{esc(l)} {icon("arrow", "icon icon-sm")}</span></a>' for ic, t, x, u, l in LINKS_404)
    cards += (f'<a class="help-card help-card--dark" href="{href("#demo")}"><span class="t-ic">{icon("calendar")}</span><h3>Book a demo</h3>'
              f'<p>See Labora set up with your own tests and price list.</p><span class="link-arrow">Book a demo {icon("arrow", "icon icon-sm")}</span></a>')
    planned = json.dumps({k: [n, href(u), l] for k, (n, u, l) in PLANNED.items()}, ensure_ascii=False, separators=(",", ":"))
    out = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <base href="/">
  <script>{BASE_FIX_JS}</script>
  <title>Page not found | Labora</title>
  <meta name="robots" content="noindex">
  <meta name="theme-color" content="#0d3a33">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preload" href="assets/fonts/figtree-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/css/styles.min.css">
  <link rel="stylesheet" href="assets/css/pages.min.css">
  {shared.INLINE_JS}
</head>
<body>
<a class="skip-link" href="#main" data-skip>Skip to content</a>
{shared.SPRITE}
{h}

{m}

<main id="main" class="nf-main">
<section class="nf-hero" aria-labelledby="nf-title">
  <div class="container">
    <p class="eyebrow"><span class="dot" aria-hidden="true"></span>Error 404</p>
    <h1 id="nf-title">This page isn't here</h1>
    <p class="lead" data-nf-lead>The link may be out of date, or the page has moved. Here are the best places to go next.</p>
    <p class="nf-path" data-nf-path hidden><span>You tried</span> <code></code></p>
    <div class="nf-soon" data-nf-soon hidden>
      <span class="t-ic">{icon("clock")}</span>
      <div>
        <span class="status status--progress">Coming soon</span>
        <h2>We're still building the <span data-nf-name></span> page</h2>
        <p>Until it's ready, the closest information is one click away.</p>
        <a class="btn btn--primary" href="{href("")}" data-nf-alt>Go to the homepage</a>
      </div>
    </div>
    <div class="nf-ctas">
      <a class="btn btn--primary btn--lg" href="{href("")}" data-nf-home>Go to homepage</a>
      <a class="btn btn--ghost btn--lg" href="{href("#demo")}">Book a demo</a>
    </div>
  </div>
</section>

<div class="container">
  <section class="nf-links" aria-labelledby="nf-links-title">
    <h2 id="nf-links-title">Popular pages</h2>
    <div class="help-cards">{cards}</div>
  </section>
</div>
<script type="application/json" id="nf-planned">{planned}</script>
</main>

{f}

<script src="assets/js/main.min.js" defer></script>
<script src="assets/js/pages.min.js" defer></script>
</body>
</html>
'''
    shared.write("404.html", out)
    return len(PLANNED)

if __name__ == "__main__":
    missing = [q for g in FAQ for q, a in g["items"] if a is FROM_HOME and q not in HOME_FAQ]
    if missing: raise SystemExit(f"Homepage FAQ answers not found for: {missing}")
    build_security()
    build_faq()
    print(f"wrote 404.html ({build_404()} planned pages mapped)")
    print(f"wrote security/index.html and faq/index.html ({sum(len(g['items']) for g in FAQ)} questions in {len(FAQ)} categories)")
