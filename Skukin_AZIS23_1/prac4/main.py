import time
import pytest

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class Lesson:
    position: int
    start: str
    end: str
    subject: str
    lesson_type: str
    lecturer: str
    auditorium: int
    comment: str
    is_even_week: bool

@dataclass
class Schedule:
    date: str
    day_of_week: str
    lessons: list

def parse_lesson_from_shedule(position, subject, lecturer, auditorium, comment, week):
    number, interval = position.split(' / ')

    number = int(number.split(' ')[0])
    number += 5 if position.find('вечер') >= 0 else 0

    start, end = interval.split('-')

    name, type = subject.split(' / ')
    type = type.replace('.', '')

    auditorium = int(auditorium)
    
    is_even = True if week.find('Четная') >= 0 else False

    return Lesson(number, start, end, name, type, lecturer, auditorium, comment, is_even)

def get_schedule_from_nntu(driver, form, group, before, after):
    VISIBILITY_TIMEOUT = 30
    schedule = []

    driver.get('https://api.nntu.ru/raspisanie')

    form_selector = WebDriverWait(driver, VISIBILITY_TIMEOUT).until(
        EC.visibility_of_element_located(
            ('xpath', '//*[@id="studentAdvert__controls--department"]')))
    form_element = Select(form_selector)
    form_element.select_by_visible_text(form)

    group_selector = WebDriverWait(driver, VISIBILITY_TIMEOUT).until(
        EC.visibility_of_element_located(
            ('xpath', '//*[@id="studentAdvert__controls--groups"]')))
    group_element = Select(group_selector)
    group_element.select_by_visible_text(group)

    date_before = driver.find_element('xpath', '//*[@id="dateBefore"]')
    date_after = driver.find_element('xpath', '//*[@id="dateAfter"]')

    time.sleep(1)
    date_before.send_keys(before)
    time.sleep(1)
    date_after.send_keys(after)
    time.sleep(1)

    table = WebDriverWait(driver, VISIBILITY_TIMEOUT).until(
        EC.visibility_of_element_located(('xpath', '//*[@id="printable"]')))
    table_elements = table.find_elements('xpath', './table')

    for element in table_elements:
        head = element.find_element('xpath', './thead')
        body = element.find_element('xpath', './tbody')

        schedule_day = head.find_element('xpath', './tr[1]/th/h3').text
        schedule_table = body.find_elements('xpath', './tr')

        lessons_list = []
        for schedule_row in schedule_table:
            lesson_elements = schedule_row.find_elements('xpath', './td')
            lesson_params = (element.text for element in lesson_elements)

            lessons_list.append(parse_lesson_from_shedule(*lesson_params))

        schedule_day_of_week = schedule_day.split(', ')[0]
        schedule_date = schedule_day.split(', ')[1]
        schedule.append(Schedule(schedule_date, schedule_day_of_week, lessons_list))

    return schedule

@pytest.fixture
def test_webdriver():
    driver = webdriver.Firefox()
    yield driver
    driver.quit()

def test_identical_schedule(test_webdriver):
    schedule = get_schedule_from_nntu(test_webdriver, 'Заочная 3 года 10 мес', 'АЗИС 23-1', '2026-09-07', '2026-09-25')
    my_schedule = deepcopy(schedule)

    print("")
    print("== Schedule from API.NNTU ==")
    print(schedule[0])
    print("")
    print("== My schedule ==")
    print(my_schedule[0])
    print("")

    assert schedule == my_schedule

def test_different_schedule(test_webdriver):
    schedule = get_schedule_from_nntu(test_webdriver, 'Заочная 3 года 10 мес', 'АЗИС 23-1', '2026-09-07', '2026-09-25')
    my_schedule = deepcopy(schedule)

    my_schedule[0].lessons[0].position = 0
    my_schedule[0].lessons[0].start = '7:00'
    my_schedule[0].lessons[0].end = '8:30'
    my_schedule[0].lessons[0].subject = 'Завтрак'
    my_schedule[0].lessons[0].lesson_type = 'Пз'
    my_schedule[0].lessons[0].lecturer = 'Хорошее настроение'
    my_schedule[0].lessons[0].auditorium = -1
    my_schedule[0].lessons[0].comment = 'Поспать бы еще!'
    my_schedule[0].lessons[0].is_even_week = False

    print("")
    print("== Schedule from API.NNTU ==")
    print(schedule[0].lessons[0])
    print("")
    print("== My schedule ==")
    print(my_schedule[0].lessons[0])
    print("")

    assert schedule == my_schedule
