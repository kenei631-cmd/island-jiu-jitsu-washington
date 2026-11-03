"""Build a static Netlify copy with trailing-slash routes and legacy 301s.

Source pages stay flat for GitHub Pages. Netlify publishes folder/index.html
pages, root-absolute resources and explicit legacy redirects. Production
marketing pages are indexable; published utility pages remain noindex.
"""
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import csv
import json
import os
import re
import shutil
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'netlify-dist'
SOURCE_ORIGIN = 'https://kenei631-cmd.github.io/island-jiu-jitsu-washington'
ASSET_ORIGIN = 'https://island-jiu-jitsu-washington.netlify.app'
SITE_ORIGIN = os.environ.get('SITE_ORIGIN', 'https://www.islandjiujitsuwa.com').rstrip('/')
INDEXABLE = os.environ.get('INDEXABLE', 'true').lower() not in {'false', '0', 'no'}
if not SITE_ORIGIN.startswith('https://') or urlsplit(SITE_ORIGIN).path:
    raise SystemExit('SITE_ORIGIN must be an explicitly configured HTTPS origin')

ROUTES = {
    'index.html': '/',
    'about.html': '/about/',
    'programs.html': '/programs/',
    'schedule.html': '/schedule/',
    'contact.html': '/contact/',
    'gallery.html': '/gallery/',
    'faq.html': '/faq/',
    'smokey-point.html': '/smokey-point/',
    'lakewood-north-marysville.html': '/lakewood-north-marysville/',
    'photo-library.html': '/photo-library/',
    'thank-you.html': '/thank-you/',
}
SOURCES = {p.name for p in ROOT.glob('*.html')}
if SOURCES != set(ROUTES) | {'404.html'}:
    raise SystemExit('Update route manifest for missing or new source pages: ' + repr(SOURCES))
LEGACY = json.loads((ROOT / 'legacy-redirect-map.json').read_text())


def page_url(value):
    """Convert only same-site page URLs, never external services or photo paths."""
    if not isinstance(value, str) or not value or value.startswith(('#', 'data:', 'mailto:', 'tel:')):
        return value
    for origin in (SOURCE_ORIGIN, ASSET_ORIGIN, SITE_ORIGIN, 'https://islandjiujitsuwa.com'):
        if value == origin or value.startswith(origin + '/'):
            relative = value[len(origin):] or '/'
            bits = urlsplit(relative)
            route = ROUTES.get(bits.path.lstrip('/'), bits.path)
            if route in [r.rstrip('/') for r in ROUTES.values() if r != '/']:
                route += '/'
            return SITE_ORIGIN + urlunsplit(('', '', route, bits.query, bits.fragment))
    bits = urlsplit(value)
    if bits.scheme or bits.netloc:
        return value
    path = bits.path.removeprefix('./')
    if path.lstrip('/') in ROUTES:
        path = ROUTES[path.lstrip('/')]
    elif path.lstrip('/').startswith('assets/') or path.lstrip('/') in {'robots.txt', 'sitemap.xml', 'site.webmanifest'}:
        path = '/' + path.lstrip('/')
    return urlunsplit(('', '', path, bits.query, bits.fragment))


def schema_urls(value):
    if isinstance(value, str):
        return page_url(value)
    if isinstance(value, list):
        return [schema_urls(item) for item in value]
    if isinstance(value, dict):
        return {key: schema_urls(item) for key, item in value.items()}
    return value


def convert_html(filename):
    soup = BeautifulSoup((ROOT / filename).read_text(), 'html.parser')
    for tag in soup.find_all(True):
        for attr in ['href', 'src', 'poster', 'action', 'data-src', 'data-full-src']:
            if tag.has_attr(attr):
                tag[attr] = page_url(tag[attr])
        if tag.has_attr('srcset'):
            tag['srcset'] = re.sub(r'(?<![\w/])(?:\./)?assets/', '/assets/', tag['srcset'])
        if tag.name == 'meta' and tag.has_attr('content') and str(tag['content']).startswith(('https://', 'http://')):
            tag['content'] = page_url(tag['content'])
    for script in soup.find_all('script', type='application/ld+json'):
        data = json.loads(script.get_text())
        script.string = json.dumps(schema_urls(data), ensure_ascii=False, separators=(',', ':'))
    if filename == 'contact.html':
        form = soup.select_one('form[name="offer-inquiry"]')
        if not form or form.get('data-netlify') != 'true':
            raise SystemExit('Expected the native Netlify offer-inquiry form')
        inputs = form.select('input[name="form-name"]')
        if len(inputs) != 1 or inputs[0].get('value') != 'offer-inquiry':
            raise SystemExit('Expected exactly one matching native form-name input')
        form['action'] = ROUTES['thank-you.html']
    # Keep the unlisted photo-library explanation consistent with stable copied asset URLs.
    if filename == 'photo-library.html':
        for link in soup.select('a[href]'):
            if link.get('href') == SITE_ORIGIN + '/assets/photos/library.csv':
                link['href'] = ASSET_ORIGIN + '/assets/photos/library.csv'
    return str(soup) + '\n'


if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
OUTPUT.mkdir()
for filename, route in ROUTES.items():
    target = OUTPUT / route.lstrip('/') / 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(convert_html(filename), encoding='utf-8')
(OUTPUT / '404.html').write_text(convert_html('404.html'), encoding='utf-8')

