#!/usr/bin/env python3
"""
Локальное зеркало страницы https://api.nntu.ru/raspisanie (АПИ НГТУ).

Отдаёт точную копию DOM реальной страницы (page_raw.html) с переписанными
ссылками на локальные ресурсы и эмулирует три конечные точки API сайта:
    GET  /getdepartments  -> api.json["deps"]
    POST /getgroups       -> api.json["groups"]
    POST /getschedule     -> data/schedule_current.json (подменяемый файл)

Запуск:  python3 server.py  [--port 8765]
"""
import argparse
import base64
import json
import os
import re
import sys

from flask import Flask, Response, abort, request

HERE = os.path.dirname(os.path.abspath(__file__))
CSS_DIR = os.path.join(HERE, "css")
DATA_DIR = os.path.join(HERE, "data")
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedule_current.json")
SCHEDULE_ORIG = os.path.join(DATA_DIR, "schedule_original.json")

with open(os.path.join(HERE, "api.json"), encoding="utf-8") as f:
    API = json.load(f)

# --- подготовка data/: расписание читается из отдельного файла ------------
os.makedirs(DATA_DIR, exist_ok=True)
_sched_obj = json.loads(API["sched"]) if isinstance(API["sched"], str) else API["sched"]
if not os.path.exists(SCHEDULE_ORIG):
    with open(SCHEDULE_ORIG, "w", encoding="utf-8") as f:
        json.dump(_sched_obj, f, ensure_ascii=False, indent=1)
if not os.path.exists(SCHEDULE_FILE):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(_sched_obj, f, ensure_ascii=False, indent=1)

# логотип: data URL из api.json -> байты PNG
_logo_b64 = API["logo"].split(",", 1)[1]
LOGO_PNG = base64.b64decode(_logo_b64)

app = Flask(__name__)


# --- переписывание HTML -----------------------------------------------------
def build_page() -> str:
    with open(os.path.join(HERE, "page_raw.html"), encoding="utf-8") as f:
        html = f.read()

    # 1. Сторонние скрипты (метрика, analytics, gtag, recaptcha) — удалить.
    html = re.sub(
        r'<script[^>]*src="https?://(mc\.yandex\.ru|www\.google-analytics\.com|'
        r'www\.googletagmanager\.com|www\.gstatic\.com|www\.google\.com)[^"]*"[^>]*>\s*</script>',
        "", html)
    # inline-скрипты счётчиков и gtag
    html = re.sub(r'<script[^>]*>\s*\(function \(d, w, c\).*?</script>', "", html, flags=re.S)
    html = re.sub(r'<script[^>]*>\s*\(function\(m,e,t,r,i,k,a\).*?</script>', "", html, flags=re.S)
    html = re.sub(r'<script>\s*window\.dataLayer.*?</script>', "", html, flags=re.S)
    html = re.sub(r'<script>\s*\$\(document\)\.ready.*?</script>', "", html, flags=re.S)
    # html2canvas (если присутствует)
    html = re.sub(r'<script[^>]*html2canvas[^>]*>\s*</script>', "", html)

    # 2. Дублирующая загрузка vanilla_raspisanie.js через document.write — убрать,
    #    оставить один статический тег -> /js/vanilla_raspisanie.js
    html = re.sub(r'<script>document\.write\(.*?</script>', "", html, flags=re.S)
    html = re.sub(r'<script[^>]*src="/frontend/web/js/vanilla_raspisanie\.js[^"]*"[^>]*>',
                  '<script type="text/javascript" src="/js/vanilla_raspisanie.js">', html)
    html = re.sub(r'<script src = "/frontend/web/js/vanilla_raspisanie\.js[^"]*">', "", html)

    # 3. CSS: /frontend/web/css/.../name.css?ver -> /css/name.css
    def _css(m):
        return '<link href="/css/%s" rel="stylesheet">' % os.path.basename(m.group(1))
    html = re.sub(r'<link href="/frontend/web/css/([^"?]+)(\?[^"]*)?" rel="stylesheet">', _css, html)

    # 4. Абсолютные ссылки на сайт -> локальные
    html = html.replace("https://api.nntu.ru/frontend/", "/frontend/")

    # 5. Сброс состояния DOM (снимок был сделан ПОСЛЕ выбора группы):
    #    - селект формы обучения: пустой, опции подставит JS из /getdepartments
    html = re.sub(
        r'(<select id="studentAdvert__controls--department"[^>]*>).*?</select>',
        r'\1</select>', html, flags=re.S)
    #    - селект групп: только заглушка
    html = re.sub(
        r'(<select id="studentAdvert__controls--groups"[^>]*>).*?</select>',
        r'\1<option value="null" selected>Выберите группу</option></select>', html, flags=re.S)
    #    - блок типа расписания скрыт до выбора группы
    html = re.sub(
        r'(<div id="studentAdvert__controls--types__box" class="advert__box mt-3" style=")display: block;',
        r'\1display: none;', html)
    #    - спиннеры "Пожалуйста, подождите..." в исходном HTML отсутствуют
    #      (их вставляет JS), в снимке DOM они остались -> удалить
    html = re.sub(r'<div class="lds-spinner" id="\w+" style="display: none;">.*?<h2>Пожалуйста, подождите\.\.\.</h2></div>',
                  "", html)
    #    - контейнер расписания пуст
    html = re.sub(r'(<div id="printable"[^>]*>).*?</div>(\s*</div>)', r'\1</div>\2', html, flags=re.S)
    return html


