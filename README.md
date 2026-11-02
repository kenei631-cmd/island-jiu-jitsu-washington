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
