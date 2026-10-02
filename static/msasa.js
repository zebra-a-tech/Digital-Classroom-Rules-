/* Msasa — small progressive-enhancement helpers.
   No framework. No CDN. Everything fails gracefully. */
(function () {
  "use strict";

  // ---- toast ----
  var host = null;
  function toastHost() {
    if (host) return host;
    host = document.createElement("div");
    host.className = "ms-toast-host";
    document.body.appendChild(host);
    return host;
  }
  function toast(msg, ms) {
    var h = toastHost();
    var el = document.createElement("div");
    el.className = "ms-toast";
    el.textContent = msg;
    h.appendChild(el);
    requestAnimationFrame(function () { el.classList.add("is-on"); });
    setTimeout(function () {
      el.classList.remove("is-on");
      setTimeout(function () { el.remove(); }, 250);
    }, ms || 2400);
  }
  window.msToast = toast;

  // ---- timer widget (server-authoritative; this only reflects it) ----
  function initTimers() {
    document.querySelectorAll("[data-ms-timer]").forEach(function (node) {
      var expiresAt = node.getAttribute("data-expires-at");
      var paused    = node.getAttribute("data-paused") === "1";
      var valueEl   = node.querySelector(".ms-timer__value");
      if (!valueEl || !expiresAt) return;

      var end = new Date(expiresAt).getTime();
      function tick() {
        var now = Date.now();
        var remain = Math.max(0, Math.floor((end - now) / 1000));
        var m = String(Math.floor(remain / 60)).padStart(2, "0");
        var s = String(remain % 60).padStart(2, "0");
        valueEl.textContent = paused ? "paused" : (m + ":" + s);
        if (!paused) {
          node.classList.toggle("ms-timer--warn", remain <= 60 && remain > 0);
          node.classList.toggle("ms-timer--paused", false);
        } else {
          node.classList.add("ms-timer--paused");
        }
        if (remain <= 0 && !paused) {
          valueEl.textContent = "expired";
          node.classList.add("ms-timer--warn");
          return;
        }
        requestAnimationFrame(function () { setTimeout(tick, 1000); });
      }
      tick();
    });
  }

  // ---- progress rings ----
  function initRings() {
    document.querySelectorAll(".ms-ring").forEach(function (node) {
      var pct = parseFloat(node.getAttribute("data-pct") || "0");
      pct = Math.max(0, Math.min(100, pct));
      var r = 36, c = 2 * Math.PI * r;
      var offset = c * (1 - pct / 100);
      var svg = node.querySelector("svg");
      if (!svg) return;
      var val = svg.querySelector(".ms-ring__value");
      if (val) val.style.strokeDashoffset = offset;
      var label = node.querySelector(".ms-ring__label");
      if (label) label.textContent = Math.round(pct) + "%";
    });
  }

  // ---- bar fills ----
  function initBars() {
    document.querySelectorAll(".ms-bar[data-pct]").forEach(function (node) {
      var pct = Math.max(0, Math.min(100, parseFloat(node.getAttribute("data-pct") || "0")));
      var fill = node.querySelector(".ms-bar__fill");
      if (fill) fill.style.width = pct + "%";
      node.classList.toggle("ms-bar--clay", pct < 60);
      node.classList.toggle("ms-bar--sun", pct >= 60 && pct < 80);
    });
  }

  // ---- confirm before POST (used by pause/finish buttons) ----
  function initConfirms() {
    document.querySelectorAll("form[data-ms-confirm]").forEach(function (f) {
      f.addEventListener("submit", function (e) {
        var msg = f.getAttribute("data-ms-confirm") || "Are you sure?";
        if (!window.confirm(msg)) e.preventDefault();
      });
    });
  }

  function boot() {
    initTimers();
    initRings();
    initBars();
    initConfirms();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
