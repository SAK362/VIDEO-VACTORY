import json,math,sys,subprocess,os
from PIL import ImageFont
T=json.load(open('timing.json'));GR=T['groups'];DUR=T['dur'];MOUTH=T['mouth'];FPS=30
CT=0.0
FB=ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',52)
def gs(i): return GR[i]['start']
def ge(i): return GR[i]['end']
def cl(x,a=0.0,b=1.0): return max(a,min(b,x))
def sm(x): x=cl(x); return x*x*(3-2*x)
def eo(x): x=cl(x); return 1-(1-x)**3
def pop(x):
    x=cl(x)
    return 0 if x<=0 else (1+ (1.70158+1)*(x-1)**3+1.70158*(x-1)**2)
def mix(a,b,k):
    ca=[int(a[i:i+2],16) for i in (1,3,5)];cb=[int(b[i:i+2],16) for i in (1,3,5)]
    return '#%02x%02x%02x'%tuple(int(ca[i]+(cb[i]-ca[i])*k) for i in range(3))
def wordt(g,p,wd):
    for w in GR[g]['phrases'][p]['words']:
        if w['w'].strip(',.?!').lower()==wd: return w['start']
    raise KeyError(wd)

DEFS='''<defs>
<linearGradient id="inside" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffbe0"/><stop offset="1" stop-color="#ffd36b"/></linearGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffe9a0" stop-opacity="0.85"/><stop offset="1" stop-color="#ffe9a0" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff3c4" stop-opacity="0.55"/><stop offset="1" stop-color="#fff3c4" stop-opacity="0"/></linearGradient>
<linearGradient id="dl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd98a" stop-opacity="0.95"/><stop offset="1" stop-color="#ffd98a" stop-opacity="0"/></linearGradient>
<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EDEBDD"/><stop offset="0.7" stop-color="#EDEBDD" stop-opacity="0.96"/><stop offset="1" stop-color="#EDEBDD" stop-opacity="0"/></linearGradient>
<radialGradient id="vig" cx="0.5" cy="0.5" r="0.78"><stop offset="0.62" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#2a1608" stop-opacity="0.5"/></radialGradient>
<pattern id="hatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="9" stroke="#b8f0d8" stroke-width="2" stroke-opacity="0.85"/></pattern>
</defs>'''

def room(k,beam=True):
    wt=mix('#c4cfdd','#f7dfb9',k);wb=mix('#a3b3c8','#eab98a',k);ft=mix('#838a9c','#cf955f',k);fb=mix('#565c70','#8a5a38',k)
    s=f'<defs><linearGradient id="wl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{wt}"/><stop offset="1" stop-color="{wb}"/></linearGradient><linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ft}"/><stop offset="1" stop-color="{fb}"/></linearGradient></defs>'
    s+='<rect x="-320" y="-80" width="1720" height="1080" fill="url(#wl)"/><rect x="-320" y="1000" width="1720" height="1000" fill="url(#fl)"/>'
    s+=f'<rect x="-320" y="990" width="1720" height="22" fill="{mix("#4b5568","#7a4a2c",k)}"/>'
    s+=f'<g stroke="{mix("#3b4254","#6d4024",k)}" stroke-opacity="0.3" stroke-width="3"><line x1="-320" y1="1170" x2="1400" y2="1170"/><line x1="-320" y1="1390" x2="1400" y2="1390"/><line x1="-320" y1="1630" x2="1400" y2="1630"/><line x1="-320" y1="1850" x2="1400" y2="1850"/></g>'
    s+=f'<rect x="60" y="400" width="190" height="230" rx="10" fill="{mix("#9aa9bd","#8fc7e8",k)}" stroke="#8a5a3a" stroke-width="14"/>'
    c1=(CT*14)%330-90;c2=(CT*9+150)%330-90
    s+=f'<clipPath id="wclip"><rect x="67" y="407" width="176" height="216"/></clipPath><g clip-path="url(#wclip)" opacity="{0.4+0.6*k:.2f}"><ellipse cx="{67+c1:.0f}" cy="452" rx="42" ry="14" fill="#fff" opacity="0.92"/><ellipse cx="{67+c1+22:.0f}" cy="442" rx="28" ry="14" fill="#fff" opacity="0.92"/><ellipse cx="{67+c2:.0f}" cy="565" rx="36" ry="12" fill="#fff" opacity="0.8"/>'
    u=(CT%8)/2.4
    if u<1: s+=f'<path d="M{67+u*190:.0f} {500+14*math.sin(u*12):.0f} q8 -{8+6*math.sin(CT*30):.0f} 16 0 q8 -{8-6*math.sin(CT*30):.0f} 16 0" stroke="#34495e" stroke-width="3" fill="none"/>'
    s+='</g><line x1="155" y1="400" x2="155" y2="630" stroke="#8a5a3a" stroke-width="10"/><line x1="60" y1="515" x2="250" y2="515" stroke="#8a5a3a" stroke-width="10"/>'
    s+=f'<circle cx="855" cy="640" r="32" fill="#fff6e6" stroke="#8a5a3a" stroke-width="7"/><line x1="855" y1="640" x2="{855+18*math.sin(CT*0.4):.1f}" y2="{640-18*math.cos(CT*0.4):.1f}" stroke="#3a2b20" stroke-width="5" stroke-linecap="round"/><line x1="855" y1="640" x2="{855+25*math.sin(CT*2.2):.1f}" y2="{640-25*math.cos(CT*2.2):.1f}" stroke="#d9442f" stroke-width="3" stroke-linecap="round"/>'
    if beam: s+=f'<polygon points="60,420 250,420 700,1000 330,1000" fill="url(#beam)" opacity="{0.2+0.8*k:.2f}"/><circle cx="205" cy="455" r="22" fill="#fff6c9" opacity="{0.25+0.65*k:.2f}"/>'
    s+='<rect x="790" y="470" width="130" height="100" rx="6" fill="#8a5a3a"/><rect x="802" y="482" width="106" height="76" fill="#cfe9d2"/><path d="M802 558 L835 520 L862 545 L885 510 L908 558 Z" fill="#6fae7c"/>'
    return s

def padlock(x,y,s,body='#e0b84a',sh='#b9922e',op=0.0):
    r=-30*op
    return (f'<g transform="translate({x},{y}) scale({s:.3f})"><g transform="translate({16*op:.1f},{-14*op:.1f}) rotate({r:.1f} 18 -4)"><path d="M-18 -4 L-18 -26 A18 18 0 0 1 18 -26 L18 -4" stroke="{sh}" stroke-width="9" fill="none" stroke-linecap="round"/></g>'
            f'<rect x="-32" y="-6" width="64" height="52" rx="10" fill="{body}"/><circle cx="0" cy="16" r="7" fill="#4a3410"/><rect x="-3" y="18" width="6" height="14" fill="#4a3410"/></g>')

