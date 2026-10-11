/* M2ISDA 2027 — interactions : loader, Lorenz, révélations, onglets, FR/EN */
(function () {
  'use strict';
  var doc = document, html = doc.documentElement;
  var $ = function (s, r) { return (r || doc).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); };
  var EASE = 'cubic-bezier(.16,1,.3,1)';
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = matchMedia('(hover:hover) and (pointer:fine)').matches;
  var wideMQ = matchMedia('(min-width:1180px)');
  var canAnim = typeof Element.prototype.animate === 'function';
  var lang = 'fr';

  /* ---------------------------------------------------------------- langue */
  var DICT = {
    menu: { fr: 'Menu', en: 'Menu' },
    close: { fr: 'Fermer', en: 'Close' },
    copied: { fr: 'Copié ✓', en: 'Copied ✓' },
    inDays: { fr: function (n) { return 'Dans ' + n + ' jours'; }, en: function (n) { return 'In ' + n + ' days'; } },
    tomorrow: { fr: 'Demain', en: 'Tomorrow' },
    today: { fr: 'Aujourd’hui', en: 'Today' },
    past: { fr: 'Passé', en: 'Past' }
  };
  var TITLES = { fr: 'M2ISDA 2027 — Djibouti, 19–21 janvier 2027', en: 'M2ISDA 2027 — Djibouti, 19–21 January 2027' };

  function renderLead() {
    var el = $('[data-words]'); if (!el) return;
    var text = el.getAttribute('data-lead-' + lang), acc = el.getAttribute('data-accent-' + lang).split(' ');
    el.innerHTML = '';
    text.split(' ').forEach(function (w) {
      var s = doc.createElement('span'); s.setAttribute('data-w', ''); s.textContent = w + ' ';
      if (acc.indexOf(w) > -1) s.className = 'acc';
      el.appendChild(s);
    });
    wordGroups = [{ c: el, w: $$('[data-w]', el) }];
    scrollDirty = true;
  }

  function applyLang(l) {
    lang = l; html.lang = l;
    $$('[data-en]').forEach(function (el) {
      if (el.getAttribute('data-fr') === null) el.setAttribute('data-fr', el.textContent);
      el.textContent = el.getAttribute('data-' + l);
    });
    $$('[data-lang]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === l)); });
    var pf = $('#poster-fr'), pe = $('#poster-en');
    if (pf && pe) { pf.hidden = l !== 'fr'; pe.hidden = l === 'fr'; }
    $$('[data-copy]').forEach(function (b) { b.textContent = b.getAttribute('data-label-' + l); });
    var ml = $('#menu-lbl'); if (ml) ml.textContent = menuOpen ? DICT.close[l] : DICT.menu[l];
    doc.title = TITLES[l];
    renderLead(); milestones();
    try { localStorage.setItem('m2isda_lang', l); } catch (e) {}
  }
  $$('[data-lang]').forEach(function (b) { b.addEventListener('click', function () { applyLang(b.getAttribute('data-lang')); }); });

  /* ---------------------------------------------------------------- état partagé */
  var menuOpen = false, wordGroups = [], scrollDirty = true, mx = innerWidth / 2, my = innerHeight / 2;
  var hot = false, rx = mx, ry = my, fx = mx, fy = my;

  /* ---------------------------------------------------------------- loader */
  var loader = $('#loader'), heroDone = false;
  function heroIn(base) {
    if (heroDone) return; heroDone = true;
    if (reduced || !canAnim) return;
    var b = base || 0;
    $$('[data-letter]').forEach(function (el, i) { el.animate([{ transform: 'translateY(110%) rotate(8deg)' }, { transform: 'none' }], { duration: 1500, delay: b + i * 70, easing: EASE, fill: 'both' }); });
    $$('[data-hero]').forEach(function (el, i) { el.animate([{ opacity: 0, transform: 'translateY(24px)' }, { opacity: 1, transform: 'none' }], { duration: 1200, delay: b + 500 + i * 90, easing: EASE, fill: 'both' }); });
    var cv = $('#hero-cv'); if (cv) cv.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 2400, delay: b, easing: 'ease-out', fill: 'both' });
  }
  function runLoader() {
    if (!loader) return heroIn();
    if (!html.classList.contains('intro') || !canAnim || doc.hidden) { loader.style.display = 'none'; return heroIn(); }
    try { sessionStorage.setItem('m2isda_intro', '1'); } catch (e) {}
    var num = $('#loader-num'), bar = $('#loader-bar'), t0 = performance.now(), D = 1300, fallback = setTimeout(done, 2600);
    function done() { clearTimeout(fallback); loader.style.display = 'none'; heroIn(); }
    (function step(now) {
      var p = Math.min(1, (now - t0) / D), e = 1 - Math.pow(1 - p, 3);
      num.textContent = String(Math.round(e * 100)); bar.style.transform = 'scaleX(' + e + ')';
      if (p < 1) return requestAnimationFrame(step);
      clearTimeout(fallback); heroIn(250);
      var a = loader.animate([{ clipPath: 'inset(0 0 0 0)' }, { clipPath: 'inset(0 0 100% 0)' }], { duration: 1100, easing: 'cubic-bezier(.76,0,.24,1)', fill: 'forwards' });
      a.onfinish = function () { loader.style.display = 'none'; };
    })(t0);
  }

  /* ---------------------------------------------------------------- révélations */
  function setupReveals() {
    if (reduced || !canAnim || !('IntersectionObserver' in window)) return;
    var KF = {
      up: [{ opacity: 0, transform: 'translateY(60px)' }, { opacity: 1, transform: 'none' }],
      fade: [{ opacity: 0 }, { opacity: 1 }],
      rise: [{ transform: 'translateY(110%)' }, { transform: 'none' }],
      line: [{ transform: 'scaleX(0)' }, { transform: 'scaleX(1)' }],
      scale: [{ opacity: 0, transform: 'scale(.9)', filter: 'blur(12px)' }, { opacity: 1, transform: 'none', filter: 'blur(0px)' }]
    };
    var pending = new Map();
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        (pending.get(en.target) || []).forEach(function (a) { a.play(); });
        io.unobserve(en.target);
      });
    }, { threshold: 0, rootMargin: '0px 0px -6% 0px' });
    $$('[data-reveal]').forEach(function (el) {
      var k = el.getAttribute('data-reveal');
      var a = el.animate(KF[k] || KF.up, { duration: k === 'line' ? 1600 : k === 'rise' ? 1300 : 1100, delay: +(el.getAttribute('data-delay') || 0), easing: EASE, fill: 'both' });
      a.pause();
      var tgt = k === 'rise' ? el.parentElement : el;
      if (!pending.has(tgt)) { pending.set(tgt, []); io.observe(tgt); }
      pending.get(tgt).push(a);
    });
    if ('IntersectionObserver' in window) {
      var cio = new IntersectionObserver(function (es) {
        es.forEach(function (en) {
          if (!en.isIntersecting) return; cio.unobserve(en.target);
          var el = en.target, n = +el.getAttribute('data-count'), t0 = performance.now(), D = 1800;
          el.textContent = '0';
          (function f(now) { var p = Math.min(1, (now - t0) / D); el.textContent = String(Math.round(n * (1 - Math.pow(2, -10 * p)))); if (p < 1) requestAnimationFrame(f); else el.textContent = String(n); })(t0);
        });
      }, { threshold: 0.4 });
      $$('[data-count]').forEach(function (el) { cio.observe(el); });
    }
  }
  function animIn(el) {
    if (!el || reduced || !canAnim) return;
    $$('[data-in]', el).forEach(function (c, i) {
      c.animate([{ opacity: 0, transform: 'translateY(28px)', filter: 'blur(8px)' }, { opacity: 1, transform: 'none', filter: 'blur(0px)' }], { duration: 900, delay: i * 55, easing: EASE, fill: 'backwards' });
    });
  }

  /* ---------------------------------------------------------------- marquees / magnétique */
  function setupMarquees() {
    if (reduced || !canAnim) return;
    $$('[data-marquee]').forEach(function (el) {
      var r = el.getAttribute('data-dir') === 'r';
      el.animate([{ transform: 'translateX(' + (r ? '-50%' : '0') + ')' }, { transform: 'translateX(' + (r ? '0' : '-50%') + ')' }], { duration: (+el.getAttribute('data-marquee') || 50) * 1000, iterations: Infinity });
    });
  }
  function setupMagnetic() {
    if (!fine || reduced) return;
    $$('[data-magnetic]').forEach(function (el) {
      el.addEventListener('mousemove', function (e) { var r = el.getBoundingClientRect(); el.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * .3) + 'px,' + ((e.clientY - r.top - r.height / 2) * .4) + 'px)'; });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------------------------------------------------------------- compte à rebours & jalons */
  function startCountdown() {
    var target = new Date('2027-01-19T08:00:00+03:00').getTime(), d = $('#cd-d'), h = $('#cd-h'), m = $('#cd-m'), s = $('#cd-s');
    var pad = function (n) { return String(n).padStart(2, '0'); };
    function tick() {
      var t = Math.max(0, target - Date.now()) / 1000, dd = Math.floor(t / 86400); t -= dd * 86400;
      var hh = Math.floor(t / 3600); t -= hh * 3600; var mm = Math.floor(t / 60), ss = Math.floor(t - mm * 60);
      d.textContent = String(dd); h.textContent = pad(hh); m.textContent = pad(mm); s.textContent = pad(ss);
    }
    tick(); setInterval(tick, 1000);
  }
  function milestones() {
    $$('.ms').forEach(function (li) {
      var dd = Math.ceil((new Date(li.getAttribute('data-iso') + 'T00:00:00+03:00').getTime() - Date.now()) / 86400000), el = $('.ms-left', li);
      el.textContent = dd > 1 ? DICT.inDays[lang](dd) : dd === 1 ? DICT.tomorrow[lang] : dd === 0 ? DICT.today[lang] : DICT.past[lang];
    });
  }

  /* ---------------------------------------------------------------- Lorenz */
  var cv = $('#hero-cv'), hero = $('#top'), ctx = cv && cv.getContext('2d'), cw = 0, ch = 0, dpr = 1, lzOn = false, heroVisible = true;
  var A, B, frame = 0, theta = .5, lzTxt = $('#lz-live'), lzD = $('#lz-d');
  function sizeCanvas() {
    if (!cv || !hero) return;
    var r = hero.getBoundingClientRect(); dpr = Math.min(wideMQ.matches ? 2 : 1.5, window.devicePixelRatio || 1);
    cw = r.width; ch = r.height; cv.width = Math.round(cw * dpr); cv.height = Math.round(ch * dpr);
  }
  function rk4(p, h) {
    var f = function (x, y, z) { return [10 * (y - x), x * (28 - z) - y, x * y - (8 / 3) * z]; };
    var x = p[0], y = p[1], z = p[2], k1 = f(x, y, z), k2 = f(x + h / 2 * k1[0], y + h / 2 * k1[1], z + h / 2 * k1[2]),
      k3 = f(x + h / 2 * k2[0], y + h / 2 * k2[1], z + h / 2 * k2[2]), k4 = f(x + h * k3[0], y + h * k3[1], z + h * k3[2]);
    return [x + h / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]), y + h / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]), z + h / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])];
  }
  function mk(p, N) { return { p: p, buf: new Float32Array(N * 3), i: 0, n: 0, N: N }; }
  function push(T) { var j = T.i * 3; T.buf[j] = T.p[0]; T.buf[j + 1] = T.p[1]; T.buf[j + 2] = T.p[2]; T.i = (T.i + 1) % T.N; T.n = Math.min(T.n + 1, T.N); }
  function resetB() { var a = A.p; B = mk([a[0] + 1e-5, a[1], a[2]], A.N); }
  function startLorenz() {
    if (!cv || !ctx) return;
    sizeCanvas();
    A = mk([-8, 8, 27], 2200);
    for (var k = 0; k < 1800; k++) { A.p = rk4(A.p, .007); push(A); }
    resetB(); lzOn = true;
    if ('IntersectionObserver' in window) new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; }).observe(hero);
    if (window.ResizeObserver) new ResizeObserver(sizeCanvas).observe(hero);
  }
  function drawLorenz() {
    if (!cw || !ch) { sizeCanvas(); if (!cw || !ch) return; }
    var w = cw, h = ch, wide = wideMQ.matches, steps = wide ? 4 : 3;
    for (var k = 0; k < steps; k++) { A.p = rk4(A.p, .007); push(A); B.p = rk4(B.p, .007); push(B); }
    frame++; if (frame % 2600 === 0) resetB();
    theta += .0016;
    var th = theta + (mx / innerWidth - .5) * .6, ph = .32 + (my / innerHeight - .5) * .35;
    var ct = Math.cos(th), st = Math.sin(th), cp = Math.cos(ph), sp = Math.sin(ph);
    var s = wide ? h / 56 : Math.min(w, h) / 50 * 1.15, cx = wide ? w * .64 : w * .5, cy = wide ? h * .5 : h * .42;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, w, h);
    ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
    function draw(T, rgb, maxA, lw) {
      var n = T.n, CH = 22, per = Math.ceil(n / CH), prev = null;
      for (var c = 0; c < CH; c++) {
        ctx.beginPath(); ctx.strokeStyle = 'rgba(' + rgb + ',' + (maxA * Math.pow((c + 1) / CH, 1.6)) + ')'; ctx.lineWidth = lw;
        if (prev) ctx.moveTo(prev[0], prev[1]);
        for (var q = c * per; q < Math.min(n, (c + 1) * per); q++) {
          var j = ((T.i - n + q + T.N) % T.N) * 3, x = T.buf[j], y = T.buf[j + 1], z = T.buf[j + 2] - 25;
          var X = x * ct - y * st, Y = x * st + y * ct, Z = z * cp - Y * sp, D = z * sp + Y * cp, f = 1 / (1 + D / 140);
          var px = cx + X * s * f, py = cy - Z * s * f;
          if (!prev && q === c * per) ctx.moveTo(px, py); else ctx.lineTo(px, py);
          prev = [px, py];
        }
        ctx.stroke();
      }
      return prev;
    }
    var kk = wide ? 1 : .6;
    draw(A, '242,237,228', .42 * kk, 1);
    var hb = draw(B, '228,71,43', .95 * kk, 1.3);
    if (hb && isFinite(hb[0]) && isFinite(hb[1])) {
      var g = ctx.createRadialGradient(hb[0], hb[1], 0, hb[0], hb[1], 22); g.addColorStop(0, 'rgba(228,71,43,.9)'); g.addColorStop(1, 'rgba(228,71,43,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(hb[0], hb[1], 22, 0, 7); ctx.fill();
      ctx.fillStyle = '#F2EDE4'; ctx.beginPath(); ctx.arc(hb[0], hb[1], 2.2, 0, 7); ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';
    if (frame % 4 === 0 && wide) {
      var a = A.p, b = B.p, fm = function (v) { return (v >= 0 ? ' ' : '') + v.toFixed(3); };
      if (lzTxt) lzTxt.textContent = 'x ' + fm(a[0]) + '   y ' + fm(a[1]) + '\nz ' + fm(a[2]);
      if (lzD) lzD.textContent = Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]).toExponential(2);
    }
  }

  /* ---------------------------------------------------------------- scroll & boucle d'animation */
  var prog = $('#nav-prog'), heroText = $('#hero-text'), campus = $('#campus-img');
  function onScroll() {
    var y = window.scrollY, H = html.scrollHeight - innerHeight, vh = innerHeight;
    if (prog) prog.style.transform = 'scaleX(' + (H > 0 ? y / H : 0) + ')';
    if (!reduced) {
      if (heroText && y < vh * 1.2) { heroText.style.transform = 'translateY(' + (y * .28) + 'px)'; heroText.style.opacity = String(Math.max(0, 1 - y / (vh * .95))); }
      if (cv && y < vh * 1.2) cv.style.transform = 'translateY(' + (y * .45) + 'px) scale(' + (1 + y / vh * .15) + ')';
      if (campus) { var r = campus.parentElement.getBoundingClientRect(); if (r.bottom > 0 && r.top < vh) campus.style.transform = 'translateY(' + (((r.top + r.height / 2 - vh / 2) / vh) * -60) + 'px)'; }
    }
    wordGroups.forEach(function (g) {
      if (reduced) return;
      var r = g.c.getBoundingClientRect(), p = Math.min(1, Math.max(0, (vh * .82 - r.top) / (r.height + vh * .35))), n = g.w.length, lit = p * n * 1.05;
      g.w.forEach(function (el, i) { el.style.opacity = i < lit ? '1' : '.16'; });
    });
  }
  addEventListener('scroll', function () { scrollDirty = true; }, { passive: true });
  addEventListener('resize', function () { scrollDirty = true; }, { passive: true });

  var ring = $('#cur-ring'), dot = $('#cur-dot'), fl = $('#float-pic'), flImg = $('#float-img');
  if (fine) {
    addEventListener('mousemove', function (e) {
      mx = e.clientX; my = e.clientY;
      hot = !!(e.target.closest && e.target.closest('a,button,.spk,.axe,.person,.partner'));
    }, { passive: true });
    html.classList.add('has-cursor');
  }
  var hoverIdx = null;
  function loop() {
    requestAnimationFrame(loop);
    if (fine) {
      rx += (mx - rx) * .2; ry += (my - ry) * .2;
      if (ring) ring.style.transform = 'translate(' + rx + 'px,' + ry + 'px) scale(' + (hot ? 1.9 : 1) + ')';
      if (dot) dot.style.transform = 'translate(' + mx + 'px,' + my + 'px)';
      if (fl && hoverIdx !== null) { fx += (mx - fx) * .12; fy += (my - fy) * .12; fl.style.transform = 'translate(' + (fx + 28) + 'px,' + (fy - 125) + 'px) rotate(' + ((mx - fx) * .06) + 'deg)'; }
    }
    if (scrollDirty) { scrollDirty = false; onScroll(); }
    if (lzOn && heroVisible && !doc.hidden && !reduced) drawLorenz();
  }

  /* ---------------------------------------------------------------- intervenants : vignette flottante */
  if (fine) {
    var list = $('#speakers');
    $$('.spk', list).forEach(function (row) {
      row.addEventListener('mouseenter', function () {
        $$('.spk.hot', list).forEach(function (r) { r.classList.remove('hot'); });
        row.classList.add('hot'); hoverIdx = row;
        if (wideMQ.matches && fl) { flImg.src = row.getAttribute('data-img'); fl.classList.add('on'); }
      });
    });
    if (list) list.addEventListener('mouseleave', function () {
      $$('.spk.hot', list).forEach(function (r) { r.classList.remove('hot'); }); hoverIdx = null; if (fl) fl.classList.remove('on');
    });
  }

  /* ---------------------------------------------------------------- onglets : programme & comités */
  var panels = $$('.day-panel'), tabs = $$('.day-tab');
  function showDay(i) {
    tabs.forEach(function (t, k) { var on = k === i; t.classList.toggle('on', on); t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; });
    panels.forEach(function (p, k) { p.hidden = k !== i; });
    animIn(panels[i]);
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { showDay(i); });
    t.addEventListener('keydown', function (e) {
      var n = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (!n) return;
      e.preventDefault(); var k = (i + n + tabs.length) % tabs.length; showDay(k); tabs[k].focus();
    });
  });
  showDay(0);

  var seg = $('.seg'), comBtns = $$('[data-com]'), comPanels = { org: $('#com-org'), sci: $('#com-sci') };
  function showCom(k) {
    seg.classList.toggle('sci', k === 'sci');
    comBtns.forEach(function (b) { var on = b.getAttribute('data-com') === k; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; });
    Object.keys(comPanels).forEach(function (p) { comPanels[p].hidden = p !== k; });
    animIn(comPanels[k]);
  }
  comBtns.forEach(function (b) {
    b.addEventListener('click', function () { showCom(b.getAttribute('data-com')); });
    b.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return; e.preventDefault();
      var o = b.getAttribute('data-com') === 'org' ? 'sci' : 'org'; showCom(o); $('[data-com="' + o + '"]').focus();
    });
  });
  showCom('org');

  /* ---------------------------------------------------------------- menu mobile */
  var menu = $('#menu'), menuBtn = $('#menu-btn');
  function setMenu(open) {
    menuOpen = open; menu.hidden = !open; menuBtn.setAttribute('aria-expanded', String(open));
    doc.body.classList.toggle('lock', open);
    var ml = $('#menu-lbl'); ml.textContent = open ? DICT.close[lang] : DICT.menu[lang];
    if (open) animIn(menu);
  }
  menuBtn.addEventListener('click', function () { setMenu(!menuOpen); });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menuOpen) { setMenu(false); menuBtn.focus(); } });
  wideMQ.addEventListener && wideMQ.addEventListener('change', function (e) { if (e.matches && menuOpen) setMenu(false); });

  /* ---------------------------------------------------------------- copier */
  var TEXTS = { mail: 'lamo@univ.edu.dj', code: '' };
  try { TEXTS.code = JSON.parse($('#tex-src').textContent); } catch (e) {}
  function fallbackCopy(txt) {
    var ta = doc.createElement('textarea'); ta.value = txt; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:-9999px;top:0';
    doc.body.appendChild(ta); ta.select(); try { doc.execCommand('copy'); } catch (e) {} ta.remove();
  }
  $$('[data-copy]').forEach(function (btn) {
    var t;
    btn.addEventListener('click', function () {
      var txt = TEXTS[btn.getAttribute('data-copy')];
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).catch(function () { fallbackCopy(txt); }); else fallbackCopy(txt);
      btn.textContent = DICT.copied[lang]; clearTimeout(t);
      t = setTimeout(function () { btn.textContent = btn.getAttribute('data-label-' + lang); }, 1800);
    });
  });

  /* ---------------------------------------------------------------- démarrage */
  try { var saved = localStorage.getItem('m2isda_lang'); if (saved === 'en' || saved === 'fr') lang = saved; } catch (e) {}
  applyLang(lang);
  setupReveals(); setupMarquees(); setupMagnetic(); startCountdown(); startLorenz();
  runLoader();
  requestAnimationFrame(loop);
})();
