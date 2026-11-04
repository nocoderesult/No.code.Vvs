import React from "react";
import { Audio, Video } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile, useVideoConfig } from "remotion";
import { Question, QuestionStyle } from "./V3Question";
import "./v3fonts";

// DJ reel V3 - "Știi unde mă duce piesa asta?"
// Editable timeline (Remotion best practices): every clip is its own JSX node with literal timing props, so each one
// can be trimmed or moved in the Studio. One continuous passage of the track drives every cut (126.045 BPM,
// 14.28 frames per beat, frame 0 = bar A downbeat). The deck never moves: the white room is the real take placed on the
// AI deck axis, every world changes around the same booth.
//
//   0-56    white room + the question        touch on the mixer = cut on beat 4 (bar B downbeat)
//   57-99   fire (match on the hand landing)  cut to blue on beat 7 (the bass hit before the break)
//   100-170 blue: stand, prepare, lift, hold  only the track; cut on the drop's first kick (beat 12)
//   171-327 red smoke -> the source's own fog/water transition, uncut
//   328-399 rails, vanishing point behind     ends on the bar-H downbeat (beat 28)

export const QUESTION: QuestionStyle = {
  font: "Geist", weight: 700, size: 92, tracking: "-0.03em", lineHeight: 1.02, ink: "#111111", accent: "#FF5A1F", top: 372,
};

export const ReelV3: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Video name="Camera albă" src={staticFile("v3/white_plate.mp4")} trimBefore={0} durationInFrames={57} premountFor={fps} muted />
      <Sequence name="Întrebarea" from={0} durationInFrames={57} premountFor={fps}>
        <Question s={QUESTION} lines={["Știi unde mă duce", "piesa asta?"]} />
      </Sequence>
      <Video name="Foc" src={staticFile("v3/ai_master.mp4")} trimBefore={8} from={57} durationInFrames={43} premountFor={fps} muted />
      <Video name="Albastru + ridicarea" src={staticFile("v3/ai_master.mp4")} trimBefore={76} from={100} durationInFrames={71} premountFor={fps} muted />
      <Video name="Roșu → apă" src={staticFile("v3/ai_master.mp4")} trimBefore={182} from={171} durationInFrames={157} premountFor={fps} muted />
      <Video name="Șine" src={staticFile("v3/ai_master.mp4")} trimBefore={351} from={328} durationInFrames={72} premountFor={fps} muted />

      <Audio name="Piesa" src={staticFile("v3/song_v3.wav")} />
      <Audio name="SFX aprindere" src={staticFile("v3/sfx/ignition.wav")} from={57} volume={0.22} />
      <Audio name="SFX foșnet foaie" src={staticFile("v3/sfx/rustle.wav")} from={97} volume={0.3} />
      <Audio name="SFX apă" src={staticFile("v3/sfx/water.wav")} from={266} volume={0.13} />
    </AbsoluteFill>
  );
};

// Preview of the alternative white -> fire timing: the cut follows the touch at 1.67 s (the "and" of beat 3).
export const V3TouchPreview: React.FC = () => {
  const { fps } = useVideoConfig();
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <Video name="Camera albă" src={staticFile("v3/white_plate.mp4")} trimBefore={7} durationInFrames={50} premountFor={fps} muted />
      <Sequence name="Întrebarea" from={0} durationInFrames={50} premountFor={fps}>
        <Question s={QUESTION} lines={["Știi unde mă duce", "piesa asta?"]} />
      </Sequence>
      <Video name="Foc" src={staticFile("v3/ai_master.mp4")} trimBefore={8} from={50} durationInFrames={50} premountFor={fps} muted />
      <Video name="Albastru" src={staticFile("v3/ai_master.mp4")} trimBefore={76} from={100} durationInFrames={5} premountFor={fps} muted />
      <Audio name="Piesa" src={staticFile("v3/song_v3.wav")} />
      <Audio name="SFX aprindere" src={staticFile("v3/sfx/ignition.wav")} from={50} volume={0.22} />
      <Audio name="SFX foșnet foaie" src={staticFile("v3/sfx/rustle.wav")} from={97} volume={0.3} />
    </AbsoluteFill>
  );
};
