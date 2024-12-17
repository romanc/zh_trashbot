# Züri Trash Bot

Züri Trash Bot is a [Telegram](https://telegram.org) bot, which offers a convenient way to query paper :newspaper: and cardboard :package: collection dates for people living in Zurich. The bot also support querying dates :calendar: for the next cargo tram and E-tram :train:.

## Usage

Visit [https://t.me/zh_trashbot](https://t.me/zh_trashbot) or use `@zh_trashbot` directly from within Telegram.

## Deployment

You don't need to deploy the bot to use it. For using the bot, just follow the link above. If - for whatever reason - you want to deploy (a copy of) this bot, you will need to:

- clone this repository,
- create a virtual environment (use python 3.6 or later),
- install the dependencies (into your virtual environment): `pip install -r requirements.txt`,
- copy `config.ini.example` to `config.ini`, get a [Telegram bot token](https://core.telegram.org/bots#creating-a-new-bot) and configure it in `config.ini`,
- run `python trashbot.py`  from within the `src/` folder (or submit a PR to fix the fact that we currently have a hard-coded relative path to the config file)
