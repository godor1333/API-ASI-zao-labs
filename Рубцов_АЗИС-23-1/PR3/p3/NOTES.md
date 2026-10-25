# Практика 3 — тестирование класса AuthManager с pytest

## Окружение

| Компонент | Версия |
|-----------|--------|
| Python    | 3.11.15 |
| pytest    | 9.1.1 (pluggy 1.6.0) |
| sqlite3 (библиотека SQLite) | 3.45.1 |
| ОС        | Linux |

Рабочая папка: `/home/claude/work/p3`.

## Файлы проекта

| Файл | Назначение |
|------|------------|
| `auth_manager.py` | Тестируемый класс `AuthManager` — взят из методички дословно; SQL-инъекции в нём оставлены намеренно (учебная уязвимость), только комментарии заменены на русские `# уязвимость: SQL-инъекция`. |
| `pytest.ini` | Регистрация меток: `basic`, `parametrized`, `exception`, `security`, `slow`. |
| `test_auth_manager.py` | Основной набор тестов (19 passed + 1 skipped). |
| `test_auth_manager_failing.py` | Один заведомо падающий тест для демонстрации красного прогона. |
| `out/run_*.txt`, `out/run_*.png` | Логи прогонов и их «скриншоты терминала». |

## Фикстуры

* `db` — `sqlite3.connect(":memory:")`, отдаётся через `yield`, после теста соединение закрывается (`connection.close()`). Каждый тест получает чистую БД.
* `auth_manager` — зависит от `db`, возвращает `AuthManager(db)` (конструктор сам создаёт таблицу `users`).
* `get_balance(db, user_id)` — вспомогательная функция (не фикстура) для чтения баланса напрямую из БД.

## Состав тестов

| Тест | Тип | Метка | Что проверяет |
|------|-----|-------|---------------|
| `test_register_and_get_user_by_id` | базовый | `basic` | после `register_user` строка находится через `get_user_by_id`, все поля (id, username, password, country, balance) сохранены верно |
| `test_authenticate_user_success_and_wrong_password` | базовый | `basic` | верная пара логин/пароль → кортеж пользователя; неверный пароль → `None` |
| `test_delete_user` | базовый | `basic` | после `delete_user(1)` пользователь не находится по id |
| `test_count_users_by_country[CountryA-2]`, `[CountryB-1]`, `[CountryC-0]` | параметризованный (3 случая) | `parametrized` | подсчёт пользователей по стране; данные как в методичке (2 в CountryA, 1 в CountryB, 0 в CountryC) |
| `test_authenticate_user_parametrized[...]` (4 случая) | параметризованный | `parametrized` | верная пара → найден; неверный пароль, несуществующий логин, другой регистр логина → `None` |
| `test_transfer_balance_parametrized[...]` (4 случая) | параметризованный | `parametrized` | перевод 200 / 0 / 1000 / 0.5 между user1 (1000) и user2 (500) → ожидаемые балансы обоих (пример методички: 800 и 700) |
| `test_transfer_balance_insufficient_funds` | исключение | `exception` | перевод 500 при балансе 100 → `ValueError`, `match="Insufficient funds"`; балансы не изменились |
| `test_register_duplicate_username` | исключение | `exception` | повторная регистрация того же username → `sqlite3.IntegrityError` (UNIQUE constraint failed) |
| `test_sql_injection_authenticate_user` | безопасность | `security` | `authenticate_user("admin' OR '1'='1", "x")` возвращает admin без пароля; `"' OR 1=1 --"` возвращает пользователя даже без логина; обычный неверный пароль → `None` |
| `test_sql_injection_register_user_drop_table` | безопасность | `security` | payload `x', 'p', 'c', 0); DROP TABLE users; --` → `sqlite3.ProgrammingError`, таблица `users` существует, строк в ней 0 |
| `test_register_many_users` | пропускаемый | `slow` + `@pytest.mark.skip` | регистрация 10 000 пользователей; пропущен с reason «Медленный тест…» |
| `test_user_row_to_dict` | условно пропускаемый | `@pytest.mark.skipif(sys.version_info < (3, 7))` | преобразование строки в dict; на Python 3.11 выполняется (PASSED), на Python < 3.7 был бы пропущен |
| `test_transfer_balance_wrong_expectation` (отдельный файл) | заведомо падающий | — | ожидается баланс 900 вместо реальных 800 → `assert 800.0 == 900` |

Итого в `test_auth_manager.py`: 20 элементов (12 функций, из них 3 параметризованы → 3+4+4 = 11 случаев), результат **19 passed, 1 skipped**. С падающим файлом: 21 элемент, **1 failed, 19 passed, 1 skipped**.

Реально используемые метки: `basic` (3), `parametrized` (3 функции / 11 случаев), `exception` (2), `security` (2), `slow` (1). Отбор `-m "basic or exception"` выбирает 5 тестов, 16 отклоняются (deselected).

## Поведение SQL-инъекций (проверено фактически)

Класс подставляет параметры в SQL через `str.format`, без параметризованных запросов.

### 1. `authenticate_user` — уязвимость подтверждена

