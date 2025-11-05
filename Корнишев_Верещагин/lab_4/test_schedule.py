import pytest
from schedule_scraper import get_schedule, get_schedule_mock
import re
from datetime import datetime

# =====================================================================
# ОЖИДАЕМОЕ РАСПИСАНИЕ — ПРИМЕР (можно скорректировать)
# =====================================================================
EXPECTED_SCHEDULE = [
    {
        "day": "Среда, 5 Ноября 2025",
        "lessons": [
            "5 пара / 15:30-17:00 Корпоративные информационные системы / Зач.Оц. Гуськова Юлия Александровна 220 Четная",
    "1 пара вечер / 17:30-19:00 Теория цифровой обработки сигналов / Экз. Абаимов Анатолий Вячеславович 220 Четная",
    "2 пара вечер / 19:10-20:40 Теория цифровой обработки сигналов / Экз. Абаимов Анатолий Вячеславович 220 Четная"
        ]
    },
    {
        "day": "Четверг, 6 Ноября 2025",
        "lessons": [
            "1 пара / 08:30-10:00 Инфокоммуникационные системы и сети / КР. Гуськова Юлия Александровна 220 прием КР Четная",
    "2 пара / 10:10-11:40 Инфокоммуникационные системы и сети / Экз. Гуськова Юлия Александровна 220 Четная",
    "3 пара / 12:10-13:40 Основы тестирования программного обеспечения / Экз. Комаров Александр Олегович 324 Четная"
        ]
    },
    {
        "day": "Пятница, 7 Ноября 2025",
        "lessons": [
            "3 пара / 12:10-13:40 производственная (преддипломная практика) заочка / Жидкова Наталья Валерьевна 218 Четная",
    "4 пара / 13:50-15:20 Организационно-экономическое обоснование научных и технических решений / Зач. Гусева Ирина Борисовна 218 Четная",
    "5 пара / 15:30-17:00 Эксплуатация и модификация информационных систем / Экз. Жидкова Наталья Валерьевна 226 Четная"
        ]
    }
]

# === НАСТРОЙКИ ===
EDUCATION_VALUE = "3"
GROUP_VALUE = "804"
START_DATE = "2025-11-03"
END_DATE = "2025-11-09"
DRIVER_PATH = r"E:\webdrivers\chromedriver.exe"


# =====================================================================
# ФИКСТУРА: одно обращение к сайту
# =====================================================================
@pytest.fixture(scope="session")
def real_schedule():
    return get_schedule(
        education_value=EDUCATION_VALUE,
        group_value=GROUP_VALUE,
        start_date=START_DATE,
        end_date=END_DATE,
        driver_path=DRIVER_PATH
    )


# =====================================================================
# ТЕСТ 1: Совпадение с ожидаемым
# =====================================================================
def test_real_matches_expected(real_schedule):
    assert real_schedule == EXPECTED_SCHEDULE, (
        f"\n=== Расписание не совпадает ===\n"
        f"Ожидалось:\n{EXPECTED_SCHEDULE}\n"
        f"Получено:\n{real_schedule}\n"
    )


# =====================================================================
# ТЕСТ 2: Проверка структуры
# =====================================================================
def test_structure(real_schedule):
    assert isinstance(real_schedule, list)
    assert len(real_schedule) > 0
    for item in real_schedule:
        assert isinstance(item, dict)
        assert "day" in item and "lessons" in item
        assert isinstance(item["day"], str)
        assert isinstance(item["lessons"], list)
        assert all(isinstance(l, str) for l in item["lessons"])


# =====================================================================
# ТЕСТ 3: Уникальные дни
# =====================================================================
def test_unique_days(real_schedule):
    days = [item["day"] for item in real_schedule]
    assert len(days) == len(set(days)), f"Дубликаты дней: {days}"


# =====================================================================
# ТЕСТ 4: Нет пустых уроков
# =====================================================================
def test_no_empty_lessons(real_schedule):
    for item in real_schedule:
        assert item["lessons"], f"Пустой день: {item['day']}"
        for lesson in item["lessons"]:
            assert lesson.strip(), f"Пустой урок: '{lesson}'"


# =====================================================================
# ТЕСТ 5: Даты в диапазоне
# =====================================================================
def test_dates_in_range(real_schedule):
    start_dt = datetime.strptime(START_DATE, "%Y-%m-%d")
    end_dt = datetime.strptime(END_DATE, "%Y-%m-%d")

    for item in real_schedule:
        match = re.search(r"(\d{1,2}\s+[а-яА-Я]+\s+\d{4})", item["day"])
        assert match, f"Дата не найдена: {item['day']}"
        day_str = match.group(1)
        # Приводим русские месяцы к английским для datetime
        months = {
            "Января": "January", "Февраля": "February", "Марта": "March",
            "Апреля": "April", "Мая": "May", "Июня": "June",
            "Июля": "July", "Августа": "August", "Сентября": "September",
            "Октября": "October", "Ноября": "November", "Декабря": "December"
        }
        for ru, en in months.items():
            if ru in day_str:
                day_str = day_str.replace(ru, en)
                break
        day_dt = datetime.strptime(day_str, "%d %B %Y")
        assert start_dt <= day_dt <= end_dt, f"Дата вне диапазона: {day_dt.date()}"


# =====================================================================
# ТЕСТ 6: Мок (падает специально)
# =====================================================================
def test_mock_fails():
    mock = get_schedule_mock()
    assert mock == EXPECTED_SCHEDULE, "МОК СОВПАЛ! Тест должен был упасть."


