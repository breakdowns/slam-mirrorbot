import os
import time
import html
import asyncio
import aiohttp
import json
import feedparser
import requests

from telegram.ext import CommandHandler
from telegram import ParseMode

from urllib.parse import quote as urlencode, urlsplit

from pyrogram import Client, filters, emoji
from pyrogram.parser import html as pyrogram_html
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import app, dispatcher, IMAGE_URL
from bot.helper import custom_filters
from bot.helper.telegram_helper.filters import CustomFilters

session = aiohttp.ClientSession()
search_lock = asyncio.Lock()
search_info = {False: dict(), True: dict()}

async def return_search(query, page=1, sukebei=False):
    page -= 1
    query = query.lower().strip()
    used_search_info = search_info[sukebei]
    async with search_lock:
        results, get_time = used_search_info.get(query, (None, 0))
        if (time.time() - get_time) > 3600:
            results = []
            async with session.get(f'https://{"sukebei." if sukebei else ""}nyaa.si/?page=rss&q={urlencode(query)}') as resp:
                d = feedparser.parse(await resp.text())
            text = ''
            a = 0
            parser = pyrogram_html.HTML(None)
            for i in sorted(d['entries'], key=lambda i: int(i['nyaa_seeders']), reverse=True):
                if i['nyaa_size'].startswith('0'):
                    continue
                if not int(i['nyaa_seeders']):
                    break
                link = i['link']
                splitted = urlsplit(link)
                if splitted.scheme == 'magnet' and splitted.query:
                    link = f'<code>{link}</code>'
                newtext = f'''<b>{a + 1}.</b> <code>{html.escape(i["title"])}</code>
<b>Link:</b> <code>{link}</code>
<b>Size:</b> <code>{i["nyaa_size"]}</code>
<b>Seeders:</b> <code>{i["nyaa_seeders"]}</code>
<b>Leechers:</b> <code>{i["nyaa_leechers"]}</code>
<b>Category:</b> <code>{i["nyaa_category"]}</code>\n\n'''
                futtext = text + newtext
                if (a and not a % 10) or len((await parser.parse(futtext))['message']) > 4096:
                    results.append(text)
                    futtext = newtext
                text = futtext
                a += 1
            results.append(text)
        ttl = time.time()
        used_search_info[query] = results, ttl
        try:
            return results[page], len(results), ttl
        except IndexError:
            return '', len(results), ttl

message_info = dict()
ignore = set()

@app.on_message(filters.command(['ts', 'nyaa', 'nyaasi']))
async def nyaa_search(client, message):
    text = message.text.split(' ')
    text.pop(0)
    query = ' '.join(text)
    await init_search(client, message, query, False)

@app.on_message(filters.command(['sts', 'sukebei']))
async def nyaa_search_sukebei(client, message):
    text = message.text.split(' ')
    text.pop(0)
    query = ' '.join(text)
    await init_search(client, message, query, True)

async def init_search(client, message, query, sukebei):
    result, pages, ttl = await return_search(query, sukebei=sukebei)
    if not result:
        await message.reply_text('No results found')
    else:
        buttons = [InlineKeyboardButton(f'1/{pages}', 'nyaa_nop'), InlineKeyboardButton(f'Next', 'nyaa_next')]
        if pages == 1:
            buttons.pop()
        reply = await message.reply_text(result, reply_markup=InlineKeyboardMarkup([
            buttons 
        ]))
        message_info[(reply.chat.id, reply.message_id)] = message.from_user.id, ttl, query, 1, pages, sukebei

@app.on_callback_query(custom_filters.callback_data('nyaa_nop'))
async def nyaa_nop(client, callback_query):
    await callback_query.answer(cache_time=3600)

