from pyrogram.api import types, functions, errors
from pyrogram.api.types import InputPeerSelf
from requests import get as HTTP_GET
from bs4 import BeautifulSoup


## https://docs.pyrogram.ml/types/UpdateNewMessage
## https://docs.pyrogram.ml/types/UpdateEditMessage
def is_newmessage_from_self(update:types.UpdateNewMessage or types.UpdateEditMessage) -> bool:
  """Verifica se a atualização é de uma mensagem (enviada ou editada) do próprio usuário Client."""
  return update.message.out or (isinstance(update.message.to_id, types.PeerUser) and update.message.from_id == update.message.to_id.user_id)


## https://docs.pyrogram.ml/functions/messages/DeleteHistory
def clear_history(client, peer_id:int or str) -> types.messages.AffectedHistory:
  try:
    cls_chat_id = client.resolve_peer(peer_id)
    return client.send(
      functions.messages.DeleteHistory(cls_chat_id, max_id=0)
    )
  except Exception as err:
    print(clear_history.__name__, err)
    return None


## https://github.com/pyrogram/pyrogram/blob/a961eb88db115ca0516df935eef0f2a07e5ff221/pyrogram/client/style/markdown.py#L54
## https://github.com/pyrogram/pyrogram/blob/027f843047cc9766c9498d4c66f4d17efe801cc6/pyrogram/client/client.py#L236
## https://t.me/PyrogramChat/4985
def is_not_foreign_user(client, peer_id:str or int) -> bool:
  return peer_id in (
    client.peers_by_username if type(peer_id) is str
                             else client.peers_by_id
  )
  # try:
  #   return isinstance(
  #     client.resolve_peer(peer_id), types.InputPeerUser
  #   )
  # except Exception as err:
  #   return False


## https://docs.pyrogram.ml/types/UpdateNewMessage
def get_first_x_on_update(client, update:types.Update, typex):
  return next((x for x in update.updates if type(x) == typex), None)

def message_has_media(message:types.Message) -> bool:
  return hasattr(message, 'media') and message.media != None

def message_has_link(message:types.Message) -> bool:
  return 'https://' in message.message or 'http://' in message.message


def parse_usernames(users, separator:str='\n') -> str:
  return separator.join([ user['username'] for user in users ])

## https://docs.pyrogram.ml/functions/channels/GetParticipants
def get_chat_admins(client, chat_id:int) -> list:
  users = client.send(
    functions.channels.GetParticipants(
      channel=client.resolve_peer(chat_id),
      filter=types.ChannelParticipantsAdmins(),
      offset=0,
      limit=5,
      hash=0
    )
  ).users

  return [ {'username':'@' + user.username, 'status':user.status} for user in users if user.username and user.status ]

def filter_users_with_status(users, tuple_types=()) -> list:
  return list( filter(lambda u: isinstance(u['status'], tuple_types), users) ) if tuple_types else users


def get_last_announcement_sites_google(project_name):
  def formatar_data(str_data):
    if (str_data is None):
      return str_data

    [dia, _, mes, _, ano, hora] = str_data.split(' ')
    return '{}/{}/{} ({})'.format(dia, mes, ano, hora)

  BASE_URL = 'https://sites.google.com'
  url = BASE_URL + '/site/' + project_name + '/classroom-news'
  page = HTTP_GET(url)
  soup = BeautifulSoup(page.text, 'html.parser')

  el_last_announcement = soup.find(class_='announcement')
  el_timestamp = el_last_announcement.find(class_='timestamp')
  el_updatedTime = el_timestamp.find(class_='updatedTime')

  el_title = el_last_announcement.h4

  return {
    'title': el_title.a.text,
    'link': BASE_URL + el_title.a['href'],
    'publish_date': formatar_data( el_timestamp.span.text ),
    'updated_date': formatar_data( el_updatedTime.span.text )
  }
