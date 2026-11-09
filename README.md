# Northwest Clear Exteriors mockup

Static multi-page site for Cloudflare Pages. No build step. Build command: none. Output directory: /.

At launch: remove the noindex meta from each page, set robots.txt to allow and add `Sitemap: https://<domain>/sitemap.xml`, and replace `https://1nwc-clearexterior-mockup.pages.dev` with the real domain in canonical, og:url, og:image, the JSON-LD schema and sitemap.xml.

## Pages

- `/` (home)
- `/services/window-cleaning/`, `/services/pressure-washing/`, `/services/roof-cleaning/`, `/services/gutter-cleaning/`, `/services/house-washing/`, `/services/solar-panel-cleaning/`
- `/gallery/`, `/reviews/`, `/about/`, `/contact/`, `404.html`
- `/exterior-cleaning-anacortes-wa/`, `/exterior-cleaning-mount-vernon-wa/`, `/exterior-cleaning-burlington-wa/`, `/exterior-cleaning-camano-island-wa/`, `/exterior-cleaning-la-conner-wa/`, `/exterior-cleaning-sedro-woolley-wa/`, `/exterior-cleaning-stanwood-wa/`
- Old one-page links (`/#svc-windows` and so on) redirect to the new pages. `/services/` redirects to Window Cleaning (`_redirects`).

## Behavior (same approach as Bullseye, Kane, Red Line)

- Every page is its own HTML file, so Back, Forward and Refresh are handled by the browser. A head script restores the scroll spot before the first paint on refresh and Back. A link to the page you are on scrolls to the top. The menu, its dropdowns and the photo viewer close when you come back with Back. Mobile menu dropdowns always open collapsed.
- Mobile hero height uses `--vh`, set once on load (after the viewport meta) and again only on rotation. The home hero is taller than the screen on phones: `max(100lvh + 20px, 100 × --vh + 120px)`.
- Home reviews are a looping carousel: the cards are in the track three times and it wraps back to the middle set after each swipe or arrow tap. The reviews page shows 6 at a time (4 on phones).
- TikTok in-app browser: a head script adds `tt` to `<html>`; CSS hides videos and play buttons and the JS skips video loading.
- Hero video: desktop or phone file picked before it loads, starts once the page has loaded, fades in over its poster. Clips wait 200ms after load, play only on screen, fade in when playing. If autoplay is blocked, any tap starts them and a Tap to play button shows. Video files are untouched (no re-encoding).
- Photos past the first section load as you scroll near them (same files, same quality).
- Jobber quote form loads on the Contact page after the page has loaded. Maps load when scrolled near.

## Editing

`build.py` regenerates every page from the single-file design (`NWClear19.html`): `python3 build.py NWClear19.html out`. CSS is inlined (minified) in each page; `assets/style.css` is the readable source. `assets/main.js` is minified with terser from `assets/main.src.js`; bump the `?v=` after changing it.
