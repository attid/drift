# Drift Telegram Bridge

Минимальная Telegram-прослойка к Neuraldeep Drift API.

Что делает:

- принимает личные сообщения только от разрешённых Telegram user ID;
- в разрешённых группах реагирует только на сообщения с mention бота, например `@my_bot статус`;
- заводит отдельную Drift conversation на каждый Telegram chat ID;
- хранит связь `telegram_chat_id -> drift_conversation_id` в SQLite;
- отправляет в Drift только последний пользовательский prompt, без локального дубля истории.

## Конфиг

Переменные:

- `TELEGRAM_BOT_TOKEN` - токен Telegram-бота от BotFather.
- `DRIFT_API_TOKEN` - Drift API token формата `dft_*`.
- `ALLOWED_USER_IDS` - comma-separated Telegram user IDs, которым разрешено писать боту.
- `ALLOWED_GROUP_CHAT_IDS` - comma-separated chat IDs групп, где бот отвечает только по mention.
- `DRIFT_MODEL` - по умолчанию `gpt-oss-120b`, можно поставить `qwen3.6-35b-a3b`.
- `SQLITE_PATH` - путь к SQLite DB, в Docker по умолчанию `/data/bot.sqlite3`.

## Docker

Образ публикуется GitHub Actions в GHCR:

```bash
docker pull ghcr.io/attid/drift:latest
```

```bash
export TELEGRAM_BOT_TOKEN="123456:telegram-token"
export DRIFT_API_TOKEN="dft_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export ALLOWED_USER_IDS="123456789,987654321"
export ALLOWED_GROUP_CHAT_IDS="-1001234567890"

docker compose pull
docker compose up -d
docker compose logs -f
```

`docker-compose.yml` не читает `.env` через `env_file`: переменные нужно передать из shell,
CI/CD secrets или окружения хоста.

## Локальный запуск

```bash
uv sync
uv run drift-tg-bot
```

## Тесты и линт

```bash
uv run pytest
uv run ruff check .
```

## Drift API

Используются публичные endpoint'ы Drift:

- `POST https://drift.neuraldeep.ru/v1/conversations`
- `POST https://drift.neuraldeep.ru/v1/chat/completions`

В `chat/completions` передаётся `conversation_id`, поэтому Drift сам поднимает историю и память из своей БД.
