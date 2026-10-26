import React from "react";
import { loadFont } from "@remotion/fonts";
import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import data from "./data.json";

export type LayerKind = "front" | "behind" | "mask";
type Box = number[]; // [x, y, w, h] normalized to the output frame

const W = 1080;
const H = 1920;
const FPS = 30;
const SANS = "Inter Display";
const SERIF = "Instrument Serif";
const LATIN = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD";
const LATIN_EXT = "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF";

for (const [file, weight] of [["Medium", "500"], ["SemiBold", "600"], ["Bold", "700"], ["ExtraBold", "800"], ["Black", "900"]]) {
  loadFont({ family: SANS, url: staticFile(`fonts/InterDisplay-${file}.otf`), weight, format: "opentype" });
}
loadFont({ family: SERIF, url: staticFile("fonts/isi-latin.woff2"), weight: "400", style: "italic", unicodeRange: LATIN });
loadFont({ family: SERIF, url: staticFile("fonts/isi-latinext.woff2"), weight: "400", style: "italic", unicodeRange: LATIN_EXT });
loadFont({ family: SERIF, url: staticFile("fonts/isr-latin.woff2"), weight: "400", style: "normal", unicodeRange: LATIN });
loadFont({ family: SERIF, url: staticFile("fonts/isr-latinext.woff2"), weight: "400", style: "normal", unicodeRange: LATIN_EXT });

const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const f = (t: number) => Math.round(t * FPS);
const ramp = (frame: number, a: number, b: number, ease = Easing.out(Easing.cubic)) =>
  interpolate(frame, [a, b], [0, 1], { ...CLAMP, easing: ease });
const pop = (frame: number, start: number, damping = 15, stiffness = 170) =>
  frame < start ? 0 : spring({ frame: frame - start, fps: FPS, config: { damping, stiffness, mass: 0.9 } });

function segAt(frame: number) {
  let s = data.segments[0];
  for (const x of data.segments) if (frame >= x.start) s = x;
  return s;
}

const SHADOW = "0 2px 14px rgba(0,0,0,0.55), 0 0 3px rgba(0,0,0,0.35)";
const GLASS_DARK = {
  background: "linear-gradient(180deg, rgba(255,255,255,0.10) 0%, rgba(255,255,255,0.02) 38%, rgba(10,12,10,0.30) 100%)",
  border: "1.5px solid rgba(255,255,255,0.17)",
  boxShadow: "0 24px 60px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.22)",
};
const GLASS_LIGHT = {
  background: "linear-gradient(180deg, rgba(255,255,255,0.20) 0%, rgba(255,255,255,0.08) 45%, rgba(255,255,255,0.05) 100%)",
  border: "1.5px solid rgba(255,255,255,0.30)",
  boxShadow: "0 30px 80px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.40)",
};

// ---------------------------------------------------------------- glass card (+ its frost mask)
const Glass: React.FC<{
  layer: LayerKind; on: "front" | "behind"; x: number; y: number; w: number; h: number; r: number;
  tone: "dark" | "light"; transform?: string; opacity?: number; children?: React.ReactNode;
}> = ({ layer, on, x, y, w, h, r, tone, transform = "none", opacity = 1, children }) => {
  const geo: React.CSSProperties = { position: "absolute", left: x, top: y, width: w, height: h, borderRadius: r, transform, opacity };
  if (layer === "mask") {
    return <div style={{ ...geo, background: on === "behind" ? "#FF0000" : "#00FF00", mixBlendMode: "screen" }} />;
  }
  if (layer !== on) return null;
  return <div style={{ ...geo, ...(tone === "dark" ? GLASS_DARK : GLASS_LIGHT), overflow: "hidden" }}>{children}</div>;
};

