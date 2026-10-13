/* M2ISDA 2027 — rubriques séparées, apparitions et transitions douces, langue, onglets, compte à rebours */
(function () {
  'use strict';
  var doc = document;
  var $ = function (s, r) { return (r || doc).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); };
  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var lang = 'fr';

  /* ------------------------------------------------------------ langue */
  var DICT = {
    copied: { fr: 'Copié ✓', en: 'Copied ✓' },
    inDays: { fr: function (n) { return 'Dans ' + n + ' jours'; }, en: function (n) { return 'In ' + n + ' days'; } },
    tomorrow: { fr: 'Demain', en: 'Tomorrow' }, today: { fr: 'Aujourd’hui', en: 'Today' }, past: { fr: 'Passé', en: 'Past' }
  };
  var TITLES = { fr: 'M2ISDA 2027 — Djibouti, 19–21 janvier 2027', en: 'M2ISDA 2027 — Djibouti, 19–21 January 2027' };

  function applyLang(l) {
    lang = l; doc.documentElement.lang = l;
    $$('[data-en]').forEach(function (el) {
      if (el.getAttribute('data-fr') === null) el.setAttribute('data-fr', el.textContent);
      el.textContent = el.getAttribute('data-' + l);
    });
    $$('[data-lang]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === l)); });
    var pf = $('#poster-fr'), pe = $('#poster-en');
    if (pf && pe) { pf.hidden = l !== 'fr'; pe.hidden = l === 'fr'; }
    $$('[data-copy]').forEach(function (b) { b.textContent = b.getAttribute('data-label-' + l); });
    doc.title = TITLES[l];
    milestones();
    try { localStorage.setItem('m2isda_lang', l); } catch (e) {}
  }
  $$('[data-lang]').forEach(function (b) { b.addEventListener('click', function () { applyLang(b.getAttribute('data-lang')); }); });

  /* ------------------------------------------------------------ apparitions au défilement */
  var hasIO = 'IntersectionObserver' in window;
  var io = hasIO ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
  }, { threshold: 0, rootMargin: '0px 0px -6% 0px' }) : null;

  function countUp(el) {
    var n = +el.getAttribute('data-count'); if (reduced) { el.textContent = String(n); return; }
    var t0 = performance.now(), D = 1500; el.textContent = '0';
    (function f(now) {
      var p = Math.min(1, (now - t0) / D); el.textContent = String(Math.round(n * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(f); else el.textContent = String(n);
    })(t0);
  }
  var cio = hasIO ? new IntersectionObserver(function (es) {
    es.forEach(function (en) { if (en.isIntersecting) { cio.unobserve(en.target); countUp(en.target); } });
  }, { threshold: 0.5 }) : null;

  /* (ré)arme les apparitions d'une rubrique à chaque affichage */
  function arm(page) {
    $$('.rv', page).forEach(function (el) { el.classList.remove('in'); if (io) io.observe(el); else el.classList.add('in'); });
    $$('[data-count]', page).forEach(function (el) { if (cio) cio.observe(el); });
  }

  /* ------------------------------------------------------------ rubriques (une seule visible) */
  var pages = $$('.page'), current = null;
  var navLinks = $$('.side-nav a, .drawer a');
  var top = $('#top'), burger = $('#burger'), drawer = $('#drawer');
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';

  function pageOf(el) { return el && (el.classList.contains('page') ? el : el.closest('.page')); }
  function setCurrent(page) {
    pages.forEach(function (p) { p.classList.toggle('cur', p === page); });
    navLinks.forEach(function (a) {
      var on = a.getAttribute('href') === '#' + page.id;
      if (on) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
    });
  }
  function enter(page) {
    page.classList.remove('is-in'); void page.offsetWidth; page.classList.add('is-in');
    arm(page);
  }
  function scrollToEl(el) {
    var y = el.getBoundingClientRect().top + window.scrollY - (top.offsetHeight + 16);
    window.scrollTo({ top: y, behavior: reduced ? 'auto' : 'smooth' });
  }
  function route(id, first) {
    if (id === 'top') { window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }); return; }
    if (id === 'contenu') { var m = $('#contenu'); if (m) { m.focus({ preventScroll: true }); scrollToEl(m); } return; }
    var el = id ? doc.getElementById(id) : null, page = pageOf(el) || doc.getElementById('accueil');
    if (page !== current) {
      current = page; setCurrent(page); enter(page);
      window.scrollTo({ top: 0, behavior: 'auto' });
    } else if (first) { arm(page); }
    if (el && el !== page) setTimeout(function () { scrollToEl(el); }, 80);
  }

  /* liens internes : changent de rubrique sans défiler vers les autres */
  doc.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a) return;
    var id = a.getAttribute('href').slice(1); if (!id) return;
    e.preventDefault();
    if (location.hash !== '#' + id) history.pushState(null, '', '#' + id);
    route(id);
  });
  addEventListener('popstate', function () { route(location.hash.slice(1)); });

  /* ------------------------------------------------------------ menu mobile */
  function setMenu(open) { burger.setAttribute('aria-expanded', String(open)); drawer.hidden = !open; }
  burger.addEventListener('click', function () { setMenu(drawer.hidden); });
  $$('a', drawer).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !drawer.hidden) { setMenu(false); burger.focus(); } });
  doc.addEventListener('click', function (e) { if (!drawer.hidden && !top.contains(e.target)) setMenu(false); });
  matchMedia('(min-width:1000px)').addEventListener('change', function (e) { if (e.matches) setMenu(false); });

  var ticking = false;
  function onScroll() { ticking = false; top.classList.toggle('scrolled', window.scrollY > 8); }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ------------------------------------------------------------ compte à rebours & jalons */
  var target = new Date('2027-01-19T08:00:00+03:00').getTime(), cd = { d: $('#cd-d'), h: $('#cd-h'), m: $('#cd-m'), s: $('#cd-s') };
  function pad(n) { return String(n).padStart(2, '0'); }
  function tick() {
    var t = Math.max(0, target - Date.now()) / 1000, d = Math.floor(t / 86400); t -= d * 86400;
    var h = Math.floor(t / 3600); t -= h * 3600; var m = Math.floor(t / 60), s = Math.floor(t - m * 60);
    cd.d.textContent = String(d); cd.h.textContent = pad(h); cd.m.textContent = pad(m); cd.s.textContent = pad(s);
  }
  tick(); setInterval(tick, 1000);
  function milestones() {
    $$('.step').forEach(function (li) {
      var dd = Math.ceil((new Date(li.getAttribute('data-iso') + 'T00:00:00+03:00').getTime() - Date.now()) / 86400000);
      $('.step-left', li).textContent = dd > 1 ? DICT.inDays[lang](dd) : dd === 1 ? DICT.tomorrow[lang] : dd === 0 ? DICT.today[lang] : DICT.past[lang];
    });
  }

  /* ------------------------------------------------------------ onglets : programme & comités */
  var dayTabs = $$('.tab'), dayPanels = $$('.day');
  function showDay(i) {
    dayTabs.forEach(function (t, k) { var on = k === i; t.classList.toggle('on', on); t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; });
    dayPanels.forEach(function (p, k) { p.hidden = k !== i; });
  }
  dayTabs.forEach(function (t, i) {
    t.addEventListener('click', function () { showDay(i); });
    t.addEventListener('keydown', function (e) {
      var n = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0; if (!n) return;
      e.preventDefault(); var k = (i + n + dayTabs.length) % dayTabs.length; showDay(k); dayTabs[k].focus();
    });
  });
  showDay(0);


  /* ------------------------------------------------------------ copier */
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

  /* ------------------------------------------------------------ démarrage */
  try { var saved = localStorage.getItem('m2isda_lang'); if (saved === 'en' || saved === 'fr') lang = saved; } catch (e) {}
  applyLang(lang);
  var start = doc.querySelector('.page.cur') || doc.getElementById('accueil');
  current = start; setCurrent(start); enter(start);
  var h = location.hash.slice(1), he = h && doc.getElementById(h);
  if (he && he !== start) setTimeout(function () { scrollToEl(he); }, 400);
})();
