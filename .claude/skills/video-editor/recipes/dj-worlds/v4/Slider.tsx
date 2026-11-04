import React from "react";
import { interpolate, spring } from "remotion";

// A before/after comparison slider pulled by a finger: a thin divider with a round handle (‹ ›).
// Each drag springs from the previous target to the next (one small overshoot, then it settles), the handle dips
// while pressed and a soft halo shows the finger. A horizontal blur scaled to the speed stands in for motion blur.

export type Drag = { at: number; to: number };
export type Press = [number, number, number, number]; // grab starts, fully pressed, release starts, released

const SPRING = { damping: 12.5, mass: 1, stiffness: 80 }; // zeta ~0.7: ~11 frames to the target, ~5% overshoot
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

export const sliderX = (t: number, fps: number, drags: Drag[], start = 0) => {
  let x = start;
  let prev = start;
  for (const d of drags) {
    x += (d.to - prev) * spring({ frame: t - d.at, fps, config: SPRING });
    prev = d.to;
  }
  return x;
};

export const pressAt = (t: number, presses: Press[]) =>
  Math.max(0, ...presses.map((p) => interpolate(t, p, [0, 1, 1, 0], clamp)));

export const ComparisonHandle: React.FC<{
  x: number; vx: number; y: number; press: number; appear: number; arrows?: string; size?: number;
}> = ({ x, vx, y, press, appear, arrows = "#121212", size = 108 }) => {
  const r = size / 2;
  const blur = Math.min(24, Math.abs(vx) * 0.22); // half-frame shutter as a gaussian
  return (
    <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id="slider-motion-blur" x="-20%" y="0%" width="140%" height="100%">
          <feGaussianBlur stdDeviation={`${blur.toFixed(2)} 0`} />
        </filter>
      </svg>
      <div style={{ position: "absolute", inset: 0, opacity: appear, filter: blur > 0.35 ? "url(#slider-motion-blur)" : undefined }}>
        <div style={{
          position: "absolute", left: x - 2.5, top: 0, width: 5, height: 1920, background: "#FFFFFF",
          boxShadow: "0 0 12px rgba(0,0,0,0.20), 0 0 2px rgba(0,0,0,0.16)",
        }} />
        <div style={{
          position: "absolute", left: x - r * 1.6, top: y - r * 1.6, width: r * 3.2, height: r * 3.2, borderRadius: "50%",
          background: "rgba(255,255,255,0.18)", border: "2px solid rgba(255,255,255,0.5)",
          opacity: press, transform: `scale(${0.72 + 0.28 * press})`,
        }} />
        <div style={{
          position: "absolute", left: x - r, top: y - r, width: size, height: size, borderRadius: "50%", background: "#FFFFFF",
          boxShadow: "0 10px 30px rgba(0,0,0,0.30), 0 2px 8px rgba(0,0,0,0.20)",
          transform: `scale(${(0.6 + 0.4 * appear) * (1 - 0.08 * press)})`,
        }}>
          <svg width={size} height={size} viewBox="0 0 108 108" style={{ display: "block" }}>
            <g fill="none" stroke={arrows} strokeWidth={6.5} strokeLinecap="round" strokeLinejoin="round">
              <path d="M45 40 L32 54 L45 68" />
              <path d="M63 40 L76 54 L63 68" />
            </g>
          </svg>
        </div>
      </div>
    </div>
  );
};
