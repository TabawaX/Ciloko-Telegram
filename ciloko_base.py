import logging
from telegram.ext import MessageHandler, filters
from admin import welcome_enabled
import json
import os

GROUP_DB_FILE = 'databases/group.json'

def load_group_db():
    if os.path.exists(GROUP_DB_FILE):
        with open(GROUP_DB_FILE, 'r') as file:
            return json.load(file)
    return {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def welcome(update, context):
    if update.message.chat.type in ['group', 'supergroup']:
        group_db = load_group_db()
        chat_id = str(update.effective_chat.id)
        if chat_id in group_db and group_db[chat_id].get('welcome', False):
            new_members = update.message.new_chat_members
            for member in new_members:
                welcome_message = group_db.get(chat_id, {}).get('welcome_message', 'Welcome {name} to the group!')
                welcome_message = welcome_message.format(name=member.full_name)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)
                logger.info(f"Sent welcome message to {member.full_name} in chat {chat_id}")

async def goodbye(update, context):
    if update.message.chat.type in ['group', 'supergroup']:
        if update.message.left_chat_member:
            chat_id = str(update.effective_chat.id)
            goodbye_message = group_db.get(chat_id, {}).get('goodbye_message', 'Goodbye {name}!')
            goodbye_message = goodbye_message.format(name=update.message.left_chat_member.full_name)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=goodbye_message)
            logger.info(f"Sent goodbye message to {update.message.left_chat_member.full_name} in chat {chat_id}")

async def log_message(update, context):
    user = update.message.from_user
    username = user.username or user.first_name
    user_id = user.id
    message_text = update.message.text
    
    logger.info(f"User: {username} (ID: {user_id}) sent a message: {message_text}")

def get_handlers():
    return [
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome),
        MessageHandler(filters.TEXT & ~filters.COMMAND, log_message),
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye),
    ]