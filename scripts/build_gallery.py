"""Generate the curated gallery from gallery-curation.json and the photo catalog."""
from pathlib import Path
from html import escape
import json
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = 'https://kenei631-cmd.github.io/island-jiu-jitsu-washington/'
PHOTO_ORIGIN = 'https://island-jiu-jitsu-washington.netlify.app/'
LABELS = {'gym': 'In the Gym', 'competition': 'Competition & Medals'}
VERSION = '20261102-g1'

def markup(pattern, text):
    match = re.search(pattern, text, re.S)
    if not match:
        raise ValueError(pattern)
    return match.group(0)

def picture(photo, eager=False):
    variants = photo['variants']
    medium = variants['medium']
    srcset = ', '.join(f'{item["path"]} {item["width"]}w' for item in variants.values())
    position = f'{photo["focal_x"]}% {photo["focal_y"]}%'
    return (f'<img src="{escape(medium["path"])}" srcset="{escape(srcset)}" '
            f'sizes="(max-width:620px) 90vw, (max-width:940px) 44vw, 29vw" '
            f'width="{medium["width"]}" height="{medium["height"]}" '
            f'alt="{escape(photo["alt"])}" loading="{"eager" if eager else "lazy"}" '
            f'decoding="async" style="object-position:{position}" data-photo-id="{photo["id"]}"/>')

