import React from "react";
import { Audio, Video } from "@remotion/media";
import { lightLeak } from "@remotion/effects/light-leak";
import { zoomBlur } from "@remotion/effects/zoom-blur";
import { AbsoluteFill, Easing, interpolate, Sequence, Solid, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { QuestionV2 } from "./TypeV2";
import { ComparisonHandle, Drag, Press, pressAt, sliderX } from "./Slider";

// DJ reel V4 - real take and AI worlds intercut on the track, simulated camera angles in both, 17.4 s: the track runs
// on through its main drop and the reel ends on the drop's first accent (beat 36) and the tail of that note.
// 126.045 BPM -> 14.2806 frames/beat; frame 0 = song beat 0. One continuous passage of the creator's track.
// Sources at 1620x2880 so punch-ins stay sharp. The rules of the V3 brief still hold: direct white -> fire cut,
// the lift is one locked shot with only the track, the drop's kick is the only impact, the song is not processed
// beyond static gain and a peak limiter that only touches the main drop's loudest transients.
//
//   0-56    REAL  white room, native framing, the question, slow push            touch = beat 4
//   57-99   AI    fire: match cut at the take's scale, pull-back reveal (zoom blur)
//   100-170 AI    blue + the lift, locked                                        beat 7 -> drop
//   171-199 AI    red wide: shake + a pulse on every kick                        beat 12 (drop)
//   200-213 AI    red medium (punch-in)                                          beat 14
//   214-227 REAL  close-up on the hands, second camera                           beat 15
//   228-327 AI    red fog -> the source's own whiteout -> water, slow push       beat 16
//   328-370 AI    rails: settle + warm light leak                                beat 23
//   371-399 REAL  close-up on the face, third camera                             beat 26
//   400-521 REAL | AI  comparison slider, reality on the left:                   beat 28 (main drop) -> 36
//           400 a finger pulls the handle in from the left edge; the AI half visits the worlds, one per kick
//               (fire, blue, red, water), and lands on the rails on beat 32
//           457 pulled left (more rails), 485 pulled right (more reality), 504 back to the centre on the accent

const BEAT = 14.2806;
const WE = "v4/white_end_30.mp4";  // raw 120 fps frames 1176..1664 (real time, native framing); trimBefore = (raw - 1176) / 4

// the slider: where each drag goes and when the finger is down
const DRAGS: Drag[] = [
  { at: 400, to: 540 },  // grabbed at the left edge on the main drop's downbeat, pulled to the centre
  { at: 457, to: 300 },  // beat 32: the rails land, pulled left to show more of them
  { at: 485, to: 780 },  // beat 34: pulled right, back to reality
  { at: 504, to: 540 },  // the fill -> the centre, landing on the final accent (beat 36 = frame 514)
];
const PRESSES: Press[] = [[397, 400, 412, 416], [454, 457, 468, 472], [482, 485, 514, 518]];
const HANDLE_Y = 1000;
const W = "v4/white120_15x.mp4";   // raw 120 fps frames 700..1200 (real time); trimBefore = (raw - 700) / 4
const AI = "v4/ai_master15.mp4";   // AI frames 0..422; trimBefore = AI frame
const full = { width: "100%", height: "100%" } as const;
const ease = Easing.out(Easing.cubic);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

const pulse = (f: number) => {
  if (f < 171 || (f >= 251 && f < 277)) return 1;           // no pulses before the drop or in the whiteout
  const last = Math.floor(Math.floor((f + 0.25) / BEAT) * BEAT + 0.25);
  return 1 + 0.02 * Math.exp(-(f - last) / 3);
};

type Cam = { s: number; ox: number; oy: number; tx?: number; ty?: number; rot?: number; drift?: number };
const Shot: React.FC<{ from: number; cam: (abs: number, rel: number) => Cam; clip?: string; children: React.ReactNode }> = ({ from, cam, clip, children }) => {
  const rel = useCurrentFrame();
  const abs = from + rel;
  const c = cam(abs, rel);
  const d = c.drift ?? 0;
  const dx = d * (Math.sin(abs * 0.23) + 0.6 * Math.sin(abs * 0.57 + 1.3));
  const dy = d * (Math.cos(abs * 0.19) + 0.6 * Math.sin(abs * 0.43 + 0.4));
  return (
    <AbsoluteFill style={{ overflow: "hidden", clipPath: clip }}>
      <AbsoluteFill style={{
        transformOrigin: `${c.ox}px ${c.oy}px`,
        transform: `translate(${(c.tx ?? 0) + dx}px, ${(c.ty ?? 0) + dy}px) rotate(${c.rot ?? 0}deg) scale(${c.s * pulse(abs)})`,
      }}>
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// AI frame -> the white take's native framing (inverse of the booth-edge fit: canvas = 0.5815 * raw + (228.1, 347.3))
const MATCH = { s: 1 / 0.5815, tx: -228.1 / 0.5815, ty: -347.3 / 0.5815 };

export const ReelV4: React.FC = () => {
  const { fps } = useVideoConfig();
  const f = useCurrentFrame();
  const x = sliderX(f, fps, DRAGS);                                         // the divider, where the finger has it
  const vx = (sliderX(f + 0.25, fps, DRAGS) - sliderX(f - 0.25, fps, DRAGS)) * 2;
  const cut = Math.min(1080, Math.max(0, x));
  // the AI picture moves into its half while reality is pulled in, then stays put (a comparison slider only reveals)
  const aiHalf = (a: number): Cam => {
    const sp = a < 430 ? Math.min(1, Math.max(0, sliderX(a, fps, DRAGS) / 540)) : 1;
    return { s: 1 + 0.75 * sp, ox: 540, oy: 1080, tx: 270 * sp, ty: 181 * sp };
  };
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Sequence name="REAL alb + întrebarea" from={0} durationInFrames={57} premountFor={fps}>
        <Shot from={0} cam={(a) => ({ s: 1 + 0.04 * (a / 56), ox: 540, oy: 1000 })}>
          <Video src={staticFile(W)} trimBefore={68} muted style={full} />
        </Shot>
        <QuestionV2 />
      </Sequence>

      <Sequence name="AI foc – match cut + retragere" from={57} durationInFrames={43} premountFor={fps}>
        <Shot from={57} cam={(_, r) => {
          const u = interpolate(r, [0, 14], [0, 1], { ...clamp, easing: ease });
          return { s: MATCH.s + (1 - MATCH.s) * u, ox: 0, oy: 0, tx: MATCH.tx * (1 - u), ty: MATCH.ty * (1 - u) };
        }}>
          <Video src={staticFile(AI)} trimBefore={8} muted style={full} effects={[
            zoomBlur({ amount: interpolate(f, [58, 70], [55, 0], clamp), center: [0.5, 0.5], samples: 24 }),
          ]} />
        </Shot>
      </Sequence>

      <Sequence name="AI albastru + ridicarea" from={100} durationInFrames={71} premountFor={fps}>
        <Video src={staticFile(AI)} trimBefore={76} muted style={full} />
      </Sequence>

      <Sequence name="AI roșu larg (drop)" from={171} durationInFrames={29} premountFor={fps}>
        <Shot from={171} cam={(_, r) => ({ s: 1, ox: 540, oy: 960, tx: 9 * Math.exp(-r / 3) * Math.sin(r * 2.6), ty: 9 * Math.exp(-r / 3) * Math.cos(r * 3.7) })}>
          <Video src={staticFile(AI)} trimBefore={182} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="AI roșu mediu" from={200} durationInFrames={14} premountFor={fps}>
        <Shot from={200} cam={() => ({ s: 1.22, ox: 540, oy: 930 })}>
          <Video src={staticFile(AI)} trimBefore={211} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="REAL mâini (camera 2)" from={214} durationInFrames={14} premountFor={fps}>
        <Shot from={214} cam={() => ({ s: 1.7, ox: 600, oy: 1250, tx: -40, ty: -190, rot: 3, drift: 4 })}>
          <Video src={staticFile(W)} trimBefore={99} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="AI fum → apă" from={228} durationInFrames={100} premountFor={fps}>
        <Shot from={228} cam={(a) => ({ s: interpolate(a, [277, 327], [1, 1.1], clamp), ox: 540, oy: 900 })}>
          <Video src={staticFile(AI)} trimBefore={239} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="AI șine" from={328} durationInFrames={43} premountFor={fps}>
        <Shot from={328} cam={(_, r) => ({ s: interpolate(r, [0, 10], [1.08, 1], { ...clamp, easing: ease }), ox: 540, oy: 820 })}>
          <Video src={staticFile(AI)} trimBefore={351} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Strălucire caldă șine (light leak discret)" from={328} durationInFrames={30} layout="none">
        <Solid color="#000000" width={1080} height={1920} style={{ position: "absolute", mixBlendMode: "screen", opacity: 0.28 }}
          effects={[lightLeak({ seed: 7, hueShift: 8, progress: interpolate(f, [328, 357], [0, 1], clamp) })]} />
      </Sequence>
      <Sequence name="REAL față (camera 3)" from={371} durationInFrames={29} premountFor={fps}>
        <Shot from={371} cam={() => ({ s: 1.55, ox: 540, oy: 860, tx: 20, ty: 120, rot: -2, drift: 3 })}>
          <Video src={staticFile(W)} trimBefore={0} muted style={full} />
        </Shot>
      </Sequence>

      <Sequence name="Final AI: foc" from={400} durationInFrames={14} premountFor={fps}>
        <Shot from={400} cam={aiHalf}>
          <Video src={staticFile(AI)} trimBefore={60} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Final AI: albastru" from={414} durationInFrames={14} premountFor={fps}>
        <Shot from={414} cam={aiHalf}>
          <Video src={staticFile(AI)} trimBefore={80} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Final AI: roșu" from={428} durationInFrames={14} premountFor={fps}>
        <Shot from={428} cam={aiHalf}>
          <Video src={staticFile(AI)} trimBefore={200} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Final AI: apă" from={442} durationInFrames={15} premountFor={fps}>
        <Shot from={442} cam={aiHalf}>
          <Video src={staticFile(AI)} trimBefore={305} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Final AI: șine" from={457} durationInFrames={65} premountFor={fps}>
        <Shot from={457} cam={aiHalf}>
          <Video src={staticFile(AI)} trimBefore={358} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Final REAL (stânga, slider)" from={400} durationInFrames={122} premountFor={fps}>
        <Shot from={400} clip={`inset(0px ${1080 - cut}px 0px 0px)`} cam={() => ({ s: 1, ox: 540, oy: 1000, tx: -270 })}>
          <Video src={staticFile(WE)} trimBefore={0} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Slider: linie + mâner" from={400} durationInFrames={122} layout="none">
        <ComparisonHandle x={x} vx={vx} y={HANDLE_Y} press={pressAt(f, PRESSES)}
          appear={interpolate(f, [400, 404], [0, 1], { ...clamp, easing: ease })} />
      </Sequence>

      <Audio name="Piesa (pasaj continuu, până la accentul din drop-ul mare)" src={staticFile("v4/song_v4b.wav")} />
      <Audio name="SFX click" src={staticFile("v4/sfx/click.wav")} from={57} volume={0.1} />
      <Audio name="SFX aprindere" src={staticFile("v4/sfx/ignition.wav")} from={57} volume={0.22} />
      <Audio name="SFX retragere" src={staticFile("v4/sfx/swish.wav")} from={57} volume={0.07} />
      <Audio name="SFX foșnet foaie" src={staticFile("v4/sfx/rustle.wav")} from={97} volume={0.3} />
      <Audio name="SFX swish mâini" src={staticFile("v4/sfx/swish.wav")} from={206} volume={0.1} />
      <Audio name="SFX apă" src={staticFile("v4/sfx/water.wav")} from={266} volume={0.13} />
      <Audio name="SFX aer șine" src={staticFile("v4/sfx/air_lr.wav")} from={319} volume={0.1} />
      <Audio name="SFX swish față" src={staticFile("v4/sfx/swish.wav")} from={363} volume={0.1} />
      <Audio name="SFX slider intră" src={staticFile("v4/sfx/swish.wav")} from={395} volume={0.13} />
      <Audio name="SFX slider stânga" src={staticFile("v4/sfx/swish.wav")} from={453} volume={0.07} />
      <Audio name="SFX slider dreapta" src={staticFile("v4/sfx/swish.wav")} from={481} volume={0.07} />
    </AbsoluteFill>
  );
};
