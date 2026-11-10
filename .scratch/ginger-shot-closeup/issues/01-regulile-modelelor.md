# Regulile modelelor pentru prompturi

Type: research
Status: resolved
Blocked by: —

## Question

Ce cere fiecare model ca promptul și rezultatul să iasă corect: Gemini Omni Flash 1.2 (image-to-video), Kling 4.0
(image-to-video), Seedance 2.5 (image-to-video) și modelul de imagine pentru cadrul de vârf (Nano Banana Pro edit, cu
o alternativă)? Schema exactă (cadru de pornire și final, durate, rezoluții, 9:16, fps, audio), ghidul oficial de prompt
(structură, lungime, vocabular de cameră și mișcare, cum ceri sunetul), ce resping regulile de utilizare și filtrele
(branduri, text pe produs, mâncare și băuturi), cum se comportă interpolarea spre cadrul final și ce costă modul draft
al Seedance 2.5.

## Answer

Detaliile și sursele sunt în [research/01-regulile-modelelor.md](../research/01-regulile-modelelor.md). Pe scurt:

- Toate trei modelele video primesc cadru de pornire și cadru final, iar 4 s merge la toate. Gemini cere
  `aspect_ratio: "9:16"` (implicit e 16:9) și are maximum 10 s cu cadru final. Kling și Seedance urmează raportul
  cadrului de intrare. Gemini și Seedance dau 24 fps.
- Gemini și Kling fac implicit mai multe planuri, așa că promptul cere „one continuous shot, no cuts”. Sunetul se cere
  doar din efecte, cu „no music” scris explicit.
- Cadrul de vârf trebuie să păstreze încadrarea și poziția sticlei din cadrul de pornire. Se schimbă doar lumina și
  particulele: Kling avertizează că schimbările mari simultane fac tranziția dificilă. Camera stă aproape fixă, ca
  eticheta să nu fie redesenată din alt unghi.
- Româna („ghimbir, lămâie, miere”) nu apare printre limbile în care modelele randează text. Promptul cere „keep the
  label exactly as in the first frame”, iar eticheta se verifică la fiecare take, cu refacere în post ca rezervă.
- Seedance 2.5 respinge fețele reale din cadre. Îi setăm `duration: "4"` (string) și `codec: "H264"`, fiindcă 1080p
  vine implicit pe 10 biți H.265. Draftul la 480p se completează doar la 1080p și costă cât un 1080p direct (total
  ≈ $5.4–5.5 pentru 4 s). Promptul nu se mai schimbă după draft.
- API-ul Kling 4.0 pe fal apărea „coming soon” pe 21 octombrie și 4 noiembrie. Azi e neconfirmat.
- Cadrul de vârf: Nano Banana Pro costă $0.15 și dă 1536×2752 la 9:16 (trebuie decupat). Seedream 5.0 Pro dă exact
  1080×1920 pentru $0.0675.
