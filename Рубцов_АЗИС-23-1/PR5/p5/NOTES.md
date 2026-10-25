# Практика 5. Нагрузочное тестирование FastAPI-бэкенда в Apache JMeter

Рабочая папка: `/home/claude/work/p5`. Все результаты в `out/`.

## Версии

| Компонент | Версия |
|---|---|
| Python | 3.11.15 |
| FastAPI | 0.141.1 |
| Uvicorn | 0.46.0 |
| Pydantic | 2.13.3 |
| Apache JMeter | 5.5 (см. раздел «Проблемы» — почему не 5.6.3) |
| Java | OpenJDK 21.0.10 (Ubuntu 24.04) |
| Xvfb / openbox / xdotool / ImageMagick `import` | системные пакеты Ubuntu |
| Chromium (для скриншотов Swagger и HTML-отчёта) | Playwright chromium-1194 |

## Шаг 1. Сервер

1. `main.py` создан дословно по методичке (без правок кода). Файл: `/home/claude/work/p5/main.py`.
2. Запуск: `cd p5 && uvicorn main:app --reload --port 8000 > out/uvicorn.log 2>&1 &`
   Сервер стартовал без ошибок (`Application startup complete`).
3. Проверка curl (вывод в `out/curl_check.txt`, PNG `out/curl_check.png`):
   - `POST /items/` с JSON `{"name": "Item 1", "description": "A description of Item 1", "price": 100.0}` → `200 OK`,
     тело `{"name":"Item 1","description":"A description of Item 1","price":100.0}`;
   - `GET /items/` → `200 OK`, массив объектов **без поля `id`**;
   - `GET /items/1` → `200 OK`;
   - `GET /items/999` → `404 {"detail":"Item not found"}`.
4. Swagger UI `http://127.0.0.1:8000/docs` — скриншот `out/swagger.png` (видны GET /items/, POST /items/, GET /items/{item_id}, схема Item).
   Скрипт `out/swagger_shot.py` (Playwright). В сети окружения CDN `cdn.jsdelivr.net` заблокирован прокси, поэтому запросы
   к `swagger-ui.css`/`swagger-ui-bundle.js` перехватываются и отдаются из локальной копии swagger-ui-dist 5.17.14
   (`out/swui/`, скачан с registry.npmjs.org). Сервер при этом не изменялся.
5. Скриншот терминала сервера: `out/uvicorn.png` (лог содержит строки запросов POST/GET от curl и от трёх прогонов JMeter).

## Шаг 2. JMeter

### Установка

`dlcdn.apache.org`, `archive.apache.org`, `downloads.apache.org`, Maven Central и все проверенные зеркала Apache
(aliyun, tuna, yandex, berkeley, icm.edu.pl) возвращают `403` от egress-прокси окружения. Из доступных хостов —
`raw.githubusercontent.com`. Через поиск Sourcegraph найден публичный репозиторий, в котором закоммичен полный дистрибутив
**apache-jmeter-5.5** (`LearnCodeWithDurgesh/Microservices-Tutorial-Series`, каталог `apache-jmeter-5.5/apache-jmeter-5.5/`).
Файлы (bin/, lib/, lib/ext/, report-template) скачаны пофайлово в `/home/claude/work/p5/jmeter` (280 файлов, 76 MB,
список — `out/jmeter_files.txt`). Целостность jar проверена (`zipfile.testzip`), `jmeter/bin/jmeter --version` → **5.5**.
Отсутствовал `lib/ext/ApacheJMeter_config.jar` (в исходном репозитории его нет) — для данного плана он не нужен
(HTTP Header Manager входит в `ApacheJMeter_http.jar`, Response Assertion — в `ApacheJMeter_components.jar`).
Также в репозитории нет `fontawesome-webfont.woff2` (на отчёт не влияет).

### Тест-план `auction_test.jmx`

Создан как XML (`jmeter="5.5"`), затем открыт в GUI — загрузился без ошибок и предупреждений:

- Test Plan «Auction API Test»
  - Thread Group: Number of Threads = **5**, Ramp-Up = **10**, Loop Count = **1**
    - HTTP Request «Create Item»: `http://127.0.0.1:8000`, `POST /items/`, Body Data
      `{"name": "Item 1", "description": "A description of Item 1", "price": 100.0}`
      - HTTP Header Manager: `Content-Type: application/json`
      - Response Assertion: Response Code equals `200`
    - HTTP Request «Get Items»: `GET /items/`
      - Response Assertion: Response Code equals `200`
    - View Results Tree, Summary Report, Aggregate Report

### GUI под Xvfb

```
Xvfb :98 -screen 0 1400x950x24 &
DISPLAY=:98 openbox &
DISPLAY=:98 jmeter/bin/jmeter -t auction_test.jmx &
```
Окно растянуто до 1400×920 (`xdotool windowsize/windowmove`), дерево раскрыто кликами по стрелкам, запуск — `Ctrl+R`,
скриншоты — `import -window root`. Каждый скриншот открыт и проверен визуально.

### Non-GUI прогон

```
jmeter/bin/jmeter -n -t auction_test.jmx -l out/results.jtl -e -o out/report
```
Консольный вывод — `out/jmeter_cli.txt` / `out/jmeter_cli.png`, результаты — `out/results.jtl` (10 строк + заголовок),
HTML-дашборд — `out/report/index.html` (скриншот `out/07_html_report.png`).

## Скриншоты (`out/`)

