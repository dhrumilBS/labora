/*!
 * Labora landing page
 * Vanilla JS, no dependencies. Loaded with `defer`.
 */
(function () {
  'use strict';

  var doc = document;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var desktopNav = window.matchMedia('(min-width: 1025px)');
  var hasIO = 'IntersectionObserver' in window;

  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function onMQChange(mq, fn) {
    if (mq.addEventListener) mq.addEventListener('change', fn); else if (mq.addListener) mq.addListener(fn);
  }

  /* ---------- Hero: product visual entrance (text is never hidden, protecting LCP) ---------- */
  var hero = $('.hero');
  if (hero) requestAnimationFrame(function () { hero.classList.add('is-loaded'); });

  /* ---------- Sticky header state (rAF-throttled) ---------- */
  var header = $('.site-header');
  var ticking = false;
  function updateHeader() {
    header.classList.toggle('is-scrolled', window.scrollY > 8);
    ticking = false;
  }
  if (header) {
    // First read waits for a frame: reading scrollY before the initial layout forces a full
    // synchronous layout of the page inside this script (seen as a long task on slow phones)
    requestAnimationFrame(updateHeader);
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(updateHeader); }
    }, { passive: true });
  }

  /* ---------- Desktop dropdowns ---------- */
  var dropdowns = $$('[data-dropdown]');
  var closeTimer;

  function setOpen(item, open) {
    item.classList.toggle('is-open', open);
    var btn = $('.nav-link', item);
    if (btn) btn.setAttribute('aria-expanded', String(open));
  }
  function closeAll(except) {
    dropdowns.forEach(function (i) { if (i !== except) setOpen(i, false); });
  }

  dropdowns.forEach(function (item) {
    var btn = $('.nav-link', item);
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = !item.classList.contains('is-open');
      closeAll(item);
      setOpen(item, open);
    });
    item.addEventListener('mouseenter', function () {
      if (!desktopNav.matches) return;
      clearTimeout(closeTimer);
      closeAll(item);
      setOpen(item, true);
    });
    item.addEventListener('mouseleave', function () {
      if (!desktopNav.matches) return;
      closeTimer = setTimeout(function () { setOpen(item, false); }, 160);
    });
    item.addEventListener('focusout', function (e) {
      if (!item.contains(e.relatedTarget)) setOpen(item, false);
    });
  });
  doc.addEventListener('click', function () { closeAll(); });

  /* ---------- Mobile menu: focus trap, inert background, Escape to close ---------- */
  var toggle = $('.menu-toggle');
  var menu = $('#mobile-menu');
  var background = [$('#main'), $('.site-footer'), $('#mobile-cta')].filter(Boolean);

  function menuIsOpen() { return toggle && toggle.getAttribute('aria-expanded') === 'true'; }

  function toggleMenu(open, returnFocus) {
    if (!menu || !toggle) return;
    menu.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    doc.body.classList.toggle('menu-open', open);
    doc.documentElement.classList.toggle('menu-open', open);
    if (lenis) { if (open) lenis.stop(); else lenis.start(); }
    background.forEach(function (el) {
      if (open) el.setAttribute('inert', ''); else el.removeAttribute('inert');
    });
    if (open) {
      var first = $('summary, a', menu);
      if (first) first.focus();
    } else if (returnFocus) {
      toggle.focus();
    }
  }

  if (toggle && menu) {
    toggle.addEventListener('click', function () { toggleMenu(!menuIsOpen()); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) toggleMenu(false); });
    menu.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var focusables = $$('summary, a, button', menu).concat([toggle])
        .filter(function (el) { return el.offsetParent !== null; });
      var first = focusables[0], last = focusables[focusables.length - 1];
      if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    onMQChange(desktopNav, function (e) { if (e.matches) toggleMenu(false); });
  }

  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var openItem = dropdowns.filter(function (i) { return i.classList.contains('is-open'); })[0];
    if (openItem) { setOpen(openItem, false); $('.nav-link', openItem).focus(); }
    if (menuIsOpen()) toggleMenu(false, true);
  });

  /* ---------- Scroll reveals (one shared observer) ---------- */
  var reveals = $$('.reveal');
  if (hasIO && !reduceMotion) {
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealIO.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { revealIO.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Trusted brands slider: animate only while on screen ---------- */
  $$('[data-marquee]').forEach(function (el) {
    if (!hasIO || reduceMotion) return;
    new IntersectionObserver(function (entries) {
      el.classList.toggle('in-view', entries[0].isIntersecting);
    }).observe(el);
  });

  /* ---------- Testimonial slider: scroll-snap track + arrows, counter, gentle autoplay ----------
     Swipe and trackpad use native scrolling. Autoplay only while on screen and not hovered,
     focused, or touched; off for reduced motion. */
  $$('[data-slider]').forEach(function (slider) {
    var track = $('.t-track', slider);
    var slides = $$('.t-slide', slider);
    var count = $('.t-count', slider);
    if (!track || slides.length < 2) return;
    var current = 0, timer = null, paused = false, visible = false, scrollTick = false, anim = 0;

    // Own easing instead of scrollTo({behavior:'smooth'}), which mandatory scroll-snap can cancel
    // or redirect; snapping is paused for the 450 ms animation, then restored.
    function animateTo(x) {
      cancelAnimationFrame(anim);
      if (reduceMotion) { track.scrollLeft = x; return; }
      var from = track.scrollLeft, dist = x - from, t0 = 0;
      track.style.scrollSnapType = 'none';
      anim = requestAnimationFrame(function step(ts) {
        if (!t0) t0 = ts;
        var p = Math.min(1, (ts - t0) / 450);
        track.scrollLeft = from + dist * (1 - Math.pow(1 - p, 3));
        if (p < 1) anim = requestAnimationFrame(step); else track.style.scrollSnapType = '';
      });
    }
    function go(i) {
      current = (i + slides.length) % slides.length;
      animateTo(slides[current].offsetLeft - slides[0].offsetLeft);
    }
    function update() {
      var i = Math.round(track.scrollLeft / (track.clientWidth || 1));
      current = Math.max(0, Math.min(slides.length - 1, i));
      if (count) count.textContent = (current + 1) + ' / ' + slides.length;
      scrollTick = false;
    }
    function stop() { clearInterval(timer); timer = null; }
    function start() {
      stop();
      if (reduceMotion || paused || !visible) return;
      timer = setInterval(function () { go(current + 1); }, 7000);
    }

    $('.t-prev', slider).addEventListener('click', function () { go(current - 1); start(); });
    $('.t-next', slider).addEventListener('click', function () { go(current + 1); start(); });
    track.addEventListener('scroll', function () {
      if (!scrollTick) { scrollTick = true; requestAnimationFrame(update); }
    }, { passive: true });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(current + 1); }
      else if (e.key === 'ArrowLeft') { e.preventDefault(); go(current - 1); }
    });
    ['mouseenter', 'focusin', 'touchstart'].forEach(function (t) {
      slider.addEventListener(t, function () { paused = true; stop(); }, { passive: true });
    });
    ['mouseleave', 'focusout'].forEach(function (t) {
      slider.addEventListener(t, function (e) {
        if (t === 'focusout' && slider.contains(e.relatedTarget)) return;
        paused = false; start();
      });
    });
    if (hasIO) {
      new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; start(); }, { threshold: 0.4 }).observe(slider);
    }
  });

  /* ---------- Product tour: muted autoplay loop once on screen, custom play/pause ----------
     The file is only requested after window load and when the frame nears the viewport, so it never
     competes with the hero (LCP). Reduced motion or Data Saver: no autoplay, the button starts it. */
  $$('[data-video]').forEach(function (frame) {
    var video = $('video', frame);
    var btn = $('.video-toggle', frame);
    if (!video || !btn) return;
    var conn = navigator.connection || {};
    var autoplay = !reduceMotion && !conn.saveData;
    var userPaused = false, inView = false, loaded = false;

    function load() {
      if (loaded) return;
      loaded = true;
      // Full-clarity 1080p everywhere except phone-width frames (and Data Saver), where 720p is already sharp
      video.src = frame.getAttribute(frame.clientWidth > 640 && !conn.saveData ? 'data-src-1080' : 'data-src-720');
      video.preload = 'auto';
    }
    function play() {
      load();
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    }
    function sync() {
      var playing = !video.paused;
      frame.classList.toggle('is-playing', playing);
      btn.setAttribute('aria-label', playing ? 'Pause product tour' : 'Play product tour');
    }

    video.muted = true; // no audio track; muted keeps autoplay allowed everywhere
    video.addEventListener('playing', function () { frame.classList.add('is-ready'); sync(); });
    video.addEventListener('pause', sync);
    btn.hidden = false;
    btn.addEventListener('click', function () {
      if (video.paused) { userPaused = false; play(); } else { userPaused = true; video.pause(); }
    });

    if (!autoplay || !hasIO) return;
    // Arm autoplay on the visitor's first scroll/tap/key, or 3.5 s after load, so the file never
    // downloads inside the page-load window (it would compete with the hero image on slow networks).
    var armed = false;
    var arm = function () {
      if (armed) return;
      armed = true;
      ['wheel', 'touchstart', 'keydown', 'pointerdown', 'scroll'].forEach(function (t) { window.removeEventListener(t, arm); });
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
        if (inView && !userPaused) play();
        else if (!inView && !video.paused) video.pause();
      }, { threshold: 0.2 }).observe(frame);
    };
    var onLoad = function () {
      ['wheel', 'touchstart', 'keydown', 'pointerdown', 'scroll'].forEach(function (t) { window.addEventListener(t, arm, { passive: true, once: true }); });
      setTimeout(arm, 3500);
    };
    if (doc.readyState === 'complete') onLoad(); else window.addEventListener('load', onLoad, { once: true });
  });

  /* ---------- Smooth wheel scrolling (Lenis, bundled) ----------
     Desktop mouse/trackpad only; touch keeps native momentum. Off for reduced motion.
     Started after load so it adds nothing to the critical path. */
  var lenis = null;
  if (window.Lenis && !reduceMotion && window.matchMedia('(pointer: fine)').matches) {
    var startLenis = function () {
      lenis = new window.Lenis({
        lerp: 0.11,
        autoRaf: true,
        anchors: true // honours the CSS scroll-padding-top that clears the sticky header
      });
    };
    if (doc.readyState === 'complete') startLenis(); else window.addEventListener('load', startLenis, { once: true });
  }

  /* ---------- Mobile sticky CTA: hidden over the hero and the demo form ---------- */
  var mobileCta = $('#mobile-cta');
  var demo = $('#demo');
  if (mobileCta && hero && hasIO) {
    var heroVisible = true, demoVisible = false;
    var updateCta = function () {
      var show = !heroVisible && !demoVisible;
      mobileCta.classList.toggle('is-visible', show);
      if (show) mobileCta.removeAttribute('aria-hidden'); else mobileCta.setAttribute('aria-hidden', 'true');
      $$('a', mobileCta).forEach(function (a) { a.tabIndex = show ? 0 : -1; });
    };
    updateCta();
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; updateCta(); }).observe(hero);
    if (demo) new IntersectionObserver(function (e) { demoVisible = e[0].isIntersecting; updateCta(); }).observe(demo);
  }

  /* ---------- Demo request form ---------- */
  var form = $('#demo-form');
  var status = $('#form-status');
  var formError = $('#form-error');
  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function validateField(el) {
    var value = el.value.trim();
    var valid = !el.required || (value !== '' && (el.type !== 'email' || emailRe.test(value)));
    var err = $('#' + el.id + '-err');
    el.closest('.field').classList.toggle('has-error', !valid);
    el.setAttribute('aria-invalid', String(!valid));
    if (err) {
      if (valid) el.removeAttribute('aria-describedby'); else el.setAttribute('aria-describedby', err.id);
    }
    return valid;
  }

  function showFormError(msg) {
    if (!formError) return;
    formError.textContent = msg;
    formError.classList.toggle('is-visible', !!msg);
  }

  if (form && status) {
    var fields = $$('input[required], select[required]', form);
    var submitBtn = $('button[type="submit"]', form);
    var submitLabel = submitBtn.textContent;

    fields.forEach(function (el) {
      el.addEventListener('blur', function () { if (el.value) validateField(el); });
      el.addEventListener(el.tagName === 'SELECT' ? 'change' : 'input', function () {
        if (el.closest('.field').classList.contains('has-error')) validateField(el);
      });
    });

    var showSuccess = function () {
      form.hidden = true;
      status.classList.add('is-visible');
      status.focus();
      if (window.dataLayer) window.dataLayer.push({ event: 'demo_request_submitted' });
      // Let the confirmation register for a moment, then open the thank-you page. Details travel in
      // sessionStorage, never the URL, so no personal data reaches server logs or analytics.
      var thanks = form.getAttribute('data-thanks');
      if (!thanks) return;
      try {
        sessionStorage.setItem('labora_thanks', JSON.stringify({
          form: 'demo', name: form.elements.namedItem('name').value.trim().split(/\s+/)[0].slice(0, 40), ts: Date.now()
        }));
      } catch (e) {}
      setTimeout(function () { location.assign(thanks); }, 1500);
    };
    var resetButton = function () {
      submitBtn.disabled = false;
      submitBtn.textContent = submitLabel;
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      showFormError('');

      var firstInvalid = null;
      fields.forEach(function (el) { if (!validateField(el) && !firstInvalid) firstInvalid = el; });
      if (firstInvalid) { firstInvalid.focus(); return; }

      // Honeypot: bots fill hidden fields. Pretend success, send nothing.
      var hp = form.elements.website;
      if (hp && hp.value) { showSuccess(); return; }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';

      var endpoint = form.getAttribute('data-endpoint');
      if (!endpoint) { setTimeout(showSuccess, 500); return; } // demo mode until an endpoint is set

      var controller = 'AbortController' in window ? new AbortController() : null;
      var timeout = setTimeout(function () { if (controller) controller.abort(); }, 15000);

      fetch(endpoint, {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: new FormData(form),
        signal: controller ? controller.signal : undefined
      }).then(function (res) {
        clearTimeout(timeout);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        showSuccess();
      }).catch(function () {
        clearTimeout(timeout);
        resetButton();
        showFormError('Your request was not sent. Check your connection and try again.');
      });
    });
  }

  /* ---------- Cookie consent ----------
     One first-party cookie (labora_consent) stores the visitor's choice. Nothing else is set today.
     Future scripts that need consent are added as <script type="text/plain" data-consent="analytics" src="...">
     and only run once that category is allowed. API: window.laboraConsent.get() / .has('analytics') / .open() */
  var consent = (function () {
    var NAME = 'labora_consent', VERSION = 1, MAX_AGE = 180 * 24 * 3600;
    // What each category is for and exactly what it stores. Keep in sync with the cookie policy page.
    var CATS = [
      { id: 'necessary', title: 'Strictly necessary', locked: true,
        desc: 'Needed for the site to work. They cannot be switched off.',
        items: [['labora_consent', 'Remembers the cookie choices you make here', '6 months']] },
      { id: 'analytics', title: 'Analytics',
        desc: 'Help us understand which pages are useful, through visit statistics.', items: [] },
      { id: 'marketing', title: 'Marketing',
        desc: 'Measure our advertising and show relevant ads on other sites.', items: [] }
    ];
    var box = null, lastFocus = null;

    function read() {
      var m = document.cookie.match(new RegExp('(?:^|; )' + NAME + '=([^;]*)'));
      if (!m) return null;
      try { var v = JSON.parse(decodeURIComponent(m[1])); return v && v.v === VERSION ? v : null; } catch (e) { return null; }
    }
    function write(choice) {
      choice.v = VERSION;
      choice.ts = new Date().toISOString();
      document.cookie = NAME + '=' + encodeURIComponent(JSON.stringify(choice)) + '; Max-Age=' + MAX_AGE +
        '; Path=/; SameSite=Lax' + (location.protocol === 'https:' ? '; Secure' : '');
    }
    function apply(choice) {
      // Run scripts held back until their category was allowed
      $$('script[type="text/plain"][data-consent]').forEach(function (old) {
        if (!choice[old.getAttribute('data-consent')]) return;
        var s = document.createElement('script');
        Array.prototype.forEach.call(old.attributes, function (a) { if (a.name !== 'type' && a.name !== 'data-consent') s.setAttribute(a.name, a.value); });
        s.text = old.text;
        old.parentNode.replaceChild(s, old);
      });
      // Remove cookies of categories that were switched off
      CATS.forEach(function (c) {
        if (c.locked || choice[c.id]) return;
        c.items.forEach(function (it) { document.cookie = it[0] + '=; Max-Age=0; Path=/'; });
      });
      if (window.dataLayer) window.dataLayer.push({ event: 'consent_update', analytics: !!choice.analytics, marketing: !!choice.marketing });
      document.dispatchEvent(new CustomEvent('labora:consent', { detail: choice }));
    }
    function save(choice) { write(choice); apply(choice); close(); }

    function policyHref() {
      var a = document.querySelector('a[href$="cookies/"]');
      return a ? a.getAttribute('href') : 'cookies/';
    }
    function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
    function button(cls, label, action) { var b = el('button', 'btn ' + cls, label); b.type = 'button'; b.setAttribute('data-cc', action); return b; }

    function build(current) {
      box = el('section', 'cc');
      box.setAttribute('role', 'dialog');
      box.setAttribute('aria-modal', 'false');
      box.setAttribute('aria-labelledby', 'cc-title');
      box.setAttribute('aria-describedby', 'cc-desc');

      var main = el('div', 'cc-main');
      var h = el('h2', null, 'Your privacy choices'); h.id = 'cc-title'; h.tabIndex = -1;
      var p = el('p', null, 'We use one cookie to remember this choice. With your permission, we may also use analytics and marketing cookies. ');
      p.id = 'cc-desc';
      var link = el('a', null, 'Cookie policy'); link.href = policyHref(); p.appendChild(link);
      var actions = el('div', 'cc-actions');
      actions.appendChild(button('btn--ghost', 'Customize', 'customize'));
      actions.appendChild(button('btn--ghost', 'Deny all', 'deny'));
      actions.appendChild(button('btn--primary', 'Accept all', 'accept'));
      main.appendChild(h); main.appendChild(p); main.appendChild(actions);

      var prefs = el('div', 'cc-prefs'); prefs.hidden = true;
      var ph = el('h2', null, 'Customize cookies'); ph.id = 'cc-prefs-title'; ph.tabIndex = -1;
      prefs.appendChild(ph);
      prefs.appendChild(el('p', 'cc-sub', 'Choose what we may store. You can change this at any time from "Cookie settings" at the bottom of every page.'));
      var list = el('ul', 'cc-cats');
      CATS.forEach(function (c) {
        var li = el('li', 'cc-cat');
        var head = el('div', 'cc-cat-head');
        var label = el('label', 'cc-switch');
        var input = el('input'); input.type = 'checkbox'; input.setAttribute('role', 'switch'); input.name = c.id;
        input.checked = c.locked || !!(current && current[c.id]);
        if (c.locked) { input.disabled = true; input.checked = true; }
        var t = el('span', 'cc-cat-title', c.title);
        label.appendChild(t);
        if (c.locked) label.appendChild(el('span', 'cc-always', 'Always on'));
        label.appendChild(input); label.appendChild(el('span', 'cc-track'));
        head.appendChild(label);
        li.appendChild(head);
        li.appendChild(el('p', 'cc-cat-desc', c.desc));
        var det = el('details', 'cc-store');
        det.appendChild(el('summary', null, 'What we store'));
        if (c.items.length) {
          var tbl = el('table'); var tb = el('tbody');
          var hr = el('tr'); ['Cookie', 'Purpose', 'Kept for'].forEach(function (x) { var th = el('th', null, x); th.scope = 'col'; hr.appendChild(th); });
          var thead = el('thead'); thead.appendChild(hr); tbl.appendChild(thead);
          c.items.forEach(function (it) { var tr = el('tr'); it.forEach(function (x) { tr.appendChild(el('td', null, x)); }); tb.appendChild(tr); });
          tbl.appendChild(tb); det.appendChild(tbl);
        } else {
          det.appendChild(el('p', null, 'Nothing today. This site does not use any ' + c.title.toLowerCase() + ' tools. If we add one, it will run only with your permission.'));
        }
        li.appendChild(det);
        list.appendChild(li);
      });
      prefs.appendChild(list);
      var pa = el('div', 'cc-actions');
      pa.appendChild(button('btn--ghost', 'Deny all', 'deny'));
      pa.appendChild(button('btn--ghost', 'Save choices', 'save'));
      pa.appendChild(button('btn--primary', 'Accept all', 'accept'));
      prefs.appendChild(pa);

      box.appendChild(main); box.appendChild(prefs);
      box.addEventListener('click', function (e) {
        var b = e.target.closest('[data-cc]'); if (!b) return;
        var act = b.getAttribute('data-cc');
        if (act === 'accept') save({ necessary: true, analytics: true, marketing: true });
        else if (act === 'deny') save({ necessary: true, analytics: false, marketing: false });
        else if (act === 'save') save({ necessary: true, analytics: prefs.querySelector('[name="analytics"]').checked, marketing: prefs.querySelector('[name="marketing"]').checked });
        else if (act === 'customize') { main.hidden = true; prefs.hidden = false; box.setAttribute('aria-labelledby', 'cc-prefs-title'); ph.focus(); }
      });
      box.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !prefs.hidden && read()) { close(); }
        else if (e.key === 'Escape' && !prefs.hidden) { prefs.hidden = true; main.hidden = false; box.setAttribute('aria-labelledby', 'cc-title'); h.focus(); }
      });
      document.body.appendChild(box);
      requestAnimationFrame(function () { box.classList.add('is-in'); });
    }
    function open(opts) {
      if (box) box.remove();
      lastFocus = document.activeElement;
      build(read());
      if (opts && opts.customize) box.querySelector('[data-cc="customize"]').click();
      else if (opts && opts.focus) box.querySelector('#cc-title').focus();
    }
    function close() {
      if (!box) return;
      var b = box; box = null;
      b.classList.remove('is-in');
      setTimeout(function () { b.remove(); }, 250);
      if (lastFocus && lastFocus.focus && lastFocus !== document.body) lastFocus.focus();
    }

    var saved = read();
    if (saved) apply(saved);
    else if (navigator.globalPrivacyControl) { write({ necessary: true, analytics: false, marketing: false, gpc: true }); apply(read()); }
    else window.addEventListener('load', function () { setTimeout(function () { if (!read()) open(); }, 600); }, { once: true });

    document.addEventListener('click', function (e) {
      var t = e.target.closest('[data-cookie-settings]');
      if (t) { e.preventDefault(); open({ customize: true }); }
    });
    return { get: read, has: function (c) { var v = read(); return !!(v && v[c]); }, open: function () { open({ customize: true }); } };
  })();
  window.laboraConsent = consent;

  /* ---------- Footer year ---------- */
  var year = $('[data-year]');
  if (year) year.textContent = String(new Date().getFullYear());
})();
