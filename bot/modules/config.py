# Implement by https://github.com/jusidama18
# Based on this https://github.com/DevsExpo/FridayUserbot/blob/master/plugins/heroku_helpers.py

import os
import time
import heroku3

from functools import wraps

from pyrogram import Client, filters, types, emoji
from pyrogram.types import Message
from bot import app, HEROKU_API_KEY, HEROKU_APP_NAME, OWNER_ID
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import *

# Setting Message

def get_text(message: Message) -> [None, str]:
    """Extract Text From Commands"""
    text_to_return = message.text
    if message.text is None:
        return None
    if " " in text_to_return:
        try:
            return message.text.split(None, 1)[1]
        except IndexError:
            return None
    else:
        return None

# Preparing

heroku_client = None
if HEROKU_API_KEY:
    heroku_client = heroku3.from_key(HEROKU_API_KEY)

def _check_heroku(func):
    @wraps(func)
    async def heroku_cli(client, message):
        heroku_app = None
        if not heroku_client:
            await message.reply_text("`Please Add HEROKU_API_KEY Key For This To Function To Work!`", parse_mode="markdown")
        elif not HEROKU_APP_NAME:
            await message.reply_text("`Please Add HEROKU_APP_NAME For This To Function To Work!`", parse_mode="markdown")
        if HEROKU_APP_NAME and heroku_client:
            try:
                heroku_app = heroku_client.app(HEROKU_APP_NAME)
            except:
                await message.reply_text(message, "`Heroku Api Key And App Name Doesn't Match!`", parse_mode="markdown")
            if heroku_app:
                await func(client, message, heroku_app)

    return heroku_cli

# Add Variable

@app.on_message(filters.command('setvar') & filters.user(OWNER_ID))
@_check_heroku
async def set_varr(client, message, app_):
    msg_ = await message.reply_text("`Please Wait!`")
    heroku_var = app_.config()
    _var = get_text(message)
    if not _var:
        await msg_.edit("`Here is Usage Syntax : .setvar KEY VALUE`", parse_mode="markdown")
        return
    if not " " in _var:
        await msg_.edit("`Here is Usage Syntax : .setvar KEY VALUE`", parse_mode="markdown")
        return
    var_ = _var.split(" ", 1)
    if len(var_) > 2:
        await msg_.edit("`Here is Usage Syntax : .setvar KEY VALUE`", parse_mode="markdown")
        return
    _varname, _varvalue = var_
    await msg_.edit(f"`Variable {_varname} Added With Value {_varvalue}!`")
    heroku_var[_varname] = _varvalue

# Delete Variable
        
@app.on_message(filters.command('delvar') & filters.user(OWNER_ID))
@_check_heroku
async def del_varr(client, message, app_):
    msg_ = await message.reply_text("`Please Wait!`", parse_mode="markdown")
    heroku_var = app_.config()
    _var = get_text(message)
    if not _var:
        await msg_.edit("`Give Var Name As Input!`", parse_mode="markdown")
        return
    if not _var in heroku_var:
        await msg_.edit("`This Var Doesn't Exists!`", parse_mode="markdown")
        return
    await msg_.edit(f"`Sucessfully Deleted {_var} Var!`", parse_mode="markdown")
    del heroku_var[_var]

# CONFIG LIST #

__header__='📕 **Page** **{}**\n\n'

