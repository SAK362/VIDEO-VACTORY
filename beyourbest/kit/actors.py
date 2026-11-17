# Pemeran BeYourBest: bebas jenis, jumlah, usia, gender. Tata letak maskot/watermark/subtitle TIDAK diubah.
# actor(x,y,t,kind,...) -> SVG group. (x,y)=tengah kaki. s=skala. Dipakai di dalam scene() menggantikan boy().
import math

SKIN={'terang':'#f6d3b3','sawo':'#e2ad85','cokelat':'#c08a62','gelap':'#8d5a3c'}
PRESET={
 'anak_laki':   dict(leg=50,tor=85,hr=44,sw=34,hw=30,arm=62,skin=SKIN['sawo'],hair='short',hc='#3a2216',top='#e8554a',bot='#2b3f6e',style='pants',shoe='#fff'),
 'anak_perempuan':dict(leg=48,tor=85,hr=44,sw=32,hw=34,arm=60,skin=SKIN['terang'],hair='pigtails',hc='#2a1a14',top='#f2a63b',bot='#f2a63b',style='dress',shoe='#d9442f'),
 'remaja_laki': dict(leg=80,tor=118,hr=42,sw=46,hw=40,arm=92,skin=SKIN['cokelat'],hair='short',hc='#1f1a18',top='#4aa38a',bot='#33384a',style='pants',shoe='#fff'),
 'remaja_perempuan':dict(leg=78,tor=112,hr=41,sw=42,hw=38,arm=88,skin=SKIN['sawo'],hair='long',hc='#2a1a14',top='#7e6bd1',bot='#33384a',style='pants',shoe='#fff'),
 'pria':        dict(leg=96,tor=142,hr=45,sw=58,hw=48,arm=106,skin=SKIN['sawo'],hair='short',hc='#2a1c14',top='#3c6fa8',bot='#2e3440',style='pants',shoe='#1a1a1a',tie='#c0392b'),
 'wanita':      dict(leg=92,tor=130,hr=43,sw=48,hw=44,arm=98,skin=SKIN['terang'],hair='long',hc='#3b2417',top='#c85a7c',bot='#3a3f5c',style='skirt',shoe='#1a1a1a'),
 'ibu_hijab':   dict(leg=90,tor=130,hr=43,sw=48,hw=46,arm=98,skin=SKIN['sawo'],hair='hijab',hc='#c9a24b',top='#7a5a9a',bot='#7a5a9a',style='dress',shoe='#1a1a1a'),
 'kakek':       dict(leg=86,tor=132,hr=44,sw=52,hw=46,arm=98,skin=SKIN['cokelat'],hair='bald',hc='#e6e6ea',top='#8a6d4b',bot='#5a5f6b',style='pants',shoe='#3a2a20',glasses=True,beard=True,cane=True,old=True,stoop=-7),
 'nenek':       dict(leg=82,tor=126,hr=42,sw=44,hw=46,arm=92,skin=SKIN['terang'],hair='bun',hc='#e8e8ea',top='#7f6fb0',bot='#7f6fb0',style='dress',shoe='#5a3a2a',glasses=True,cane=True,old=True,stoop=-6),
 'pria_berjenggot':dict(leg=96,tor=142,hr=45,sw=60,hw=50,arm=106,skin=SKIN['gelap'],hair='short',hc='#1a1412',top='#e0a526',bot='#2e3440',style='pants',shoe='#1a1a1a',beard=True),
}

