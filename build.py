#!/usr/bin/env python3
"""Split the single-file NWClear build into a static multi-page site (Cloudflare Pages, no build step).
Usage: python3 build.py SRC.html OUTDIR
Mirrors the Bullseye / Kane setup: one HTML file per page, inlined minified CSS, shared main.js,
scroll restore on refresh/back, --vh hero height, looping home review carousel, TikTok in-app fallback."""
import re, sys, os, json, subprocess, html

SRC, OUT = sys.argv[1], sys.argv[2]
BASE = 'https://1nwc-clearexterior-mockup.pages.dev'
VER = '1'
s = open(SRC, encoding='utf-8').read()

URL = {
 'home': '/',
 'svc-windows': '/services/window-cleaning/',
 'svc-pressure': '/services/pressure-washing/',
 'svc-roof': '/services/roof-cleaning/',
 'svc-gutters': '/services/gutter-cleaning/',
 'svc-house': '/services/house-washing/',
 'svc-solar': '/services/solar-panel-cleaning/',
 'gallery': '/gallery/',
 'area-anacortes': '/exterior-cleaning-anacortes-wa/',
 'area-mount-vernon': '/exterior-cleaning-mount-vernon-wa/',
 'area-burlington': '/exterior-cleaning-burlington-wa/',
 'area-camano-island': '/exterior-cleaning-camano-island-wa/',
 'area-la-conner': '/exterior-cleaning-la-conner-wa/',
 'area-sedro-woolley': '/exterior-cleaning-sedro-woolley-wa/',
 'area-stanwood': '/exterior-cleaning-stanwood-wa/',
 'reviews': '/reviews/',
 'about': '/about/',
 'contact': '/contact/',
}
T = ' | Northwest Clear Exteriors'
TITLE = {
 'home': 'Northwest Clear Exteriors | Window Cleaning, Roof Cleaning and Moss Removal in Anacortes, WA',
 'svc-windows': 'Window Cleaning in Anacortes and Skagit County' + T,
 'svc-roof': 'Roof Cleaning and Moss Removal' + T,
 'svc-gutters': 'Gutter Cleaning and Gutter Brightening' + T,
 'svc-house': 'House Washing and Soft Washing' + T,
 'svc-pressure': 'Pressure Washing for Driveways and Walkways' + T,
 'svc-solar': 'Solar Panel Cleaning' + T,
 'area-anacortes': 'Window and Exterior Cleaning in Anacortes, WA' + T,
 'area-mount-vernon': 'Window and Exterior Cleaning in Mount Vernon, WA' + T,
 'area-burlington': 'Window and Exterior Cleaning in Burlington, WA' + T,
 'area-camano-island': 'Window and Exterior Cleaning on Camano Island, WA' + T,
 'area-la-conner': 'Window and Exterior Cleaning in La Conner, WA' + T,
 'area-sedro-woolley': 'Window and Exterior Cleaning in Sedro-Woolley, WA' + T,
 'area-stanwood': 'Window and Exterior Cleaning in Stanwood, WA' + T,
 'gallery': 'Gallery of Recent Jobs' + T,
 'reviews': 'Reviews' + T,
 'about': 'About Us' + T,
 'contact': 'Contact and Free Quote' + T,
}
DESC_OVERRIDE = {
 'contact': 'Request a free quote from Northwest Clear Exteriors. Call or text 360-447-8086, Monday to Saturday, 8:00 AM to 5:00 PM.',
 'reviews': '60+ five-star reviews for window cleaning, roof cleaning and exterior cleaning across Skagit County and Camano Island.',
}

# ---------- pieces of the single file ----------
head = s[:s.find('<body')]
body = s[s.find('<body'):]
css = re.search(r'<style[^>]*>(.*?)</style>', head, re.S).group(1)
home_desc = re.search(r'<meta name="description" content="([^"]*)"', head).group(1)
jsonld = re.search(r'<script type="application/ld\+json">.*?</script>', head, re.S).group(0)
js = max(re.findall(r'<script>(.*?)</script>', body, re.S), key=len)