def door(op=0.0,glow=0.0,lock=0.0,lockcol='#e0b84a',t=0.0):
    s='<rect x="410" y="400" width="300" height="590" rx="8" fill="#6b3f26"/>'
    if op>0.001:
        s+='<rect x="430" y="420" width="260" height="570" fill="url(#inside)"/>'
        for i in range(5):
            a=-0.5+i*0.25
            s+=f'<polygon points="560,760 {560+a*900:.0f},1260 {560+a*900+120:.0f},1260" fill="#fff6c9" opacity="{0.22*op:.2f}"/>'
    sx=1-0.9*op
    s+=f'<g transform="translate(430,0) scale({sx:.3f},1) translate(-430,0)"><rect x="430" y="420" width="260" height="570" rx="6" fill="#8b5a3c"/><g fill="#7a4b30"><rect x="455" y="450" width="95" height="205" rx="4"/><rect x="570" y="450" width="95" height="205" rx="4"/><rect x="455" y="695" width="95" height="225" rx="4"/><rect x="570" y="695" width="95" height="225" rx="4"/></g><circle cx="655" cy="750" r="14" fill="#e0b84a"/></g>'
    g=cl(glow)
    if g>0 or op>0:
        s+=f'<ellipse cx="560" cy="1010" rx="{300+200*g:.0f}" ry="{110+60*g:.0f}" fill="url(#halo)" opacity="{0.25+0.6*g+0.4*op:.2f}"/>'
    s+=f'<rect x="430" y="990" width="260" height="14" fill="#ffd98a" opacity="{0.45+0.5*g:.2f}"/>'
    sp=0.45+0.5*g+0.6*op
    s+=f'<polygon points="430,1004 690,1004 {830+90*op:.0f},1190 {290-90*op:.0f},1190" fill="url(#dl)" opacity="{min(1,sp):.2f}"/>'
    if lock>0: s+=padlock(560,720+4*math.sin(t*3),1.5*pop(lock),lockcol)
    return s

def rug(cx=300,cy=1085,rx=230):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="38" fill="#b4533b" opacity="0.85"/><ellipse cx="{cx}" cy="{cy}" rx="{rx-40}" ry="28" fill="none" stroke="#f3d9b0" stroke-width="4" opacity="0.8"/>'

def plant(x,y,g=1.0,sway=0.0):
    return (f'<g transform="translate({x},{y}) scale({g:.3f}) translate(-900,-1040)"><ellipse cx="900" cy="1040" rx="55" ry="10" fill="#000" opacity="0.18"/><path d="M860 960 L940 960 L926 1040 L874 1040 Z" fill="#b5533a"/>'
            f'<g transform="rotate({sway:.1f} 900 960)"><path d="M900 960 C860 900 850 850 880 800 C900 850 905 900 900 960 Z" fill="#4f9a55"/><path d="M900 960 C940 910 960 860 935 820 C905 860 898 910 900 960 Z" fill="#3d8445"/></g></g>')

def star(x,y,r,col='#fff3a8',a=1.0,rot=0):
    return f'<path transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f}) scale({r:.2f})" d="M0 -1 L0.28 -0.28 L1 0 L0.28 0.28 L0 1 L-0.28 0.28 L-1 0 L-0.28 -0.28 Z" fill="{col}" opacity="{a:.2f}"/>'
def sparkles(t,n,x0,x1,y0,y1,seed=1,col='#fff3a8',sz=16):
    s=''
    for i in range(n):
        ph=(t*0.7+ (i*0.137+seed*0.31))%1.0
        x=x0+(x1-x0)*((math.sin(i*12.9898+seed*78.233)*43758.5453)%1)
        y=y0+(y1-y0)*((math.sin(i*4.1414+seed*12.345)*24634.6345)%1)
        a=math.sin(ph*math.pi)
        s+=star(x,y-ph*30,sz*(0.4+0.8*a),col,a,ph*180)
    return s
def confetti(t,n=26,x0=60,x1=1020,y0=380,y1=1300):
    cols=['#ff6b6b','#ffd166','#06d6a0','#4cc9f0','#b388ff']
    s=''
    for i in range(n):
        sp=0.18+0.12*((i*7)%5)/5
        ph=(t*sp+((math.sin(i*91.7)*1e4)%1))%1.0
        x=x0+(x1-x0)*((math.sin(i*12.9898)*43758.5453)%1)+30*math.sin(t*2+i)
        y=y0+(y1-y0)*ph
        s+=f'<rect x="{x:.0f}" y="{y:.0f}" width="12" height="20" rx="3" fill="{cols[i%5]}" transform="rotate({(t*140+i*50)%360:.0f} {x+6:.0f} {y+10:.0f})" opacity="0.95"/>'
    return s

def boy(x,y,t,s=1.0,mood='smile',armL=0.0,armR=0.0,lean=0.0,look=0.0,sy=None):
    br=1+0.012*math.sin(t*2*math.pi/2.6) if sy is None else sy
    armL+=2.5*math.sin(t*1.3);armR+=2.5*math.sin(t*1.3+1.5);lean+=1.6*math.sin(t*0.9);look+=2.5*math.sin(t*0.7)
    blink=1.0 if (t%3.3)>0.14 else 0.1
    mouth={'smile':'M238 800 Q250 809 262 800','flat':'M241 803 L259 803','sad':'M238 807 Q250 798 262 807','open':'M236 800 Q250 818 264 800 Z'}[mood]
    mfill='#7a2d2d' if mood=='open' else 'none'
    brows='<path d="M221 763 L243 756 M279 763 L257 756" stroke="#3a2418" stroke-width="4" stroke-linecap="round"/>' if mood=='sad' else ''
    return (f'<g transform="translate({x-250*s:.1f},{y-1075*s:.1f}) scale({s})"><ellipse cx="250" cy="1078" rx="88" ry="14" fill="#000" opacity="0.22"/>'
    '<rect x="205" y="1000" width="26" height="62" rx="8" fill="#f0c3a0"/><rect x="269" y="1000" width="26" height="62" rx="8" fill="#f0c3a0"/><rect x="198" y="1030" width="40" height="14" fill="#fff"/><rect x="262" y="1030" width="40" height="14" fill="#fff"/><ellipse cx="214" cy="1070" rx="30" ry="14" fill="#d9442f"/><ellipse cx="286" cy="1070" rx="30" ry="14" fill="#d9442f"/>'
    '<path d="M190 950 L310 950 L318 1018 L182 1018 Z" fill="#222"/>'
    f'<g transform="translate(0,{950*(1-br):.1f}) scale(1,{br:.4f})">'
    f'<g transform="rotate({armL:.1f} 168 845)"><rect x="150" y="838" width="36" height="100" rx="16" fill="#f0c3a0"/></g><g transform="rotate({-armR:.1f} 332 845)"><rect x="314" y="838" width="36" height="100" rx="16" fill="#f0c3a0"/></g>'
    '<path d="M185 830 L315 830 L322 960 L178 960 Z" fill="#fff"/><path d="M185 830 L215 830 L215 960 L178 960 Z" fill="#2b2b33"/><path d="M285 830 L315 830 L322 960 L285 960 Z" fill="#2b2b33"/><rect x="200" y="814" width="100" height="22" rx="8" fill="#2a3f7a"/>'
    f'<g transform="rotate({lean:.1f} 250 830)"><circle cx="250" cy="770" r="52" fill="#f0c3a0"/><path d="M196 765 C190 700 245 690 270 705 C305 700 312 740 304 765 C285 735 235 740 196 765 Z" fill="#4a2a18"/>'
    f'<ellipse cx="{232+look:.1f}" cy="778" rx="6" ry="{6*blink:.1f}" fill="#3a2418"/><ellipse cx="{268+look:.1f}" cy="778" rx="6" ry="{6*blink:.1f}" fill="#3a2418"/>{brows}'
    f'<path d="{mouth}" stroke="#3a2418" stroke-width="4" fill="{mfill}" stroke-linecap="round" stroke-linejoin="round"/></g></g></g>')

