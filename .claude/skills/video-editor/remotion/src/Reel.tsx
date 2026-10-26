import React, { useEffect, useState } from "react";
import { Audio, Video } from "@remotion/media";
import { chromaticAberration } from "@remotion/effects/chromatic-aberration";
import { zoomBlur } from "@remotion/effects/zoom-blur";
import { vignette } from "@remotion/effects/vignette";
import { lightLeak } from "@remotion/effects/light-leak";
import { Lottie, LottieAnimationData } from "@remotion/lottie";
import { loadFont } from "@remotion/fonts";
import {
  AbsoluteFill,
  Easing,
  Sequence,
  Solid,
  cancelRender,
  continueRender,
  delayRender,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import data from "./data.json";

const fontFamily = "Montserrat";
loadFont({ family: fontFamily, url: staticFile("fonts/montserrat-900-latin.woff2"), weight: "900",
  unicodeRange: "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2212" });
loadFont({ family: fontFamily, url: staticFile("fonts/montserrat-900-latinext.woff2"), weight: "900",
  unicodeRange: "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+1E00-1E9F, U+2C60-2C7F, U+A720-A7FF" });

// ---- timeline (frames @ 30 fps)
const SWAP1 = 41; // man -> woman
const SWAP2 = 148; // woman -> man
const CUT_B = 190; // clip 2 starts
const BEAT_2 = 233; // "...numărul 2"
const BEAT_OK = 259; // "ok"
const CTA_IN = 262;
const SEG_STARTS = [0, SWAP1, 124, CUT_B, 247, 290, 315];
const YELLOW = "#FFE600";

type Face = [number, number, number, number] | null;
const faces = data.faces as Face[];

// ---------- helpers
const decay = (frame: number, at: number, tau: number) =>
  frame < at ? 0 : Math.exp(-(frame - at) / tau);

const textStyle = (size: number, color = "white"): React.CSSProperties => ({
  fontFamily,
  fontWeight: 900,
  fontSize: size,
  color,
  lineHeight: 1,
  letterSpacing: -1,
  WebkitTextStroke: `${Math.round(size * 0.16)}px black`,
  paintOrder: "stroke fill",
  textShadow: `0 ${Math.round(size * 0.09)}px 0 rgba(0,0,0,0.45)`,
  whiteSpace: "nowrap",
});

/** Static spot for a sticker over [f0, f1): inside y 560-1060, x 120-960, least time on the face. */
const bestSpot = (f0: number, f1: number, size: number): [number, number] => {
  const half = size / 2;
  let best: [number, number] = [840, 820];
  let bestScore = Infinity;
  for (let cy = 560 + half; cy <= 1060 - half; cy += 30) {
    for (let cx = 120 + half; cx <= 960 - half; cx += 30) {
      let overlap = 0;
      let dist = 0;
      let n = 0;
      for (let f = f0; f < f1; f += 2) {
        const fc = faces[Math.min(f, faces.length - 1)];
        if (!fc) continue;
        const [x, y, w, h] = fc;
        const bx0 = x - 0.25 * w, by0 = y - 0.35 * h, bx1 = x + 1.25 * w, by1 = y + 1.1 * h;
        const ox = Math.max(0, Math.min(cx + half, bx1) - Math.max(cx - half, bx0));
        const oy = Math.max(0, Math.min(cy + half, by1) - Math.max(cy - half, by0));
        overlap += ox * oy;
        dist += Math.hypot(cx - (x + w / 2), cy - (y + h * 0.75));
        n++;
      }
      const score = overlap * 4 + (n ? dist / n : 0) * 60;
      if (score < bestScore) {
        bestScore = score;
        best = [cx, cy];
      }
    }
  }
  return best;
};

// ---------- camera: push-ins, impact punches, shake, whip pan
const useCamera = () => {
  const frame = useCurrentFrame();
  let seg = 0;
  while (frame >= SEG_STARTS[seg + 1]) seg++;
  const segLen = SEG_STARTS[seg + 1] - SEG_STARTS[seg];
  const push = interpolate(frame - SEG_STARTS[seg], [0, segLen], [1.0, 1.06], {
    easing: Easing.inOut(Easing.quad),
  });
  const punch =
    0.24 * decay(frame, SWAP1, 5) + 0.14 * decay(frame, SWAP2, 5) + 0.09 * decay(frame, BEAT_2, 4) + 0.07 * decay(frame, BEAT_OK, 4);
  const shakeAmp = 26 * decay(frame, SWAP1, 6) + 18 * decay(frame, SWAP2, 5);
  let sx = shakeAmp * Math.sin(frame * 2.7);
  let sy = shakeAmp * Math.cos(frame * 3.3);
  // glitch jitter at SWAP2 (stepwise, every 2 frames)
  if (frame >= SWAP2 && frame < SWAP2 + 8) sx += [38, -44, 26, -18][Math.floor((frame - SWAP2) / 2)];
  // whip pan into clip 2
  const whipOut = interpolate(frame, [CUT_B - 7, CUT_B], [0, -380], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic),
  });
  const whipIn = interpolate(frame, [CUT_B, CUT_B + 7], [380, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic),
  });
  const whip = frame < CUT_B ? whipOut : whipIn;
  const whipBlur = Math.abs(whip) / 380;
  return { scale: push + punch, x: sx + whip, y: sy, whipBlur };
};

