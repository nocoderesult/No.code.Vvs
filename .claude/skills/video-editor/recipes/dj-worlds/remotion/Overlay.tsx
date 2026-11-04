import React from "react";
import { loadFont } from "@remotion/fonts";
import { AbsoluteFill, Easing, interpolate, staticFile, useCurrentFrame } from "remotion";
import plan from "./plan.json";

// Typography layer for Reel4 v2 (transparent; composited over the graded plates in compose4.py).
// Two voices only: Instrument Serif Italic speaks (hook, CTA); JetBrains Mono labels the worlds (00 REAL .. 05 APUS).
const SERIF = "Instrument Serif";
const MONO = "JetBrains Mono";
const LATIN = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD";
const LATIN_EXT = "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF";
loadFont({ family: SERIF, url: staticFile("fonts/isi-latin.woff2"), weight: "400", style: "italic", unicodeRange: LATIN });
loadFont({ family: SERIF, url: staticFile("fonts/isi-latinext.woff2"), weight: "400", style: "italic", unicodeRange: LATIN_EXT });
loadFont({ family: MONO, url: staticFile("fonts/jbm-latin.woff2"), weight: "100 800", unicodeRange: LATIN });
loadFont({ family: MONO, url: staticFile("fonts/jbm-latin-ext.woff2"), weight: "100 800", unicodeRange: LATIN_EXT });

const W = plan.w;
const INK = "#121212";
const BONE = "#F4F1EA";
const EMBER = "#FF6A1A";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const ramp = (f: number, a: number, b: number, ease = Easing.out(Easing.cubic)) => interpolate(f, [a, b], [0, 1], { ...CLAMP, easing: ease });

type Label = { from: number; to: number; idx: string; name: string; dark?: boolean; typed?: boolean };
const LABELS: Label[] = [
  { from: 0, to: 28, idx: "00", name: "REAL", dark: true, typed: false },
  { from: 57, to: 114, idx: "01", name: "FOC" },
  { from: 114, to: 171, idx: "02", name: "NOAPTE" },
  { from: 171, to: 228, idx: "03", name: "CEAȚĂ" },
  { from: 228, to: 257, idx: "04", name: "OCEAN", dark: true },
  { from: 257, to: plan.frames, idx: "05", name: "APUS", dark: true },
];

const WorldLabel: React.FC<{ l: Label; frame: number }> = ({ l, frame }) => {
  const text = `${l.idx}  ${l.name}`;
  const k = frame - l.from;
  const shown = l.typed === false ? text.length : Math.min(text.length, Math.floor(k * 1.7) + 1);
  const cursor = l.typed !== false && k < Math.ceil(text.length / 1.7) + 5 && Math.floor(k / 2) % 2 === 0;
  const color = l.dark ? "rgba(18,18,18,0.82)" : "rgba(244,241,234,0.94)";
  return (
    <div style={{
      position: "absolute", top: 236, left: 0, width: W, display: "flex", justifyContent: "center", alignItems: "center",
      fontFamily: MONO, fontWeight: 500, fontSize: 30, letterSpacing: "0.34em", paddingLeft: "0.34em", color,
      textShadow: l.dark ? "none" : "0 2px 14px rgba(0,0,0,0.5)", whiteSpace: "pre",
    }}>
      <span style={{ opacity: 0.55 }}>{text.slice(0, Math.min(shown, 2))}</span>
      <span>{text.slice(2, shown)}</span>
      <span style={{ display: "inline-block", width: 15, height: 30, marginLeft: 6, background: color, opacity: cursor ? 1 : 0 }} />
    </div>
  );
};

const serifLine: React.CSSProperties = {
  position: "absolute", left: 0, width: W, textAlign: "center", fontFamily: SERIF, fontStyle: "italic", fontWeight: 400,
  letterSpacing: "-0.015em", lineHeight: 1.0, whiteSpace: "nowrap",
};

export const Overlay: React.FC = () => {
  const frame = useCurrentFrame();
  const t = plan.text;
  const label = LABELS.find((l) => frame >= l.from && frame < l.to);

  // hook 1: ink on the light wall, fully readable on frame 0 (it is the thumbnail), drifts up a few px
  const h1 = frame >= t.hook1.from && frame < t.hook1.to;
  const h1y = interpolate(frame, [t.hook1.from, t.hook1.to], [10, 0], CLAMP);

  // hook 2: bone on black, blur-in on beat 10; "AI" ignites on beat 11
  const h2 = frame >= t.hook2.from && frame < t.hook2.to;
  const h2in = ramp(frame, t.hook2.from, t.hook2.from + 5);
  const ign = ramp(frame, t.hook2.accent_from, t.hook2.accent_from + 3, Easing.out(Easing.quad));

  // CTA
  const cta = frame >= t.cta.from && frame < t.cta.to;
  const cin = ramp(frame, t.cta.from, t.cta.from + 6);
  const cin2 = ramp(frame, t.cta.from + 6, t.cta.from + 12);

  return (
    <AbsoluteFill>
      {label ? <WorldLabel l={label} frame={frame} /> : null}

      {h1 ? (
        <div style={{ ...serifLine, top: 448, fontSize: 124, color: INK, transform: `translateY(${h1y}px)` }}>{t.hook1.text}</div>
      ) : null}

      {h2 ? (
        <div style={{
          ...serifLine, top: 448, fontSize: 124, color: BONE, opacity: h2in, filter: `blur(${(1 - h2in) * 14}px)`,
          transform: `translateY(${(1 - h2in) * 14}px)`,
        }}>
          Restul e{" "}
          <span style={{
            color: ign > 0 ? `color-mix(in srgb, ${EMBER} ${Math.round(ign * 100)}%, ${BONE})` : BONE,
            textShadow: `0 0 ${28 * ign}px rgba(255,106,26,${0.75 * ign}), 0 0 ${70 * ign}px rgba(255,90,10,${0.35 * ign})`,
          }}>AI</span>.
        </div>
      ) : null}

      {cta ? (
        <>
          <div style={{
            ...serifLine, top: 1296, fontSize: 88, lineHeight: 1.04, color: BONE, opacity: cin, filter: `blur(${(1 - cin) * 12}px)`,
            transform: `translateY(${(1 - cin) * 16}px)`, textShadow: "0 4px 30px rgba(0,0,0,0.65)",
          }}>În ce lume îl duc<br />data viitoare?</div>
          <div style={{
            position: "absolute", top: 1508, left: 0, width: W, textAlign: "center", fontFamily: MONO, fontWeight: 500, fontSize: 25,
            letterSpacing: "0.3em", paddingLeft: "0.3em", color: "rgba(244,241,234,0.86)", opacity: cin2,
            textShadow: "0 2px 14px rgba(0,0,0,0.6)",
          }}>SCRIE ÎN COMENTARII ↓</div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};