pages = {}
starts = [(m.group(1), m.start()) for m in re.finditer(r'<div class="page[^"]*" id="([^"]+)">', body)]
foot_at = body.find('<footer')
for k, (pid, st) in enumerate(starts):
    en = starts[k + 1][1] if k + 1 < len(starts) else foot_at
    seg = body[st:en]
    seg = seg[:seg.rfind('</div>') + 6]          # the page div itself
    seg = re.sub(r'<div class="page[^"]*" id="', '<div class="page active" id="', seg, count=1)
    pages[pid] = seg
assert set(pages) == set(URL), set(pages) ^ set(URL)

pre = body[:starts[0][1]]                          # <body> sprite, nav, mobile menu
pre = re.sub(r'\s*<!--[^>]*?-->\s*$', '\n', pre)
post = body[foot_at:body.find('<script>', foot_at)] # footer, fab, lightbox
pre = pre.replace('<body>', '').replace('<nav id="topnav" class="over">', '<nav id="topnav">')

# ---------- link + path rewriting ----------
def links(h):
    h = re.sub(r"""href="#([a-z-]+)" onclick="return go\('([a-z-]+)'\)\"""", lambda m: 'href="%s"' % URL[m.group(2)], h)
    assert 'return go(' not in h, re.findall(r'.{60}return go\(.{40}', h)[:3]
    return h
def paths(h):
    return re.sub(r'(?<=["\' ,(])(img|vid|fonts)/', r'/\1/', h)
pre, post = paths(links(pre)), paths(links(post))
for k in pages: pages[k] = paths(links(pages[k]))

# ---------- CSS ----------
css = paths(css)
css += '''
/* ===== MPA ===== */
/* home hero on phones: taller than the screen, same formula as Kane, Red Line, Clean Sweep and Bullseye */
@media(max-width:880px){.hero{min-height:max(calc(100lvh + 20px),calc(var(--vh,1vh)*100 + 120px))}}
/* TikTok in-app browser: posters only */
html.tt video,html.tt .hero-play,html.tt .clip-ic{display:none!important}
.rv-track.jump{scroll-behavior:auto!important}
/* content already on screen when the page opens shows right away (no reveal wait) */
html.js .ph+section .rv,html.js .ph+section.rv,html.js .trust2+.intro2 .rv{opacity:1;transform:none;transition:none}
'''
open('/tmp/nwc.css', 'w').write(css)
mincss = subprocess.run(['npx', '--yes', 'lightningcss-cli@1.30.1', '--minify', '/tmp/nwc.css'], capture_output=True, text=True)
if mincss.returncode != 0:
    raise SystemExit(mincss.stderr[:2000])
mincss = mincss.stdout

# ---------- JS ----------
def cut(t, a, b):
    i = t.find(a); j = t.find(b, i)
    assert i >= 0 and j > i, (a, b)
    return t[:i], t[j:]