// ---------------------------------------------------------------- captions (reference style: one word, white, soft shadow)
const Captions: React.FC<{ frame: number }> = ({ frame }) => {
  const t = frame / FPS;
  const c = data.captions.find((x) => t >= x.start && t < x.end);
  if (!c) return null;
  const p = ramp(frame, f(c.start), f(c.start) + 4);
  const type: React.CSSProperties = c.emph
    ? { fontFamily: SERIF, fontStyle: "italic", fontWeight: 400, fontSize: 96, letterSpacing: "-0.01em" }
    : { fontFamily: SANS, fontWeight: 600, fontSize: 70, letterSpacing: "-0.022em" };
  return (
    <div style={{
      position: "absolute", left: 60, right: 60, top: c.y * H, textAlign: "center", color: "white",
      transform: `translateY(-50%) translateY(${(1 - p) * 14}px) scale(${0.95 + 0.05 * p})`,
      opacity: p, filter: `blur(${(1 - p) * 9}px)`, textShadow: SHADOW, lineHeight: 1.05, ...type,
    }}>{c.text}</div>
  );
};

// ---------------------------------------------------------------- effect counter pill
const Pills: React.FC<{ frame: number }> = ({ frame }) => (
  <>
    {data.pills.map((p) => {
      if (p.start == null || p.end == null) return null;
      const s = f(p.start), e = f(p.end);
      if (frame < s || frame >= e) return null;
      const k = pop(frame, s, 16, 190);
      const out = 1 - ramp(frame, e - 7, e, Easing.in(Easing.cubic));
      return (
        <div key={p.n} style={{
          position: "absolute", top: 0.108 * H, left: W / 2, display: "flex", alignItems: "center", gap: 16,
          height: 74, padding: "0 32px 0 11px", borderRadius: 37, background: "rgba(14,16,14,0.64)",
          border: "1.5px solid rgba(255,255,255,0.20)", boxShadow: "0 10px 30px rgba(0,0,0,0.30)",
          transform: `translate(-50%, -50%) translateY(${(1 - k) * -16 + (1 - out) * -10}px) scale(${0.88 + 0.12 * k})`,
          opacity: Math.min(1, k * 1.5) * out, color: "white", fontFamily: SANS, whiteSpace: "nowrap",
        }}>
          <div style={{ height: 52, padding: "0 17px", borderRadius: 26, background: "#FFFFFF", color: "#0B0B0B",
            display: "flex", alignItems: "center", fontWeight: 800, fontSize: 30, letterSpacing: "-0.01em" }}>
            {p.n}<span style={{ opacity: 0.45, fontWeight: 700 }}>/6</span>
          </div>
          <div style={{ fontWeight: 600, fontSize: 35, letterSpacing: "-0.015em" }}>{p.label}</div>
        </div>
      );
    })}
  </>
);

// ---------------------------------------------------------------- 1. huge word rising from behind the head
const BehindWords: React.FC<{ frame: number }> = ({ frame }) => (
  <>
    {data.behind.map((b, i) => {
      const s = f(b.start), e = f(b.end);
      if (frame < s || frame >= e) return null;
      const fc: Box = segAt(frame).face;
      const cx = (fc[0] + fc[2] / 2) * W;
      const base = (fc[1] + 0.34 * fc[3]) * H;            // baseline at the forehead: the head covers the foot of the letters
      const rise = frame - s < 0 ? 0 : spring({ frame: frame - s, fps: FPS, config: { damping: 15, stiffness: 95, mass: 1 } });
      const sink = ramp(frame, e - 9, e, Easing.in(Easing.cubic));
      const t = frame / FPS;
      const glow = "glow" in b && b.glow ? Math.max(0, 1 - Math.abs(t - (b.glow as number) - 0.15) / 0.4) : 0;
      return (
        <div key={i} style={{
          position: "absolute", left: cx, top: base, transformOrigin: "50% 100%",
          transform: `translate(-50%, -100%) translateY(${((1 - rise) + sink) * 0.28 * H}px) scale(${0.86 + 0.14 * rise})`,
          fontFamily: SANS, fontWeight: 900, fontSize: 600, lineHeight: 0.74, letterSpacing: "-0.065em", whiteSpace: "nowrap",
          color: "#FFFFFF", opacity: Math.min(1, rise * 1.8) * (1 - sink * 0.7),
          textShadow: `0 20px 60px rgba(0,0,0,0.45), 0 0 ${6 + glow * 46}px rgba(255,255,255,${0.10 + glow * 0.45})`,
        }}>{b.text}</div>
      );
    })}
  </>
);

