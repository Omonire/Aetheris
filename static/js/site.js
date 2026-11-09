// Aetheris — shared site interactions.
(function () {
  "use strict";

  var progress = document.getElementById("scroll-progress");
  var glow = document.getElementById("cursor-glow");
  var mockup = document.getElementById("hero-mockup");
  var parallaxLayers = document.querySelectorAll(".parallax-layer");
  var navToggle = document.getElementById("nav-toggle");
  var nav = document.querySelector(".site-nav");

  function onScroll() {
    if (!progress) return;
    var scrollTop = window.scrollY || document.documentElement.scrollTop;
    var height = document.documentElement.scrollHeight - window.innerHeight;
    var pct = height > 0 ? (scrollTop / height) * 100 : 0;
    progress.style.width = pct + "%";
  }

  function onMouseMove(event) {
    var x = event.clientX;
    var y = event.clientY;

    if (glow) {
      glow.style.left = x + "px";
      glow.style.top = y + "px";
    }

    if (mockup) {
      var rx = (window.innerHeight / 2 - y) / 40;
      var ry = (window.innerWidth / 2 - x) / 40;
      mockup.style.transform = "rotateX(" + rx + "deg) rotateY(" + ry + "deg)";
    }

    parallaxLayers.forEach(function (layer) {
      var speed = parseFloat(layer.dataset.speed) || 0.05;
      var mx = (x - window.innerWidth / 2) * speed;
      var my = (y - window.innerHeight / 2) * speed;
      layer.style.transform = "translate(" + mx + "px, " + my + "px)";
    });
  }

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!reduceMotion) {
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("mousemove", onMouseMove);
    onScroll();
  }

  // Scroll-triggered reveals.
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add("reveal-visible");
    });
  }

  // Mobile navigation.
  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Auto-dismiss flash messages.
  document.querySelectorAll(".flash").forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = "opacity .4s ease, transform .4s ease";
      flash.style.opacity = "0";
      flash.style.transform = "translateY(8px)";
      setTimeout(function () {
        flash.remove();
      }, 420);
    }, 4200);
  });
})();
