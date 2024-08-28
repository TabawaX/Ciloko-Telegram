import platform
import psutil
import time
import json
import os
import re
from telegram.ext import CommandHandler

GROUP_DB_FILE = 'databases/group.json'


def load_group_db():
    if os.path.exists(GROUP_DB_FILE):
        with open(GROUP_DB_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_group_db(data):
    with open(GROUP_DB_FILE, 'w') as file:
        json.dump(data, file, indent=4)

async def start(update, context):
    await update.message.reply_text('Sekai Network Here!!.')

async def enter_group(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /enter [invitation_link]")
        return

    invitation_link = context.args[0]
    if not re.match(r'^https://t.me/joinchat/[A-Za-z0-9_-]+$', invitation_link):
        await update.message.reply_text("Invalid invitation link.")
        return

    await update.message.reply_text(f"Invitation link received: {invitation_link}")

async def get_chat_id(update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID: {chat_id}")

async def set_welcome(update, context):
    if context.args and context.args[0].lower() in ['on', 'off']:
        status = context.args[0].lower() == 'on'
        group_db = load_group_db()
        chat_id = str(update.effective_chat.id)
        if chat_id in group_db:
            group_db[chat_id]['welcome'] = status
        else:
            group_db[chat_id] = {'welcome': status, 'id_topic': None, 'welcome_message': 'Welcome {name} to the group!', 'goodbye_message': 'Goodbye {name}!'}
        save_group_db(group_db)
        await update.message.reply_text(f"Welcome messages are now {'enabled' if status else 'disabled'}.")
    else:
        await update.message.reply_text("Usage: /welcome [on|off]")

async def set_welcome_channel(update, context):
    if context.args:
        channel_id = context.args[0]
        group_db = load_group_db()
        chat_id = str(update.effective_chat.id)
        if chat_id in group_db:
            group_db[chat_id]['id_topic'] = channel_id
        else:
            group_db[chat_id] = {'welcome': False, 'id_topic': channel_id, 'welcome_message': 'Welcome {name} to the group!', 'goodbye_message': 'Goodbye {name}!'}
        save_group_db(group_db)
        await update.message.reply_text(f"Welcome channel set to {channel_id}.")
    else:
        await update.message.reply_text("Usage: /welcome_channel [channel_id]")

async def set_welcome_message(update, context):
    if context.args:
        message = ' '.join(context.args)
        group_db = load_group_db()
        chat_id = str(update.effective_chat.id)
        if chat_id in group_db:
            group_db[chat_id]['welcome_message'] = message
        else:
            group_db[chat_id] = {'welcome': False, 'id_topic': None, 'welcome_message': message, 'goodbye_message': 'Goodbye {name}!'}
        save_group_db(group_db)
        await update.message.reply_text(f"Welcome message updated.")
    else:
        await update.message.reply_text("Usage: /welcome_message [message]")

async def set_goodbye_message(update, context):
    if context.args:
        message = ' '.join(context.args)
        group_db = load_group_db()
        chat_id = str(update.effective_chat.id)
        if chat_id in group_db:
            group_db[chat_id]['goodbye_message'] = message
        else:
            group_db[chat_id] = {'welcome': False, 'id_topic': None, 'welcome_message': 'Welcome {name} to the group!', 'goodbye_message': message}
        save_group_db(group_db)
        await update.message.reply_text(f"Goodbye message updated.")
    else:
        await update.message.reply_text("Usage: /goodbye_message [message]")

async def goodbye(update, context):
    if update.message.chat.type in ['group', 'supergroup']:
        if update.message.left_chat_member:
            group_db = load_group_db()
            chat_id = str(update.effective_chat.id)
            goodbye_message = group_db.get(chat_id, {}).get('goodbye_message', 'Goodbye {name}!')
            goodbye_message = goodbye_message.format(name=update.message.left_chat_member.full_name)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=goodbye_message)

async def ping(update, context):
    start_time = time.time()
    await update.message.reply_text('Pong!')
    end_time = time.time()
    ping_time = (end_time - start_time) * 1000  
    await update.message.reply_text(f'Ping: {ping_time:.2f} ms')

async def info(update, context):
    uname = platform.uname()
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)

    info_message = (
        f"System: {uname.system}\n"
        f"Node Name: {uname.node}\n"
        f"Release: {uname.release}\n"
        f"Version: {uname.version}\n"
        f"Machine: {uname.machine}\n"
        f"Processor: {uname.processor}\n\n"
        f"CPU Usage: {cpu}%\n"
        f"Total Memory: {mem.total / (1024 ** 3):.2f} GB\n"
        f"Available Memory: {mem.available / (1024 ** 3):.2f} GB\n"
        f"Used Memory: {mem.used / (1024 ** 3):.2f} GB\n"
        f"Memory Usage: {mem.percent}%"
    )

    await update.message.reply_text(info_message)

def get_command_handlers():
    return [
        CommandHandler('start', start),
        CommandHandler('ping', ping),
        CommandHandler('info', info),
        CommandHandler('welcome', set_welcome),
        CommandHandler('welcome_channel', set_welcome_channel),
        CommandHandler('welcome_message', set_welcome_message),
        CommandHandler('goodbye_message', set_goodbye_message),
        CommandHandler('goodbye', goodbye),
        CommandHandler('enter', enter_group),
        CommandHandler('get_chat_id', get_chat_id),
    ]