import json
import pathlib
import re
import sys

base = pathlib.Path(__file__).resolve().parents[1] / 'packets/03_dialogue'
translations_path = pathlib.Path(__file__).resolve().parent / 'data/_dialogue_batch.json'
translations = json.loads(translations_path.read_text(encoding='utf-8-sig'))
paths = []
for path in base.glob('*.json'):
    data = json.loads(path.read_bytes().decode('utf-8-sig'))
    if data.get('packet_type') == 'dialogue_graph':
        match = re.match(r'dialog_(\d{4})', data.get('packet_id', ''))
        if not match or int(match.group(1)) > 237:
            continue
    paths.append(path)
updated = 0
remaining = set(translations)
for path in paths:
    raw = path.read_bytes().decode('utf-8-sig')
    data = json.loads(raw)
    spans = []
    pos = raw.index('[', raw.index('"entries"')) + 1
    decoder = json.JSONDecoder()
    while True:
        while pos < len(raw) and (raw[pos].isspace() or raw[pos] == ','):
            pos += 1
        if pos >= len(raw) or raw[pos] == ']':
            break
        item, end = decoder.raw_decode(raw, pos)
        key = item.get('key')
        if key in translations:
            if item.get('JA_new') is not None:
                raise ValueError(f'JA_new already set: {path.name} {key}')
            obj = raw[pos:end]
            replacement = json.dumps(translations[key], ensure_ascii=False)
            obj, count = re.subn(r'("JA_new"\s*:\s*)null', lambda m: m.group(1) + replacement, obj, count=1)
            if count != 1:
                raise ValueError(f'JA_new slot not found: {path.name} {key}')
            spans.append((pos, end, obj))
            remaining.discard(key)
        pos = end
    for start, end, replacement in reversed(spans):
        raw = raw[:start] + replacement + raw[end:]
        updated += 1
    if spans:
        json.loads(raw)
        path.write_bytes(raw.encode('utf-8'))
if remaining:
    raise ValueError('unmatched keys: ' + ', '.join(sorted(remaining)))
print(f'updated={updated}')
