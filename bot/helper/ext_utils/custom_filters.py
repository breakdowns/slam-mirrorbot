from pyrogram import filters

def callback_data(data):
    def func(flt, client, callback_query):
        return callback_query.data in flt.data

    data = data if isinstance(data, list) else [data]
    return filters.create(
        func,
        'CustomCallbackDataFilter',
        data=data
    )

def callback_chat(chats):
    def func(flt, client, callback_query):
        return callback_query.message.chat.id in flt.chats

    chats = chats if isinstance(chats, list) else [chats]
    return filters.create(
        func,
        'CustomCallbackChatsFilter',
        chats=chats
    )
