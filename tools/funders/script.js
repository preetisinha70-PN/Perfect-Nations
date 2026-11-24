/* Perfect Nations - For Funders v2.0. No "less than" sign is written in this script, so the WordPress
   formatter never takes any part of it for a tag. Every text a visitor reads is set with textContent. */
(function(){
  'use strict';
  var root = document.getElementById('pn-fund');
  if (!root || root.getAttribute('data-ready')) { return; }
  root.setAttribute('data-ready', '1');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function q(s, el){ return (el || root).querySelector(s); }
  function qa(s, el){ return Array.prototype.slice.call((el || root).querySelectorAll(s)); }
  function el(tag, cls, text){ var e = document.createElement(tag); if (cls) { e.className = cls; } if (text != null) { e.textContent = text; } return e; }
  function safe(u){ return typeof u === 'string' && /^https:\/\/[^\s"'()]+$/.test(u) && u.indexOf('>') === -1; }
  function ext(u, text){ var a = el('a', '', text); if (safe(u)) { a.href = u; a.target = '_blank'; a.rel = 'noopener noreferrer'; } return a; }
  function comma(n){ return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function getJSON(urls, done, fail){
    if (!window.fetch) { if (fail) { fail(); } return; }
    (function get(n){
      if (n >= urls.length || !urls[n]) { if (fail) { fail(); } return; }
      fetch(urls[n], { cache: 'no-cache' }).then(function(r){ if (!r.ok) { throw new Error(String(r.status)); } return r.json(); })
        .then(done).catch(function(){ get(n + 1); });
    })(0);
  }
  function idle(fn){ if ('requestIdleCallback' in window) { window.requestIdleCallback(fn, { timeout: 3000 }); } else { setTimeout(fn, 1200); } }

  /* ---------- 01 the hero: capital moving toward the nations ---------- */
  (function(){
    var c = q('.pf-flow'), hero = q('.pf-hero');
    if (!c || !c.getContext) { return; }
    var x = c.getContext('2d'), W = 0, H = 0, dpr = 1, streams = [], dots = [], on = true, raf = 0, t0 = 0;
    function rnd(a, b){ return a + Math.random() * (b - a); }
    function build(){
      var r = hero.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      W = Math.max(1, r.width); H = Math.max(1, r.height);
      c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
      x.setTransform(dpr, 0, 0, dpr, 0, 0);
      var small = 700 > W, n = small ? 9 : 16, k;
      streams = []; dots = [];
      for (k = 0; n > k; k++) {
        var y0 = rnd(.45, 1.1) * H, y1 = rnd(-.1, .75) * H;
        streams.push({ a: [-.05 * W, y0], b: [rnd(.25, .45) * W, y0 - rnd(-.2, .35) * H], c: [rnd(.55, .8) * W, y1 + rnd(-.15, .3) * H], d: [1.05 * W, y1], w: rnd(.5, 1.2) });
      }
      var m = small ? 34 : 80;
      for (k = 0; m > k; k++) { dots.push({ s: k % n, t: Math.random(), v: rnd(.016, .04), r: rnd(.6, 1.7) }); }
    }
    function at(s, t){
      var u = 1 - t, a = u * u * u, b = 3 * u * u * t, cc = 3 * u * t * t, d = t * t * t;
      return [a * s.a[0] + b * s.b[0] + cc * s.c[0] + d * s.d[0], a * s.a[1] + b * s.b[1] + cc * s.c[1] + d * s.d[1]];
    }
    function draw(dt){
      x.clearRect(0, 0, W, H);
      streams.forEach(function(s){
        x.beginPath(); x.moveTo(s.a[0], s.a[1]); x.bezierCurveTo(s.b[0], s.b[1], s.c[0], s.c[1], s.d[0], s.d[1]);
        x.strokeStyle = 'rgba(227,194,88,' + (0.09 * s.w).toFixed(3) + ')'; x.lineWidth = s.w; x.stroke();
      });
      dots.forEach(function(p){
        p.t += p.v * dt; if (p.t > 1) { p.t -= 1; }
        var s = streams[p.s], h = at(s, p.t), tail = at(s, Math.max(0, p.t - 0.035)), fade = Math.sin(Math.PI * p.t);
        x.beginPath(); x.moveTo(tail[0], tail[1]); x.lineTo(h[0], h[1]);
        x.strokeStyle = 'rgba(240,214,143,' + (0.22 * fade).toFixed(3) + ')'; x.lineWidth = p.r * 0.7; x.stroke();
        x.beginPath(); x.arc(h[0], h[1], p.r, 0, 6.2832);
        x.fillStyle = 'rgba(251,231,166,' + (0.6 * fade).toFixed(3) + ')'; x.fill();
      });
    }
    function loop(ts){
      var dt = t0 ? Math.min(0.05, (ts - t0) / 1000) : 0.016; t0 = ts;
      draw(dt); raf = on ? window.requestAnimationFrame(loop) : 0;
    }
    function start(){ if (!raf && on && !still) { t0 = 0; raf = window.requestAnimationFrame(loop); } }
    build();
    if (still) { draw(0); return; }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function(es){ on = es[0].isIntersecting && !document.hidden; if (on) { start(); } }).observe(hero);
    }
    document.addEventListener('visibilitychange', function(){ on = !document.hidden; if (on) { start(); } });
    var rs = 0;
    window.addEventListener('resize', function(){ clearTimeout(rs); rs = setTimeout(function(){ build(); if (still) { draw(0); } }, 200); });
    start();
  })();

  /* the hero figures count up once; the real figures are written in the page for every reader */
  (function(){
    if (still) { return; }
    var bs = qa('.pf-figs b[data-n]');
    var t0 = 0, dur = 1300;
    bs.forEach(function(b){ b.textContent = '0'; });
    function step(ts){
      if (!t0) { t0 = ts; }
      var k = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      bs.forEach(function(b){ b.textContent = comma(e * +b.getAttribute('data-n')); });
      if (1 > k) { window.requestAnimationFrame(step); }
    }
    window.requestAnimationFrame(step);
  })();

  /* ---------- the Capital Wire tape: the newest deals, read live from the wire ---------- */
  (function(){
    var tape = q('.pf-tape'), list = q('.pf-tape__l');
    if (!tape || !list) { return; }
    function loopIt(){
      qa('li[data-copy]', list).forEach(function(li){ list.removeChild(li); });
      var items = qa('li', list), n = items.length;
      items.forEach(function(li){ var c = li.cloneNode(true); c.setAttribute('data-copy', '1'); c.setAttribute('aria-hidden', 'true'); var a = c.querySelector('a'); if (a) { a.tabIndex = -1; } list.appendChild(c); });
      list.style.setProperty('--dur', Math.max(30, n * 6) + 's');
    }
    function render(d){
      if (!d || !d.items || !d.items.length) { return; }
      var keep = d.items.filter(function(i){ return i && safe(i.url) && i.figure && i.nation; });
      if (!keep.length) { return; }
      list.textContent = '';
      keep.forEach(function(i){
        var li = el('li'), a = ext(i.url, '');
        a.appendChild(el('b', '', i.nation)); a.appendChild(el('em', '', i.figure)); a.appendChild(el('span', '', i.line || i.type || ''));
        if (i.signal) { a.appendChild(el('i', '', i.signal)); }
        li.appendChild(a); list.appendChild(li);
      });
      var c = q('.pf-tape__c');
      if (c && d.count && d.count.deals) { c.textContent = comma(d.count.deals) + ' deals in ' + comma(d.count.nations) + ' nations'; }
      loopIt();
    }
    loopIt();
    idle(function(){ getJSON([tape.getAttribute('data-src'), tape.getAttribute('data-mirror')], render); });
  })();

  /* ---------- 02 Match of the week: the Match of this week, the earlier ones a tap away ---------- */
  (function(){
    var box = q('.pf-matches'), slot = q('.pf-m__slot'), more = q('.pf-m__more'), rail = q('.pf-m__rail');
    if (!box || !slot) { return; }
    var all = [], answer = {};
    try { all = JSON.parse(box.textContent) || []; answer = JSON.parse(q('.pf-answer').textContent) || {}; } catch (e) { return; }
    if (!all.length) { return; }
    var d = new Date(), today = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
    var live = all.filter(function(m){ return today >= m.week; });
    if (!live.length) { live = [all[all.length - 1]]; }
    function row(h, title, text){
      var r = el('div', 'pf-m__row'); r.appendChild(el('h4', '', h));
      if (title) { r.appendChild(el('p', 'pf-m__t', title)); }
      if (text) { r.appendChild(el('p', '', text)); }
      return r;
    }
    function card(m){
      var a = el('article', 'pf-m'), l = el('div', 'pf-m__l'), r = el('div', 'pf-m__r'), k = el('p', 'pf-m__k');
      a.setAttribute('data-no', m.no);
      k.appendChild(el('b', '', 'Match No. ' + m.no)); k.appendChild(el('span', '', m.weekText)); l.appendChild(k);
      l.appendChild(el('h3', 'pf-m__n', m.nation)); l.appendChild(el('p', 'pf-m__s', m.standard));
      l.appendChild(el('p', 'pf-m__f', m.figure));
      var cap = el('p', 'pf-m__c', m.caption + '. '); if (safe(m.sourceUrl)) { cap.appendChild(ext(m.sourceUrl, m.source)); } l.appendChild(cap);
      r.appendChild(row('The Solution', m.title, m.advises));
      if (m.proof && m.proof.name) {
        var pr = row('The proof'), p = el('p'), b = el('b', '', m.proof.name), g = el('em', 'pf-gold', m.proof.figure);
        p.appendChild(b); p.appendChild(document.createTextNode(', ' + m.proof.where + ' ' + m.proof.year + ': ')); p.appendChild(g);
        p.appendChild(document.createTextNode(' ' + m.proof.label + '. ')); if (safe(m.proof.url)) { p.appendChild(ext(m.proof.url, m.proof.source)); }
        pr.appendChild(p); r.appendChild(pr);
      }
      var fit = row('The funder that fits', m.funder, m.why); fit.className += ' pf-m__fit';
      var chips = el('p', 'pf-chips');
      (m.networks || []).forEach(function(n){ var c = el('a', 'pf-chip', n.name); c.href = '#pf-who-' + n.id; chips.appendChild(c); });
      fit.appendChild(chips); r.appendChild(fit);
      var bt = el('div', 'pf-btns'), b1 = el('a', 'pf-btn', answer.label || 'Answer this Match'), b2 = el('a', 'pf-btn pf-btn--line', 'Read the Solution');
      if (safe(answer.url)) { b1.href = answer.url; } if (safe(m.solutionUrl)) { b2.href = m.solutionUrl; }
      bt.appendChild(b1); bt.appendChild(b2); r.appendChild(bt);
      a.appendChild(l); a.appendChild(r);
      return a;
    }
    function show(m){
      slot.textContent = ''; slot.appendChild(card(m));
      qa('button', rail).forEach(function(b){ b.classList.toggle('is-on', +b.getAttribute('data-no') === m.no); });
    }
    function buildRail(){
      if (!rail || !more) { return; }
      rail.textContent = '';
      if (2 > live.length) { more.hidden = true; return; }
      live.forEach(function(m, i){
        var li = el('li'), b = el('button'); b.type = 'button'; b.setAttribute('data-no', m.no);
        b.appendChild(el('b', '', 'No. ' + m.no)); b.appendChild(el('span', '', m.nation)); b.appendChild(el('em', '', i === 0 ? 'This week' : m.weekText));
        b.addEventListener('click', function(){ show(m); });
        li.appendChild(b); rail.appendChild(li);
      });
      var p = q('p', more); if (p) { p.textContent = 'Every Match'; }
      more.hidden = false;
    }
    buildRail();
    show(live[0]);
  })();

  /* network chips light the source they point to */
  root.addEventListener('click', function(e){
    var a = e.target.closest ? e.target.closest('a.pf-chip') : null;
    if (!a) { return; }
    var t = document.getElementById(a.getAttribute('href').slice(1));
    if (!t) { return; }
    qa('.pf-fam li.is-lit').forEach(function(li){ li.classList.remove('is-lit'); });
    t.classList.add('is-lit'); setTimeout(function(){ t.classList.remove('is-lit'); }, 2600);
  });

  /* ---------- 03 the deal pipeline: loads on the first tap, then filters by standard, funder, region, nation ---------- */
  (function(){
    var sec = q('.pf-pipe');
    if (!sec) { return; }
    var listEl = q('.pf-lines', sec), count = q('.pf-count', sec), moreB = q('.pf-moreb', sec), input = q('.pf-q input', sec);
    var st = { std: '', fin: '', reg: '', q: '' }, data = null, loading = false, shown = 12, waiting = false;
    function fold(s){ return String(s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
    function match(x){
      if (st.std && x.standard !== st.std) { return false; }
      if (st.fin === 'lead' && x.finance) { return false; }
      if (st.fin && st.fin !== 'lead' && x.finance !== st.fin) { return false; }
      if (st.reg && x.region !== st.reg) { return false; }
      if (st.q && fold(x.nation).indexOf(fold(st.q)) === -1) { return false; }
      return true;
    }
    function line(x){
      var li = el('li', 'pf-line'), k = el('p', 'pf-line__k'), h = el('h3'), a = el('a', '', x.title);
      k.appendChild(el('b', '', x.nation)); k.appendChild(el('span', '', x.standard));
      k.appendChild(el('span', '', x.finance || (x.no ? 'Solution No. ' + x.no : 'Lead Solution')));
      if (safe(x.url)) { a.href = x.url; }
      h.appendChild(a); li.appendChild(k); li.appendChild(h); li.appendChild(el('p', '', x.challenge));
      return li;
    }
    function words(){
      var w = [];
      if (st.std) { w.push(st.std); }
      if (st.fin) { w.push(st.fin === 'lead' ? 'Lead Solutions' : st.fin); }
      if (st.reg) { w.push(st.reg); }
      if (st.q) { w.push('\u201c' + st.q + '\u201d'); }
      return w.length ? ' \u00b7 ' + w.join(' \u00b7 ') : '';
    }
    function render(){
      if (!data) { return; }
      var hits = data.lines.filter(match), part = hits.slice(0, shown);
      listEl.textContent = '';
      part.forEach(function(x){ listEl.appendChild(line(x)); });
      count.textContent = hits.length ? comma(hits.length) + ' Solution' + (hits.length === 1 ? '' : 's') + words() : 'No Solution fits these filters yet' + words() + '. Request one below.';
      moreB.hidden = part.length >= hits.length;
      moreB.textContent = 'Show ' + Math.min(12, hits.length - part.length) + ' more';
      qa('.pf-cell', sec).forEach(function(b){
        var f = b.getAttribute('data-fin');
        b.classList.toggle('is-on', !!st.std && b.getAttribute('data-std') === st.std && !!st.fin && f === st.fin);
      });
    }
    function load(){
      if (data) { render(); return; }
      if (loading) { waiting = true; return; }
      loading = true; count.textContent = 'Opening the pipeline\u2026';
      getJSON([sec.getAttribute('data-src'), sec.getAttribute('data-mirror')], function(d){
        if (!d || !d.lines) { count.textContent = 'The pipeline could not be opened. Request it below.'; return; }
        data = d; render();
      }, function(){ count.textContent = 'The pipeline could not be opened just now. Request it below.'; });
    }
    function setChips(){
      qa('.pf-fc', sec).forEach(function(b){ b.classList.toggle('is-on', (st[b.getAttribute('data-k')] || '') === b.getAttribute('data-v')); });
    }
    qa('.pf-fc', sec).forEach(function(b){
      b.addEventListener('click', function(){ st[b.getAttribute('data-k')] = b.getAttribute('data-v'); shown = 12; setChips(); load(); });
    });
    qa('.pf-cell', sec).forEach(function(b){
      b.addEventListener('click', function(){
        var s = b.getAttribute('data-std'), f = b.getAttribute('data-fin');
        if (st.std === s && st.fin === f) { st.std = ''; st.fin = ''; } else { st.std = s; st.fin = f; }
        st.reg = ''; shown = 12; setChips(); load();
        if (640 >= window.innerWidth && count.scrollIntoView) { count.scrollIntoView({ behavior: still ? 'auto' : 'smooth', block: 'start' }); }
      });
    });
    var tq = 0;
    if (input) {
      input.addEventListener('input', function(){ clearTimeout(tq); tq = setTimeout(function(){ st.q = input.value.trim(); shown = 12; load(); }, 160); });
      input.addEventListener('focus', function(){ if (!data) { load(); } });
    }
    moreB.addEventListener('click', function(){ shown += 12; render(); });
    if (waiting) { render(); }
  })();
})();