def actor(x,y,t,kind='pria',s=1.0,mood='smile',armL=0.0,armR=0.0,lean=0.0,look=0.0,sy=None,**ov):
    P=dict(PRESET[kind]);P.update(ov)
    leg,tor,hr,sw,hw,arm=P['leg'],P['tor'],P['hr'],P['sw'],P['hw'],P['arm']
    skin,hair,hc,top,bot=P['skin'],P['hair'],P['hc'],P['top'],P['bot']
    br=1+0.012*math.sin(t*2*math.pi/2.6) if sy is None else sy
    ph=hash(kind)%7
    armL+=2.5*math.sin(t*1.3+ph);armR+=2.5*math.sin(t*1.3+1.5+ph)
    lean+=P.get('stoop',0)+1.6*math.sin(t*0.9+ph);look+=2.5*math.sin(t*0.7+ph)
    blink=1.0 if ((t+ph*0.4)%3.3)>0.14 else 0.1
    yh=-leg;ys=-leg-tor;cy=ys-hr*0.95-8
    o=f'<g transform="translate({x:.1f},{y:.1f}) scale({s})"><ellipse cx="0" cy="0" rx="{hw*1.5:.0f}" ry="13" fill="#000" opacity="0.22"/>'
    # kaki
    st=P['style']
    if st=='pants':
        o+=f'<rect x="{-hw*0.78:.0f}" y="{yh}" width="{hw*0.62:.0f}" height="{leg-8}" rx="8" fill="{bot}"/><rect x="{hw*0.16:.0f}" y="{yh}" width="{hw*0.62:.0f}" height="{leg-8}" rx="8" fill="{bot}"/>'
    else:
        o+=f'<rect x="{-hw*0.55:.0f}" y="{-leg*0.5:.0f}" width="{hw*0.4:.0f}" height="{leg*0.5-8:.0f}" rx="6" fill="{skin}"/><rect x="{hw*0.15:.0f}" y="{-leg*0.5:.0f}" width="{hw*0.4:.0f}" height="{leg*0.5-8:.0f}" rx="6" fill="{skin}"/>'
    o+=f'<ellipse cx="{-hw*0.45:.0f}" cy="-4" rx="{hw*0.6:.0f}" ry="11" fill="{P["shoe"]}"/><ellipse cx="{hw*0.45:.0f}" cy="-4" rx="{hw*0.6:.0f}" ry="11" fill="{P["shoe"]}"/>'
    # badan (napas)
    o+=f'<g transform="translate(0,{yh*(1-br):.1f}) scale(1,{br:.4f})">'
    aw=26 if P['hr']>=42 and leg>60 else 22
    def armsvg(sx,ang,flip):
        sl=arm*0.55
        return (f'<g transform="rotate({ang:.1f} {sx} {ys+10})"><rect x="{sx-aw//2}" y="{ys+4}" width="{aw}" height="{arm}" rx="{aw//2}" fill="{skin}"/><rect x="{sx-aw//2-2}" y="{ys+4}" width="{aw+4}" height="{sl:.0f}" rx="{aw//2}" fill="{top}"/></g>')
    o+=armsvg(-sw-2,armL,0)+armsvg(sw+2,-armR,1)
    if st=='pants': o+=f'<path d="M{-sw} {ys} L{sw} {ys} L{hw+4} {yh} L{-hw-4} {yh} Z" fill="{top}"/>'
    elif st=='skirt':
        o+=f'<path d="M{-sw} {ys} L{sw} {ys} L{hw} {yh} L{-hw} {yh} Z" fill="{top}"/><path d="M{-hw-2} {yh-6} L{hw+2} {yh-6} L{hw*1.45:.0f} {-leg*0.42:.0f} L{-hw*1.45:.0f} {-leg*0.42:.0f} Z" fill="{bot}"/>'
    else:
        o+=f'<path d="M{-sw} {ys} L{sw} {ys} L{hw*1.25:.0f} {-leg*0.4:.0f} L{-hw*1.25:.0f} {-leg*0.4:.0f} Z" fill="{top}"/><path d="M{-sw*0.6:.0f} {ys} Q0 {ys+22} {sw*0.6:.0f} {ys}" stroke="#fff" stroke-opacity="0.35" stroke-width="5" fill="none"/>'
    if P.get('tie'):
        o+=f'<path d="M-9 {ys} L9 {ys} L5 {ys+14} L12 {ys+tor*0.7:.0f} L0 {ys+tor*0.78:.0f} L-12 {ys+tor*0.7:.0f} L-5 {ys+14} Z" fill="{P["tie"]}"/><path d="M{-sw*0.4:.0f} {ys} L0 {ys+16} L{sw*0.4:.0f} {ys} L{sw*0.28:.0f} {ys-6} L0 {ys+4} L{-sw*0.28:.0f} {ys-6} Z" fill="#fff"/>'
    if P.get('cane'):
        hx=sw+2+ (arm*math.sin(math.radians(-armR))*-1)
        o+=f'<line x1="{sw+34}" y1="{ys+tor*0.55:.0f}" x2="{sw+38}" y2="-2" stroke="#7a4a2c" stroke-width="7" stroke-linecap="round"/><path d="M{sw+34} {ys+tor*0.55:.0f} q-4 -18 -18 -14" stroke="#7a4a2c" stroke-width="7" fill="none" stroke-linecap="round"/>'
    # kepala
    mouth={'smile':(f'M{-hr*0.28:.0f} {cy+hr*0.42:.0f} Q0 {cy+hr*0.62:.0f} {hr*0.28:.0f} {cy+hr*0.42:.0f}','none'),
           'flat':(f'M{-hr*0.22:.0f} {cy+hr*0.5:.0f} L{hr*0.22:.0f} {cy+hr*0.5:.0f}','none'),
           'sad':(f'M{-hr*0.26:.0f} {cy+hr*0.58:.0f} Q0 {cy+hr*0.4:.0f} {hr*0.26:.0f} {cy+hr*0.58:.0f}','none'),
           'open':(f'M{-hr*0.3:.0f} {cy+hr*0.4:.0f} Q0 {cy+hr*0.8:.0f} {hr*0.3:.0f} {cy+hr*0.4:.0f} Z','#7a2d2d')}[mood]
    o+=f'<g transform="rotate({lean:.1f} 0 {ys})"><rect x="-10" y="{ys-14}" width="20" height="22" fill="{skin}"/>'
    # rambut belakang
    if hair=='long': o+=f'<path d="M{-hr-6} {cy} L{-hr-8} {cy+hr*1.7:.0f} Q{-hr+8} {cy+hr*1.9:.0f} {-hr*0.55:.0f} {cy+hr*1.5:.0f} L{-hr*0.5:.0f} {cy+hr*0.2:.0f} L{hr*0.5:.0f} {cy+hr*0.2:.0f} L{hr*0.55:.0f} {cy+hr*1.5:.0f} Q{hr-8} {cy+hr*1.9:.0f} {hr+8} {cy+hr*1.7:.0f} L{hr+6} {cy} Z" fill="{hc}"/>'
    if hair=='hijab': o+=f'<path d="M{-hr-8} {cy} C{-hr-10} {cy-hr-24:.0f} {hr+10} {cy-hr-24:.0f} {hr+8} {cy} C{hr+10} {cy+hr*0.9:.0f} {hr+34} {cy+hr*1.5:.0f} {hr+40} {ys+tor*0.45:.0f} C{hr*0.5:.0f} {ys+tor*0.62:.0f} {-hr*0.5:.0f} {ys+tor*0.62:.0f} {-hr-40} {ys+tor*0.45:.0f} C{-hr-34} {cy+hr*1.5:.0f} {-hr-10} {cy+hr*0.9:.0f} {-hr-8} {cy} Z" fill="{hc}" stroke="#00000022" stroke-width="3"/>'
    o+=f'<ellipse cx="{-hr:.0f}" cy="{cy+4}" rx="7" ry="10" fill="{skin}"/><ellipse cx="{hr:.0f}" cy="{cy+4}" rx="7" ry="10" fill="{skin}"/><ellipse cx="0" cy="{cy}" rx="{hr}" ry="{hr*1.04:.0f}" fill="{skin}"/>'
    # rambut depan
    cap=f'<path d="M{-hr-3} {cy-4} C{-hr-8} {cy-hr-16:.0f} {hr+8} {cy-hr-16:.0f} {hr+3} {cy-4} C{hr*0.55:.0f} {cy-hr*0.6:.0f} {-hr*0.55:.0f} {cy-hr*0.6:.0f} {-hr-3} {cy-4} Z" fill="{hc}"/>'
    if hair in('short','long'): o+=cap
    elif hair=='pigtails': o+=cap+f'<circle cx="{-hr-12:.0f}" cy="{cy+hr*0.5:.0f}" r="{hr*0.3:.0f}" fill="{hc}"/><circle cx="{hr+12:.0f}" cy="{cy+hr*0.5:.0f}" r="{hr*0.3:.0f}" fill="{hc}"/>'
    elif hair=='bun': o+=cap+f'<circle cx="0" cy="{cy-hr-8:.0f}" r="{hr*0.4:.0f}" fill="{hc}"/>'
    elif hair=='bald': o+=f'<ellipse cx="{-hr+2:.0f}" cy="{cy-2}" rx="7" ry="14" fill="{hc}"/><ellipse cx="{hr-2:.0f}" cy="{cy-2}" rx="7" ry="14" fill="{hc}"/><path d="M{-hr*0.6:.0f} {cy-hr*0.8:.0f} q{hr*0.6:.0f} -10 {hr*1.2:.0f} 0" stroke="#fff" stroke-opacity="0.5" stroke-width="5" fill="none" stroke-linecap="round"/>'
    elif hair=='hijab': o+=f'<path d="M{-hr*0.86:.0f} {cy-hr*0.2:.0f} C{-hr*0.6:.0f} {cy-hr*0.98:.0f} {hr*0.6:.0f} {cy-hr*0.98:.0f} {hr*0.86:.0f} {cy-hr*0.2:.0f}" stroke="{hc}" stroke-width="11" fill="none" stroke-linecap="round"/>'
    if P.get('beard'): o+=f'<path d="M{-hr*0.86:.0f} {cy+2} C{-hr*0.9:.0f} {cy+hr*1.2:.0f} {hr*0.9:.0f} {cy+hr*1.2:.0f} {hr*0.86:.0f} {cy+2} C{hr*0.5:.0f} {cy+hr*0.34:.0f} {-hr*0.5:.0f} {cy+hr*0.34:.0f} {-hr*0.86:.0f} {cy+2} Z" fill="{hc}"/>'
    ex=hr*0.36
    o+=f'<ellipse cx="{-ex+look:.1f}" cy="{cy+2}" rx="5.5" ry="{5.5*blink:.1f}" fill="#3a2418"/><ellipse cx="{ex+look:.1f}" cy="{cy+2}" rx="5.5" ry="{5.5*blink:.1f}" fill="#3a2418"/>'
    if mood=='sad': o+=f'<path d="M{-ex-10:.0f} {cy-12} L{-ex+8:.0f} {cy-17} M{ex+10:.0f} {cy-12} L{ex-8:.0f} {cy-17}" stroke="#3a2418" stroke-width="4" stroke-linecap="round"/>'
    elif P.get('old'): o+=f'<path d="M{-ex-8:.0f} {cy-14} q8 -5 16 0 M{ex-8:.0f} {cy-14} q8 -5 16 0" stroke="#999" stroke-width="3" fill="none" stroke-linecap="round"/>'
    if P.get('glasses'): o+=f'<circle cx="{-ex:.0f}" cy="{cy+2}" r="13" fill="none" stroke="#2a3a48" stroke-width="3.5"/><circle cx="{ex:.0f}" cy="{cy+2}" r="13" fill="none" stroke="#2a3a48" stroke-width="3.5"/><line x1="{-ex+13:.0f}" y1="{cy+2}" x2="{ex-13:.0f}" y2="{cy+2}" stroke="#2a3a48" stroke-width="3.5"/>'
    o+=f'<circle cx="{-hr*0.62:.0f}" cy="{cy+hr*0.34:.0f}" r="7" fill="#ff9a9a" opacity="0.4"/><circle cx="{hr*0.62:.0f}" cy="{cy+hr*0.34:.0f}" r="7" fill="#ff9a9a" opacity="0.4"/>'
    mc='#fff' if P.get('beard') and mood!='open' else '#3a2418'
    o+=f'<path d="{mouth[0]}" stroke="{mc}" stroke-width="4" fill="{mouth[1]}" stroke-linecap="round" stroke-linejoin="round"/>'
    o+='</g></g></g>'
    return o
