/*!
 * Labora site pages: Trust Center section menu, FAQ search/filter/deep links/feedback.
 * Vanilla JS, no dependencies. Loaded with `defer` after main.min.js.
 */
(function () {
  'use strict';
  var doc = document;
  var hasIO = 'IntersectionObserver' in window;
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }

  /* ---------- Shared: highlight the link for the section in view ---------- */
  function spy(links, rootMargin, onChange) {
    if (!links.length || !hasIO) return;
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
    var targets = Object.keys(byId).map(function (id) { return doc.getElementById(id); }).filter(Boolean);
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        links.forEach(function (a) { a.classList.toggle('is-active', a === byId[e.target.id]); });
        if (onChange) onChange(byId[e.target.id]);
      });
    }, { rootMargin: rootMargin });
    targets.forEach(function (t) { io.observe(t); });
  }

  /* ---------- Toast ---------- */
  var toast = $('.toast');
  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('is-visible');
    clearTimeout(showToast.t);
    showToast.t = setTimeout(function () { toast.classList.remove('is-visible'); }, 2200);
  }
  function copy(text) {
    var done = function () { showToast('Link copied'); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () { showToast(text); });
    else showToast(text);
  }

  /* ---------- Trust Center: sticky section menu ---------- */
  var trustNav = $('.trust-nav ul');
  if (trustNav) {
    spy($$('a[href^="#"]', trustNav), '-30% 0px -60% 0px', function (a) {
      // keep the active tab visible inside the horizontally scrolling menu
      if (!a) return;
      var l = a.offsetLeft - trustNav.clientWidth / 2 + a.clientWidth / 2;
      trustNav.scrollTo({ left: Math.max(0, l), behavior: 'smooth' });
    });
  }

  /* ---------- 404: name the missing page; for planned pages, point to the closest live content ---------- */
  var planned = $('#nf-planned');
  if (planned) {
    // The page has <base href="/"> (any depth), so "#main" would point at the homepage: keep the skip link on this page
    var skip = $('[data-skip]');
    if (skip) skip.setAttribute('href', location.pathname + location.search + '#main');
    var base = doc.querySelector('base');
    var basePath = base ? new URL(base.href).pathname : '/';
    var path = location.pathname.indexOf(basePath) === 0 ? location.pathname.slice(basePath.length) : location.pathname.replace(/^\/+/, '');
    var setText = function (sel, text) { var el = $(sel); if (el) el.textContent = text; };
    if (path && path !== '404.html') setText('[data-nf-query]', '/' + decodeURIComponent(path));
    var map = {};
    try { map = JSON.parse(planned.textContent); } catch (e) {}
    var hit = map[path.toLowerCase().replace(/\/?$/, '/')];
    if (hit) {
      // A planned page: say so plainly, and make the closest live content the main action
      setText('[data-nf-eyebrow]', 'Coming soon');
      setText('#nf-title', 'The ' + hit[0] + ' page is on its way');
      setText('[data-nf-lead]', 'We are still building this page. Until it is ready, the same information is one click away.');
      var primary = $('[data-nf-primary]');
      if (primary) { primary.setAttribute('href', hit[1]); primary.textContent = hit[2]; }
      var home = $('[data-nf-home]');
      if (home) home.hidden = false;
      setText('[data-nf-result]', hit[0] + ' page in progress');
      setText('[data-nf-result-note]', 'Publishing soon');
      setText('[data-nf-status]', 'Coming soon');
      document.title = hit[0] + ': coming soon | Labora';
      doc.documentElement.classList.add('nf-planned');
    }
  }

  /* ---------- Legal pages: highlight the section in view ---------- */
  spy($$('.lg-toc ol a[href^="#"]'), '-20% 0px -70% 0px');

  /* ---------- Pricing: build a plan from modules, then hand it to the contact form ---------- */
  var builder = $('[data-plan-builder]');
  if (builder) {
    var names = {};
    try { names = JSON.parse($('#pb-names').textContent); } catch (e) {}
    var pbPlan = $('[data-pb-plan]', builder), pbCount = $('[data-pb-count]', builder), pbCenters = $('[data-pb-centers]', builder);
    var pbList = $('[data-pb-list]', builder), pbQuote = $('[data-pb-quote]', builder);
    var quoteBase = pbQuote.getAttribute('href');
    var update = function () {
      var mods = $$('input[name="modules[]"]:checked', builder).map(function (i) { return i.value; });
      var centers = ($('input[name="centers"]:checked', builder) || {}).value || '1';
      // Suggest the plan the choices fit: integrations or 20+ centers -> Enterprise; any multi-site need -> Multi-center
      var plan = (mods.indexOf('integrations') !== -1 || centers === 'More than 20') ? 'Enterprise'
        : (centers !== '1' || mods.indexOf('centers') !== -1 || mods.indexOf('home-collection') !== -1) ? 'Multi-center' : 'Single center';
      pbPlan.textContent = plan;
      pbCount.textContent = mods.length + (mods.length === 1 ? ' module' : ' modules');
      pbCenters.textContent = centers === '1' ? '1 center' : centers.replace('More than 20', '20+') + ' centers';
      pbList.innerHTML = '';
      mods.forEach(function (m) { var li = doc.createElement('li'); li.textContent = names[m] || m; pbList.appendChild(li); });
      pbQuote.setAttribute('href', quoteBase + '?plan=' + encodeURIComponent(plan.toLowerCase().replace(/\s+/g, '-')) +
        '&centers=' + encodeURIComponent(centers) + '&modules=' + encodeURIComponent(mods.join(',')) + '#form');
    };
    builder.addEventListener('change', update);
    update();
  }

  /* ---------- Contact: validation, demo mode until data-endpoint is set, and prefill from Pricing ---------- */
  var lead = $('[data-lead-form]');
  if (lead) {
    var leadStatus = $('[data-lead-status]');
    var leadError = $('#' + lead.getAttribute('aria-describedby'));
    var mailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    var required = $$('input[required], select[required]', lead);
    var submit = $('button[type="submit"]', lead), submitText = submit.textContent;
    var check = function (el) {
      var v = el.value.trim();
      var ok = v !== '' && (el.type !== 'email' || mailRe.test(v));
      var err = $('#' + el.id + '-err');
      el.closest('.field').classList.toggle('has-error', !ok);
      el.setAttribute('aria-invalid', String(!ok));
      if (err) { if (ok) el.removeAttribute('aria-describedby'); else el.setAttribute('aria-describedby', err.id); }
      return ok;
    };
    required.forEach(function (el) {
      el.addEventListener('blur', function () { if (el.value) check(el); });
      el.addEventListener(el.tagName === 'SELECT' ? 'change' : 'input', function () { if (el.closest('.field').classList.contains('has-error')) check(el); });
    });

    // Arriving from Pricing: ?plan=multi-center&centers=2–5&modules=a,b
    var params = new URLSearchParams(location.search);
    var plan = params.get('plan'), modules = (params.get('modules') || '').split(',').filter(Boolean);
    if (plan || modules.length) {
      var label = function (s) { return s.replace(/-/g, ' ').replace(/^./, function (c) { return c.toUpperCase(); }); };
      lead.elements.topic.value = 'Pricing and a quote';
      if (params.get('centers')) lead.elements.centers.value = params.get('centers');
      lead.elements.plan.value = plan || '';
      lead.elements.modules.value = modules.join(',');
      var from = $('[data-ct-from]', lead);
      if (from) {
        from.textContent = 'Quote request: ' + (plan ? label(plan) + ' plan' : 'custom plan') +
          (modules.length ? ', ' + modules.length + (modules.length === 1 ? ' module' : ' modules') : '') + '. Add anything else below.';
        from.hidden = false;
      }
    }

    lead.addEventListener('submit', function (e) {
      e.preventDefault();
      if (leadError) leadError.classList.remove('is-visible');
      var bad = null;
      required.forEach(function (el) { if (!check(el) && !bad) bad = el; });
      if (bad) { bad.focus(); return; }
      var done = function () {
        lead.hidden = true;
        leadStatus.classList.add('is-visible');
        leadStatus.focus();
        if (window.dataLayer) window.dataLayer.push({ event: 'contact_submitted', topic: lead.elements.topic.value });
      };
      if (lead.elements.website && lead.elements.website.value) { done(); return; } // honeypot: pretend success
      submit.disabled = true;
      submit.textContent = 'Sending…';
      var endpoint = lead.getAttribute('data-endpoint');
      if (!endpoint) { setTimeout(done, 500); return; } // demo mode until a form handler is connected
      fetch(endpoint, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(lead) })
        .then(function (r) { if (!r.ok) throw new Error(); done(); })
        .catch(function () {
          submit.disabled = false;
          submit.textContent = submitText;
          if (leadError) { leadError.textContent = 'Your message was not sent. Check your connection and try again.'; leadError.classList.add('is-visible'); }
        });
    });
  }

  /* ---------- FAQ: open a question from the URL hash (e.g. /faq/#q-hipaa) ---------- */
  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var el = doc.getElementById(id);
    if (!el || !el.classList.contains('faq-item')) return;
    $$('.faq-item.is-target').forEach(function (x) { x.classList.remove('is-target'); });
    el.open = true;
    el.classList.add('is-target');
    requestAnimationFrame(function () { el.scrollIntoView({ block: 'start' }); });
  }
  window.addEventListener('hashchange', openFromHash);
  if (location.hash) window.addEventListener('load', openFromHash, { once: true });

  /* ---------- FAQ: copy link + feedback (works on the FAQ page and the Trust Center FAQ) ---------- */
  $$('[data-copy-q]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.faq-item');
      var base = ((doc.querySelector('link[rel="canonical"]') || {}).href || location.href).split('#')[0];
      copy(base + '#' + item.id);
    });
  });
  $$('[data-helpful]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var tools = btn.closest('.faq-tools');
      $$('[data-helpful]', tools).forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
      var msg = $('.faq-thanks', tools);
      if (msg) msg.textContent = 'Thanks for the feedback.';
      // Analytics hook: pushes to Google Tag Manager's dataLayer only if it exists on the page
      if (window.dataLayer) window.dataLayer.push({ event: 'faq_feedback', question: btn.closest('.faq-item').id, helpful: btn.getAttribute('data-helpful') });
    });
  });

  /* ---------- FAQ page: category menu + instant search ---------- */
  var faqRoot = $('[data-faq]');
  if (!faqRoot) return;
  var groups = $$('.faq-group', faqRoot);
  var catLinks = $$('.faq-cats a[href^="#"]');
  var input = $('#faq-search');
  var results = $('.faq-results');
  var empty = $('.faq-empty');
  spy(catLinks, '-25% 0px -65% 0px', function (a) {
    var list = a && a.closest('ul');
    if (list && list.scrollWidth > list.clientWidth) list.scrollTo({ left: Math.max(0, a.offsetLeft - 16), behavior: 'smooth' });
  });

  // Keep the original question text so highlights can be removed cleanly
  var items = $$('.faq-item', faqRoot).map(function (el) {
    var h = $('summary h3', el);
    return { el: el, h: h, q: h.textContent, text: el.textContent.toLowerCase() };
  });
  var escapeRe = function (s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); };
  var escapeHtml = function (s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  var apply = function () {
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    items.forEach(function (it) {
      var hit = !q || it.text.indexOf(q) !== -1;
      it.el.hidden = !hit;
      if (hit) shown++;
      it.h.innerHTML = q && hit ? escapeHtml(it.q).replace(new RegExp('(' + escapeRe(escapeHtml(q)) + ')', 'ig'), '<mark class="hl">$1</mark>') : escapeHtml(it.q);
    });
    groups.forEach(function (g) {
      var visible = $$('.faq-item', g).filter(function (i) { return !i.hidden; }).length;
      g.hidden = visible === 0;
      var link = $('.faq-cats a[href="#' + g.id + '"] .n');
      if (link) link.textContent = visible;
    });
    if (empty) empty.classList.toggle('is-visible', shown === 0);
    if (results) results.textContent = q ? shown + (shown === 1 ? ' answer' : ' answers') + ' for "' + input.value.trim() + '"' : '';
  };
  if (input) {
    input.addEventListener('input', apply);
    doc.addEventListener('keydown', function (e) {
      var tag = (e.target.tagName || '').toLowerCase();
      if (e.key === '/' && tag !== 'input' && tag !== 'textarea' && tag !== 'select') { e.preventDefault(); input.focus(); }
    });
  }
  var reset = $('[data-faq-reset]');
  if (reset) reset.addEventListener('click', function () { input.value = ''; apply(); input.focus(); });
})();
