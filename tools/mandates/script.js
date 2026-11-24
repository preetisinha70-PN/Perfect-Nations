/* The three mandates, v2.0: what moves, and only when it can be seen. ROOT is replaced by the page's root id. */
(function () {
  var R = document.getElementById('ROOT');
  if (!R) { return; }
  R.classList.add('md-js');
  var still = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false;
  var parts = R.querySelectorAll('.md-io, .md-rise');
  var i;
  /* figures that count up: each .md-n holds its real figure; with motion allowed it starts from data-from (or 0)
     and counts to the figure when its band comes on screen */
  var nums = R.querySelectorAll('.md-n');
  if (!still) {
    for (i = 0; i < nums.length; i++) {
      nums[i].setAttribute('data-to', nums[i].textContent);
      nums[i].textContent = nums[i].getAttribute('data-from') || '0';
    }
  }
  function count(el) {
    if (still || el.getAttribute('data-done')) { return; }
    el.setAttribute('data-done', '1');
    var to = parseInt(el.getAttribute('data-to'), 10);
    var from = parseInt(el.getAttribute('data-from') || '0', 10);
    var start = null;
    function step(ts) {
      if (start === null) { start = ts; }
      var p = Math.min(1, (ts - start) / 2400);
      el.textContent = String(Math.round(from + (to - from) * (1 - Math.pow(1 - p, 4))));
      if (p < 1) { window.requestAnimationFrame(step); }
    }
    window.requestAnimationFrame(step);
  }
  function show(el) {
    el.classList.add('is-in');
    var n = el.querySelectorAll('.md-n');
    for (var j = 0; j < n.length; j++) { count(n[j]); }
  }
  if (still || !('IntersectionObserver' in window)) {
    for (i = 0; i < parts.length; i++) { show(parts[i]); }
  } else {
    var io = new IntersectionObserver(function (seen) {
      seen.forEach(function (e) {
        if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
      });
    }, { threshold: 0.2 });
    for (i = 0; i < parts.length; i++) { io.observe(parts[i]); }
  }
  /* the light that follows the cursor across the hero (laptops only) */
  var hero = R.querySelector('.md-hero');
  var fine = window.matchMedia ? window.matchMedia('(hover: hover) and (pointer: fine)').matches : false;
  if (hero ? (fine ? !still : false) : false) {
    hero.addEventListener('pointermove', function (e) {
      var b = hero.getBoundingClientRect();
      hero.style.setProperty('--mx', ((e.clientX - b.left) / b.width * 100).toFixed(1) + '%');
      hero.style.setProperty('--my', ((e.clientY - b.top) / b.height * 100).toFixed(1) + '%');
    });
  }
  /* deal tombstones: a tap, Enter or Space turns the card over */
  function turn(t) {
    var on = !t.classList.contains('is-turned');
    t.classList.toggle('is-turned', on);
    t.setAttribute('aria-pressed', on ? 'true' : 'false');
  }
  R.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('.md-tomb') : null;
    if (!t || e.target.closest('a')) { return; }
    turn(t);
  });
  R.addEventListener('keydown', function (e) {
    var t = e.target;
    if (!t.classList || !t.classList.contains('md-tomb')) { return; }
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); turn(t); }
  });
})();
