from . import commands
from micalevisk.utils import *
from inspect import getmembers, isfunction
from sys import stderr


##############################################################################
########################### CommandsHandler module ###########################
##############################################################################
COMMAND_KEYWORD = '!'
COMMAND_HANDLER_PREFIX = 'handler_command_'
COMMANDS_AND_ACTIONS = { ## chave:str, valor:callable (client, update) [o handler_command_x]
  'teste': lambda c, u, *args: c.send_message('me', 'o comando !teste foi executadoooo'),
}


def msg_with_cmd_style(message:str):
  """Check if message starts with an especial string."""
  return message.strip().startswith(COMMAND_KEYWORD)

# def listener(cmd_message:str, *args): ## https://stackoverflow.com/questions/3394835/args-and-kwargs
def listener(cmd_message:str, args:list):
  cmd_like = cmd_message.split(' ', 1)[0]
  cmd = cmd_like[ len(COMMAND_KEYWORD) : ]
  cmd_args = cmd_message[ len(COMMAND_KEYWORD) + len(cmd) + 1 : ]
  # print(f'mensagem comando-like |{cmd}| ; args = |{cmd_args}|', file=stderr)#§

  return COMMANDS_AND_ACTIONS[cmd](*args, cmd_args) if cmd in COMMANDS_AND_ACTIONS else None


def enable():
  # print(__name__, enable.__name__, file=stderr)#§

  for (fname, f) in getmembers(commands):
    if isfunction(f) and fname.startswith(COMMAND_HANDLER_PREFIX):
      func_name = fname[ len(COMMAND_HANDLER_PREFIX): ]
      COMMANDS_AND_ACTIONS[func_name] = f
