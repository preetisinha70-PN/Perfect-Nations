(function () {
  /* Blueprint v10.0: the page follows its Nation Steward and the State of Nations.
     - On load it reads data/<nation>.json (raw.githubusercontent.com, then jsDelivr) for the hero, the
       seven standards, the register, the record, the assets, the enterprises and the Newswire.
     - Near the Solutions it reads data/solutions-by-nation.json and data/state-of-nations.json for the
       Solution for this nation and every State of Nations Solution about it.
     - Every file is revalidated (cache:'no-cache'): an unchanged file costs a 304, not a download.
     The page code stays wherever a file cannot be read. */
  /*pn:cfg*/
  var root = document.getElementById(CFG.root);
  if (!root || root.getAttribute('data-live') === '1') return;
  root.setAttribute('data-live', '1');
  var BASES = ['https://raw.githubusercontent.com/preetisinha70-PN/perfect-nations/main/',
               'https://cdn.jsdelivr.net/gh/preetisinha70-PN/perfect-nations@main/'];
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var ORDER = ['Food', 'Water', 'Shelter', 'Energy', 'Education', 'Health', 'Livelihoods'];
  var MONEY = /^(?:[A-Z]{0,3}\$|\u20ac|\u00a3|\u20b9|\u20a6|~?\$|(?:USD|EUR|KSh|Sh|GHS|ZAR|FCFA|CFA|MAD|EGP|ETB|NGN|PKR|BDT|INR|IDR|PHP|VND|LKR|MXN|COP|JOD|FJD|UAH|BBD|BWP|AOA|MZN|TZS|UGX|RWF|ZMW|MWK|NAD|SZL|LSL|SOS|SSP|CDF|BIF|MGA|XAF|XOF|JMD|BRL|R)\s?\d)/;
  function q(s) { return root.querySelector(s); }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function T(v) { return typeof v === 'string' ? v : ''; }
  function okUrl(u) { return typeof u === 'string' && /^https:\/\/[^\s'"()<>\\]+$/.test(u); }
  function link(a, u) { a.href = u; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a; }
  function num(v) { return typeof v === 'number' && isFinite(v) && v >= 0 && v <= 100; }
  function fmt(v) { return String(Math.round(v * 10) / 10); }
  function lab(n) { return n === 'Livelihoods' ? 'Livelihood' : n; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
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

  /* ---------- interactions that also serve the page code ---------- */
  function wireRegister() {
    var list = q('#bp-irs'), more = q('#bp-showall');
    if (!list) return;
    var buttons = root.querySelectorAll('.bpx-filters .bpx-fb');
    if (more) {
      var c = more.cloneNode(true); more.parentNode.replaceChild(c, more); more = c;
      var nl = list.querySelectorAll('.bpx-ir').length;
      more.hidden = nl <= 5; more.classList.toggle('is-phone', nl <= 8);
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
  function near(target, fn, margin) {
    if (!target) return;
    if (!('IntersectionObserver' in window)) { fn(); return; }
    var io = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { io.disconnect(); fn(); } }, { rootMargin: margin || '0px' });
    io.observe(target);
  }
  near(q('.bw-wheel'), function () { var w = q('.bw-wheel'); if (w) w.classList.add('is-in'); }, '-10% 0px');
  /* the handwriting of the Letter loads only when the Letter is near, so it never holds up the first screen */
  near(q('#bp-letter'), function () {
    if (document.querySelector('link[data-pn-caveat]')) return;
    var l = document.createElement('link'); l.rel = 'stylesheet'; l.setAttribute('data-pn-caveat', '1');
    l.href = 'https://fonts.googleapis.com/css2?family=Caveat:wght@600&display=swap'; document.head.appendChild(l);
  }, '600px 0px');

  /* ---------- the seven standards ---------- */
  function pt(r, a) { a = (a - 90) * Math.PI / 180; return (300 + r * Math.cos(a)).toFixed(1) + ' ' + (300 + r * Math.sin(a)).toFixed(1); }
  function arc(ra, rb, a0, a1) { return 'M' + pt(rb, a0) + 'A' + rb + ' ' + rb + ' 0 0 1 ' + pt(rb, a1) + 'L' + pt(ra, a1) + 'A' + ra + ' ' + ra + ' 0 0 0 ' + pt(ra, a0) + 'Z'; }
  function standards(d) {
    if (!d.guarantees || d.guarantees.length !== 7) return;
    var g = {}, ok = true;
    d.guarantees.forEach(function (x) { if (!x || ORDER.indexOf(x.name) < 0 || !(x.value === null || num(x.value))) ok = false; else g[x.name] = x; });
    if (!ok || Object.keys(g).length !== 7) return;
    var scored = ORDER.filter(function (n) { return num(g[n].value); });
    if (!scored.length) return;
    var set = d.coverage && ORDER.indexOf(d.coverage.set_by) >= 0 ? d.coverage.set_by : (d.coverage && d.coverage.set_by === 'Livelihood' ? 'Livelihoods' : null);
    var low = scored.reduce(function (a, b) { return g[b].value < g[a].value ? b : a; }, scored[0]);
    var hasScore = d.coverage && num(d.coverage.score);
    var bind = hasScore ? (set && num(g[set].value) && g[set].value === d.coverage.score ? set : low) : (set || low);
    var score = hasScore ? d.coverage.score : null;
    var segs = root.querySelectorAll('.bw-seg');
    for (var s = 0; s < segs.length; s++) {
      var seg = segs[s], k = +seg.getAttribute('data-i'), name = ORDER[k], v = g[name].value;
      var a0 = k * 360 / 7 + 0.8, a1 = (k + 1) * 360 / 7 - 0.8;
      var f = seg.querySelector('.bw-fill'); if (f) f.setAttribute('d', num(v) ? arc(148, 148 + 124 * v / 100, a0, a1) : '');
      var vl = seg.querySelector('.bw-val'); if (vl) vl.textContent = num(v) ? fmt(v) : '\u2013';
      seg.setAttribute('aria-label', lab(name) + (num(v) ? ', coverage ' + fmt(v) + ' of 100' : ', not scored'));
      seg.classList.toggle('is-bind', name === bind);
      var b = seg.querySelector('.bw-bind'); if (b) b.style.display = name === bind ? '' : 'none';
    }
    var c2 = q('.bw-c2'); if (c2) c2.textContent = score === null ? '' : fmt(score);
    var c3 = q('.bw-c3'); if (c3) c3.textContent = score === null ? (CFG.unscored && CFG.unscored.center || 'NOT SCORED') : 'OF 100 \u00b7 SET BY ' + lab(bind).toUpperCase();
    var h = q('#bp-pcx-h');
    if (h) h.textContent = score === null ? (CFG.unscored && CFG.unscored.heading || h.textContent) : 'The ' + CFG.name + ' wheel: held at ' + fmt(score) + ' by ' + lab(bind).toLowerCase();
    function row(k, v, t) { var r = q('.bpx-four li[data-k="' + k + '"]'); if (!r) return; if (v) r.querySelector('b').textContent = v; if (t) r.querySelector('span').textContent = t; }
    var cv = d.coverage || {};
    if (score !== null) row('cov', fmt(score), 'Out of 100, set by ' + lab(bind).toLowerCase() + ', the standard ' + CFG.name + ' provides least.');
    if (cv.gap) row('gap', cv.gap, cv.gap_text || '');
    if (cv.perfect_capita) row('pc', cv.perfect_capita, '');
    if (cv.price) row('price', cv.price, '');
    var def = q('#bw-def');
    if (def && score !== null) {
      var next = scored.filter(function (n) { return n !== bind; }).sort(function (a, b) { return g[a].value - g[b].value; }).slice(0, 2);
      var tail = next.length === 2 ? ', with ' + lab(next[0]).toLowerCase() + ' at ' + fmt(g[next[0]].value) + ' and ' + lab(next[1]).toLowerCase() + ' at ' + fmt(g[next[1]].value) + ' next.' : '.';
      def.textContent = 'The poverty line measures income. The Living Line measures a life: food, water, shelter, energy, education, health and livelihood. Perfect Capita is the yearly cost, per person, of lifting everyone above the Living Line in all seven basic living standards. Coverage scores each standard strictly out of 100, and a nation is held at its weakest: ' + CFG.name + ' at ' + fmt(score) + ', by ' + lab(bind).toLowerCase() + tail;
    }
    var ul = q('.bpx-std');
    if (ul) {
      ul.textContent = '';
      ORDER.forEach(function (n) {
        var x = g[n], item = el('li', n === bind ? 'is-bind' : '');
        item.appendChild(el('span', '', lab(n)));
        item.appendChild(el('b', '', x.display || (num(x.value) ? fmt(x.value) : '\u2013')));
        if (x.note) item.appendChild(el('small', '', x.note));
        if (okUrl(x.url)) item.appendChild(link(el('a', '', x.source || 'Source'), x.url));
        ul.appendChild(item);
      });
    }
  }

  /* ---------- the hero, the register, the record, the assets, the enterprises ---------- */
  var CAT = { govt: 'Government', humanitarian: 'Humanitarian', multi: 'Multilateral', regional: 'Regional', bilat: 'Bilateral', 'private': 'Private', impact: 'Impact' };
  var CATS = ['govt', 'humanitarian', 'multi', 'regional', 'bilat', 'private', 'impact'];
  function hero(h) {
    if (!h) return;
    var ld = q('.bpx-hero .bpx-lead'); if (ld && T(h.lead)) ld.textContent = h.lead;
    var ul = q('.bpx-stats'); if (!ul || !h.stats || !h.stats.length) return;
    var items = h.stats.filter(function (x) { return x && T(x.value) && T(x.label); }); if (!items.length) return;
    ul.textContent = '';
    items.forEach(function (x) { var li = el('li'), b = el('b'); money(b, x.value, MONEY.test(x.value)); li.appendChild(b); li.appendChild(el('span', '', x.label)); ul.appendChild(li); });
  }
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
      var li = el('li', 'bpx-ir' + (i >= 8 ? ' bpx-ir--more' : '')); li.setAttribute('data-cat', cat);
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
    Array.prototype.forEach.call(root.querySelectorAll('.bpx-stats li'), function (li) {
      var s = li.querySelector('span'), b = li.querySelector('b'); if (s && b && s.textContent === 'Instruments and investments on record') b.textContent = String(lines.length);
    });
    var rc = q('[data-bpx="count"]'); if (rc) rc.textContent = String(lines.length);
  }
  function assets(list) {
    var ul = q('.bpx-acards'); if (!ul || !list || !list.length) return;
    var items = list.filter(function (x) { return x && T(x.name) && T(x.figure); }); if (!items.length) return;
    ul.textContent = '';
    items.forEach(function (x, i) {
      var li = el('li', 'bpx-acard'), plate = el('span', 'bpx-plate');
      var t = (x.tint && x.tint.length === 2 && /^#[0-9a-fA-F]{6}$/.test(x.tint[0]) && /^#[0-9a-fA-F]{6}$/.test(x.tint[1])) ? x.tint : ['#3A5A40', '#1E2E22'];
      plate.style.backgroundImage = 'linear-gradient(160deg,' + t[0] + ' 0%,' + t[1] + ' 100%)';
      var imgs = (x.images || []).filter(okUrl);
      if (imgs.length) {
        var im = el('img'); im.alt = T(x.alt) || x.name; im.loading = 'lazy'; im.decoding = 'async'; im.width = 768; im.height = 560;
        var k = 0; im.onerror = function () { im.removeAttribute('srcset'); k++; if (k < imgs.length) im.src = imgs[k]; else im.remove(); };
        if (CFG.img && CFG.img[imgs[0]]) { im.srcset = CFG.img[imgs[0]]; im.sizes = CFG.sizes; }
        im.src = imgs[0]; plate.appendChild(im);
      }
      plate.appendChild(el('span', 'bpx-plate__n', pad(i + 1))); li.appendChild(plate);
      var b = el('div', 'bpx-acard__b'); b.appendChild(el('h3', '', x.name));
      var fig = el('span', 'bpx-acard__fig'); money(fig, x.figure, x.money); if (T(x.label)) fig.appendChild(el('small', '', x.label)); b.appendChild(fig);
      if (T(x.text)) b.appendChild(el('p', '', x.text));
      li.appendChild(b); ul.appendChild(li);
    });
  }
  function enterprises(list) {
    var ul = q('.bpx-ents'); if (!ul || !list || !list.length) return;
    var items = list.filter(function (x) { return x && T(x.name) && (okUrl(x.url) || /^mailto:[^\s'"<>]+$/.test(x.url || '')); }); if (!items.length) return;
    ul.textContent = '';
    items.forEach(function (x) {
      var li = el('li'); li.appendChild(el('span', 'bpx-ent__s', T(x.standard))); li.appendChild(el('h3', '', x.name));
      if (T(x.text)) li.appendChild(el('p', '', x.text));
      li.appendChild(link(el('a', '', T(x.source) || 'Source'), x.url)); ul.appendChild(li);
    });
  }
  function head(id, s) { var h = q('#' + id); if (h && T(s)) h.textContent = s; }

  /* ---------- the Newswire ---------- */
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
      d.newswire.slice(0, 8).forEach(function (w) { var li = wireLi(w); if (li) wire.appendChild(li); });
      if (d.newswire.length >= 8) allNews(wire, d.newswire);
    }
    var sd = q('.bpx-stew time'); if (sd && d.updated) { var L = longDate(d.updated); if (L) { sd.setAttribute('datetime', d.updated); sd.textContent = 'Last updated ' + L; } }
  }
  function allNews(wire, shown) {
    var btn = q('#bp-newswire .bpx-allnews'); if (!btn) return;
    var seen = {}, extra = [], done = false;
    function add(w) { if (w && w.title && okUrl(w.url) && !seen[w.url]) { seen[w.url] = 1; extra.push(w); } }
    shown.slice(0, 8).forEach(function (w) { if (w && w.url) seen[w.url] = 1; });
    shown.slice(8).forEach(add);
    function show() {
      if (done) return; done = true;
      var more = el('ul', 'bpx-wire'); more.id = 'bp-wire-more'; more.hidden = true;
      extra.forEach(function (w) { var li = wireLi(w); if (li) more.appendChild(li); });
      if (!more.children.length) return;
      wire.parentNode.insertBefore(more, btn);
      var label = 'All news (' + (wire.children.length + more.children.length) + ')';
      btn.textContent = label; btn.setAttribute('aria-controls', 'bp-wire-more'); btn.setAttribute('aria-expanded', 'false'); btn.hidden = false;
      btn.addEventListener('click', function () { var open = more.hidden; more.hidden = !open; btn.setAttribute('aria-expanded', open ? 'true' : 'false'); btn.textContent = open ? 'Show fewer' : label; });
    }
    get('archive/newswire/' + CFG.slug + '.json', function (list) { if (list && typeof list.length === 'number') for (var k = 0; k < list.length; k++) add(list[k]); show(); }, show);
  }

  /* ---------- Solutions (from State of Nations) ---------- */
  var nationFile = null, solDone = false;
  function solCard(x, sigName, sigRole, n) {
    var li = el('li', 'bpx-sol');
    var k = el('p', 'bpx-sol__k'); k.appendChild(el('b', '', 'Solution No. ' + pad(x.no || 0)));
    var tm = el('time', '', x.label || shortDate(x.date) || ''); tm.setAttribute('datetime', x.date || ''); k.appendChild(tm); li.appendChild(k);
    var h = el('h3'), href = okUrl(x.url) ? x.url : 'https://perfectnations.org/state-of-nations/#solution-' + pad(x.no || 0);
    h.appendChild(link(el('a', '', x.title), href)); li.appendChild(h);
    if (T(x.challenge) && T(x.ffd) && T(x.si)) {
      var how = el('ul', 'bpx-sol__how');
      [['01', 'The challenge', x.challenge], ['02', 'How FfD solves it', x.ffd], ['03', 'How SI solves it', x.si]].forEach(function (r) {
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
    if (!play || !T(play.ffd) || !T(play.si)) return null;
    var li = el('li', 'bpx-sol bpx-sol--brief');
    var k = el('p', 'bpx-sol__k'); k.appendChild(el('b', '', 'The Solution for ' + CFG.name)); k.appendChild(el('span', '', me.standard)); li.appendChild(k);
    li.appendChild(el('h3', '', play.head || ('Close the gap in ' + me.standard.toLowerCase() + '.')));
    var how = el('ul', 'bpx-sol__how');
    function rowx(no, t, words, a) { var it = el('li'); it.appendChild(el('b', '', no)); it.appendChild(el('strong', '', t)); var sp = el('span', '', words); if (a) { sp.appendChild(document.createTextNode(' ')); sp.appendChild(a); } it.appendChild(sp); how.appendChild(it); }
    var src = me.source && okUrl(me.source.url) ? link(el('a', '', me.source.label || 'Source'), me.source.url) : null;
    rowx('01', 'The challenge', (me.gap ? me.gap + ' ' : '') + T(me.gap_text), src);
    var w = T(play.name) + ': ' + play.ffd, wa = null;
    if (me.at_work && T(me.at_work.name) && okUrl(me.at_work.url)) { w += ' At work in ' + CFG.name + ': ' + me.at_work.name + (me.at_work.amount ? ', ' + me.at_work.amount : '') + '.'; wa = link(el('a', '', 'Source'), me.at_work.url); }
    else if (play.proof && okUrl(play.proof.url)) { w += ' Proved in ' + play.proof.where + ', ' + play.proof.year + ': ' + play.proof.figure + ' ' + play.proof.label + '.'; wa = link(el('a', '', play.proof.source || 'Source'), play.proof.url); }
    rowx('02', 'How FfD solves it', w, wa);
    rowx('03', 'How SI solves it', play.si, null);
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
    try { hero(d.hero); } catch (e) {}
    try { standards(d); } catch (e) {}
    var c = d.capital, a = d.assets, e2 = d.enterprises;
    if (c) { head('bp-cap-h', c.heading); try { record(c.record); } catch (e) {} try { register(c.register); } catch (e) {} }
    if (a) { head('bp-assets-h', a.heading); try { assets(a.items); } catch (e) {} }
    if (e2) { head('bp-ent-h', e2.heading); try { enterprises(e2.items); } catch (e) {} }
    try { newswire(d); } catch (e) {}
    near(q('#bp-solutions'), loadSolutions, '900px 0px');
  }
  if (window.fetch) get('data/' + CFG.slug + '.json', apply, function () { near(q('#bp-solutions'), loadSolutions, '900px 0px'); });
})();
