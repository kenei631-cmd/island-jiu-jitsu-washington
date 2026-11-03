"""Render the academy About page from documented copy and optimized source photos."""
from copy import deepcopy
from datetime import date
from html import escape
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://kenei631-cmd.github.io/island-jiu-jitsu-washington'
URL = ORIGIN + '/about.html'
TITLE = 'About Professor Brandon | Island Jiu-Jitsu Washington'
DESCRIPTION = 'Meet Professor Brandon Wiygul, explore his Jiu-Jitsu journey, and learn how family, technique, discipline, and community shaped IJJ Washington in Arlington.'
COPY = json.loads((ROOT / 'docs/about-content.json').read_text())
PHOTOS = json.loads((ROOT / 'docs/about-photo-variants.json').read_text())
TEMPLATE = (ROOT / 'faq.html').read_text()
DATE = '2026-11-02'


def paragraphs(items):
    return ''.join('<p>' + escape(value) + '</p>' for value in items)


def image(key, alt, caption, *, eager=False, sizes='(max-width:760px) 88vw, 48vw', css=''):
    variants = PHOTOS[key]
    medium = variants[1]
    srcset = ', '.join(f"{photo['path']} {photo['width']}w" for photo in variants)
    loading = 'eager' if eager else 'lazy'
    priority = ' fetchpriority="high"' if eager else ''
    return (
        f'<figure class="about-portrait {css}"><img src="{medium["path"]}" '
        f'srcset="{srcset}" sizes="{sizes}" width="{medium["width"]}" height="{medium["height"]}" '
        f'alt="{escape(alt, quote=True)}" loading="{loading}" decoding="async"{priority}/>'
        f'<figcaption>{escape(caption)}</figcaption></figure>'
    )


