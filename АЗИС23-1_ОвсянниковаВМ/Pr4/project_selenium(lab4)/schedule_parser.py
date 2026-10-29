
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


class ScheduleParser:

    URL = "https://api.nntu.ru/raspisanie"

    
    SELECT_FORM_ID = "studentAdvert__controls--department"
    SELECT_GROUP_ID = "studentAdvert__controls--groups"
    DATE_BEFORE_ID = "dateBefore"
    DATE_AFTER_ID = "dateAfter"
    TABLE_CSS = "table.raspTable tbody tr"
    WEEK_HEADER_CSS = "h2"
    SPINNER_ID = "ls-spinner"

    # Период по умолчанию 
    DEFAULT_DATE_FROM = "2026-09-07"
    DEFAULT_DATE_TO = "2026-10-18"

  
    def __init__(self, headless: bool = True):
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")

        options.add_experimental_option(
            "excludeSwitches", ["enable-automation"]
        )
        options.add_experimental_option(
            "useAutomationExtension", False
        )

        self.driver = webdriver.Edge(options=options)
        self.wait = WebDriverWait(self.driver, 20)

    
    def open_page(self):
        
        self.driver.get(self.URL)

        # 1. Ждём появления <select>
        self.wait.until(
            EC.presence_of_element_located(
                (By.ID, self.SELECT_FORM_ID)
            )
        )


        self.wait.until(
            lambda d: len(
                Select(
                    d.find_element(By.ID, self.SELECT_FORM_ID)
                ).options
            ) > 1
        )


    def select_form(self, form_name: str = "Заочная 3 года 10 мес"):
        
        
        self.wait.until(
            lambda d: self._option_exists(
                d, self.SELECT_FORM_ID, form_name
            )
        )

        select_element = self.driver.find_element(
            By.ID, self.SELECT_FORM_ID
        )
        select = Select(select_element)

        
        current_text = (
            select.first_selected_option.text
            .replace("\xa0", " ").strip()
        )
        if current_text.lower() == form_name.replace("\xa0", " ").strip().lower():
            return

        
        try:
            select.select_by_visible_text(form_name)
            return
        except Exception:
            pass

        
        target = form_name.replace("\xa0", " ").strip().lower()
        for opt in select.options:
            opt_text = opt.text.replace("\xa0", " ").strip().lower()
            if target in opt_text or opt_text in target:
                select.select_by_visible_text(opt.text)
                return

        
        available = [
            opt.text.replace("\xa0", " ").strip()
            for opt in select.options
        ]
        raise ValueError(
            f"Форма обучения {form_name!r} не найдена!\n"
            f"Доступные опции: {available}"
        )


    def select_group(self, group_name: str = "АЗИС 23-1"):
        
        self.wait.until(
            lambda d: self._option_exists(
                d, self.SELECT_GROUP_ID, group_name
            )
        )

        select_element = self.driver.find_element(
            By.ID, self.SELECT_GROUP_ID
        )
        select = Select(select_element)

        
        current_text = (
            select.first_selected_option.text
            .replace("\xa0", " ").strip()
        )
        if current_text.lower() == group_name.replace("\xa0", " ").strip().lower():
            return

        
        try:
            select.select_by_visible_text(group_name)
            return
        except Exception:
            pass

        
        target = group_name.replace("\xa0", " ").strip().lower()
        for opt in select.options:
            opt_text = opt.text.replace("\xa0", " ").strip().lower()
            if target in opt_text:
                select.select_by_visible_text(opt.text)
                return

        available = [
            opt.text.replace("\xa0", " ").strip()
            for opt in select.options
        ]
        raise ValueError(
            f"Группа {group_name!r} не найдена!\n"
            f"Доступные опции (первые 30): {available[:30]}"
        )


    @staticmethod
    def _option_exists(driver, element_id: str, option_text: str) -> bool:
        try:
            select = Select(
                driver.find_element(By.ID, element_id)
            )
            target = option_text.replace("\xa0", " ").strip().lower()
            for opt in select.options:
                opt_text = (
                    opt.text.replace("\xa0", " ").strip().lower()
                )
                if target == opt_text or target in opt_text:
                    return True
            return False
        except Exception:
            return False


    def set_dates(self, date_from: str, date_to: str):

        self._set_date(self.DATE_BEFORE_ID, date_from)
        self._set_date(self.DATE_AFTER_ID, date_to)


        time.sleep(3)


        try:
            self.wait.until(
                EC.invisibility_of_element_located(
                    (By.ID, self.SPINNER_ID)
                )
            )
        except Exception:
            pass

    def _set_date(self, element_id: str, iso_date: str):

        element = self.wait.until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        self.driver.execute_script(
            """
            const el = arguments[0];
            el.value = arguments[1];
            el.dispatchEvent(new Event('input',  { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            element,
            iso_date,
        )

 
    def get_schedule(self,
                     form: str = "Заочная 3 года 10 мес",
                     group: str = "АЗИС 23-1",
                     date_from: str = DEFAULT_DATE_FROM,
                     date_to: str = DEFAULT_DATE_TO) -> list:
        """
        Получает расписание за указанный период.

        :param form:      форма обучения
        :param group:     группа
        :param date_from: дата "с"  (YYYY-MM-DD)
        :param date_to:   дата "по" (YYYY-MM-DD)
        :return: список строк таблицы (каждая строка — список ячеек)
        """
        self.open_page()
        self.select_form(form)
        self.select_group(group)
        self.set_dates(date_from, date_to)

        
        self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, self.TABLE_CSS)
            )
        )
        
        self.wait.until(
            lambda d: len(
                d.find_elements(By.CSS_SELECTOR, self.TABLE_CSS)
            ) > 0
        )

        
        rows = self.driver.find_elements(
            By.CSS_SELECTOR, self.TABLE_CSS
        )
        schedule = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                schedule.append(
                    [cell.text.strip() for cell in cells]
                )
        return schedule

    def get_week_type(self) -> str:
        """Возвращает тип текущей недели (заголовок <h2>)."""
        try:
            header = self.driver.find_element(
                By.CSS_SELECTOR, self.WEEK_HEADER_CSS
            )
            return header.text.strip()
        except Exception:
            return ""


    def close(self):
        """Закрывает браузер."""
        self.driver.quit()