| Файл | Что видно |
|---|---|
| `swagger.png` | Swagger UI /docs: три эндпоинта и схемы |
| `uvicorn.png` | терминал uvicorn: старт и строки запросов `POST /items/ 200`, `GET /items/ 200` |
| `curl_check.png` | вывод curl POST/GET/GET by id/404 |
| `01_thread_group.png` | JMeter GUI, дерево плана (все элементы), Thread Group: 5 / 10 / 1 |
| `02_create_item.png` | HTTP Request «Create Item»: 127.0.0.1:8000, POST, /items/, вкладка Body Data с JSON |
| `03_get_items.png` | HTTP Request «Get Items»: GET /items/ |
| `03b_header_manager.png` | HTTP Header Manager: Content-Type = application/json |
| `03c_response_assertion.png` | Response Assertion (Response Code, Equals, 200) |
| `04_results_tree_response.png` | View Results Tree после запуска: 10 зелёных результатов, выбран первый «Create Item», вкладка Response data → Response Body: `{"name":"Item 1","description":"A description of Item 1","price":100.0}` |
| `04b_results_tree_request.png` | тот же результат, вкладка Request |
| `05_summary_report.png` | Summary Report с цифрами после прогона |
| `06_aggregate_report.png` | Aggregate Report с цифрами после прогона |
| `07_html_report.png` | HTML-дашборд non-GUI прогона (APDEX 1.000, PASS 100 %) |
| `jmeter_cli.png` | консольный вывод non-GUI прогона |
| `db_after.png` | содержимое таблицы items после тестов |

## Результаты (реальные цифры)

### GUI-прогон (Summary Report, `05_summary_report.png`)

| Label | # Samples | Average, ms | Min | Max | Std. Dev. | Error % | Throughput |
|---|---|---|---|---|---|---|---|
| Create Item | 5 | 27 | 5 | 108 | 40.32 | 0.00 % | 38.5/min |
| Get Items | 5 | 3 | 2 | 4 | 0.75 | 0.00 % | 39.1/min |
| TOTAL | 10 | 15 | 2 | 108 | 30.98 | 0.00 % | 1.3/sec |

Aggregate Report (`06_aggregate_report.png`): Create Item — Median 8, 90 % 9, 95 % 108, 99 % 108;
Get Items — Median 3, 90/95/99 % 4; TOTAL — Median 4, 90 % 9, 95 % 9, 99 % 108. Ошибок 0.

### Non-GUI прогон (`jmeter_cli.txt`, `results.jtl`)

```
summary =     10 in 00:00:08 =    1.2/s Avg:     8 Min:     2 Max:    54 Err:     0 (0.00%)
```
Все 10 сэмплов — код 200, `success=true`. Create Item: 54, 7, 6, 5, 5 мс (avg 15.4); Get Items: 2, 4, 2, 2, 2 мс (avg 2.4).
HTML-дашборд: APDEX 1.000 для обоих запросов, 0 FAIL.

Первый запрос каждого прогона (54–108 мс) заметно медленнее остальных (2–9 мс) — прогрев HTTP-клиента JMeter и
первое соединение; при Ramp-Up 10 с потоки стартуют раз в 2 с, поэтому нагрузка фактически последовательная.

### База данных после тестов (`out/db_after.txt`)

`count(*) = 16` строк `Item 1 | A description of Item 1 | 100.0`, id 1…16:
1 — curl-проверка, 5 — контрольный non-GUI прогон перед GUI, 5 — GUI-прогон, 5 — non-GUI прогон с отчётом.
В логе uvicorn 16 `POST /items/` и 16 `GET /items/`.

## Найденные проблемы

1. **Поле `id` отсутствует в ответах API.** Модель `Item` не содержит поля `id`, но в `get_items` / `get_item` код
   вызывает `Item(id=row[0], ...)`. Pydantic v2 по умолчанию (`extra='ignore'`) молча отбрасывает лишнее поле, поэтому
   сервер **не падает**, но клиент не получает идентификаторы: `GET /items/` возвращает
   `[{"name":..., "description":..., "price":...}, ...]` без `id`. Различить записи невозможно, `GET /items/{item_id}`
   приходится вызывать «вслепую». Исправление (в код не вносилось, т.к. задание — код по методичке): добавить
   `id: Optional[int] = None` в `Item` или отдельную модель `ItemOut`.
2. `POST /items/` возвращает исходный объект запроса, а не созданную запись — созданный `id` неизвестен клиенту.
3. `description: str = None` — типизация некорректна (должно быть `Optional[str] = None`); pydantic v2 принимает
   значение по умолчанию без проверки, поэтому работает, но в схеме OpenAPI поле помечено как обязательная строка.
4. Каждый запрос открывает новое соединение SQLite; при `--reload` файл `auction.db` лежит в отслеживаемой папке.
   На данной нагрузке (5 потоков) ошибок не проявилось.
5. Ответ `GET /items/` растёт с каждым POST (в JTL размер ответа 271 → 559 байт за прогон) — пагинации нет;
   при длительной нагрузке время ответа будет расти.
6. Окружение: загрузка JMeter 5.6.3 с официальных зеркал и Maven Central невозможна (прокси 403), использована
   версия 5.5, полученная из публичного GitHub-репозитория через raw.githubusercontent.com. Загруженный CDN Swagger UI
   также заблокирован — для скриншота ассеты подменены локальной копией (сервер не менялся).
