import React from "react";
import { FONTS } from "./v3fonts";

// The only text in the reel. Static, two lines, upper third; one accent colour on the key words (taste: one accent per
// frame, key words in the accent colour). Line 1 near-black for legibility on the white wall, "piesa asta?" in orange
// so the question already carries the colour of the fire that the touch will trigger.
export type QuestionStyle = {
  font: string; weight: number; size: number; tracking: string; lineHeight: number;
  ink: string; accent: string; top: number; upper?: boolean;
};
export const Question: React.FC<{ s: QuestionStyle; lines: [string, string] }> = ({ s, lines }) => {
  const t = (x: string) => (s.upper ? x.toLocaleUpperCase("ro-RO") : x);
  return (
    <div style={{
      position: "absolute", top: s.top, left: 0, width: 1080, textAlign: "center", fontFamily: FONTS[s.font] ?? s.font,
      fontWeight: s.weight, fontSize: s.size, lineHeight: s.lineHeight, letterSpacing: s.tracking,
      fontFeatureSettings: '"ss01" 0, "kern" 1',
    }}>
      <div style={{ color: s.ink }}>{t(lines[0])}</div>
      <div style={{ color: s.accent }}>{t(lines[1])}</div>
    </div>
  );
};
