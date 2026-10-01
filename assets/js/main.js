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
    updateHeader();
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

  /* ---------- Integration network: run line animation only while on screen ---------- */
  var net = $('.integ-net');
  if (net && hasIO && !reduceMotion) {
    new IntersectionObserver(function (entries) {
      net.classList.toggle('in-view', entries[0].isIntersecting);
    }).observe(net);
  }

  /* ---------- Trusted brands slider: animate only while on screen ---------- */
  $$('[data-marquee]').forEach(function (el) {
    if (!hasIO || reduceMotion) return;
    new IntersectionObserver(function (entries) {
      el.classList.toggle('in-view', entries[0].isIntersecting);
    }).observe(el);
  });

  /* ---------- Product tour: swap the poster for the video only on play ---------- */
  $$('[data-video]').forEach(function (frame) {
    var btn = $('.video-play', frame);
    if (!btn) return;
    btn.addEventListener('click', function () {
      var conn = navigator.connection || {};
      var px = frame.clientWidth * (window.devicePixelRatio || 1);
      var base = frame.getAttribute(px > 1280 && !conn.saveData ? 'data-src-1080' : 'data-src-720');
      var img = $('img', btn);
      var video = doc.createElement('video');
      video.controls = true;
      video.playsInline = true;
      video.muted = true; // the tour has no audio track; muted also guarantees play() is allowed
      video.preload = 'auto';
      video.width = 1600;
      video.height = 900;
      if (img) video.poster = img.currentSrc || img.src;
      video.setAttribute('aria-label', btn.getAttribute('aria-label').replace(/^Play /, ''));
      video.src = base + '.mp4';
      btn.replaceWith(video);
      video.focus();
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
    });
  });

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

  /* ---------- Footer year ---------- */
  var year = $('[data-year]');
  if (year) year.textContent = String(new Date().getFullYear());
})();