PAGE_HTML = None


@app.route("/raspisanie")
@app.route("/")
def raspisanie():
    global PAGE_HTML
    if PAGE_HTML is None or app.debug:
        PAGE_HTML = build_page()
    return Response(PAGE_HTML, mimetype="text/html; charset=utf-8")


# --- API ------------------------------------------------------------------
@app.route("/getdepartments", methods=["GET", "POST"])
def getdepartments():
    return Response(_as_json(API["deps"]), mimetype="application/json")


@app.route("/getgroups", methods=["POST"])
def getgroups():
    return Response(_as_json(API["groups"]), mimetype="application/json")


@app.route("/getschedule", methods=["POST"])
def getschedule():
    # оригинал отвечает расписанием только для АСИ 23-1 (group_id=810, type=1)
    with open(SCHEDULE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return Response(json.dumps(data, ensure_ascii=False), mimetype="application/json")


def _as_json(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


# --- статика ---------------------------------------------------------------
@app.route("/css/<path:name>")
@app.route("/frontend/web/css/<path:name>")
def css(name):
    p = os.path.join(CSS_DIR, os.path.basename(name))
    if not os.path.exists(p):
        abort(404)
    with open(p, "rb") as f:
        return Response(f.read(), mimetype="text/css")


@app.route("/js/vanilla_raspisanie.js")
def rasp_js():
    with open(os.path.join(HERE, "vanilla_raspisanie.js"), "rb") as f:
        return Response(f.read(), mimetype="application/javascript")


@app.route("/frontend/web/js/<path:name>")
def other_js(name):
    # vendor.js, script.js, select2 и т.п. локально отсутствуют — пустой JS
    return Response("/* stub: %s */\n" % name, mimetype="application/javascript")


@app.route("/frontend/web/ngtu/files/API_logo_full_white.png")
@app.route("/frontend/web/ngtu/files/General/API_logo_white_short.png")
def logo():
    return Response(LOGO_PNG, mimetype="image/png")


@app.route("/frontend/web/<path:rest>")
def missing_asset(rest):
    abort(404)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()
    print("mirror: http://%s:%d/raspisanie  (schedule file: %s)" % (args.host, args.port, SCHEDULE_FILE),
          file=sys.stderr)
    app.run(host=args.host, port=args.port, debug=False, threaded=True)
