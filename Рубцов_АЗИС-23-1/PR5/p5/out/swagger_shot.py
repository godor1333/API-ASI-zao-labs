# Скриншот Swagger UI (/docs). CDN cdn.jsdelivr.net недоступен в сети окружения,
# поэтому запросы к CDN перехватываются и отдаются из локальной копии swagger-ui-dist 5.17.14 (npm).
import os, sys
from playwright.sync_api import sync_playwright

local = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swui')  # swagger-ui-dist 5.17.14 из registry.npmjs.org
exe = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

def route(r):
    url = r.request.url
    name = url.split("/")[-1]
    p = os.path.join(local, name)
    if os.path.exists(p):
        ct = "application/javascript" if name.endswith(".js") else "text/css" if name.endswith(".css") else "application/octet-stream"
        r.fulfill(path=p, content_type=ct)
    else:
        r.abort()

with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=exe, args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.route("**/cdn.jsdelivr.net/**", route)
    pg.goto("http://127.0.0.1:8000/docs", wait_until="load")
    pg.wait_for_timeout(4000); print("opblocks:", pg.locator(".opblock").count())
    pg.wait_for_timeout(800)
    pg.screenshot(path=sys.argv[1])
    b.close()
print("ok")