js = paths(js)
# 1. replace the single-page router with per-page state
a, b = cut(js, "const PAGES=[", "/* dropdown */")
core = r'''const URLS=%s;
const $=function(s,r){return (r||document).querySelector(s);};
const $$=function(s,r){return [].slice.call((r||document).querySelectorAll(s));};
const nav=$('#topnav');
const cur=document.body.getAttribute('data-page');
const TT=document.documentElement.classList.contains('tt');
/* old one-page links (/#svc-windows) go to the new page */
if(cur==='home'&&location.hash&&URLS[location.hash.slice(1)])location.replace(URLS[location.hash.slice(1)]);

/* scroll position per page: saved here, restored by the head script on refresh and Back */
const SYK='sy:'+location.pathname;
function saveSy(){try{sessionStorage.setItem(SYK,String(Math.round(window.scrollY)));}catch(e){}}
window.addEventListener('scroll',function(){clearTimeout(saveSy.t);saveSy.t=setTimeout(saveSy,120);},{passive:true});
window.addEventListener('pagehide',saveSy);

function navState(){
 const top=window.scrollY<30;
 nav.classList.toggle('over',cur==='home'&&top&&!$('#mob').classList.contains('open'));
 const fb=$('#fab');if(fb)fb.classList.toggle('show',cur!=='contact'&&window.scrollY>(cur==='home'?window.innerHeight*.75:240));
}
window.addEventListener('scroll',navState,{passive:true});
(function(){
 const inSvc=cur.indexOf('svc-')===0,inArea=cur.indexOf('area-')===0;
 $$('.nav-links [data-nav]').forEach(function(a){const k=a.getAttribute('data-nav');a.classList.toggle('on',k==='services'?inSvc:k==='areas'?inArea:k==='aboutgrp'?(cur==='about'||cur==='reviews'):k===cur);});
 $$('.mob-links [data-m]').forEach(function(a){a.classList.toggle('on',a.getAttribute('data-m')===cur);});
 $('#mobAcc').classList.toggle('on',inSvc);$('#mobAcc2').classList.toggle('on',inArea);
})();
/* a link to the page you are on just goes back to the top */
document.addEventListener('click',function(e){
 const a=e.target.closest&&e.target.closest('a[href^="/"]');if(!a||e.metaKey||e.ctrlKey||e.shiftKey||a.target)return;
 const u=new URL(a.href,location.href);
 if(u.pathname===location.pathname&&!u.hash){e.preventDefault();closeMenu();closeDd();window.scrollTo(0,0);}
});

''' % json.dumps(URL)
js = a + core + b

# 2. menus and the photo viewer close when you come back with Back
js = js.replace("window.addEventListener('pageshow',function(e){if(e.persisted)closeMenu(true);});",
  "window.addEventListener('pageshow',function(e){if(e.persisted){closeMenu(true);closeDd();if($('#lb').classList.contains('open'))closeLb();navState();}});")

# 3. reveal: only the one page exists now
js = js.replace("$$('.page.active .rv:not(.seen)')", "$$('.rv:not(.seen)')")

# 4. hero video: home only, picked before it loads, starts once the page has loaded
a, b = cut(js, "const hv=$('#heroVid')", "/* CLIPS:")
hero = r'''const hv=$('#heroVid'),hp=$('#heroPoster'),hb=$('#heroPlay');
function heroCtl(){
 if(!hv||TT||window.matchMedia('(prefers-reduced-motion:reduce)').matches)return;
 hv.src=window.innerWidth>880?'/vid/hero-d.mp4':'/vid/hero-m.mp4';hv.load();
 const p=hv.play();if(p&&p.catch)p.catch(function(){hb.classList.add('show');});
}
if(hv){
 const ld=function(){hp.classList.add('ld');};
 if(hp.complete&&hp.naturalWidth){hp.classList.add('ld');hp.style.transition='none';}else hp.addEventListener('load',ld);
 hv.addEventListener('playing',function(){hv.classList.add('on');hb.classList.remove('show');});
 hb.addEventListener('click',function(){hv.play().catch(function(){});});
}

'''
js = a + hero + b

# 5. clips: wait 200ms after load, skip in TikTok
js = js.replace("$$('.clip').forEach(initClip);\nfunction clipsPauseAll(){$$('.page:not(.active) .clip video').forEach(function(v){v.pause();});}",
  "function startClips(){if(TT)return;$$('.clip').forEach(initClip);}")
assert 'startClips' in js

