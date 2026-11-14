import wave,subprocess,re,json,numpy as np
from align import ch,UNITS,syl,WAV,DUR
# blok manual (unit_awal, unit_akhir_eksklusif, chunk_awal, chunk_akhir_eksklusif), diverifikasi dari durasi vs suku kata
import json as _j
WT=_j.load(open('wtimes.json'))['times']
w=wave.open(WAV);sr=w.getframerate();n=w.getnframes();x=np.frombuffer(w.readframes(n),dtype=np.int16);dur=n/sr
chunks=ch
removed=[]
for i in range(1,len(chunks)):
    a,b=chunks[i-1][1],chunks[i][0]
    if b-a>0.70:
        cut=(b-a)-0.55;mid=(a+b)/2;removed.append((mid-cut/2,mid+cut/2))
keep=[];p=0.0
for a,b in removed: keep.append((p,a));p=b
keep.append((p,dur))
y=np.concatenate([x[int(a*sr):int(b*sr)] for a,b in keep])
def mp(t):
    d=0.0
    for a,b in removed:
        if t>=b: d+=b-a
        elif t>a: d+=t-a
    return t-d
ww=wave.open("clean_raw.wav","wb");ww.setnchannels(1);ww.setsampwidth(2);ww.setframerate(sr);ww.writeframes(y.tobytes());ww.close()
subprocess.run(["ffmpeg","-loglevel","error","-y","-i","clean_raw.wav","-af","loudnorm=I=-14:TP=-1.5:LRA=11","-ar","44100","-ac","1","vo_clean.wav"],check=True)
out=[];k=0
for ui,u in enumerate(UNITS):
    n=len(u['text'].split());ws=[]
    for wd in u['text'].split():
        a0,a1=WT[k];k+=1
        ws.append({"w":wd,"start":round(mp(a0),3),"end":round(mp(a1),3)})
    # akhir kata tidak boleh melewati awal kata berikut
    for q in range(len(ws)-1): ws[q]["end"]=min(ws[q]["end"],max(ws[q+1]["start"],ws[q]["start"]+0.05))
    parts=[ws] if len(ws)<=7 else [ws[:(len(ws)+1)//2],ws[(len(ws)+1)//2:]]
    if any(len(p)>7 for p in parts):
        kk=(len(ws)+2)//3;parts=[ws[:kk],ws[kk:2*kk],ws[2*kk:]]
    phr=[{"text":' '.join(a['w'] for a in pp),"words":pp,"start":pp[0]["start"],"end":pp[-1]["end"]} for pp in parts]
    out.append({"unit":ui,"sent_end":u['end']=='.',"phrases":phr,"start":phr[0]["start"],"end":phr[-1]["end"]})
assert k==len(WT)
w2=wave.open("vo_clean.wav");sr2=w2.getframerate();z=np.frombuffer(w2.readframes(w2.getnframes()),dtype=np.int16).astype(float)/32768
fd=len(z)/sr2;nf=int(fd*30)+2;mouth=[]
for f in range(nf):
    c=int(f/30*sr2);s=z[max(0,c-int(0.02*sr2)):c+int(0.02*sr2)]
    mouth.append(float(np.sqrt(np.mean(s**2))) if len(s) else 0.0)
m=np.array(mouth);ref=np.percentile(m,95)+1e-9;m=np.clip(m/ref,0,1.2)
json.dump({"dur":fd,"groups":out,"mouth":[round(float(v),3) for v in m]},open("timing.json","w"),ensure_ascii=False)
print("asli",round(dur,2),"-> bersih",round(fd,2),"grup",len(out))
for i,g in enumerate(out): print(i,round(g['start'],2),round(g['end'],2),'|',' || '.join(p['text'] for p in g['phrases'])[:70])
