/* M2ISDA 2027 — interactions sobres : langue, menu, onglets, compte à rebours, apparitions douces */
(function () {
  'use strict';
  var doc = document;
  var $ = function (s, r) { return (r || doc).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); };
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

  /* ------------------------------------------------------------ en-tête & menu mobile */
  var top = $('#top'), burger = $('#burger'), drawer = $('#drawer');
  function setMenu(open) {
    burger.setAttribute('aria-expanded', String(open)); drawer.hidden = !open;
  }
  burger.addEventListener('click', function () { setMenu(drawer.hidden); });
  $$('a', drawer).forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !drawer.hidden) { setMenu(false); burger.focus(); } });
  doc.addEventListener('click', function (e) { if (!drawer.hidden && !top.contains(e.target)) setMenu(false); });
  if (matchMedia) matchMedia('(min-width:1100px)').addEventListener('change', function (e) { if (e.matches) setMenu(false); });

  var ticking = false;
  function onScroll() { ticking = false; top.classList.toggle('scrolled', window.scrollY > 8); }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* lien actif selon la section visible */
  var links = {};
  $$('#nav a').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        Object.keys(links).forEach(function (k) { links[k].classList.toggle('act', k === en.target.id); });
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(links).forEach(function (k) { var s = doc.getElementById(k); if (s) spy.observe(s); });
  }

  /* ------------------------------------------------------------ apparitions douces */
  var items = $$('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0, rootMargin: '0px 0px -6% 0px' });
    items.forEach(function (el) { io.observe(el); });
  } else items.forEach(function (el) { el.classList.add('in'); });

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

  var comBtns = $$('[data-com]'), comPanels = { org: $('#com-org'), sci: $('#com-sci') };
  function showCom(k) {
    comBtns.forEach(function (b) { var on = b.getAttribute('data-com') === k; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; });
    Object.keys(comPanels).forEach(function (p) { comPanels[p].hidden = p !== k; });
  }
  comBtns.forEach(function (b) {
    b.addEventListener('click', function () { showCom(b.getAttribute('data-com')); });
    b.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return; e.preventDefault();
      var o = b.getAttribute('data-com') === 'org' ? 'sci' : 'org'; showCom(o); $('[data-com="' + o + '"]').focus();
    });
  });
  showCom('org');

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
})();