def create_page():
    soup = BeautifulSoup(TEMPLATE, 'html.parser')
    head = deepcopy(soup.head)
    head.title.string = TITLE
    head.find('meta', attrs={'name': 'description'})['content'] = DESCRIPTION
    head.find('link', rel='canonical')['href'] = URL
    for key, value in [('og:title', TITLE), ('og:description', DESCRIPTION), ('og:url', URL),
                       ('og:image', ORIGIN + '/' + PHOTOS['island-jiu-jitsu-lineage-leadership'][2]['path']),
                       ('og:image:width', str(PHOTOS['island-jiu-jitsu-lineage-leadership'][2]['width'])),
                       ('og:image:height', str(PHOTOS['island-jiu-jitsu-lineage-leadership'][2]['height'])),
                       ('og:image:alt', 'Island Jiu-Jitsu black belts together at the Hawaii academy')]:
        head.find('meta', attrs={'property': key})['content'] = value
    for key, value in [('twitter:title', TITLE), ('twitter:description', DESCRIPTION),
                       ('twitter:image', ORIGIN + '/' + PHOTOS['island-jiu-jitsu-lineage-leadership'][2]['path'])]:
        head.find('meta', attrs={'name': key})['content'] = value
    if not head.find('link', href=re.compile(r'assets/about\.css')):
        link = soup.new_tag('link', rel='stylesheet', href='assets/about.css?v=20261102-about')
        head.append(link)
    old_schema = head.find('script', type='application/ld+json')
    business = deepcopy(json.loads(old_schema.string)['@graph'][0])
    person_id = ORIGIN + '/#professor-brandon'
    business['founder'] = {'@id': person_id}
    graph = [business, {
        '@type': 'WebSite', '@id': ORIGIN + '/#website', 'url': ORIGIN + '/',
        'name': 'Island Jiu-Jitsu Washington', 'publisher': {'@id': business['@id']}, 'inLanguage': 'en-US'
    }, {
        '@type': 'Person', '@id': person_id, 'name': 'Brandon Wiygul',
        'honorificPrefix': 'Professor', 'jobTitle': 'Head Instructor',
        'description': 'Head instructor of Island Jiu-Jitsu Washington and a Brazilian Jiu-Jitsu black belt under Professor Surfah J Vigil.',
        'image': ORIGIN + '/' + PHOTOS['professor-brandon-wiygul'][2]['path'],
        'worksFor': {'@id': business['@id']}, 'knowsAbout': ['Brazilian Jiu-Jitsu', 'Gi Jiu-Jitsu', 'No-Gi Jiu-Jitsu', 'Youth Jiu-Jitsu']
    }, {
        '@type': 'AboutPage', '@id': URL + '#webpage', 'url': URL, 'name': TITLE,
        'description': DESCRIPTION, 'isPartOf': {'@id': ORIGIN + '/#website'},
        'mainEntity': {'@id': person_id}, 'about': [{'@id': person_id}, {'@id': business['@id']}],
        'breadcrumb': {'@id': URL + '#breadcrumb'}, 'inLanguage': 'en-US',
        'image': [ORIGIN + '/' + variants[2]['path'] for variants in PHOTOS.values()]
    }, {
        '@type': 'BreadcrumbList', '@id': URL + '#breadcrumb',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': ORIGIN + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'About Professor Brandon', 'item': URL}
        ]
    }]
    old_schema.string = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':'))
    header = re.search(r'<header\b[\s\S]*?</header>', TEMPLATE).group(0)
    footer = re.search(r'<footer\b[\s\S]*?</footer>', (ROOT / 'index.html').read_text()).group(0)
    navigation_script = 'document.querySelectorAll(".menu-toggle").forEach(button=>button.addEventListener("click",()=>{const nav=document.querySelector(".nav");const opened=nav.classList.toggle("open");button.setAttribute("aria-expanded",String(opened))}));'
    journey = ''.join(f'<article class="about-stage"><h3>{escape(stage["heading"])}</h3><p>{escape(stage["body"])}</p></article>' for stage in COPY['journey'])
    values = ''.join(f'<article class="about-value"><h3>{escape(value["heading"])}</h3><p>{escape(value["body"])}</p></article>' for value in COPY['values'])
    content = f'''<main id="main-content">
<section class="about-intro"><div class="wrap"><nav class="about-breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span>About Professor Brandon</nav><div class="about-intro-grid"><div><div class="eyebrow">Our instructor. Our roots. Our community.</div><h1>PROFESSOR<br/><span class="blue">BRANDON WIYGUL.</span></h1><p class="about-role">Head Instructor · Island Jiu-Jitsu Washington</p><p class="about-lead">{escape(COPY['intro'])}</p><div class="buttons"><a class="button" href="contact.html#offer-form">Meet us on the mats →</a><a class="button outline" href="schedule.html">See class times</a></div></div>{image('professor-brandon-wiygul', 'Professor Brandon Wiygul pictured at Island Jiu-Jitsu in Hawaii', 'Professor Brandon at Island Jiu-Jitsu in Hawaii.', eager=True)}</div></div></section>
<section class="section"><div class="wrap"><div class="about-overview"><p><strong>Black-belt lineage</strong>Professor “Surfah J” Vigil · Island Jiu-Jitsu</p><p><strong>Academy home</strong>Arlington / Smokey Point, Washington</p><p><strong>Our foundation</strong>Technique · Discipline · Community</p></div></div></section>
<section class="section soft"><div class="wrap"><div class="about-story-heading"><div class="eyebrow">The path to the mats</div><h2>A JOURNEY BUILT<br/>ON FUNDAMENTALS.</h2></div><div class="about-journey">{journey}</div><div class="about-lineage">{image('island-jiu-jitsu-lineage-leadership', 'Island Jiu-Jitsu black belts together at the Hawaii academy', 'Lineage and leadership. Island Jiu-Jitsu black belts together in Hawaii.', sizes='(max-width:760px) 88vw, 1000px')}</div></div></section>
<section class="section"><div class="wrap"><div class="about-story-layout"><div class="about-story-copy"><div class="eyebrow">From Hawaii to the Pacific Northwest</div><h2>{escape(COPY['washington']['heading']).upper()}</h2>{paragraphs(COPY['washington']['paragraphs'])}<aside class="about-family"><h3>{escape(COPY['family']['heading'])}</h3>{paragraphs(COPY['family']['paragraphs'])}</aside></div>{image('island-jiu-jitsu-arlington-community', 'Young students and adults from the Island Jiu-Jitsu Washington community together on the mats', 'Building Arlington community through Jiu-Jitsu. Students and adults together at the academy.')}</div></div></section>
<section class="section about-values"><div class="wrap"><div class="about-story-heading"><div class="eyebrow">What we bring to every class</div><h2>TECHNIQUE.<br/>DISCIPLINE. COMMUNITY.</h2><p>The principles behind Professor Brandon’s instruction and the academy we are building together.</p></div><div class="about-value-grid">{values}</div><p class="about-more">See these principles in practice in <a href="gallery.html">our academy gallery</a> or explore <a href="programs.html">our training programs</a>.</p></div></section>
<section class="section soft"><div class="wrap about-micah-grid">{image('coach-micah-island-jiu-jitsu', 'Coach Micah pictured in a black gi at the academy', 'Coach Micah · Instructor', sizes='(max-width:760px) 88vw, 340px')}<div class="about-story-copy"><div class="eyebrow">Part of the coaching team</div><h2>MEET COACH MICAH.</h2><p>Micah began Brazilian Jiu-Jitsu in 2018 at Vital Jiu-Jitsu in Fife, Washington, under black belts Kyle Mitchell and Nick Ryan. Career and family brought him to Arlington, where he trained locally before finding his home at Island Jiu-Jitsu under Professor Brandon.</p><p>His approach emphasizes purposeful training, awareness of individual limitations, and applying technique with appropriate intensity. Outside the academy, Micah is an ICU nurse, a musician, a husband, and a father of two boys.</p><a class="button dark" href="schedule.html">Explore the class schedule →</a></div></div></section>
<section class="banner"><div class="wrap"><h2>FIND YOUR REASON TO TRAIN.</h2><p>{escape(COPY['closing'])} Ask about our 3 months for $300 offer.</p><div class="buttons" style="justify-content:center"><a class="button" href="contact.html#offer-form">Ask about this offer →</a><a class="button outline" href="programs.html">Find your program</a></div></div></section>
</main>'''
    return '<!DOCTYPE html>\n<html lang="en">' + str(head) + '<body class="about-page"><a class="skip-link" href="#main-content">Skip to content</a>' + header + content + footer + '<script>' + navigation_script + '</script></body></html>\n'


