/* PERFECT NATIONS - A STATE BLUEPRINT - script. The county map: hover or tap a county for its share below the poverty line. */
(function(){
  var root = document.getElementById('ROOT');
  if (!root || root.__pnst) { return; }
  root.__pnst = 1;
  var ch = root.querySelector('.pnst-ch'), tip = root.querySelector('.pnst-tip');
  if (!ch || !tip) { return; }
  var paths = Array.prototype.slice.call(ch.querySelectorAll('path[data-n]'));
  var pinned = null;
  function fill(p){
    tip.innerHTML = '';
    var b = document.createElement('b');
    b.textContent = p.getAttribute('data-n');
    tip.appendChild(b);
    tip.appendChild(document.createTextNode(p.getAttribute('data-v') + '% below the poverty line'));
    tip.appendChild(document.createElement('br'));
    tip.appendChild(document.createTextNode(p.getAttribute('data-p') + ' people'));
  }
  function place(p, ev){
    var box = ch.getBoundingClientRect(), r = p.getBoundingClientRect();
    var x = ev && ev.clientX ? ev.clientX - box.left : (r.left + r.right) / 2 - box.left;
    var y = ev && ev.clientY ? ev.clientY - box.top : r.top - box.top;
    tip.hidden = false;
    var w = tip.offsetWidth, h = tip.offsetHeight;
    var left = Math.max(0, Math.min(box.width - w, x - w / 2));
    var top = y - h - 12;
    if (0 > top) { top = Math.min(box.height - h, y + 16); }
    tip.style.left = Math.round(left) + 'px';
    tip.style.top = Math.round(top) + 'px';
  }
  function on(p, ev){
    paths.forEach(function(q){ q.classList.toggle('is-on', q === p); });
    fill(p);
    place(p, ev);
  }
  function off(){
    pinned = null;
    tip.hidden = true;
    paths.forEach(function(q){ q.classList.remove('is-on'); });
  }
  paths.forEach(function(p){
    p.addEventListener('mousemove', function(ev){ if (!pinned) { on(p, ev); } });
    p.addEventListener('mouseleave', function(){ if (!pinned) { off(); } });
    p.addEventListener('click', function(ev){
      if (pinned === p) { off(); return; }
      pinned = p;
      on(p, ev);
    });
    p.addEventListener('focus', function(){ on(p); });
    p.addEventListener('blur', function(){ if (!pinned) { off(); } });
    p.addEventListener('keydown', function(ev){
      if (ev.key === 'Enter' || ev.key === ' ' || ev.key === 'Spacebar') { ev.preventDefault(); pinned = p; on(p); }
    });
  });
  document.addEventListener('click', function(ev){ if (pinned && !ch.contains(ev.target)) { off(); } });
  document.addEventListener('keydown', function(ev){ if (ev.key === 'Escape') { off(); } });
})();