// ---------------------------------------------------------------- 2. over the shoulder: BEFORE / AFTER cards behind him
const OtsCards: React.FC<{ frame: number; layer: LayerKind }> = ({ frame, layer }) => {
  const o = data.ots;
  if (frame < f(o.start) || frame >= f(o.end)) return null;
  const left = Math.min(Math.max(0.50, o.head_right + 0.01), 0.56) * W;
  const width = 0.955 * W - left;
  const drift = interpolate(frame, [f(o.start), f(o.end)], [0, -26], CLAMP);   // parallax against the camera move
  const card = (k: number, top: number, label: string, value: string, sub: string, start: number, valT: number, accent: string) => {
    const s = f(start);
    const p = pop(frame, s, 17, 150);
    if (frame < s) return null;
    const blur = (1 - ramp(frame, s, s + 7)) * 14;
    const pulse = 1 + 0.07 * Math.exp(-Math.max(0, frame - f(valT)) / 4) * (frame >= f(valT) ? 1 : 0);
    const tr = `translateX(${(1 - p) * 90 + drift}px) scale(${0.93 + 0.07 * p})`;
    return (
      <Glass key={k} layer={layer} on="behind" x={left} y={top * H} w={width} h={0.168 * H} r={38} tone="light" transform={tr} opacity={Math.min(1, p * 1.6)}>
        <div style={{ padding: "30px 34px", fontFamily: SANS, color: "white", filter: `blur(${blur}px)` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, fontWeight: 600, fontSize: 25, letterSpacing: "0.16em", color: "rgba(255,255,255,0.66)" }}>
            <div style={{ width: 12, height: 12, borderRadius: 6, background: accent, boxShadow: `0 0 14px ${accent}` }} />{label}
          </div>
          <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 140, lineHeight: 0.95, marginTop: 10, letterSpacing: "-0.01em",
            transform: `scale(${pulse})`, transformOrigin: "0% 70%" }}>{value}</div>
          <div style={{ fontWeight: 500, fontSize: 28, color: "rgba(255,255,255,0.72)", marginTop: 6 }}>{sub}</div>
        </div>
      </Glass>
    );
  };
  const chipP = pop(frame, f(o.chip), 13, 200);
  return (
    <>
      {card(1, 0.150, "ÎNAINTE", "3 ore", "pe un singur clip", o.card1, o.val1, "#FF8A65")}
      {card(2, 0.335, "ACUM", "15 min", "pe același clip", o.card2, o.val2, "#4ADE80")}
      {layer === "behind" && frame >= f(o.chip) ? (
        <div style={{
          position: "absolute", left: left + 30, top: 0.522 * H, padding: "12px 24px", borderRadius: 30, background: "#4ADE80",
          color: "#052E16", fontFamily: SANS, fontWeight: 800, fontSize: 32, letterSpacing: "-0.01em",
          boxShadow: "0 10px 30px rgba(0,0,0,0.35)", transform: `translateX(${drift}px) scale(${chipP})`, transformOrigin: "0% 50%",
        }}>12× mai rapid</div>
      ) : null}
    </>
  );
};

