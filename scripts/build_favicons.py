"""Convert the complete supplied logo into square web icons; preserve original artwork."""
from pathlib import Path
import json
from PIL import Image, ImageOps
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'assets/images/island-jiu-jitsu-washington-logo.png'
logo=Image.open(source).convert('RGBA')
folder=ROOT/'assets/icons';folder.mkdir(exist_ok=True)
# Preserve the complete wordmark and its proportions; use the site's existing navy.
for size in [180,192,512]:
    icon=ImageOps.pad(logo,(size,size),method=Image.Resampling.LANCZOS,color=(12,20,25,255),centering=(0.5,0.5))
    icon=Image.alpha_composite(Image.new('RGBA',icon.size,(12,20,25,255)),icon)
    icon.save(folder/f'favicon-{size}.png',format='PNG',optimize=True)
Image.open(folder/'favicon-512.png').save(ROOT/'favicon.ico',format='ICO',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
manifest=json.loads((ROOT/'site.webmanifest').read_text())
manifest['icons']=[{'src':f'assets/icons/favicon-{size}.png','sizes':f'{size}x{size}','type':'image/png','purpose':'any'} for size in [192,512]]
(ROOT/'site.webmanifest').write_text(json.dumps(manifest,indent=2)+'\n')
for page in ROOT.glob('*.html'):
    soup=BeautifulSoup(page.read_text(),'html.parser')
    for rel,size in [('icon',192),('apple-touch-icon',180)]:
        tag=soup.select_one(f'link[rel="{rel}"]')
        if tag is None:tag=soup.new_tag('link',rel=rel);soup.head.append(tag)
        tag['href']=f'assets/icons/favicon-{size}.png';tag['sizes']=f'{size}x{size}';tag['type']='image/png'
    page.write_text(str(soup).rstrip()+'\n')
print('Square favicons generated from the full supplied logo; three PNG sizes plus legacy ICO. Original logo, all photos and page-body content unchanged.')
