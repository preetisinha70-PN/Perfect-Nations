/* PERFECT NATIONS - THE 50 STATES - script. The map, the card of a state, the regions, the list (find, sort,
   Show all) and the live blueprints: a pn-us-<slug> key in pages/manifest.json turns that state bright gold. */
(function(){
  var root = document.getElementById('pn-us');
  if (!root || root.__pnus) { return; }
  root.__pnus = 1;
  var $ = function(sel, el){ return (el || root).querySelector(sel); };
  var $$ = function(sel, el){ return Array.prototype.slice.call((el || root).querySelectorAll(sel)); };
  var DATA = {};
  try { DATA = JSON.parse(($('#pnus-data') || {}).textContent || '{}'); } catch (e) { DATA = {}; }
  var SITE = 'https://perfectnations.org';
  var REGION = { northeast:'Northeast', midwest:'Midwest', south:'South', west:'West' };
  var live = {};            /* slug: url of an open state blueprint */
  var map = $('#pnus-map'), card = $('#pnus-card'), rows = $('#pnus-rows');
  var paths = $$('.pnus-st'), calls = $$('.pnus-lb--c');
  var phone = window.matchMedia ? window.matchMedia('(max-width:760px)') : { matches:false };
  var fine = window.matchMedia ? window.matchMedia('(hover:hover) and (pointer:fine)') : { matches:false };
  var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion:reduce)').matches;
  var pinned = '', shown = '', region = '', query = '', sortBy = 'n', showAll = false;

  function byS(list, s){ return list.filter(function(el){ return el.getAttribute('data-s') === s; }); }
  function ask(name){ return SITE + '/contact/?about=blueprint&country=' + encodeURIComponent(name); }

  /* ---- the card ---- */
  function fillCard(s){
    var d = DATA[s];
    if (!d || !card) { return; }
    $('.pnus-card__ab', card).textContent = d[1];
    $('.pnus-card__rg', card).textContent = REGION[d[2]] || '';
    $('.pnus-card__h', card).textContent = d[0];
    $('.pnus-card__gdp', card).textContent = d[3];
    $('.pnus-card__pop', card).textContent = d[4];
    $('.pnus-card__pov', card).textContent = d[6] + '%';
    $('.pnus-card__pov', card).setAttribute('title', d[5] + ' people');
    var go = $('.pnus-card__go', card), open = !!live[s];
    go.setAttribute('href', open ? live[s] : ask(d[0]));
    $('.pnus-card__st', card).textContent = open ? 'Blueprint open' : 'Blueprint in preparation';
    $('.pnus-card__ac', card).textContent = open ? 'Open the blueprint' : 'Ask for it';
    card.classList.toggle('is-live', open);
    card.setAttribute('aria-label', d[0]);
  }
  function place(s){
    if (!card || !map) { return; }
    if (phone.matches) { card.style.left = ''; card.style.top = ''; return; }
    var p = byS(paths, s)[0];
    if (!p) { return; }
    var m = map.getBoundingClientRect(), r = p.getBoundingClientRect();
    var c = byS(calls, s)[0];
    if (c) { var cr = c.getBoundingClientRect(); r = { left:Math.min(r.left, cr.left), right:Math.max(r.right, cr.right), top:Math.min(r.top, cr.top), bottom:Math.max(r.bottom, cr.bottom) }; }
    var w = card.offsetWidth, h = card.offsetHeight, gap = 12;
    var L = r.left - m.left, R = r.right - m.left, T = r.top - m.top, B = r.bottom - m.top, cy = (T + B) / 2;
    var x, y, side = true;
    if (R + gap + w <= m.width) { x = R + gap; }
    else if (L - gap - w >= 0) { x = L - gap - w; }
    else { side = false; x = Math.max(0, Math.min(m.width - w, (L + R) / 2 - w / 2)); }
    y = side ? Math.max(0, Math.min(m.height - h, cy - h / 2))
             : (T - gap - h >= 0 ? T - gap - h : Math.max(0, Math.min(m.height - h, B + gap)));
    card.style.left = Math.round(x) + 'px';
    card.style.top = Math.round(y) + 'px';
  }
  function show(s){
    if (!DATA[s]) { return; }
    shown = s;
    paths.concat(calls).forEach(function(el){ el.classList.toggle('is-on', el.getAttribute('data-s') === s); });
    fillCard(s);
    card.hidden = false;
    place(s);
  }
  function hide(){
    shown = ''; pinned = '';
    if (card) { card.hidden = true; }
    paths.concat(calls).forEach(function(el){ el.classList.remove('is-on'); });
    $$('.pnus-row.is-on').forEach(function(el){ el.classList.remove('is-on'); });
  }
  function pin(s, fromList){
    pinned = s;
    show(s);
    $$('.pnus-row').forEach(function(el){ el.classList.toggle('is-on', el.getAttribute('data-s') === s); });
    if (fromList && map) {
      var top = map.getBoundingClientRect().top;
      if (top < 60 || top > window.innerHeight * 0.55) {
        window.scrollTo({ top:Math.max(0, window.pageYOffset + top - 90), behavior:calm ? 'auto' : 'smooth' });
      }
    }
  }

  paths.concat(calls).forEach(function(el){
    var s = el.getAttribute('data-s');
    el.addEventListener('click', function(){ if (pinned === s) { hide(); } else { pin(s); } });
    el.addEventListener('mouseenter', function(){ if (fine.matches && !pinned) { show(s); } });
    el.addEventListener('keydown', function(e){
      if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') { e.preventDefault(); pin(s); }
    });
  });
  if (map) {
    map.addEventListener('mouseleave', function(){ if (fine.matches && !pinned) { hide(); } });
  }
  if (card) {
    $('.pnus-card__x', card).addEventListener('click', hide);
    card.addEventListener('mouseenter', function(){ if (fine.matches && shown && !pinned) { pinned = shown; } });
  }
  document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && shown) { hide(); } });
  document.addEventListener('click', function(e){
    if (!pinned || !map) { return; }
    var t = e.target;
    if (map.contains(t) || (t.closest && t.closest('.pnus-row__b'))) { return; }
    hide();
  });
  window.addEventListener('resize', function(){ if (shown) { place(shown); } });

  /* ---- regions: the tabs above the map and the chips over the list move together ---- */
  function setRegion(r){
    region = r || '';
    $$('.pnus-tab,.pnus-chip').forEach(function(b){ b.setAttribute('aria-pressed', (b.getAttribute('data-reg') || '') === region ? 'true' : 'false'); });
    if (map) {
      map.classList.toggle('is-reg', !!region);
      $$('.pnus-st,.pnus-lb,.pnus-ld', map).forEach(function(el){
        var s = el.getAttribute('data-s');
        el.classList.toggle('is-in', !!region && !!DATA[s] && DATA[s][2] === region);
      });
    }
    if (shown && region && DATA[shown] && DATA[shown][2] !== region) { hide(); }
    list();
  }
  $$('.pnus-tab,.pnus-chip').forEach(function(b){
    b.addEventListener('click', function(){ setRegion(b.getAttribute('data-reg') || ''); });
  });

  /* ---- the list: find, sort, Show all ---- */
  function norm(s){
    s = String(s || '');
    if (s.normalize) { s = s.normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
    return s.toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/^\s+|\s+$/g, '');
  }
  function list(){
    if (!rows) { return; }
    var items = $$('.pnus-row', rows), q = norm(query), n = 0;
    var key = { n:'data-n', g:'data-g', p:'data-p', v:'data-v' }[sortBy];
    items.sort(function(a, b){
      if (sortBy === 'n') { return a.getAttribute(key) < b.getAttribute(key) ? -1 : 1; }
      return parseFloat(b.getAttribute(key)) - parseFloat(a.getAttribute(key));
    });
    items.forEach(function(el){
      var s = el.getAttribute('data-s'), d = DATA[s] || [];
      var hit = (!region || el.getAttribute('data-r') === region) &&
                (!q || (' ' + norm(d[0])).indexOf(' ' + q) >= 0 || norm(d[1]) === q);
      el.hidden = !hit;
      if (hit) { n++; }
      rows.appendChild(el);
    });
    var shortList = !showAll && !q && !region;
    rows.classList.toggle('is-short', shortList);
    var more = $('#pnus-more');
    if (more) { more.hidden = !shortList || !phone.matches; }
    var none = $('#pnus-none');
    if (none) { none.hidden = n > 0; }
  }
  var q = $('#pnus-q');
  if (q) { q.addEventListener('input', function(){ query = q.value; list(); }); }
  $$('.pnus-so').forEach(function(b){
    b.addEventListener('click', function(){
      sortBy = b.getAttribute('data-sort');
      $$('.pnus-so').forEach(function(o){ o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
      list();
    });
  });
  var more = $('#pnus-more');
  if (more) { more.addEventListener('click', function(){ showAll = true; list(); }); }
  if (phone.addEventListener) { phone.addEventListener('change', function(){ list(); if (shown) { place(shown); } }); }
  $$('.pnus-row__b').forEach(function(b){
    b.addEventListener('click', function(){ pin(b.parentNode.getAttribute('data-s'), true); });
  });

  /* ---- the live blueprints, from the manifest ---- */
  function markLive(){
    Object.keys(live).forEach(function(s){
      byS(paths, s).concat(byS(calls, s)).forEach(function(el){ el.classList.add('is-live'); });
      var row = $('#pnus-' + s);
      if (row) {
        row.classList.add('is-live');
        var go = $('.pnus-row__go', row);
        go.setAttribute('href', live[s]);
        $('.pnus-row__st', row).textContent = 'Blueprint open';
        $('.pnus-row__ac', row).textContent = 'Open';
      }
    });
    if (shown) { fillCard(shown); }
  }
  function loadLive(){
    if (!window.fetch) { return; }
    var urls = [
      'https://raw.githubusercontent.com/preetisinha70-PN/perfect-nations/main/pages/manifest.json',
      'https://cdn.jsdelivr.net/gh/preetisinha70-PN/perfect-nations@main/pages/manifest.json'
    ];
    (function get(i){
      if (i >= urls.length) { return; }
      fetch(urls[i], { cache:'no-cache' }).then(function(r){ if (!r.ok) { throw 0; } return r.json(); }).then(function(m){
        var k, hit, p = (m && m.pages) || {};
        for (k in p) {
          hit = /^pn-us-([a-z0-9-]+)$/.exec(k);
          if (hit && DATA[hit[1]] && p[k] && /^https:\/\/perfectnations\.org\//.test(p[k].url || '')) { live[hit[1]] = p[k].url; }
        }
        markLive();
      }).catch(function(){ get(i + 1); });
    })(0);
  }

  /* ---- start: a state named in the address opens on the map (?state=texas or #texas) ---- */
  list();
  loadLive();
  var want = '';
  try { want = (new URLSearchParams(window.location.search).get('state') || '').toLowerCase(); } catch (e) {}
  if (!want && window.location.hash) { want = window.location.hash.slice(1).toLowerCase().replace(/^state-/, ''); }
  if (want && DATA[want]) { setTimeout(function(){ pin(want); }, 60); }
})();