const Footage: React.FC = () => {
  const frame = useCurrentFrame();
  const cam = useCamera();
  const ca = 34 * decay(frame, SWAP1, 3) + (frame >= SWAP2 && frame < SWAP2 + 9 ? 28 : 0) + 30 * cam.whipBlur;
  const zb = 70 * decay(frame, SWAP1, 3) + 45 * decay(frame, SWAP2, 3) + 25 * decay(frame, BEAT_2, 2);
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${cam.x}px, ${cam.y}px) scale(${cam.scale})`,
        filter: cam.whipBlur > 0.02 ? `blur(${(cam.whipBlur * 22).toFixed(1)}px)` : undefined,
      }}
    >
      <Video
        src={staticFile("base.mp4")}
        muted
        style={{ width: "100%", height: "100%" }}
        effects={[
          chromaticAberration({ amount: ca, angle: frame >= SWAP2 && frame < SWAP2 + 9 ? 90 * (frame % 2) : 0, disabled: ca < 0.5 }),
          zoomBlur({ amount: zb, center: [0.5, 0.42], samples: 24, disabled: zb < 0.5 }),
          vignette({ amount: 0.32, radius: 0.75, feather: 0.5 }),
        ]}
      />
    </AbsoluteFill>
  );
};

const Flash: React.FC = () => {
  const frame = useCurrentFrame();
  const a = 0.95 * decay(frame, SWAP1, 2.2) + 0.7 * decay(frame, SWAP2, 1.8);
  return a > 0.01 ? <AbsoluteFill style={{ backgroundColor: "white", opacity: a }} /> : null;
};

const LeakOverlay: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  return (
    <Solid
      width={width}
      height={height}
      color="black"
      style={{ mixBlendMode: "screen", opacity: 0.6 }}
      effects={[lightLeak({ seed: 3, hueShift: 20, progress: interpolate(frame, [0, 16], [0, 1], { extrapolateRight: "clamp" }) })]}
    />
  );
};

// ---------- hook with in-text countdown
const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s1 = spring({ frame, fps, config: { damping: 11, stiffness: 220 }, from: 1.15, to: 1 });
  const s2 = spring({ frame: frame - 2, fps, config: { damping: 11, stiffness: 220 }, from: 1.2, to: 1 });
  const flip = spring({ frame: frame - 20, fps, config: { damping: 9, stiffness: 260 }, from: 1.7, to: 1 });
  const out = interpolate(frame, [SWAP1 - 1, SWAP1 + 5], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const outScale = interpolate(frame, [SWAP1 - 1, SWAP1 + 5], [1, 1.45], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const n = frame < 20 ? "2" : "1";
  const unit = frame < 20 ? "SECUNDE…" : "SECUNDĂ…";
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 300, opacity: out, transform: `scale(${outScale})` }}>
      <div style={{ ...textStyle(100), transform: `scale(${s1}) rotate(-3deg)` }}>AȘTEAPTĂ</div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 26, marginTop: 18, transform: `scale(${s2}) rotate(-3deg)` }}>
        <span style={{ ...textStyle(150, YELLOW), display: "inline-block", transform: `scale(${frame >= 20 ? flip : 1})` }}>{n}</span>
        <span style={{ ...textStyle(88, YELLOW) }}>{unit}</span>
      </div>
    </AbsoluteFill>
  );
};

// ---------- word-by-word kinetic captions
type Chunk = { words: { text: string; start: number; end: number }[]; start: number; end: number };
const chunks = (data.chunks as Chunk[]).map((c) =>
  c.start < SWAP1 / 30 && c.end > SWAP1 / 30 ? { ...c, end: SWAP1 / 30 } : c,
);

const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cam = useCamera();
  const t = frame / fps;
  const c = chunks.find((ch) => t >= ch.start && t < ch.end);
  if (!c) return null;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", top: 1110 }}>
      <div style={{ display: "flex", gap: 0, opacity: 1 - cam.whipBlur }}>
        {c.words.map((w, i) => {
          const spoken = t >= w.start - 0.02;
          const f = Math.max(0, frame - Math.round(w.start * fps));
          const pop = spring({ frame: f, fps, config: { damping: 10, stiffness: 300 }, from: 0.45, to: 1 });
          const active = t >= w.start && t < Math.max(w.end, w.start + 0.25);
          return (
            <span
              key={i}
              style={{
                ...textStyle(96, active ? YELLOW : "white"),
                display: "inline-block",
                margin: "0 20px",
                opacity: spoken ? 1 : 0,
                transform: `translateY(${(1 - pop) * 40}px) scale(${pop * (active ? 1.06 : 1)}) rotate(${active ? -2 : 0}deg)`,
              }}
            >
              {w.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------- stickers (animated Noto emoji)
const useLottie = (file: string) => {
  const [handle] = useState(() => delayRender(`lottie ${file}`));
  const [anim, setAnim] = useState<LottieAnimationData | null>(null);
  useEffect(() => {
    fetch(staticFile(file))
      .then((r) => r.json())
      .then((j) => {
        setAnim(j);
        continueRender(handle);
      })
      .catch((e) => cancelRender(e));
  }, [file, handle]);
  return anim;
};

const Sticker: React.FC<{ file: string; size: number; at: [number, number]; dur: number; tilt?: number }> = ({
  file, size, at, dur, tilt = 0,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const anim = useLottie(file);
  const pop = spring({ frame, fps, config: { damping: 8, stiffness: 240 } });
  const out = interpolate(frame, [dur - 5, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const wob = 12 * Math.exp(-frame / 8) * Math.sin(frame * 0.9);
  if (!anim) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: at[0] - size / 2,
        top: at[1] - size / 2,
        width: size,
        height: size,
        transform: `scale(${pop * out}) rotate(${tilt + wob}deg)`,
        filter: "drop-shadow(0 10px 14px rgba(0,0,0,0.45))",
      }}
    >
      <Lottie animationData={anim} loop style={{ width: size, height: size }} />
    </div>
  );
};

const STICKERS = [
  { file: "emoji/1f631.json", from: SWAP1 + 2, dur: 48, size: 270, tilt: 8 },
  { file: "emoji/1f440.json", from: 90, dur: 34, size: 230, tilt: -6 },
  { file: "emoji/1f602.json", from: SWAP2 + 2, dur: 38, size: 250, tilt: 8 },
  { file: "emoji/1f44c.json", from: BEAT_OK, dur: 30, size: 230, tilt: -8 },
].map((s) => ({ ...s, at: bestSpot(s.from, s.from + s.dur, s.size * 0.8) }));

// ---------- badges & CTA
const Badge: React.FC<{ label: string; color: string; dur: number }> = ({ label, color, dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inX = spring({ frame, fps, config: { damping: 12, stiffness: 200 }, from: -700, to: 0 });
  const out = interpolate(frame, [dur - 6, dur], [0, -700], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute", left: 130, top: 300,
        transform: `translateX(${inX + out}px) rotate(-4deg)`,
        background: color, borderRadius: 22, padding: "14px 30px", border: "6px solid white",
        boxShadow: "0 12px 26px rgba(0,0,0,0.4)",
        fontFamily, fontWeight: 900, fontSize: 70, color: "black", lineHeight: 1,
      }}
    >
      {label}
    </div>
  );
};

const CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 9, stiffness: 220 }, from: 0, to: 1 });
  const pop2 = spring({ frame: frame - 6, fps, config: { damping: 9, stiffness: 220 }, from: 0, to: 1 });
  const pulse = 1 + 0.04 * Math.sin(frame * 0.5);
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 290 }}>
      <div style={{ ...textStyle(150), transform: `scale(${pop * pulse}) rotate(-3deg)` }}>
        1 <span style={{ color: YELLOW }}>SAU</span> 2?
      </div>
      <div
        style={{
          marginTop: 26, transform: `scale(${pop2})`, background: "white", borderRadius: 999,
          padding: "16px 40px", display: "flex", alignItems: "center", gap: 14,
          boxShadow: "0 12px 26px rgba(0,0,0,0.4)",
          fontFamily, fontWeight: 900, fontSize: 50, color: "black",
        }}
      >
        <PointDownIcon />
        SCRIE ÎN COMENTARII
      </div>
    </AbsoluteFill>
  );
};

const PointDownIcon: React.FC = () => {
  const frame = useCurrentFrame();
  const anim = useLottie("emoji/1f447.json");
  const bob = Math.abs(Math.sin(frame * 0.35)) * 10;
  if (!anim) return <div style={{ width: 84, height: 84 }} />;
  return (
    <div style={{ width: 84, height: 84, transform: `translateY(${bob}px)` }}>
      <Lottie animationData={anim} loop style={{ width: 84, height: 84 }} />
    </div>
  );
};

// ---------- sound design
const S = (name: string) => staticFile(`sfx/${name}.wav`);
const SFX: { at: number; src: string; vol: number; dur?: number; fade?: number }[] = [
  { at: 0, src: S("whoosh"), vol: 0.6 },
  { at: 1, src: S("tick_001"), vol: 0.9 },
  { at: 20, src: S("tick_001"), vol: 0.9 },
  { at: SWAP1 - 16, src: S("riser"), vol: 0.55 },
  { at: SWAP1, src: S("vine-boom"), vol: 1.0 },
  { at: SWAP1, src: S("shutter-modern"), vol: 0.6 },
  { at: SWAP1 + 5, src: S("anime-wow"), vol: 0.32, dur: 26, fade: 8 },
  { at: SWAP1 + 3, src: S("drop_002"), vol: 0.5 },
  { at: 50, src: S("whip"), vol: 0.45 },
  { at: 90, src: S("switch"), vol: 0.45 },
  { at: SWAP2 - 3, src: S("record-scratch"), vol: 0.6, dur: 15, fade: 5 },
  { at: SWAP2, src: S("glitch_002"), vol: 0.9 },
  { at: SWAP2, src: S("impactPunch_heavy_000"), vol: 0.75 },
  { at: SWAP2 + 3, src: S("drop_002"), vol: 0.45 },
  { at: CUT_B - 8, src: S("whoosh"), vol: 0.9 },
  { at: CUT_B - 2, src: S("whip"), vol: 0.6 },
  { at: CUT_B + 3, src: S("ding"), vol: 0.32 },
  { at: BEAT_2, src: S("impactPunch_heavy_000"), vol: 0.35 },
  { at: BEAT_OK, src: S("snapchat-notification"), vol: 0.5 },
  { at: CTA_IN, src: S("whip"), vol: 0.45 },
  { at: CTA_IN + 6, src: S("drop_002"), vol: 0.45 },
];

const SoundDesign: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <>
      <Audio src={staticFile("voice.wav")} />
      {SFX.map((s, i) => (
        <Sequence key={i} from={s.at} durationInFrames={s.dur} premountFor={fps}>
          <Audio
            src={s.src}
            volume={(f) =>
              s.dur && s.fade ? s.vol * interpolate(f, [s.dur - s.fade, s.dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : s.vol
            }
          />
        </Sequence>
      ))}
    </>
  );
};

export const Reel: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Footage />
      <Sequence from={CUT_B - 7} durationInFrames={16} premountFor={fps}>
        <LeakOverlay />
      </Sequence>
      <Flash />
      <Sequence from={0} durationInFrames={SWAP1 + 6} premountFor={fps}>
        <Hook />
      </Sequence>
      <Captions />
      {STICKERS.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={s.dur} premountFor={fps}>
          <Sticker file={s.file} size={s.size} at={s.at} dur={s.dur} tilt={s.tilt} />
        </Sequence>
      ))}
      <Sequence from={SWAP1 + 8} durationInFrames={SWAP2 - SWAP1 - 12} premountFor={fps}>
        <Badge label="PROBA #1" color="#FF4D8D" dur={SWAP2 - SWAP1 - 12} />
      </Sequence>
      <Sequence from={CUT_B + 2} durationInFrames={CTA_IN - CUT_B - 4} premountFor={fps}>
        <Badge label="PROBA #2" color={YELLOW} dur={CTA_IN - CUT_B - 4} />
      </Sequence>
      <Sequence from={CTA_IN} premountFor={fps}>
        <CTA />
      </Sequence>
      <SoundDesign />
    </AbsoluteFill>
  );
};
