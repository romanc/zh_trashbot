# Züri Trash Bot

Züri Trash Bot is a [Telegram](https://telegram.org) bot, which offers a convenient way to query paper :newspaper: and cardboard :package: collection dates for people living in Zurich. The bot also support querying dates :calendar: for the next cargo tram and E-tram :train:.

## Usage

Visit [https://t.me/zh_trashbot](https://t.me/zh_trashbot) or use `@zh_trashbot` directly from within Telegram.

## Deployment

You don't need to deploy the bot to use it. For using the bot, just follow [this link](https://t.me/zh_trashbot).

Steps to deploy (a copy of) this bot include

- clone this repository,
- [install uv](https://docs.astral.sh/uv/getting-started/installation/) for project management,
- setup python: `uv install python`,
- install the project: `uv sync --all-extras --dev`
- get a [Telegram bot token](https://core.telegram.org/bots#creating-a-new-bot)
- create a config file: `mv config.ini.example config.ini` and configure the token in it
- run the bot: `uv run src/zh_trashbot/bot.py`
