import React from "react";
import { Audio, Video } from "@remotion/media";
import { lightLeak } from "@remotion/effects/light-leak";
import { zoomBlur } from "@remotion/effects/zoom-blur";
import { AbsoluteFill, Easing, interpolate, Sequence, Solid, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { QuestionV2 } from "./TypeV2";

// DJ reel V4 - real take and AI worlds intercut on the track, simulated camera angles in both, 15.23 s = 8 bars.
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
//   400-456 REAL | AI  split: reality slides in on the main drop, rails on the right   beat 28 -> 32

const BEAT = 14.2806;
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
  const div = interpolate(f, [400, 407], [0, 540], { ...clamp, easing: ease });            // split divider x
  const sp = interpolate(f, [400, 407], [0, 1], { ...clamp, easing: ease });
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

      <Sequence name="Final: AI șine (dreapta)" from={400} durationInFrames={57} premountFor={fps}>
        <Shot from={400} cam={() => ({ s: 1 + 0.75 * sp, ox: 540, oy: 1080, tx: 270 * sp, ty: 181 * sp })}>
          <Video src={staticFile(AI)} trimBefore={366} muted style={full} />
        </Shot>
      </Sequence>
      <Sequence name="Final: REAL (stânga, slide)" from={400} durationInFrames={57} premountFor={fps}>
        <Shot from={400} clip={`inset(0px ${1080 - div}px 0px 0px)`} cam={() => ({ s: 1, ox: 540, oy: 1000, tx: -270 })}>
          <Video src={staticFile(W)} trimBefore={17} muted style={full} />
        </Shot>
        <div style={{
          position: "absolute", top: 0, left: div - 2, width: 4, height: 1920, background: "#FFF6EC",
          boxShadow: "0 0 18px rgba(255,255,255,0.9), 0 0 46px rgba(255,140,60,0.55)", opacity: div > 2 ? 1 : 0,
        }} />
      </Sequence>

      <Audio name="Piesa (pasaj continuu, 8 măsuri)" src={staticFile("v4/song_v4.wav")} />
      <Audio name="SFX click" src={staticFile("v4/sfx/click.wav")} from={57} volume={0.1} />
      <Audio name="SFX aprindere" src={staticFile("v4/sfx/ignition.wav")} from={57} volume={0.22} />
      <Audio name="SFX retragere" src={staticFile("v4/sfx/swish.wav")} from={57} volume={0.07} />
      <Audio name="SFX foșnet foaie" src={staticFile("v4/sfx/rustle.wav")} from={97} volume={0.3} />
      <Audio name="SFX swish mâini" src={staticFile("v4/sfx/swish.wav")} from={206} volume={0.1} />
      <Audio name="SFX apă" src={staticFile("v4/sfx/water.wav")} from={266} volume={0.13} />
      <Audio name="SFX aer șine" src={staticFile("v4/sfx/air_lr.wav")} from={319} volume={0.1} />
      <Audio name="SFX swish față" src={staticFile("v4/sfx/swish.wav")} from={363} volume={0.1} />
      <Audio name="SFX slide final" src={staticFile("v4/sfx/swish.wav")} from={392} volume={0.13} />
    </AbsoluteFill>
  );
};
