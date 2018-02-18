import base64
import json
import os
from dotenv import load_dotenv
from pyrogram import Client
from configparser import ConfigParser
from collections import namedtuple

Config = namedtuple('Config', ['api_id', 'api_hash'])

APP_ROOT = os.path.dirname(__file__)
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)


class XClient(Client):
  """An wrapper for pyrogram.Client who overriding 'load_config' & 'load_session' methods."""

  ## original: https://github.com/pyrogram/pyrogram/blob/69e4ebfa559b10a613af70f00f69d4630843defb/pyrogram/client/client.py#L588
  def load_config(self):
    """Versão criada para manter as chaves do app em variáveis de ambiente.
    Assim, o arquivo config.ini é desnecessário.
    A chave 'api_id' virou a env 'TELEGRAM_API_ID'
    A chave 'api_hash' virou a env 'TELEGRAM_API_HASH'.
    """
    parser = ConfigParser()

    self.config = Config(
      api_id=int( os.environ.get('TELEGRAM_API_ID') ),
      api_hash=os.environ.get('TELEGRAM_API_HASH')
    )

    if parser.has_section('proxy'):
      self.proxy = Proxy(
          enabled=parser.getboolean('proxy', 'enabled'),
          hostname=parser.get('proxy', 'hostname'),
          port=parser.getint('proxy', 'port'),
          username=parser.get('proxy', 'username', fallback=None) or None,
          password=parser.get('proxy', 'password', fallback=None) or None
      )

  ## original: https://github.com/pyrogram/pyrogram/blob/69e4ebfa559b10a613af70f00f69d4630843defb/pyrogram/client/client.py#L606
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