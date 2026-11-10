# Cadrul de pornire curat

Type: task
Status: resolved
Blocked by: 03, 04

## Question

Care e cadrul de pornire, fără subtitrare, din care pornește insertul? Candidatul e cadrul 193 din montaj (8,042 s):
capacul a ieșit din gât, mâna îl duce în dreapta sus, camera reală s-a retras deja, iar eticheta se vede întreagă. Peste
lichid, deasupra etichetei, stă subtitrarea „gust pe care nu”. Ea se scoate cu Nano Banana Pro, după ce ești de acord
cu generarea, iar în cadrul real se pune înapoi doar zona ei.

## Answer

Ai cerut ambele cadre. Am curățat cadrul 188 (7,833 s: capacul tocmai iese din gât) și cadrul 193 (8,042 s: eticheta
se vede întreagă).

- Nano Banana Pro edit a scos subtitrarea „gust pe care nu”, cu conturul și umbra ei, la 2K. Au fost două joburi,
  $0,30 în total, cu request id-urile `01a1c5b2-5e8a-75a1-a6ed-32b5fbad9037` (193) și
  `01a1c5b2-d91b-73f2-8824-923ce5d78282` (188).
- Rezultatul AI a fost aliniat la cadrul real cu o transformare afină (ECC 0,9998; modelul întinsese imaginea pe
  orizontală cu 0,8%). Din el a intrat în cadrul real doar zona în care diferă de original, adică subtitrarea și umbra
  ei. Restul cadrului e pixel cu pixel cel filmat.
- Fișierele sunt `start_f188_clean.png` și `start_f193_clean.png` (1080×1920, PNG), în folderul de lucru al sesiunii.
  Nu le punem în repo.
