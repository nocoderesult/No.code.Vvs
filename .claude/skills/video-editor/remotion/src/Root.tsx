import { Composition } from "remotion";
import { Reel } from "./Reel";

export const RemotionRoot: React.FC = () => {
  return <Composition id="Reel" component={Reel} durationInFrames={315} fps={30} width={1080} height={1920} />;
};
