# Setup:
This Section  describes the steps needed to get the bot working on your server.
## Requirements:
1. PostgreSQL Server
2. Python 3.6+

## Installation:
### PostgreSQL
1. Create a Database
2. In this Database run the commands inside of the [dbsetup.sql](../blob/master/sourukorekuta/dbsetup.sql)
### Python
1. Run `pip install -r requirements.txt`
2. This shouldve installed python-telegram-bot, telethon and psycopg2
### Config
1. Copy and rename [empty_config.py](../blob/master/sourukorekuta/empty_config.py) to `config.py`
2. Fill out all the fields. To get a token for the Userbot follow this Tutorial: [Creating your Telegram Application](https://core.telegram.org/api/obtaining_api_id)
