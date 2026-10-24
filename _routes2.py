# -*- coding: utf-8 -*-
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
out = []
out.append('=== ROUTES ===')
from app import app
for r in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    m = ','.join(sorted(x for x in r.methods if x not in ('HEAD', 'OPTIONS')))
    out.append(f"{str(r):50s} {m:15s} {r.endpoint}")
out.append('=== app.py lesson route ===')
src = open('app.py', encoding='utf-8').read().splitlines()
for i, line in enumerate(src, 1):
    if 'def lesson' in line or '@app.route' in line:
        out.append(f"{i}: {line}")
out.append('=== lesson.html fetch URL ===')
lh = open('templates/lesson.html', encoding='utf-8').read().splitlines()
for i, line in enumerate(lh, 1):
    if 'fetch(' in line or 'url_for' in line:
        out.append(f"{i}: {line.strip()[:120]}")
open('_routes2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('done')