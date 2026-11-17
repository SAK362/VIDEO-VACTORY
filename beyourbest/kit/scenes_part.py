# ---------- adegan 0002 ----------
def wfind(u,wd,nth=0):
    k=0
    for p in GR[u]['phrases']:
        for w in p['words']:
            if w['w'].strip(',.?!:“”').lower()==wd:
                if k==nth: return w['start']
                k+=1
    return gs(u)
SU=[0,1,4,6,8,10,13,14,17,19,21,23,25,28,31,36,38]
ST=[0.0]+[gs(u)-0.08 for u in SU[1:]]
def sidx(t):
    i=0
    for k,s0 in enumerate(ST):
        if t>=s0: i=k
    return i,t-ST[i]
def cls():
    o='<defs><linearGradient id="fl2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c9955f"/><stop offset="1" stop-color="#8a5a38"/></linearGradient></defs>'
    o+='<rect x="-320" y="-80" width="1720" height="1090" fill="#e9eef0"/><rect x="-320" y="1000" width="1720" height="1000" fill="url(#fl2)"/><rect x="-320" y="990" width="1720" height="20" fill="#7a4a2c"/>'
    return o
def outdoor():
    o='<defs><linearGradient id="sk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bfe3f2"/><stop offset="1" stop-color="#eaf6ef"/></linearGradient><linearGradient id="gr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8cc98a"/><stop offset="1" stop-color="#5a9a62"/></linearGradient></defs>'
    o+='<rect x="-320" y="-80" width="1720" height="1090" fill="url(#sk)"/><ellipse cx="900" cy="560" rx="70" ry="70" fill="#fff3b0" opacity="0.9"/>'
    o+=f'<g fill="#fff" opacity="0.9"><ellipse cx="{200+30*math.sin(CT*0.3):.0f}" cy="520" rx="90" ry="30"/><ellipse cx="{260+30*math.sin(CT*0.3):.0f}" cy="505" rx="60" ry="28"/></g>'
    o+='<path d="M-100 1000 C200 930 420 960 640 985 C860 1005 1000 960 1200 940 L1200 1900 L-100 1900Z" fill="url(#gr)"/>'
    return o
def board():
    s='<rect x="300" y="430" width="480" height="250" rx="14" fill="#5b3a22"/><rect x="314" y="444" width="452" height="222" rx="8" fill="#2f5d4a"/>'
    s+='<path d="M350 520 q30 -24 60 0 t60 0 M350 580 h160 M350 620 h110 M600 500 l70 60 M670 500 l-70 60" stroke="#e8efe9" stroke-width="6" fill="none" stroke-linecap="round" opacity="0.85"/>'
    return s+'<rect x="320" y="680" width="440" height="10" fill="#8a5a3a"/>'
def desk(x,y,mark='#d9442f',w=300,paper='#fff'):
    return (f'<ellipse cx="{x}" cy="{y+70}" rx="{w*0.62:.0f}" ry="16" fill="#000" opacity="0.18"/><rect x="{x-w//2}" y="{y-10}" width="{w}" height="24" rx="8" fill="#b9854f"/><rect x="{x-w//2+24}" y="{y+14}" width="14" height="74" fill="#8a5a3a"/><rect x="{x+w//2-38}" y="{y+14}" width="14" height="74" fill="#8a5a3a"/>'
            f'<g transform="translate({x-60},{y-62}) rotate(-5)"><rect width="120" height="78" rx="4" fill="{paper}"/><path d="M14 22 L70 22 M14 38 L96 38 M14 54 L58 54" stroke="#9aa5b4" stroke-width="4" stroke-linecap="round"/><path d="M78 50 q10 -22 22 -6 q-2 14 -20 10" stroke="{mark}" stroke-width="5" fill="none" stroke-linecap="round"/></g>')
def pair(t,L='sad',R='smile',s=0.95,qL=True):
    o=boy(290,1150,t,s=s,mood=L,lean=-5,look=-3,armL=4,armR=4)+desk(290,1090)
    o+=boy(790,1150,t,s=s,mood=R,armR=20+8*math.sin(t*3),lean=2)+desk(790,1090)
    return o
