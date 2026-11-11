import json, sys, os
from faster_whisper import WhisperModel
props = json.load(open('work/props.json', encoding='utf-8'))
script = ' '.join(s['narration'] for s in props['scenes'])
model = WhisperModel(os.environ.get('M', 'medium'), device='cpu', compute_type='int8')
for tag, kw in (('prompt', dict(initial_prompt=script)), ('plain', {})):
    segs, _ = model.transcribe('public/voiceover.wav', language='id', word_timestamps=True, beam_size=5, condition_on_previous_text=False, **kw)
    out = []
    for s in segs:
        for w in (s.words or []): out.append([w.word.strip(), round(w.start, 2), round(w.end, 2)])
    json.dump(out, open('asr_%s.json' % tag, 'w'), ensure_ascii=False)
    print('=== ASR', tag, len(out))
    print(' | '.join('%s %.2f-%.2f' % tuple(x) for x in out))