def bubble(x,y,t,kind='q',sc=1.0):
    b=3*math.sin(t*2)
    inner={'q':f'<text x="{x+65}" y="{y+75+b:.1f}" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="64" fill="#1F7A63">?</text>'}[kind]
    return (f'<g opacity="{cl(sc):.2f}"><circle cx="{x-12}" cy="{y+160+b:.1f}" r="8" fill="#fff"/><circle cx="{x+10}" cy="{y+125+b:.1f}" r="13" fill="#fff"/><rect x="{x}" y="{y+b:.1f}" width="130" height="100" rx="40" fill="#fff" opacity="0.97"/>{inner}</g>')

def bulb(x,y,t,k):
    k=pop(k);s=f'<g transform="translate({x},{y}) scale({k:.3f})">'
    for i in range(8):
        a=i*math.pi/4+t*0.6
        s+=f'<line x1="{math.cos(a)*52:.0f}" y1="{math.sin(a)*52:.0f}" x2="{math.cos(a)*72:.0f}" y2="{math.sin(a)*72:.0f}" stroke="#ffd34d" stroke-width="7" stroke-linecap="round"/>'
    s+='<circle cx="0" cy="0" r="38" fill="#ffe066"/><rect x="-18" y="34" width="36" height="22" rx="6" fill="#9aa0a8"/><path d="M-10 8 L0 -8 L10 8" stroke="#e0a800" stroke-width="4" fill="none"/></g>'
    return s

def cloud(x,y,t,sc=1.0):
    s=f'<g transform="translate({x},{y}) scale({sc})"><g fill="#6c7689"><ellipse cx="0" cy="0" rx="90" ry="40"/><ellipse cx="-50" cy="12" rx="60" ry="34"/><ellipse cx="55" cy="14" rx="62" ry="34"/><ellipse cx="10" cy="-26" rx="52" ry="38"/></g>'
    for i in range(7):
        ph=(t*0.9+i*0.31)%1.0
        s+=f'<line x1="{-70+i*24}" y1="{40+ph*120:.0f}" x2="{-74+i*24}" y2="{54+ph*120:.0f}" stroke="#7fa8d8" stroke-width="5" stroke-linecap="round" opacity="{1-ph:.2f}"/>'
    return s+'</g>'

def baby(x,y,t,mode):
    # fase siklus
    ang=0.0;dx=0.0;dy=0.0;stars=0.0;walk=0.0
    if mode=='try':
        c=(t%3.0)
        if c<1.1: ang=7*math.sin(c*9)*(c/1.1)
        elif c<1.5: u=(c-1.1)/0.4;ang=7+ 80*sm(u);dy=18*sm(u);stars=u
        elif c<2.2: ang=87;dy=20;stars=max(0,1-(c-1.5))
        elif c<2.8: u=(c-2.2)/0.6;ang=87*(1-sm(u));dy=20*(1-sm(u))
    elif mode=='fall':
        c=(t%1.6)
        if c<0.5: ang=8*math.sin(c*14)
        elif c<0.8: u=(c-0.5)/0.3;ang=80*sm(u);dy=18*sm(u);stars=u
        elif c<1.2: ang=80;dy=20;stars=max(0,1-(c-0.8)/0.4)
        else: u=(c-1.2)/0.4;ang=80*(1-sm(u));dy=20*(1-sm(u))
    else:
        walk=1.0;dx=150*math.sin(t*1.3);ang=4*math.sin(t*6)
        dy=-7*abs(math.sin(t*6))
    face=1 if (mode!='walk' or math.cos(t*1.3)>=0) else -1
    sw=18*math.sin(t*6)*walk
    s=f'<g transform="translate({x+dx:.1f},{y+dy:.1f}) scale({face},1)"><ellipse cx="0" cy="8" rx="70" ry="12" fill="#000" opacity="0.2"/><g transform="rotate({ang:.1f} 0 0)">'
    s+=f'<rect x="-26" y="-60" width="18" height="60" rx="9" fill="#f6cfae" transform="rotate({sw:.1f} -17 -60)"/><rect x="8" y="-60" width="18" height="60" rx="9" fill="#f6cfae" transform="rotate({-sw:.1f} 17 -60)"/>'
    s+='<ellipse cx="-17" cy="2" rx="20" ry="9" fill="#fff"/><ellipse cx="17" cy="2" rx="20" ry="9" fill="#fff"/>'
    s+='<path d="M-42 -62 L42 -62 L36 -150 L-36 -150 Z" fill="#7bdcb5"/><path d="M-30 -62 L30 -62 L26 -85 L-26 -85 Z" fill="#fff" opacity="0.9"/>'
    s+=f'<rect x="-60" y="-146" width="22" height="56" rx="11" fill="#f6cfae" transform="rotate({-10-sw:.1f} -49 -146)"/><rect x="38" y="-146" width="22" height="56" rx="11" fill="#f6cfae" transform="rotate({10+sw:.1f} 49 -146)"/>'
    s+='<circle cx="0" cy="-196" r="50" fill="#f6cfae"/><path d="M-30 -232 C-10 -262 20 -258 32 -236 C10 -248 -12 -246 -30 -232 Z" fill="#4a2a18"/><circle cx="-18" cy="-192" r="6" fill="#3a2418"/><circle cx="18" cy="-192" r="6" fill="#3a2418"/><path d="M-12 -174 Q0 -164 12 -174" stroke="#3a2418" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="-34" cy="-180" r="8" fill="#ffa9a0" opacity="0.7"/><circle cx="34" cy="-180" r="8" fill="#ffa9a0" opacity="0.7"/></g>'
    if stars>0:
        for i in range(3): s+=star(-60+i*60,-120-30*stars,22*stars+6,'#ffe066',1-0.3*stars,t*200+i*40)
    return s+'</g>'

def stairs(step_t,k):
    # tiga anak tangga naik ke kanan
    s=''
    xs=[(80,360,1005),(360,640,905),(640,920,805)]
    cols=['#c98a58','#bf7f4e','#b5754a']
    for (a,b,top),c in zip(xs,cols):
        s+=f'<rect x="{a}" y="{top}" width="{b-a}" height="{1180-top}" fill="{c}"/><rect x="{a}" y="{top}" width="{b-a}" height="16" fill="#e6b987"/><rect x="{a}" y="{top+16}" width="{b-a}" height="10" fill="#000" opacity="0.10"/><rect x="{a}" y="{top}" width="8" height="{1180-top}" fill="#fff" opacity="0.12"/><rect x="{b-12}" y="{top}" width="12" height="{1180-top}" fill="#000" opacity="0.10"/><rect x="{a}" y="1165" width="{b-a}" height="15" fill="#000" opacity="0.12"/>'
    return s

