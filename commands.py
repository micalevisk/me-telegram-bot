import os
import traceback
import logging
import re
from pyrogram import Client
import pyrogram.filters as Filter
from tinydb import TinyDB, where
from configparser import ConfigParser
from functools import wraps

def restrict(filters=None):
  def add_filters(message_handler):
    @wraps(message_handler)
    def message_handler_with_filters(*args, **kwargs):
      return message_handler(*args, **kwargs)

    ## Attach metadata
    message_handler_with_filters.filters = filters
    return message_handler_with_filters

  return add_filters


def command(cmd: str, low_level = False):

  def wraps_message_handler(command_handler):
    @wraps(command_handler)
    def safe_message_handler(client, msg):
      try:
        command_handler(client, msg)
      except Exception as e:
        client.delete_messages(msg.chat.id, msg.message_id)
        logging.error(traceback.format_exc())

    safe_message_handler.cmd = cmd
    safe_message_handler.deferred = False
    return safe_message_handler


  def wraps_deferred_message_handler(deferred_command_handler):
    @wraps(deferred_command_handler)
    def safe_message_handler(app: Client):
      message_handler = deferred_command_handler(app)
      return wraps_message_handler(message_handler)

    safe_message_handler.cmd = cmd
    safe_message_handler.deferred = True
    return safe_message_handler

  return wraps_deferred_message_handler if low_level else wraps_message_handler

####################################
############# 'admins' #############
####################################
METION_MARKDOWN="[{text}](tg://user?id={user_id})"
METION_HTML="<a href='tg://user?id={user_id}'>{text}</a>"

def get_mention_format(user, parse_mode="md"):
  username = user.username
  first_name = user.first_name

  if parse_mode == "md":
    if username:
      return METION_MARKDOWN.format(text=f"@{username}", user_id=user.id)
    if first_name:
      return METION_MARKDOWN.format(text=f"{first_name}", user_id=user.id)

  elif parse_mode == "html":
    if username:
      return METION_HTML.format(text=f"@{username}", user_id=user.id)
    if first_name:
      return METION_HTML.format(text=f"{first_name}", user_id=user.id)

  return ''

@command('admins', True)
def command_lowlevel__admins(app: Client):
  open_db = lambda: TinyDB("admins-reports.json")

  @app.on_deleted_messages() ## Is only one `on_deleted_messages` handler in app instance
  def handler_delete_message(client, msgs):
    reply_message_ids = [ msg.message_id for msg in msgs ]
    if len(reply_message_ids) <= 0:
      return

    db = open_db()
    db_report_msgs = db.search( where('reply_to_message_id').one_of(reply_message_ids) )
    if len(db_report_msgs) <= 0:
      return

    db_message_id_to_remove = []

    for db_report_msg in db_report_msgs:
      try:
        # TODO: group messages by `chat_id` so this delete operation will be perfomed only once in some cases
        client.delete_messages(db_report_msg['chat_id'], db_report_msg['message_id'])
        db_message_id_to_remove.append(db_report_msg['message_id'])
      except Exception as err:
        print(err)
        pass

    try:
      db.remove( where('message_id').one_of(db_message_id_to_remove) )
    except Exception as err:
      print(err)
      pass

  @restrict( Filter.group )
  def command__admins(client, msg):
    chat_id = msg.chat.id
    message_id = msg.message_id
    msg_id_reply = msg.reply_to_message.message_id if (msg.reply_to_message is not None) else None
    admins_mentions = []

    client.edit_message_text(chat_id, message_id, '`...`', parse_mode="md")#§

    for member in client.iter_chat_members(chat_id, filter="administrators"):
      user = member.user
      if not user.is_bot and not user.is_self:
        if user.username:
          admins_mentions.append( get_mention_format(user, parse_mode="md") )

    if len(admins_mentions) <= 0:
      client.delete_messages(chat_id, message_id)
      return

    try:
      new_text = '\n'.join(admins_mentions)
      if msg_id_reply:
        db = open_db()
        db.insert({ 'chat_id': chat_id, 'message_id': message_id, 'reply_to_message_id': msg_id_reply })

      client.edit_message_text(chat_id, message_id, new_text, parse_mode="md")
    except:
      client.delete_messages(chat_id, message_id)

  return command__admins


