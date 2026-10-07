// ARCHIVE (archive/vibecode/): blocks moved out of assets/js/main.js on Oct 7, 2026. They only animated the archived
// workflow mockup ([data-workflow], ../removed-sections.html) and integration network (.integ-net, homepage-sections.html).
// To restore, paste a block back inside the main.js IIFE (it uses $, $$, hasIO, and reduceMotion from there).

  /* ---------- Workflow builder mockup: step highlight while visible ---------- */
  var chain = $('[data-workflow]');
  if (chain) {
    var wfNodes = $$('.wf-node:not(.is-trigger)', chain);
    if (!reduceMotion && hasIO && wfNodes.length) {
      var wfIdx = 0, wfTimer = null;
      var wfStep = function () {
        wfNodes.forEach(function (n) { n.classList.remove('is-active'); });
        wfNodes[wfIdx].classList.add('is-active');
        wfIdx = (wfIdx + 1) % wfNodes.length;
      };
      new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting && !wfTimer) { wfStep(); wfTimer = setInterval(wfStep, 1500); }
        else if (!entries[0].isIntersecting && wfTimer) { clearInterval(wfTimer); wfTimer = null; }
      }, { threshold: 0.4 }).observe(chain);
    } else if (wfNodes[1]) {
      wfNodes[1].classList.add('is-active');
    }
  }

  /* ---------- Integration network: run line animation only while on screen ---------- */
  var net = $('.integ-net');
  if (net && hasIO && !reduceMotion) {
    new IntersectionObserver(function (entries) {
      net.classList.toggle('in-view', entries[0].isIntersecting);
    }).observe(net);
  }
