# Photo library

- [x] Import the supplied William Wallace photo archive as optimized assets in the existing Island Jiu-Jitsu GitHub working copy, without publishing the original ZIP or original photos.
- [x] Correct orientation, normalize embedded color profiles, strip EXIF/GPS metadata, preserve the full frame, and make thumbnail, medium, and large WebP variants without upscaling.
- [x] Deduplicate identical source files and provide a searchable photo index, original filename mapping, dimensions, size data and direct Netlify links.
- [x] Match the existing site header/footer, retain staging noindex, use responsive uncropped images, and do not replace marketing photos or modify the domain.
- [x] Verify every WebP and the actual local library page, preview controls, mobile viewport, shared footer and unchanged schedule before pushing.
- [x] Deploy through the existing Netlify connection and verify the live catalog, sampled image URLs, cache headers and loaded browser interface.

Netlify deployment: `6ae8eb4d1679b164122b3f91` (ready). The clean `netlify-dist` output was deployed after the full working-directory upload timed out without publishing. The library contains 352 unique photos, 20 duplicate aliases and 1,056 optimized WebP files. The MOV and original archive are excluded.
