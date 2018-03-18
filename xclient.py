import base64
import json
import os
from pyrogram import Client
from dotenv import load_dotenv
from configparser import ConfigParser
from collections import namedtuple

Config = namedtuple('Config', ['api_id', 'api_hash'])

APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)


class XClient(Client):
  """An wrapper for pyrogram.Client who overriding 'load_session' method."""

  ## original: https://github.com/pyrogram/pyrogram/blob/5b5fb6cbec6ea083418b7485fc766f18181b698c/pyrogram/client/client.py#L800
  def load_session(self, session_name):
    """Versão criada para manter o 'auth_key' em uma variável de ambiente.
    Assim, o arquivo .session não precisa ser escondido, pois os demais
    dados não precisam ser privados.
    """
    try:
      with open('{}.session'.format(session_name), encoding='utf-8') as f:
        s = json.load(f)
    except FileNotFoundError:
      self.dc_id = 1
      self.auth_key = Auth(self.dc_id, self.test_mode, self.proxy).create()
    else:
      self.dc_id = s['dc_id']
      self.test_mode = s['test_mode']
      self.auth_key = base64.b64decode( os.environ.get('TELEGRAM_SESSION_AUTH_KEY') )
      self.user_id = s['user_id']
