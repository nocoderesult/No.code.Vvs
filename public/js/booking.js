// Link-ul de programare: platforma salonului (Booksy, MERO...) sau WhatsApp cu mesaj precompletat.
import { site } from './config.js';

export function whatsappLink(what) {
  const msg = what ? `Salut! Aș vrea o programare pentru: ${what}.` : 'Salut! Aș vrea o programare.';
  return `https://wa.me/${site.whatsapp}?text=${encodeURIComponent(msg)}`;
}

export function bookingLink(what) {
  return site.bookingUrl || whatsappLink(what);
}
