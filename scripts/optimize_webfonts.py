"""Move existing embedded WOFF2 bytes into hashed assets; preserve all CSS rules."""
from pathlib import Path
import base64
import hashlib
import json
import re
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
css_path=ROOT/'assets/site.css'
css=css_path.read_text()
manifest_path=ROOT/'docs/font-assets.json'
manifest=[]
font_dir=ROOT/'assets/fonts';font_dir.mkdir(exist_ok=True)

def externalize(match):
    body=match.group(1)
    family=re.search(r"font-family:([^;]+)",body).group(1).strip(" '\"")
    weight=re.search(r'font-weight:([^;]+)',body).group(1)
    data=re.search(r'data:font/woff2;base64,([A-Za-z0-9+/=]+)',body)
    if not data:
        raise ValueError('Expected embedded WOFF2 in original font rule')
    blob=base64.b64decode(data.group(1),validate=True)
    assert blob[:4]==b'wOF2'
    digest=hashlib.sha256(blob).hexdigest()
    name=re.sub(r'[^a-z0-9]+','-',family.lower()).strip('-')+'-'+digest[:16]+'.woff2'
    path=font_dir/name;path.write_bytes(blob)
    body=body.replace(data.group(0),'fonts/'+name)
    manifest.append({'family':family,'weight':weight,'path':'assets/fonts/'+name,'bytes':len(blob),'sha256':digest})
    return '@font-face{'+body+'}'

before=len(css.encode())
if 'data:font/woff2;base64,' in css:
    css=re.sub(r'@font-face\s*\{([^}]*)\}',externalize,css)
    assert len(manifest)==9 and css.count('@font-face')==9 and 'data:font' not in css
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
else:
    manifest=json.loads(manifest_path.read_text())

# These explicit heights equal the existing final logo box at each breakpoint.
# Reserve the box before the lazy/decode phase rather than resizing it later.
marker='/* Stable above-the-fold brand box; same final responsive dimensions. */'
if marker not in css:
    h215=min(85,215*392/1127);h180=min(85,180*392/1127)
    css+='\n'+marker+'\n.brand img{height:85px}\n'
    css+='@media(max-width:760px){.brand img{height:'+f'{h215:.6f}'+'px}}\n'
    css+='@media(max-width:380px){.home-page .brand img{height:'+f'{h180:.6f}'+'px}}\n'
css_path.write_text(css)
preloads=[next(x['path'] for x in manifest if x['family']==family and x['weight']==weight)
          for family,weight in [('Barlow Condensed','700'),('Inter','400')]]
for page in ROOT.glob('*.html'):
    soup=BeautifulSoup(page.read_text(),'html.parser')
    for stylesheet in soup.select('link[rel="stylesheet"][href]'):
        if stylesheet['href'].split('?')[0]=='assets/site.css':
            stylesheet['href']='assets/site.css?v=20261103-seo'
    for path in dict.fromkeys(preloads):
        if not soup.select_one('link[as="font"][href="'+path+'"]'):
            tag=soup.new_tag('link',attrs={'rel':'preload','as':'font','href':path,'type':'font/woff2','crossorigin':'anonymous'})
            soup.head.append(tag)
    for image in soup.select('.brand img'):
        image['loading']='eager'
    # Correct an existing intrinsic-dimension typo; the fixed photo crop stays unchanged.
    for image in soup.select('img[src="assets/images/adult-jiu-jitsu-arlington-wa.webp"]'):
        image['width']='1200';image['height']='839'
    page.write_text(str(soup).rstrip()+'\n')
for item in manifest:
    assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
print('Stylesheet bytes:',before,'->',len(css.encode()))
print('Exact original font faces retained:',len(manifest),'unique font files:',len({x['path'] for x in manifest}))
print('All source photos unchanged; shared header dimensions reserved; body/headline font preloads added.')