def brain(x,y,sc,col='#f3a6b8',t=0.0,glow=0.0):
    s=f'<g transform="translate({x},{y}) scale({sc:.3f})">'
    if glow>0: s+=f'<circle r="150" fill="#fff3a8" opacity="{0.35*glow:.2f}"/>'
    s+=f'<ellipse cx="-34" cy="0" rx="78" ry="64" fill="{col}"/><ellipse cx="34" cy="0" rx="78" ry="64" fill="{col}"/><rect x="-14" y="50" width="28" height="50" rx="12" fill="{col}"/>'
    s+='<path d="M-90 -10 q20 -30 40 -6 M-30 -40 q22 -14 36 8 M20 -42 q30 -12 40 14 M-70 24 q22 14 40 -4 M10 22 q24 18 46 -6 M0 -50 v90" stroke="#00000030" stroke-width="7" fill="none" stroke-linecap="round"/></g>'
    return s
def chart(t,t0,dur,lines,x0=100,y0=470,w=880,h=700,lab='NILAI'):
    p=sm((t-t0)/dur)
    o=f'<rect x="{x0+6}" y="{y0+10}" width="{w}" height="{h}" rx="40" fill="#000" opacity="0.18"/><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="40" fill="#fff" opacity="0.96"/>'
    o+=f'<text x="{x0+50}" y="{y0+60}" font-family="DejaVu Sans Mono" font-size="26" letter-spacing="4" fill="#55594c">{lab}</text>'
    ax0=x0+70;ay0=y0+h-70;aw=w-140;ah=h-190
    o+=f'<path d="M{ax0} {y0+90} V{ay0} H{ax0+aw}" stroke="#aab2a6" stroke-width="6" fill="none" stroke-linecap="round"/>'
    for pts,col in lines:
        P=[(ax0+aw*x,ay0-ah*y) for x,y in pts]
        n=len(P)-1;cut=p*n;seg=[P[0]]
        for k in range(1,n+1):
            if cut>=k: seg.append(P[k])
            else:
                f=cut-(k-1)
                if f>0: seg.append((P[k-1][0]+(P[k][0]-P[k-1][0])*f,P[k-1][1]+(P[k][1]-P[k-1][1])*f))
                break
        d=' '.join(f'{x:.0f},{y:.0f}' for x,y in seg)
        o+=f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>'
        o+=f'<circle cx="{seg[-1][0]:.0f}" cy="{seg[-1][1]:.0f}" r="18" fill="{col}"/>'
    return o
