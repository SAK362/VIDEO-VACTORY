import React from "react";
import { Composition } from "remotion";
import { EP02 } from "./ep02/EP02";
import { TOTAL_FRAMES as FRAMES_EP02 } from "./ep02/timing";

export const Root: React.FC = () => (
  <>
    <Composition id="EP02" component={EP02} durationInFrames={FRAMES_EP02} fps={30} width={1080} height={1920} />
  </>
);