Вызов `authenticate_user("admin' OR '1'='1", "x")` формирует запрос:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'x'
```

В SQL оператор `AND` имеет более высокий приоритет, чем `OR`, поэтому условие
читается как `username = 'admin' OR ('1'='1' AND password = 'x')`. Первая
часть истинна для строки `admin` → она возвращается, пароль фактически не
проверяется. Тест это доказывает: возвращается кортеж `(1, 'admin', 'supersecret', ...)`.

Важный нюанс: из-за приоритета `AND` этот конкретный payload срабатывает только
при известном логине (`"nobody' OR '1'='1"` вернёт `None`). Payload с
SQL-комментарием `"' OR 1=1 --"` отрезает проверку пароля целиком:

```sql
SELECT * FROM users WHERE username = '' OR 1=1 --' AND password = 'x'
```

и возвращает первого пользователя таблицы без знания ни логина, ни пароля. Оба
варианта закреплены в тесте `test_sql_injection_authenticate_user`.
Контрольная проверка `authenticate_user("admin", "x") is None` показывает,
что «честный» неверный пароль по-прежнему отклоняется.

### 2. `register_user` с `DROP TABLE` — таблица НЕ удаляется

Payload `x', 'p', 'c', 0); DROP TABLE users; --` формирует строку:

```sql
INSERT INTO users (username, password, country, balance)
VALUES ('x', 'p', 'c', 0); DROP TABLE users; --', 'p', 'c', 0)
```

Синтаксически это два SQL-выражения. Метод `sqlite3.Connection.execute()` (как и
`Cursor.execute()`) выполняет ровно одно выражение и отвергает строку целиком с
исключением:

```
sqlite3.ProgrammingError: You can only execute one statement at a time.
```

Фактические последствия (закреплены в assert'ах теста):
* исключение `sqlite3.ProgrammingError` выброшено (`pytest.raises(..., match="only execute one statement")`);
* таблица `users` присутствует в `sqlite_master` (`len(tables) == 1`);
* `INSERT` тоже не выполнен — `SELECT COUNT(*) FROM users` даёт 0
  (транзакция `with self.connection` откатывается).

Дополнительно проверен payload из методички `testuser'; DROP TABLE users; --`:
он даёт `sqlite3.OperationalError: near ";": syntax error`, потому что скобка
`VALUES (` остаётся незакрытой; таблица также сохраняется. Поэтому тест из
методички `test_sql_injection_register_user` в исходном виде (без `pytest.raises`)
упал бы на исключении — в работе используется вариант с ожиданием исключения,
соответствующий реальному поведению sqlite3.

Вывод: защита от многовыражённой инъекции в данном случае — свойство DB-API
драйвера sqlite3, а не кода `AuthManager`; инъекции внутри одного выражения
(обход аутентификации) работают. Для исправления нужны параметризованные запросы
(`execute("... WHERE username = ? AND password = ?", (username, password))`).

## Выполненные команды

Из папки `/home/claude/work/p3`, с переменными `PY_COLORS=1 FORCE_COLOR=1 COLUMNS=110`
для сохранения цвета в файле:

```bash
python3 -m pytest test_auth_manager.py -v --maxfail=2 --tb=short 2>&1 | tee out/run_ok.txt
python3 -m pytest test_auth_manager.py test_auth_manager_failing.py -v --maxfail=2 --tb=short 2>&1 | tee out/run_fail.txt
python3 -m pytest -m "basic or exception" -v 2>&1 | tee out/run_markers.txt
python3 -m pytest --collect-only -q 2>&1 | tee out/run_collect.txt
```

Преобразование логов в PNG (из `/home/claude/work`):

```bash
python3 tools/term2png.py p3/out/run_ok.txt p3/out/run_ok.png --title "python -m pytest test_auth_manager.py -v --maxfail=2 --tb=short"
python3 tools/term2png.py p3/out/run_fail.txt p3/out/run_fail.png --title "python -m pytest test_auth_manager.py test_auth_manager_failing.py -v --maxfail=2 --tb=short"
python3 tools/term2png.py p3/out/run_markers.txt p3/out/run_markers.png --title 'python -m pytest -m "basic or exception" -v'
python3 tools/term2png.py p3/out/run_collect.txt p3/out/run_collect.png --title "python -m pytest --collect-only -q"
```

## Результаты прогонов

| Файл | Команда | Итог |
|------|---------|------|
| `out/run_ok.txt` / `.png` | `pytest test_auth_manager.py -v --maxfail=2 --tb=short` | 19 passed, 1 skipped |
| `out/run_fail.txt` / `.png` | `pytest test_auth_manager.py test_auth_manager_failing.py -v --maxfail=2 --tb=short` | 1 failed, 19 passed, 1 skipped; в разделе FAILURES виден `E   assert 800.0 == 900` |
| `out/run_markers.txt` / `.png` | `pytest -m "basic or exception" -v` | 5 passed, 16 deselected |
| `out/run_collect.txt` / `.png` | `pytest --collect-only -q` | 21 tests collected (список всех узлов, включая параметризованные id) |

Все PNG (ширина 1021 px, тёмная тема терминала) открыты и проверены на читаемость.
