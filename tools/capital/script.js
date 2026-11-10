(function(){
  var root = document.getElementById('pn-arch');
  if (!root || root.getAttribute('data-pca') === '1') { return; }
  root.setAttribute('data-pca', '1');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* photographs: if one fails, the painted plate behind it stays */
  Array.prototype.forEach.call(root.querySelectorAll('.pca-t__ph img'), function(img){
    function off(){ img.style.display = 'none'; }
    if (img.complete && !img.naturalWidth) { off(); } else { img.addEventListener('error', off); }
  });

  /* reveal once: the five tiles rise, the bars draw */
  if (!still && 'IntersectionObserver' in window){
    root.classList.add('pca-anim');
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){ if (e.isIntersecting){ e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: 0.15 });
    Array.prototype.forEach.call(root.querySelectorAll('.pca-five,.pca-bars'), function(el){ io.observe(el); });
    window.setTimeout(function(){
      Array.prototype.forEach.call(root.querySelectorAll('.pca-five,.pca-bars'), function(el){ el.classList.add('is-in'); });
    }, 4000);
  }

  /* the toolkit on phones: one family at a time, chosen from the chips (All shows every line) */
  var idx = root.querySelector('.pca-idx');
  var chips = idx ? idx.querySelectorAll('.pca-jump a[data-f]') : [];
  var fams = idx ? idx.querySelectorAll('.pca-fam') : [];
  var phone = window.matchMedia ? window.matchMedia('(max-width:640px)') : null;
  var current = fams.length ? fams[0].id : 'all';
  function pick(id){
    current = id;
    Array.prototype.forEach.call(fams, function(f){ f.classList.toggle('is-on', id === 'all' || f.id === id); });
    Array.prototype.forEach.call(chips, function(c){
      var on = c.getAttribute('data-f') === id;
      c.classList.toggle('is-on', on);
      if (on) { c.setAttribute('aria-current', 'true'); } else { c.removeAttribute('aria-current'); }
    });
  }
  function mode(){
    if (!idx) { return; }
    var tabs = !!(phone && phone.matches);
    idx.classList.toggle('is-tabs', tabs);
    if (tabs) { pick(current); }
  }
  Array.prototype.forEach.call(chips, function(c){
    c.addEventListener('click', function(e){
      if (!(phone && phone.matches)) { return; }
      e.preventDefault();
      pick(c.getAttribute('data-f'));
      var top = c.getBoundingClientRect().top;
      if (top < 0) { window.scrollBy({ top: top - 80, behavior: still ? 'auto' : 'smooth' }); }
    });
  });
  if (phone){
    if (phone.addEventListener) { phone.addEventListener('change', mode); } else if (phone.addListener) { phone.addListener(mode); }
  }
  mode();

  /* the nations on record: the first few, then all */
  var list = root.querySelector('.pca-nats');
  var more = root.querySelector('.pca-more-n');
  function label(){
    if (!more || !list) { return; }
    var n = list.children.length;
    more.textContent = list.classList.contains('is-short') ? 'Show all ' + n + ' nations' : 'Show fewer nations';
    more.setAttribute('aria-expanded', list.classList.contains('is-short') ? 'false' : 'true');
  }
  if (list && more){
    list.classList.add('is-short');
    more.hidden = false;
    more.addEventListener('click', function(){ list.classList.toggle('is-short'); label(); });
    label();
  }

  /* live record: data/capital-architecture.json, refreshed by the Capital Architecture Steward.
     If it cannot be read or does not look right, the page keeps the figures it was built with. */
  var SRC = [
    'https://raw.githubusercontent.com/preetisinha70-PN/perfect-nations/main/data/capital-architecture.json',
    'https://cdn.jsdelivr.net/gh/preetisinha70-PN/perfect-nations@main/data/capital-architecture.json'
  ];
  function num(v){ return typeof v === 'number' && isFinite(v) && v >= 0 ? Math.round(v) : null; }
  function txt(v){ return typeof v === 'string' ? v : ''; }
  function safe(u){ return /^https:\/\/[^\s"'<>()]+$/.test(u || '') ? u : ''; }
  function fmt(n){ return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function el(tag, cls, text){ var e = document.createElement(tag); if (cls) { e.className = cls; } if (text) { e.textContent = text; } return e; }
  function apply(d){
    var r = d && d.record;
    if (!r || num(r.count) === null || num(r.nations) === null || !Array.isArray(r.by) || !Array.isArray(r.list) || !r.list.length) { return; }
    var vals = { count: num(r.count), nations: num(r.nations) };
    r.by.forEach(function(b){ if (b && b.cat === 'multi') { vals.multi = num(b.n); } });
    vals.pi = 0;
    r.by.forEach(function(b){ if (b && (b.cat === 'private' || b.cat === 'impact')) { vals.pi += num(b.n) || 0; } });
    Array.prototype.forEach.call(root.querySelectorAll('[data-pca-n]'), function(e){
      var v = vals[e.getAttribute('data-pca-n')];
      if (typeof v === 'number') { e.textContent = fmt(v); }
    });
    var bars = root.querySelector('.pca-bars');
    var max = 0;
    r.by.forEach(function(b){ max = Math.max(max, num(b && b.n) || 0); });
    if (bars && max){
      var frag = document.createDocumentFragment();
      r.by.forEach(function(b, i){
        var n = num(b && b.n);
        if (n === null || !txt(b.label)) { return; }
        var li = el('li', 'pca-bar');
        li.style.setProperty('--i', i);
        var l = el('span', 'pca-bar__l');
        l.appendChild(el('b', '', txt(b.label)));
        if (txt(b.sub)) { l.appendChild(el('span', '', txt(b.sub))); }
        var t = el('span', 'pca-bar__t');
        t.setAttribute('aria-hidden', 'true');
        var fill = el('i');
        fill.style.setProperty('--w', (n / max * 100).toFixed(1) + '%');
        t.appendChild(fill);
        li.appendChild(l); li.appendChild(t); li.appendChild(el('span', 'pca-bar__c', fmt(n)));
        frag.appendChild(li);
      });
      if (frag.childNodes.length) { bars.innerHTML = ''; bars.appendChild(frag); }
    }
    if (list){
      var nf = document.createDocumentFragment();
      r.list.forEach(function(x){
        var url = safe(x && x.url), n = num(x && x.n);
        if (!url || n === null || !txt(x.name)) { return; }
        var li = el('li');
        var a = el('a', 'pca-nat');
        a.href = url + '#bp-register';
        var h = el('span', 'pca-nat__h');
        h.appendChild(el('b', '', txt(x.name)));
        h.appendChild(el('span', '', n + ' on record'));
        a.appendChild(h);
        if (txt(x.top)){
          var t = el('span', 'pca-nat__t');
          t.appendChild(el('span', '', txt(x.top)));
          if (txt(x.amount)) { t.appendChild(el(x.money ? 'em' : 'span', '', txt(x.amount))); }
          a.appendChild(t);
        }
        li.appendChild(a);
        nf.appendChild(li);
      });
      if (nf.childNodes.length) { list.innerHTML = ''; list.appendChild(nf); label(); }
    }
  }
  function get(i){
    if (i >= SRC.length || !window.fetch) { return; }
    fetch(SRC[i], { cache: 'no-cache' }).then(function(res){
      if (!res.ok) { throw new Error('status ' + res.status); }
      return res.json();
    }).then(apply).catch(function(){ get(i + 1); });
  }
  get(0);
})();
