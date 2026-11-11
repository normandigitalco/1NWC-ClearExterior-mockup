"""Go-live switch. Run once, on launch day:   python3 launch.py https://www.example.com
- removes the noindex line from every page
- swaps the mockup address for the real domain in canonical, og tags, schema and sitemap.xml
- opens robots.txt to search engines and points it at the sitemap
Nothing else changes. Commit and push afterwards."""
import sys,glob,re
if len(sys.argv)!=2 or not sys.argv[1].startswith("https://"): sys.exit("usage: python3 launch.py https://www.yourdomain.com")
NEW=sys.argv[1].rstrip("/");OLD="https://1nwc-clearexterior-mockup.pages.dev"
for f in glob.glob("**/*.html",recursive=True)+["sitemap.xml"]:
    s=open(f,encoding="utf-8").read()
    s=s.replace(OLD,NEW)
    s=re.sub(r'<!-- MOCKUP:[^>]*-->\n?','',s)
    s=re.sub(r'<meta name="robots" content="noindex, nofollow">\n?','',s)
    open(f,"w",encoding="utf-8").write(s)
open("robots.txt","w").write(f"User-agent: *\nAllow: /\n\nSitemap: {NEW}/sitemap.xml\n")
print("Live settings applied for",NEW)
