# Map: DJ reel V4 (wayfinder, local markdown)

## Destination

A ~17 s vertical reel on the creator's own track: the real white-room take and the AI worlds intercut on the beat,
simulated camera angles in both, one opening question in the V2 type, ending on a real | AI comparison slider.

## Notes

Skills: taste (one accent per frame, cut on the music), remotion-video-creation + the official Remotion rules
(editable timeline, local fonts, effects), video-editor (punch-in limits, QC). The V3 brief rules still hold.

## Decisions so far

- Combine real + AI: intercut real inserts between AI worlds **and** simulated angles (punch-ins, close-ups) in both.
- Angle cadence: calm in the break; the lift is one locked shot; after the drop a change every ~2 beats.
- V3 rules kept: direct white -> fire cut (no flash), only the track during the lift, no extra impact on the drop,
  the song not processed (static gain; a peak limiter only touches the main drop's loudest transients).
- Ending (first cut): split screen, reality slides in from the left on the main drop (beat 28), rails on the right,
  decks aligned.
- Ending (after review): the creator heard the 8-bar cut as the song being swapped at the slide (the main drop has
  new chords and ~9 dB more) and asked to let the track run on, and for the slide to look like a slider "you can
  drag", fluid. Now: the track runs to the main drop's first accent (beat 36, a fill on 35-and leads into it) plus the
  note's tail, 17.4 s. The divider is a comparison slider pulled by a finger (`Slider.tsx`): each drag is a spring
  (zeta ~0.7, ~11 frames, ~5% overshoot), the handle dips while pressed, a soft halo marks the finger, and a horizontal
  blur scaled to the speed stands in for motion blur. The pictures stay put and are only revealed.
- The rails take is only 72 AI frames, too short for a 122-frame ending, so the AI half visits the worlds one per kick
  in the main drop's first bar (fire, blue, red, water) and lands on the rails on beat 32. The finger then pulls the
  handle left (more rails), right (more reality) and back to the centre, landing on the final accent.
- Type: the V2 face (Instrument Serif Italic), key words in V2's ember orange.
- Song: one continuous passage (beat 0 -> 36 + the accent's tail) from the 30 s source the creator sent; the source
  contains the white-take audio at offset 0.000 s (corr 0.9987). The track rises ~9 dB at beat 28 (its main drop),
  kept as is (static gain + a peak limiter).

## Out of scope

- New camera angles generated with AI (fal.ai): the creator asked to leave generation aside.
