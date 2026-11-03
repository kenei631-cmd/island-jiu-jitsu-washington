"""Check the built production site; no network requests or unpublished crawling."""
from pathlib import Path
import hashlib
import json
import tomllib
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'netlify-dist'
ORIGIN='https://www.islandjiujitsuwa.com'
urls=[x.text for x in ET.fromstring((OUT/'sitemap.xml').read_text()).findall('{*}url/{*}loc')]
assert len(urls)==9 and len(set(urls))==9
for url in urls:
    path=url.removeprefix(ORIGIN+'/');page=OUT/path/'index.html'
    soup=BeautifulSoup(page.read_text(),'html.parser')
    assert soup.select_one('link[rel=canonical]')['href']==url, (url,'canonical')
    assert 'noindex' not in soup.select_one('meta[name=robots]')['content'], (url,'meta robots')
    assert len(soup.find_all('h1'))==1, (url,'H1')
    for script in soup.select('script[type="application/ld+json"]'):json.loads(script.text)
    for link in soup.select('link[as=font]'):
        assert (OUT/link['href'].lstrip('/')).is_file(), (url,'font preload path')

# _headers scope must be parsed by exact rule, not a substring of a private wildcard.
blocks={};current=None
for line in (OUT/'_headers').read_text().splitlines():
    if not line.strip() or line.startswith('#'):continue
    if not line.startswith((' ','\t')):
        current=line.strip();blocks.setdefault(current,{})
    else:
        name,value=line.strip().split(':',1);blocks[current][name.lower()]=value.strip()
assert 'x-robots-tag' not in blocks['/*'], 'Unexpected global indexing block'
for private in ['/photo-library/*','/thank-you/*','/404.html']:
    assert 'noindex' in blocks[private].get('x-robots-tag',''), private
assert 'immutable' in blocks['/assets/fonts/*']['cache-control']

fonts=json.loads((ROOT/'docs/font-assets.json').read_text())
assert len(fonts)==9
for font in fonts:
    data=(OUT/font['path']).read_bytes()
    assert data[:4]==b'wOF2' and hashlib.sha256(data).hexdigest()==font['sha256'], font['path']
photos=list((ROOT/'assets/photos/william-wallace').glob('*.webp'))
assert len(photos)==1056
for source in photos:
    target=OUT/source.relative_to(ROOT)
    assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest(), source.name
assert len(json.loads((OUT/'assets/photos/library.json').read_text())['photos'])==352
assert 'data:font' not in (OUT/'assets/site.css').read_text()
for rule in (OUT/'_redirects').read_text().splitlines():
    if not rule or rule.startswith('#'):continue
    source,target,status=rule.split()
    assert source!=target and status=='301!', rule
    if source.startswith('https://island-jiu-jitsu-washington.netlify.app'):
        assert target.startswith(ORIGIN+'/') and '/assets/' not in source, rule
tomllib.loads((ROOT/'netlify.toml').read_text())
print('PASS build:9 canonical marketing pages; production indexing open; utilities excluded;9 exact original font faces;1056 unchanged copied photo variants/352 photos; valid host/page redirects; configuration parses.')
