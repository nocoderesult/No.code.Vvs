import React from "react";
import { Composition } from "remotion";
import { Overlay } from "./Overlay";
import { Cover } from "./Cover";
import plan from "./plan.json";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Overlay" component={Overlay} durationInFrames={plan.frames} fps={plan.fps} width={plan.w} height={plan.h} />
    <Composition id="Cover" component={Cover} durationInFrames={1} fps={plan.fps} width={plan.w} height={plan.h} />
  </>
);
