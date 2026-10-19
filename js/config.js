// Datele barbershop-ului. Tot ce e specific salonului se schimbă de aici
// (textele mari din pagină sunt direct în index.html).
export const site = {
  brand: 'The Barber Experience',
  phone: '+40 700 000 000',
  // WhatsApp în format internațional, doar cifre (fără +, spații sau 0 în față)
  whatsapp: '40700000000',
  // Link de programare online (Booksy, MERO, Fresha...). Gol = programările merg pe WhatsApp.
  bookingUrl: '',
  instagram: 'https://instagram.com/',
  // Endpoint-ul care trimite selfie-ul la AI (vezi functions/api/tryon.js)
  tryOnEndpoint: '/api/tryon',
};
