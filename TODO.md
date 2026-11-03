# Technical SEO audit and repairs

- [x] Audit only live, published pages. Use the nine canonical sitemap pages for marketing SEO and check the published photo library and thank-you page separately. Exclude drafts and unpublished content; controlled missing-URL requests are status probes, not draft crawling.
- [x] Make marketing pages technically eligible for indexing on the primary custom domain: consistent HTTPS www canonical URLs, crawlable initial HTML, robots/sitemap alignment, correct permanent redirects, genuine 404 responses and no unintended noindex on marketing pages. Preserve intentional noindex on the public asset library, confirmation page and error content.
- [x] Ensure page-specific titles/descriptions, social metadata, structured data, visible NAP and class-hours information remain accurate and consistent. Preserve approved offers, schedule, personal biography and real photo content. Qualify the future Friday women's class start date as November 13, 2026 in visible content and relevant hours markup.
- [x] Check published link/resource loading, responsive image boxes, mobile navigation and measured lab loading performance. Retain all 352 library photos and 1,056 optimized variants at existing asset paths. Resolve the isolated thumbnail request timeout with a focused HTTP 200, byte-identical retry.
- [x] Fix confirmed technical issues, verify changes directly on the current platform before publication, deploy to the existing Netlify project and verify affected live behavior afterward. Final favicon release 6aea58f54ec34c8c9f186717 is ready in production; the final nine-page verification passed November 3, 2026 and exported page results. Credentials remain outside the website.

## Remaining follow-ups, not claimed complete

- [ ] Use Search Console URL Inspection to request recrawling of key marketing URLs and monitor indexing after removal of the production noindex blocker. Google indexing, ranking and favicon appearance are not guaranteed.
- [ ] Complete an end-to-end FormSubmit test with confirmed recipient inbox delivery. Field validation and submission contract passed, but human verification prevented confirmation of delivery.
- [ ] Further optimize mobile gallery loading. Post-release lab Performance scores varied from 71 to 84; confirmation LCP was 2.6 seconds and CLS 0. No real-user Core Web Vitals pass has been established.
- [ ] Configure GitHub-triggered Netlify builds separately from source synchronization. The live release was published through the existing Netlify connection, not an automatic repository build. Review the historical GitHub Pages mirror's indexing policy when consolidating hosting.
