from telegram.ext import CommandHandler, run_async
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot import LOGGER, dispatcher
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands


@run_async
def list_drive(update, context):
    if update.message.text == f'/{BotCommands.ListCommand}':
        sendMessage(f'Send a search key along with {BotCommands.ListCommand} command', context.bot, update)
    else:
        search = update.message.text.split(' ', maxsplit=1)[1]
        LOGGER.info(f"Searching: '{search}'...")
        reply = sendMessage('Searching..... Please Wait!', context.bot, update)
        gdrive = GoogleDriveHelper(None)
        msg, button = gdrive.drive_list(search)
        if msg:
            if button:
                editMessage(msg, reply, button)
            else:
                editMessage(msg, reply)
        else:
            editMessage('No results found', reply)
        # if not USE_TELEGRAPH:
        #     threading.Thread(target=auto_delete_message, args=(context.bot, update.message, reply)).start()


list_handler = CommandHandler(BotCommands.ListCommand, list_drive, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
dispatcher.add_handler(list_handler)
