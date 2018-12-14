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


########################################################
######################### 'as' #########################
## TODO: sanitizar o texto (remover tags HTML)        ##
########################################################
def exec_command_as(client, message:types.Message, cmd_args):
  url, text = cmd_args.split(' ', 1)

  chat_id = message.to_id.user_id if isinstance(message.to_id, types.PeerUser) else message.to_id.channel_id
  try:
    msg_result = f'<a href="{url}">{text}</a>'
    client.edit_message_text(chat_id, message.id, msg_result, ParseMode.HTML)
    print(msg_result)
  except Exception as inst:
    print(inst)
    return client.delete_messages(chat_id, [message.id], True)

def handler_command_as(client, update, cmd_args):
  if is_newmessage_from_self(update):
    return exec_command_as(client, update.message, cmd_args)
