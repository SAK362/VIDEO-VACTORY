import {Config} from '@remotion/cli/config';

// Server GitHub tidak punya GPU: 3D dirender lewat software (SwiftShader/ANGLE).
Config.setChromiumOpenGlRenderer('swangle');
Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
