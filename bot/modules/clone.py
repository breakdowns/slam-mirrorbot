from telegram.ext import CommandHandler
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.ext_utils.bot_utils import new_thread
from bot import dispatcher, LOGGER


@new_thread
def cloneNode(update,context):
    if update.message.from_user.last_name:
        last_name = f" {update.message.from_user.last_name}"
    else:
        last_name = ""
    if update.message.from_user.username:
        username = f"@{update.message.from_user.username}"
    else:
        username = ""
    name = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}{last_name}</a>'

    args = update.message.text.split(" ",maxsplit=1)
    if len(args) > 1:
        link = args[1]
        msg = f'Cloning...\n' \
              f'User: {username}\n' \
              f'Link: <a href="{link}">{link}</a>'
        sendMessage(msg, context.bot, update)
        gd = GoogleDriveHelper()
        result, button = gd.clone(link)
        LOGGER.info('ID: {} - Username: {} - Message: {}'.format(update.message.chat.id,update.message.chat.username,update.message.text))
        # deleteMessage(context.bot,msg)
        sendMarkup(result,context.bot,update,button)
    else:
        sendMessage("Provide G-Drive Shareable Link to Clone.",context.bot,update)

clone_handler = CommandHandler(BotCommands.CloneCommand,cloneNode,filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
dispatcher.add_handler(clone_handler)
