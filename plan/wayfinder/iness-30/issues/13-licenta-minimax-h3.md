# Putem folosi MiniMax H3 (local, pe pod) pentru postările lui Iness?

Type: grilling
Status: open
Blocked by: —

## Question

Primul reel al lui Iness (`H3_Character_Swap_00001_.mp4`) e făcut cu **MiniMax H3**, cu greutățile deschise rulate pe pod (Ref2VA + LoRA Character Swap). Licența greutăților e **MiniMax H3 Community License**. Ce spun sursele oficiale (verificat pe 23.10.2026):

- **UE, UK, Coreea de Sud și SUA sunt „teritorii restricționate”** pentru greutățile deschise. „Organizations in these regions can apply for a formal license”, prin https://platform.minimax.io/h3-license. Aprobarea nu e garantată.
  - Surse: https://huggingface.co/MiniMaxAI/MiniMax-H3 și https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/QA-about-License.md
- Ghidul comunitar „Awesome MiniMax-H3” spune la fel la mai multe modele derivate: „not licensed in the EU, UK, South Korea or the US without MiniMax's separate authorization”.

Omul e în România, iar contul e făcut pentru colaborări plătite. Alegem una dintre variante:
1. **Cerem licența** prin formular (ca MUSQAI) și până la aprobare nu publicăm nimic făcut cu H3.
2. **Trecem pe unelte cu licență clară în UE:**
   - Wan, cu LoRA-ul v2 existent (licență Apache-2.0, de verificat versiunea);
   - Kling, decis în [Ce unealtă video AI folosim pentru reels-urile lui Iness?](01-unealta-video.md);
   - API-ul oficial MiniMax/Hailuo (termenii API, nu licența greutăților).
3. **Ambele:** cerem licența, iar între timp producem cu 2.

**Textul complet din `LICENSE`, verificat pe 23.10.2026** (https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/main/LICENSE):
- Def. 3 și 5: „Applicable Territory” înseamnă „worldwide, excluding the Excluded Territories”. „Excluded Territories” sunt „the European Union, the United Kingdom, the Republic of Korea and the United States of America”.
- §II: dreptul de folosire se dă „**Solely within the Applicable Territory**”.
- §V.4: „You may not use, reproduce, modify, distribute, or display the MiniMax H3 Works **or any of their Outputs** or results outside the Applicable Territory.” Așadar și clipurile generate intră sub regulă, nu doar modelul.
- §IV.1: pragul de bani e de **20 de milioane USD venit anual**, nu de 1 milion. Peste prag îți trebuie aprobare scrisă. **Pragul se aplică doar în teritoriul permis**, deci nu ajută pe cineva din UE.
- AUP pct. 12: orice conținut public trebuie marcat „clearly and prominently” ca generat de mașină (bifat deja prin etichetele AI).
- La Pod-ul RunPod contează și unde e serverul: SUA e tot teritoriu exclus.
