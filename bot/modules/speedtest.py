import speedtest

from bot.helper.telegram_helper.filters import CustomFilters
from bot import dispatcher, AUTHORIZED_CHATS
from bot.helper.telegram_helper.bot_commands import BotCommands
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CallbackContext, Filters, run_async, CommandHandler


@run_async
def speedtst(update, context):
    message = update.effective_message
    ed_msg = message.reply_text("Running Speed Test . . . ")
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()
    context.bot.editMessageText(
        "Download Speed: "
        f"{speed_convert(result['download'])}\n"
        "Upload Speed: "
        f"{speed_convert(result['upload'])}\n"
        "Ping: "
        f"{result['ping']}\n"
        "ISP: "
        f"{result['client']['isp']}",
        update.effective_chat.id,
        ed_msg.message_id,
    )

def speed_convert(size):
    """Hi human, you can't read bytes?"""
    power = 2 ** 10
    zero = 0
    units = {0: "", 1: "Kb/s", 2: "Mb/s", 3: "Gb/s", 4: "Tb/s"}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


SPEED_HANDLER = CommandHandler(BotCommands.SpeedCommand, speedtst, 
                                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user)

dispatcher.add_handler(SPEED_HANDLER)