# 6. home before/after tabs + reviews: guard for pages that do not have them
js = js.replace("const tabs=$$('#baTabs button'),box=$('#baMain');if(!box)return;", "const tabs=$$('#baTabs button'),box=$('#baMain');if(!box||!tabs.length)return;")
a, b = cut(js, " const tr=$('#rvTrack');", "/* maps:")
reviews = r''' const tr=$('#rvTrack'),all=$('#rvAll');
 /* home: looping carousel. The cards are in the track three times; after a swipe or arrow tap it wraps back to the middle set. */
 if(tr){
  const set=HOME_RV.map(function(i){return card(byI[i]);}).join('');
  const clone=set.replace(/<article class="rc"/g,'<article class="rc" aria-hidden="true"');
  tr.innerHTML=clone+set+clone;
  const n=HOME_RV.length;
  function setW(){return tr.children[n].offsetLeft-tr.children[0].offsetLeft;}
  function jump(x){tr.classList.add('jump');tr.scrollLeft=x;void tr.offsetWidth;tr.classList.remove('jump');}
  function home(){jump(setW());}
  function wrap(){const w=setW();if(tr.scrollLeft<w*.5)jump(tr.scrollLeft+w);else if(tr.scrollLeft>w*1.5)jump(tr.scrollLeft-w);}
  function step(){const c=tr.children[n];return c?c.getBoundingClientRect().width+parseFloat(getComputedStyle(tr).columnGap||18):300;}
  $('#rvPrev').addEventListener('click',function(){tr.scrollBy({left:-step(),behavior:'smooth'});});
  $('#rvNext').addEventListener('click',function(){tr.scrollBy({left:step(),behavior:'smooth'});});
  tr.addEventListener('scroll',function(){clearTimeout(wrap.t);wrap.t=setTimeout(wrap,140);},{passive:true});
  home();window.addEventListener('resize',function(){clearTimeout(home.t);home.t=setTimeout(home,150);});
 }
 /* reviews page: Show more reviews */
 if(all){
  const order=HOME_RV.concat(RV.map(function(r){return r.i;}).filter(function(i){return HOME_RV.indexOf(i)<0;}));
  const STEP=function(){return window.innerWidth<700?4:6;};let shown=0,list=order;
  const more=$('#rvMore');
  function addMore(){const k=STEP(),slice=list.slice(shown,shown+k);all.insertAdjacentHTML('beforeend',slice.map(function(i){return card(byI[i]);}).join(''));shown+=slice.length;more.parentNode.style.display=shown>=list.length?'none':'';}
  function setF(f){list=f==='all'?order:order.filter(function(i){return (byI[i].c||[]).indexOf(f)>=0;});shown=0;all.innerHTML='';addMore();}
  $$('#rvF button').forEach(function(b){b.addEventListener('click',function(){$$('#rvF button').forEach(function(x){x.classList.toggle('on',x===b);x.setAttribute('aria-selected',x===b);});setF(b.getAttribute('data-f'));});});
  addMore();more.addEventListener('click',addMore);
 }
})();

'''
js = a + reviews + b
js = js.replace(" const all=$('#rvAll');\n", "")

# 7. maps, Jobber: load per page, Jobber after load; no warm-up on other pages
js = js.replace("$$('.page.active .map iframe')", "$$('.map iframe')")
a, b = cut(js, "/* start loading the quote form as soon as someone shows intent", "/* gallery filter")
js = a + b
# 8. start
a, b = cut(js, "/* start */", "/* project viewer")
start = r'''/* photos below the first section load as you scroll toward them */
(function(){
 const ims=$$('img[data-src]');if(!ims.length)return;
 function show(im){if(im.dataset.srcset)im.srcset=im.dataset.srcset;im.src=im.dataset.src;im.removeAttribute('data-src');im.removeAttribute('data-srcset');}
 if(!('IntersectionObserver' in window)){ims.forEach(show);return;}
 const lio=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){show(e.target);lio.unobserve(e.target);}});},{rootMargin:'300px 0px'});
 ims.forEach(function(im){lio.observe(im);});
})();
/* start */
navState();observe();loadMaps();
function afterLoad(){heroCtl();setTimeout(startClips,200);if(cur==='contact')loadJobber();}
if(document.readyState==='complete')afterLoad();else window.addEventListener('load',afterLoad);
/* Low Power Mode or blocked autoplay: the first tap anywhere starts the videos */
document.addEventListener('pointerdown',function(){if(hv&&hv.src&&hv.paused)hv.play().catch(function(){});$$('.clip.blocked:not(.paused) video').forEach(function(v){v.play().catch(function(){});});},{once:true,passive:true});

'''
js = a + start + b
assert "/* start */" in js
assert 'showPage' not in js and 'PAGES' not in js and 'TITLES' not in js, [w for w in ['showPage','PAGES','TITLES'] if w in js]

