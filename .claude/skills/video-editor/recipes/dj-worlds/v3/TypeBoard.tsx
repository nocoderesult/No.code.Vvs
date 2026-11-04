import React from "react";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Video } from "@remotion/media";
import { Question, QuestionStyle } from "./V3Question";

// Font audition: the real white-room frame with one question style (props), rendered as a still.
export const TypeBoard: React.FC<{ s: QuestionStyle }> = ({ s }) => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Sequence from={0} durationInFrames={1}>
      <Video src={staticFile("v3/white_plate.mp4")} trimBefore={30} muted style={{ width: "100%", height: "100%" }} />
    </Sequence>
    <Question s={s} lines={["Știi unde mă duce", "piesa asta?"]} />
  </AbsoluteFill>
);
