# Inserting a shot into a finished edit

Use this when a new shot (a generated insert, a pickup, a B-roll replacement) goes into a video the creator has
already finished, especially when they say not to change anything else.

## The mistake this prevents

On the SNOOZZ ginger-shot reel the creator asked for a generated insert at the cap opening, the original audio, the
removed subtitles put back, and nothing else changed. To keep the audio in sync I overwrote frames 185–303 without
asking. That silently removed three shots: the lips drinking, the woman drinking in the café, and the start of the
presenter drinking. The creator caught it. A shot the creator put in the edit is part of what they asked to keep,
whether it is real footage or AI b-roll.

## Checklist

1. **Map before you cut.** List the cut points around the insert (frame-difference scan), the word timings of the
   speech (`transcribe.py`) and the frames each burned-in subtitle covers.
2. **Show the change as a shot list before rendering.** For each original shot, say whether it stays, moves, or is
   covered, with its timestamps. Covering or removing any shot needs the creator's explicit OK. "Nothing else changes"
   rules it out unless they agree to it.
3. **Default to a ripple insert.** Every original shot stays complete and in order, and the video gets longer by
   (insert length − replaced length). Overwrite only when the creator asks for it.
4. **Original audio under a ripple insert.** Keep the speech untouched and in sync with the picture after the insert.
   Fill the added seconds with the original's own music bed:
   - pick a splice point in a speech-free stretch, right after the last word before the insert;
   - repeat whole beats of the music from that stretch (at least half-bar multiples, bars if the arrangement changes);
   - cut on kick onsets with 5–10 ms crossfades.

   Never splice inside speech. Never use the generator's audio unless asked. Tell the creator what was repeated.
5. **Subtitles.** Burned-in subtitles on frames the insert covers must be put back as the original pixels at their
   original frames. Extract a layer by grey matting between a frame with the subtitle and its cleaned background,
   using several frames when a letter sits on a highlight. Do not re-typeset them.
6. **Export like the source.** Match the source's container, codec, profile and level, size, frame rate, bitrate class,
   GOP, colour tags, audio format and timecode. Stream-copy the audio when it is unchanged.
7. **QC against the shot list.** Every original shot is still there (count the cuts). Speech after the insert lines
   up with the lips. Subtitles are back on the right frames. Format matches.
