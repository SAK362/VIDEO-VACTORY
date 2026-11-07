export type Callout = {text: string; target?: string};
export type DataCard = {value: string; caption: string} | null;

export type Scene = {
  id?: string | number;
  type: string;
  label?: string;
  heading?: string;
  narration_ref?: string;
  set?: string;
  focus?: string;
  camera?: string;
  curio?: string | null;
  flow?: string | null;
  callouts?: Callout[];
  data_card?: DataCard;
};

export type VideoProps = {
  title: string;
  narration: string;
  scenes: Scene[];
  lang: 'en' | 'id';
  audioSeconds: number;
  audioFile: string;
  project?: string;
  style?: 'toon' | 'real';
};

export type TimedScene = Scene & {from: number; dur: number};
export type Token = {text: string; hi: boolean};
export type Phrase = {tokens: Token[]; from: number; to: number; wordFrames: number[]};
