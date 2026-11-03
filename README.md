# Island Jiu-Jitsu Washington

Static marketing website for Island Jiu-Jitsu Washington.

## GitHub Pages copy

<https://kenei631-cmd.github.io/island-jiu-jitsu-washington/>

## Netlify production

Project: `island-jiu-jitsu-washington` in the FANNIT team.

Primary URL: <https://www.islandjiujitsuwa.com/>. The Netlify.app page-copy URLs redirect to this host; existing direct Netlify photo asset URLs remain available.

Dashboard: <https://app.netlify.com/projects/island-jiu-jitsu-washington>

Netlify project ID: `7715e103-044b-4953-b640-aafbccd10f02`.

The current Netlify primary domain is <https://www.islandjiujitsuwa.com/>. `netlify.toml` installs `requirements.txt` and runs `python3 scripts/build_netlify.py` with publish directory `netlify-dist`. Source HTML remains flat for GitHub Pages; Netlify generates `route/index.html` pages with trailing-slash canonical URLs, root-absolute resources and explicit legacy 301 rules. Production marketing pages are indexable. Only non-production builds use the global `X-Robots-Tag: noindex, nofollow` gate; the public asset library, confirmation and error content retain their individual exclusions. Offer-form confirmations point to `/thank-you/` on the primary host. No DNS or Netlify domain setting is changed by this build.

The initial Netlify deployment uses the Netlify connector. Automatic GitHub-to-Netlify deployment is not yet configured: the connector's exposed project operations do not provide repository linking. When linking the existing repository in Netlify, use `kenei631-cmd/island-jiu-jitsu-washington`, production branch `main`, and the committed build settings. Do not create or clone a second GitHub repository.

Netlify local state (`.netlify/`) and build output (`netlify-dist/`) are ignored by Git.

## Pages

- `index.html`: homepage
- `about.html`: Professor Brandon’s history, family, academy principles, Coach Micah and four original-source academy photos
- `programs.html`: adult, kids, and women-only programs
- `schedule.html`: current class schedule and membership pricing
- `contact.html`: address, maps, registration, and offer inquiry form
- `faq.html`: academy FAQ
- `smokey-point.html`: Smokey Point landing page
- `lakewood-north-marysville.html`: Lakewood and North Marysville landing page
- `thank-you.html`: form confirmation, noindex
- `404.html`: custom not-found page

## SEO files

- `robots.txt` and `sitemap.xml`
- canonical, Open Graph, Twitter Card, and LocalBusiness structured data on public pages

Source canonical and sitemap URLs use GitHub Pages. The Netlify build rewrites metadata and sitemap URLs to the existing primary custom domain and canonical slash paths. `SITE_ORIGIN` can override the configured canonical origin explicitly. Production marketing pages are indexable; the photo library, thank-you page and error page remain individually noindex. `INDEXABLE=false` enables a global indexing block for non-production builds, and deploy-preview/branch-deploy contexts set it explicitly. Published Netlify.app page copies redirect to the primary custom domain, while stable Netlify photo asset URLs remain available. The form still uses FormSubmit; its inbox-delivery test remains unconfirmed.

The November 2026 technical SEO update externalizes all nine original WOFF2 font faces into exact-byte hashed assets with long-lived caching. The shared stylesheet retains all route and responsive rules; no photos or typography were substituted. Needed body/headline fonts are preloaded, the header logo loads eagerly into a reserved box, and the existing stacked weekly schedule no longer inherits a desktop minimum width on phones.

Square opaque favicon PNGs at 180, 192 and 512 pixels and the legacy `favicon.ico` are derived only from the supplied academy logo. `scripts/build_favicons.py` regenerates them without creating new artwork or cropping the original mark. All source pages reference the 192-pixel favicon and the 180-pixel Apple touch icon; the manifest uses the 192- and 512-pixel icons. Keep their public URLs stable.

