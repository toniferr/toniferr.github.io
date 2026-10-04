// Progressive enhancement only: the page is complete and readable without this file.
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  // ------------------------------------------------------------ theme

  var themeBtn = $(".theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) { /* not persisted, still switched */ }
    });
  }

  // ------------------------------------------------------------ top bar & mobile nav

  var topbar = $("#topbar");
  function onScroll() { if (topbar) topbar.classList.toggle("is-scrolled", window.scrollY > 12); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var nav = $(".nav");
  var navToggle = $(".nav-toggle");
  if (nav && navToggle) {
    navToggle.addEventListener("click", function () {
      var open = !nav.classList.contains("open");
      nav.classList.toggle("open", open);
      navToggle.setAttribute("aria-expanded", String(open));
    });
    $$(".nav-links a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Language links keep the section you're reading.
  function syncLangLinks() {
    $$(".lang-link").forEach(function (a) {
      a.href = a.href.split("#")[0] + (location.hash || "");
    });
  }
  window.addEventListener("hashchange", syncLangLinks);

  // ------------------------------------------------------------ reveal on scroll

  // Stagger diagram parts by their data-i index (CSSOM writes are allowed by the CSP).
  $$(".dg [data-i]").forEach(function (el) { el.style.setProperty("--i", el.getAttribute("data-i")); });

  var revealTargets = $$(".reveal, .dg:not(.dg-hero)");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("in-view");
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: "0px 0px -10% 0px", threshold: 0.12 });
    revealTargets.forEach(function (el) { io.observe(el); });
  } else {
    revealTargets.forEach(function (el) { el.classList.add("in-view"); });
  }

  // Active section in the nav.
  var navLinks = $$("[data-nav]");
  if ("IntersectionObserver" in window && navLinks.length) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        navLinks.forEach(function (a) {
          a.classList.toggle("is-active", a.getAttribute("data-nav") === en.target.id);
        });
        if (history.replaceState && en.target.id) {
          history.replaceState(null, "", "#" + en.target.id);
          syncLangLinks();
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    $$("main > section[id]").forEach(function (s) { if (s.id !== "top") spy.observe(s); });
  }

  // ------------------------------------------------------------ count-up figures

  function countUp(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    if (!target || target > 999 || reduceMotion) return;
    var start = null;
    function step(t) {
      if (start === null) start = t;
      var p = Math.min((t - start) / 1200, 1);
      el.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(step);
    }
    el.textContent = "0";
    requestAnimationFrame(step);
  }
  var figs = $$(".fig dd[data-count]");
  if ("IntersectionObserver" in window && figs.length) {
    var fio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { countUp(en.target); fio.unobserve(en.target); }
      });
    }, { threshold: 0.6 });
    figs.forEach(function (f) { fio.observe(f); });
  }

  // ------------------------------------------------------------ hero diagram: live traffic

  var hero = $(".dg-hero");
  if (hero) {
    requestAnimationFrame(function () { hero.classList.add("in-view"); });

    var NS = "http://www.w3.org/2000/svg";
    var edges = $$(".dg-edge-g", hero).map(function (g) {
      var path = $(".dg-flow", g);
      return { from: g.getAttribute("data-from"), to: g.getAttribute("data-to"), g: g, path: path, len: path.getTotalLength() };
    });
    var nodes = {};
    $$(".dg-node", hero).forEach(function (n) { nodes[n.getAttribute("data-id")] = n; });
    var incoming = {};
    edges.forEach(function (e) { incoming[e.to] = true; });
    var entry = Object.keys(nodes).filter(function (id) { return !incoming[id]; })[0];

    function outEdges(id) { return edges.filter(function (e) { return e.from === id; }); }

    // Path of edges from the entry node to `target` (breadth-first), or null.
    function pathTo(target) {
      var queue = [[entry, []]], seen = {};
      while (queue.length) {
        var item = queue.shift(), id = item[0], trail = item[1];
        if (id === target) return trail;
        if (seen[id]) continue;
        seen[id] = true;
        outEdges(id).forEach(function (e) { queue.push([e.to, trail.concat([e])]); });
      }
      return null;
    }

    function randomWalk() {
      var trail = [], id = entry, guard = 0;
      while (guard++ < 8) {
        var outs = outEdges(id);
        if (!outs.length) break;
        var e = outs[Math.floor(Math.random() * outs.length)];
        trail.push(e);
        id = e.to;
        if (outs.length > 1 && Math.random() < 0.25) break; // some requests end at a service
      }
      return trail;
    }

    var layer = document.createElementNS(NS, "g");
    layer.setAttribute("class", "packets");
    layer.setAttribute("aria-hidden", "true");
    hero.appendChild(layer);

    var packets = [];
    var focus = null;
    var SPEED = 0.24; // px per ms

    function spawn(trail, hot) {
      if (!trail || !trail.length || packets.length > 24) return;
      var c = document.createElementNS(NS, "circle");
      c.setAttribute("r", hot ? "3.6" : "2.8");
      c.setAttribute("class", hot ? "packet hot" : "packet");
      layer.appendChild(c);
      packets.push({ el: c, trail: trail, seg: 0, dist: 0 });
    }

    function highlight(id) {
      focus = id;
      hero.classList.toggle("has-hl", !!id);
      var related = {};
      if (id) {
        related[id] = true;
        var trail = pathTo(id) || [];
        trail.forEach(function (e) { related[e.from] = true; });
        edges.forEach(function (e) { if (e.from === id) related[e.to] = true; });
      }
      Object.keys(nodes).forEach(function (k) { nodes[k].classList.toggle("hl", !!related[k]); });
      edges.forEach(function (e) {
        var on = !!(id && related[e.from] && related[e.to] && (e.from === id || e.to === id || (pathTo(id) || []).indexOf(e) >= 0));
        e.g.classList.toggle("hl", on);
      });
      if (id) spawn(pathTo(id), true);
    }

    $$(".dg-node", hero).forEach(function (n) {
      var id = n.getAttribute("data-id");
      var target = n.closest("a") || n;
      target.addEventListener("mouseenter", function () { highlight(id); });
      target.addEventListener("mouseleave", function () { highlight(null); });
      target.addEventListener("focus", function () { highlight(id); });
      target.addEventListener("blur", function () { highlight(null); });
    });

    var running = false, last = 0, sinceSpawn = 0;
    function frame(t) {
      if (!running) return;
      var dt = last ? Math.min(t - last, 64) : 16;
      last = t;
      sinceSpawn += dt;
      var interval = focus ? 380 : 650;
      if (sinceSpawn > interval) {
        sinceSpawn = 0;
        spawn(focus ? pathTo(focus) : randomWalk(), !!focus);
      }
      for (var i = packets.length - 1; i >= 0; i--) {
        var p = packets[i], e = p.trail[p.seg];
        p.dist += dt * SPEED;
        if (p.dist > e.len) {
          p.dist -= e.len;
          p.seg++;
          if (p.seg >= p.trail.length) {
            layer.removeChild(p.el);
            packets.splice(i, 1);
            continue;
          }
          e = p.trail[p.seg];
        }
        var pt = e.path.getPointAtLength(p.dist);
        p.el.setAttribute("cx", pt.x.toFixed(1));
        p.el.setAttribute("cy", pt.y.toFixed(1));
      }
      requestAnimationFrame(frame);
    }
    function setRunning(on) {
      if (on === running || reduceMotion) return;
      running = on;
      last = 0;
      if (on) requestAnimationFrame(frame);
    }
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) { setRunning(en[0].isIntersecting && !document.hidden); }).observe(hero);
    } else {
      setRunning(true);
    }
    document.addEventListener("visibilitychange", function () { setRunning(!document.hidden && hero.getBoundingClientRect().bottom > 0); });

    // Subtle parallax on the hero diagram.
    var heroSection = $(".hero");
    if (heroSection && !reduceMotion && window.matchMedia("(hover: hover)").matches) {
      heroSection.addEventListener("mousemove", function (ev) {
        var r = heroSection.getBoundingClientRect();
        var x = (ev.clientX - r.left) / r.width - 0.5, y = (ev.clientY - r.top) / r.height - 0.5;
        hero.style.transform = "translate(" + (x * -10).toFixed(1) + "px," + (y * -8).toFixed(1) + "px)";
      });
      heroSection.addEventListener("mouseleave", function () { hero.style.transform = ""; });
    }
  }

  // ------------------------------------------------------------ CAD-style cursor readout

  var readout = $(".readout");
  if (readout && window.matchMedia("(hover: hover)").matches) {
    var rx = $(".rx", readout), ry = $(".ry", readout), idle;
    var pad = function (n) { return ("0000" + Math.max(0, Math.round(n))).slice(-4); };
    window.addEventListener("mousemove", function (ev) {
      rx.textContent = "X " + pad(ev.pageX);
      ry.textContent = "Y " + pad(ev.pageY);
      readout.classList.add("on");
      clearTimeout(idle);
      idle = setTimeout(function () { readout.classList.remove("on"); }, 1800);
    }, { passive: true });
  }

  // ------------------------------------------------------------ tooltips for chart marks

  var tip = $(".tip");
  if (tip) {
    document.addEventListener("mouseover", function (ev) {
      var t = ev.target.closest && ev.target.closest("[data-tip]");
      if (!t) { tip.hidden = true; return; }
      tip.textContent = t.getAttribute("data-tip");
      tip.hidden = false;
    });
    document.addEventListener("mousemove", function (ev) {
      if (tip.hidden) return;
      var w = tip.offsetWidth, x = ev.clientX + 14;
      if (x + w > window.innerWidth - 8) x = ev.clientX - w - 14;
      tip.style.left = x + "px";
      tip.style.top = (ev.clientY + 16) + "px";
    }, { passive: true });
  }

  // Show the most recent weeks of the contribution calendar on narrow screens.
  $$(".heatmap-scroll").forEach(function (s) { s.scrollLeft = s.scrollWidth; });

  // ------------------------------------------------------------ career filter (professional / open source / education)

  var filterBtns = $$(".tl-legend button[data-filter]");
  var tlItems = $$(".timeline .tl-item");
  function applyFilter(track) {
    filterBtns.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-filter") === track)); });
    var shown = 0;
    tlItems.forEach(function (li) {
      var show = track === "all" || li.getAttribute("data-track") === track;
      li.hidden = !show;
      if (!show) return;
      // Re-flow the zigzag over the visible entries only.
      li.classList.toggle("is-right", shown % 2 === 1);
      li.classList.toggle("is-after", shown > 0);
      li.classList.add("in-view");
      shown++;
    });
  }
  filterBtns.forEach(function (b) {
    b.addEventListener("click", function () {
      var f = b.getAttribute("data-filter");
      applyFilter(b.getAttribute("aria-pressed") === "true" && f !== "all" ? "all" : f);
    });
  });

  // ------------------------------------------------------------ email, assembled client-side

  $$(".js-mail").forEach(function (a) {
    var addr = a.getAttribute("data-u") + "@" + a.getAttribute("data-d");
    a.href = "mailto:" + addr;
    var text = $(".js-mail-text", a);
    if (text) text.textContent = addr;
  });
})();
