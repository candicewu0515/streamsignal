"""Refresh the static field cache version and reproducible dependency-size audit."""
from pathlib import Path
import hashlib,re,json
root=Path(__file__).resolve().parents[1]
sw=root/'sw.js';text=sw.read_text();files=re.search(r'const FILES=(\[.*?\]);',text).group(1)
files=re.findall(r"'([^']+)'",files)
version=hashlib.sha256(b''.join((root/('index.html' if f=='./' else f)).read_bytes() for f in files)).hexdigest()[:12]
text=re.sub(r"const CACHE='[^']+';",f"const CACHE='streamsignal-field-{version}';",text);sw.write_text(text)
old=(root/'research.html').read_text();new=(root/'index.html').read_text()
legacy=['research.html']+re.findall(r'(?:src|href)="((?:assets|data)/[^"#]+)"',old)
initial=['index.html']+re.findall(r'(?:src|href)="((?:assets|data)/[^"#]+)"',new)+['data/sites.json','manifest.webmanifest']
fonts=['assets/fonts/'+p.name for p in (root/'assets/fonts').glob('*.woff2')]
legacy+=fonts;initial+=fonts
oldbytes=sum((root/f).stat().st_size for f in set(legacy));newbytes=sum((root/f).stat().st_size for f in set(initial));cachebytes=sum((root/('index.html' if f=='./' else f)).stat().st_size for f in files)
audit={'legacyBytes':oldbytes,'newInitialBytes':newbytes,'fieldCacheBytes':cachebytes,'reductionPct':100*(1-newbytes/oldbytes),'cacheVersion':version,'dashboardDeferredBytes':(root/'data/countries.js').stat().st_size,'dashboardTotalStaticBytes':newbytes+(root/'data/countries.js').stat().st_size,'scope':'Uncompressed static dependency bytes, not request timing. Initial excludes the separately loaded dashboard map, background PWA preparation and weather responses. Cache bytes include both root and index HTML keys.','initialFiles':sorted(set(initial))}
(root/'results/loading_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit,indent=2))
