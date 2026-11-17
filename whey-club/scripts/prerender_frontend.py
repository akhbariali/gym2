#!/usr/bin/env python3
"""Keep searchable HTML for existing routes while booting React on each page."""
import json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
build=root/'frontend/build'
entry=re.search(r'<script[^>]+src="([^"]+)"', (build/'index.html').read_text()).group(1)
(build/'react-entry.json').write_text(json.dumps({'src':entry}))
for source in (root/'dist').rglob('index.html'):
    if 'blog' in source.relative_to(root/'dist').parts:continue
    text=source.read_text()
    text=re.sub(r'<script\b[^>]*>.*?</script>','',text,flags=re.S)
    text=re.sub(r'(<body\b[^>]*>)',r'\1<div id="root">',text).replace('</body>','</div><script type="module" src="'+entry+'"></script></body>')
    target=build/source.relative_to(root/'dist');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
