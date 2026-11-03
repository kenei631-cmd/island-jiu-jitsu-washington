# Netlify DNS cutover guidance

Checked November 3, 2026. The existing Netlify project API reports islandjiujitsuwa.com as its primary site URL. No settings or DNS records were changed during this check.

In the supplied DNS screenshot, the website apex A record is host @ pointing to 50.6.19.152. For standard Netlify external DNS, replace this record's value with 75.2.60.5, keeping type A and TTL 1 Hour. Leave autoconfig, autodiscover and localhost unchanged; do not change MX or other email records. A www CNAME should point to island-jiu-jitsu-washington.netlify.app, without a protocol or path. Review existing www records for conflicts rather than adding duplicate records.

Netlify recommends ALIAS/ANAME/flattened CNAME to apex-loadbalancer.netlify.com where supported, with A 75.2.60.5 as the fallback. Dedicated High-Performance Edge configurations use different provider-specified values; use customized domain verification instructions if those apply.

Source: https://docs.netlify.com/manage/domains/configure-domains/configure-external-dns/ (opened and read). DNS propagation may take several hours and up to a day.

Historical launch issues at the time of the DNS question: the current form uses FormSubmit and had not passed an end-to-end delivery test. That deployment retained pre-launch X-Robots-Tag: noindex, nofollow. The user's DNS question asked which record to change, not authorization for the agent to edit DNS.

Technical audit update, November 3, 2026: the existing primary host is now https://www.islandjiujitsuwa.com/. The production noindex blocker was removed, custom-domain HTTPS and the nine canonical marketing pages passed live verification, and utility exclusions were retained. No DNS or domain settings were changed by the audit. FormSubmit inbox delivery still needs confirmation.
