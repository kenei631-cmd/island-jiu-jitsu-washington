# Direct legacy redirects: SEO decision and remaining routing work

Decision date: November 3, 2026. Keep `https://www.islandjiujitsuwa.com/` as the public canonical origin. Do not migrate canonical metadata, sitemap, structured data or internal links to a different hostname merely to move the automatic host-redirect hop to the other hostname.

## Verified current behavior

All 24 configured legacy/HTML aliases on the HTTPS www host return exactly one server-side 301 to an existing final trailing-slash page, followed by HTTP 200. The same 24 aliases on the original Netlify hostname also use one 301 directly to the final www page. All 24 non-www aliases use two 301s: Netlify's automatic apex-to-www normalization first, then the configured path alias. These 72 combinations were tested successfully on November 3, 2026. Separately, all 11 canonical Netlify page copies use one 301 to www and their final www pages return direct 200 responses.

The remaining chain is real and not claimed fixed. For example:

`https://islandjiujitsuwa.com/about.html` → `https://www.islandjiujitsuwa.com/about.html` → `https://www.islandjiujitsuwa.com/about/`

Required final behavior:

`https://islandjiujitsuwa.com/about.html` → `https://www.islandjiujitsuwa.com/about/` → HTTP 200

Tracking parameters are preserved. Unknown paths return actual 404s rather than being redirected indiscriminately to the homepage. All 12 generated HTML pages were checked for internal HTML-alias/non-www links; none were found. The live About page was also inspected and uses its final self-canonical URL.

## Why preserve the canonical hostname

Google recommends permanent server-side redirects directly to the final destination. When a direct redirect is not possible, Google advises keeping chains low, ideally no more than three and fewer than five. A two-hop chain is therefore not the desired final outcome, but it is not a reason to perform a needless canonical-host migration. This is a recommendation to preserve consistent canonical signals and existing working routes, not a guarantee of indexing or rankings.

Netlify documents automatic apex/www normalization to the configured primary domain. The built-in domain redirect precedes the site's path redirect in the observed production response. Adding another apex-qualified `_redirects` entry alone does not establish that the earlier built-in redirect can be bypassed. Merely choosing the apex as primary would shift the extra host hop to www legacy URLs instead of removing chains for both hosts.

## Routing required to eliminate the outstanding chain

An HTTPS-capable, path-aware redirect handler must receive the non-www requests before Netlify's automatic hostname normalization. It must combine the hostname and old-path mapping in a single 301 whose Location is the exact final HTTPS www URL. Equivalent mappings must be available for HTTP entry points if a strict one-hop outcome is required for every protocol variant; those HTTP variants were not included in the 72 HTTPS legacy tests.

Public DNS inspection on November 3 found authoritative nameservers `hgns1.hostgator.com` and `hgns2.hostgator.com`. The www CNAME points to `island-jiu-jitsu-washington.netlify.app`. DNS alone cannot map `/about.html` to `/about/`; it must point to a working redirect service. A verified Netlify domain configuration alternative or an independently hosted redirect endpoint could provide the HTTP layer, but no such alternative has been provisioned or proven for this account.

Before changing traffic, confirm authorized control of the relevant domain/hosting account, select and stage the redirect endpoint, verify its TLS coverage and every target, record the exact existing apex DNS values for rollback, and check certificate renewal effects on the Netlify www site. Preserve all MX/TXT mail and verification records and keep the current www CNAME, form action, photo asset URLs and canonical metadata unchanged. Present the exact configuration and any service costs before switching live traffic. No DNS records, primary-domain settings or hosting assignments were changed during this review.

## Regression protection

`scripts/verify_technical_seo_build.py` now checks that every generated redirect target is an existing self-canonical page on the approved HTTPS www host, that no target is another explicit rule source, and that generated internal links do not use legacy aliases or the non-www hostname. This detects future site-rule chains before deployment; it does not override or prove the absence of Netlify's automatic domain/TLS redirects.

## Sources

- Google site moves and redirect strategy: https://developers.google.com/search/docs/crawling-indexing/site-move-with-url-changes
- Google server-side permanent redirects and canonical signals: https://developers.google.com/search/docs/crawling-indexing/301-redirects
- Netlify automatic apex/www normalization: https://docs.netlify.com/manage/domains/manage-domains/manage-multiple-domains/
- Netlify product/support explanation of automatic TLS and primary-domain redirects: https://answers.netlify.com/t/improvements-to-tls-and-primary-domain-redirects-for-non-static-assets/74903
- Netlify support example of separately managed apex routing: https://answers.netlify.com/t/www-domain-com-only-as-primary-domain-with-no-apex-domain-set-up-on-netlify/140115
