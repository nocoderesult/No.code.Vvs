# Daria — setul de antrenare v2 (34 de poze)

Structură: **12 față + 10 studio (corp) + 12 insta (poze de telefon)**.
Același set îl folosim pentru LoRA-ul de poze (Krea 2) și pentru LoRA-ul video (Wan).

## Pasul 0 — referințe curate (fără tatuaj)
Pozele de referință vechi au tatuajul pe încheietură. Înainte de orice, în Nano Banana:
1. Urci `daria_ref.png` (fața) → scrii: `Remove the tattoo from her wrist. Keep everything else exactly identical.` → salvezi ca **ref_fata.png**
2. Urci `front_00002_.png` (corpul din față) → aceeași instrucțiune → salvezi ca **ref_corp.png**

De aici încolo folosești DOAR `ref_fata.png` și `ref_corp.png`.

## Cum generezi
- **Nano Banana**, format **3:4 vertical**, PNG.
- **Pozele 01–12 (față):** urci `ref_fata.png`.
- **Pozele 13–34 (corp + insta):** urci `ref_fata.png` + `ref_corp.png`.
- La fiecare ~5 poze începi un chat nou și reurci referințele (altfel fața „alunecă”).
- Fiecare prompt = **ÎNCEPUT** + textul din tabel + **SFÂRȘIT**.
- Salvezi cu numele exact din tabel (ex. `daria_v2_01.png`).

**ÎNCEPUT** (copiezi la fiecare poză):
```
Use the reference images. Keep the exact same woman: same face, same jet-black jaw-length bob with a side part, same green-hazel eyes, same warm tan skin, same athletic hourglass figure. She is 25 years old. No tattoos anywhere on her body.
```

**SFÂRȘIT** (copiezi la fiecare poză):
```
Real smartphone photo, natural skin texture, not airbrushed, realistic light. 3:4 vertical. No text, no watermark.
```

## Verificare (fiecare poză, înainte s-o păstrezi)
- [ ] fața seamănă 100% cu ref_fata (ochi verde-alune, cărare laterală, bob la maxilar)
- [ ] fără tatuaj, fără alunițe/semne noi pe gât
- [ ] mâini corecte (5 degete), unghii nude-roz migdală
- [ ] fără text, logo, steluța Gemini în colț
- [ ] dacă ai dubii → o refaci. **Mai bine 28 perfecte decât 34 cu greșeli.**

---

## A. FAȚA — 12 poze (fundal gri de studio)

| Fișier | Text pentru mijlocul promptului |
|---|---|
| daria_v2_01.png | Close-up head and shoulders portrait, facing the camera straight on, neutral relaxed expression, plain black tank top, plain medium-grey seamless studio background, soft even studio light. |
| daria_v2_02.png | Close-up head and shoulders portrait, facing the camera, soft closed-mouth smile, plain black tank top, plain medium-grey studio background, soft studio light. |
| daria_v2_03.png | Close-up portrait, head turned three-quarters to her left, neutral expression, plain black tank top, plain grey studio background, soft studio light. |
| daria_v2_04.png | Close-up portrait, head turned three-quarters to her right, laughing naturally with teeth showing, eyes slightly squinted, plain black tank top, plain grey studio background. |
| daria_v2_05.png | Close-up portrait, full side profile facing left, hair tucked behind her ear, neutral expression, plain black tank top, plain grey studio background. |
| daria_v2_06.png | Close-up portrait, full side profile facing right, calm expression, plain black tank top, plain grey studio background. |
| daria_v2_07.png | Close-up portrait shot from slightly above, she looks up into the camera, gentle expression, plain black tank top, plain grey studio background. |
| daria_v2_08.png | Close-up portrait shot from slightly below, chin slightly raised, confident expression, plain black tank top, plain grey studio background. |
| daria_v2_09.png | Close-up portrait from behind, she looks back over her shoulder at the camera, slight smile, plain black tank top, plain grey studio background. |
| daria_v2_10.png | Close-up portrait, eyes looking down, shy smile, plain black tank top, plain grey studio background, soft light. |
| daria_v2_11.png | Close-up portrait, facing the camera but looking off to the side, thoughtful expression, plain black tank top, plain grey studio background. |
| daria_v2_12.png | Extreme close-up of her face from forehead to chin, looking into the camera, serious expression, very detailed eyes and natural skin, plain grey background. |