def integrate_navigation():
    home = (ROOT / 'index.html').read_text()
    footer = re.search(r'<footer\b[\s\S]*?</footer>', home).group(0)
    if 'href="about.html"' not in footer:
        footer = footer.replace('<a href="programs.html">Programs</a>', '<a href="about.html">About Professor Brandon</a><a href="programs.html">Programs</a>', 1)
    for page in ROOT.glob('*.html'):
        text = page.read_text()
        header_match = re.search(r'<header\b[\s\S]*?</header>', text)
        if header_match:
            header = BeautifulSoup(header_match.group(0), 'html.parser')
            nav = header.select_one('.nav')
            if nav:
                if not nav.find('a', href='about.html'):
                    link = header.new_tag('a', href='about.html')
                    link.string = 'About'
                    nav.find('a', href='programs.html').insert_before(link)
                for link in nav.find_all('a'):
                    classes = [value for value in link.get('class', []) if value != 'active']
                    link.attrs.pop('aria-current', None)
                    if link.get('href') == page.name:
                        classes.append('active')
                        link['aria-current'] = 'page'
                    if classes:
                        link['class'] = classes
                    else:
                        link.attrs.pop('class', None)
                text = text[:header_match.start()] + str(header) + text[header_match.end():]
        text = re.sub(r'<footer\b[\s\S]*?</footer>', lambda _: footer, text, count=1)
        text = re.sub(r'assets/site\.css(?:\?[^"\s<>]*)?', 'assets/site.css?v=20261102-about', text)
        page.write_text(text)


def punctuation():
    replacements = {
        'Competition is optional—there is more than one reason to train.': 'Competition is optional. There is more than one reason to train.',
        'Competing is a choice—not a requirement to train.': 'Competing is a choice, not a requirement to train.',
        '“Finally—after too long—back on the mats.”': 'Back on the mats after some time away.',
        'Washington—from programs': 'Washington, from programs',
        'Washington—located at': 'Washington, located at',
        'Public library — not private.': 'Public library, not private.'
    }
    paths = list(ROOT.glob('*.html')) + [ROOT / 'scripts/build_gallery.py']
    for path in paths:
        text = path.read_text()
        for before, after in replacements.items():
            text = text.replace(before, after)
        if path.name == 'photo-library.html':
            text = text.replace('>—<', '>Loading<')
        path.write_text(text)


def sitemap():
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    ET.register_namespace('', ns)
    path = ROOT / 'sitemap.xml'
    tree = ET.parse(path)
    urls = tree.getroot()
    found = False
    for node in urls:
        loc = node.find('{' + ns + '}loc')
        if loc.text.rstrip('/') == URL:
            found = True
        modified = node.find('{' + ns + '}lastmod')
        if modified is not None:
            modified.text = DATE
    if not found:
        node = ET.SubElement(urls, '{' + ns + '}url')
        ET.SubElement(node, '{' + ns + '}loc').text = URL
        ET.SubElement(node, '{' + ns + '}lastmod').text = DATE
        ET.SubElement(node, '{' + ns + '}priority').text = '0.8'
    ET.indent(tree, space='  ')
    tree.write(path, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    (ROOT / 'about.html').write_text(create_page())
    integrate_navigation()
    punctuation()
    sitemap()
    print('About page built: verified biography, all four original-source photos, shared navigation/footer and sitemap.')