#############################################
############# 'as <url> <text>' #############
#############################################
@command('as')
def command__as(client, msg):
  (url, text) = msg.command[1:]
  msg_result = f"<a href='{url}'>{text}</a>"

  try:
    client.edit_message_text(
      msg.chat.id, msg.message_id, msg_result,
      parse_mode="html", disable_web_page_preview=True)
  except:
    client.delete_messages(msg.chat.id, msg.message_id)


##################################
############# 'help' #############
##################################
@restrict( Filter.chat('me') )
@command('help')
def command__help(client, msg):
  available_commands = '\n'.join([
    'admins',
    'as <url> <text>',
    'help',
    'ping',
    'rm <number-of-messages>',
    'tags',
    't <emote-name>',
    'vaga'
  ])

  msg_result = f"<code>{available_commands}</code>"
  client.edit_message_text(msg.chat.id, msg.message_id, msg_result, "html")


##################################
############# 'ping' #############
##################################
@command('ping')
def command__ping(client, msg):
  client.delete_messages(msg.chat.id, msg.message_id)


#####################################################
############# 'rm <number-of-messages>' #############
#####################################################
@command('rm')
def command__rm(client, msg):
  chat_id = msg.chat.id
  number_of_messages = int( msg.command[1] ) + 1
  number_of_messages_to_fetch = number_of_messages * 2
  message_ids = []

  for message in client.iter_history(chat_id, reverse=False, limit=number_of_messages_to_fetch):
    if len(message_ids) >= number_of_messages: break
    if message.from_user != None and message.from_user.is_self:
      message_ids.append(message.message_id)

  client.delete_messages(chat_id, message_ids)


##################################
############# 'tags' #############
##################################
REGEX_HASHTAGS = re.compile(r'\B(#\w+)')

@restrict( Filter.chat('me') )
@command('tags')
def command__tags(client, msg):
  chat_id = msg.chat.id
  message_id = msg.message_id
  tags = []

  client.edit_message_text(chat_id, message_id, '`...`', parse_mode="md")#§

  for message in client.iter_history(chat_id):
    tags.extend( set(re.findall(REGEX_HASHTAGS, message.text)) )

  if len(tags) > 0:
    new_text = '\n'.join( set(tags) )
    try:
      client.edit_message_text(chat_id, message_id, new_text, parse_mode="md")
    except:
      client.delete_messages(chat_id, message_id)
  else:
    client.delete_messages(chat_id, message_id)


##############################################
############## 't <emote-name>' ##############
##############################################
stickers_id = ConfigParser()
stickers_id.read('stickers_file_id.ini')
if not stickers_id.has_section('twitch_stickers'):
  raise LookupError('There is no "twitch_stickers" section on the file "stickers_file_id.ini"')

@command('t')
def command__t(client, msg):
  chat_id = msg.chat.id
  emote_name = msg.command[1]
  client.delete_messages(chat_id, msg.message_id)

  if stickers_id.has_option('twitch_stickers', emote_name):
    file_id = stickers_id.get('twitch_stickers', emote_name)
    msg_id_reply = msg.reply_to_message.message_id if (msg.reply_to_message is not None) else None
    client.send_sticker(chat_id, file_id,
      reply_to_message_id=msg_id_reply,disable_notification=False)


##################################
############# 'vaga' #############
##################################
CHAT_ID_TO_FORWARD_VAGA=os.getenv("CHAT_ID_TO_FORWARD_VAGA")
MSG_ON_FORWARD_VAGA=os.getenv("MSG_ON_FORWARD_VAGA")
if CHAT_ID_TO_FORWARD_VAGA != None and MSG_ON_FORWARD_VAGA != None:
  @command('vaga')
  def command__vaga(client, msg):
    chat_id = msg.chat.id
    message_id = msg.message_id

    msg_reply = msg.reply_to_message
    if msg_reply is not None:
      author_mention = get_mention_format(msg_reply.from_user, parse_mode="md")

      try:
        msg_reply.forward(CHAT_ID_TO_FORWARD_VAGA)
        new_text = author_mention + ' ' + MSG_ON_FORWARD_VAGA
        client.edit_message_text(chat_id, message_id, new_text, parse_mode="md", disable_web_page_preview=True)
        client.delete_messages(chat_id, msg_reply.message_id)
      except:
        ## Ignore errors
        pass

