# Практические работы по тестированию программного обеспечения

Студент: **Воронин**  
Группа: **АЗИС 23-1**

В репозитории собраны пять практических работ: отчёты в формате PDF, исходный код и тесты.

## Состав работ

| № | Тема | Папка | Отчёт |
|---|------|-------|-------|
| 1 | Анализ функциональности ПО. Тестовые условия. Mind map | `PR1/` | [ПР1](PR1/ПР1_Воронин_АЗИС23-1_Анализ_функциональности.pdf) |
| 2 | Техники Black-box, тест-кейсы IEEE 829, статическое рецензирование | `PR2/` | [ПР2](PR2/ПР2_Воронин_АЗИС23-1_Black-box_тест-кейсы_рецензирование.pdf) |
| 3 | Модульное тестирование класса `AuthManager` на pytest | `PR3/` | [ПР3](PR3/ПР3_Воронин_АЗИС23-1_pytest_AuthManager.pdf) |
| 4 | Selenium-проверка расписания сайта api.nntu.ru | `PR4/` | [ПР4](PR4/ПР4_Воронин_АЗИС23-1_Selenium_расписание.pdf) |
| 5 | Нагрузочное тестирование Auction API в Apache JMeter | `PR5/` | [ПР5](PR5/ПР5_Воронин_АЗИС23-1_JMeter_нагрузочное_тестирование.pdf) |

## Краткое содержание

### ПР1. Mind map кофейного автомата
- Приложение на PyQt5: внесение монет, выбор напитка, выдача со сдачей, сброс через 10 секунд.
- Карта ума из 16 тестовых условий — рисунок 6 в отчёте.

### ПР2. Чёрный ящик и рецензирование
- Применены эквивалентное разбиение, анализ граничных значений, таблица решений, таблица переходов и сценарии использования.
- Пять тест-кейсов по IEEE 829.
- 10 дефектов спецификации (4 мажорных) и 5 рекомендаций по ревью кода Приложения А.
- Исправленное приложение: `PR2/vending_machine.py`; автотесты: `PR2/test_vending_machine.py` (23 passed).

### ПР3. pytest и `AuthManager`
- 3 базовых, 3 параметризованных (10 наборов), 2 теста исключений.
- Фикстура SQLite `:memory:`, 4 метки, пропускаемый тест.
- Обязательные тесты SQL-инъекций, запуск с `--maxfail=2`.
- Результат: **17 passed, 1 skipped, 1 xfailed**.

```bash
cd PR3
python -m pytest test_auth_manager.py -v --maxfail=2 --tb=short
python -m pytest test_failure_demo.py -v --maxfail=2 --tb=short   # демонстрация падения
```

### ПР4. Selenium и расписание
- Выбор кафедры и группы АЗИС 23-1, диапазон 01.09.2026–25.12.2026.
- Эталон: `PR4/expected_schedule.json` (85 занятий, 23 даты).
- Позитивный прогон: 3 passed; с подменённым эталоном: 1 failed, 2 passed.

```bash
cd PR4
python -m pytest test_schedule.py -v
set EXPECTED_SCHEDULE=expected_schedule_mutated.json
python -m pytest test_schedule.py -v
```

### ПР5. JMeter и FastAPI
- Сервер аукциона: `PR5/main.py` (FastAPI + SQLite).
- Тестовый план: `PR5/auction_test_plan.jmx` — 5 пользователей, ramp-up 10 с, 1 цикл, POST и GET `/items/`.
- Результат: 10 запросов, 0 ошибок, среднее 19,3 мс, APDEX 1,000.
- Результаты прогона: `PR5/results.jtl`, `PR5/statistics.json`.

```bash
cd PR5
pip install "fastapi[all]" uvicorn
python -m uvicorn main:app --host 127.0.0.1 --port 8000
jmeter -n -t auction_test_plan.jmx -l results.jtl -e -o report
```

## Зависимости

- Python 3.12
- `PyQt5` (ПР1–ПР2), `pytest` (ПР2–ПР4), `selenium` (ПР4), `fastapi`, `uvicorn` (ПР5)
- Microsoft Edge и Selenium Manager (ПР4)
- Apache JMeter 5.6.3 и Java 8+ (ПР5)

## Примечания

- Все пути и данные в тестах соответствуют группе АЗИС 23-1 на момент выполнения работ.
