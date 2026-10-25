# Практика 4 — проверка расписания группы АСИ 23-1 (pytest + Selenium)

Объект: страница расписания АПИ НГТУ (Арзамасский политехнический институт, филиал НГТУ)
https://api.nntu.ru/raspisanie, группа **АСИ 23-1**, форма обучения «Очная», расписание «Основное».

## Окружение

| Компонент | Версия |
|---|---|
| Python | 3.11.15 |
| pytest | 9.1.1 |
| selenium | 4.49.0 |
| Chromium (браузер) | 141.0.7390.37 (`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, сборка Playwright) |
| ChromeDriver | 141.0.7390.54 (пакет PyPI `chromedriver-py==141.0.7390.54`; системный `/opt/node22/bin/chromedriver` 147.0.7727.24 несовместим с Chromium 141 — «This version of ChromeDriver only supports Chrome version 147») |
| Flask (сервер зеркала) | 3.1.3 |
| Playwright (только для контрольного скриншота зеркала) | chromium-1194 |

Драйвер подключается через `webdriver.Chrome(service=Service(executable_path=chromedriver_py.binary_path), options=...)`;
опции: `--headless=new --no-sandbox --disable-gpu --window-size=1400,1000 --lang=ru-RU`.

## Схема работы: реальный сайт -> локальное зеркало

Из среды выполнения тестов нет сетевого доступа к api.nntu.ru. Поэтому тесты запускались против
локального зеркала, собранного из **точной копии реальной страницы**, снятой в обычном браузере:

```
реальный сайт                          локальное зеркало (mirror/server.py, порт 8765)
GET  /raspisanie      --> page_raw.html   (полный DOM реальной страницы; переписаны ссылки)
GET  /getdepartments  --> api.json.deps   (реальный ответ API)
POST /getgroups       --> api.json.groups (реальный ответ API, 38 групп 1–5 курсов)
POST /getschedule     --> data/schedule_current.json (реальный ответ для group_id=810, type=1;
                                                      ОТДЕЛЬНЫЙ файл — его подменяет swap_schedule.py)
/frontend/web/css/*   --> mirror/css/*    (оригинальные стили сайта)
/frontend/web/js/vanilla_raspisanie.js --> оригинальный JS сайта (без изменений)
/frontend/web/ngtu/files/API_logo_full_white.png --> PNG логотипа из api.json.logo
```

Что делает `server.py` с HTML: удаляет сторонние скрипты (Яндекс.Метрика, Google Analytics/gtag,
reCAPTCHA) и их inline-инициализацию; убирает дублирующую загрузку `vanilla_raspisanie.js` через
`document.write`; переписывает `<link href="/frontend/web/css/...">` на `/css/<имя>`; отдаёт пустой JS
вместо отсутствующих локально `vendor.js`, `script.js`, select2 и т.п.; возвращает DOM в исходное состояние
(снимок был сделан после выбора группы: очищены селекты, `#printable`, удалены JS-вставленные спиннеры,
скрыт блок «Расписание»). Логика подгрузки формы обучения -> групп -> расписания выполняется
**оригинальным** JS сайта (XMLHttpRequest на те же URL).

Проверка зеркала (headless Chromium, Playwright): после выбора «Очная» в селект групп приходит 38 опций;
после выбора «АСИ 23-1» JS сам выставляет тип «Основное» и выводит 4 таблицы `.raspTable`
(Вторник, Среда, Четверг, Пятница); `#weekType` = «Текущая неделя является четной»; `<title>` = «Расписание».
Скриншот зеркала `out/mirror_page.png` совпадает по структуре и содержимому с рендером реального сайта
`site_shots/asi23_v3.png` (отличия: веб-шрифты Open Sans/themify не загружаются без сети — системный
sans-serif и отсутствие иконок «поиск»/«версия для слабовидящих»).

## Локаторы

| Элемент | Локатор | Примечание |
|---|---|---|
| Форма обучения | `#studentAdvert__controls--department` (`<select>`) | опции подгружаются JS; «Очная» = `value="1"` (в API — «Дневное», JS переименовывает) |
| Группа | `#studentAdvert__controls--groups` (`<select>`, `<optgroup label="N Курс">`) | «АСИ 23-1» = `value="810"` |
| Тип расписания | `#studentAdvert__controls--types` | выставляется JS автоматически в «Основное» (`value=1`) |
| Чётность недели | `#weekType` (`<h2>`) | текст «Текущая неделя является четной/нечетной», вычисляется JS от 31 августа |
| Таблицы расписания | `#printable table.raspTable` | одна таблица на день |
| День недели | `table.raspTable thead th h3` | «Вторник», «Среда», … |
| Строка пары | `table.raspTable tbody tr` | 6 `td`: Пара («1 пара / 08:30-10:00»), Дисциплина («… / Лк.»), Преподаватель, Дист/Ауд, Примечание, Неделя («Всегда»/«Четная»/«Нечетная») |

Ожидания реализованы через `WebDriverWait` (20 с): появление `option[value='1']` в селекте формы,
>1 опции в селекте групп, появление `#printable table.raspTable` и строк `tbody tr`.

## Структура тестов (`tests/`)

| Файл | Назначение |
|---|---|
| `conftest.py` | фикстуры `driver` (headless Chrome 1400x1000), `schedule_page` (открывает `RASP_URL`, выбирает «Очная» и «АСИ 23-1», ждёт таблицы, сохраняет `out/selenium_page.png`, возвращает `{день: [пары]}`), `expected`; функция `parse_tables()` |
| `expected_schedule.py` | ЭТАЛОН — заранее выбранное расписание АСИ 23-1 (16 пар, 4 дня), составлено по реальному ответу `/getschedule` |
| `expected_schedule_other.py` | «чужой» эталон — расписание АСП 23-1 (18 пар, 5 дней) для негативного сценария `EXPECTED=other` |
| `test_schedule.py` | тесты (ниже) |

| Тест | Что проверяет | Кол-во |
|---|---|---|
| `test_page_title_and_week` | `<title>` == «Расписание»; `#weekType` содержит «Текущая неделя является» и оканчивается на «четной»/«нечетной» | 1 |
| `test_group_present_in_list` | в списке групп есть «АСИ 23-1» и она выбрана | 1 |
| `test_days_match` | множество дней с занятиями == дни эталона | 1 |
| `test_lessons_count_per_day[день]` | число пар в каждый день эталона | 4 (АСИ) / 5 (АСП) |
| `test_lesson_matches_expected[день-параN]` | номер пары, дисциплина, преподаватель, аудитория == эталон | 16 (АСИ) / 18 (АСП) |
| `test_testing_course_on_friday` | пятница, 3 и 4 пара — «Основы тестирования программного обеспечения / Лк.», Комаров Александр Олегович, ауд. 324 | 1 |
| `test_no_lessons_on_monday_and_saturday` | таблиц за понедельник и субботу нет | 1 |

Итого 25 тестов с эталоном АСИ 23-1, 28 — с эталоном АСП 23-1.

Переменные окружения: `RASP_URL` (по умолчанию `https://api.nntu.ru/raspisanie`; в прогонах —
`http://127.0.0.1:8765/raspisanie`), `EXPECTED=asi|other`, опционально `CHROME_BIN`, `CHROMEDRIVER`.

## Результаты прогонов

Команда: `RASP_URL=http://127.0.0.1:8765/raspisanie python3 -m pytest tests -v --tb=short`

| № | Прогон | Условия | Результат | Файлы |
|---|---|---|---|---|
| 1 | Позитивный | оригинальное расписание, эталон АСИ 23-1 | **25 passed**, 0 failed (3.46 s) | `out/run_ok.txt`, `out/run_ok.png` |
| 2 | Негативный «расписание на сайте изменилось» | `python3 mirror/swap_schedule.py`, эталон АСИ 23-1 | **7 failed, 18 passed** (2.98 s) | `out/run_fail_site_changed.txt/.png` |
| 3 | Негативный «подменён эталон» | `EXPECTED=other` (эталон АСП 23-1), расписание оригинальное | **22 failed, 6 passed** (3.17 s) | `out/run_fail_other_expected.txt/.png` |
| 4 | Контроль после `swap_schedule.py --restore` | как № 1 | **25 passed** (3.07 s) | `out/run_ok_after_restore.txt/.png` |

### Прогон 2 — что подменялось в `data/schedule_current.json`

1. Пятница, 3 и 4 пара «Основы тестирования программного обеспечения / Лк.»: преподаватель
   Комаров Александр Олегович -> Иванов Иван Иванович, аудитория 324 -> 218.
2. Добавлен понедельник: 1 пара «Физическая культура / Пз.», Петров Пётр Петрович, с/з.
3. Вторник: удалена 4 пара («Управление ИТ-проектами / Лк.»).

Упавшие тесты: `test_days_match` (лишний «Понедельник»), `test_lessons_count_per_day[Вторник]` (3 != 4),
`test_lesson_matches_expected[Вторник-пара4]` (пары нет), `[Пятница-пара3]`, `[Пятница-пара4]`
(diff: `{'ауд': '218'} != {'ауд': '324'}`, `{'преподаватель': 'Иванов Иван Иванович'} != {'преподаватель': 'Комаров Александр Олегович'}`),
`test_testing_course_on_friday`, `test_no_lessons_on_monday_and_saturday`. Незатронутые дни (Среда, Четверг,
пары 1–3 вторника, 1–2 пятницы) остались зелёными. `swap_schedule.py --restore` копирует
`data/schedule_original.json` обратно в `schedule_current.json`.

### Прогон 3 — подмена эталона

Страница показывает АСИ 23-1, эталон — АСП 23-1. Прошли только тесты, не зависящие от эталона:
`test_page_title_and_week`, `test_group_present_in_list`, `test_testing_course_on_friday`,
`test_no_lessons_on_monday_and_saturday`, а также `test_lessons_count_per_day[Вторник]` и `[Четверг]`
(в обеих группах по 4 пары). Упали 22: `test_days_match` (в эталоне есть «Понедельник»),
count для Понедельника/Среды/Пятницы, все 18 `test_lesson_matches_expected` (другие дисциплины и
преподаватели; для Среды-пара5/6 — «на сайте только 4 пар»).

## Файлы

```
p4/
  NOTES.md
  pytest.ini                         testpaths=tests, кириллические id параметров без escape
  mirror/
    server.py                        Flask-зеркало, порт 8765
    swap_schedule.py                 подмена расписания / --restore
    page_raw.html                    DOM реальной страницы
    vanilla_raspisanie.js            оригинальный JS сайта
    api.json                         реальные ответы API (deps, groups, sched, logo)
    css/                             стили сайта
    data/schedule_original.json      оригинал расписания АСИ 23-1
    data/schedule_current.json       файл, который отдаёт /getschedule (подменяемый)
  tests/
    conftest.py, test_schedule.py, expected_schedule.py, expected_schedule_other.py
  site_shots/asi23_v3.png            рендер реального сайта (АСИ 23-1)
  out/
    mirror_page.png                  скриншот зеркала (Playwright, вся страница, 1400x3127)
    selenium_page.png                скриншот из Selenium (driver.save_screenshot, вся страница, 1400x3088)
    run_ok.txt/.png                  прогон 1
    run_fail_site_changed.txt/.png   прогон 2 (включая вывод swap_schedule.py и --restore)
    run_fail_other_expected.txt/.png прогон 3
    run_ok_after_restore.txt/.png    прогон 4
```

Запуск: `cd p4/mirror && python3 server.py &`, затем `cd p4 && RASP_URL=http://127.0.0.1:8765/raspisanie python3 -m pytest tests -v --tb=short`.
