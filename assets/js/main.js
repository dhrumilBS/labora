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
