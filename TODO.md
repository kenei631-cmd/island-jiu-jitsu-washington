# Homepage offer update

- [x] Remove the promotional popup completely, including its dialog markup, timer, focus trap and session-storage behavior, while retaining normal navigation and schedule controls.
- [x] Make “3 months for $300” the main offer in the homepage hero, preserve the approved January 1–April 1 dates and academy/location context, and provide a prominent CTA linking to the existing offer inquiry form at `contact.html#offer-form` instead of repeating the offer in a separate homepage strip.
- [x] Preserve the existing academy photography, programs, schedule, inquiry form, SEO metadata, shared footer, Netlify image hosting and pre-launch crawl settings; verify the updated platform layout before pushing to GitHub and publishing to Netlify.

Pre-publish evidence: the actual homepage was visually reviewed; browser checks at 1280, 390 and 320 pixels showed the CTA within the initial viewport, no horizontal overflow and no promotional popup after the former timer interval. Mobile navigation opened and closed normally. Clicking the hero CTA landed at the existing offer form with the offer selected and message prefilled, without submitting it. Static checks confirmed unchanged schedules, matching sitewide footers, retained structured data and the 352-photo library.