def mini_room(px,py,pw,ph,k,op,lock,plantg,t,cid):
    sc=0.62
    s=f'<clipPath id="{cid}"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="36"/></clipPath><g clip-path="url(#{cid})"><g transform="translate({px+pw/2-560*sc:.1f},{py-380*sc:.1f}) scale({sc})">'
    s+=room(k,beam=False)+door(op,0.0,lock,'#8a909c',t)
    if plantg>0: s+=plant(880,1040,plantg,3*math.sin(t*1.5))
    s+=f'</g></g><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="36" fill="none" stroke="#fff" stroke-width="8"/>'
    return s

def dust(t):
    s=''
    for i in range(22):
        ph=(t*0.05+i*0.0913)%1.0
        x=((math.sin(i*37.1)*1e4)%1)*1080+28*math.sin(t*0.7+i)
        y=1250-ph*900
        a=math.sin(ph*math.pi)*0.5
        s+=f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{2+(i%3)}" fill="#fff6d8" opacity="{a:.2f}"/>'
    return s
EX=lambda lt:-420*(1-eo(lt/0.8))
EY=lambda lt:-22*abs(math.sin(lt*11))*(1-eo(lt/0.8))
# ---------- adegan ----------
def scene(t):
    f=int(t*FPS)
    sc=[(0,0),(gs(2)-0.08,1),(gs(6)-0.08,2),(gs(8)-0.08,3),(gs(11)-0.08,4),(gs(14)-0.08,5),(gs(18)-0.08,6),(gs(20)-0.08,7),(gs(28)-0.08,8)]
    idx=max(i for s0,i in sc if t>=s0)
    s0=[s for s,i in sc if i==idx][0];lt=t-s0
    z=(1.0+0.06*sm(lt/7.0)) if idx%2==0 else (1.07-0.06*sm(lt/7.0)); fx,fy=540,900
    pxx=24*math.sin(lt*0.5+idx);rot=0.35*math.sin(t*0.6)
    o=''
    if idx==0:
        o+=room(0.55)+door(0,0.05)+rug()
        o+=plant(900,1040)+boy(300,1075,t,mood='sad',lean=-4*math.sin(t*1.2)-3,look=-3,armL=3,armR=3)
        o+=bubble(380,520,t,'q',sm(lt/0.5))
    elif idx==1:
        k=0.6+0.4*sm(lt/3.0);g3=gs(3)
        o+=room(k)+door(0,0.3+0.7*sm((t-g3)/1.2)+0.15*math.sin(t*3)*sm((t-g3)/1.2),0,t=t)+rug()+plant(900,1040,1,3*math.sin(t*1.3))
        happy=t>=wordt(3,0,'belum') if False else t>=GR[3]['phrases'][0]['words'][2]['start']
        o+=boy(300,1075,t,mood='smile' if happy else 'flat',lean=0 if happy else -2,armR=(25+10*math.sin(t*5)) if happy else 0)
        o+=bulb(335,640,t,(t-gs(2))/0.45)
        if t>=g3: o+=sparkles(t,10,150,650,520,1100,2)
    elif idx==2:
        o+='<rect x="-320" y="-200" width="1720" height="1500" fill="#e6e1d1"/><rect x="-320" y="1010" width="1720" height="1200" fill="#d2cab4"/>'
        kL=pop(lt/0.45);kR=pop((t-gs(7)+0.1)/0.45)
        if kR<1: o+='<rect x="560" y="470" width="440" height="640" rx="36" fill="none" stroke="#fff" stroke-width="7" stroke-dasharray="20 16" opacity="0.9"/>'
        o+=f'<g transform="translate(260,860) scale({kL:.3f}) translate(-260,-860)">'+mini_room(40,470,440,640,0.0,0,1.0,0,t,'cL')+'</g>'
        o+=f'<g transform="translate(820,860) scale({kR:.3f}) translate(-820,-860)">'+mini_room(560,470,440,640,1.0,0.85,0,0.25+0.8*sm((t-gs(7))/2.6),t,'cR')+'</g>' if kR>0 else ''
        o+=f'<g transform="translate(540,840)"><circle r="34" fill="#fff" stroke="#1E3A34" stroke-width="5"/><path d="M-10 -10 L10 10 M10 -10 L-10 10" stroke="#1E3A34" stroke-width="6" stroke-linecap="round" opacity="0"/></g>' if False else ''
    elif idx==3:
        o+=room(0.0)+f'<rect x="-10" y="-90" width="1100" height="1300" fill="#6b7a99" opacity="0.18"/>'
        o+=door(0,0,1.0,'#8a909c',t)+rug()+plant(900,1040,0.8,0)
        o+=boy(300+EX(lt),1075+EY(lt),t,mood='sad',lean=-6,look=-4,armL=4,armR=4,sy=1+0.008*math.sin(t*1.5))
        o+=cloud(300,560,t,1.0+0.04*math.sin(t*1.5))
    elif idx==4:
        g=0.45+0.8*sm(lt/6.5)
        o+=room(1.0)+door(0,0.35+0.2*math.sin(t*2))+rug()+plant(900,1040,g,3*math.sin(t*1.4))
        o+=boy(300+EX(lt),1075+EY(lt),t,mood='smile',armR=20+10*math.sin(t*3),lean=2)
        o+=sparkles(t,14,120,960,480,1100,4)
    elif idx==5:
        o+=room(1.0)+door(0,0.25)+rug(540,1100,300)+plant(900,1040,1.0,2*math.sin(t*1.5))
        mode='try' if t<gs(15)-0.05 else ('fall' if t<gs(16)-0.05 else 'walk')
        tt=t-(gs(14) if mode=='try' else gs(15) if mode=='fall' else gs(16))
        o+=baby(540,1090,tt+0.0,mode)
        if mode=='walk': o+=sparkles(t,12,200,900,560,1050,7)
    elif idx==6:
        tm=wordt(18,0,'membuka');tc=wordt(19,0,'menguncinya')
        op=sm((t-tm+0.25)/1.1)*(1-sm((t-tc+0.55)/0.5))
        lk=cl((t-tc+0.15)/0.45)
        o+=room(0.8+0.2*op)+door(op,0.1,lk,'#e0b84a',t)+rug()+plant(900,1040,1,0)
        o+=boy(300+EX(lt),1075+EY(lt),t,mood='open' if (op>0.4 and lk<=0) else ('sad' if lk>0 else 'smile'),armR=(30+8*math.sin(t*4)) if op>0.5 else 0,lean=0)
        if op>0.3: o+=sparkles(t,12,300,820,480,1100,5)
    elif idx==7:
        o+=room(0.9)
        o+=stairs(0,0)
        # posisi anak: lantai -> tangga 1 -> 2 -> 3
        st=[(gs(22)-0.1),(gs(24)-0.1),(gs(26)-0.1)]
        pos=[(180,1075),(220,1005),(500,905),(780,805)]
        cur=0;ts=0.0
        for i,tt in enumerate(st):
            if t>=tt: cur=i+1;ts=tt
        a=pos[cur-1] if cur>0 else pos[0]; b=pos[cur]
        if cur==0: px,py=pos[0]
        else:
            u=cl((t-ts)/0.55);px=a[0]+(b[0]-a[0])*sm(u);py=a[1]+(b[1]-a[1])*sm(u)-110*math.sin(math.pi*u)
        cheer=cur==3 and t>st[2]+0.7
        o+=boy(px,py,t,s=0.85,mood='smile' if cur>0 else 'flat',armL=(150+10*math.sin(t*8)) if cheer else 0,armR=(150+10*math.sin(t*8+1)) if cheer else 0)
        # ikon langkah
        if cur>=1: o+=padlock(105,880-4*math.sin(t*3),1.0*pop((t-st[0])/0.4),'#e0b84a','#b9922e',op=sm((t-st[0]-0.4)/0.5))
        if cur>=2:
            k2=pop((t-st[1])/0.4);o+=f'<g transform="translate(345,770) scale({k2:.3f})"><circle r="38" fill="#7bdcb5"/><circle cx="0" cy="-6" r="14" fill="none" stroke="#1E3A34" stroke-width="7"/><line x1="10" y1="6" x2="28" y2="26" stroke="#1E3A34" stroke-width="8" stroke-linecap="round"/></g>'
        if cur>=3:
            k3=pop((t-st[2])/0.4);o+=f'<g transform="translate(935,610) scale({k3:.3f})">'+star(0,0,56,'#ffd34d')+'</g>'
            o+=sparkles(t,10,600,980,520,900,3,'#ffd34d')
            if cheer: o+=confetti(t)
    else:
        o+=room(1.0)+door(0.35,0.7,0,t=t)+rug()+plant(900,1040,1.1,3*math.sin(t*1.4))
        o+=boy(300+EX(lt),1075+EY(lt),t,mood='open' if MOUTH[min(f,len(MOUTH)-1)]>0.35 else 'smile',armR=60+25*math.sin(t*6),lean=3)
        o+=confetti(t)+sparkles(t,12,120,960,480,1100,6)
        k=pop((t-gs(28))/0.5)
        o+=f'<g transform="translate(540,1245) scale({k:.3f}) translate(-540,-1245)"><rect x="110" y="1185" width="860" height="120" rx="60" fill="#fff"/><circle cx="190" cy="1245" r="38" fill="#1F7A63"/><path d="M174 1232 h32 a6 6 0 0 1 6 6 v14 a6 6 0 0 1 -6 6 h-18 l-10 9 v-9 a6 6 0 0 1 -4 -6 v-14 a6 6 0 0 1 4 -6 z" fill="#fff"/><text x="260" y="1236" font-family="Poppins" font-weight="700" font-size="32" fill="#1d2a26">Follow BeYourBest &amp;</text><text x="260" y="1280" font-family="Poppins" font-weight="700" font-size="32" fill="#1F7A63">tulis topik berikutnya di komentar</text></g>'
    o+=dust(t)
    return f'<g transform="translate({fx+pxx:.1f},{fy}) rotate({rot:.2f}) scale({z:.4f}) translate({-fx},{-fy})"><g transform="translate(0,70)">{o}</g></g>'