callback_lock = asyncio.Lock()
@app.on_callback_query(custom_filters.callback_data(['nyaa_back', 'nyaa_next']))
async def nyaa_callback(client, callback_query):
    message = callback_query.message
    message_identifier = (message.chat.id, message.message_id)
    data = callback_query.data
    async with callback_lock:
        if message_identifier in ignore:
            await callback_query.answer()
            return
        user_id, ttl, query, current_page, pages, sukebei = message_info.get(message_identifier, (None, 0, None, 0, 0, None))
        og_current_page = current_page
        if data == 'nyaa_back':
            current_page -= 1
        elif data == 'nyaa_next':
            current_page += 1
        if current_page < 1:
            current_page = 1
        elif current_page > pages:
            current_page = pages
        ttl_ended = (time.time() - ttl) > 3600
        if ttl_ended:
            text = getattr(message.text, 'html', 'Search expired')
        else:
            if callback_query.from_user.id != user_id:
                await callback_query.answer('...no', cache_time=3600)
                return
            text, pages, ttl = await return_search(query, current_page, sukebei)
        buttons = [InlineKeyboardButton(f'Prev', 'nyaa_back'), InlineKeyboardButton(f'{current_page}/{pages}', 'nyaa_nop'), InlineKeyboardButton(f'Next', 'nyaa_next')]
        if ttl_ended:
            buttons = [InlineKeyboardButton('Search Expired', 'nyaa_nop')]
        else:
            if current_page == 1:
                buttons.pop(0)
            if current_page == pages:
                buttons.pop()
        if ttl_ended or current_page != og_current_page:
            await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                buttons
            ]))
        message_info[message_identifier] = user_id, ttl, query, current_page, pages, sukebei
        if ttl_ended:
            ignore.add(message_identifier)
    await callback_query.answer()

# Using https://api.api-zero.workers.dev API and https://www.jaybeetgx.cf API based on this repo https://github.com/devillD/Torrent-Searcher
# Implemented by https://github.com/jusidama18

m = None
i = 0
a = None
query = None

#====== 1337x =======#

@app.on_message(filters.command(["1337x"]))
async def find_1337x(_, message):
    global m
    global i
    global a
    global query
    if len(message.command) < 2:
        await message.reply_text("Usage: /1337x query")
        return
    query = message.text.split(None, 1)[1].replace(" ", "%20")
    m = await message.reply_text("Searching")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.api-zero.workers.dev/yts/{query}") \
                    as resp:
                a = json.loads(await resp.text())
    except:
        await m.edit("Found Nothing.")
        return
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: `{a[i]['Name']}`\n"
        f"➲By {a[i]['UploadedBy']} "
        f"{a[i]['DateUploaded']}\n" 
        f"➲{a[i]['Type']} "
        f"{a[i]['Category']}\n"
        f"➲Poster: {a[i]['Poster']}\n"
        f"➲Language: {a[i]['Language']} || "
        f"➲Checked: {a[i]['LastChecked']}\n"
        f"➲Seeds: {a[i]['Seeders']} & "
        f"➲Leeches: {a[i]['Leechers']}\n\n"
        f"➲Magnet: `{a[i]['Magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Next",
                                         callback_data="1337x_next"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete")
                ]
            ]
        ),
        parse_mode="markdown",
    )


@app.on_callback_query(filters.regex("1337x_next"))
async def callback_query_next_1337x(_, message):
    global i
    global m
    global a
    global query
    i += 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: `{a[i]['Name']}`\n"
        f"➲By {a[i]['UploadedBy']} "
        f"{a[i]['DateUploaded']}\n" 
        f"➲{a[i]['Type']} "
        f"{a[i]['Category']}\n"
        f"➲Poster: {a[i]['Poster']}\n"
        f"➲Language: {a[i]['Language']} || "
        f"➲Checked: {a[i]['LastChecked']}\n"
        f"➲Seeds: {a[i]['Seeders']} & "
        f"➲Leeches: {a[i]['Leechers']}\n\n"
        f"➲Magnet: `{a[i]['Magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="1337x_previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="1337x_next")
                    
                ]
            ]
        ),
        parse_mode="markdown",
    )


@app.on_callback_query(filters.regex("1337x_previous"))
async def callback_query_previous_1337x(_, message):
    global i
    global m
    global a
    global query
    i -= 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: `{a[i]['Name']}`\n"
        f"➲By {a[i]['UploadedBy']} "
        f"{a[i]['DateUploaded']}\n" 
        f"➲{a[i]['Type']} "
        f"{a[i]['Category']}\n"
        f"➲Poster: {a[i]['Poster']}\n"
        f"➲Language: {a[i]['Language']} || "
        f"➲Checked: {a[i]['LastChecked']}\n"
        f"➲Seeds: {a[i]['Seeders']} & "
        f"➲Leeches: {a[i]['Leechers']}\n\n"
        f"➲Magnet: `{a[i]['Magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="next")
                ]
            ]
        ),
        parse_mode="markdown",
    )

#====== 1337x =======#

#====== piratebay =======#