// ---------------------------------------------------------------- 3. glass graph: 4 -> 20 clips a week
const GlassGraph: React.FC<{ frame: number; layer: LayerKind }> = ({ frame, layer }) => {
  const g = data.graph;
  const s = f(g.start), e = f(g.end);
  if (frame < s || frame >= e) return null;
  const inP = pop(frame, s, 18, 140);
  const outP = 1 - ramp(frame, e - 6, e, Easing.in(Easing.cubic));
  const x = 0.075 * W, y = 0.50 * H, w = 0.85 * W, h = 0.27 * H;
  const tr = `translateY(${(1 - inP) * 120 + (1 - outP) * 40}px) scale(${0.94 + 0.06 * inP})`;
  const op = Math.min(1, inP * 1.6) * outP;
  // count 4 -> 20 between "la" and "20"
  const cp = ramp(frame, f(g.count_start), f(g.count_end), Easing.inOut(Easing.cubic));
  const value = Math.round(4 + 16 * cp);
  const fourPulse = 1 + 0.08 * Math.exp(-Math.max(0, frame - f(g.four)) / 4) * (frame >= f(g.four) ? 1 : 0);
  // line: drawn slowly from "a crescut", shoots up with the count
  const drawn = Math.min(1, 0.32 * ramp(frame, s + 8, f(g.count_start), Easing.inOut(Easing.quad)) + 0.68 * cp);
  const gw = w - 100, gh = 0.125 * H;
  const pts: [number, number][] = [];
  for (let i = 0; i <= 60; i++) {
    const u = i / 60;
    const v = u < 0.32 ? 0 : Math.pow((u - 0.32) / 0.68, 1.7);
    const val = 4 + 16 * v;
    pts.push([u * gw, gh - (val / 20) * 0.92 * gh]);
  }
  const n = Math.max(1, Math.round(drawn * 60));
  const shown = pts.slice(0, n + 1);
  const d = shown.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(" ");
  const last = shown[shown.length - 1];
  const area = `${d} L${last[0].toFixed(1)},${gh} L0,${gh} Z`;
  const chipP = pop(frame, f(g.chip), 13, 210);
  return (
    <Glass layer={layer} on="front" x={x} y={y} w={w} h={h} r={44} tone="light" transform={tr} opacity={op}>
      <div style={{ position: "absolute", left: 46, top: 36, right: 46, fontFamily: SANS, color: "white" }}>
        <div style={{ fontWeight: 600, fontSize: 34, letterSpacing: "-0.01em", color: "rgba(255,255,255,0.86)" }}>Clipuri pe săptămână</div>
        <div style={{ display: "flex", alignItems: "center", gap: 22, marginTop: 4 }}>
          <div style={{ fontWeight: 700, fontSize: 170, lineHeight: 1, letterSpacing: "-0.05em", fontVariantNumeric: "tabular-nums",
            transform: `scale(${fourPulse})`, transformOrigin: "0% 60%", textShadow: "0 6px 30px rgba(0,0,0,0.25)" }}>{value}</div>
          {frame >= f(g.chip) ? (
            <div style={{ padding: "10px 22px", borderRadius: 28, background: "#4ADE80", color: "#052E16", fontWeight: 800, fontSize: 36,
              transform: `scale(${chipP})`, transformOrigin: "0% 50%", boxShadow: "0 8px 24px rgba(0,0,0,0.25)" }}>+400%</div>
          ) : (
            <div style={{ fontWeight: 600, fontSize: 34, color: "rgba(255,255,255,0.72)" }}>{cp < 0.5 ? "înainte" : "acum"}</div>
          )}
        </div>
      </div>
      <svg style={{ position: "absolute", left: 50, bottom: 40, overflow: "visible" }} width={gw} height={gh}>
        <defs>
          <linearGradient id="ga" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#FFFFFF" stopOpacity="0.28" />
            <stop offset="1" stopColor="#FFFFFF" stopOpacity="0" />
          </linearGradient>
        </defs>
        {[0.25, 0.5, 0.75].map((k) => <line key={k} x1={0} x2={gw} y1={gh * k} y2={gh * k} stroke="rgba(255,255,255,0.14)" strokeWidth={1.5} strokeDasharray="6 10" />)}
        <path d={area} fill="url(#ga)" />
        <path d={d} fill="none" stroke="#FFFFFF" strokeWidth={9} strokeLinecap="round" strokeLinejoin="round"
          style={{ filter: "drop-shadow(0 0 10px rgba(255,255,255,0.7))" }} />
        <circle cx={last[0]} cy={last[1]} r={13} fill="#FFFFFF" style={{ filter: "drop-shadow(0 0 16px rgba(255,255,255,0.95))" }} />
      </svg>
    </Glass>
  );
};

