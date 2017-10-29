# Setup:
This Section describes the steps needed to get the bot working on your server.
## Requirements:
1. PostgreSQL Server (Tested on 9.4 and 9.6)
2. Python 3.6+
3. A Telegram Bot (Use [@BotFather](t.me/botfather))
4. A Telegram Account

## Installation:
### PostgreSQL
1. Create a Database
2. In this Database run the commands inside of the [dbsetup.sql](../master/sourukorekuta/dbsetup.sql)
### Python
1. Run `pip install -r requirements.txt`
2. This should've installed python-telegram-bot, telethon and psycopg2
### Config
1. Copy and rename [empty_config.py](../master/sourukorekuta/empty_config.py) to `config.py`
2. Fill out all the fields. To get a token for the Userbot follow this Tutorial: [Creating your Telegram Application](https://core.telegram.org/api/obtaining_api_id)

# Misc
## BotFather:
If you want to autocomplete the commands send this as command list to BotFather:
```start - starts the bot
help - displays help for the bot
ping - pings the bot
joho - shows info for the user that has been replied to or the user that sent the command
tokei - show group stats
jikkokeikoku - tag all members subject to execution
jikko - execute all lurkers```

## Using the bot
Add the bot as Admin to your Group. It should start working.