# ---------- overlay ----------
TITLES=[(0,'MINDSET · PEMBUKA','Pernah bilang','*nggak bisa*?'),(2,'GANTI SATU KATA','Ganti *satu kata*','saja'),(3,'GANTI SATU KATA','Dari *nggak bisa*','jadi *belum* bisa'),
(6,'DUA CARA BERPIKIR','Dua pola pikir','*tetap* vs *bertumbuh*'),(8,'POLA PIKIR TETAP','Kemampuan itu','*sudah dari lahir*'),(11,'POLA PIKIR BERTUMBUH','Kemampuan itu','*bisa dilatih*'),
(14,'ANALOGI','Bayi belajar jalan','*jatuh* berkali-kali'),(18,'KATA KUNCI','Kata *belum*','membuka pintu'),(19,'KATA KUNCI','Kata *nggak bisa*','menguncinya'),
(20,'TIGA LANGKAH','Mulai hari ini','*tiga langkah*'),(22,'LANGKAH 1','Ganti *nggak bisa*','jadi *belum bisa*'),(24,'LANGKAH 2','Tanya satu hal kecil','yang bisa *dilatih*'),
(26,'LANGKAH 3','Rayakan *kemajuan*','bukan cuma hasil akhir'),(28,'BEYOURBEST','Topik apa lagi','yang mau *kita bahas*?')]
def rich(txt,col='#1d2a26',kw='#1F7A63'):
    out='';parts=txt.split('*')
    for i,p in enumerate(parts):
        if p: out+=f'<tspan fill="{kw if i%2 else col}">{p.replace("&","&amp;")}</tspan>'
    return out
def title(t):
    cur=None
    for g,l,a,b in TITLES:
        if t>=gs(g)-0.08 if g>0 else True: cur=(g,l,a,b)
    g,l,a,b=cur;t0=gs(g)-0.08 if g>0 else 0.0
    u=eo((t-t0)/0.35);dy=(1-u)*26
    return (f'<rect width="1080" height="380" fill="url(#panel)"/><g opacity="{u:.2f}" transform="translate(0,{dy:.1f})"><text x="540" y="178" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="26" letter-spacing="6" fill="#55594c">{l}</text>'
            f'<text x="540" y="246" text-anchor="middle" xml:space="preserve" font-family="Poppins" font-weight="700" font-size="58">{rich(a)}</text><text x="540" y="312" text-anchor="middle" xml:space="preserve" font-family="Poppins" font-weight="700" font-size="58">{rich(b)}</text></g>')
def watermark(t):
    u=eo((t-0.3)/0.3)
    return (f'<g opacity="{u:.2f}"><rect x="350" y="42" width="380" height="64" rx="32" fill="#1E3A34"/><circle cx="396" cy="74" r="15" fill="#8ff0c8"/><path d="M396 83 L396 66 M396 74 C402 70 404 67 404 62 C399 63 396 67 396 74 Z" stroke="#1E3A34" stroke-width="3" fill="#1E3A34" stroke-linecap="round"/>'
            '<text x="428" y="87" font-family="Poppins" font-weight="700" font-size="36" fill="#fff">Be<tspan fill="#8ff0c8">Your</tspan>Best</text></g>')
ALL=[p for g in GR for p in g['phrases']]
SP=FB.getlength(' ')
def layout(p):
    ws=[w['w'] for w in p['words']];tot=FB.getlength(' '.join(ws))
    if tot<=850: lines=[list(range(len(ws)))]
    else:
        best=None
        for k in range(1,len(ws)):
            a=FB.getlength(' '.join(ws[:k]));b=FB.getlength(' '.join(ws[k:]));m=max(a,b)
            if best is None or m<best[0]: best=(m,k)
        k=best[1];lines=[list(range(k)),list(range(k,len(ws)))]
    ys=[1541] if len(lines)==1 else [1517,1573]
    pos={}
    for li,ln in enumerate(lines):
        lw=FB.getlength(' '.join(ws[i] for i in ln));x=540-lw/2
        for i in ln:
            w=FB.getlength(ws[i]);pos[i]=(x,w,ys[li]);x+=w+SP
    return lines,ys,pos
