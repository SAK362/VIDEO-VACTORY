"""Render video 1080x1920@30 dengan engine WebGL (Chrome headless, SwiftShader).
  python webgl/render_webgl.py meta                      -> cetak jumlah frame
  python webgl/render_webgl.py chunk i n OUT.mp4         -> render potongan ke-i dari n (video saja)
  python webgl/render_webgl.py still T [T...]            -> simpan frame uji (stills/f_T.jpg)"""
import base64, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30


def total_frames():
    d = json.loads(re.search(r'=(.*);\s*$', open(os.path.join(HERE, 'timing.js'), encoding='utf-8').read(), re.S).group(1))
    return int(round((d['dur'] + 0.8) * FPS))


def page(p):
    exe = os.environ.get('CHROME_PATH', '/usr/bin/google-chrome')
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--no-sandbox'])
    pg = b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.on('pageerror', lambda e: print('PAGEERR', e))
    pg.goto('file://' + os.path.join(HERE, 'engine.html')); pg.wait_for_function('window.READY===true', timeout=60000)
    return b, pg


def main():
    mode = sys.argv[1]; n = total_frames()
    if mode == 'meta':
        print(json.dumps({'frames': n, 'seconds': round(n / FPS, 2)})); return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b, pg = page(p)
        if mode == 'still':
            os.makedirs('stills', exist_ok=True)
            for t in sys.argv[2:]:
                d = pg.evaluate('frameJPEG(%s,0.92)' % t); open('stills/f_%s.jpg' % t, 'wb').write(base64.b64decode(d.split(',')[1]))
            b.close(); return
        ci, cn, out = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        a, z = n * ci // cn, n * (ci + 1) // cn
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        for f in range(a, z):
            d = pg.evaluate('frameJPEG(%d/%d,0.92)' % (f, FPS)); ff.stdin.write(base64.b64decode(d.split(',')[1]))
            if (f - a) % 30 == 0: print('frame %d/%d (potongan %d: %d-%d)' % (f, n, ci, a, z), flush=True)
        b.close(); ff.stdin.close()
        if ff.wait() != 0: raise SystemExit('ffmpeg gagal')


if __name__ == '__main__':
    main()
