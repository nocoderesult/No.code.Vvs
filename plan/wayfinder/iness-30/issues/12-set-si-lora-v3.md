# Refacem setul de antrenare și LoRA-ul lui Iness după metoda Mickmumpitz

Type: task
Status: resolved
Blocked by: 05

## Question

Setul v2 trebuie refăcut după poza oficială (vezi [Aliniem fișa lui Iness la poza oficială](05-look-oficial.md)). Îl facem automat pe pod, cu metoda din videoclipul Mickmumpitz „Create HYPERREALISTIC AI Characters That INTERACT” (https://youtu.be/ghFYDG0DF1w, 17.07.2026):

1. **Licențe, înainte de orice download:** Flux 2 Klein (varianta 4B sau 9B), Krea 2 și Qwen3-VL trebuie să permită uz comercial pentru conținutul unui cont.
2. **Setul:** workflow-ul gratuit „Character Creator” (Flux 2 Klein) pornește de la poza oficială, în modul preview.
   - Adăugăm grupuri de prim-plan pentru detaliile care alunecă: cerceii rotunzi argintii, pistruii, cărarea pe mijloc.
   - Facem cadre variate: aproape și departe, lumini diferite, ținute de lifestyle și costum de baie, în limitele din [Cum arată și sună contul @ines.s.official?](06-identitatea-contului.md).
3. **Captionurile:** „Dataset Tagger” (Qwen3-VL) scrie captionuri lungi, în stilul Krea 2, cu cuvântul `d4ria`, fără să descrie fața (ca să rămână legată de cuvânt), dar cu hainele descrise (ca să le putem schimba).
4. **LoRA:** AI Toolkit, Krea 2 RAW, eșantioane la fiecare 250 de pași, până la 3000. Comparăm checkpoint-urile între 1250 și 2500 cu poza oficială.
5. **Opțional:** LoRA Wan 2.1/2.2 pe același set, pentru clipurile fără vorbit (mai ieftin decât creditele Kling).

Ce nu rezolvă: vocea în română și lip-sync-ul rămân pe ElevenLabs + Kling, după [Ce unealtă video AI folosim pentru reels-urile lui Iness?](01-unealta-video.md).

Gata când avem setul v3 aprobat de om, LoRA-ul ales (checkpoint-ul) și 3 poze de test care trec checklistul din `personaj/CARACTER.md`. Agentul de pe pod nu șterge nimic fără să întrebe și cere voie pentru download-uri peste 2 GB. LoRA-urile existente nu se ating.

## Answer

**Nu e nevoie.** Omul are deja **LoRA v2** (`d4ria`) pentru **Krea 2** (poze) și pentru **Wan** (video). Poza oficială e chiar din LoRA v2, iar look-ul oficial iese stabil: cărare pe mijloc, cercei argintii, pistrui. Nu refacem setul și nu antrenăm din nou.

Din metoda Mickmumpitz rămân utile, dacă vreodată facem un v3:
- descrieri lungi, în stilul Krea 2;
- prim-planuri pe detaliile care alunecă;
- alegerea checkpoint-ului între pașii 1250 și 2000, nu ultimul.

Clipurile fără vorbit se pot face cu LoRA-ul Wan existent.
