import build2 as B, subprocess
t=1.6
B.CT=t
svg=('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">'+B.DEFS+B.scene(t)+'<rect width="1080" height="1920" fill="url(#vig)"/>'
 '<rect width="1080" height="470" fill="url(#panel)"/>'
 f'<text x="540" y="182" text-anchor="middle" font-family="DejaVu Sans Mono" font-size="28" letter-spacing="7" fill="#55594c">MINDSET</text>'
 f'<text x="540" y="290" text-anchor="middle" xml:space="preserve" font-family="Poppins" font-weight="700" font-size="84">{B.rich("Nilai sama,")}</text>'
 f'<text x="540" y="392" text-anchor="middle" xml:space="preserve" font-family="Poppins" font-weight="700" font-size="84">{B.rich("*pola pikir* beda")}</text>'
 +B.watermark(5)+B.mascot(5,150)+'</svg>')
open('thumb.png','wb').write(subprocess.run(['rsvg-convert','-f','png'],input=svg.encode(),capture_output=True,check=True).stdout)