shutil.copytree(ROOT / 'assets', OUTPUT / 'assets')
if (ROOT / 'favicon.ico').is_file():
    shutil.copy2(ROOT / 'favicon.ico', OUTPUT / 'favicon.ico')
# Relative JS-generated thumbnail, preview and catalog URLs must still start at the site root.
library_script = OUTPUT / 'assets/photo-library.js'
code = library_script.read_text()
old_local = 'return `./${encodedPath(path)}`;'
old_fetch = "fetch('./assets/photos/library.json'"
if code.count(old_local) != 1 or code.count(old_fetch) != 1:
    raise SystemExit('Unexpected photo-library URL constructors; update this build transform')
code = code.replace(old_local, 'return `/${encodedPath(path)}`;')
code = code.replace(old_fetch, "fetch('/assets/photos/library.json'")
library_script.write_text(code)

ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('', ns)
xml = (ROOT / 'sitemap.xml').read_text().replace('\\n', '\n')
tree = ET.ElementTree(ET.fromstring(xml))
for item in tree.getroot():
    loc = item.find('{' + ns + '}loc')
    loc.text = page_url(loc.text)
ET.indent(tree, space='  ')
tree.write(OUTPUT / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
robots = (ROOT / 'robots.txt').read_text().replace(SOURCE_ORIGIN, SITE_ORIGIN).replace(ASSET_ORIGIN, SITE_ORIGIN)
(OUTPUT / 'robots.txt').write_text(robots)
shutil.copy2(ROOT / 'site.webmanifest', OUTPUT / 'site.webmanifest')

rows = []
seen = set()
legacy_by_source = {row['source']: row for row in LEGACY['redirects']}


def redirect(source, target, evidence, kind, google=False):
    if source in seen:
        return
    if not target.endswith('/') or source == target or target not in ROUTES.values():
        raise SystemExit('Invalid redirect: ' + source + ' to ' + target)
    seen.add(source)
    rows.append({'old_url': SITE_ORIGIN + source, 'source_path': source, 'destination_url': SITE_ORIGIN + target,
                 'destination_path': target, 'intended_status': 301, 'classification': kind,
                 'evidence': evidence, 'google_result_observed': google, 'verified_first_status': '',
                 'verified_location': '', 'verified_final_status': '', 'verified_redirect_hops': ''})


for row in LEGACY['redirects']:
    redirect(row['source'], row['target'], row['evidence'], 'Confirmed original-site route', row['google_observed'])
for filename, route in ROUTES.items():
    if '/' + filename not in legacy_by_source:
        redirect('/' + filename, route, 'Current source page filename; protective HTML alias', 'Current flat-HTML alias')
    if route != '/':
        redirect(route + 'index.html', route, 'Generated Netlify directory index; canonical URL consolidation', 'Directory-index alias')
redirect('/blog', '/gallery/', 'Protective alias for confirmed original Gallery / News route; slash variant matches same rule', 'Legacy clean-URL alias')
redirect('/blog/index.html', '/gallery/', 'Protective directory-index alias for confirmed Gallery / News route', 'Legacy directory alias')

# Never emit /route -> /route/ as a forced rule: Netlify matches both and would loop.
# The directory/index.html output gives native one-hop slash normalization for bare routes.
redirect_text = '# Legacy and HTML-alias redirects. Canonical destinations end in a slash.\n'
redirect_text += '# Bare named routes use Netlify directory normalization; no looping slash rules.\n'
# Consolidate published Netlify page copies, but preserve stable 200 asset URLs.
# Host-qualified rules precede path aliases to avoid an extra host/page hop.
host_paths = {route: route for route in ROUTES.values()}
host_paths.update({row['source_path']: row['destination_path'] for row in rows})
for source, target in sorted(host_paths.items()):
    redirect_text += f'{ASSET_ORIGIN}{source} {SITE_ORIGIN}{target} 301!\n'
redirect_text += '\n'.join(f"{row['source_path']} {row['destination_path']} 301!" for row in rows) + '\n'
(OUTPUT / '_redirects').write_text(redirect_text)
(ROOT / 'redirects-generated.txt').write_text(redirect_text)
(ROOT / 'output').mkdir(exist_ok=True)
with (ROOT / 'output/Island-Jiu-Jitsu-301-Redirect-Inventory.csv').open('w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

(OUTPUT / '_headers').write_text(
    '/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n' +
    ('' if INDEXABLE else '  X-Robots-Tag: noindex, nofollow\n') +
    ''.join(f'{path}\n  X-Robots-Tag: noindex, follow\n' for path in [
        '/photo-library', '/photo-library/*', '/thank-you', '/thank-you/*', '/404.html'
    ]) +
    '/assets/photos/william-wallace/*\n  Cache-Control: public, max-age=31536000, immutable\n' +
    '/assets/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n' +
    ''.join(f'{path}\n  Cache-Control: public, max-age=0, must-revalidate\n' for path in [
        '/assets/site.css', '/assets/photos/library.json', '/assets/photos/library.csv', '/assets/photo-library.css',
        '/assets/photo-library.js', '/assets/gallery.css', '/assets/gallery.js', '/assets/about.css'
    ]), encoding='utf-8')
print(f'Netlify directory build: {len(ROUTES)} content pages plus real 404; {len(rows)} explicit 301 rules.')
print(f'Canonical origin: {SITE_ORIGIN}; offer confirmation: {SITE_ORIGIN}/thank-you/')
print(f'All photo assets preserved. Marketing indexable: {INDEXABLE}; utilities noindex; native Netlify offer form; no DNS changes.')
