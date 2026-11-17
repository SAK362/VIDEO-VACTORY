import sys,json,re,difflib
sys.path.insert(0,'/home/claude/video-vactory/webgl')
from align_whisper import align_tokens,norm
d=json.load(open('/home/claude/video-vactory/beyourbest/align/0002_heard.json'))
heard=[tuple(x) for x in d['words']]
toks=open('/home/claude/video-vactory/beyourbest/align/0002_narasi.txt',encoding='utf-8').read().split()
times,ratio=align_tokens(toks,heard,d['duration'])
print('tokens',len(toks),'heard',len(heard),'cocok',round(ratio,3))
json.dump({'toks':toks,'times':times},open('wtimes.json','w'),ensure_ascii=False)
# selisih kata naskah vs terdengar (per kata)
a=[norm(t) for t in toks];b=[norm(w) for w,_,_ in heard]
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
for op,i1,i2,j1,j2 in sm.get_opcodes():
    if op!='equal': print(op,toks[i1:i2],'->',[h[0] for h in heard[j1:j2]],'@',[round(h[1],2) for h in heard[j1:j2]][:2])
