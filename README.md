# me as [Telegram](https://telegram.org/) Bot

check [Wiki Pages](https://github.com/micalevisk/me-telegram-bot/wiki)

## Development usage

### first usage

Get your own Telegram API keys [here](https://my.telegram.org/auth?to=apps)

```bash
cp .env.example .env # and place your API values there

# To authorize this client once and generate the .session file
# follow the prompted instructions
export PIPENV_VENV_IN_PROJECT="enabled"

pipenv install
pipenv run python -B setup.py

# authorize and quit (Ctrl-C)
```

### once the project is set up

```bash
export PIPENV_VENV_IN_PROJECT="enabled"

pipenv install
#pipenv shell
pipenv run python start_client.py

## or to restart on file changes (`$ npm i -g nodemon` before)
nodemon --signal SIGHUP -e '.py' ./start_client.py
```

In case of `sqlite3.OperationalError: database is locked` error:

```bash
fuser me_bot.session
kill -9 <pid>
```

## Deploy to Heroku

Create an app on [Heroku](https://heroku.com) and use **Heroku Git** as deployment method (_Deploy_ tab).

```bash
# Remove the first two lines of `.gitignore` file
sed 1,2d -i .gitignore # now your .env and .session files are tracked by Git

git add -A
git commit
git push heroku master
```

