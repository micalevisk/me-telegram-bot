import sys, signal, os
import re
from pyrogram import Client
from pyrogram.handlers import MessageHandler
import pyrogram.filters as Filter
from inspect import getmembers, isfunction
from dotenv import load_dotenv
from functools import wraps

APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

# https://docs.pyrogram.org/api/client
app = Client(
  session_name="me_bot",
  api_id=os.getenv("TELEGRAM_API_ID"),
  api_hash=os.getenv("TELEGRAM_API_HASH")
)

def nodemon_handler(signum, frame):
  app.stop()
  sys.exit(0)
  # os.kill(os.getpid(), signal.SIGKILL)

signal.signal(signal.SIGINT, nodemon_handler)
signal.signal(signal.SIGHUP, nodemon_handler)


################# inject auto-reply to messages that match with certain regex #################
re_to_msg = {}

PATTERN_ENV_KEY_PREFIX=os.getenv("PATTERN_ENV_KEY_PREFIX")
REPLY_ENV_KEY_PREFIX=os.getenv("REPLY_ENV_KEY_PREFIX")
if PATTERN_ENV_KEY_PREFIX and REPLY_ENV_KEY_PREFIX:
  for (env_key, env_value) in os.environ.items():
    if env_key[:len(PATTERN_ENV_KEY_PREFIX)] == PATTERN_ENV_KEY_PREFIX:
      pattern_id = env_key[len(PATTERN_ENV_KEY_PREFIX):]
      re_to_msg[env_value] = os.getenv(f"{REPLY_ENV_KEY_PREFIX}{pattern_id}")

def make_reply_handler(text):
  def reply_msg(client, msg):
    is_self = msg.from_user != None and msg.from_user.is_self
    if not is_self:
      client.send_message(msg.chat.id, text,
        reply_to_message_id=msg.message_id, parse_mode="html")
  return reply_msg

for (regex_filter, reply_text) in re_to_msg.items():
  if reply_text == None: continue

  filters = ~Filter.bot & \
    ~Filter.scheduled & \
    Filter.private & \
    Filter.text & \
    Filter.regex(regex_filter, flags=re.IGNORECASE)

  app.add_handler(
    MessageHandler( make_reply_handler(reply_text), filters=filters),
    group=-1 )

  print(f"loaded auto-reply to RegExp: {regex_filter}")
###############################################################################################


if __name__ == "__main__":
  ## @see https://docs.pyrogram.org/topics/more-on-updates#handler-groups
  COMMAND_GROUP=0x1
  commands = __import__("commands")

  for (fname, maybe_message_handler) in getmembers(commands): ## Load commands
    if not( isfunction(maybe_message_handler) and hasattr(maybe_message_handler, 'cmd') ):
      continue

    deferred = maybe_message_handler.deferred
    if deferred:
      maybe_message_handler = maybe_message_handler(app)

    cmd = maybe_message_handler.cmd
    base_filters = Filter.command(cmd, prefixes='!') & Filter.user('me')
    filters = (base_filters & maybe_message_handler.filters) \
      if hasattr(maybe_message_handler, 'filters') \
      else (base_filters)

    app.add_handler(
      MessageHandler(maybe_message_handler, filters=filters),
      group=COMMAND_GROUP )
    print(f"command '{cmd}' loaded!")

  app.run() ## runs `app.start()` and `app.idle()`
