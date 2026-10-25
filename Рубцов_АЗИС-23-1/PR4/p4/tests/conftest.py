"""
Общие фикстуры pytest для проверки расписания группы АСИ 23-1
на странице https://api.nntu.ru/raspisanie (АПИ НГТУ).

Переменные окружения:
    RASP_URL  — адрес страницы расписания
                (по умолчанию https://api.nntu.ru/raspisanie;
                 в прогонах практики — http://127.0.0.1:8765/raspisanie, локальное зеркало).
    EXPECTED  — какой эталон использовать: "asi" (по умолчанию, АСИ 23-1)
                или "other" (АСП 23-1 — негативный сценарий "чужой эталон").
    CHROME_BIN / CHROMEDRIVER — пути к бинарникам (необязательно).
"""
import importlib
import os
import shutil

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = os.environ.get("RASP_URL", "https://api.nntu.ru/raspisanie")
GROUP_NAME = "АСИ 23-1"
DEPARTMENT_VALUE = "1"          # «Очная»
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")

# --- локаторы страницы ------------------------------------------------------
SEL_DEPARTMENT = (By.ID, "studentAdvert__controls--department")
SEL_GROUPS = (By.ID, "studentAdvert__controls--groups")
SEL_TYPES = (By.ID, "studentAdvert__controls--types")
WEEK_TYPE = (By.ID, "weekType")
RASP_TABLES = (By.CSS_SELECTOR, "#printable table.raspTable")


def _find_chromedriver():
    p = os.environ.get("CHROMEDRIVER")
    if p:
        return p
    try:
        from chromedriver_py import binary_path
        return binary_path
    except ImportError:
        return shutil.which("chromedriver")


def _find_chrome():
    p = os.environ.get("CHROME_BIN")
    if p:
        return p
    for cand in ("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                 shutil.which("chromium"), shutil.which("chromium-browser"),
                 shutil.which("google-chrome")):
        if cand and os.path.exists(cand):
            return cand
    return None


@pytest.fixture(scope="session")
def expected():
    """Эталонное расписание: expected_schedule (АСИ 23-1) или expected_schedule_other (АСП 23-1)."""
    name = os.environ.get("EXPECTED", "asi").lower()
    mod = "expected_schedule_other" if name == "other" else "expected_schedule"
    return importlib.import_module(mod)


@pytest.fixture(scope="session")
def driver():
    """Headless Chrome 1400x1000 через Selenium 4."""
    opts = webdriver.ChromeOptions()
    chrome = _find_chrome()
    if chrome:
        opts.binary_location = chrome
    for a in ("--headless=new", "--no-sandbox", "--disable-gpu",
              "--window-size=1400,1000", "--lang=ru-RU"):
        opts.add_argument(a)
    service = Service(executable_path=_find_chromedriver())
    drv = webdriver.Chrome(service=service, options=opts)
    drv.set_window_size(1400, 1000)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


def parse_tables(driver):
    """
    Разбирает все таблицы #printable table.raspTable в словарь
    {день: [{'пара','время','дисциплина','преподаватель','ауд','примечание','неделя'}, ...]}.
    В каждой таблице: thead/tr[0]/th/h3 — день недели; tbody/tr — пары,
    столбцы td: Пара («N пара / чч:мм-чч:мм»), Дисциплина, Преподаватель,
    Дист/Ауд, Примечание, Неделя.
    """
    result = {}
    for table in driver.find_elements(*RASP_TABLES):
        day = table.find_element(By.CSS_SELECTOR, "thead th h3").text.strip()
        lessons = []
        for tr in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
            tds = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
            if len(tds) < 6:
                continue
            para_raw = tds[0]
            num, _, time = para_raw.partition(" / ")
            lessons.append({
                "пара": num.strip(),            # «1 пара»
                "время": time.strip(),
                "дисциплина": tds[1],
                "преподаватель": tds[2],
                "ауд": tds[3],
                "примечание": tds[4],
                "неделя": tds[5],
            })
        result[day] = lessons
    return result


def save_full_screenshot(driver, path):
    """Скриншот всей страницы: окно временно растягивается до высоты документа."""
    w, h = 1400, 1000
    try:
        full_h = driver.execute_script("return document.documentElement.scrollHeight")
        driver.set_window_size(w, full_h + 100)
        driver.save_screenshot(path)
    finally:
        driver.set_window_size(w, h)


@pytest.fixture(scope="session")
def schedule_page(driver):
    """
    Открывает страницу, выбирает форму обучения «Очная» и группу АСИ 23-1,
    дожидается таблиц расписания и возвращает разобранное расписание.
    """
    wait = WebDriverWait(driver, 20)
    driver.get(BASE_URL)

    # форма обучения — опции подгружаются JS из /getdepartments
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#studentAdvert__controls--department option[value='%s']" % DEPARTMENT_VALUE)))
    Select(driver.find_element(*SEL_DEPARTMENT)).select_by_value(DEPARTMENT_VALUE)

    # группы — подгружаются из /getgroups
    wait.until(lambda d: len(d.find_element(*SEL_GROUPS).find_elements(By.TAG_NAME, "option")) > 1)
    Select(driver.find_element(*SEL_GROUPS)).select_by_visible_text(GROUP_NAME)

    # расписание — из /getschedule
    wait.until(EC.presence_of_element_located(RASP_TABLES))
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#printable table.raspTable tbody tr")) > 0)

    os.makedirs(OUT_DIR, exist_ok=True)
    save_full_screenshot(driver, os.path.join(OUT_DIR, "selenium_page.png"))

    return parse_tables(driver)