// ---------------------------------------------------------------- big top words (reference style)
const TopWords: React.FC<{ frame: number }> = ({ frame }) => (
  <>
    {data.top.map((tw, i) => {
      const s = f(tw.start), e = f(tw.end);
      if (frame < s || frame >= e) return null;
      const fc: Box = segAt(frame).face;
      const hairTop = (fc[1] - 0.28 * fc[3]) * H;
      const bottom = Math.max(hairTop - 18, 0.25 * H);
      const p = ramp(frame, s, s + 5);
      const out = 1 - ramp(frame, e - 5, e, Easing.in(Easing.quad));
      const sp = tw.sub && tw.sub_start ? ramp(frame, f(tw.sub_start), f(tw.sub_start) + 5) : 0;
      return (
        <div key={i} style={{ position: "absolute", left: 0, right: 0, top: bottom, transform: "translateY(-100%)", textAlign: "center" }}>
          <div style={{
            display: "inline-block", position: "relative", fontFamily: SANS, fontWeight: 700, fontSize: 205, lineHeight: 0.9,
            letterSpacing: "-0.055em", color: "white", textShadow: "0 6px 30px rgba(0,0,0,0.40)", whiteSpace: "nowrap",
            opacity: p * out, filter: `blur(${(1 - p) * 12}px)`, transform: `scale(${1.06 - 0.06 * p})`,
          }}>
            {tw.text}
            {tw.sub ? (
              <div style={{
                position: "absolute", right: -18, bottom: -62, fontFamily: SERIF, fontStyle: "italic", fontWeight: 400,
                fontSize: 104, letterSpacing: "-0.01em", transform: `rotate(-5deg) translateY(${(1 - sp) * 14}px)`, opacity: sp,
                filter: `blur(${(1 - sp) * 8}px)`,
              }}>{tw.sub}</div>
            ) : null}
          </div>
        </div>
      );
    })}
  </>
);

