/*!
 * Labora blog: hub filters/search, article reading progress, table of contents, sharing, newsletter.
 * Vanilla JS, no dependencies. Loaded with `defer` after main.min.js.
 */
(function () {
  'use strict';
  var doc = document;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(s, c) { return (c || doc).querySelector(s); }
  function $$(s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); }

  /* ---------- Hub: topic filter + search ---------- */
  var grid = $('[data-posts]');
  if (grid) {
    var posts = $$('.post', grid);
    var topics = $$('.topic');
    var input = $('#blog-search');
    var count = $('[data-count]');
    var empty = $('[data-empty]');
    var mostRead = $('.most-read', grid);
    var featured = $('[data-featured]');
    var active = 'all';

    var apply = function () {
      var q = (input ? input.value : '').trim().toLowerCase();
      var shown = 0;
      posts.forEach(function (p) {
        var okTopic = active === 'all' || p.getAttribute('data-topic') === active;
        var okText = !q || p.textContent.toLowerCase().indexOf(q) !== -1;
        p.hidden = !(okTopic && okText);
        if (!p.hidden) shown++;
      });
      var filtering = active !== 'all' || !!q;
      if (mostRead) mostRead.hidden = filtering;
      if (featured) featured.hidden = filtering;
      if (empty) empty.classList.toggle('is-visible', shown === 0);
      if (count) count.textContent = shown + (shown === 1 ? ' article' : ' articles');
    };

    topics.forEach(function (btn) {
      btn.addEventListener('click', function () {
        active = btn.getAttribute('data-filter');
        topics.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        apply();
      });
    });
    if (input) {
      input.addEventListener('input', apply);
      // "/" focuses search, like most product docs and blogs
      doc.addEventListener('keydown', function (e) {
        var tag = (e.target.tagName || '').toLowerCase();
        if (e.key === '/' && tag !== 'input' && tag !== 'textarea' && tag !== 'select') { e.preventDefault(); input.focus(); }
      });
    }
    var reset = $('[data-reset]');
    if (reset) reset.addEventListener('click', function () {
      active = 'all';
      if (input) input.value = '';
      topics.forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-filter') === 'all')); });
      apply();
    });
  }

  /* ---------- Article: reading progress (rAF-throttled, transform only) ---------- */
  var article = $('[data-article]');
  var bar = $('.read-progress span');
  if (article && bar) {
    var tick = false;
    var update = function () {
      var r = article.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 1;
      bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
      tick = false;
    };
    window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener('resize', update);
    requestAnimationFrame(update);
  }

  /* ---------- Article: highlight the current section in the table of contents ---------- */
  var tocLinks = $$('.toc a[href^="#"]');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute('href').slice(1)] = a; });
    var headings = Object.keys(map).map(function (id) { return doc.getElementById(id); }).filter(Boolean);
    var setActive = function (id) { tocLinks.forEach(function (a) { a.classList.toggle('is-active', a === map[id]); }); };
    // A heading counts as "current" once it crosses the upper part of the screen
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) setActive(e.target.id); });
    }, { rootMargin: '-15% 0px -75% 0px' });
    headings.forEach(function (h) { io.observe(h); });
    // On small screens the contents list is collapsible: close it after choosing a section
    var toc = $('.toc');
    tocLinks.forEach(function (a) {
      a.addEventListener('click', function () { if (toc && window.matchMedia('(max-width: 1024px)').matches) toc.open = false; });
    });
  }

  /* ---------- Article: share ---------- */
  var toast = $('.toast');
  var showToast = function (msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('is-visible');
    clearTimeout(showToast.t);
    showToast.t = setTimeout(function () { toast.classList.remove('is-visible'); }, 2200);
  };
  $$('[data-copy-link]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var url = (doc.querySelector('link[rel="canonical"]') || {}).href || location.href;
      if (navigator.share && window.matchMedia('(pointer: coarse)').matches) {
        navigator.share({ title: doc.title, url: url }).catch(function () {});
        return;
      }
      var done = function () { showToast('Link copied'); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { showToast(url); });
      else showToast(url);
    });
  });

  /* ---------- Newsletter (demo mode until data-endpoint is set) ---------- */
  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  $$('[data-newsletter]').forEach(function (form) {
    var field = $('input[type="email"]', form);
    var msg = $('.nl-msg', form.parentNode);
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = field.value.trim();
      if (!emailRe.test(v)) {
        field.setAttribute('aria-invalid', 'true');
        if (msg) { msg.textContent = 'Enter a valid work email.'; msg.className = 'nl-msg is-error'; }
        field.focus();
        return;
      }
      field.removeAttribute('aria-invalid');
      var ok = function () { form.reset(); if (msg) { msg.textContent = 'You are subscribed. Watch your inbox for the next issue.'; msg.className = 'nl-msg is-ok'; } };
      var endpoint = form.getAttribute('data-endpoint');
      if (!endpoint) { ok(); return; }
      fetch(endpoint, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form) })
        .then(function (r) { if (!r.ok) throw new Error(); ok(); })
        .catch(function () { if (msg) { msg.textContent = 'That did not go through. Try again in a moment.'; msg.className = 'nl-msg is-error'; } });
    });
  });

  if (reduceMotion) doc.documentElement.classList.add('reduce-motion');
})();
