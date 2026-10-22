# Aliniem fișa lui Iness la poza oficială

Type: task
Status: resolved
Blocked by: —

## Question

Look-ul oficial e cel din poză: cărare pe mijloc, cercei argintii, pistrui. Fișierele vechi spun încă „cărare laterală, cercei cu diamant”. Ce se schimbă:
- `personaj/CARACTER.md`;
- `personaj/04_dataset_v2.md` și `personaj/04_captions_v2.txt`;
- celelalte prompturi din `personaj/`.

Agentul de pe pod primește mesajul pentru `DARIA_CONTEXT.md`. Gata când niciun fișier nu mai descrie look-ul vechi.

## Answer

Am aliniat fișierele la poza oficială (`musqai/web/static/assets/img/iness-960.jpg`): bob drept negru-corb puțin sub maxilar, **cărare pe mijloc**, ochi verde-alune deschiși, **pistrui fini**, **cercei rotunzi subțiri argintii** și un mic cercel argintiu sus pe ureche.

Ce am schimbat:
- `personaj/CARACTER.md`:
  - descrierea fixă și checklistul;
  - poza declarată ca referință oficială („când textul și poza nu se potrivesc, are dreptate poza”);
  - conținutul și conturile, după hartă;
  - bio-ul și eticheta AI, după [Ce trebuie bifat ca Iness să fie etichetată corect ca AI?](02-eticheta-ai.md).
- `personaj/02_dataset_edit.txt`, `personaj/02b_corp_referinta.txt`, `personaj/04_dataset_v2.md`: prefixul de prompt și checklistul de verificare.

Ce nu am schimbat:
- `personaj/04_captions_v2.txt`: captionurile LoRA nu descriu look-ul (îl învață cuvântul `d4ria`).
- Site-ul: era deja după poză.
- Numele tehnice (`d4ria`, `daria_v2_*.png`, `DARIA_CONTEXT.md`) rămân.

**De știut:** ~~pozele v2 vechi se refac~~ Corectat pe 22.10: LoRA v2 e deja antrenat și dă look-ul oficial stabil (poza oficială e din el), deci nu refacem nimic. Prompturile actualizate contează doar pentru seturi viitoare.

**Mesaj pentru agentul de pe pod** (de lipit în chat-ul lui):

```
Update /workspace/persist/DARIA_CONTEXT.md — add a section "Official look (decided 21 Oct 2026)":
- The official reference is the Iness photo (center part). Old descriptions with "side part" and "diamond stud earrings" are obsolete.
- Look: sleek straight jet-black blunt bob just below the jawline, CENTER part, light green-hazel eyes, fine light freckles on nose and cheeks, thin silver hoop earrings + tiny silver stud in the upper ear, warm tan skin, no tattoos.
- Dataset v2 prompts in the repo (personaj/04_dataset_v2.md, 02_dataset_edit.txt) are updated for any future dataset. LoRA v2 (Krea 2 + Wan) already produces the official look — keep using it, nothing to retrain.
- Do not delete any files without asking me first.
```
