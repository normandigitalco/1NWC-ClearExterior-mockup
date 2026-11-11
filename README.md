# Northwest Clear Exteriors mockup

Static multi-page site for Cloudflare Pages. No build step. Build command: none. Output directory: /.

At launch: remove the noindex meta from each page, set robots.txt to allow and add `Sitemap: https://<domain>/sitemap.xml`, and replace `https://1nwc-clearexterior-mockup.pages.dev` with the real domain in canonical, og:url, og:image, the JSON-LD schema and sitemap.xml.

## Pages

- `/` (home)
- `/services/window-cleaning/`, `/services/pressure-washing/`, `/services/roof-cleaning/`, `/services/gutter-cleaning/`, `/services/house-washing/`, `/services/solar-panel-cleaning/`, `/services/holiday-lights/`
- `/gallery/`, `/reviews/`, `/about/`, `/contact/`, `/privacy/`, `404.html`
- `/exterior-cleaning-anacortes-wa/`, `/exterior-cleaning-mount-vernon-wa/`, `/exterior-cleaning-burlington-wa/`, `/exterior-cleaning-camano-island-wa/`, `/exterior-cleaning-la-conner-wa/`, `/exterior-cleaning-sedro-woolley-wa/`, `/exterior-cleaning-stanwood-wa/`
- Old one-page links (`/#svc-windows` and so on) redirect to the new pages. `/services/` redirects to Window Cleaning (`_redirects`).

## Behavior (same approach as Bullseye, Kane, Red Line)

- Every page is its own HTML file, so Back, Forward and Refresh are handled by the browser. A head script restores the scroll spot on refresh and Back, hiding the page for a moment until it is back in place (Bullseye approach). Sections already on screen or above it show at once. A link to the page you are on scrolls to the top. The menu, its dropdowns and the photo viewer close when you come back with Back. Mobile menu dropdowns always open collapsed.
- Mobile hero height uses `--vh`, set once on load (after the viewport meta) and again only on rotation. The home hero is taller than the screen on phones: `max(100lvh + 20px, 100 × --vh + 120px)`.
- Home reviews are a looping carousel: the cards are in the track three times and it wraps back to the middle set after each swipe or arrow tap. Height-only resizes (the phone address bar) are ignored; on rotation it stays on the same card. The reviews page shows 6 at a time (4 on phones).
- TikTok in-app browser: a head script adds `tt` to `<html>`; CSS hides videos and play buttons and the JS skips video loading.
- Hero video: desktop or phone file picked before it loads, starts once the page has loaded, fades in over its poster. Clips wait 200ms after load, play only on screen, fade in when playing. If autoplay is blocked, any tap starts them and a Tap to play button shows. Video files are untouched (no re-encoding).
- Photos past the first section load as you scroll near them (same files, same quality).
- Jobber quote form loads on the Contact page after the page has loaded. Maps load when scrolled near.

## Editing

`build.py` regenerates every page from the single-file design (`NWClear19.html`): `python3 build.py NWClear19.html out`. CSS is inlined (minified) in each page; `assets/style.css` is the readable source. `assets/main.js` is minified with terser from `assets/main.src.js`; bump the `?v=` after changing it.

## Round 2 (client notes, Nov 10)

- **Home hero:** headline is "Premium Exterior Cleaning". Desktop plays `hero-w.mp4` (one wide clip cropped from the phone video) once and phones play `hero-m.mp4` once, then both fade into a slow photo slideshow (`/img/hs-1..6-d.webp` on desktop, `-m.webp` on phones). To use a different video, change `HERO_D` / `HERO_M` in `assets/main.src.js`.
- **Pop color:** every quote and call button uses `.btn-pop` (`--pop:#f7a823`, navy text).
- **Licensed, Bonded & Insured:** home hero, home trust card, a credentials strip under every service, area, About and Gallery header (`.cred`), every CTA band and the footer.
- **Holiday lights:** new page `/services/holiday-lights/`, in the Services menus, footer, sitemap and a card on the home page.
- **Service area map:** `/img/area-map.svg` (drawn from county outlines) with HTML pins that link to each city page. On the home page (replaces the Google embed there) and on every area page with that town's pin highlighted.
- **Service pages:** Victor's wording for windows, roof, gutters and house washing (why sections, process cards, FAQs, roof types), and his real job photos in place of the stand-in photos (roof, gutter, house washing, pressure washing and solar heroes, CTA bands and cards). Before and after pairs live on the Gallery board.
- **Gallery:** a third grid of new photos, and a before and after board: befores on the left, afters on the right, filter by service, 6 rows at a time.
- **Photos:** every new photo has a full size (1600px, used by the photo viewer and big screens), an `-800` and a `-480` version, loaded only when scrolled near (`data-src`/`data-srcset`).
- **Quote form speed:** the Jobber iframe is in the Contact page HTML, so it starts loading with the page. Pointing at or pressing any quote link on another page warms up the Jobber connection and prefetches the form, and the Contact page is prerendered on hover.

**Editing from now on:** edit the page HTML directly. Do not rerun `build.py` from the single-file design: it would overwrite these changes. CSS: edit `assets/style.css`, then minify it with lightningcss and paste it into the `<style>` of every page. JS: edit `assets/main.src.js`, run terser to `assets/main.js` and bump `?v=`.

## Launch checklist

1. Confirm with Victor: hours, email address (`nwclearexteriors.com` vs `northwestclearexteriors.com`), and the same name, phone and address on Google, Yelp, BBB and Nextdoor.
2. Run `python3 launch.py https://www.<real-domain>` (removes `noindex`, swaps the mockup address everywhere, opens `robots.txt` with the sitemap line). Commit and push.
3. Connect the domain in Cloudflare Pages.
4. Google Search Console: verify the domain, submit `/sitemap.xml`, request indexing for the home page and service pages.
5. Google Business Profile: set the website to the new domain and link the service pages.
6. GA4 if wanted.

## SEO setup

- Titles: `Service in Anacortes, WA | Northwest Clear Exteriors` and `Exterior Cleaning in Town, WA | Northwest Clear Exteriors`. H1 repeats the service or town plus `, WA`; the line under it starts with the service name.
- Meta descriptions 140 to 165 characters, with service, city and "Licensed, bonded and insured".
- Schema: `HomeAndConstructionBusiness` (`@id …/#business`) on the home page; `Service` (provider = the business, areaServed = the towns) on each service and town page; `BreadcrumbList` on every inner page; `FAQPage` wherever there is an FAQ.
- Internal links: every service page links to all 7 town pages ("near you" section), every town page links to all 7 service pages (under the map).
- `sitemap.xml` has `lastmod`. Update it when pages change.