LAY=[layout(p) for p in ALL]
def subtitle(t):
    cur=None
    for i,p in enumerate(ALL):
        if t>=p['start']-0.08: cur=i
    if cur is None: return ''
    p=ALL[cur]
    if t>p['end']+0.35: return ''
    lines,ys,pos=LAY[cur];ws=p['words']
    s='<rect x="80" y="1456" width="920" height="134" rx="40" fill="#1E3A34" opacity="0.92"/>'
    # kata aktif
    act=None
    for i,w in enumerate(ws):
        nxt=ws[i+1]['start'] if i+1<len(ws) else w['end']+0.12
        if w['start']-0.06<=t<max(nxt,w['end']+0.06): act=i
    if act is not None:
        x,w,y=pos[act];al=cl((t-(ws[act]['start']-0.06))/0.06)
        s+=f'<rect x="{x-12:.1f}" y="{y-47}" width="{w+24:.1f}" height="64" rx="16" fill="#8ff0c8" fill-opacity="{0.26*al:.2f}"/><rect x="{x-12:.1f}" y="{y-47}" width="{w+24:.1f}" height="64" rx="16" fill="url(#hatch)" opacity="{0.6*al:.2f}"/>'
    for ln,y in zip(lines,ys):
        txt=' '.join(ws[i]['w'] for i in ln).replace('&','&amp;')
        s+=f'<text x="540" y="{y}" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="52" fill="#fff">{txt}</text>'
    return s
def mascot(t,f):
    k=pop((t-0.15)/0.4)
    if k<=0: return ''
    o=MOUTH[min(f,len(MOUTH)-1)];blink=(t%3.0)<0.12
    wave=0.0
    if t<3.2 or t>gs(28) or (gs(26)+0.6<t<gs(28)): wave=22+26*math.sin(t*9)
    nod=3.0*min(o,1.0)+1.2*math.sin(t*2.0)
    sway=1.4*math.sin(t*1.6)
    HJ='#3b8f8a';HD='#2d726e'
    mo=f'<ellipse cx="850" cy="1366" rx="9" ry="{3+9*min(o,1):.1f}" fill="#8a2d3e"/>' if o>0.12 else '<path d="M839 1363 Q850 1372 861 1363" stroke="#c4506a" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    eyes='<line x1="827" y1="1335" x2="839" y2="1335" stroke="#3a2b20" stroke-width="4"/><line x1="861" y1="1335" x2="873" y2="1335" stroke="#3a2b20" stroke-width="4"/>' if blink else '<circle cx="833" cy="1335" r="4.5" fill="#3a2b20"/><circle cx="867" cy="1335" r="4.5" fill="#3a2b20"/><path d="M820 1324 l6 4 M880 1324 l-6 4" stroke="#3a2b20" stroke-width="2.5" stroke-linecap="round"/>'
    return (f'<g transform="translate(850,1860) rotate({sway:.2f}) scale({k:.3f}) translate(-850,-1545)"><ellipse cx="850" cy="1545" rx="95" ry="14" fill="#000" opacity="0.25"/>'
    '<rect x="826" y="1496" width="17" height="40" rx="6" fill="#2b2f45"/><rect x="858" y="1496" width="17" height="40" rx="6" fill="#2b2f45"/><ellipse cx="830" cy="1540" rx="24" ry="9" fill="#1a1a1a"/><ellipse cx="872" cy="1540" rx="24" ry="9" fill="#1a1a1a"/>'
    '<path d="M788 1388 Q850 1366 912 1388 L934 1508 L766 1508 Z" fill="#fafafa" stroke="#d6d6d6" stroke-width="3"/><path d="M850 1390 L850 1506" stroke="#d6d6d6" stroke-width="3"/>'
    f'<g transform="rotate({wave:.1f} 786 1405)"><rect x="768" y="1400" width="30" height="90" rx="14" fill="#fafafa" stroke="#d6d6d6" stroke-width="3"/><circle cx="783" cy="1494" r="12" fill="#f4cfae"/></g>'
    '<g transform="rotate(-8 928 1450)"><rect x="900" y="1410" width="62" height="80" rx="6" fill="#8b5a3c"/><rect x="908" y="1420" width="46" height="62" rx="3" fill="#fff"/><line x1="914" y1="1436" x2="948" y2="1436" stroke="#999" stroke-width="3"/><line x1="914" y1="1450" x2="948" y2="1450" stroke="#999" stroke-width="3"/><line x1="914" y1="1464" x2="940" y2="1464" stroke="#999" stroke-width="3"/></g>'
    '<rect x="905" y="1425" width="28" height="70" rx="12" fill="#fafafa" stroke="#d6d6d6" stroke-width="3" transform="rotate(10 919 1460)"/>'
    f'<g transform="translate(0,{nod+12:.1f})">'
    f'<path d="M800 1340 C790 1268 910 1268 900 1340 C904 1368 926 1388 938 1420 C902 1442 798 1442 762 1420 C774 1388 796 1368 800 1340 Z" fill="{HJ}" stroke="{HD}" stroke-width="3"/>'
    f'<path d="M812 1402 C826 1418 838 1428 850 1434 M888 1402 C874 1418 862 1428 850 1434" stroke="{HD}" stroke-width="3" fill="none" opacity="0.55"/>'
    '<path d="M826 1412 C818 1442 840 1458 850 1448 C860 1458 882 1442 874 1412" stroke="#33384a" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="850" cy="1454" r="8" fill="#c9d1d9" stroke="#33384a" stroke-width="3"/>'
    f'<ellipse cx="850" cy="1338" rx="44" ry="47" fill="#f4cfae" stroke="{HD}" stroke-width="4"/>'
    '<circle cx="818" cy="1354" r="9" fill="#ff9a9a" opacity="0.55"/><circle cx="882" cy="1354" r="9" fill="#ff9a9a" opacity="0.55"/>'
    '<circle cx="833" cy="1335" r="15" fill="none" stroke="#2a6f78" stroke-width="4"/><circle cx="867" cy="1335" r="15" fill="none" stroke="#2a6f78" stroke-width="4"/><line x1="848" y1="1335" x2="852" y2="1335" stroke="#2a6f78" stroke-width="4"/>'
    f'{eyes}{mo}</g></g>')

