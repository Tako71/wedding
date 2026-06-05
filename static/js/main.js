// Preloader
(function () {
  const preloader = document.getElementById("preloader");
  if (!preloader) return;

  function hide() {
    preloader.classList.add("hidden");
  }

  if (document.readyState === "complete") {
    setTimeout(hide, 400);
  } else {
    window.addEventListener("load", function () {
      setTimeout(hide, 400);
    });
    // Страховка — скрыть через 3 сек в любом случае
    setTimeout(hide, 3000);
  }
})();

// Countdown timer
(function () {
  const target = new Date(WEDDING_DATE);

  function pad(n) { return String(n).padStart(2, "0"); }

  function tick() {
    const now = new Date();
    const diff = target - now;

    if (diff <= 0) {
      document.getElementById("cd-days").textContent    = "00";
      document.getElementById("cd-hours").textContent   = "00";
      document.getElementById("cd-minutes").textContent = "00";
      document.getElementById("cd-seconds").textContent = "00";
      return;
    }

    const days    = Math.floor(diff / 86400000);
    const hours   = Math.floor((diff % 86400000) / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);

    document.getElementById("cd-days").textContent    = pad(days);
    document.getElementById("cd-hours").textContent   = pad(hours);
    document.getElementById("cd-minutes").textContent = pad(minutes);
    document.getElementById("cd-seconds").textContent = pad(seconds);
  }

  tick();
  setInterval(tick, 1000);
})();

// Scroll reveal
(function () {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("visible");
          observer.unobserve(e.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
})();