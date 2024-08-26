# Züri Trash Bot

Züri Trash Bot is a [Telegram](https://telegram.org) bot, which offers a convenient way to query paper :newspaper: and cardboard :package: collection dates for people living in Zurich. The bot also support querying dates :calendar: for the next cargo tram and E-tram :train:.

## Usage

Visit [https://t.me/zh_trashbot](https://t.me/zh_trashbot) or use `@zh_trashbot` directly from within Telegram.

## Deployment

You don't need to deploy the bot to use it. For using the bot, just follow the link above. If - for whatever reason - you want to deploy (a copy of) this bot, you will need to:

- clone this repository,
- install [asdf-vm](https://asdf-vm.com) and [asdf-python](https://github.com/asdf-community/asdf-python) to manage the python version,
- run `asdf global python system` to use the system's python version (if installed) outside this project,
- run `asdf install` to install the configured python version,
- run `python -m venv .venv/` to create the virtual environment,
- run `source .venv/bin/activate` to activate the virtual environment,
- run `pip install -r requirements.txt` to install the dependencies,
- copy `config.ini.example` to `config.ini`,
- get a [Telegram bot token](https://core.telegram.org/bots#creating-a-new-bot) and configure it in `config.ini`,
- run `python trashbot.py`  from within the `src/` folder (or submit a PR to fix the fact that we currently have a hard-coded relative path to the config file)

## VSCode setup

Recommended extensions are [ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) and [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker).
