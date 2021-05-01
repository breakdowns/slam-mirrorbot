import time
import html
import asyncio
import aiohttp
import feedparser
from telegram.ext import run_async, CommandHandler
from telegram import ParseMode
from bot import dispatcher, IMAGE_URL
from urllib.parse import quote as urlencode, urlsplit
from pyrogram import Client, filters
from pyrogram.parser import html as pyrogram_html
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.helper import custom_filters
from bot import app
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
                newtext = f'''{a + 1}. {html.escape(i["title"])}
<b>Link:</b> {link}
<b>Size:</b> {i["nyaa_size"]}
<b>Seeders:</b> {i["nyaa_seeders"]}
<b>Leechers:</b> {i["nyaa_leechers"]}
<b>Category:</b> {i["nyaa_category"]}\n\n'''
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
        buttons = [InlineKeyboardButton(f'1/{pages}', 'nyaa_nop'), InlineKeyboardButton('Next', 'nyaa_next')]
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
        buttons = [InlineKeyboardButton('Back', 'nyaa_back'), InlineKeyboardButton(f'{current_page}/{pages}', 'nyaa_nop'), InlineKeyboardButton('Next', 'nyaa_next')]
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

@run_async
def searchhelp(update, context):
    help_string = '''
• /ts <i>[search query]</i>
• /nyaa <i>[search query]</i>
• /nyaasi <i>[search query]</i>

• /sts <i>[search query]</i>
• /sukebei <i>[search query]</i>
'''
    update.effective_message.reply_photo(IMAGE_URL, help_string, parse_mode=ParseMode.HTML)
    
    
SEARCHHELP_HANDLER = CommandHandler("tshelp", searchhelp)
dispatcher.add_handler(SEARCHHELP_HANDLER)
