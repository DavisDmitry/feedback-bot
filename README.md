# Telegram Feedback Bot

Convenient telegram bot forwards messages from users to the owner and gives an opportunity to reply to them. For the most active users, you can create separate chats by adding a bot and using a special command `/link`.

## Commands:

`/start` — send help message

`/link <CHAT_ID>` — link group to user (for admin)

`/unlink` — unlink group from user (for admin)

## Deploy

### With Docker

[docker-compose example with traefik as a reverse proxy](https://github.com/DavisDmitry/feedback-bot/blob/master/docker-compose.yml)

### Manual

For donwload dependencies you need to install [poetry](https://python-poetry.org/).

Than clone this repository:

```bash
git clone https://github.com/DavisDmitry/feedback-bot.git
```

#### Install dependencies:

With dev:

```bash
poetry install
```

Or without dev:

```bash
poetry install --no-dev
```

Set env vars. LOG_LEVEL for example:

```bash
export LOG_LEVEL=INFO
```

And run:

```bash
python -m feedback_bot
```

Also you can change the messages sent by the bot in the messages.yml file

## Env vars:

`LOG_LEVEL` — logging level (`INFO` is default, may be `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, `NOTSET`)

`BOT_TOKEN` — your bot token, can be obtained from [BotFather](https://t.me/botfather)

`BOT_DOMAIN` — your bot domain (`bot.dmitrydavis.xyz` for example)

`ADMIN_ID` — your telegram ID

`DATABASE_PATH` — path to sqlite3 database file

`DEFAULT_CHAT_ID` — chat id that will be used to receive messages from users (equals ADMIN_ID as default)

`MESSAGES_PATH` — path to messages.yml file

## Run tests and linters

For tests and linters you need to install dev dependecies:

```bash
poetry install
```

### Run isort:

```bash
poetry run isort .
```

### Run black:

```bash
poetry run black .
```

### Run pytest with coverage display:

```bash
poetry run pytest --cov=feedback_bot --cov-report=term-missing
```