// ---------------------------------------------------------------- 4. tier list built under the face
const TIER_COLORS: Record<string, string> = { S: "#FF6B6B", A: "#FF9F45", B: "#FFD24C", C: "#7BE08A", D: "#6CB8FF" };
const TierList: React.FC<{ frame: number; layer: LayerKind }> = ({ frame, layer }) => {
  const tl = data.tier;
  const s = f(tl.start), e = f(tl.end);
  if (frame < s || frame >= e) return null;
  const x = 0.07 * W, y = 0.445 * H, w = 0.86 * W, h = 0.29 * H;
  const inP = pop(frame, s, 17, 150);
  const outP = 1 - ramp(frame, e - 8, e, Easing.in(Easing.cubic));
  const tr = `translateY(${(1 - inP) * 90 + (1 - outP) * 60}px) scale(${0.95 + 0.05 * inP})`;
  const rows = ["S", "A", "B", "C", "D"];
  const pad = 20, gap = 9, rh = (h - 2 * pad - 4 * gap) / 5;
  const fc: Box = tl.face;
  const faceCx = (fc[0] + fc[2] / 2) * W - x, faceCy = (fc[1] + fc[3] * 0.6) * H - y;
  const t = frame / FPS;
  return (
    <Glass layer={layer} on="front" x={x} y={y} w={w} h={h} r={40} tone="dark" transform={tr} opacity={Math.min(1, inP * 1.5) * outP}>
      <div style={{ position: "absolute", inset: 0, background: "rgba(8,9,8,0.42)" }} />
      {rows.map((r, i) => {
        const ry = pad + i * (rh + gap);
        const rowIn = ramp(frame, s + 3 + i * 2, s + 9 + i * 2);
        const drop = tl.drops.find((d) => d.tier === r)!;
        const land = f(drop.t) + 6;                                  // tile leaves at the word, lands ~0.2 s later
        const fly = frame >= f(drop.t) ? spring({ frame: frame - f(drop.t), fps: FPS, config: { damping: 13, stiffness: 120, mass: 0.8 } }) : 0;
        const tileX0 = faceCx - 40, tileY0 = faceCy - ry - 40;
        const tileX = pad + rh + 22, tileY = (rh - 72) / 2;
        const tx = tileX0 + (tileX - tileX0) * fly, ty = tileY0 + (tileY - tileY0) * fly;
        const flash = frame >= land ? Math.exp(-(frame - land) / 5) : 0;
        const nameP = ramp(frame, land - 1, land + 6);
        const suspense = r === "D" && t >= tl.suspense && t < drop.t ? 0.5 + 0.5 * Math.sin((t - tl.suspense) * 14) : 0;
        return (
          <div key={r} style={{ position: "absolute", left: pad, top: ry, width: w - 2 * pad, height: rh, opacity: rowIn, transform: `translateX(${(1 - rowIn) * -30}px)` }}>
            <div style={{
              position: "absolute", left: 0, top: 0, width: rh, height: rh, borderRadius: 20, background: TIER_COLORS[r],
              display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 900, fontSize: 52,
              color: "#141414", boxShadow: `0 0 ${flash * 40}px ${TIER_COLORS[r]}`, filter: `brightness(${1 + flash * 0.35})`,
            }}>{r}</div>
            <div style={{
              position: "absolute", left: rh + 12, top: 0, right: 0, height: rh, borderRadius: 20,
              background: `rgba(255,255,255,${0.055 + suspense * 0.08 + flash * 0.08})`, border: "1px solid rgba(255,255,255,0.08)",
            }} />
            {frame >= f(drop.t) ? (
              <>
                <div style={{
                  position: "absolute", left: tx, top: ty, width: 72, height: 72, borderRadius: 18, background: drop.bg,
                  display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 8px 22px rgba(0,0,0,0.35)",
                  transform: `scale(${0.6 + 0.4 * fly}) rotate(${(1 - fly) * -14}deg)`,
                  border: drop.bg === "#0D0D0D" ? "1.5px solid rgba(255,255,255,0.18)" : "none",
                }}>
                  <Img src={staticFile(`logos/${drop.logo}`)} style={{ width: 46, height: 46 }} />
                </div>
                <div style={{
                  position: "absolute", left: tileX + 72 + 22, top: 0, height: rh, display: "flex", alignItems: "center", gap: 14,
                  fontFamily: SANS, fontWeight: 600, fontSize: 38, letterSpacing: "-0.015em", color: "white",
                  opacity: nameP, transform: `translateX(${(1 - nameP) * -12}px)`,
                }}>
                  {drop.name}
                  {r === "S" ? <span style={{ fontSize: 24, fontWeight: 800, color: "#141414", background: "#FFD24C", borderRadius: 14, padding: "5px 12px" }}>#1</span> : null}
                </div>
              </>
            ) : null}
          </div>
        );
      })}
    </Glass>
  );
};

// ---------------------------------------------------------------- 5. freeze frame tag (the cut-out sticker itself is made in the compositor)
const FreezeTag: React.FC<{ frame: number }> = ({ frame }) => {
  const z = data.freeze;
  const s = f(z.start) + 5, e = f(z.end);
  if (frame < s || frame >= e) return null;
  const p = pop(frame, s, 11, 190);
  const p2 = pop(frame, s + 7, 14, 190);
  return (
    <div style={{ position: "absolute", right: 46, top: 0.585 * H, display: "flex", flexDirection: "column", alignItems: "flex-end" }}>
      <div style={{
        display: "inline-block", padding: "14px 34px 20px", borderRadius: 26, background: "#FFFFFF", color: "#0B0B0B",
        fontFamily: SERIF, fontStyle: "italic", fontSize: 104, lineHeight: 1, letterSpacing: "-0.015em",
        boxShadow: "0 18px 40px rgba(0,0,0,0.45), 0 0 0 7px rgba(255,255,255,0.35)",
        transform: `rotate(${-4 - (1 - p) * 10}deg) scale(${0.55 + 0.45 * p})`, transformOrigin: "80% 50%", opacity: Math.min(1, p * 2),
      }}>{z.tag}</div>
      <div style={{
        marginTop: 18, marginRight: 18, display: "inline-flex", alignItems: "center", gap: 10, padding: "12px 20px", borderRadius: 22,
        background: "rgba(10,10,10,0.72)", color: "white", fontFamily: SANS, fontWeight: 600, fontSize: 28, letterSpacing: "-0.01em",
        transform: `rotate(-2deg) scale(${p2})`, transformOrigin: "100% 50%", opacity: Math.min(1, p2 * 2), whiteSpace: "nowrap",
      }}>{z.sub} <span style={{ fontSize: 30 }}>↓</span></div>
    </div>
  );
};

// ---------------------------------------------------------------- 6. colour grade chips (the wipe itself is in the compositor)
const GradeChips: React.FC<{ frame: number }> = ({ frame }) => {
  const g = data.grade;
  const t = frame / FPS;
  if (t < g.log_start || t >= g.end) return null;
  const chip = (text: string, sub: string, s: number, e: number, accent: string) => {
    if (frame < s || frame >= e) return null;
    const p = pop(frame, s, 16, 190);
    const out = 1 - ramp(frame, e - 5, e, Easing.in(Easing.quad));
    return (
      <div style={{
        position: "absolute", top: 0.155 * H, left: W / 2, transform: `translate(-50%, -50%) scale(${0.85 + 0.15 * p})`,
        opacity: Math.min(1, p * 1.6) * out, display: "flex", alignItems: "center", gap: 16, padding: "18px 34px",
        borderRadius: 44, background: "rgba(12,12,12,0.68)", border: "1.5px solid rgba(255,255,255,0.22)",
        fontFamily: SANS, color: "white", whiteSpace: "nowrap", boxShadow: "0 10px 30px rgba(0,0,0,0.3)",
      }}>
        <div style={{ width: 18, height: 18, borderRadius: 9, background: accent, boxShadow: `0 0 18px ${accent}` }} />
        <span style={{ fontWeight: 700, fontSize: 42, letterSpacing: "-0.015em" }}>{text}</span>
        <span style={{ fontWeight: 500, fontSize: 34, color: "rgba(255,255,255,0.72)" }}>{sub}</span>
      </div>
    );
  };
  return (
    <>
      {chip("Original", "Apple Log, spălat", f(g.log_start) + 4, f(g.wipe_start), "#A3A3A3")}
      {chip("După", "color grade cu AI", f(g.wipe_end) - 2, f(g.end), "#FFB547")}
    </>
  );
};

// ---------------------------------------------------------------- end card
const Cta: React.FC<{ frame: number; layer: LayerKind }> = ({ frame, layer }) => {
  const c = data.cta;
  const s = f(c.start);
  if (frame < s) return null;
  const p = pop(frame, s, 17, 140);
  const x = 0.06 * W, y = 0.515 * H, w = 0.88 * W, h = 0.25 * H;
  return (
    <Glass layer={layer} on="front" x={x} y={y} w={w} h={h} r={44} tone="dark" transform={`translateY(${(1 - p) * 80}px) scale(${0.94 + 0.06 * p})`} opacity={Math.min(1, p * 1.5)}>
      <div style={{ position: "absolute", inset: 0, background: "rgba(8,9,8,0.35)" }} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 46, textAlign: "center", fontFamily: SANS, color: "white" }}>
        <div style={{ fontWeight: 700, fontSize: 60, letterSpacing: "-0.035em", lineHeight: 1.0 }}>Care efect a fost</div>
        <div style={{ fontFamily: SERIF, fontStyle: "italic", fontWeight: 400, fontSize: 92, lineHeight: 1.0, marginTop: 2 }}>cel mai tare?</div>
        <div style={{ display: "flex", justifyContent: "center", gap: 18, marginTop: 30 }}>
          {[1, 2, 3, 4, 5, 6].map((n, i) => {
            const k = pop(frame, s + 6 + i * 3, 12, 220);
            return (
              <div key={n} style={{
                width: 104, height: 104, borderRadius: 52, background: "rgba(255,255,255,0.14)", border: "2px solid rgba(255,255,255,0.40)",
                display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: 50, transform: `scale(${k})`,
              }}>{n}</div>
            );
          })}
        </div>
        <div style={{ marginTop: 28, fontWeight: 600, fontSize: 36, color: "rgba(255,255,255,0.82)" }}>Scrie numărul în comentarii ↓</div>
      </div>
    </Glass>
  );
};

export const Layer: React.FC<{ layer: LayerKind }> = ({ layer }) => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: layer === "mask" ? "#000000" : undefined }}>
      {layer === "behind" ? <BehindWords frame={frame} /> : null}
      <OtsCards frame={frame} layer={layer} />
      <GlassGraph frame={frame} layer={layer} />
      <TierList frame={frame} layer={layer} />
      <Cta frame={frame} layer={layer} />
      {layer === "front" ? (
        <>
          <TopWords frame={frame} />
          <FreezeTag frame={frame} />
          <GradeChips frame={frame} />
          <Captions frame={frame} />
          <Pills frame={frame} />
        </>
      ) : null}
    </AbsoluteFill>
  );
};