os.makedirs(OUT + '/assets', exist_ok=True)
open(OUT + '/assets/main.src.js', 'w').write(js)
open(OUT + '/assets/style.css', 'w').write(css)
r = subprocess.run(['npx', '--yes', 'terser@5.36.0', OUT + '/assets/main.src.js', '-c', '-m', '-o', OUT + '/assets/main.js'], capture_output=True, text=True)
if r.returncode != 0: raise SystemExit(r.stderr[:3000])

# ---------- head ----------
HEADJS = r'''<script>(function(){var d=document.documentElement;d.className='js';
if(/musical_ly|Bytedance|TikTok|trill_/i.test(navigator.userAgent))d.className+=' tt';
if('scrollRestoration' in history)history.scrollRestoration='manual';
d.style.setProperty('--vh',innerHeight*.01+'px');
addEventListener('orientationchange',function(){setTimeout(function(){d.style.setProperty('--vh',innerHeight*.01+'px');},400);});
var t='';try{t=performance.getEntriesByType('navigation')[0].type;}catch(e){}
if(t==='reload'||t==='back_forward'){try{window.__sy=+sessionStorage.getItem('sy:'+location.pathname)||0;}catch(e){}}})();</script>'''
RESTORE = '<script>if(window.__sy)window.scrollTo(0,window.__sy);</script>'

def lead(pid):
    m = re.search(r'<header class="ph">.*?<p class="lead">(.*?)</p>', pages[pid], re.S)
    return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else ''

