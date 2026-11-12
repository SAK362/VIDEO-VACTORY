"""Ubah spec JSON menjadi webgl/spec.js.   python webgl/make_spec.py spec.json [keluar=webgl/spec.js]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'spec.js')
d = json.load(open(src, encoding='utf-8'))
open(out, 'w', encoding='utf-8').write('window.SPEC=' + json.dumps(d, ensure_ascii=False) + ';\n'); print('spec ->', out, len(d.get('scenes', [])), 'adegan')
