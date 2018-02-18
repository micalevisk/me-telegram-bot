from os import path, environ
from dotenv import load_dotenv
from pyrogram import Client
from configparser import ConfigParser
from collections import namedtuple

Config = namedtuple('Config', ['api_id', 'api_hash'])

APP_ROOT = path.dirname(__file__)
dotenv_path = path.join(APP_ROOT, '.env')


class XClient(Client):
  """An wrapper for pyrogram.Client who overwrite 'load_config' method."""

  ## original: https://github.com/pyrogram/pyrogram/blob/69e4ebfa559b10a613af70f00f69d4630843defb/pyrogram/client/client.py#L588
  def load_config(self):
    load_dotenv(dotenv_path)
    parser = ConfigParser()

    self.config = Config(
      api_id=int(environ.get('TELEGRAM_API_ID')),
      api_hash=environ.get('TELEGRAM_API_HASH')
    )

    if parser.has_section('proxy'):
      self.proxy = Proxy(
          enabled=parser.getboolean('proxy', 'enabled'),
          hostname=parser.get('proxy', 'hostname'),
          port=parser.getint('proxy', 'port'),
          username=parser.get('proxy', 'username', fallback=None) or None,
          password=parser.get('proxy', 'password', fallback=None) or None
      )