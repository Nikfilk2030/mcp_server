# Аудитории клубов: MCP-сервер

`ping` возвращает `pong` и проверяет связь без LLM. `lookup_club_room` уже виден клиенту, но его нужно дописать в [tools.py](tools.py)

## Локальный запуск

Нужны Python 3.14, Bash, curl и jq. Из каталога `starter`:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python server.py
```

Во втором терминале из того же каталога:

```bash
curl -fsS http://127.0.0.1:8000/healthz
bash scripts/lifecycle.sh
```

[Скрипт с curl-запросами](scripts/lifecycle.sh) отправляет `initialize` на `/mcp`, проверяет версию `2025-11-25`, затем отправляет `notifications/initialized` (HTTP 202), `tools/list` и три `tools/call`. Сервер не хранит сессии, поэтому `Mcp-Session-Id` не нужен. Для `ping` ожидается `pong`, для поиска до реализации ожидается `isError: true`

## Поиск аудитории

В [schedule.json](schedule.json) три вымышленных клуба. Для точного `club_id` верните строку `room` из расписания, для неизвестного идентификатора верните `Клуб не найден` без исключения. Например, `orbit` и `ORBIT` считаются разными идентификаторами

```bash
.venv/bin/python -m unittest discover -s tests -v
```

В заготовке проходит тест `ping`, а два теста поиска завершаются с `NotImplementedError`. После правки перезапустите сервер и повторите curl-проверку: для `orbit` ожидается `Б-204` без ошибки инструмента

## Docker на учебной ВМ

Скопируйте каталог на ВМ с Docker Engine и Compose. В каталоге проекта на самой ВМ выполните:

```bash
docker compose up --build --wait
bash scripts/lifecycle.sh
docker compose down
```

Порт `8000` привязан к `127.0.0.1` ВМ. Не запускайте одновременно Python-сервер и контейнер на одном порту

## Подключение клиента

Для проверки с ноутбука оставьте контейнер на ВМ запущенным и выполните на ноутбуке `ssh -N -L 8000:127.0.0.1:8000 user@VM_IP`, подставив пользователя и белый IP своей ВМ. Пока SSH открыт, локальный MCP-клиент может использовать Streamable HTTP по адресу `http://127.0.0.1:8000/mcp`. Так не нужно открывать порт контейнера всему интернету

Облачный ассистент не увидит этот localhost. Для него нужен доступный с его стороны HTTPS-адрес `/mcp` на учебной ВМ с поддерживаемой клиентом авторизацией. Получите параметры у преподавателя. Не указывайте ключ в URL и не публикуйте его в отчёте

[Описание обмена MCP](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle) · [Вызов инструментов](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
