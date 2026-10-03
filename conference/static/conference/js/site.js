(function(){
  var lang = "fr";
  var bf = document.getElementById("btn-fr"), be = document.getElementById("btn-en");
  function apply(l){
    lang = l;
    document.querySelectorAll("[data-fr]").forEach(function(el){
      var v = el.getAttribute("data-" + l);
      if (v !== null) el.textContent = v;
    });
    bf.setAttribute("aria-pressed", l === "fr");
    be.setAttribute("aria-pressed", l === "en");
    document.documentElement.lang = l;
    var pf = document.getElementById("poster-fr"), pe = document.getElementById("poster-en");
    if (pf && pe) { pf.hidden = (l !== "fr"); pe.hidden = (l === "fr"); }
    count();
  }
  bf.addEventListener("click", function(){ apply("fr"); });
  be.addEventListener("click", function(){ apply("en"); });

  var el = document.getElementById("countdown");
  function count(){
    var d = Math.ceil((new Date("2027-01-19T08:00:00+03:00") - new Date()) / 86400000);
    if (d > 0) {
      el.innerHTML = lang === "fr"
        ? "<b>J\u2212" + d + "</b> avant l\u2019ouverture"
        : "<b>" + d + " days</b> to go";
    } else {
      el.textContent = lang === "fr" ? "La conf\u00e9rence a eu lieu." : "The conference has taken place.";
    }
  }
  count();

  var ctex = document.getElementById("copy-tex");
  if (ctex) ctex.addEventListener("click", function(){
    var src = document.getElementById("tex-src").textContent;
    var done = function(t){ ctex.textContent = t; setTimeout(function(){
      ctex.textContent = lang === "fr" ? "Copier le code" : "Copy the code"; }, 1800); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(src).then(function(){
        done(lang === "fr" ? "Copié" : "Copied");
      }).catch(function(){
        var r = document.createRange(); r.selectNodeContents(document.getElementById("tex-src"));
        var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
        done(lang === "fr" ? "Sélectionné" : "Selected");
      });
    }
  });

  document.querySelectorAll(".copy").forEach(function(btn){
    var node = btn.parentNode.querySelector(".mail");
    function back(){ setTimeout(function(){ btn.textContent = lang === "fr" ? "Copier" : "Copy"; }, 1800); }
    function select(){
      var r = document.createRange(); r.selectNodeContents(node);
      var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r);
      btn.textContent = lang === "fr" ? "Sélectionné" : "Selected"; back();
    }
    btn.addEventListener("click", function(){
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(node.textContent).then(function(){
          btn.textContent = lang === "fr" ? "Copié" : "Copied"; back();
        }).catch(select);
      } else { select(); }
    });
  });

  var links = {};
  document.querySelectorAll("[data-nav]").forEach(function(a){ links[a.getAttribute("data-nav")] = a; });
  var sections = {};
  document.querySelectorAll("main section").forEach(function(sec){ sections[sec.id] = sec; });

  function show(id, push){
    if (!sections[id]) id = "accueil";
    for (var k in sections) sections[k].hidden = (k !== id);
    for (var j in links) links[j].classList.toggle("active", j === id);
    if (push) {
      if (history.replaceState) history.replaceState(null, "", "#" + id);
      else location.hash = id;
    }
    window.scrollTo({ top: 0, behavior: "auto" });
    var cur = links[id], sc = cur && cur.parentNode;
    if (sc && sc.scrollWidth > sc.clientWidth + 4) {
      sc.scrollTo({ left: cur.offsetLeft - sc.clientWidth / 2 + cur.offsetWidth / 2, behavior: "smooth" });
    }
  }

  document.addEventListener("click", function(e){
    var a = e.target.closest ? e.target.closest('a[href^="#"]') : null;
    if (!a) return;
    var id = a.getAttribute("href").slice(1);
    if (!sections[id]) return;
    e.preventDefault();
    show(id, true);
  });
  window.addEventListener("hashchange", function(){ show(location.hash.slice(1), false); });
  show((location.hash || "#accueil").slice(1), false);

})();
