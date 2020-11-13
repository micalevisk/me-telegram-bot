import os
from pyrogram import Client
from dotenv import load_dotenv

APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# https://docs.pyrogram.org/api/client
app = Client(
  session_name="me_bot",
  api_id=os.getenv("TELEGRAM_API_ID"),
  api_hash=os.getenv("TELEGRAM_API_HASH"),
  app_version="Pyrogram 1.0.7")

app.run()