RED='#d9483b';GRN='#1F7A63'
def chip(cx,cy,w,h,txt,fill,tc='#fff',sx=1.0,sy=1.0,rot=0.0,fs=46,op=1.0):
    if sx<=0 or sy<=0 or op<=0: return ''
    r=h/2.6
    return (f'<g opacity="{op:.2f}" transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f}) scale({sx:.3f},{sy:.3f})"><rect x="{-w/2+6}" y="{-h/2+9}" width="{w}" height="{h}" rx="{r:.0f}" fill="#000" opacity="0.22"/>'
            f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="{r:.0f}" fill="{fill}" stroke="#fff" stroke-width="6"/><text x="0" y="{fs*0.36:.0f}" text-anchor="middle" font-family="Poppins" font-weight="700" font-size="{fs}" fill="{tc}">{txt}</text></g>')
def flip(t,t0,tf,a,ca,b,cb,cx,cy,w,h):
    if t<t0: return ''
    k=pop((t-t0)/0.4)
    if t<tf:
        rot=(5*math.sin(t*38) if t>tf-0.7 else 1.5*math.sin(t*3))
        return chip(cx,cy,w,h,a,ca,sx=k,sy=k,rot=rot)
    u=(t-tf)/0.5
    if u<1:
        return chip(cx,cy,w,h,a if u<0.5 else b,ca if u<0.5 else cb,sx=max(abs(math.cos(math.pi*u)),0.001))
    pu=1+0.04*math.sin((t-tf)*5)
    return chip(cx,cy,w,h,b,cb,sx=pu,sy=pu)+(sparkles(t,10,cx-w/2,cx+w/2,cy-h,cy+h*0.4,11,'#fff3a8',18) if u<3 else '')
def xmark(x,y,r,col='#fff'):
    return f'<path d="M{x-r} {y-r} L{x+r} {y+r} M{x+r} {y-r} L{x-r} {y+r}" stroke="{col}" stroke-width="7" stroke-linecap="round"/>'
def check(x,y,r,col='#fff'):
    return f'<path d="M{x-r} {y} L{x-r*0.25} {y+r*0.75} L{x+r} {y-r*0.7}" stroke="{col}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
def barcard(t,fill,col,icon,k,shake=0.0):
    s=f'<g transform="translate(0,26)"><g transform="translate(540,1245) scale({k:.3f}) translate(-540,-1245)"><rect x="116" y="1194" width="860" height="120" rx="40" fill="#000" opacity="0.2"/><rect x="110" y="1185" width="860" height="120" rx="40" fill="#fff" opacity="0.96"/>'
    s+='<text x="150" y="1226" font-family="DejaVu Sans Mono" font-size="22" letter-spacing="4" fill="#55594c">KEMAMPUAN</text>'
    s+=f'<rect x="150" y="1246" width="640" height="34" rx="17" fill="#dfe3d8"/><rect x="150" y="1246" width="{max(8,640*fill):.0f}" height="34" rx="17" fill="{col}"/>'
    if icon=='lock': s+=f'<g transform="rotate({shake:.1f} 880 1245)">'+padlock(880,1252,1.0,'#8a909c','#6b7280')+'</g>'
    else: s+=star(880,1245,40,'#ffd34d',1.0,t*60)
    return s+'</g></g>'
def cards(t):
    o=''
    # --- kartu kata: NGGAK BISA -> BELUM BISA (hook + ganti satu kata)
    t0=wordt(1,0,'nggak')-0.05;tf=wordt(2,0,'kata');te=gs(6)-0.08
    if t0<=t<te: o+=flip(t,t0,tf,'NGGAK BISA',RED,'BELUM BISA',GRN,690,830,430,112)
    # --- dua pola pikir
    a,b=gs(6)-0.08,gs(8)-0.08
    if a<=t<b:
        o+=chip(260,1245,300,84,'TETAP','#6b7280',sx=pop((t-a-0.2)/0.4),sy=pop((t-a-0.2)/0.4),fs=40)
        k=pop((t-gs(7)+0.1)/0.45)
        if k>0:
            o+=chip(820,1245,360,84,'BERTUMBUH',GRN,sx=k,sy=k,fs=40)
            o+=chip(540,860,110,110,'VS','#1E3A34',sx=pop((t-gs(7)-0.1)/0.4),sy=pop((t-gs(7)-0.1)/0.4),rot=6*math.sin(t*3),fs=42)
    # --- bar kemampuan: tetap
    a,b=gs(8)-0.08,gs(11)-0.08
    if a<=t<b:
        lt=t-a;f=0.35+0.2*max(0,math.sin(lt*3.0))**2
        o+=barcard(t,f,'#8a909c','lock',pop((lt)/0.4),shake=7*math.sin(t*25) if math.sin(lt*3.0)>0.7 else 0)
        if t>wordt(10,0,'tidak')-0.1: o+=chip(540,1130,300,84,'TERKUNCI',RED,sx=pop((t-wordt(10,0,'tidak')+0.1)/0.4),sy=pop((t-wordt(10,0,'tidak')+0.1)/0.4),rot=3*math.sin(t*14),fs=38)
    # --- bar kemampuan: bertumbuh
    a,b=gs(11)-0.08,gs(14)-0.08
    if a<=t<b:
        lt=t-a;f=0.35+0.65*sm(lt/(b-a-0.2))
        o+=barcard(t,f,GRN,'star',pop(lt/0.4))
        o+=sparkles(t,8,150+640*f-60,150+640*f+60,1180,1290,5,'#fff3a8',16)
        if t>wordt(13,0,'belum')-0.1: o+=chip(540,1130,380,84,'BELUM SAMPAI','#e29a1a',sx=pop((t-wordt(13,0,'belum')+0.1)/0.4),sy=pop((t-wordt(13,0,'belum')+0.1)/0.4),fs=36)
    # --- bayi: tally percobaan
    a,b=gs(14)-0.08,gs(18)-0.08
    if a<=t<b:
        lt=t-a
        tf1=gs(15)-0.05
        nt=int(((tf1-gs(14))-1.1)//3.0)+1 if tf1-gs(14)>=1.1 else 0
        if t<tf1: n=int((t-gs(14)-1.1)//3.0)+1 if t-gs(14)>=1.1 else 0
        elif t<gs(16)-0.05:
            tt=t-gs(15);n=nt+(int((tt-0.5)//1.6)+1 if tt>=0.5 else 0)
        else: n=5
        n=min(5,n);walk=t>=gs(16)-0.05
        s=f'<g transform="translate(0,26)"><g transform="translate(540,1245) scale({pop(lt/0.4):.3f}) translate(-540,-1245)"><rect x="116" y="1194" width="860" height="120" rx="40" fill="#000" opacity="0.2"/><rect x="110" y="1185" width="860" height="120" rx="40" fill="#fff" opacity="0.96"/>'
        s+=f'<text x="150" y="1240" font-family="DejaVu Sans Mono" font-size="24" letter-spacing="4" fill="{GRN if walk else "#55594c"}">{"TERUS MENCOBA" if walk else "PERCOBAAN"}</text>'
        for i in range(5):
            cx=560+i*84;cy=1246
            if walk:
                kk=pop((t-gs(16)-0.1*i)/0.35);s+=f'<g transform="translate({cx},{cy}) scale({kk:.3f}) translate({-cx},{-cy})"><circle cx="{cx}" cy="{cy}" r="29" fill="{GRN}"/>{check(cx,cy,13)}</g>'
            elif i<n:
                s+=f'<circle cx="{cx}" cy="{cy}" r="29" fill="{RED}"/>{xmark(cx,cy,11)}'
            else: s+=f'<circle cx="{cx}" cy="{cy}" r="27" fill="none" stroke="#c9cdc2" stroke-width="6"/>'
        o+=s+'</g></g>'
    # --- pintu: BELUM / NGGAK BISA
    a,b=gs(18)-0.08,gs(20)-0.08
    if a<=t<b:
        tb=wordt(18,0,'belum')-0.05;tn=wordt(19,0,'nggak')-0.05
        if tb<=t<tn:
            k=pop((t-tb)/0.4);o+=chip(540,1272,380,112,'BELUM',GRN,sx=k,sy=k,rot=2*math.sin(t*4),fs=54)+sparkles(t,8,360,720,1190,1330,9,'#fff3a8',16)
        elif t>=tn:
            u=eo((t-tn)/0.35);y=1000+272*u;o+=chip(540,y,470,112,'NGGAK BISA',RED,sx=1,sy=1,rot=(5*math.sin(t*34) if t-tn>0.3 and t-tn<1.2 else 0),fs=50)
    # --- tiga langkah
    a,b=gs(20)-0.08,gs(28)-0.08
    if a<=t<b:
        t1=gs(22)-0.1;t2=gs(24)-0.1;t3=gs(26)-0.1
        if t1<=t<t2: o+=flip(t,t1,wordt(23,0,'jadi'),'NGGAK BISA',RED,'BELUM BISA',GRN,540,600,420,108)
        elif t2<=t<t3:
            k=pop((t-t2)/0.4);cx,cy=370,620
            s=f'<g transform="translate({cx},{cy}) scale({k:.3f})"><circle r="104" fill="#000" opacity="0.2" cx="6" cy="9"/><circle r="104" fill="#fff" stroke="{RED}" stroke-width="10"/><circle r="70" fill="{RED}"/><circle r="40" fill="#fff"/><circle r="16" fill="{RED}"/></g>'
            ta=wordt(25,0,'kecil')-0.35;u=cl((t-ta)/0.3)
            if t>=ta-0.3:
                ax=cx+(1-eo(u))*230;ay=cy-(1-eo(u))*230
                s+=f'<g transform="rotate(45 {ax:.0f} {ay:.0f})"><line x1="{ax-70:.0f}" y1="{ay:.0f}" x2="{ax:.0f}" y2="{ay:.0f}" stroke="#1E3A34" stroke-width="9" stroke-linecap="round"/><polygon points="{ax:.0f},{ay-14:.0f} {ax+28:.0f},{ay:.0f} {ax:.0f},{ay+14:.0f}" fill="#1E3A34"/></g>'
            if t>=ta+0.3:
                kk=pop((t-ta-0.3)/0.4);s+=chip(cx+330,cy,300,84,'1 HAL KECIL',GRN,sx=kk,sy=kk,fs=36)+sparkles(t,8,cx-120,cx+120,cy-110,cy+110,3,'#fff3a8',16)
            o+=s
        elif t>=t3:
            cx,cy=540,610;k=pop((t-t3)/0.4)
            s=f'<g transform="translate({cx},{cy}) scale({k:.3f})"><rect x="-150" y="-110" width="300" height="240" rx="36" fill="#000" opacity="0.2" transform="translate(6,9)"/><rect x="-150" y="-110" width="300" height="240" rx="36" fill="#fff" stroke="{GRN}" stroke-width="8"/>'
            for i,hh in enumerate((50,100,150)):
                gk=eo((t-t3-0.3-0.35*i)/0.6)
                s+=f'<rect x="{-100+i*72}" y="{100-hh*gk:.0f}" width="56" height="{hh*gk:.0f}" rx="10" fill="{GRN if i<2 else "#e29a1a"}"/>'
            s+='</g>'
            if t>t3+1.5: s+=star(cx+110,cy-100,34*pop((t-t3-1.5)/0.4),'#ffd34d',1.0,t*70)
            o+=s
    # --- penutup: hati dan komentar naik
    a=gs(28)-0.08
    if t>=a:
        for i in range(6):
            ph=((t-a)*0.45+i*0.17)%1.0
            x=170+i*150+20*math.sin((t-a)*2+i);y=1170-ph*330
            al=math.sin(ph*math.pi);sc=0.6+0.5*al
            if i%2==0: o+=f'<path transform="translate({x:.0f},{y:.0f}) scale({sc:.2f})" d="M0 -10 C-16 -30 -40 -4 0 26 C40 -4 16 -30 0 -10 Z" fill="#ff5d73" opacity="{al:.2f}"/>'
            else: o+=f'<g transform="translate({x:.0f},{y:.0f}) scale({sc:.2f})" opacity="{al:.2f}"><rect x="-26" y="-20" width="52" height="38" rx="14" fill="#1F7A63"/><path d="M-10 18 L-16 30 L4 18 Z" fill="#1F7A63"/><circle cx="-12" cy="-1" r="4" fill="#fff"/><circle cx="0" cy="-1" r="4" fill="#fff"/><circle cx="12" cy="-1" r="4" fill="#fff"/></g>'
        pr=((t-a)%1.3)/1.3
        o+=f'<rect x="{110-60*pr:.0f}" y="{1185-60*pr:.0f}" width="{860+120*pr:.0f}" height="{120+120*pr:.0f}" rx="{40+30*pr:.0f}" fill="none" stroke="#8ff0c8" stroke-width="6" opacity="{(1-pr)*0.8:.2f}"/>'
    return o

SCS=None
def band(t):
    starts=[gs(i)-0.08 for i in (2,6,8,11,14,18,20,28)]
    for s0 in starts:
        u=(t-(s0-0.16))/0.46
        if 0<=u<=1:
            cx=-1000+3080*sm(u);sk=220
            return (f'<polygon points="{cx-560+sk:.0f},-10 {cx+560+sk:.0f},-10 {cx+560-sk:.0f},1930 {cx-560-sk:.0f},1930" fill="#1F7A63" opacity="0.96"/>'
                    f'<polygon points="{cx+560+sk:.0f},-10 {cx+590+sk:.0f},-10 {cx+590-sk:.0f},1930 {cx+560-sk:.0f},1930" fill="#8ff0c8"/>')
    return ''
def frame_svg(t):
    global CT
    CT=t
    f=int(round(t*FPS))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">'+DEFS+scene(t)+'<rect width="1080" height="1920" fill="url(#vig)"/>'+cards(t)+band(t)
            +title(t)+watermark(t)+'<text x="540" y="1430" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="22" letter-spacing="4" fill="#fff" opacity="0.85">ILUSTRASI DISEDERHANAKAN</text>'
            +subtitle(t)+mascot(t,f)+'</svg>')
def png(t):
    return subprocess.run(['rsvg-convert','-f','png'],input=frame_svg(t).encode(),capture_output=True,check=True).stdout
NF=int((DUR+0.3)*FPS)
if __name__=='__main__':
    m=sys.argv[1]
    if m=='still':
        for a in sys.argv[3:]:
            open(f'still_{a}.png','wb').write(png(float(a)))
    elif m=='range':
        a,b,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        p=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','image2pipe','-framerate',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for fr in range(a,b): p.stdin.write(png(fr/FPS))
        p.stdin.close();p.wait();print('range ok',a,b)
    elif m=='chunk':
        i,n,out=int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
        a=NF*i//n;b=NF*(i+1)//n
        p=subprocess.Popen(['ffmpeg','-loglevel','error','-y','-f','image2pipe','-framerate',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
        for fr in range(a,b): p.stdin.write(png(fr/FPS))
        p.stdin.close();p.wait();print('chunk',i,'ok',a,b)
