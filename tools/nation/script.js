(function () {
  /* Blueprint v11.1: the page follows its Nation Steward and the State of Nations.
     v11.1: What Perfect Nations advises, in place of how FfD and SI solve it (the Steward-General, 9 Nov 2026):
       a Solution reads 01 The challenge, 02 What Perfect Nations advises; the Solution for the nation reads
       01 The challenge, 02 The deal, 03 What Perfect Nations advises (as tools/build_nations.py writes them).
     - On load it reads data/<nation>.json (raw.githubusercontent.com, then jsDelivr) for the nation line and
       the figures at a glance, the seven stars, the register, the record, the assets, the enterprises and
       the Newswire.
     - Near the Solutions it reads data/solutions-by-nation.json and data/state-of-nations.json for the
       Solution for this nation and every State of Nations Solution about it.
     - Every file is revalidated (cache:'no-cache'): an unchanged file costs a 304, not a download.
     The page code stays wherever a file cannot be read. No composite score is computed: each of the seven
     standards keeps its own figure and source, and the one furthest from reach is marked. */
  /*pn:cfg*/
  var root = document.getElementById(CFG.root);
  if (!root || root.getAttribute('data-live') === '1') return;
  root.setAttribute('data-live', '1');
  var BASES = ['https://raw.githubusercontent.com/preetisinha70-PN/perfect-nations/main/',
               'https://cdn.jsdelivr.net/gh/preetisinha70-PN/perfect-nations@main/'];
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihoods'];
  var COLOURS = CFG.colours || [];
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function q(s) { return root.querySelector(s); }
  function qa(s) { return root.querySelectorAll(s); }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function T(v) { return typeof v === 'string' ? v : ''; }
  function okUrl(u) { return typeof u === 'string' && /^https:\/\/[^\s'"()<>\\]+$/.test(u); }
  function link(a, u) { a.href = u; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a; }
  function num(v) { return typeof v === 'number' && isFinite(v) && v >= 0 && v <= 100; }
  function fmt(v) { return String(Math.round(v * 10) / 10); }
  function lab(n) { return n === 'Livelihoods' ? 'Livelihood' : n; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function commas(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function popFmt(n) { if (!(n > 0)) return ''; if (n < 1e6) return commas(Math.round(n)); if (n < 1e9) return (n / 1e6).toFixed(1) + 'm'; return (n / 1e9).toFixed(2) + 'bn'; }
  function longDate(iso) { var p = String(iso || '').split('-'); if (p.length !== 3) return ''; return (+p[2]) + ' ' + MONTHS[(+p[1]) - 1] + ' ' + p[0]; }
  function shortDate(iso) { var p = String(iso || '').split('-'); if (p.length !== 3) return ''; return (+p[2]) + ' ' + MONTHS[(+p[1]) - 1].slice(0, 3) + ' ' + p[0]; }
  function money(parent, v, m) { if (m) parent.appendChild(el('span', 'bpx-money', v)); else parent.appendChild(document.createTextNode(v)); }
  function get(path, done, fail) {
    var i = 0;
    (function next() {
      if (i >= BASES.length) { if (fail) fail(); return; }
      fetch(BASES[i++] + path, { cache: 'no-cache' }).then(function (r) { if (!r.ok) throw 0; return r.json(); })
        .then(done).catch(next);
    })();
  }
  function near(target, fn, margin) {
    if (!target) return;
    if (!('IntersectionObserver' in window)) { fn(); return; }
    var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { io.disconnect(); fn(); } }, { rootMargin: margin || '0px' });
    io.observe(target);
  }

  /* ---------- the sections rise as they arrive (always shown after a few seconds) ---------- */
  (function reveal() {
    var parts = qa('.bpx-do, .bpx-assets, .bpx-pc');
    if (reduce || !('IntersectionObserver' in window)) { Array.prototype.forEach.call(parts, function (p) { p.classList.add('is-in'); }); return; }
    Array.prototype.forEach.call(parts, function (p) {
      p.classList.add('is-armed');
      near(p, function () { p.classList.add('is-in'); }, '0px 0px -12% 0px');
      setTimeout(function () { p.classList.add('is-in'); }, 9000);
    });
  })();

  /* ---------- interactions that also serve the page code ---------- */
  function wireRegister() {
    var list = q('#bp-irs'), more = q('#bp-showall');
    if (!list) return;
    var buttons = qa('.bpx-filters .bpx-fb');
    if (more) {
      var c = more.cloneNode(true); more.parentNode.replaceChild(c, more); more = c;
      var nl = list.querySelectorAll('.bpx-ir[data-cat]').length;
      more.hidden = nl <= 4; more.classList.toggle('is-phone', nl <= 6);
      more.addEventListener('click', function () { list.classList.add('is-all'); more.hidden = true; });
    }
    Array.prototype.forEach.call(buttons, function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-filter');
        Array.prototype.forEach.call(buttons, function (b) { var on = b === btn; b.classList.toggle('is-on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false'); });
        if (f !== 'all') { list.classList.add('is-all'); if (more) more.hidden = true; }
        Array.prototype.forEach.call(list.querySelectorAll('.bpx-ir'), function (r) { r.hidden = !(f === 'all' || r.getAttribute('data-cat') === f); });
      });
    });
  }
  wireRegister();
  (function mail() {
    var t = q('#bp-toast'), c = q('#bp-toast-copy'), x = q('#bp-toast-x'), timer;
    if (!t) return;
    function hide() { t.hidden = true; }
    root.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href^="mailto:"]') : null;
      if (!a) return;
      t.hidden = false; if (c) c.textContent = 'Copy address';
      clearTimeout(timer); timer = setTimeout(hide, 12000);
    });
    if (x) x.addEventListener('click', hide);
    if (c) c.addEventListener('click', function () {
      var addr = 'contact@perfectnations.org';
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(addr).then(function () { c.textContent = 'Copied'; }, function () { c.textContent = addr; });
      else c.textContent = addr;
    });
  })();
  /* a link to the Sources opens them */
  root.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href="#bp-sources"]') : null, d = q('#bp-sources');
    if (a && d) d.open = true;
  });
  /* the handwriting of the Letter loads only when the Letter is near, so it never holds up the first screen */
  near(q('#bp-letter'), function () {
    if (document.querySelector('link[data-pn-caveat]')) return;
    var l = document.createElement('link'); l.rel = 'stylesheet'; l.setAttribute('data-pn-caveat', '1');
    l.href = 'https://fonts.googleapis.com/css2?family=Caveat:wght@600&display=swap'; document.head.appendChild(l);
  }, '600px 0px');

  /* ---------- the seven stars: a star opens its figure and source in the card beneath ---------- */
  var sky = q('.bpx-stars'), stars = sky ? sky.querySelectorAll('.bpx-star') : [];
  function starAt(pos) { for (var s = 0; s < stars.length; s++) if (+stars[s].getAttribute('data-pos') === pos) return stars[s]; return null; }
  function pick(i) {
    var li = q('.bpx-std li[data-i="' + i + '"]'), call = q('#bp-call');
    if (!li || !call) return;
    Array.prototype.forEach.call(stars, function (s) { var on = +s.getAttribute('data-i') === i; s.classList.toggle('is-on', on); s.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    call.style.setProperty('--c', li.getAttribute('data-c') || COLOURS[i] || '#8A5A12');
    var v = q('#bp-call-v'), n = q('#bp-call-n'), f = q('#bp-call-f'), l = q('#bp-call-l'), a = q('#bp-call-s');
    var b = li.querySelector('b'), sp = li.querySelector('span'), sm = li.querySelector('small'), src = li.querySelector('a');
    if (v && b) v.textContent = b.textContent;
    if (n && sp) n.textContent = sp.textContent;
    if (f) f.hidden = !li.classList.contains('is-bind');
    if (l) l.textContent = sm ? sm.textContent : '';
    if (a) { if (src) { a.hidden = false; a.textContent = src.textContent; a.href = src.href; } else a.hidden = true; }
    var t = call.querySelector('.bpx-call__t');
    if (t && !reduce) { t.classList.remove('is-fade'); void t.offsetWidth; t.classList.add('is-fade'); }
  }
  Array.prototype.forEach.call(stars, function (s) {
    var k = +s.getAttribute('data-i'), pos = +s.getAttribute('data-pos');
    s.addEventListener('click', function () { pick(k); });
    s.addEventListener('keydown', function (e) {
      var to = null;
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(k); return; }
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') to = starAt((pos + 1) % 7);
      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') to = starAt((pos + 6) % 7);
      if (to) { e.preventDefault(); pick(+to.getAttribute('data-i')); to.focus(); }
    });
  });
  if (sky) near(sky, function () { sky.classList.add('is-in'); }, '-8% 0px');

  function standards(d) {
    if (!d.guarantees || d.guarantees.length !== 7) return;
    var g = {}, ok = true;
    d.guarantees.forEach(function (x) { if (!x || ORDER.indexOf(x.name) < 0 || !(x.value === null || num(x.value))) ok = false; else g[x.name] = x; });
    if (!ok || Object.keys(g).length !== 7) return;
    var scored = ORDER.filter(function (n) { return num(g[n].value); });
    var set = d.coverage && d.coverage.set_by === 'Livelihood' ? 'Livelihoods' : (d.coverage && d.coverage.set_by);
    var bind = ORDER.indexOf(set) >= 0 ? set : (scored.length ? scored.reduce(function (a, b) { return g[b].value < g[a].value ? b : a; }, scored[0]) : null);
    function shown(x) { return T(x.display) || (num(x.value) ? fmt(x.value) : '\u2013'); }
    Array.prototype.forEach.call(stars, function (s) {
      var k = +s.getAttribute('data-i'), name = ORDER[k], x = g[name];
      var vl = s.querySelector('.bpx-star__v'); if (vl) vl.textContent = shown(x).length <= 7 ? shown(x) : '\u2013';
      s.setAttribute('aria-label', lab(name) + ': ' + shown(x) + (name === bind ? ', the standard furthest from reach' : ''));
      s.classList.toggle('is-bind', name === bind);
    });
    var ul = q('.bpx-std');
    if (ul) {
      ul.textContent = '';
      ORDER.forEach(function (n, k) {
        var x = g[n], item = el('li', n === bind ? 'is-bind' : '');
        item.setAttribute('data-i', String(k)); item.setAttribute('data-c', COLOURS[k] || '');
        item.appendChild(el('span', '', lab(n)));
        item.appendChild(el('b', '', shown(x)));
        if (T(x.note)) item.appendChild(el('small', '', x.note));
        if (okUrl(x.url)) item.appendChild(link(el('a', '', T(x.source) || 'Source'), x.url));
        ul.appendChild(item);
      });
    }
    var on = sky && sky.querySelector('.bpx-star.is-on');
    pick(on ? +on.getAttribute('data-i') : ORDER.indexOf(bind));
    var t3 = q('.bpx-t[href="#bp-pc"] .bpx-t__q');
    if (t3 && bind) t3.textContent = 'Perfect Capita: seven basic standards of living for every citizen, star by star. ' + lab(bind) + ' is furthest from reach today.';
    return bind;
  }

  /* ---------- the nation line, the figures at a glance and the price ---------- */
  function glance(d, bind) {
    var h = d.hero || {}, cv = d.coverage || {};
    var nl = q('.bpx-hero__nation'); if (nl && T(h.lead)) nl.textContent = h.lead;
    var pop = +d.population;
    var pc = q('.bpx-stats [data-k="pop"] b'); if (pc && pop > 0) pc.textContent = popFmt(pop);
    var gp = q('.bpx-stats [data-k="gap"]');
    if (gp && T(cv.gap)) {
      gp.querySelector('b').textContent = cv.gap;
      var t = T(cv.gap_text).trim(); t = t.indexOf(':') >= 0 ? t.split(':')[0] : t.split(/\.\s/)[0]; t = t.replace(/\.$/, '');
      if (/^Of /.test(t) && /(%|in \d+)$/.test(cv.gap)) t = 'of ' + t.slice(3);
      if (t) gp.querySelector('span').textContent = t;
      var bi = gp.querySelector('em i'); if (bi && bind) bi.textContent = lab(bind);
    }
    var okPrice = /^\$[0-9][0-9.,]*(bn|m|B|M)?$/.test(T(cv.price)) && /^\$[0-9][0-9,]*$/.test(T(cv.perfect_capita));
    if (okPrice) {
      var pr = q('.bpx-stats [data-k="price"] b'); if (pr) pr.textContent = cv.price;
      var s1 = q('.bpx-sum [data-k="pc"] b'), s2 = q('.bpx-sum [data-k="pop"] b'), s3 = q('.bpx-sum [data-k="price"] b');
      if (s1) s1.textContent = cv.perfect_capita;
      if (s2 && pop > 0) s2.textContent = commas(Math.round(pop));
      if (s3) s3.textContent = cv.price;
    }
  }

  /* ---------- the register, the record, the assets, the enterprises ---------- */
  var CAT = { govt: 'Government', humanitarian: 'Humanitarian', multi: 'Multilateral', regional: 'Regional', bilat: 'Bilateral', 'private': 'Private', impact: 'Impact' };
  var CATS = ['govt', 'humanitarian', 'multi', 'regional', 'bilat', 'private', 'impact'];
  function record(list) {
    var ul = q('.bpx-recs'); if (!ul || !list || !list.length) return;
    var items = list.filter(function (x) { return x && T(x.value) && T(x.text) && okUrl(x.url); }); if (!items.length) return;
    ul.textContent = '';
    items.forEach(function (x) { var li = el('li'), b = el('b'); money(b, x.value, x.money); li.appendChild(b); li.appendChild(el('span', '', x.text)); li.appendChild(link(el('a', '', T(x.source) || 'Source'), x.url)); ul.appendChild(li); });
  }
  function register(list) {
    var irs = q('#bp-irs'); if (!irs || !list || !list.length) return;
    var lines = list.filter(function (x) { return x && T(x.name) && T(x.cat) && okUrl(x.url); }); if (!lines.length) return;
    var count = {};
    irs.textContent = ''; irs.classList.remove('is-all');
    lines.forEach(function (x, i) {
      var cat = x.cat.replace(/[^a-z]/g, ''), tone = T(x.tone).replace(/[^a-z]/g, '') || 'active';
      count[cat] = (count[cat] || 0) + 1;
      var li = el('li', 'bpx-ir' + (i >= 6 ? ' bpx-ir--more' : '')); li.setAttribute('data-cat', cat);
      var det = el('details'), sm = el('summary'), tags = el('span', 'bpx-tags');
      tags.appendChild(el('span', 'bpx-cat', CAT[cat] || cat)); tags.appendChild(el('span', 'bpx-stat bpx-stat--' + tone, T(x.status) || 'Active')); sm.appendChild(tags);
      var n = el('span', 'bpx-ir__n', x.name); if (T(x.detail)) n.appendChild(el('small', '', x.detail)); sm.appendChild(n);
      var a = el('span', 'bpx-ir__a'); if (T(x.amount)) money(a, x.amount, x.money); sm.appendChild(a); det.appendChild(sm);
      var b = el('div', 'bpx-ir__b');
      if (T(x.note)) b.appendChild(el('p', 'bpx-ir__note', x.note));
      if (T(x.text)) b.appendChild(el('p', '', x.text));
      if (x.by && x.by.length) { var by = el('p', 'bpx-ir__by'); x.by.forEach(function (s) { if (T(s)) by.appendChild(el('span', '', s)); }); if (by.children.length) b.appendChild(by); }
      b.appendChild(link(el('a', 'bpx-ir__src', 'Source'), x.url));
      det.appendChild(b); li.appendChild(det); irs.appendChild(li);
    });
    var more = q('#bp-showall'); if (more) more.textContent = 'Show all ' + lines.length + ' lines';
    var fw = q('.bpx-filters');
    if (fw) {
      fw.textContent = '';
      ['all'].concat(CATS.filter(function (k) { return count[k]; })).forEach(function (k) {
        var bt = el('button', 'bpx-fb' + (k === 'all' ? ' is-on' : '')); bt.type = 'button'; bt.setAttribute('data-filter', k); bt.setAttribute('aria-pressed', k === 'all' ? 'true' : 'false');
        bt.appendChild(document.createTextNode((k === 'all' ? 'All' : CAT[k]) + ' ')); bt.appendChild(el('span', '', String(k === 'all' ? lines.length : count[k])));
        fw.appendChild(bt);
      });
    }
    wireRegister();
    var rg = q('.bpx-stats [data-k="reg"] b'); if (rg) rg.textContent = String(lines.length);
    var rc = q('[data-bpx="count"]'); if (rc) rc.textContent = String(lines.length);
    var t2 = q('.bpx-t[href="#bp-capital"] .bpx-t__q');
    if (t2) {
      var names = CATS.filter(function (k) { return count[k]; }).map(function (k) { return CAT[k].toLowerCase(); });
      var from = names.length > 1 ? names.slice(0, -1).join(', ') + ' and ' + names[names.length - 1] : (names[0] || 'every');
      t2.textContent = lines.length + ' instruments and investments on record, from ' + from + ' sources.';
    }
  }
  function assets(list) {
    var ul = q('.bpx-acards'); if (!ul || !list || !list.length) return;
    var items = list.filter(function (x) { return x && T(x.name) && T(x.figure); }); if (!items.length) return;
    ul.textContent = ''; ul.setAttribute('data-n', String(items.length));
    items.forEach(function (x, i) {
      var li = el('li', 'bpx-acard'); li.style.setProperty('--i', String(i));
      var n = el('span', 'bpx-acard__n', pad(i + 1)); n.setAttribute('aria-hidden', 'true'); li.appendChild(n);
      var fig = el('p', 'bpx-acard__fig'), b = el('b', '', x.figure); fig.appendChild(b);
      if (T(x.label)) fig.appendChild(el('span', '', x.label)); li.appendChild(fig);
      li.appendChild(el('h3', '', x.name));
      if (T(x.text)) li.appendChild(el('p', '', x.text));
      ul.appendChild(li);
    });
    var t1 = q('.bpx-t[href="#bp-assets"] .bpx-t__q');
    if (t1 && items.length > 1) {
      var words = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven'];
      var nm = items.map(function (x) { return x.name; });
      t1.textContent = nm.slice(0, -1).join(', ') + ' and ' + nm[nm.length - 1] + ': ' + (words[nm.length] || nm.length) + ' sovereign assets, valued.';
    }
  }
  function enterprises(list) {
    var ul = q('.bpx-ents'); if (!ul || !list || !list.length) return;
    var items = list.filter(function (x) { return x && T(x.name) && (okUrl(x.url) || /^mailto:[^\s'"<>]+$/.test(x.url || '')); }); if (!items.length) return;
    ul.textContent = '';
    items.forEach(function (x) {
      var li = el('li'); li.appendChild(el('span', 'bpx-ent__s', T(x.standard))); li.appendChild(el('h4', '', x.name));
      if (T(x.text)) li.appendChild(el('p', '', x.text));
      li.appendChild(link(el('a', '', T(x.source) || 'Source'), x.url)); ul.appendChild(li);
    });
  }
  function head(id, s) { var h = q('#' + id); if (h && T(s)) h.textContent = s; }

  /* ---------- the Newswire: five lines (four on phones), then All news ---------- */
  var SHOW = 5;
  function wireLi(w) {
    if (!w || !w.title || !okUrl(w.url)) return null;
    var li = el('li'), tm = el('time', '', w.label || shortDate(w.date) || w.date); tm.setAttribute('datetime', w.date || ''); li.appendChild(tm);
    var a = link(el('a'), w.url), b = el('b'), t = w.title, hl = w.highlight, at = hl ? t.indexOf(hl) : -1;
    if (at >= 0) { b.appendChild(document.createTextNode(t.slice(0, at))); b.appendChild(el('span', 'bpx-money', hl)); b.appendChild(document.createTextNode(t.slice(at + hl.length))); } else b.textContent = t;
    a.appendChild(b); li.appendChild(a); li.appendChild(el('span', 'bpx-src', w.source || '')); return li;
  }
  function newswire(d) {
    var wire = q('#bp-newswire .bpx-wire');
    if (wire && d.newswire && d.newswire.length) {
      wire.textContent = '';
      d.newswire.slice(0, SHOW).forEach(function (w) { var li = wireLi(w); if (li) wire.appendChild(li); });
      if (!wire.children.length) { var none = el('li', 'bpx-wire__none'); none.appendChild(el('b', '', 'The first sourced news for ' + CFG.name + ' is in review.')); wire.appendChild(none); }
      allNews(wire, d.newswire);
    }
    var sd = q('.bpx-stew time'); if (sd && d.updated) { var L = longDate(d.updated); if (L) { sd.setAttribute('datetime', d.updated); sd.textContent = 'Last updated ' + L; } }
  }
  function allNews(wire, shown) {
    var btn = q('#bp-newswire .bpx-allnews'), nw = q('#bp-newswire'); if (!btn || !nw) return;
    nw.classList.add('is-js');
    var seen = {}, extra = [], done = false;
    function add(w) { if (w && w.title && okUrl(w.url) && !seen[w.url]) { seen[w.url] = 1; extra.push(w); } }
    shown.slice(0, SHOW).forEach(function (w) { if (w && w.url) seen[w.url] = 1; });
    shown.slice(SHOW).forEach(add);
    function show() {
      if (done) return; done = true;
      var more = el('ul', 'bpx-wire'); more.id = 'bp-wire-more'; more.hidden = true;
      extra.forEach(function (w) { var li = wireLi(w); if (li) more.appendChild(li); });
      /* phones show four lines; the button opens the rest, and on laptops the lines beyond five */
      if (!more.children.length && wire.children.length <= 4) return;
      if (more.children.length) wire.parentNode.insertBefore(more, btn); else btn.classList.add('is-phone');
      var label = 'All news (' + (wire.children.length + more.children.length) + ')';
      btn.textContent = label; btn.setAttribute('aria-expanded', 'false'); btn.hidden = false;
      if (more.children.length) btn.setAttribute('aria-controls', 'bp-wire-more');
      btn.addEventListener('click', function () { var open = !nw.classList.contains('is-open'); nw.classList.toggle('is-open', open); more.hidden = !open; btn.setAttribute('aria-expanded', open ? 'true' : 'false'); btn.textContent = open ? 'Show fewer' : label; });
    }
    if (shown.length < 8) { show(); return; }
    get('archive/newswire/' + CFG.slug + '.json', function (list) { if (list && typeof list.length === 'number') for (var k = 0; k < list.length; k++) add(list[k]); show(); }, show);
  }

  /* ---------- Solutions (from State of Nations) ---------- */
  var nationFile = null, solDone = false;
  function solCard(x, sigName, sigRole) {
    var li = el('li', 'bpx-sol');
    var k = el('p', 'bpx-sol__k'); k.appendChild(el('b', '', 'Solution No. ' + pad(x.no || 0)));
    var tm = el('time', '', x.label || shortDate(x.date) || ''); tm.setAttribute('datetime', x.date || ''); k.appendChild(tm); li.appendChild(k);
    var h = el('h3'), href = okUrl(x.url) ? x.url : 'https://perfectnations.org/state-of-nations/#solution-' + pad(x.no || 0);
    h.appendChild(link(el('a', '', x.title), href)); li.appendChild(h);
    if (T(x.challenge) && T(x.advises)) {
      var how = el('ul', 'bpx-sol__how');
      [['01', 'The challenge', x.challenge], ['02', 'What Perfect Nations advises', x.advises]].forEach(function (r) {
        var it = el('li'); it.appendChild(el('b', '', r[0])); it.appendChild(el('strong', '', r[1])); it.appendChild(el('span', '', r[2])); how.appendChild(it);
      });
      li.appendChild(how);
    } else if (T(x.standfirst) || T(x.summary)) li.appendChild(el('p', '', x.standfirst || x.summary));
    if (T(x.figure)) { var f = el('p', 'bpx-sol__fig'); f.appendChild(el('b', '', x.figure)); if (T(x.caption)) f.appendChild(el('span', '', x.caption)); li.appendChild(f); }
    var foot = el('div', 'bpx-sol__foot'), sig = el('span', 'bpx-sig', 'From');
    sig.appendChild(el('b', '', sigName)); sig.appendChild(el('small', '', sigRole)); foot.appendChild(sig);
    foot.appendChild(link(el('a', 'bpx-btn', 'Read the Solution'), href)); li.appendChild(foot);
    return li;
  }
  function brief(sbn) {
    var me = null; (sbn.nations || []).forEach(function (n) { if (n && n.slug === CFG.slug) me = n; });
    if (!me) return null;
    var play = null; (sbn.standards || []).forEach(function (s) { if (s && s.standard === me.standard) play = s; });
    if (!play || !T(play.advises)) return null;
    var li = el('li', 'bpx-sol bpx-sol--brief');
    var k = el('p', 'bpx-sol__k'); k.appendChild(el('b', '', 'The Solution for ' + CFG.name)); k.appendChild(el('span', '', me.standard)); li.appendChild(k);
    li.appendChild(el('h3', '', play.head || ('Close the gap in ' + me.standard.toLowerCase() + '.')));
    var how = el('ul', 'bpx-sol__how');
    function rowx(no, t, words, a) { var it = el('li'); it.appendChild(el('b', '', no)); it.appendChild(el('strong', '', t)); var sp = el('span', '', words); if (a) { sp.appendChild(document.createTextNode(' ')); sp.appendChild(a); } it.appendChild(sp); how.appendChild(it); }
    var src = me.source && okUrl(me.source.url) ? link(el('a', '', me.source.label || 'Source'), me.source.url) : null;
    rowx('01', 'The challenge', (me.gap ? me.gap + ' ' : '') + T(me.gap_text), src);
    /* 02 The deal: the instrument already at work in the nation, or else the deal that proved the playbook */
    var w = '', wa = null;
    if (me.at_work && T(me.at_work.name) && okUrl(me.at_work.url)) { w = 'At work in ' + CFG.name + ': ' + me.at_work.name + (me.at_work.amount ? ', ' + me.at_work.amount : '') + '.'; wa = link(el('a', '', 'Source'), me.at_work.url); }
    else if (play.proof && okUrl(play.proof.url)) { w = T(play.name) + ', proved in ' + play.proof.where + ', ' + play.proof.year + ': ' + play.proof.figure + ' ' + play.proof.label + '.'; wa = link(el('a', '', play.proof.source || 'Source'), play.proof.url); }
    if (w) rowx('02', 'The deal', w, wa);
    rowx(w ? '03' : '02', 'What Perfect Nations advises', play.advises, null);
    li.appendChild(how);
    var foot = el('div', 'bpx-sol__foot'), sig = el('span', 'bpx-sig', 'Co-design it in');
    sig.appendChild(el('b', '', 'The ReDesign Studio')); foot.appendChild(sig);
    var go = el('a', 'bpx-btn', 'The three mandates'); go.href = '#bp-mandates'; foot.appendChild(go); li.appendChild(foot);
    return li;
  }
  function solutions(sbn, son) {
    var ul = q('#bp-sols'); if (!ul) return;
    var cards = [], seen = {}, nos = [];
    if (sbn && sbn.nations) sbn.nations.forEach(function (n) { if (n && n.slug === CFG.slug && n.solutions) nos = n.solutions; });
    var lead = sbn ? brief(sbn) : null;
    if (!lead) { var kept = ul.querySelector('.bpx-sol--brief'); if (kept) lead = kept.cloneNode(true); }
    var pool = [];
    if (son && son.dispatches) son.dispatches.forEach(function (x) {
      if (!x || !x.title || !x.no) return;
      var mine = nos.indexOf(x.no) >= 0 || x.nation === CFG.name || (x.nations && x.nations.indexOf && x.nations.indexOf(CFG.name) >= 0);
      if (mine) pool.push({ x: x, who: 'preeti' });
    });
    if (nationFile && nationFile.dispatches) nationFile.dispatches.forEach(function (x) { if (x && x.title && x.no) pool.push({ x: x, who: x.author === 'steward' || x.author === 'nia' ? 'steward' : 'preeti' }); });
    pool.sort(function (a, b) { return String(b.x.date || '').localeCompare(String(a.x.date || '')) || (b.x.no - a.x.no); });
    pool.forEach(function (p) {
      if (seen[p.x.no]) return; seen[p.x.no] = 1;
      var st = p.who === 'steward';
      cards.push(solCard(p.x, st ? CFG.steward : 'Preeti Sinha', st ? CFG.stewardRole + ' \u00b7 SI Researcher' : 'President and CEO, Perfect Nations'));
    });
    if (!lead && !cards.length) return;
    ul.textContent = ''; ul.classList.remove('is-all');
    var all = (lead ? [lead] : []).concat(cards.slice(0, lead ? 5 : 6));
    all.forEach(function (c, i) { c.classList.toggle('bpx-sol--more', i >= 3); ul.appendChild(c); });
    var btn = q('.bpx-solmore');
    if (!btn && all.length > 3) { btn = el('button', 'bpx-showall bpx-solmore'); btn.type = 'button'; ul.parentNode.insertBefore(btn, ul.nextSibling); }
    if (btn) { btn.hidden = all.length <= 3; btn.textContent = 'Show all ' + all.length + ' Solutions'; btn.setAttribute('aria-expanded', 'false'); }
  }
  root.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('.bpx-solmore') : null; if (!b) return;
    var ul = q('#bp-sols'); if (!ul) return;
    var open = !ul.classList.contains('is-all'); ul.classList.toggle('is-all', open);
    b.setAttribute('aria-expanded', open ? 'true' : 'false');
    b.textContent = open ? 'Show fewer' : 'Show all ' + ul.children.length + ' Solutions';
  });
  function loadSolutions() {
    if (solDone) return; solDone = true;
    var sbn, son, n = 0;
    function both() { if (++n === 2) { try { solutions(sbn, son); } catch (e) {} } }
    get('data/solutions-by-nation.json', function (d) { if (d && d.page === 'solutions-by-nation') sbn = d; both(); }, both);
    get('data/state-of-nations.json', function (d) { if (d && d.page === 'state-of-nations') son = d; both(); }, both);
  }

  function apply(d) {
    if (!d || d.nation !== CFG.name) return;
    nationFile = d;
    var bind = null;
    try { bind = standards(d); } catch (e) {}
    try { glance(d, bind); } catch (e) {}
    var c = d.capital, a = d.assets, e2 = d.enterprises;
    if (c) { head('bp-cap-h', c.heading); try { record(c.record); } catch (e) {} try { register(c.register); } catch (e) {} }
    if (a) { head('bp-assets-h', a.heading); try { assets(a.items); } catch (e) {} }
    if (e2) { head('bp-ent-h', e2.heading); try { enterprises(e2.items); } catch (e) {} }
    try { newswire(d); } catch (e) {}
    near(q('#bp-solutions'), loadSolutions, '900px 0px');
  }
  if (window.fetch) get('data/' + CFG.slug + '.json', apply, function () { near(q('#bp-solutions'), loadSolutions, '900px 0px'); });
})();
