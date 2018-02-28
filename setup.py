## https://docs.pyrogram.ml
## https://core.telegram.org/methods
from pyrogram.api import types, functions
from micalevisk import *
import sys
from xclient import XClient

## https://docs.pyrogram.ml/pyrogram/Client/#pyrogram.Client.send_message
def handler_action_auto_reply(client, message:types.Message):
  try:
    chat_history = client.send(
      functions.messages.GetHistory(
        client.peers_by_id[message.from_id], 0, 0, 0, 5, 0, 0, 0
      )
    )

    if len(chat_history.messages) <= 1: ## XXX: a lógica admite que um foreign user não enviará mais de 1 menssagens de uma vez
      client.send_message(message.from_id, '**eo**', reply_to_message_id=message.id)
      return client.send( functions.account.UpdateStatus(offline=True) ) ## deixa o client offline
  except Exception as err:
    print(handler_action_auto_reply.__name__, err, file=sys.stderr)#§


## https://docs.pyrogram.ml/types/Update
def update_handler(client, update, users, chats):
  commands_switcher_func_args = [client, update] ## TODO: incluir os demais parâmetros

  ## handling private messages or edit messages
  ## https://docs.pyrogram.ml/types/UpdateNewMessage
  ## https://docs.pyrogram.ml/types/UpdateEditMessage
  if isinstance(update, types.UpdateNewMessage) or isinstance(update, types.UpdateEditMessage):
    message = update.message

    if not isinstance(message, types.Message): return

    if isinstance(message.to_id, types.PeerUser):
      if is_newmessage_from_self(update):
        if command.msg_with_cmd_style(message.message):
          return command.listener(message.message, commands_switcher_func_args)
      elif not users[message.from_id].bot:
        return handler_action_auto_reply(client, message)
    return

  ## handling channels edit messages
  ## https://docs.pyrogram.ml/types/UpdateNewChannelMessage
  if isinstance(update, types.UpdateEditChannelMessage):
    message = update.message

    if isinstance(message, types.Message) and command.msg_with_cmd_style(message.message):
      return command.listener(message.message, commands_switcher_func_args)

  ## handling channels updates
  ## https://docs.pyrogram.ml/types/UpdateNewChannelMessage
  if isinstance(update, types.UpdateNewChannelMessage):
    message = update.message
    if not isinstance(message.to_id, types.PeerChannel): return

    ## handling 'join' messages
    ## TODO: implementar handler obedecendo ao algoritmo do 'suspect spam'
    if isinstance(message, types.MessageService):
      if isinstance(message.action, types.MessageActionChatAddUser):
        users_joined = message.action.users
        return

    ## handling channel messages
    if not isinstance(message, types.Message): return
    if command.msg_with_cmd_style(message.message):
      return command.listener(message.message, commands_switcher_func_args)

    ## handling 'forward' messages (except from myself)
    ## TODO: implementar handler obedecendo ao algoritmo do 'suspect spam'
    elif message.fwd_from:
      fwd_message_id = message.id
      from_user_id = message.from_id
      to_channel_id = message.to_id.channel_id
      # client.forward_messages('me', to_channel_id, [ fwd_message_id ])
      return




if __name__ == '__main__':
  try:
    client = XClient(session_name='me_bot')
    client.set_update_handler(update_handler)

    client.start()

    client.idle()
    # client.stop()
  except Exception as err:
    print('[MAIN ERROR]', err, file=sys.stderr)#§
