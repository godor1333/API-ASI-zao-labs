"""ПР4. Selenium-тест расписания группы АЗИС 23-1 на сайте api.nntu.ru.

Тест открывает страницу расписания, выбирает кафедру и группу, задаёт
диапазон дат, разбирает все таблицы расписания и сравнивает результат
с заранее сохранённым эталоном ``expected_schedule.json``.

Запуск (позитивный сценарий):
    pytest test_schedule.py -v

Запуск с подменённым эталоном (негативный сценарий):
    set EXPECTED_SCHEDULE=expected_schedule_mutated.json
    pytest test_schedule.py -v
"""

import json
import os
import re
import time
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait

BASE_URL = "https://api.nntu.ru/raspisanie"
DEPARTMENT_ID = "3"          # Заочная 3 года 10 месяцев
GROUP_ID = "817"             # АЗИС 23-1
GROUP_NAME = "АЗИС 23-1"
DATE_FROM = "2026-09-01"
DATE_TO = "2026-12-25"

HERE = Path(__file__).resolve().parent
SCREENSHOTS = HERE / "screenshots"
EXPECTED = Path(os.environ.get("EXPECTED_SCHEDULE", HERE / "expected_schedule.json"))

MONTHS = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
    "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11,
    "декабря": 12,
}


# ---------------------------------------------------------------------------
# Разбор данных страницы
# ---------------------------------------------------------------------------
def parse_header(text: str):
    """'Понедельник, 7 Сентября 2026' -> '2026-09-07'."""
    match = re.search(r"(\d{1,2})\s+([А-Яа-яЁё]+)\s+(\d{4})", text)
    if not match:
        return None
    day, month, year = int(match.group(1)), match.group(2).lower(), int(match.group(3))
    if month not in MONTHS:
        return None
    return f"{year:04d}-{MONTHS[month]:02d}-{day:02d}"


def normalize_subject(cell: str):
    """'Предмет / Экз.' -> ('Предмет', 'Экз.'); 'Практика /' -> ('Практика', '')."""
    cell = " ".join(cell.split())
    if " / " in cell:
        subject, ptype = cell.rsplit(" / ", 1)
    elif cell.endswith(" /"):
        subject, ptype = cell[:-2], ""
    else:
        subject, ptype = cell, ""
    return subject.strip(" /"), ptype.strip()


def read_schedule(driver):
    """Собирает все занятия со страницы в список словарей."""
    entries = []
    tables = driver.find_elements(By.CSS_SELECTOR, "#printable table.raspTable")
    for table in tables:
        headers = table.find_elements(By.CSS_SELECTOR, "thead h3")
        date = parse_header(headers[0].text) if headers else None
        if date is None:
            continue
        for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
            cells = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
            if not cells or not cells[0]:
                continue
            subject, ptype = normalize_subject(cells[1] if len(cells) > 1 else "")
            entries.append({
                "date": date,
                "para": cells[0].split(" / ")[0].strip(),
                "subject": subject,
                "type": ptype,
                "teacher": cells[2].strip() if len(cells) > 2 else "",
                "room": cells[3].strip() if len(cells) > 3 else "",
            })
    return entries


def entry_key(entry):
    """Ключ занятия: в расписании группы на одну дату приходится одна пара."""
    return (entry["date"], entry["para"])


# ---------------------------------------------------------------------------
# Фикстуры
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,1200")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    browser = webdriver.Edge(options=options)
    yield browser
    browser.quit()


@pytest.fixture(scope="module")
def page_entries(driver):
    """Открывает расписание, выбирает группу и возвращает разобранные занятия."""
    SCREENSHOTS.mkdir(exist_ok=True)
    driver.get(BASE_URL)
    wait = WebDriverWait(driver, 40)

    department = wait.until(
        lambda d: d.find_element(By.ID, "studentAdvert__controls--department")
    )
    wait.until(lambda d: len(department.find_elements(By.TAG_NAME, "option")) > 1)
    Select(department).select_by_value(DEPARTMENT_ID)
    time.sleep(2)

    groups = wait.until(
        lambda d: d.find_element(By.ID, "studentAdvert__controls--groups")
    )
    wait.until(lambda d: len(groups.find_elements(By.TAG_NAME, "option")) > 1)
    Select(groups).select_by_value(GROUP_ID)
    time.sleep(1)

    driver.execute_script(
        """
        const from = document.getElementById('dateBefore');
        const to = document.getElementById('dateAfter');
        if (from) { from.value = arguments[0]; from.dispatchEvent(new Event('change', {bubbles: true})); }
        if (to)   { to.value   = arguments[1]; to.dispatchEvent(new Event('change', {bubbles: true})); }
        """,
        DATE_FROM,
        DATE_TO,
    )
    # Ждём, пока подгрузятся все таблицы расписания.
    wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#printable table.raspTable")) >= 20)
    time.sleep(2)

    driver.save_screenshot(str(SCREENSHOTS / "schedule_page.png"))
    entries = read_schedule(driver)
    assert entries, "На странице не найдено ни одной таблицы с занятиями"
    return entries


# ---------------------------------------------------------------------------
# Тесты
# ---------------------------------------------------------------------------
def test_group_is_selected(driver, page_entries):
    groups = Select(driver.find_element(By.ID, "studentAdvert__controls--groups"))
    assert groups.first_selected_option.text.strip() == GROUP_NAME


def test_schedule_is_not_empty(page_entries):
    dates = {entry["date"] for entry in page_entries}
    assert len(page_entries) >= 50
    assert len(dates) >= 10


def test_schedule_matches_expected(driver, page_entries):
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))["entries"]

    actual_map = {entry_key(e): e for e in page_entries}
    expected_map = {entry_key(e): e for e in expected}

    missing = sorted(set(expected_map) - set(actual_map))
    extra = sorted(set(actual_map) - set(expected_map))
    changed = sorted(
        key for key in set(actual_map) & set(expected_map)
        if actual_map[key] != expected_map[key]
    )

    if missing or extra or changed:
        driver.save_screenshot(str(SCREENSHOTS / "schedule_mismatch.png"))
        details = []
        for key in missing[:5]:
            details.append(f"  НЕТ НА СТРАНИЦЕ: {key}")
        for key in extra[:5]:
            details.append(f"  ЛИШНЕЕ НА СТРАНИЦЕ: {key}")
        for key in changed[:5]:
            details.append(
                f"  ОТЛИЧАЕТСЯ: {key}\n"
                f"      эталон: {expected_map[key]}\n"
                f"      страница: {actual_map[key]}"
            )
        pytest.fail(
            "Расписание не совпало с эталоном "
            f"(нет: {len(missing)}, лишних: {len(extra)}, изменено: {len(changed)})\n"
            + "\n".join(details)
        )

    assert len(actual_map) == len(expected_map)