@app.on_message(filters.command(["piratebay"]))
async def find_piratebay(_, message):
    global m
    global i
    global a
    global query
    if len(message.command) < 2:
        await message.reply_text("Usage: /piratebay query")
        return
    query = message.text.split(None, 1)[1].replace(" ", "%20")
    m = await message.reply_text("Searching")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.api-zero.workers.dev/piratebay/{query}") \
                    as resp:
                a = json.loads(await resp.text())
    except:
        await m.edit("Found Nothing.")
        return
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: {a[i]['Name']}\n"
        f"➲{a[i]['Uploader']} on "
        f"{a[i]['Date']}\n" 
        f"➲Size: {a[i]['Size']}\n"
        f"➲Leechers: {a[i]['Leechers']} || "
        f"➲Seeders: {a[i]['Seeders']}\n"
        f"➲Type: {a[i]['Category']}\n\n"
        f"➲Magnet: `{a[i]['Magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Next",
                                         callback_data="piratebay_next"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete")
                ]
            ]
        ),
        parse_mode="markdown",
    )


@app.on_callback_query(filters.regex("piratebay_next"))
async def callback_query_next_piratebay(_, message):
    global i
    global m
    global a
    global query
    i += 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: {a[i]['Name']}\n"
        f"➲{a[i]['Uploader']} on "
        f"{a[i]['Date']}\n" 
        f"➲Size: {a[i]['Size']}\n"
        f"➲Leechers: {a[i]['Leechers']} || "
        f"➲Seeders: {a[i]['Seeders']}\n"
        f"➲Type: {a[i]['Category']}\n\n"
        f"➲Magnet: `{a[i]['Magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="piratebay_previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="piratebay_next")
                    
                ]
            ]
        ),
        parse_mode="markdown",
    )


@app.on_callback_query(filters.regex("piratebay_previous"))
async def callback_query_previous_piratebay(_, message):
    global i
    global m
    global a
    global query
    i -= 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: {a[i]['Name']}\n"
        f"➲{a[i]['Uploader']} on "
        f"{a[i]['Date']}\n" 
        f"➲Size: {a[i]['Size']}\n"
        f"➲Leechers: {a[i]['Leechers']} || "
        f"➲Seeders: {a[i]['Seeders']}\n"
        f"➲Type: {a[i]['Category']}\n\n"
        f"➲Magnet: `{a[i]['Magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="piratebay_previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="piratebay_next")
                ]
            ]
        ),
        parse_mode="markdown",
    )

#====== piratebay =======#

#====== tgx =======#

@app.on_message(filters.command(["tgx"]))
async def find_tgx(_, message):
    global m
    global i
    global a
    global query
    if len(message.command) < 2:
        await message.reply_text("Usage: /tgx query")
        return
    query = message.text.split(None, 1)[1].replace(" ", "%20")
    m = await message.reply_text("Searching")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.jaybeetgx.cf/tor/{query}") \
                    as resp:
                a = json.loads(await resp.text())
    except:
        await m.edit("Found Nothing.")
        return
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: {a[i]['name']}\n"
        f"➲{a[i]['uploader']} on "
        f"{a[i]['date']}\n" 
        f"➲Size: {a[i]['size']}\n"
        f"➲Leechers: {a[i]['peers']} || "
        f"➲Seeders: {a[i]['seeders']}\n\n"
        f"➲Magnet: `{a[i]['magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Next",
                                         callback_data="tgx_next"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete")
                ]
            ]
        ),
        parse_mode="markdown",
    )


@app.on_callback_query(filters.regex("tgx_next"))
async def callback_query_next_tgx(_, message):
    global i
    global m
    global a
    global query
    i += 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: {a[i]['name']}\n"
        f"➲{a[i]['uploader']} on "
        f"{a[i]['date']}\n" 
        f"➲Size: {a[i]['size']}\n"
        f"➲Leechers: {a[i]['peers']} || "
        f"➲Seeders: {a[i]['seeders']}\n\n"
        f"➲Magnet: `{a[i]['magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="tgx_previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="tgx_next")
                    
                ]
            ]
        ),
        parse_mode="markdown",
    )


@app.on_callback_query(filters.regex("tgx_previous"))
async def callback_query_previous_tgx(_, message):
    global i
    global m
    global a
    global query
    i -= 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: {a[i]['name']}\n"
        f"➲{a[i]['uploader']} on "
        f"{a[i]['date']}\n" 
        f"➲Size: {a[i]['size']}\n"
        f"➲Leechers: {a[i]['peers']} || "
        f"➲Seeders: {a[i]['seeders']}\n\n"
        f"➲Magnet: `{a[i]['magnet']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="tgx_previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="tgx_next")
                ]
            ]
        ),
        parse_mode="markdown",
    )

