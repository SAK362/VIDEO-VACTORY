import re,subprocess,math,json
from units import UNITS
WAV="/mnt/user-data/uploads/82a7abe8-vo-1794658150956.wav"
DUR=113.683833
o=subprocess.run(["ffmpeg","-hide_banner","-i",WAV,"-af","silencedetect=noise=-35dB:d=0.10","-f","null","-"],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",o)]
en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",o)]
ch=[];t=0.0
for s,e in zip(st,en):
    if s>t+0.03: ch.append((t,s))
    t=e
if t<DUR-0.03: ch.append((t,DUR))
N=len(ch);U=len(UNITS)
def syl(wd):
    c=re.sub(r"[^a-z]","",wd.lower())
    return max(1,len(re.findall(r"[aeiou]+",c)))+(0.35 if re.search(r"[bcdfghjklmnpqrstvwxyz]{2}$",c) else 0)
usyl=[sum(syl(w)+0.25 for w in u['text'].split()) for u in UNITS]
speech=sum(b-a for a,b in ch);rate=speech/sum(usyl)
gap=[ch[i+1][0]-ch[i][1] for i in range(N-1)]
INF=1e9
KMAX=6;MMAX=3
dp=[[INF]*(N+1) for _ in range(U+1)];bk=[[None]*(N+1) for _ in range(U+1)]
dp[0][0]=0.0
def bcost(u,c):  # batas sebelum chunk c, unit u-1 berakhir
    if c==0: return 0.0
    g=gap[c-1]
    if UNITS[u-1]['end']=='.': return max(0,0.55-g)*6
    return max(0,0.25-g)*2
for u in range(U+1):
    for c in range(N+1):
        p=dp[u][c]
        if p>=INF: continue
        for k in range(1,KMAX+1):
            if u+k>U: break
            ex=sum(usyl[u:u+k])*rate
            for m in range(1,MMAX+1):
                if c+m>N: break
                sp=sum(ch[i][1]-ch[i][0] for i in range(c,c+m))
                cc=3.0*abs(math.log(max(sp,0.05)/ex))+sum(0.5*(gap[i]/0.25)**2 for i in range(c,c+m-1))
                cc+=bcost(u,c)+0.15*(k-1)
                if p+cc<dp[u+k][c+m]: dp[u+k][c+m]=p+cc;bk[u+k][c+m]=(u,c)
blocks=[];u,c=U,N
while u>0:
    pu,pc=bk[u][c];blocks.append((pu,u,pc,c));u,c=pu,pc
blocks.reverse()
if __name__=='__main__':
    print(N,'chunks',U,'units rate',round(rate,3),'cost',round(dp[U][N],1))
    for (u0,u1,c0,c1) in blocks:
        sp=sum(ch[i][1]-ch[i][0] for i in range(c0,c1));ex=sum(usyl[u0:u1])*rate
        print(f"u{u0:2d}-{u1-1:2d} ch{c0:2d}-{c1-1:2d} {ch[c0][0]:6.2f}-{ch[c1-1][1]:6.2f} sp {sp:4.2f} exp {ex:4.2f} | {' / '.join(UNITS[i]['text'][:22] for i in range(u0,u1))}")
