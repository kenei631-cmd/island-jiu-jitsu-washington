"""Build a clean static Netlify staging copy without changing GitHub Pages.

Before the custom-domain launch, replace the canonical origin in source HTML,
sitemap and robots, then remove the staging noindex header below.
"""
from pathlib import Path
import os
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "netlify-dist"
STAGING_ORIGIN = os.environ.get("DEPLOY_PRIME_URL") or os.environ.get("URL") or "https://island-jiu-jitsu-washington.netlify.app"
STAGING_ORIGIN = STAGING_ORIGIN.rstrip("/")
if not STAGING_ORIGIN.startswith("https://"):
    raise SystemExit("Netlify staging origin must use HTTPS")

if OUTPUT.exists():
    shutil.rmtree(OUTPUT)
OUTPUT.mkdir()

for page in ROOT.glob("*.html"):
    source = page.read_text(encoding="utf-8")
    if page.name == "contact.html":
        source, count = re.subn(
            r'(<input\b[^>]*name="_next"[^>]*value=")[^"]*(")',
            lambda match: match.group(1) + STAGING_ORIGIN + "/thank-you.html" + match.group(2),
            source,
        )
        if count != 1:
            raise SystemExit("Expected exactly one offer form confirmation URL")
    (OUTPUT / page.name).write_text(source, encoding="utf-8")

shutil.copytree(ROOT / "assets", OUTPUT / "assets")
for filename in ["robots.txt", "sitemap.xml", "site.webmanifest"]:
    shutil.copy2(ROOT / filename, OUTPUT / filename)

# Allow crawling so bots can see noindex, but do not index the pre-launch copy.
# This header is Netlify-only: it does not alter the GitHub Pages site.
(OUTPUT / "_headers").write_text(
    "/*\n"
    "  X-Robots-Tag: noindex, nofollow\n"
    "  X-Content-Type-Options: nosniff\n"
    "  Referrer-Policy: strict-origin-when-cross-origin\n"
    "/assets/site.css\n"
    "  Cache-Control: public, max-age=0, must-revalidate\n"
    "/assets/photos/william-wallace/*\n"
    "  Cache-Control: public, max-age=31536000, immutable\n"
    "/assets/photos/library.json\n"
    "  Cache-Control: public, max-age=0, must-revalidate\n"
    "/assets/photos/library.csv\n"
    "  Cache-Control: public, max-age=0, must-revalidate\n"
    "/assets/photo-library.css\n"
    "  Cache-Control: public, max-age=0, must-revalidate\n"
    "/assets/photo-library.js\n"
    "  Cache-Control: public, max-age=0, must-revalidate\n",
    encoding="utf-8",
)
print(f"Netlify staging build: {len(list(OUTPUT.glob('*.html')))} pages in {OUTPUT}")
print(f"Offer confirmation URL: {STAGING_ORIGIN}/thank-you.html")
print("Search indexing disabled for this pre-launch Netlify copy.")
