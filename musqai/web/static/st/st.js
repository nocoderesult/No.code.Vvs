/* S&T Advertising: sunetul teaserului și cercul roșu din manifest. Pagina arată complet și fără acest fișier. */
(function () {
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var video = document.getElementById("teaser");
  var button = document.getElementById("sound");

  function play() {
    var p = video.play();
    if (p && p.catch) p.catch(function () {});
  }
  function setSound(on) {
    video.muted = !on;
    button.setAttribute("aria-pressed", on ? "true" : "false");
    button.classList.toggle("on", on);
    button.querySelector(".sound-label").textContent = on ? "Oprește sunetul" : "Pornește sunetul";
  }

  if (video && button) {
    if (reduce) { video.removeAttribute("autoplay"); video.pause(); }
    button.addEventListener("click", function () {
      var turnOn = video.muted;
      if (turnOn) { try { video.currentTime = 0; } catch (e) {} }
      setSound(turnOn);
      play();
    });
    document.querySelectorAll("[data-play-sound]").forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        document.getElementById("top").scrollIntoView({ behavior: reduce ? "auto" : "smooth" });
        try { video.currentTime = 0; } catch (err) {}
        setSound(true);
        play();
      });
    });
  }

  /* Cercul roșu se desenează când manifestul intră în ecran. */
  var circled = document.querySelector(".circled");
  if (circled && !reduce && "IntersectionObserver" in window) {
    circled.classList.add("pending");
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        circled.classList.add("drawn");
        circled.classList.remove("pending");
        io.disconnect();
      });
    }, { threshold: 0.6 });
    io.observe(circled);
  }
})();
