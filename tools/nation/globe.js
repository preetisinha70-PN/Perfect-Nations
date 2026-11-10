(function pnGlobe() {
  /* The nation globe (blueprint v10.0; v11.8 below). A small WebGL picture of the Earth, drawn by this page alone:
     no globe.gl and no three.js (about 290 KB of script that every blueprint used to download).
     - The Earth is NASA Blue Marble (Media Library: pn-globe-earth-day, the 1536 px copy on laptops,
       the 1024 px copy on phones). The nation is painted in gold from its outline, built into the page.
     - Order of appearance: an Earthrise sphere at once (CSS), then the Earth as soon as its picture loads.
     - It turns gently back and forth around the nation, so the nation never leaves the view.
     - It draws only while on screen and while the tab is visible, at most 30 frames a second, and at a
       capped pixel ratio (1.25 phones, 1.5 laptops). It asks the laptop for its low-power graphics chip.
     - If the browser takes the drawing surface away (a graphics reset), the still Earth shows in its place
       and the moving globe returns by itself when the surface is restored.
     - Without WebGL it draws one still Earth on a plain canvas. With reduced motion it draws one frame.
     v11.8 (10 Nov 2026, some globes showed only the blue placeholder and a dot on phones):
     - The globe with the nation in gold is now drawn into the page by the build (SVG), so the map shows at once and
       stays whenever the Earth cannot be shown.
     - If this script runs before the globe is on the page (a cache or optimiser that moves scripts), it waits for it.
     - The Earth picture is asked for at the page's own address first (an optimiser or CDN that rewrites the address
       to another host makes the picture unusable for drawing), then as written, then in the other size.
     - data-globe on the globe says how it ended: gl, still, or map (the drawn map alone). */
  /*pn:globe-cfg*/
  var root = document.getElementById(CFG.root);
  if (!root && document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', pnGlobe); return; }
  var wrap = root && root.querySelector('.bpx-globe');
  if (!wrap || wrap.getAttribute('data-ready') === '1') return;
  wrap.setAttribute('data-ready', '1');
  var cv = wrap.querySelector('canvas.bpx-globe__gl');
  var still = wrap.querySelector('canvas.bpx-globe__still');
  if (!cv || !still) return;
  var phone = window.matchMedia('(max-width:767px)').matches;
  var calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var D2R = Math.PI / 180;
  var natLat = CFG.lat * D2R, natLng = CFG.lng * D2R;
  function own(u) { try { var a = new URL(u, location.href); return location.origin + a.pathname; } catch (e) { return u; } }
  var first = phone ? CFG.tex.sm : CFG.tex.lg, other = phone ? CFG.tex.lg : CFG.tex.sm, tries = [];
  [own(first), first, own(other)].forEach(function (u) { if (u && tries.indexOf(u) < 0) tries.push(u); });
  var img = null;
  function fetchEarth(i) {
    if (i >= tries.length) { wrap.classList.add('is-failed'); wrap.setAttribute('data-globe', 'map'); return; }
    img = new Image();
    img.decoding = 'async';
    img.crossOrigin = 'anonymous';
    img.onload = function () { start(); };
    img.onerror = function () { fetchEarth(i + 1); };
    img.src = tries[i];
  }
  wrap.setAttribute('data-globe', 'map');
  fetchEarth(0);

  /* The nation's outline, painted once into a small picture (red: the land; green: its edge). */
  function wrapLon(d) { d = (d + 540) % 360 - 180; return d; }
  function maskBox() {
    var x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9, n = 0;
    (CFG.outline || []).forEach(function (g) {
      var polys = g.type === 'MultiPolygon' ? g.coordinates : [g.coordinates];
      polys.forEach(function (rings) { rings.forEach(function (ring) { ring.forEach(function (p) {
        var x = wrapLon(p[0] - CFG.lng); n++;
        if (x < x0) x0 = x; if (x > x1) x1 = x; if (p[1] < y0) y0 = p[1]; if (p[1] > y1) y1 = p[1];
      }); }); });
    });
    if (!n) return null;
    var mx = Math.max(0.8, (x1 - x0) * 0.08), my = Math.max(0.8, (y1 - y0) * 0.08);
    return [x0 - mx, y0 - my, x1 + mx, y1 + my];
  }
  var box = maskBox();
  var small = !box || ((box[2] - box[0]) * (box[3] - box[1]) < 40);
  function paintMask() {
    var bw = (box[2] - box[0]) * Math.cos(((box[1] + box[3]) / 2) * D2R), bh = box[3] - box[1];
    var W = bw >= bh ? 512 : Math.max(64, Math.round(512 * bw / bh)), H = bh > bw ? 512 : Math.max(64, Math.round(512 * bh / bw));
    var c = document.createElement('canvas'); c.width = W; c.height = H;
    var x = c.getContext('2d');
    function trace() {
      x.beginPath();
      (CFG.outline || []).forEach(function (g) {
        var polys = g.type === 'MultiPolygon' ? g.coordinates : [g.coordinates];
        polys.forEach(function (rings) { rings.forEach(function (ring) {
          ring.forEach(function (p, i) {
            var px = (wrapLon(p[0] - CFG.lng) - box[0]) / (box[2] - box[0]) * W, py = (box[3] - p[1]) / (box[3] - box[1]) * H;
            if (i) x.lineTo(px, py); else x.moveTo(px, py);
          });
          x.closePath();
        }); });
      });
    }
    x.fillStyle = '#000'; x.fillRect(0, 0, W, H);
    trace(); x.fillStyle = 'rgb(255,0,0)'; x.fill('evenodd');
    x.globalCompositeOperation = 'lighter';
    trace(); x.strokeStyle = 'rgb(0,255,0)'; x.lineJoin = 'round'; x.lineWidth = Math.max(2, W / 150); x.stroke();
    return c;
  }

  /* The view: centred on the nation, swaying 24 degrees either side over a minute. */
  function view(t) {
    var lon = natLng + (calm ? 0 : Math.sin(t * 2 * Math.PI / 60) * 24 * D2R);
    var lat = natLat * 0.82;
    var cp = Math.cos(lon), sp = Math.sin(lon), cl = Math.cos(lat), sl = Math.sin(lat);
    return [cp, -sp * sl, sp * cl, 0, cl, sl, -sp, -cp * sl, cp * cl];
  }
  /* A camera 2.25 radii from the centre, as a satellite sees it: the nation comes closer than on a flat disc. */
  var DIST = 2.25, RAD = 0.47, TANA = Math.tan(Math.asin(1 / DIST));
  var NAT = [Math.cos(natLat) * Math.sin(natLng), Math.sin(natLat), Math.cos(natLat) * Math.cos(natLng)];

  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    '#ifdef GL_FRAGMENT_PRECISION_HIGH', 'precision highp float;', '#else', 'precision mediump float;', '#endif',
    'uniform vec2 uRes;uniform float uR,uF,uD;uniform vec3 uM0,uM1,uM2;uniform sampler2D uTex,uMask;',
    'uniform vec4 uBox;uniform float uNatLon,uTime,uHas,uSmall;uniform vec3 uNat;',
    'const float PI=3.14159265;',
    'void main(){',
    ' vec2 c=gl_FragCoord.xy-.5*uRes; float r=length(c);',
    ' float hl=clamp(1.-(r-uR)/(uR*.085),0.,1.); hl*=hl*.6; vec4 halo=vec4(vec3(.55,.84,.88)*hl,hl);',
    ' if(r>uR+1.){ gl_FragColor=halo; return; }',
    ' vec3 dir=normalize(vec3(c/uF,-1.)); vec3 O=vec3(0.,0.,uD); float b=dot(O,dir); float h2=max(b*b-dot(O,O)+1.,0.);',
    ' vec3 n=normalize(O+(-b-sqrt(h2))*dir); float facing=max(dot(n,-dir),0.);',
    ' vec3 w=vec3(dot(uM0,n),dot(uM1,n),dot(uM2,n));',
    ' float lat=asin(clamp(w.y,-1.,1.)); float lon=atan(w.x,w.z);',
    ' vec3 col=texture2D(uTex,vec2(lon/(2.*PI)+.5,.5-lat/PI)).rgb;',
    ' float df=max(dot(n,normalize(vec3(-.48,.42,.77))),0.);',
    ' col*=.5+.72*df;',
    ' if(uHas>.5){ float dl=mod(lon-uNatLon+PI,2.*PI)-PI;',
    '  vec2 m=vec2((dl-uBox.x)/(uBox.z-uBox.x),(uBox.w-lat)/(uBox.w-uBox.y));',
    '  if(m.x>0.&&m.x<1.&&m.y>0.&&m.y<1.){ vec4 k=texture2D(uMask,m);',
    '   col=mix(col,vec3(1.,.79,.28)*(.78+.42*df),k.r*.92); col=mix(col,vec3(1.,.95,.70),k.g*.9); } }',
    ' float d=acos(clamp(dot(w,uNat),-1.,1.)); float ph=fract(uTime*.4);',
    ' col=mix(col,vec3(1.,.88,.5),smoothstep(.007,0.,abs(d-(.014+ph*.1)))*(1.-ph)*.95);',
    ' if(uSmall>.5){ col=mix(col,vec3(1.,.83,.36),smoothstep(.02,.012,d)); col=mix(col,vec3(1.,.97,.8),smoothstep(.008,.004,d)); }',
    ' col+=vec3(.5,.8,.86)*pow(1.-facing,3.)*.55;',
    ' float aa=clamp(uR-r+.5,0.,1.); gl_FragColor=vec4(col*aa,aa)+halo*(1.-aa);',
    '}'].join('\n');

  var gl = null, prog = null, U = {}, raf = 0, last = 0, t0 = 0, onScreen = true, live = false, maskCanvas = null;
  function size() {
    var w = wrap.clientWidth, h = wrap.clientHeight, pr = Math.min(window.devicePixelRatio || 1, phone ? 1.25 : 1.5);
    var W = Math.max(2, Math.round(w * pr)), H = Math.max(2, Math.round(h * pr));
    if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
    return [W, H];
  }
  function shader(type, src) {
    var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
    return s;
  }
  function texture(unit, source) {
    var t = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, t);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);
  }
  function setup() {
    prog = gl.createProgram();
    gl.attachShader(prog, shader(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, shader(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error('link');
    gl.useProgram(prog);
    var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    ['uRes', 'uR', 'uF', 'uD', 'uM0', 'uM1', 'uM2', 'uTex', 'uMask', 'uBox', 'uNatLon', 'uTime', 'uHas', 'uSmall', 'uNat'].forEach(function (k) { U[k] = gl.getUniformLocation(prog, k); });
    texture(0, img); gl.uniform1i(U.uTex, 0);
    if (box) { maskCanvas = maskCanvas || paintMask(); texture(1, maskCanvas); }
    else { texture(1, still); }
    gl.uniform1i(U.uMask, 1);
    gl.uniform1f(U.uHas, box ? 1 : 0); gl.uniform1f(U.uSmall, small ? 1 : 0);
    if (box) gl.uniform4f(U.uBox, box[0] * D2R, box[1] * D2R, box[2] * D2R, box[3] * D2R);
    gl.uniform1f(U.uNatLon, natLng); gl.uniform3f(U.uNat, NAT[0], NAT[1], NAT[2]);
    gl.clearColor(0, 0, 0, 0);
  }
  function draw(now) {
    if (!gl || !prog) return;
    var s = size(), t = (now - t0) / 1000, m = view(t);
    gl.viewport(0, 0, s[0], s[1]); gl.clear(gl.COLOR_BUFFER_BIT);
    var R = Math.min(s[0], s[1]) * RAD;
    gl.uniform2f(U.uRes, s[0], s[1]); gl.uniform1f(U.uR, R); gl.uniform1f(U.uF, R / TANA); gl.uniform1f(U.uD, DIST);
    gl.uniform3f(U.uM0, m[0], m[1], m[2]); gl.uniform3f(U.uM1, m[3], m[4], m[5]); gl.uniform3f(U.uM2, m[6], m[7], m[8]);
    gl.uniform1f(U.uTime, calm ? 0.35 : t);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
  function loop(now) {
    raf = 0;
    if (!live || !onScreen || document.hidden) return;
    if (now - last >= 32) { last = now; draw(now); }
    raf = requestAnimationFrame(loop);
  }
  function go() { if (!raf && live && !calm) raf = requestAnimationFrame(loop); }

  /* The still Earth, drawn once on a plain canvas: the picture while WebGL starts, and the fallback. */
  function drawStill() {
    try {
      var w = wrap.clientWidth, h = wrap.clientHeight, pr = Math.min(window.devicePixelRatio || 1, 1.5);
      var W = Math.round(w * pr), H = Math.round(h * pr), R = Math.min(W, H) * RAD, cx = W / 2, cy = H / 2, F = R / TANA;
      still.width = W; still.height = H;
      var tw = img.naturalWidth, th = img.naturalHeight, tc = document.createElement('canvas');
      tc.width = tw; tc.height = th; var tx = tc.getContext('2d'); tx.drawImage(img, 0, 0);
      var src = tx.getImageData(0, 0, tw, th).data;
      var mk = null, mw = 0, mh = 0;
      if (box) { var mc = maskCanvas = maskCanvas || paintMask(); mw = mc.width; mh = mc.height; mk = mc.getContext('2d').getImageData(0, 0, mw, mh).data; }
      var sx = still.getContext('2d'), out = sx.createImageData(W, H), o = out.data, m = view(0);
      var L = [-0.48, 0.42, 0.77], ll = Math.sqrt(L[0] * L[0] + L[1] * L[1] + L[2] * L[2]);
      for (var py = 0; py < H; py++) {
        for (var px = 0; px < W; px++) {
          var ex = (px - cx), ey = (cy - py);
          if (ex * ex + ey * ey > R * R) continue;
          var dx = ex / F, dy = ey / F, dl2 = Math.sqrt(dx * dx + dy * dy + 1); dx /= dl2; dy /= dl2; var dz = -1 / dl2;
          var bb = DIST * dz, hh = Math.max(bb * bb - DIST * DIST + 1, 0), tt = -bb - Math.sqrt(hh);
          var x = tt * dx, y = tt * dy, z = DIST + tt * dz, facing = Math.max(-(x * dx + y * dy + z * dz), 0);
          var wx = m[0] * x + m[1] * y + m[2] * z, wy = m[3] * x + m[4] * y + m[5] * z, wz = m[6] * x + m[7] * y + m[8] * z;
          var lat = Math.asin(Math.max(-1, Math.min(1, wy))), lon = Math.atan2(wx, wz);
          var u = Math.min(tw - 1, Math.floor((lon / (2 * Math.PI) + 0.5) * tw)), v = Math.min(th - 1, Math.floor((0.5 - lat / Math.PI) * th));
          var k = (v * tw + u) * 4, df = Math.max(0, (x * L[0] + y * L[1] + z * L[2]) / ll), sh = 0.5 + 0.72 * df;
          var r = src[k] * sh, g = src[k + 1] * sh, b = src[k + 2] * sh;
          if (mk) {
            var dl = wrapLon(lon / D2R - CFG.lng), mx = (dl - box[0]) / (box[2] - box[0]), my = (box[3] - lat / D2R) / (box[3] - box[1]);
            if (mx > 0 && mx < 1 && my > 0 && my < 1) {
              var j = (Math.floor(my * mh) * mw + Math.floor(mx * mw)) * 4, f = mk[j] / 255 * 0.92, e = mk[j + 1] / 255 * 0.9, gs = 0.78 + 0.42 * df;
              r = r + (255 * gs - r) * f; g = g + (201 * gs - g) * f; b = b + (71 * gs - b) * f;
              r = r + (255 - r) * e; g = g + (242 - g) * e; b = b + (178 - b) * e;
            }
          }
          var fr = Math.pow(1 - facing, 3) * 0.55; r += 128 * fr; g += 204 * fr; b += 219 * fr;
          var a = Math.max(0, Math.min(1, R - Math.sqrt((px - cx) * (px - cx) + (py - cy) * (py - cy))));
          var i = (py * W + px) * 4; o[i] = r; o[i + 1] = g; o[i + 2] = b; o[i + 3] = 255 * a;
        }
      }
      sx.putImageData(out, 0, 0);
      wrap.classList.add('is-still');
      if (!live) wrap.setAttribute('data-globe', 'still');
    } catch (e) { wrap.classList.add('is-failed'); }
  }

  function startGL() {
    try {
      gl = cv.getContext('webgl', { alpha: true, antialias: false, premultipliedAlpha: true, preserveDrawingBuffer: false, powerPreference: 'low-power' }) ||
           cv.getContext('experimental-webgl', { alpha: true, powerPreference: 'low-power' });
      if (!gl) return false;
      setup();
      t0 = performance.now(); draw(t0);
      live = true; wrap.classList.add('is-on'); wrap.setAttribute('data-globe', 'gl');
      return true;
    } catch (e) { gl = null; live = false; return false; }
  }
  function start() {
    if (!startGL()) { drawStill(); return; }
    go();
    /* the still Earth is drawn in idle time, ready for a graphics reset */
    var idle = window.requestIdleCallback || function (f) { return setTimeout(f, 1200); };
    idle(function () { if (!wrap.classList.contains('is-still')) drawStill(); });
  }
  cv.addEventListener('webglcontextlost', function (ev) {
    ev.preventDefault(); live = false; prog = null; wrap.classList.remove('is-on');
    if (raf) { cancelAnimationFrame(raf); raf = 0; }
    if (!wrap.classList.contains('is-still')) drawStill();
  }, false);
  cv.addEventListener('webglcontextrestored', function () {
    try { setup(); live = true; wrap.classList.add('is-on'); t0 = performance.now(); draw(t0); go(); } catch (e) {}
  }, false);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) { onScreen = en[0].isIntersecting; if (onScreen) go(); }, { rootMargin: '80px 0px' }).observe(wrap);
  }
  document.addEventListener('visibilitychange', function () { if (!document.hidden) go(); });
  var rs = 0;
  window.addEventListener('resize', function () {
    clearTimeout(rs);
    rs = setTimeout(function () { if (live && calm) draw(performance.now()); if (wrap.classList.contains('is-still') && !live) drawStill(); }, 150);
  });
})();
