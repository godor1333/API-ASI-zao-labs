from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import List, Dict
import time
import os


def get_schedule(education_value: str, group_value: str, start_date: str, end_date: str, driver_path: str) -> List[Dict[str, str]]:
    """Парсит расписание ННТУ за указанный диапазон дат."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # включи при запуске на сервере
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://api.nntu.ru/raspisanie")
        wait = WebDriverWait(driver, 20)

        # === 1. ФОРМА ОБУЧЕНИЯ ===
        form_select_elem = wait.until(EC.presence_of_element_located((By.ID, "studentAdvert__controls--department")))
        form_select = Select(form_select_elem)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, f"//select[@id='studentAdvert__controls--department']//option[@value='{education_value}']"))
        )
        form_select.select_by_value(education_value)
        driver.save_screenshot(os.path.join(os.path.dirname(__file__), "1_form_selected.png"))
        print("✅ Форма обучения выбрана")

        # === 2. ЖДЁМ ГРУППЫ ===
        time.sleep(3)
        driver.save_screenshot(os.path.join(os.path.dirname(__file__), "2_groups_loaded.png"))

        # === 3. ГРУППА ===
        group_select_elem = wait.until(EC.presence_of_element_located((By.XPATH, f"//select[.//option[@value='{group_value}']]")))
        group_select = Select(group_select_elem)
        group_select.select_by_value(group_value)
        driver.save_screenshot(os.path.join(os.path.dirname(__file__), "3_group_selected.png"))
        print("✅ Группа выбрана")

        # === 4. ДАТЫ (через JS) ===
        print("⏳ Устанавливаем даты через JavaScript...")
        driver.execute_script(f"document.getElementsByName('dateBefore')[0].value = '{start_date}';")
        driver.execute_script(f"document.getElementsByName('dateAfter')[0].value = '{end_date}';")
        driver.execute_script("document.getElementsByName('dateBefore')[0].dispatchEvent(new Event('change'));")
        driver.execute_script("document.getElementsByName('dateAfter')[0].dispatchEvent(new Event('change'));")

        time.sleep(2)
        driver.save_screenshot(os.path.join(os.path.dirname(__file__), "4_dates_filled_js.png"))
        print(f"✅ Даты установлены: {start_date} — {end_date}")

        # === 5. ОЖИДАНИЕ РАСПИСАНИЯ ===
        print("⏳ Ожидаем расписание...")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.raspTable")))
        time.sleep(2)
        driver.save_screenshot(os.path.join(os.path.dirname(__file__), "5_schedule_loaded.png"))
        print("✅ Расписание загружено")

        # === 6. ПАРСИНГ ТАБЛИЦ ===
        print("📄 Парсим таблицы...")
        tables = driver.find_elements(By.CSS_SELECTOR, "table.raspTable")
        schedule = []

        for table in tables:
            # День недели и дата
            header_elem = table.find_element(By.TAG_NAME, "h3")
            day_name = header_elem.text.strip()

            # Строки расписания
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            lessons = []

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 6:
                    pair = cells[0].text.strip()
                    subject = cells[1].text.strip()
                    teacher = cells[2].text.strip()
                    classroom = cells[3].text.strip()
                    note = cells[4].text.strip()
                    week = cells[5].text.strip()

                    # Склеиваем в одну строку
                    lesson_text = f"{pair} {subject} {teacher} {classroom}"
                    if note:
                        lesson_text += f" {note}"
                    if week:
                        lesson_text += f" {week}"

                    lessons.append(lesson_text)

            if lessons:
                schedule.append({"day": day_name, "lessons": lessons})

        print(f"✅ Спарсено {len(schedule)} дней!")
        return schedule

    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        error_path = os.path.join(os.path.dirname(__file__), "ERROR.png")
        driver.save_screenshot(error_path)
        print(f"Скриншот ошибки: {error_path}")
        return []

    finally:
        driver.quit()


def get_schedule_mock() -> List[Dict[str, str]]:
    """Мок для тестов."""
    return [{"day": "Понедельник", "lessons": ["Другой предмет", "Ещё один"]}]


if __name__ == "__main__":
    result = get_schedule(
        education_value="3",
        group_value="804",
        start_date="2025-11-03",
        end_date="2025-11-09",
        driver_path=r"E:\webdrivers\chromedriver.exe"
    )
    print("\n=== ТВОЁ РАСПИСАНИЕ ===")
    for item in result:
        print(f"{item['day']}:")
        for lesson in item["lessons"]:
            print("   ", lesson)
