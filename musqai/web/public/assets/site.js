/* MUSQAI: meniul pe telefon, mesajele scurte și copierea. */
(() => {
  "use strict";
  const btn = document.getElementById("menu-btn");
  const nav = document.getElementById("nav");
  const close = () => { nav.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); };
  if (btn && nav) {
    btn.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && nav.classList.contains("open")) { close(); btn.focus(); } });
    nav.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
  }

  let timer = 0;
  window.MQtoast = (msg) => {
    const el = document.getElementById("toast");
    if (!el) return;
    el.textContent = msg;
    el.hidden = false;
    clearTimeout(timer);
    timer = setTimeout(() => { el.hidden = true; }, 2600);
  };

  window.MQcopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      window.MQtoast("Copiat.");
    } catch (_) {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      let ok = false;
      try { ok = document.execCommand("copy"); } catch (_) { ok = false; }
      ta.remove();
      window.MQtoast(ok ? "Copiat." : "Selectează textul și copiază-l.");
    }
  };

  document.addEventListener("click", (e) => {
    const b = e.target.closest("[data-copy-text]");
    if (b) window.MQcopy(b.getAttribute("data-copy-text"));
  });
})();