## B. STUDIO — 10 poze (corpul, fundal simplu)

| Fișier | Text pentru mijlocul promptului |
|---|---|
| daria_v2_13.png | Full body standing, facing the camera, arms relaxed, fitted black sports bra and black high-waisted leggings, barefoot, plain light-grey studio, soft even light. |
| daria_v2_14.png | Full body standing, three-quarter view, one hand on her hip, fitted black sports bra and black high-waisted leggings, barefoot, plain light-grey studio. |
| daria_v2_15.png | Full body standing, full side profile, fitted black sports bra and black high-waisted leggings, barefoot, plain light-grey studio. |
| daria_v2_16.png | Full body standing, seen from behind, head slightly turned to the side, fitted black sports bra and black high-waisted leggings, barefoot, plain light-grey studio. |
| daria_v2_17.png | Full body standing, facing the camera, white fitted tank top and light-blue straight jeans, white sneakers, plain light-grey studio. |
| daria_v2_18.png | Full body, walking toward the camera, three-quarter view, white fitted tank top and light-blue jeans, white sneakers, plain light-grey studio. |
| daria_v2_19.png | Full body standing, facing the camera, champagne satin midi slip dress, barefoot, plain light-grey studio, soft light. |
| daria_v2_20.png | Full body seen from behind, looking back over her shoulder, champagne satin midi slip dress, plain light-grey studio. |
| daria_v2_21.png | Full body standing, three-quarter view, classic black one-piece swimsuit, plain light-grey studio, soft light. |
| daria_v2_22.png | Medium shot, sitting on a simple wooden stool, beige blazer over a white tee and blue jeans, plain light-grey studio. |

## C. INSTA — 12 poze (aspect de telefon, lumină reală)

| Fișier | Text pentru mijlocul promptului |
|---|---|
| daria_v2_23.png | Mirror selfie in her bedroom in the evening, warm bedside lamp light, oversized cream knit sweater, phone covering part of her chin, unmade bed behind her. |
| daria_v2_24.png | Bathroom mirror selfie with the phone flash on, harsh flash light, white t-shirt, toiletries on the counter, slightly messy. |
| daria_v2_25.png | Photo taken by a friend across a cafe table, morning window light, she holds a latte and laughs, beige cardigan, other people blurred in the background. |
| daria_v2_26.png | Selfie in the driver's seat of a parked car, daylight through the windshield, sunglasses pushed up on her head, white shirt, seatbelt visible. |
| daria_v2_27.png | On a balcony at golden hour, loose white linen shirt, warm low sun on her face, city rooftops behind her slightly out of focus. |
| daria_v2_28.png | Gym mirror selfie, fitted grey athletic set, gym machines and other people in the background, fluorescent light. |
| daria_v2_29.png | Candid street photo, walking on a city sidewalk on an overcast day, beige trench coat, people and parked cars blurred behind her. |
| daria_v2_30.png | At a restaurant table at night, photo taken with flash, little black dress, glass of red wine, dark busy background, slight grain. |
| daria_v2_31.png | On the beach at sunset, open white linen shirt over a black one-piece swimsuit, wind in her hair, warm backlight. |
| daria_v2_32.png | Morning in her kitchen, silk pajama set, holding a mug of coffee, dishes and plants in the background, soft window light. |
| daria_v2_33.png | Standing by a hotel room window in the morning, white hotel robe, backlit by daylight, slightly overexposed window, unmade bed behind her. |
| daria_v2_34.png | At a crowded rooftop bar at night, black satin top, mixed warm and neon light, city lights bokeh, slight motion blur and phone noise. |