## Local preview and staging build

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/build_netlify.py
python3 -m http.server 8001 --directory netlify-dist
```

Class times, pricing, and offers should be reviewed and updated whenever they change.

## Web-optimized photo repository

Browse <https://www.islandjiujitsuwa.com/photo-library/> for filename search, orientation filtering, previews, direct image URLs and responsive HTML snippets. Copied photo URLs retain their stable Netlify asset address. Download the filename/URL inventory at <https://island-jiu-jitsu-washington.netlify.app/assets/photos/library.csv>.

The William Wallace ZIP contains 372 photos and one MOV. This import hosts 352 unique photos after removing 20 exact duplicate copies, with the duplicates mapped in the catalog. The video is excluded from this photo-only import; the original ZIP and original photos remain untouched outside the Git repository.

Each photo has three WebP variants, capped at 320, 960 and 1920 pixels on its longest edge, with no upscaling or cropping. The collection's 1,056 variants total 102,292,524 bytes, compared with 916,512,845 bytes of source photos including duplicate copies. Large versions alone total 74,876,604 bytes. EXIF/GPS/XMP metadata is stripped, orientation is corrected, and embedded color profiles are normalized where supported. Existing visible watermarks are retained.

Files live in `assets/photos/william-wallace/`, and `assets/photos/library.json` maps original filenames to dimensions, hashes and variant paths. Content hashes in filenames support long-lived Netlify caching. Keep these URLs stable; do not delete a hosted file that has been used in page content.

The library is publicly reachable, not a private media vault. It uses noindex and is intentionally absent from the marketing navigation and sitemap. Confirm model/parent permissions and photographer rights before using a photo in advertising or public marketing. Replace the copied HTML's generic alt-text placeholder with a truthful description of the selected image.

To recreate this specific collection from the same source archive, install Pillow with WebP support and run:

```bash
python3 scripts/optimize_photos.py /path/to/iCloudPhotosfromWilliamWallace.zip
python3 scripts/build_netlify.py
```

Future collections should have their own folder and be merged into the catalog rather than overwriting this collection. Photo optimization is performed once locally; Netlify builds only copy the committed optimized files, so deployment does not require the original ZIP or Pillow.

Image-display choices follow [web.dev responsive-image guidance](https://web.dev/learn/design/responsive-images) for full-frame `object-fit: contain`, real dimensions and responsive width descriptors, and [browser lazy-loading guidance](https://web.dev/articles/browser-level-image-lazy-loading) for deferred offscreen thumbnails and reserved image space.

## About page

`python3 scripts/build_about.py` renders the page using `docs/about-content.json` and `docs/about-photo-variants.json`. Biography sources are recorded in `docs/brandon-about-sources.md`. The four original photographs from the academy’s existing About page have three metadata-free WebP variants each in `assets/images/`; original proportions are preserved, with no AI editing or cropping. `assets/about.css` contains the page-specific layout. The generator also keeps the About navigation/footer links and sitemap entry synchronized.

The Netlify site is being updated through the existing API connection. Source synchronization is separate from publishing: ensure the latest source is pushed before enabling repository-triggered Netlify builds. Review the historical GitHub Pages mirror's indexing policy when consolidating hosting. No domain or DNS change has been made by these source updates.

## Legacy 301 redirects

Google `site:` searches for the apex and www domain returned no documents in the user's My Browser on November 3, 2026. `docs/legacy-url-discovery.md` records that limitation and the original-site navigation evidence, not an exhaustive Google index export. `legacy-redirect-map.json` maps confirmed historical page URLs to relevant replacements: home, About, Schedule, Contact and Gallery / News (`/blog.html` to `/gallery/`).

The build emits 24 exact permanent redirects in `netlify-dist/_redirects`, with a source copy in `redirects-generated.txt`. Directory output lets Netlify natively redirect bare paths to slash paths; forced same-route slash rules are omitted because Netlify matches them as equivalent and can loop. Unknown routes remain real 404s. Public navigation, sitemap and structured data use slash destinations; image bytes and catalog paths are unchanged.

`python3 scripts/verify_redirects.py` checks the configured response paths and updates `output/Island-Jiu-Jitsu-301-Redirect-Inventory.csv` with observed status codes, locations and hop counts. Canonical-www page aliases require a single 301 to a 200 response. The five original non-www URLs are recorded separately because the existing Netlify host redirect may precede the page redirect. This verification is an allowlisted HTTP response check, not another website-discovery crawl.
