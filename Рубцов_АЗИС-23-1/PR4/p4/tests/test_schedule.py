"""
Практика 4. Проверка расписания группы АСИ 23-1 на сайте АПИ НГТУ
(https://api.nntu.ru/raspisanie) средствами pytest + Selenium.

Страница открывается в headless Chrome, через селекты выбираются
форма обучения «Очная» и группа «АСИ 23-1», затем таблицы .raspTable
разбираются и сравниваются с заранее выбранным эталонным расписанием
(tests/expected_schedule.py). Если расписание на сайте изменится
или эталон будет подменён, тесты падают.
"""
import importlib
import os

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from conftest import BASE_URL, GROUP_NAME, SEL_GROUPS, WEEK_TYPE

# эталон нужен уже на этапе сбора тестов (параметризация), поэтому импортируем здесь
_EXPECTED_NAME = os.environ.get("EXPECTED", "asi").lower()
EXP = importlib.import_module("expected_schedule_other" if _EXPECTED_NAME == "other" else "expected_schedule")


def _lesson_id(param):
    return param if isinstance(param, str) else "пара%d" % (param + 1)


def test_page_title_and_week(driver, schedule_page):
    """Заголовок страницы — «Расписание», #weekType сообщает чётность недели."""
    assert driver.title.strip() == "Расписание", "Открыта не страница расписания: %s (%s)" % (driver.title, BASE_URL)
    week = driver.find_element(*WEEK_TYPE).text.strip()
    assert "Текущая неделя является" in week, "Неожиданный текст #weekType: %r" % week
    assert week.endswith(("четной", "нечетной")), "В #weekType не указана чётность недели: %r" % week


def test_group_present_in_list(driver, schedule_page):
    """В списке групп очной формы есть группа АСИ 23-1, и именно она выбрана."""
    select = Select(driver.find_element(*SEL_GROUPS))
    names = [o.text.strip() for o in select.options]
    assert GROUP_NAME in names, "Группы %s нет в списке: %s" % (GROUP_NAME, names)
    assert select.first_selected_option.text.strip() == GROUP_NAME


def test_days_match(schedule_page):
    """Набор дней недели с занятиями совпадает с эталоном."""
    assert set(schedule_page) == set(EXP.SCHEDULE), (
        "Дни на сайте: %s; в эталоне: %s" % (sorted(schedule_page), sorted(EXP.SCHEDULE)))


@pytest.mark.parametrize("day", list(EXP.SCHEDULE))
def test_lessons_count_per_day(schedule_page, day):
    """Число пар в каждый день совпадает с эталоном."""
    assert day in schedule_page, "На сайте нет таблицы за %s" % day
    got = [(l["пара"], l["дисциплина"]) for l in schedule_page[day]]
    exp = [(l["пара"], l["дисциплина"]) for l in EXP.SCHEDULE[day]]
    assert len(got) == len(exp), "%s: на сайте %d пар %s, в эталоне %d %s" % (day, len(got), got, len(exp), exp)


@pytest.mark.parametrize("day,idx", EXP.LESSON_IDS, ids=_lesson_id)
def test_lesson_matches_expected(schedule_page, day, idx):
    """Пара (день, №) совпадает с эталоном: номер, дисциплина, преподаватель, аудитория."""
    expected = EXP.SCHEDULE[day][idx]
    assert day in schedule_page, "На сайте нет таблицы за %s" % day
    lessons = schedule_page[day]
    assert idx < len(lessons), "%s: на сайте только %d пар, эталонной %s нет" % (day, len(lessons), expected["пара"])
    actual = lessons[idx]
    keys = ("пара", "дисциплина", "преподаватель", "ауд")
    assert {k: actual[k] for k in keys} == {k: expected[k] for k in keys}, (
        "%s, %s: сайт %s != эталон %s" % (day, expected["пара"], actual, expected))


def test_testing_course_on_friday(schedule_page):
    """В пятницу 3-я и 4-я пары — «Основы тестирования программного обеспечения», Комаров А.О., ауд. 324."""
    assert "Пятница" in schedule_page, "Нет таблицы за пятницу"
    friday = {l["пара"]: l for l in schedule_page["Пятница"]}
    for num in ("3 пара", "4 пара"):
        assert num in friday, "В пятницу нет %s: %s" % (num, sorted(friday))
        lesson = friday[num]
        assert lesson["дисциплина"] == "Основы тестирования программного обеспечения / Лк.", lesson
        assert lesson["преподаватель"] == "Комаров Александр Олегович", lesson
        assert lesson["ауд"] == "324", lesson


def test_no_lessons_on_monday_and_saturday(schedule_page):
    """В понедельник и субботу занятий нет — таблиц за эти дни на странице нет."""
    for day in ("Понедельник", "Суббота"):
        assert day not in schedule_page, "%s: на сайте есть %d пар: %s" % (
            day, len(schedule_page.get(day, [])), schedule_page.get(day))
