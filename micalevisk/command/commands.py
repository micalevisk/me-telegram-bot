from micalevisk.utils import *
from pyrogram import ParseMode
import re


############################################################
######################### 'admins' #########################
## TODO: implementar comandos auxiliares: !report !ignore ##
############################################################
def get_quote_admins(client, chat_id:int) -> str:
  admins = get_chat_admins(client, chat_id)
  valid_admins = filter_users_with_status(admins, (types.UserStatusOnline, types.UserStatusRecently)) or admins
  return parse_usernames(valid_admins) if valid_admins else ''

def exec_command_admins(client, message:types.Message):
  chat_id = message.to_id.channel_id
  cmd_response_msg = get_quote_admins(client, chat_id)
  return client.edit_message_text(chat_id, message.id, cmd_response_msg) if cmd_response_msg else client.delete_messages(chat_id, [message.id], True)

def handler_command_admins(client, update, *args):
  return exec_command_admins(client, update.message)


##########################################################
######################### 'tags' #########################
## TODO: unique hashtags                                ##
##########################################################
REGEX_HASHTAGS = re.compile('\B(#\w+)')
def exec_command_tags(client, message:types.Message):
  chat_id = 'me'
  client.edit_message_text(chat_id, message.id, 'executando...')

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

def handler_command_tags(client, update, *args):
  if is_newmessage_from_self(update):
    return exec_command_tags(client, update.message)


#########################################################
######################### 'plp' #########################
#########################################################
def exec_command_plp(client, message:types.Message):
  chat_id = message.to_id.user_id if isinstance(message.to_id, types.PeerUser) else message.to_id.channel_id
  client.edit_message_text(chat_id, message.id, 'executando...')

  ultimo_anuncio = get_last_announcement_sites_google('plpicompufam2018periodo2')
  if (ultimo_anuncio is None):
    return client.delete_messages(chat_id, [message.id], True)

  msg_result = '<b>{publish_date}</b>\n<a href="{link}">{title}</a> '.format(**ultimo_anuncio)
  return client.edit_message_text(chat_id, message.id, msg_result,  ParseMode.HTML)

def handler_command_plp(client, update, *args):
  if is_newmessage_from_self(update):
    return exec_command_plp(client, update.message)
