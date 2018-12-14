from micalevisk.utils import *
from pyrogram import ParseMode
from time import sleep
import re

msgs_reportadas = dict([]) ## <reply_to_msg_id> --> <message.id>

############################################################
######################### 'admins' #########################
############################################################
def get_quote_admins(client, chat_id:int) -> str:
  admins = get_chat_admins(client, chat_id)
  valid_admins = filter_users_with_status(admins, (types.UserStatusOnline, types.UserStatusRecently)) or admins
  return parse_usernames(valid_admins) if valid_admins else ''

def exec_command_admins(client, message:types.Message):
  chat_id = message.to_id.channel_id
  cmd_response_msg = get_quote_admins(client, chat_id)

  if cmd_response_msg:
    ## registrar o id mensagem [replicada] na lista de reportadas
    if hasattr(message, 'reply_to_msg_id') and message.reply_to_msg_id:
      msgs_reportadas[message.reply_to_msg_id] = message.id

    return client.edit_message_text(chat_id, message.id, cmd_response_msg)

  return client.delete_messages(chat_id, [message.id], True)

def handler_command_admins(client, update, cmd_args):
  return exec_command_admins(client, update.message)


##########################################################
######################### 'tags' #########################
## TODO: unique hashtags                                ##
##########################################################
REGEX_HASHTAGS = re.compile('\B(#\w+)')
def exec_command_tags(client, message:types.Message):
  chat_id = 'me'
  try:
    client.edit_message_text(chat_id, message.id, '<code>...</code>', ParseMode.HTML)
  except Exception as inst:
    print(inst)
    return

  saved_messages_history = client.send(
    functions.messages.GetHistory(
      InputPeerSelf(),
      0, 0, 0, 5000, 0, 0, 0
    )
  )

  msgs = [ '\n'.join(re.findall(REGEX_HASHTAGS, m.message))
    for m in saved_messages_history.messages if isinstance(m, types.Message) and re.search(REGEX_HASHTAGS, m.message) ]

  msg_result = '\n'.join(msgs) if len(msgs) > 0 else 'nenhuma tag foi encontrada'
  return client.edit_message_text(chat_id, message.id, msg_result)

def handler_command_tags(client, update, cmd_args):
  if is_newmessage_from_self(update):
    return exec_command_tags(client, update.message)


#########################################################
######################### 'plp' #########################
#########################################################
REGEX_FLOOD_WAIT_X_ERROR = re.compile('.+ wait of (\d+)', re.IGNORECASE)
def exec_command_plp(client, message:types.Message):
  chat_id = message.to_id.user_id if isinstance(message.to_id, types.PeerUser) else message.to_id.channel_id
  client.edit_message_text(chat_id, message.id, '<code>...</code>', ParseMode.HTML)

  ultimo_anuncio = get_last_announcement_sites_google('plpicompufam2018periodo2')
  if (ultimo_anuncio is None):
    return client.delete_messages(chat_id, [message.id], True)

  if (ultimo_anuncio['updated_date']):
    msg_result = '<b>{publish_date}</b> ~ <code>{updated_date}</code>\n<a href="{link}">{title}</a>'.format(**ultimo_anuncio)
  else:
    msg_result = '<b>{publish_date}</b>\n<a href="{link}">{title}</a>'.format(**ultimo_anuncio)

  edit_message = lambda: client.edit_message_text(chat_id, message.id, msg_result, ParseMode.HTML)

  try:
    return edit_message()
  except Exception as inst:
    match = REGEX_FLOOD_WAIT_X_ERROR.match( inst.args[0] )
    if match:
      sleep( int(match.group(1)) )
      return edit_message()

def handler_command_plp(client, update, cmd_args):
  if is_newmessage_from_self(update):
    return exec_command_plp(client, update.message)


########################################################
######################### 'as' #########################
########################################################
def exec_command_as(client, message:types.Message):
  chat_id = message.to_id.user_id if isinstance(message.to_id, types.PeerUser) else message.to_id.channel_id
  try:
    m = re.match(r'[^\s]+\s([^\s]+)\s(.+)', message.message) ## TODO: tratar casos onde o link começa e termina com aspas
    if m:
      msg_result = f'<a href="{m.group(1)}">{m.group(2)}</a>'
      client.edit_message_text(chat_id, message.id, msg_result, ParseMode.HTML)
  except Exception as inst:
    print(inst)
    return

def handler_command_as(client, update, *args):
  if is_newmessage_from_self(update):
    return exec_command_as(client, update.message)
