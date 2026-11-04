import React from "react";
import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// The V2 type the creator picked: Instrument Serif Italic, ink on the white wall, the key words in V2's ember orange.
const LATIN = "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD";
const LATIN_EXT = "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, U+A720-A7FF";
loadFont({ family: "Instrument Serif", url: staticFile("fonts/isi-latin.woff2"), weight: "400", style: "italic", unicodeRange: LATIN });
loadFont({ family: "Instrument Serif", url: staticFile("fonts/isi-latinext.woff2"), weight: "400", style: "italic", unicodeRange: LATIN_EXT });
export const EMBER = "#FF6A1A";

export const QuestionV2: React.FC<{ top?: number }> = ({ top = 296 }) => (
  <div style={{ position: "absolute", top, left: 0, width: 1080, textAlign: "center", fontFamily: "Instrument Serif", fontStyle: "italic", fontWeight: 400 }}>
    <div style={{ fontSize: 118, lineHeight: 1, letterSpacing: "-0.02em", color: "#121212" }}>Știi unde mă duce</div>
    <div style={{
      fontSize: 142, lineHeight: 1, letterSpacing: "-0.025em", color: EMBER, marginTop: 4,
      textShadow: "0 0 22px rgba(255,106,26,0.35), 0 0 60px rgba(255,90,10,0.18)",
    }}>piesa asta?</div>
  </div>
);
