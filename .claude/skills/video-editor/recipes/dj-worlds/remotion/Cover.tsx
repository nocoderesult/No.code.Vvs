import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";

// Cover in the same type system as the reel: mono label + Instrument Serif Italic, one ember accent.
// Text sits inside the 3:4 profile-grid crop (y 240..1680).
export const Cover: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Img src={staticFile("cover_bg.png")} style={{ width: "100%", height: "100%" }} />
    <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.62) 0%, rgba(0,0,0,0.38) 22%, rgba(0,0,0,0) 40%)" }} />
    <div style={{
      position: "absolute", top: 318, left: 0, width: 1080, textAlign: "center", fontFamily: "JetBrains Mono", fontWeight: 500,
      fontSize: 32, letterSpacing: "0.34em", paddingLeft: "0.34em", color: "rgba(244,241,234,0.92)", textShadow: "0 2px 14px rgba(0,0,0,0.5)",
    }}>1 TAKE  ·  5 LUMI</div>
    <div style={{
      position: "absolute", top: 384, left: 0, width: 1080, textAlign: "center", fontFamily: "Instrument Serif", fontStyle: "italic",
      fontSize: 168, lineHeight: 1, letterSpacing: "-0.02em", color: "#F4F1EA", textShadow: "0 6px 40px rgba(0,0,0,0.55)",
    }}>
      Restul e <span style={{ color: "#FF6A1A", textShadow: "0 0 30px rgba(255,106,26,0.7), 0 0 80px rgba(255,90,10,0.35)" }}>AI</span>.
    </div>
  </AbsoluteFill>
);
