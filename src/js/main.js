// Progressive enhancement only: the page is complete and readable without this file.
(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var canHover = window.matchMedia("(hover: hover)").matches;

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function isLight() { return root.getAttribute("data-theme") === "light"; }

  // ------------------------------------------------------------ theme

  var themeBtn = $(".theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = isLight() ? "dark" : "light";
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
    $$(".lang-link").forEach(function (a) { a.href = a.href.split("#")[0] + (location.hash || ""); });
  }
  window.addEventListener("hashchange", syncLangLinks);

  // ------------------------------------------------------------ the sky (canvas starfield)

  var sky = $(".sky");
  if (sky && sky.getContext) {
    var ctx = sky.getContext("2d");
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var W = 0, H = 0, stars = [], band = null, meteors = [], nextMeteor = 0;
    var mouseX = 0, mouseY = 0, colours = {};

    var hexToRgb = function (hex) {
      hex = hex.trim().replace("#", "");
      if (hex.length === 3) hex = hex.replace(/(.)/g, "$1$1");
      var n = parseInt(hex, 16);
      return [(n >> 16) & 255, (n >> 8) & 255, n & 255].join(",");
    };
    function readColours() {
      var cs = getComputedStyle(root);
      colours.star = hexToRgb(cs.getPropertyValue("--star"));
      colours.cool = hexToRgb(cs.getPropertyValue("--star-cool"));
      colours.gold = hexToRgb(cs.getPropertyValue("--accent"));
    }

    // The Milky Way: thousands of faint specks along a diagonal band, rendered once per resize.
    function paintBand() {
      band = document.createElement("canvas");
      band.width = W * dpr; band.height = H * dpr;
      var b = band.getContext("2d");
      b.scale(dpr, dpr);
      b.translate(W / 2, H / 2);
      b.rotate(-0.42);
      var len = Math.hypot(W, H);
      var g = b.createLinearGradient(0, -H * .22, 0, H * .22);
      g.addColorStop(0, "rgba(120,110,220,0)");
      g.addColorStop(.5, "rgba(150,140,255,0.07)");
      g.addColorStop(1, "rgba(120,110,220,0)");
      b.fillStyle = g;
      b.fillRect(-len / 2, -H * .22, len, H * .44);
      for (var i = 0; i < 2600; i++) {
        var x = (Math.random() - .5) * len;
        var y = (Math.random() + Math.random() + Math.random() - 1.5) * H * .14;
        b.fillStyle = "rgba(225,228,255," + (Math.random() * .35).toFixed(2) + ")";
        b.fillRect(x, y, Math.random() < .9 ? .7 : 1.3, Math.random() < .9 ? .7 : 1.3);
      }
    }

    function resize() {
      W = window.innerWidth; H = window.innerHeight;
      sky.width = W * dpr; sky.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.min(900, Math.round(W * H / 2100));
      stars = [];
      for (var i = 0; i < n; i++) {
        var depth = Math.pow(Math.random(), 2.2); // most stars are far and faint
        stars.push({
          x: Math.random() * W, y: Math.random() * H, depth: depth,
          r: .35 + depth * 1.5, a: .25 + depth * .75,
          phase: Math.random() * 6.3, speed: .4 + Math.random() * 1.6,
          warm: Math.random() < .3
        });
      }
      paintBand();
      draw(performance.now(), true);
    }

    function spawnMeteor(t) {
      var x = W * (.2 + Math.random() * .7), y = H * Math.random() * .45;
      meteors.push({ x: x, y: y, vx: -(5 + Math.random() * 4), vy: 2.2 + Math.random() * 2, born: t, life: 900 });
      nextMeteor = t + 5000 + Math.random() * 9000;
    }

    var last = 0;
    function draw(t, force) {
      if (!force && t - last < 33) return; // ~30 fps is plenty for a twinkle
      last = t;
      ctx.clearRect(0, 0, W, H);
      var light = isLight();
      var scroll = window.scrollY;
      if (!light && band) {
        ctx.globalAlpha = 1;
        ctx.drawImage(band, -mouseX * 4, -(scroll * .02 % H) - mouseY * 3, W, H);
      }
      for (var i = 0; i < stars.length; i++) {
        var s = stars[i];
        var tw = reduceMotion ? 1 : .7 + .3 * Math.sin(t / 1000 * s.speed + s.phase);
        var y = ((s.y - scroll * (.03 + s.depth * .12) - mouseY * s.depth * 10) % H + H) % H;
        var x = ((s.x - mouseX * s.depth * 14) % W + W) % W;
        var alpha = s.a * tw * (light ? .55 : 1);
        ctx.fillStyle = "rgba(" + (light ? colours.star : (s.warm ? colours.star : colours.cool)) + "," + alpha.toFixed(3) + ")";
        ctx.beginPath();
        ctx.arc(x, y, light ? s.r * .8 : s.r, 0, 6.283);
        ctx.fill();
        if (!light && s.depth > .85) { // the brightest get a soft glow
          ctx.fillStyle = "rgba(" + colours.cool + "," + (alpha * .12).toFixed(3) + ")";
          ctx.beginPath(); ctx.arc(x, y, s.r * 4, 0, 6.283); ctx.fill();
        }
      }
      if (!light && !reduceMotion) {
        if (!nextMeteor) nextMeteor = t + 3000;
        if (t > nextMeteor) spawnMeteor(t);
        for (var m = meteors.length - 1; m >= 0; m--) {
          var me = meteors[m], age = (t - me.born) / me.life;
          if (age >= 1) { meteors.splice(m, 1); continue; }
          var hx = me.x + me.vx * age * 60, hy = me.y + me.vy * age * 60;
          var grad = ctx.createLinearGradient(hx, hy, hx - me.vx * 14, hy - me.vy * 14);
          grad.addColorStop(0, "rgba(" + colours.star + "," + (1 - age).toFixed(2) + ")");
          grad.addColorStop(1, "rgba(" + colours.star + ",0)");
          ctx.strokeStyle = grad;
          ctx.lineWidth = 1.4;
          ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(hx - me.vx * 14, hy - me.vy * 14); ctx.stroke();
        }
      }
    }

    var running = false;
    function loop(t) {
      if (!running) return;
      draw(t, false);
      requestAnimationFrame(loop);
    }
    function setRunning(on) {
      if (reduceMotion) { draw(performance.now(), true); return; }
      if (on === running) return;
      running = on;
      if (on) requestAnimationFrame(loop);
    }

    readColours();
    resize();
    window.addEventListener("resize", function () { clearTimeout(resize.t); resize.t = setTimeout(resize, 150); });
    if (reduceMotion) window.addEventListener("scroll", function () { draw(performance.now(), true); }, { passive: true });
    document.addEventListener("visibilitychange", function () { setRunning(!document.hidden); });
    new MutationObserver(function () { readColours(); draw(performance.now(), true); })
      .observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    if (canHover && !reduceMotion) {
      window.addEventListener("mousemove", function (ev) {
        mouseX = ev.clientX / W - .5; mouseY = ev.clientY / H - .5;
      }, { passive: true });
    }
    setRunning(true);
  }

  // ------------------------------------------------------------ reveal on scroll

  // Stagger animated parts by their data-i index (CSSOM writes are allowed by the CSP).
  $$("svg [data-i]").forEach(function (el) { el.style.setProperty("--i", el.getAttribute("data-i")); });

  var revealTargets = $$(".reveal, .dg");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in-view"); io.unobserve(en.target); }
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
        navLinks.forEach(function (a) { a.classList.toggle("is-active", a.getAttribute("data-nav") === en.target.id); });
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
      var p = Math.min((t - start) / 1400, 1);
      el.textContent = String(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(step);
    }
    el.textContent = "0";
    requestAnimationFrame(step);
  }
  var figs = $$(".fig dd[data-count]");
  if ("IntersectionObserver" in window && figs.length) {
    var fio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { countUp(en.target); fio.unobserve(en.target); } });
    }, { threshold: 0.6 });
    figs.forEach(function (f) { fio.observe(f); });
  }

  // ------------------------------------------------------------ hero constellation

  var chart = $(".constellation");
  if (chart) {
    requestAnimationFrame(function () { chart.classList.add("in-view"); });
    var lines = $$(".cs-line", chart);
    $$(".cs-star", chart).forEach(function (star) {
      var id = star.getAttribute("data-id");
      var link = star.closest("a") || star;
      function on() {
        chart.classList.add("has-hl");
        star.classList.add("hl");
        lines.forEach(function (l) {
          l.classList.toggle("hl", l.getAttribute("data-a") === id || l.getAttribute("data-b") === id);
        });
      }
      function off() {
        chart.classList.remove("has-hl");
        star.classList.remove("hl");
        lines.forEach(function (l) { l.classList.remove("hl"); });
      }
      link.addEventListener("mouseenter", on);
      link.addEventListener("mouseleave", off);
      link.addEventListener("focus", on);
      link.addEventListener("blur", off);
    });
    var hero = $(".hero");
    if (hero && canHover && !reduceMotion) {
      hero.addEventListener("mousemove", function (ev) {
        var r = hero.getBoundingClientRect();
        var x = (ev.clientX - r.left) / r.width - .5, y = (ev.clientY - r.top) / r.height - .5;
        chart.style.transform = "translate(" + (x * -14).toFixed(1) + "px," + (y * -10).toFixed(1) + "px)";
      });
      hero.addEventListener("mouseleave", function () { chart.style.transform = ""; });
    }
  }

  // ------------------------------------------------------------ orrery (stack)

  var orrery = $(".orrery");
  if (orrery) {
    var planets = $$(".planet", orrery).map(function (p) {
      return {
        el: p, rx: +p.getAttribute("data-rx"), ry: +p.getAttribute("data-ry"),
        angle: +p.getAttribute("data-angle") * Math.PI / 180, period: +p.getAttribute("data-period")
      };
    });
    var spinning = false, prev = 0;
    function spin(t) {
      if (!spinning) return;
      var dt = prev ? Math.min(t - prev, 64) / 1000 : 0;
      prev = t;
      planets.forEach(function (p) {
        p.angle += dt * 2 * Math.PI / p.period;
        p.el.setAttribute("transform", "translate(" + (p.rx * Math.cos(p.angle)).toFixed(1) + " " + (p.ry * Math.sin(p.angle)).toFixed(1) + ")");
      });
      requestAnimationFrame(spin);
    }
    if (!reduceMotion && "IntersectionObserver" in window) {
      new IntersectionObserver(function (en) {
        spinning = en[0].isIntersecting;
        prev = 0;
        if (spinning) requestAnimationFrame(spin);
      }).observe(orrery);
    }
    // Hovering a layer lights its orbit, and the other way round.
    function light(layerId, on) {
      $$('[data-layer="' + layerId + '"]').forEach(function (el) { el.classList.toggle("hl", on); });
    }
    $$(".layer, .planet").forEach(function (el) {
      var id = el.getAttribute("data-layer");
      el.addEventListener("mouseenter", function () { light(id, true); });
      el.addEventListener("mouseleave", function () { light(id, false); });
    });
  }

  // ------------------------------------------------------------ celestial cursor readout (RA / Dec)

  var readout = $(".readout");
  if (readout && canHover) {
    var rx = $(".rx", readout), ry = $(".ry", readout), idle;
    var raLabel = root.lang === "en" ? "RA" : "AR";
    var two = function (n) { return ("0" + n).slice(-2); };
    window.addEventListener("mousemove", function (ev) {
      var ra = ev.clientX / window.innerWidth * 24;
      var dec = 90 - (ev.clientY + window.scrollY) / document.documentElement.scrollHeight * 180;
      var dAbs = Math.abs(dec);
      rx.textContent = raLabel + " " + two(Math.floor(ra)) + "h " + two(Math.floor(ra % 1 * 60)) + "m";
      ry.textContent = "Dec " + (dec < 0 ? "−" : "+") + two(Math.floor(dAbs)) + "° " + two(Math.floor(dAbs % 1 * 60)) + "′";
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

  // Show the most recent weeks of the contribution sky on narrow screens.
  $$(".heatmap-scroll").forEach(function (s) { s.scrollLeft = s.scrollWidth; });

  // ------------------------------------------------------------ email, assembled client-side

  $$(".js-mail").forEach(function (a) {
    var addr = a.getAttribute("data-u") + "@" + a.getAttribute("data-d");
    a.href = "mailto:" + addr;
    var text = $(".js-mail-text", a);
    if (text) text.textContent = addr;
  });
})();
