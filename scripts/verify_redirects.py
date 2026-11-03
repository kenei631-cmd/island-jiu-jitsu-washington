"""Verify an allowlisted set of configured redirects, not discover/crawl pages."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs
import csv
import hashlib
import json
import sys
import time

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://www.islandjiujitsuwa.com'
INVENTORY = ROOT / 'output/Island-Jiu-Jitsu-301-Redirect-Inventory.csv'
rows = [row for row in csv.DictReader(INVENTORY.open()) if row['old_url'].startswith(BASE + '/')]

for attempt in range(1, 31):
    probe = requests.get(BASE + '/blog.html', allow_redirects=False, timeout=20)
    if probe.status_code == 301 and urlsplit(urljoin(BASE, probe.headers.get('Location',''))).path == '/gallery/':
        canonical = requests.get(BASE + '/gallery/', allow_redirects=False, timeout=20)
        markup = BeautifulSoup(canonical.text, 'html.parser')
        canonical_link = markup.select_one('link[rel="canonical"]')
        if canonical.status_code == 200 and canonical_link and canonical_link['href'] == BASE + '/gallery/' and 'noindex' not in canonical.headers.get('X-Robots-Tag', ''):
            break
    print(f'Waiting for redirect deployment: attempt {attempt}/30', flush=True)
    time.sleep(6)
else:
    raise SystemExit('Configured redirects have not become available')


def test_row(row):
    response = requests.get(row['old_url'], allow_redirects=True, timeout=25)
    first = response.history[0] if response.history else response
    row['verified_first_status'] = first.status_code
    row['verified_location'] = urljoin(first.url, first.headers.get('Location', '')) if response.history else ''
    row['verified_final_status'] = response.status_code
    row['verified_redirect_hops'] = len(response.history)
    if first.status_code != 301 or response.status_code != 200 or len(response.history) != 1 or response.url != row['destination_url']:
        return row, 'FAIL'
    return row, 'PASS'


with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(test_row, rows))
with INVENTORY.open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(row for row, _ in results)
failures = [row for row, status in results if status == 'FAIL']
if failures:
    print(json.dumps(failures, indent=2), flush=True)
    raise SystemExit('Redirect first-hop, target or final-status validation failed')
print(f'PASS: all {len(rows)} explicit aliases return one 301 to a slash destination, then 200.', flush=True)

routes = sorted({row['destination_path'] for row in rows})
for path in routes:
    response = requests.get(BASE + path, allow_redirects=False, timeout=25)
    assert response.status_code == 200, (path, response.status_code, response.headers.get('Location'))
    soup = BeautifulSoup(response.text, 'html.parser')
    assert soup.select_one('link[rel="canonical"]')['href'] == BASE + path, path
    utility = path in {'/photo-library/', '/thank-you/'}
    assert ('noindex' in response.headers.get('X-Robots-Tag', '')) == utility, path
    if path != '/':
        bare = requests.get(BASE + path.rstrip('/'), allow_redirects=True, timeout=25)
        assert len(bare.history) == 1 and bare.history[0].status_code == 301 and bare.url == BASE + path and bare.status_code == 200, path
    for img in soup.select('img[src]'):
        assert img['src'].startswith('/assets/'), (path, img['src'])
    for tag in soup.find_all('script', type='application/ld+json'):
        json.loads(tag.text)
print('PASS: all canonical slash routes return 200; native bare routes use a single 301, no loops; metadata and resource paths match.', flush=True)

query = requests.get(BASE + '/blog.html?utm_source=redirect_test&x=1', allow_redirects=True, timeout=25)
assert len(query.history) == 1 and query.status_code == 200
assert parse_qs(urlsplit(query.url).query) == {'utm_source': ['redirect_test'], 'x': ['1']}
for path in ['/this-url-does-not-exist-ijj/', '/missing/deep/page/', '/unknown-old-page.html', '/unknown-old-page/index.html', '/assets/no-such-photo.webp']:
    result = requests.get(BASE + path, allow_redirects=False, timeout=25)
    assert result.status_code == 404, (path, result.status_code)
contact = requests.get(BASE + '/contact/', timeout=25)
form = BeautifulSoup(contact.text, 'html.parser').form
assert form['action'] == 'https://formsubmit.co/brandonwiygul@gmail.com'
assert form.select_one('input[name="_next"]')['value'] == BASE + '/thank-you/'
gallery = BeautifulSoup(requests.get(BASE + '/gallery/', timeout=25).text, 'html.parser')
assert len(gallery.select('.gallery-photo')) == 20
assert all(link['href'].startswith('/assets/photos/') for link in gallery.select('.gallery-open'))
asset_paths = ['/assets/site.css', '/assets/gallery.js', '/assets/gallery.css', '/assets/about.css', '/assets/photo-library.js', '/assets/photos/library.json']
for path in asset_paths:
    result = requests.get(BASE + path, timeout=25)
    result.raise_for_status()
    if path.endswith('.js'):
        assert 'javascript' in result.headers.get('Content-Type', ''), path
    elif path.endswith('.css'):
        assert 'text/css' in result.headers.get('Content-Type', ''), path
    if path == '/assets/photo-library.js':
        assert "fetch('/assets/photos/library.json'" in result.text and 'return `/${encodedPath(path)}`;' in result.text
    if path.endswith('library.json'):
        assert len(result.json()['photos']) == 352
photos = list((ROOT / 'assets/photos/william-wallace').glob('*.webp'))
for sample in (photos[0], photos[-1]):
    data = requests.get(BASE + '/' + str(sample.relative_to(ROOT)), timeout=25)
    data.raise_for_status()
    assert hashlib.sha256(data.content).digest() == hashlib.sha256(sample.read_bytes()).digest()
apex_rows = []
for source_row in rows[:5]:
    row = dict(source_row)
    row['old_url'] = 'https://islandjiujitsuwa.com' + row['source_path']
    row['classification'] += '; non-www host'
    row['evidence'] += '; Netlify redirects the non-www host to its existing www primary domain first'
    response = requests.get(row['old_url'], allow_redirects=True, timeout=25)
    assert response.status_code == 200 and response.url == row['destination_url']
    assert 1 <= len(response.history) <= 2 and all(step.status_code == 301 for step in response.history)
    row['verified_first_status'] = response.history[0].status_code
    row['verified_location'] = urljoin(response.history[0].url, response.history[0].headers['Location'])
    row['verified_final_status'] = response.status_code
    row['verified_redirect_hops'] = len(response.history)
    apex_rows.append(row)
with INVENTORY.open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows + apex_rows)
sitemap = requests.get(BASE + '/sitemap.xml', timeout=25)
sitemap.raise_for_status()
assert BASE + '/about/' in sitemap.text and BASE + '/gallery/' in sitemap.text
assert 'github.io' not in sitemap.text and '.html</' not in sitemap.text
print('PASS: query strings retained, unknown pages/assets return real 404s, form/gallery unchanged, library and scripts load, sample image bytes match, sitemap uses custom-domain slash routes.', flush=True)
print('PASS: five original non-www URLs also resolve correctly; Netlify existing host normalization adds a second 301 where needed. Inventory reports actual hop counts.', flush=True)
print('NOTICE: marketing indexing block removed; utilities remain excluded. FormSubmit delivery remains unverified. No DNS changes made.', flush=True)