def build():
    curation = json.loads((ROOT/'gallery-curation.json').read_text())
    catalog = {photo['id']: photo for photo in json.loads((ROOT/'assets/photos/library.json').read_text())['photos']}
    groups = {}
    hashes = set()
    for category in LABELS:
        groups[category] = []
        for selected in curation[category]:
            photo = {**catalog[selected['id']], **selected, 'category': category}
            digest = photo['variants']['thumbnail']['sha256']
            if digest in hashes:
                raise ValueError('Duplicate gallery photograph: ' + photo['id'])
            hashes.add(digest)
            for field in ['focal_x', 'focal_y']:
                assert 0 <= photo[field] <= 100
            assert len(photo['roi']) == 4
            groups[category].append(photo)
        assert groups[category]

    home_path = ROOT/'index.html'
    home = home_path.read_text()
    footer = markup(r'<footer\b.*?</footer>', home)
    footer_dom = BeautifulSoup(footer, 'html.parser')
    if not footer_dom.find('a', href='gallery.html'):
        link = footer_dom.new_tag('a', href='gallery.html')
        link.string = 'Gallery'
        footer_dom.find('a', href='faq.html').insert_after(link)
    footer = str(footer_dom.footer)

    # A single header/footer pattern is shared by all pages, without touching
    # their existing body content or metadata.
    for page in ROOT.glob('*.html'):
        text = page.read_text()
        header = markup(r'<header\b.*?</header>', text)
        header_dom = BeautifulSoup(header, 'html.parser')
        nav = header_dom.select_one('.nav')
        if not nav.find('a', href='gallery.html'):
            link = header_dom.new_tag('a', href='gallery.html')
            link.string = 'Gallery'
            nav.find('a', href='contact.html').insert_before(link)
        text = text.replace(header, str(header_dom.header), 1)
        text = re.sub(r'<footer\b.*?</footer>', lambda _: footer, text, count=1, flags=re.S)
        page.write_text(text)

    home = home_path.read_text()
    parsed = BeautifulSoup(home, 'html.parser')
    community = parsed.select_one('.home-community')
    preview = [groups['gym'][index] for index in (0, 4, 7)] + groups['competition'][:1]
    cards = []
    for photo in preview:
        cards.append(f'<a class="gallery-preview-card" href="gallery.html#{photo["category"]}">'
                     f'{picture(photo)}<div class="gallery-preview-copy"><div class="eyebrow">{escape(LABELS[photo["category"]])}</div>'
                     f'<strong>{escape(photo["caption"])}</strong></div></a>')
    preview_html = '<div class="gallery-preview">' + ''.join(cards) + '</div>'
    preview_html += ('<div class="gallery-preview-actions"><p>See everyday training, the academy community, '
                     'and competition moments. Competition is optional—there is more than one reason to train.</p>'
                     '<a class="button" href="gallery.html">View gallery →</a></div>')
    for old in community.select('.community-grid,.gallery-preview,.gallery-preview-actions'):
        old.decompose()
    community.select_one('.wrap').append(BeautifulSoup(preview_html, 'html.parser'))
    new_community = str(community)
    home = re.sub(r'<section\b[^>]*class="[^"]*home-community[^\"]*".*?</section>', lambda _: new_community, home, count=1, flags=re.S)
    if 'assets/gallery.css' not in home:
        home = home.replace('</head>', f'<link rel="stylesheet" href="assets/gallery.css?v={VERSION}"/>\n</head>', 1)
    home_path.write_text(home)

    template = BeautifulSoup((ROOT/'faq.html').read_text(), 'html.parser')
    head = template.head
    title = 'Jiu-Jitsu Photo Gallery | Arlington, WA | Island Jiu-Jitsu'
    description = 'Explore real training, academy community, and competition photos from Island Jiu-Jitsu Washington in Arlington and Smokey Point.'
    head.title.string = title
    for selector in ['meta[name="description"]', 'meta[property="og:description"]', 'meta[name="twitter:description"]']:
        head.select_one(selector)['content'] = description
    for selector in ['meta[property="og:title"]', 'meta[name="twitter:title"]']:
        head.select_one(selector)['content'] = title
    head.select_one('link[rel="canonical"]')['href'] = CANONICAL+'gallery.html'
    head.select_one('meta[property="og:url"]')['content'] = CANONICAL+'gallery.html'
    stylesheet = template.new_tag('link', rel='stylesheet', href=f'assets/gallery.css?v={VERSION}')
    head.append(stylesheet)
    gallery_script = template.new_tag('script', src=f'assets/gallery.js?v={VERSION}', defer='')
    head.append(gallery_script)
    old_graph = json.loads(head.find('script', type='application/ld+json').get_text())['@graph']
    business = next(node for node in old_graph if node.get('@id', '').endswith('#business'))
    gallery_id = CANONICAL+'gallery.html'
    graph = [business, {
        '@type': 'CollectionPage', '@id': gallery_id+'#webpage', 'url': gallery_id,
        'name': title, 'description': description,
        'isPartOf': {'@id': CANONICAL+'#website'}, 'about': {'@id': CANONICAL+'#business'},
        'inLanguage': 'en-US', 'mainEntity': {'@id': gallery_id+'#photos'}
    }, {
        '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': CANONICAL},
            {'@type': 'ListItem', 'position': 2, 'name': 'Gallery', 'item': gallery_id}
        ]
    }, {
        '@type': 'ItemList', '@id': gallery_id+'#photos',
        'numberOfItems': sum(len(items) for items in groups.values()),
        'itemListElement': [
            {'@type': 'ListItem', 'position': index+1, 'item': {
                '@type': 'ImageObject', 'contentUrl': PHOTO_ORIGIN+photo['variants']['large']['path'],
                'name': photo['caption'], 'caption': photo['caption'],
                'width': photo['variants']['large']['width'], 'height': photo['variants']['large']['height']
            }} for index, photo in enumerate(groups['gym']+groups['competition'])
        ]
    }]
    head.find('script', type='application/ld+json').string = json.dumps({'@context':'https://schema.org','@graph':graph}, ensure_ascii=False, separators=(',', ':'))
    header = template.header
    for link in header.select('.nav a'):
        link.attrs.pop('aria-current', None)
        if 'active' in link.get('class', []):
            link['class'] = [value for value in link['class'] if value != 'active']
            if not link['class']:
                link.attrs.pop('class', None)
        if link.get('href') == 'gallery.html':
            link['aria-current'] = 'page'
            link['class'] = ['active']
    navigation_script = template.body.find('script').get_text()
    sections = []
    for category, photos in groups.items():
        copy = ('Coaching, partner practice, and the people who make the academy a community.' if category == 'gym' else
                'Team outings, competition rounds, and moments worth celebrating. Competing is a choice—not a requirement to train.')
        photo_cards = []
        for index, photo in enumerate(photos):
            photo_cards.append(f'<figure class="gallery-photo" data-photo-id="{photo["id"]}">'
                               f'<a class="gallery-open" href="{photo["variants"]["large"]["path"]}" aria-label="Enlarge: {escape(photo["caption"])}">'
                               f'{picture(photo, category=="gym" and index<3)}</a>'
                               f'<figcaption><h3>{escape(photo["caption"])}</h3><span class="gallery-enlarge-label">Select photo to enlarge →</span></figcaption></figure>')
        sections.append(f'<section class="gallery-section" data-gallery-section="{category}" id="{category}" aria-labelledby="{category}-heading">'
                        f'<div class="gallery-section-heading"><h2 id="{category}-heading">{escape(LABELS[category])}</h2><p>{escape(copy)}</p></div>'
                        f'<div class="gallery-grid">{"".join(photo_cards)}</div></section>')
    main = ('<main id="main-content"><section class="hero small"><div class="wrap gallery-intro">'
            '<div class="eyebrow">Inside Island Jiu-Jitsu · Arlington / Smokey Point</div>'
            '<h1>REAL TRAINING.<br/><span class="blue">REAL MOMENTS.</span></h1>'
            '<p>See the instruction, people, and team experiences behind Island Jiu-Jitsu Washington. '
            'You can train for fitness, confidence, community, or competition.</p></div></section>'
            '<section class="section soft"><div class="wrap" data-gallery>'
            '<div class="gallery-filters" role="group" aria-label="Choose a photo collection">'
            f'<button class="gallery-filter selected" type="button" data-gallery-filter="gym" aria-pressed="true">In the Gym · {len(groups["gym"])}</button>'
            f'<button class="gallery-filter" type="button" data-gallery-filter="competition" aria-pressed="false">Competition &amp; Medals · {len(groups["competition"])}</button></div>'
            '<p id="gallery-status" class="gallery-status" aria-live="polite">Explore the photo collections below.</p>'
            '<noscript><p>Both collections are shown below. Select a photograph to open the full image.</p></noscript>'
            + ''.join(sections) + '</div></section>'
            '<section class="banner"><div class="wrap"><h2>FIND YOUR REASON TO TRAIN.</h2>'
            '<p>Ask about the 3 months for $300 membership offer, or explore the current classes before your first visit.</p>'
            '<div class="buttons" style="justify-content:center"><a class="button" href="contact.html#offer-form">Ask about this offer →</a>'
            '<a class="button outline" href="schedule.html">See class times</a></div></div></section></main>')
    viewer = ('<dialog class="gallery-viewer" id="gallery-viewer" aria-labelledby="gallery-viewer-title">'
              '<div class="gallery-viewer-head"><p id="gallery-viewer-counter"></p><button type="button" data-gallery-close aria-label="Close photo viewer">Close ×</button></div>'
              '<figure><img class="gallery-viewer-image" id="gallery-viewer-image" alt="" decoding="async"/>'
              '<figcaption><h2 id="gallery-viewer-title"></h2><div class="gallery-viewer-controls">'
              '<button type="button" data-gallery-previous aria-label="Previous photograph">← Previous</button>'
              '<a class="gallery-original" id="gallery-original" href="#" target="_blank" rel="noopener noreferrer">Open full image ↗</a>'
              '<button type="button" data-gallery-next aria-label="Next photograph">Next →</button>'
              '</div></figcaption></figure></dialog>')
    output = '<!DOCTYPE html>\n<html lang="en">'+str(head)+'\n<body><a class="skip-link" href="#main-content">Skip to content</a>'+str(header)+main+footer+viewer+'<script>'+navigation_script+'</script></body></html>\n'
    (ROOT/'gallery.html').write_text(output)

    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    sitemap = ET.parse(ROOT/'sitemap.xml')
    namespace = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    if not any(node.text == gallery_id for node in sitemap.getroot().iter(namespace+'loc')):
        url = ET.SubElement(sitemap.getroot(), namespace+'url')
        ET.SubElement(url, namespace+'loc').text = gallery_id
        ET.SubElement(url, namespace+'lastmod').text = '2026-11-02'
    for url in sitemap.getroot().findall(namespace+'url'):
        if url.find(namespace+'loc').text == CANONICAL:
            modified = url.find(namespace+'lastmod')
            if modified is not None:
                modified.text = '2026-11-02'
    sitemap.write(ROOT/'sitemap.xml', encoding='utf-8', xml_declaration=True)
    print('Gallery generated:', {category:len(items) for category,items in groups.items()})

if __name__ == '__main__':
    build()
