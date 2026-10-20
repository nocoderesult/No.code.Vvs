/* Formularul de contact: deschide aplicația de email a vizitatorului, cu cererea completată. */
(() => {
  "use strict";
  const form = document.getElementById("contact-form");
  if (!form) return;
  const TO = "contact@musqai.com";
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const f = form.elements;
    const name = f.name.value.trim();
    if (!name) {
      f.name.focus();
      window.MQtoast && window.MQtoast("Scrie-ți numele, ca să știm cui răspundem.");
      return;
    }
    const company = f.company.value.trim();
    const body = [
      `Nume: ${name}`,
      `Firma: ${company}`,
      `Site sau Instagram: ${f.link.value.trim()}`,
      `Nișa: ${f.niche.value}`,
      `Mă interesează: ${f.want.value}`,
      "",
      f.msg.value.trim()
    ].join("\n");
    const subject = "Cerere mostră" + (company ? ": " + company : "");
    window.location.href = `mailto:${TO}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    document.getElementById("contact-box").innerHTML =
      `<div class="stack" style="gap:16px"><span class="chip hot">Emailul e pregătit</span>` +
      `<h2 class="h2" style="font-size:clamp(30px,3.6vw,44px)">Mulțumim, ${esc(name.split(" ")[0])}.</h2>` +
      `<p class="lead">Ți-am deschis aplicația de email cu cererea completată. Apasă „Trimite” acolo. Dacă nu s-a deschis, scrie-ne direct la <b>${TO}</b>.</p>` +
      `<div class="btn-row"><a class="btn btn-ghost" href="/">Înapoi la prima pagină</a></div></div>`;
  });
})();
