import { Composition } from "remotion";
import { Layer } from "./Reel3";
import data from "./data.json";

// Three transparent layers composited in Python over the 4K plate:
//   Behind = things the person stands in front of, Front = everything else,
//   Masks  = where the plate gets frosted (red = behind glass, green = front glass).
export const RemotionRoot: React.FC = () => {
  const common = { durationInFrames: data.n, fps: 30, width: 1080, height: 1920 };
  return (
    <>
      <Composition id="Front" component={Layer} defaultProps={{ layer: "front" as const }} {...common} />
      <Composition id="Behind" component={Layer} defaultProps={{ layer: "behind" as const }} {...common} />
      <Composition id="Masks" component={Layer} defaultProps={{ layer: "mask" as const }} {...common} />
    </>
  );
};