def scene_inner(t):
    idx,lt=sidx(t);o=''
    if idx==0:
        o=cls()+board()+pair(t)+cloud(215,590,t,0.8)+bubble(345,640,t,'q',1.0)+bulb(790,650,t,min(1,lt/0.8))
    elif idx==1:
        o=cls()+board()+boy(540,1190,t,s=1.45,mood='sad',lean=-5,look=-3,armL=4,armR=4)+desk(540,1130,w=420)
        o+=cloud(400,610,t,1.1)+bubble(600,590,t,'q',sm(lt/0.4))
    elif idx==2:
        o=cls()+board()+boy(540,1190,t,s=1.45,mood='smile',armR=25+8*math.sin(t*3),lean=2)+desk(540,1130,w=420)
        o+=bulb(540,500,t,lt/0.5)+sparkles(t,14,200,880,560,1160,3)+plant(930,1110,0.9,3*math.sin(t*1.4))
    elif idx==3:
        o=cls()+board()+desk(290,1090)+desk(790,1090)+boy(290,1150,t,s=0.95,mood='flat')+desk(290,1090)+boy(790,1150,t,s=0.95,mood='flat')+desk(790,1090)
        k=pop(lt/0.4);o+=f'<g transform="translate(540,880) scale({k:.3f})"><circle r="52" fill="#fff"/><path d="M-26 -12 H26 M-26 12 H26" stroke="#1E3A34" stroke-width="10" stroke-linecap="round"/></g>'
        u=sm((t-gs(7)+0.1)/0.7)
        if u>0:
            o+=f'<g opacity="{u:.2f}"><path d="M290 560 L290 {560+80*u:.0f}" stroke="#8a909c" stroke-width="14" stroke-linecap="round"/><path d="M262 {600+80*u:.0f} L290 {640+80*u:.0f} L318 {600+80*u:.0f}" stroke="#8a909c" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/><path d="M790 680 L790 {680-80*u:.0f}" stroke="#1F7A63" stroke-width="14" stroke-linecap="round"/><path d="M762 {640-80*u:.0f} L790 {600-80*u:.0f} L818 {640-80*u:.0f}" stroke="#1F7A63" stroke-width="14" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
    elif idx==4:
        o=cls()+'<rect x="330" y="1020" width="420" height="30" rx="8" fill="#8a5a3a"/><rect x="450" y="1050" width="180" height="150" fill="#6b3f26"/>'
        bk=pop(lt/0.5);o+=f'<g transform="translate(540,900) scale({bk:.3f}) translate(-540,-900)"><rect x="380" y="640" width="320" height="400" rx="16" fill="#1F7A63"/><rect x="380" y="640" width="30" height="400" rx="12" fill="#14584a"/><rect x="430" y="700" width="230" height="8" rx="4" fill="#8ff0c8" opacity="0.8"/><circle cx="545" cy="840" r="62" fill="#8ff0c8"/><path d="M545 880 L545 812 M545 850 C575 840 585 815 580 790 C555 797 545 820 545 850 Z" stroke="#1E3A34" stroke-width="7" fill="#1E3A34" stroke-linecap="round"/></g>'
        o+=sparkles(t,16,260,820,560,1040,5)
    elif idx==5:
        o=cls()+brain(540,820,1.9,'#a7aebb',t)+padlock(540,860+4*math.sin(t*3),2.4,'#e0b84a')+boy(150,1150,t,s=0.7,mood='sad',lean=-4)
    elif idx==6:
        g=0.5+1.0*sm(lt/6.0)
        o=cls()+brain(540,740,1.9+0.25*sm(lt/6),'#f3a6b8',t,glow=1)+sparkles(t,16,200,880,480,1120,6)
        o+=f'<g transform="translate(540,1160) scale({g:.3f}) translate(-540,-1160)">'+plant(540,1160,1.6+0.8*sm(lt/6),3*math.sin(t*1.4))+'</g>'
    elif idx==7:
        n=int(373*sm((t-gs(14))/ (ge(16)-gs(14)+0.1)));o=cls()
        o+='<rect x="70" y="500" width="940" height="840" rx="40" fill="#fff" opacity="0.7"/>'
        cols=['#1F7A63','#4cc9f0','#ffd166','#ff8fa3','#b388ff','#06d6a0']
        for i in range(373):
            if i>=n: break
            r,c=divmod(i,19);x=120+c*46;y=545+r*40
            col=cols[(i*7+r)%6]
            o+=f'<circle cx="{x}" cy="{y}" r="11" fill="#f0c3a0"/><rect x="{x-11}" y="{y+12}" width="22" height="20" rx="8" fill="{col}"/>'
    elif idx==8:
        o=cls()+chart(t,gs(17),ge(18)-gs(17),[([(0,.12),(.2,.2),(.4,.38),(.6,.58),(.8,.74),(1,.9)],'#1F7A63')])+boy(250,1500,t,s=0.001)
        o+=boy(200,1330,t,s=0.7,mood='smile',armL=40,armR=40,lean=2)+sparkles(t,10,500,980,520,1100,2)
    elif idx==9:
        o=cls()+chart(t,gs(19),ge(20)-gs(19),[([(0,.3),(.2,.32),(.4,.29),(.6,.31),(.8,.3),(1,.31)],'#8a909c')],lab='NILAI')
        o+=boy(200,1330,t,s=0.7,mood='flat',lean=-3)
    elif idx==10:
        o=cls()+stairs(0,0)
        u=sm((t-gs(21))/(ge(22)-gs(21)))
        pos=[(180,1075),(220,1005),(500,905),(780,805)]
        k=u*3;seg=min(2,int(k));f=k-seg
        a=pos[seg];b=pos[seg+1] if seg<3 else pos[3]
        a=pos[seg] if seg>0 else pos[0]
        px=pos[seg][0]+(pos[seg+1][0]-pos[seg][0])*sm(f);py=pos[seg][1]+(pos[seg+1][1]-pos[seg][1])*sm(f)-90*math.sin(math.pi*f)
        o+=boy(px,py,t,s=0.8,mood='smile',armR=20*math.sin(t*6))
        o+=boy(930,1160,t,s=0.55,mood='sad',lean=-5)
    elif idx==11:
        o=cls()+brain(540,760,1.9*(1+0.06*math.sin(t*3)),'#f3a6b8',t,glow=0.8)
        for i,(ax,ay) in enumerate([(330,560),(540,520),(750,560)]):
            ph=(t*0.7+i*0.3)%1;o+=f'<path d="M{ax} {ay-ph*70:.0f} l-20 30 h12 v30 h16 v-30 h12 z" fill="#1F7A63" opacity="{1-ph:.2f}"/>'
        for i in range(4):
            o+=boy(150+i*250,1330,t+i*0.4,s=0.55,mood='smile')
    elif idx==12:
        o=cls()+chart(t,gs(25),ge(27)-gs(25),[([(0,.62),(.3,.64),(.6,.61),(1,.63)],'#1F7A63'),([(0,.62),(.3,.5),(.6,.34),(1,.16)],'#d9483b')],lab='NILAI MATEMATIKA')
    elif idx==13:
        o=cls()+boy(540,1210,t,s=1.5,mood='open' if MOUTH[min(int(t*FPS),len(MOUTH)-1)]>0.35 else 'smile',armL=70+10*math.sin(t*4),armR=70+10*math.sin(t*4+1),lean=2)
        o+=bulb(540,480,t,lt/0.5)+sparkles(t,14,160,920,520,1160,8)
    elif idx==14:
        o=outdoor()
        o+='<path d="M540 1100 L400 1000 M540 1100 L700 1000" stroke="#c9a46a" stroke-width="60" stroke-linecap="round"/><path d="M540 1300 L540 1100" stroke="#c9a46a" stroke-width="70" stroke-linecap="round"/>'
        o+='<rect x="530" y="760" width="22" height="260" fill="#8a5a3a"/>'
        t1=gs(34)-0.1;t2=gs(35)-0.1
        a1=pop((t-t1)/0.4);a2=pop((t-t2)/0.4)
        o+=f'<g transform="translate(330,800) scale({a1:.3f})"><rect x="-140" y="-40" width="280" height="80" rx="20" fill="#8a909c"/><path d="M-100 -4 H60 M30 -26 L60 -4 L30 18" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
        o+=f'<g transform="translate(760,720) scale({a2:.3f})"><rect x="-140" y="-40" width="280" height="80" rx="20" fill="#1F7A63"/><path d="M-100 4 H40 M10 -18 L40 4 L10 26" stroke="#fff" stroke-width="10" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>'
        o+=boy(540,1330,t,s=0.7,mood='flat' if t<t2 else 'smile',lean=-2)
        if t>=t2: o+=bulb(540,1000,t,(t-t2)/0.5)+sparkles(t,10,500,960,560,1000,4)
    elif idx==15:
        o=cls()+board()+pair(t,'flat','flat')
        k=pop(lt/0.4);o+=bubble(240,640,t,'q',k)+bubble(745,640,t,'q',k)
    else:
        o=cls()+board()+boy(540,1190,t,s=1.4,mood='open' if MOUTH[min(int(t*FPS),len(MOUTH)-1)]>0.35 else 'smile',armR=60+25*math.sin(t*6),lean=3)
        o+=confetti(t)+sparkles(t,12,120,960,480,1100,6)
        k=pop((t-gs(38))/0.5)
        o+=f'<g transform="translate(540,1245) scale({k:.3f}) translate(-540,-1245)"><rect x="110" y="1185" width="860" height="120" rx="60" fill="#fff"/><circle cx="190" cy="1245" r="38" fill="#1F7A63"/><path d="M174 1232 h32 a6 6 0 0 1 6 6 v14 a6 6 0 0 1 -6 6 h-18 l-10 9 v-9 a6 6 0 0 1 -4 -6 v-14 a6 6 0 0 1 4 -6 z" fill="#fff"/><text x="260" y="1236" font-family="Poppins" font-weight="700" font-size="32" fill="#1d2a26">Follow BeYourBest &amp;</text><text x="260" y="1280" font-family="Poppins" font-weight="700" font-size="32" fill="#1F7A63">tulis topik berikutnya di komentar</text></g>'
    return o