#====== tgx =======#

#====== yts =======#

@app.on_message(filters.command(["yts"]))
async def find_yts(_, message):
    global m
    global i
    global a
    global query
    if len(message.command) < 2:
        await message.reply_text("Usage: /yts query")
        return
    query = message.text.split(None, 1)[1].replace(" ", "%20")
    m = await message.reply_text("Searching")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.api-zero.workers.dev/yts/{query}") \
                    as resp:
                a = json.loads(await resp.text())
    except:
        await m.edit("Found Nothing.")
        return
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: [{a[i]['Name']}]({a[i]['Url']})\n"
        f"➲Released on: {a[i]['ReleasedDate']}\n"
        f"➲Genre: {a[i]['Genre']}\n" 
        f"➲Rating: {a[i]['Rating']}\n"
        f"➲Likes: {a[i]['Likes']}\n"
        f"➲Duration: {a[i]['Runtime']}\n"
        f"➲Language: {a[i]['Language']}\n\n"
        f"➲First Link `{a[i]['Dwnload1']}`\n\n"
        f"➲Second Link: `{a[i]['Download2']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Next",
                                         callback_data="yts_next"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete")
                ]
            ]
        ),
        parse_mode="markdown", disable_web_page_preview=True,
    )


@app.on_callback_query(filters.regex("yts_next"))
async def callback_query_next_yts(_, message):
    global i
    global m
    global a
    global query
    i += 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: [{a[i]['Name']}]({a[i]['Url']})\n"
        f"➲Released on: {a[i]['ReleasedDate']}\n"
        f"➲Genre: {a[i]['Genre']}\n" 
        f"➲Rating: {a[i]['Rating']}\n"
        f"➲Likes: {a[i]['Likes']}\n"
        f"➲Duration: {a[i]['Runtime']}\n"
        f"➲Language: {a[i]['Language']}\n\n"
        f"➲First Link: `{a[i]['Dwnload1']}`\n\n"
        f"➲Second Link: `{a[i]['Download2']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="yts_previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="yts_next")
                    
                ]
            ]
        ),
        parse_mode="markdown", disable_web_page_preview=True,
    )


@app.on_callback_query(filters.regex("yts_previous"))
async def callback_query_previous_yts(_, message):
    global i
    global m
    global a
    global query
    i -= 1
    result = (
        f"**Page - {i+1}**\n\n"
        f"➲Name: [{a[i]['Name']}]({a[i]['Url']})\n"
        f"➲Released on: {a[i]['ReleasedDate']}\n"
        f"➲Genre: {a[i]['Genre']}\n" 
        f"➲Rating: {a[i]['Rating']}\n"
        f"➲Likes: {a[i]['Likes']}\n"
        f"➲Duration: {a[i]['Runtime']}\n"
        f"➲Language: {a[i]['Language']}\n\n"
        f"➲First Link: `{a[i]['Dwnload1']}`\n\n"
        f"➲Second Link: `{a[i]['Download2']}`\n\n\n"
    )
    await m.edit(
        result,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Prev",
                                         callback_data="yts_previous"),
                    InlineKeyboardButton(f"{emoji.CROSS_MARK}",
                                         callback_data="delete"),
                    InlineKeyboardButton(f"Next",
                                         callback_data="yts_next")
                ]
            ]
        ),
        parse_mode="markdown", disable_web_page_preview=True,
    )

#====== yts =======#

@app.on_callback_query(filters.regex("delete"))
async def callback_query_delete(_, message):
    global m
    global i
    global a
    global query
    await m.delete()
    m = None
    i = 0
    a = None
    query = None


def searchhelp(update, context):
    help_string = '''
• /ts <i>[search query]</i>
• /nyaa <i>[search query]</i>
• /nyaasi <i>[search query]</i>

• /sts <i>[search query]</i>
• /sukebei <i>[search query]</i>

• /1337x <i>[search query] (Sometimes Work XD)</i>
• /tgx <i>[search query]</i>
• /yts <i>[search query]</i>
• /piratebay <i>[search query]</i>
'''
    update.effective_message.reply_photo(IMAGE_URL, help_string, parse_mode=ParseMode.HTML)
    
    
SEARCHHELP_HANDLER = CommandHandler("tshelp", searchhelp, filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user) & CustomFilters.mirror_owner_filter, run_async=True)
dispatcher.add_handler(SEARCHHELP_HANDLER)
