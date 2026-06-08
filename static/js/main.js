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

// Gallery carousel (photos + video mixed)
(function () {
  const items = [
    { type: "image", src: "/static/images/photo1.jpg" },
    { type: "image", src: "/static/images/photo2.jpg" },
    { type: "image", src: "/static/images/photo3.jpg" },
    { type: "image", src: "/static/images/photo4.jpg" },
    { type: "image", src: "/static/images/photo5.jpg" },
    { type: "video", src: "/static/images/couple.mp4" },
  ];
  const total = items.length;
  let current = 0;
  let timer;

  const carousel = document.getElementById("gallery");
  const dotsEl   = document.getElementById("gallery-dots");
  if (!carousel) return;

  const slides = carousel.querySelectorAll(".gallery__slide");
  const dots   = dotsEl ? dotsEl.querySelectorAll(".gallery__dot") : [];

  function idx(i) { return ((i % total) + total) % total; }

  // Создаём контент слайда
  function buildContent(item, isActive) {
    if (item.type === "video") {
      const vid = document.createElement("video");
      vid.muted = !isActive;          // активный — со звуком
      vid.playsinline = true;
      vid.preload = "metadata";
      vid.style.width = "100%";
      vid.style.height = "100%";
      vid.style.objectFit = "cover";
      const src = document.createElement("source");
      src.src = item.src;
      src.type = "video/mp4";
      vid.appendChild(src);
      return vid;
    } else {
      const img = document.createElement("img");
      img.src = item.src;
      img.alt = "";
      img.style.width = "100%";
      img.style.height = "100%";
      img.style.objectFit = "cover";
      return img;
    }
  }

  // Остановить все видео в карусели
  function stopAllVideos() {
    carousel.querySelectorAll("video").forEach((v) => { v.pause(); v.currentTime = 0; });
  }

  function render(cur) {
    stopAllVideos();
    clearInterval(timer);

    const prevIdx = idx(cur - 1);
    const nextIdx = idx(cur + 1);

    slides[0].className = "gallery__slide gallery__slide--prev";
    slides[1].className = "gallery__slide gallery__slide--active";
    slides[2].className = "gallery__slide gallery__slide--next";

    slides[0].innerHTML = "";
    slides[1].innerHTML = "";
    slides[2].innerHTML = "";

    slides[0].appendChild(buildContent(items[prevIdx], false));
    slides[2].appendChild(buildContent(items[nextIdx], false));

    const activeContent = buildContent(items[cur], true);
    slides[1].appendChild(activeContent);

    dots.forEach((d, i) => d.classList.toggle("gallery__dot--active", i === cur));

    // Если активный слайд — видео: воспроизводим, после окончания идём дальше
    if (items[cur].type === "video") {
      activeContent.play().catch(() => {});
      activeContent.addEventListener("ended", () => {
        current = idx(current + 1);
        render(current);
      }, { once: true });
    } else {
      startTimer();
    }
  }

  function goNext() { current = idx(current + 1); render(current); }
  function goPrev() { current = idx(current - 1); render(current); }

  function startTimer() {
    clearInterval(timer);
    timer = setInterval(goNext, 5000);
  }

  dots.forEach((d, i) => {
    d.addEventListener("click", () => { current = i; render(current); });
  });

  let touchStartX = 0;
  carousel.addEventListener("touchstart", (e) => { touchStartX = e.touches[0].clientX; }, { passive: true });
  carousel.addEventListener("touchend", (e) => {
    const diff = touchStartX - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 40) { diff > 0 ? goNext() : goPrev(); }
  });

  slides[0].addEventListener("click", goPrev);
  slides[2].addEventListener("click", goNext);

  render(current);
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