@app.on_message(filters.command(BotCommands.ConfigMenuCommand) & filters.user(OWNER_ID))
async def config_menu(_, message):
    await message.reply(
        f"**Hello {message.from_user.mention}**,\n\n**If you want to add or set Variable in Heroku use** `/setvar`\n\n**If you want to delete Variable in Heroku use `/delvar`**\n\n**WARNING ! Very Recommended to do this command in private since it's contain bot info.**\n\n**Here's This is MirrorBot Current Configs**",
        reply_markup=types.InlineKeyboardMarkup(
            [[types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'), types.InlineKeyboardButton(f"BOT CONFIG", callback_data='docs_1')]]
        )
    )

@app.on_callback_query(filters.regex('^docs_'))
async def config_button(_, query):
    data = query.data.split('_')[1]
    if data == '1':
        return await query.message.edit(
            __header__.format(data)
            + f"**[ Telegram Config ]**\n\n**Bot Token :** `{BOT_TOKEN}`\n\n**Telegram API :** `{TELEGRAM_API}`\n\n**Telegram HASH :** `{TELEGRAM_HASH}`\n\n**Telegraph Token** `{telegraph_token}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_9'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_2')
                    ]
                ]
            )
        )
    elif data == '2':
        return await query.message.edit(
            __header__.format(data)
            + f"**[ Drive and Index Config ]**\n**Drive Folder :** `{parent_id}`\n\n**Using Team Drive :** `{IS_TEAM_DRIVE}`\n\n**Using Service Account :** `{USE_SERVICE_ACCOUNTS}`\n\n**Index Url :** `{INDEX_URL}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_1'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_3')
                    ]
                ]
            )
        )
    elif data == '3':
        return await query.message.edit(
            __header__.format(data)
            + f"**[ Mega and Uptobox Config ]**\n\n**Mega API :** `{MEGA_API_KEY}`\n\n**Mega Email :** `{MEGA_EMAIL_ID}`\n\n**Mega Password :** `{MEGA_PASSWORD}`\n\n**Uptobox Token :** `{UPTOBOX_TOKEN}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_2'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_4')
                    ]
                ]
            )
        )
    elif data == '4':
        return await query.message.edit(
            __header__.format(data)
            + f"**[ Stop Duplicate Config ]**\n\n**Mirror :** `{STOP_DUPLICATE_MIRROR}`\n\n**Clone :** `{STOP_DUPLICATE_CLONE}`\n\n**Mega :** `{STOP_DUPLICATE_MEGA }`\n\n**[ Block Mega Config ]**\n\n**Folder :** `{BLOCK_MEGA_FOLDER}`\n\n**Link :** `{BLOCK_MEGA_LINKS}`\n\n",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_3'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_5')
                    ]
                ]
            )
        )
    elif data == '5':
        return await query.message.edit(
            __header__.format(data)
            + f"**[ Limit Size Config ]**\n\n**Torrent and Direct :** `{TORRENT_DIRECT_LIMIT}`\n\n**Clone :** `{CLONE_LIMIT}`\n\n**Mega :** `{MEGA_LIMIT}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_4'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_6')
                    ]
                ]
            )
        )
    elif data == '6':
        user = sudo = ''
        user += '\n'.join(str(id) for id in AUTHORIZED_CHATS)
        sudo += '\n'.join(str(id) for id in SUDO_USERS)
        return await query.message.edit(
            __header__.format(data)
            + f"**[ User ID Config ]**\n\n**Owner ID :** `{OWNER_ID}`\n\n**Authorized Chat :**\n`{user}`\n\n**Sudo Users :**\n`{sudo}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_5'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_7')
                    ]
                ]
            )
        )
    elif data == '7':
        return await query.message.edit(
            __header__.format(data)
            + f"**[ Button Config ]**\n\n**Button Four Name :** `{BUTTON_FOUR_NAME}`\n\n**Button Four Url :** `{BUTTON_FOUR_URL}`\n\n**Button Five Name :** `{BUTTON_FIVE_NAME}`\n\n**Button Five Url :** `{BUTTON_FIVE_URL}`\n\n**Button Six Name :** `{BUTTON_SIX_NAME}`\n\n**Button Six Url :** `{BUTTON_SIX_URL}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_6'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_8')
                    ]
                ]
            )
        )
    elif data == '8':
        return await query.message.edit(
            __header__.format(data)
            + f"**[ Heroku Config ]**\n\n**Heroku Name :** `{HEROKU_APP_NAME}`\n\n**Heroku API :** `{HEROKU_API_KEY}`\n\n**[ Shortener Config ]**\n\n**Shortener Name :** `{SHORTENER}`\n\n**Shortener API :** `{SHORTENER_API}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_7'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_9')
                    ]
                ]
            )
        )
    elif data == '9':
        return await query.message.edit(
            __header__.format(data)
            + f" **[ Others Config ]**\n\n**Ignore Pending Request :** `{IGNORE_PENDING_REQUESTS}`\n\n**Image Url :** `{IMAGE_URL}`\n\n**Directory :** `{DOWNLOAD_DIR}`\n\n**Status Interval :** `{DOWNLOAD_STATUS_UPDATE_INTERVAL}`\n\n**View Link :** `{VIEW_LINK}`\n\n**Database Url :** `{DB_URI}`\n\n**Delete Message Duration :** `{AUTO_DELETE_MESSAGE_DURATION}`",
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(f"{emoji.LEFT_ARROW}", callback_data='docs_8'),
                        types.InlineKeyboardButton(f"{emoji.CROSS_MARK}", callback_data='docs_end'),
                        types.InlineKeyboardButton(f"{emoji.RIGHT_ARROW}", callback_data='docs_1')
                    ]
                ]
            )
        )
    elif data == 'end':
        return await query.message.delete()
