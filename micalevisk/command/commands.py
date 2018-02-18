from micalevisk.utils import *


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

def handler_command_admins(client, update):
  if not is_newmessage_from_self(update):
    return exec_command_admins(client, update.message)
