from telegram.ext import CommandHandler, run_async
from bot.helper.mirror_utils.upload_utils.gdriveTools import GoogleDriveHelper
from bot.helper.telegram_helper.message_utils import sendMarkup, deleteMessage, sendMessage
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import dispatcher, CLONE_LIMIT


@run_async
def cloneNode(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    if len(args) > 1:
        link = args[1]
        gd = GoogleDriveHelper()
        if CLONE_LIMIT is not None:
            mssg = sendMessage(f"Checking The Size...", context.bot, update)
            limit = CLONE_LIMIT
            limit = limit.split(' ', maxsplit=1)
            limitint = int(limit[0])
            res, clonesizelimit = gd.count(link)
            if clonesizelimit != "":
                msgg = f'Failed, Clone limit is {CLONE_LIMIT}'
                if 'GB' in limit or 'gb' in limit:
                    if clonesizelimit > limitint * 1024**3:
                        deleteMessage(context.bot, mssg)
                        sendMessage(msgg, context.bot, update)
                        return
                    else:
                        deleteMessage(context.bot, mssg)
                elif 'TB' in limit or 'tb' in limit:
                    if clonesizelimit > limitint * 1024**4:
                        deleteMessage(context.bot, mssg)
                        sendMessage(msgg, context.bot, update)
                        return
                    else:
                        deleteMessage(context.bot, mssg)
            else:
                deleteMessage(context.bot, mssg)
                sendMessage(res, context.bot, update)
                return
        msg = sendMessage(f"Cloning: <code>{link}</code>", context.bot, update)
        result, button = gd.clone(link)
        deleteMessage(context.bot, msg)
        if button == "":
            sendMessage(result, context.bot, update)
        else:
            if update.message.from_user.username:
                uname = f'@{update.message.from_user.username}'
            else:
                uname = f'<a href="tg://user?id={update.message.from_user.id}">{update.message.from_user.first_name}</a>'
            if uname is not None:
                cc = f'\n\n#cc: {uname}'
            sendMarkup(result + cc, context.bot, update, button)
    else:
        sendMessage('Provide G-Drive Shareable Link to Clone.', context.bot, update)

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)
dispatcher.add_handler(clone_handler)
