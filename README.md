# Island Jiu-Jitsu Washington

Static marketing website for Island Jiu-Jitsu Washington.

## Current public site

<https://kenei631-cmd.github.io/island-jiu-jitsu-washington/>

## Netlify pre-launch staging

Project: `island-jiu-jitsu-washington` in the FANNIT team.

Staging URL: <https://island-jiu-jitsu-washington.netlify.app/>

Dashboard: <https://app.netlify.com/projects/island-jiu-jitsu-washington>

Netlify project ID: `7715e103-044b-4953-b640-aafbccd10f02`.

`netlify.toml` specifies `python3 scripts/build_netlify.py` with publish directory `netlify-dist`. The build copies only public HTML, assets, and crawl/manifest documents. It adds a Netlify-only `X-Robots-Tag: noindex, nofollow` header to avoid indexing the pre-launch copy and sends offer-form confirmations to the same Netlify deployment. GitHub Pages is not changed by these generated staging adjustments.

The initial Netlify deployment uses the Netlify connector. Automatic GitHub-to-Netlify deployment is not yet configured: the connector's exposed project operations do not provide repository linking. When linking the existing repository in Netlify, use `kenei631-cmd/island-jiu-jitsu-washington`, production branch `main`, and the committed build settings. Do not create or clone a second GitHub repository.

Netlify local state (`.netlify/`) and build output (`netlify-dist/`) are ignored by Git.

## Pages

- `index.html` — homepage
- `programs.html` — adult, kids, and women-only programs
- `schedule.html` — current class schedule and membership pricing
- `contact.html` — address, maps, registration, and offer inquiry form
- `faq.html` — academy FAQ
- `smokey-point.html` — Smokey Point landing page
- `lakewood-north-marysville.html` — Lakewood and North Marysville landing page
- `thank-you.html` — form confirmation, noindex
- `404.html` — custom not-found page

## SEO files

- `robots.txt` and `sitemap.xml`
- canonical, Open Graph, Twitter Card, and LocalBusiness structured data on public pages

Canonical and sitemap URLs remain on GitHub Pages until the approved custom-domain launch. Before launch, update the canonical origin, social/structured-data URLs and sitemap/robots consistently; remove the staging noindex header in `scripts/build_netlify.py`; and verify HTTPS, form routing, pages and a real 404. No domain or DNS changes are made by this setup.

## Local preview and staging build

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

```bash
python3 scripts/build_netlify.py
python3 -m http.server 8001 --directory netlify-dist
```

Class times, pricing, and offers should be reviewed and updated whenever they change.

## Web-optimized photo repository

Browse <https://island-jiu-jitsu-washington.netlify.app/photo-library.html> for filename search, orientation filtering, previews, direct image URLs and responsive HTML snippets. Download the filename/URL inventory at <https://island-jiu-jitsu-washington.netlify.app/assets/photos/library.csv>.

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
