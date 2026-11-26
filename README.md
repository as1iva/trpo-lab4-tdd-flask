# Практическая работа № 4 — TDD

Вариант 6: веб-приложение управления задачами на **Flask + SQLite**.
Выполнены **15 реальных циклов RED → GREEN → REFACTOR**. После интеграционных проверок: **31 passed**, покрытие приложения и ветвлений **100%**.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app todo run --host 127.0.0.1 --port 5000
```

Windows PowerShell: активировать окружение командой `.venv\Scripts\Activate.ps1`.
Открыть http://127.0.0.1:5000. База `instance/tasks.sqlite3` создается автоматически.
Приложение предназначено для локального учебного использования одним пользователем.

## Проверка

```bash
python -m pytest -q
python -m pytest --cov=todo --cov-branch --cov-report=term-missing --cov-fail-under=95
python scripts/watch_tests.py
```

Последняя команда запускает тесты при сохранении изменений в `todo/` или `tests/`; остановка — Ctrl+C.
GitHub Actions проверяет push и pull_request на Python 3.12, 3.13 и 3.14.

## Возможности

- Создание задачи; обрезка пробелов, длина от 1 до 200 символов.
- Завершение и возврат в работу.
- Изменение названия без потери статуса.
- Удаление только методом POST.
- Фильтры «Все», «Активные», «Выполненные» и поиск без учета регистра.
- Сохранение данных в SQLite между запусками.
- CSRF-защита форм; экранирование HTML; параметризованные SQL-запросы.
- Понятные страницы ошибок 400 и 404, адаптивная верстка.

Аутентификация, совместная работа и публичное развертывание не входят в задание. Для стабильных сессий между перезапусками можно задать `SECRET_KEY` через переменную окружения; секрет не следует коммитить.

## История TDD

Каждый цикл содержит коммиты `test: RED NN`, `feat: GREEN NN`, `refactor: NN`.
RED-коммиты намеренно содержат падающий новый тест. Итоговая ветка проходит весь набор.
В исходной среде каждый цикл выполнен автоматизированной последовательностью: запись теста → фактический запуск pytest → запись минимальной реализации → фактический запуск → рефакторинг → повторный запуск. Длительности ниже измеряют эту последовательность, без времени подготовки и оформления отчета; это не заявление о 75 минутах ручной работы.

| № | Требование | RED | GREEN | Секунд |
|---|---|---|---|---|
| 01 | empty list | 1 failed in 0.02s | 1 passed in 0.01s | 1.19 |
| 02 | create task | 1 failed, 1 passed in 0.02s | 2 passed in 0.01s | 0.83 |
| 03 | reject empty title | 2 failed, 2 passed in 0.03s | 4 passed in 0.01s | 0.85 |
| 04 | trim title | 1 failed, 4 passed in 0.03s | 5 passed in 0.02s | 0.87 |
| 05 | title length limit | 1 failed, 5 passed in 0.04s | 6 passed in 0.02s | 0.88 |
| 06 | complete task | 1 failed, 6 passed in 0.04s | 7 passed in 0.02s | 0.88 |
| 07 | reopen task | 1 failed, 7 passed in 0.04s | 8 passed in 0.02s | 0.88 |
| 08 | edit form | 1 failed, 8 passed in 0.05s | 9 passed in 0.03s | 0.9 |
| 09 | save edited task | 1 failed, 9 passed in 0.05s | 10 passed in 0.03s | 0.92 |
| 10 | delete task | 1 failed, 10 passed in 0.06s | 11 passed in 0.04s | 0.94 |
| 11 | missing task returns 404 | 4 failed, 11 passed in 0.13s | 15 passed in 0.05s | 1.03 |
| 12 | filter task status | 1 failed, 15 passed in 0.07s | 16 passed in 0.05s | 0.97 |
| 13 | persistent SQLite storage | 1 failed, 16 passed in 0.08s | 17 passed in 0.07s | 1.06 |
| 14 | search tasks | 1 failed, 17 passed in 0.10s | 18 passed in 0.09s | 1.08 |
| 15 | CSRF protection | 1 failed, 18 passed in 0.11s | 19 passed in 0.10s | 1.14 |

## Доказательства и отчет

- `docs/evidence/iterations.json` — фактические результаты, длительности и локальные SHA.
- `docs/evidence/NN-red.txt`, `NN-green.txt`, `NN-refactor.txt` — необработанные результаты pytest.
- `docs/evidence/NN-test.py.txt` — новый тест; `NN-green.diff` и `NN-refactor.diff` — фактические изменения.
- `docs/evidence/final-tests.txt` — итоговая проверка с покрытием.
- `docs/evidence/watch-tests.txt` — два запуска при сохранении файла.
- `docs/screenshots/` — реальные скриншоты создания репозитория, страниц журнала и приложения.
- `docs/REPORT.html` — подробный отчет со скриншотами; открыть в браузере.
- `docs/evidence/remote-map.json` — соответствие исходных локальных SHA коммитам GitHub.

Скриншоты циклов сняты со страницы просмотра сохраненных фактических логов и diff после выполнения циклов. Это не снимки терминала в момент разработки. При импорте истории удалено постороннее предупреждение pip с локальным путем; поэтому SHA локальной истории и GitHub отличаются. Полные результаты тестов сохранены.

## Структура

```text
todo/__init__.py     фабрика, маршруты, валидация
 todo/db.py          SQLite и транзакции
 todo/security.py    CSRF-защита
 todo/templates/     страницы Jinja
 todo/static/        стили
 tests/              функциональные и интеграционные тесты
 scripts/watch_tests.py
 .github/workflows/tests.yml
 docs/               отчет и доказательства
```

## Источники

- [Тестирование Flask](https://flask.palletsprojects.com/en/stable/testing/)
- [Фабрики приложений Flask](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
- [GitHub Actions для Python](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