def scene(t):
    idx,lt=sidx(t)
    z=(1.0+0.05*sm(lt/7.0)) if idx%2==0 else (1.06-0.05*sm(lt/7.0));fx,fy=540,900
    pxx=20*math.sin(lt*0.5+idx);rot=0.3*math.sin(t*0.6)
    return f'<g transform="translate({fx+pxx:.1f},{fy}) rotate({rot:.2f}) scale({z:.4f}) translate({-fx},{-fy})"><g transform="translate(0,70)">{scene_inner(t)}{dust(t)}</g></g>'
#@@OVERLAY
def cards(t):
    idx,lt=sidx(t);o=''
    if idx==4: o+=chip(540,455,560,84,'Carol S. Dweck','#1F7A63',fs=40,sx=pop(lt/0.4),sy=pop(lt/0.4))+(chip(540,1300,640,84,'Psikolog · Stanford','#1E3A34',fs=36,sx=pop((t-gs(9))/0.4),sy=pop((t-gs(9))/0.4)) if t>=gs(9) else '')
    if idx==5: o+=barcard(t,0.3,'#8a909c','lock',pop(lt/0.4),shake=4*math.sin(t*9))
    if idx==6: o+=barcard(t,0.15+0.8*sm(lt/6),'#1F7A63','star',pop(lt/0.4))
    if idx==7:
        tk=wfind(16,'tiga');ts=wfind(16,'kelas');td=wfind(16,'dua')
        if t>=ts-0.1: o+=chip(250,455,260,70,'KELAS 7','#1E3A34',fs=34,sx=pop((t-ts)/0.3),sy=pop((t-ts)/0.3))
        if t>=tk: o+=chip(540,455,300,76,'373 SISWA','#1F7A63',fs=40,sx=pop((t-tk)/0.3),sy=pop((t-tk)/0.3))
        if t>=td-0.1: o+=chip(830,455,260,70,'2 TAHUN','#d9483b',fs=34,sx=pop((t-td)/0.3),sy=pop((t-td)/0.3))
    if idx==13: o+=chip(540,455,300,76,'GIGIH','#1F7A63',fs=44,sx=pop(lt/0.4),sy=pop(lt/0.4))
    if idx==15: o+=chip(540,1300,680,80,'KAMU DI KUBU MANA?','#1E3A34',fs=38,sx=pop((t-gs(37))/0.4),sy=pop((t-gs(37))/0.4)) if t>=gs(37)-0.2 else ''
    return o
def band(t):
    for s0 in ST[1:]:
        u=(t-(s0-0.16))/0.46
        if 0<=u<=1:
            cx=-1000+3080*sm(u);sk=220
            return (f'<polygon points="{cx-560+sk:.0f},-10 {cx+560+sk:.0f},-10 {cx+560-sk:.0f},1930 {cx-560-sk:.0f},1930" fill="#1F7A63" opacity="0.96"/>'
                    f'<polygon points="{cx+560+sk:.0f},-10 {cx+590+sk:.0f},-10 {cx+590-sk:.0f},1930 {cx+560-sk:.0f},1930" fill="#8ff0c8"/>')
    return ''
