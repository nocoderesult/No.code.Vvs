# JURNAL: decizii, progres, pasul următor

*Se adaugă la final de fiecare sesiune: data, ce am decis, ce s-a făcut, pasul următor. Cel mai nou e sus.*

---

## 2026-10-20 (noaptea)

**Decizii:**
- **Daria se numește acum Iness.** Numele tehnice rămân la fel: cuvântul LoRA `d4ria`, fișierele `daria_v2_*.png`, `DARIA_CONTEXT.md` de pe pod.
- Poza oficială a lui Iness e cea trimisă azi: bob negru drept cu **cărare pe mijloc**, ochi verde-alune, pistrui fini, **cercei rotunzi argintii**.
- Site-ul public e construit din nou, în `musqai/web/`: pagini separate, design nou, Iness cu poza ei și 5 zone de generare care funcționează pe Cloudflare (Workers AI).

**De decis:** fișa (`personaj/CARACTER.md`) și setul v2 spun încă „cărare laterală” și „cercei mici cu diamant”. Le aliniem după poză înainte de luni?

---

## 2026-10-20 (seara)

**Decizii:**
- Numele: **MUSQAI**, adică **Marketing Universe Studio · Quantum AI**. „Quantum” e doar în nume; nu promitem calcul cuantic.
- Caracterele casei au nume: **Daria** (lifestyle și lux), **Matei** (business și imobiliare), **Ilinca** (travel și food), **Ioana** (produse de zi cu zi), **Mira** (fața platformei). Fișele complete sunt în `musqai/site/data.js`.
- Planul începe **luni, 26 octombrie 2026** și are 12 săptămâni, zi cu zi și oră cu oră, în modurile de 2, 4 sau 8 ore.

**Ce s-a făcut:**
- Planul interactiv: https://claude.ai/artifact/PxsV2fLh32QkoKwrvYGqW2 (fișierele în `musqai/plan/`).
- Site-ul MUSQAI, prototip pe mai multe pagini, cu Studio demo (Content Brain și Image → Prompt merg live): https://claude.ai/artifact/Pfw75NmdRWfk1g54VUmsi1 (fișierele în `musqai/site/`).

**Pasul următor:** săptămâna 0 din plan: domeniul musqai.com, numele @musqai, contul Dariei, cele 6 întrebări, volumul RunPod.

---

## 2026-10-20

**Decizii:**
- Construim un **studio**, apoi o **platformă**, de marketing cu caractere AI. Planul complet e în `plan/PLAN_COMPLET.md`.
- **Nișele le testăm pe rând**, cu același protocol (§5.1). Ordinea propusă: magazine online → imobiliare → turism și HoReCa → evenimente → wellness și cosmetice (doar cu reguli stricte).
- **Saloanele sunt pe pauză.** Nu folosim numele niciunui salon anume.
- **5 caractere ale casei.** Începem cu **Daria**: 25 de ani, fictivă, sexy dar elegantă, **fără tatuaj**, etichetată AI.
- **Video:** SCAIL-2 e modelul principal pentru înlocuire. **MiniMax H3 și Qwen rămân pe volum.**
- **Oferta** urmează `skills/money-model`, `skills/sales-call` și `skills/abonament-retentie`.

**Stare:**
- LoRA v1 Daria e gata (checkpoint 2500). Există și un v3, făcut de tine.
- Planul pentru setul de antrenare v2 e gata (`personaj/04_dataset_v2.md`).
- Volumul RunPod e aproape plin. Soluția propusă: mărirea la ~350 GB.
- SCAIL-2 nu e instalat complet. Testul de înlocuire (filmarea ta → Daria) așteaptă.
- Agentul de pe pod nu a pornit la ultima încercare. Îl depanăm cu logul de pornire.

**Pasul următor (săptămâna 1):**
- **Tu:** setul v2 pentru Daria, conturile IG și TikTok, 9 postări gata.
- **Eu:** fișa detaliată pentru N1, criteriile firmelor-țintă, mesajele, planul celor 5 mostre.

**Întrebări deschise:** vezi §17 din plan.