def page_head(pid, title, desc, url, extra=''):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
{HEADJS}
<title>{html.escape(title, quote=False)}</title>
<meta name="description" content="{html.escape(desc)}">
<!-- MOCKUP: remove the noindex line and switch BASE to the real domain at launch -->
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{BASE}{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{BASE}{url}">
<meta property="og:image" content="{BASE}/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13284f">
<link rel="icon" type="image/png" sizes="32x32" href="/img/favicon-32.png">
<link rel="apple-touch-icon" href="/img/favicon-180.png">
<link rel="preload" as="image" href="/img/logo-white.webp" fetchpriority="high">
<link rel="preload" as="font" type="font/woff2" href="/fonts/lexend-latin-700-normal.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="/fonts/lexend-latin-400-normal.woff2" crossorigin>
{extra}<script type="speculationrules">{{"prefetch":[{{"where":{{"href_matches":"/*"}},"eagerness":"moderate"}}]}}</script>
<style>/*CSS*/</style>
</head>
'''

LD = paths(jsonld).replace('"image":"/img/og.jpg"', f'"image":"{BASE}/img/og.jpg"').replace('"logo":"/img/logo-black.png"', f'"logo":"{BASE}/img/logo-black.png","url":"{BASE}/"')
HOME_EXTRA = ('<link rel="preload" as="image" href="/vid/hero-d-poster.webp" media="(min-width:881px)" fetchpriority="high">\n'
              '<link rel="preload" as="image" href="/vid/hero-m-poster.webp" media="(max-width:880px)" fetchpriority="high">\n' + LD + '\n')
CONTACT_EXTRA = '<link rel="preconnect" href="https://clienthub.getjobber.com">\n<link rel="dns-prefetch" href="https://cdn.jobber.com">\n'


def page_css(doc_html):
    return doc_html.replace('/*CSS*/', mincss, 1)
    open('/tmp/page.html','w',encoding='utf-8').write(doc_html)
    r=subprocess.run(['node','/home/claude/nwc/purge.mjs','/tmp/nwc.css','/tmp/page.html',OUT+'/assets/main.src.js'],capture_output=True,text=True)
    if r.returncode!=0: raise SystemExit(r.stderr[:2000])
    open('/tmp/pg.css','w').write(r.stdout)
    m=subprocess.run(['npx','--yes','lightningcss-cli@1.30.1','--minify','/tmp/pg.css'],capture_output=True,text=True)
    if m.returncode!=0: raise SystemExit(m.stderr[:2000])
    return doc_html.replace('/*CSS*/', m.stdout, 1)

def page_body(pid, content):
    return (f'<body data-page="{pid}">\n' + pre.strip() + '\n\n' + content + '\n\n' + post.strip() + '\n'
            + RESTORE + f'\n<script src="/assets/main.js?v={VER}" defer></script>\n</body>\n</html>\n')

def lazy(h):
    """Below-the-fold photos load lazily; the page header / hero image loads first with high priority."""
    m=re.search(r'</header>|<div class="hero-content">', h)
    cut_at=m.end() if m else 0
    top, rest = h[:cut_at], h[cut_at:]
    top = re.sub(r'(<div class="ph-bg"><img )(?![^>]*fetchpriority)', r'\1fetchpriority="high" ', top)
    rest = re.sub(r'<img (?![^>]*\bloading=)', '<img loading="lazy" decoding="async" ', rest)
    # past the first section, photos wait for the scroll (main.js swaps data-src in ~600px ahead).
    # Same files, same quality; they just stop competing with the top of the page.
    first_end = rest.find('</section>')
    if first_end > 0:
        a, b = rest[:first_end], rest[first_end:]
        def defer(m):
            tag = m.group(0)
            if 'data-src' in tag or 'src="data:' in tag: return tag
            tag = re.sub(r'\ssrcset="', ' data-srcset="', tag)
            tag = re.sub(r'\ssrc="', ' src="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==" data-src="', tag, count=1)
            return tag
        b = re.sub(r'<img [^>]*loading="lazy"[^>]*>', defer, b)
        rest = a + b
    return top + rest
for k in pages: pages[k] = lazy(pages[k])

for pid, url in URL.items():
    desc = home_desc if pid == 'home' else DESC_OVERRIDE.get(pid) or (lead(pid) + ' Free quotes: 360-447-8086.')
    extra = HOME_EXTRA if pid == 'home' else CONTACT_EXTRA if pid == 'contact' else ''
    content = pages[pid]
    if pid == 'home':
        content = content  # hero markup already in the page
    doc = page_head(pid, TITLE[pid], desc, url, extra) + page_body(pid, content)
    if pid != 'home':
        doc = doc.replace('<nav id="topnav">', '<nav id="topnav">')
    else:
        doc = doc.replace('<nav id="topnav">', '<nav id="topnav" class="over">')
    doc = page_css(doc)
    path = OUT + url + 'index.html'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(doc)

# 404
nf = ('<div class="page active" id="notfound"><header class="ph"><div class="ph-bg"><img src="/img/curved-windows.webp" alt="" width="1600" height="1200"></div>'
      '<div class="in"><h1>Page not found</h1><p class="lead">That page moved or never existed. Try the home page or get a free quote.</p>'
      '<div class="acts"><a class="btn btn-white" href="/">Go to the home page</a></div></div></header></div>')
open(OUT + '/404.html', 'w', encoding='utf-8').write(page_css(page_head('notfound', 'Page not found' + T, 'Page not found.', '/404') + page_body('notfound', nf)))

# deploy files
open(OUT + '/_headers', 'w').write('''/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), microphone=(), geolocation=()

/img/*
  Cache-Control: public, max-age=31536000

/vid/*
  Cache-Control: public, max-age=31536000

/fonts/*
  Cache-Control: public, max-age=31536000, immutable

/assets/*
  Cache-Control: public, max-age=31536000, immutable

/*.html
  Cache-Control: public, max-age=0, must-revalidate

/
  Cache-Control: public, max-age=0, must-revalidate
''')
open(OUT + '/_redirects', 'w').write('/services /services/window-cleaning/ 302\n/services/ /services/window-cleaning/ 302\n')
open(OUT + '/robots.txt', 'w').write('# MOCKUP: change to "Allow: /" and add the sitemap line at launch\nUser-agent: *\nDisallow: /\n')
open(OUT + '/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + ''.join(f'  <url><loc>{BASE}{u}</loc></url>\n' for u in URL.values()) + '</urlset>\n')
print('built', len(URL), 'pages; css', len(mincss), 'js', os.path.getsize(OUT + '/assets/main.js'))
