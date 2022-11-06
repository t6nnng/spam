from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import telethon
import json
import asyncio
from telethon.tl.functions.channels import JoinChannelRequest
import os
import socks
from opentele.td import TDesktop
from opentele.tl import TelegramClient
from opentele.api import API, CreateNewSession, UseCurrentSession

with open("settings.json", 'r', encoding='utf-8') as file:
    data = json.loads(file.read())

    TOKEN = data['token']
    ip = data['proxy_ip']
    port = data['proxy_port']
    login = data['proxy_login']
    password = data['proxy_password']

    proxy = [socks.SOCKS5,ip,port,True,login,password]

working = []

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb.add(types.KeyboardButton("/help"))
kb.add(types.KeyboardButton("/spam_list"), types.KeyboardButton("/join_send"))
kb.add(types.KeyboardButton("/send"), types.KeyboardButton("/list"))
kb.add(types.KeyboardButton("/messages"), types.KeyboardButton("/join"))
kb.add(types.KeyboardButton("/convert"))

kb1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
kb1.add(types.KeyboardButton("/cancel"))

class snd(StatesGroup):
    msg = State()
    session = State()

    msg1 = State()
    int1 = State()
    int2 = State()
    session1 = State()

    lst = State()
    add = State()
    check = State()
    dl = State()

    session2 = State()

    conv = State()
    chat = State()


def get_chats_list():
    chats = []
    with open("join.txt", 'r', encoding='utf-8') as f:
        text = f.read().split("\n")
        for chat in text:
            if chat == '':
                del(text[text.index(chat)])
            elif "@" in chat:
                text[text.index(chat)] = chat.replace("@", "")
            else:
                pass
        
        chats = text
    
    return chats

def get_chats_send_list():
    chats = []
    with open("send.txt", 'r', encoding='utf-8') as f:
        text = f.read().split("\n")
        for chat in text:
            if chat == '':
                del(text[text.index(chat)])
            elif "@" in chat:
                text[text.index(chat)] = chat.replace("@", "")
            else:
                pass
        
        chats = text
    
    return chats

@dp.message_handler(commands=["help", "start"])
async def help(m: types.Message):
    await m.answer("Список команд: \n\n• /help - вызывает это сообщение\n• /spam_list - проверяет все аккаунты на блокировку\n• /join_send - заходит в чат и отправляет заданное вами сообщение с заданного вами аккаунта\n• /send - отправляет заданное вами сообщение, заданное количество раз, с заданным вами интервалом во все чаты из списка /list\n• /list - отправляет список чатов, в которые бот должен отправлять сообщения\n• /messages - показывает все активные сообщения\n• /join - Выбранный вами аккаунт заходит во все чаты из списка в настройках\n• /convert - Конвертирует папку с tdata в сессию", reply_markup=kb)

@dp.message_handler(commands="spam_list")
async def spam_list(m: types.Message):
    with open("sessions.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())

        for session in data['sessions']:
            client = telethon.TelegramClient(r"sessions/" + session[0], session[1], session[2], proxy=proxy)
            await client.start()

            await client.send_message("SpamBot", "/start")
            await asyncio.sleep(0.33)
            msg = await client.get_messages("SpamBot", None)
            await bot.send_message(session[3], f"Аккаунт с сессией {session[0]}: \n\n{msg[0].message}")

            await client.disconnect()

@dp.message_handler(commands="join", state="*")
async def join(m: types.Message, state: FSMContext):
    with open("sessions.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        
        kb2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for session in data['sessions']:
            bt = types.KeyboardButton(text=f"{session[0]}")
            kb2.add(bt)

        kb2.add(types.KeyboardButton("/cancel"))
        
        await m.answer("Выберите аккаунт для входа:", reply_markup=kb2)
        await state.set_state(snd.session2.state)

@dp.message_handler(content_types=types.ContentTypes.ANY, state=snd.session2)
async def join1(m: types.Message, state: FSMContext):
    with open("sessions.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())

        session_names = []
        for session in data['sessions']:
            session_names.append(session[0])

        a = session_names.index(m.text)

        all_session = [m.text, data['sessions'][a][1], data['sessions'][a][2], data['sessions'][a][3]]
        await state.finish()

        client = telethon.TelegramClient(r"sessions/" + all_session[0], all_session[1], all_session[2], proxy=proxy)
        await client.start()

        chats = get_chats_list()
        for chat in chats:
            await client(JoinChannelRequest(chat))
            await bot.send_message(all_session[3], f"Аккаунт зашел в чат @{chat}")

        await m.answer("Аккаунт вступил во все чаты из списка!", reply_markup=kb)
        await client.disconnect()

@dp.message_handler(commands="cancel", state="*")
async def cancel_state(m: types.Message, state: FSMContext):
    await m.answer("Отменено!", reply_markup=kb)
    await state.finish()

@dp.message_handler(commands="join_send", state="*")
async def join_send(m: types.Message, state: FSMContext):
    await m.answer("Введите сообщение для отправки(картинки и форматирование текста поддерживается)", reply_markup=kb1)
    await state.set_state(snd.msg.state)

@dp.message_handler(content_types=types.ContentTypes.ANY, state=snd.msg)
async def join_send2(m: types.Message, state: FSMContext):
    await state.update_data(msg_to_send=m)

    with open("sessions.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        
        kb2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for session in data['sessions']:
            bt = types.KeyboardButton(text=f"{session[0]}")
            kb2.add(bt)

        kb2.add(types.KeyboardButton("/cancel"))
        
        await m.answer("Выберите аккаунт для рассылки:", reply_markup=kb2)
        await state.set_state(snd.session.state)

@dp.message_handler(state=snd.session)
async def join_send3(m: types.Message, state: FSMContext):
    with open("sessions.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())

        session_names = []
        for session in data['sessions']:
            session_names.append(session[0])

        a = session_names.index(m.text)

        await state.update_data(all_session=[m.text, data['sessions'][a][1], data['sessions'][a][2], data['sessions'][a][3]])

        all_data = await state.get_data()
        await state.finish()

    await m.answer(f"Аккаунт с сессией {all_data['all_session'][0]} зайдёт в чаты, и отправит это сообщение:",reply_markup=kb)
    if all_data['msg_to_send'].caption == None:
        try:
            await m.answer(all_data['msg_to_send'].text, entities=all_data['msg_to_send'].entities)
        except:
            await m.answer(all_data['msg_to_send'].text)
    else:
        try:
            await bot.download_file_by_id(all_data['msg_to_send'].photo[-1].file_id, "cache\\photo.png")
            await m.answer_photo(all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, caption_entities=all_data['msg_to_send'].caption_entities)
        except:
            await bot.download_file_by_id(all_data['msg_to_send'].photo[-1].file_id, "cache\\photo.png")
            await m.answer_photo(all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption)

    client = telethon.TelegramClient(r"sessions/" + all_data['all_session'][0],all_data['all_session'][1],all_data['all_session'][2], proxy=proxy)
    await client.start()

    with open("settings.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        chats = get_chats_list()

        for chat in chats:
            await client(JoinChannelRequest(chat))
            await bot.send_message(all_data['all_session'][3], f"Аккаунт зашел в чат @{chat}")
            if all_data['msg_to_send'].caption == None:
                try:
                    ent = []
                    for entity in all_data['msg_to_send'].entities:
                        if entity.type == "bold":
                            ent.append(telethon.tl.types.MessageEntityBold(entity.offset, entity.length))
                        elif entity.type == "italic":
                            ent.append(telethon.tl.types.MessageEntityItalic(entity.offset, entity.length))
                        elif entity.type == "text_link":
                            ent.append(telethon.tl.types.MessageEntityTextUrl(entity.offset, entity.length, entity.url))
                    await client.send_message(chat, all_data['msg_to_send'].text, formatting_entities=ent)
                except:
                    await client.send_message(chat, all_data['msg_to_send'].text)
                await bot.send_message(all_data['all_session'][3], f"Аккаунт отправил сообщение в чат @{chat}")
            else:
                with open(r"cache/photo.png", 'rb') as f:
                    try:
                        ent = []
                        for entity in all_data['msg_to_send'].caption_entities:
                            if entity.type == "bold":
                                ent.append(telethon.tl.types.MessageEntityBold(entity.offset, entity.length))
                            elif entity.type == "italic":
                                ent.append(telethon.tl.types.MessageEntityItalic(entity.offset, entity.length))
                            elif entity.type == "text_link":
                                ent.append(telethon.tl.types.MessageEntityTextUrl(entity.offset, entity.length, entity.url))
                        await client.send_file(chat, caption=all_data['msg_to_send'].caption, formatting_entities=ent, file=f)
                    except:
                        await client.send_file(chat, caption=all_data['msg_to_send'].caption, file=f)
                await bot.send_message(all_data['all_session'][3], f"Аккаунт отправил сообщение в чат @{chat}")
            
            await asyncio.sleep(0.33)
        
    try:
        os.remove(r"cache/photo.png")
    except:
        pass
    await bot.send_message(all_data['all_session'][3], f"Рассылка завершена!")
    await client.disconnect()

@dp.message_handler(commands="send", state='*')
async def send(m: types.Message, state: FSMContext):
    await m.answer("Введите сообщение для отправки(картинки и форматирование текста поддерживается)", reply_markup=kb1)
    await state.set_state(snd.msg1.state)

@dp.message_handler(content_types=types.ContentTypes.ANY, state=snd.msg1)
async def send2(m: types.Message, state: FSMContext):
    await state.update_data(msg_to_send=m)

    with open("sessions.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        
        kb2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for session in data['sessions']:
            bt = types.KeyboardButton(text=f"{session[0]}")
            kb2.add(bt)

        kb2.add(types.KeyboardButton("/cancel"))
        
        await m.answer("Выберите аккаунт для рассылки:", reply_markup=kb2)
        await state.set_state(snd.session1.state)

@dp.message_handler(state=snd.session1)
async def send3(m: types.Message, state: FSMContext):
    with open("sessions.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())

        session_names = []
        for session in data['sessions']:
            session_names.append(session[0])

        a = session_names.index(m.text)
        await state.update_data(all_session=[m.text, data['sessions'][a][1], data['sessions'][a][2], data['sessions'][a][3]])
        
        await m.answer("Введите количество кругов отправки сообщения:", reply_markup=kb1)
        await state.set_state(snd.int1.state)

@dp.message_handler(state=snd.int1)
async def send4(m: types.Message, state: FSMContext):
    if not m.text.isdigit():
        await m.answer("Пожалуйста введите количество кругов отправки:" , reply_markup=kb1)
        return
    else:
        await state.update_data(int_of_rep=int(m.text))
        await m.answer("Введите интервал между отправкой сообщения в секундах:" , reply_markup=kb1)
        await state.set_state(snd.int2.state)

@dp.message_handler(state=snd.int2)
async def send4(m: types.Message, state: FSMContext):
    if not m.text.isdigit():
        await m.answer("Пожалуйста введите интервал между отправкой сообщения в секундах:" , reply_markup=kb1)
        return
    else:
        await state.update_data(sec_btw_rep=int(m.text))
        all_data = await state.get_data()
        await state.finish()

    await m.answer(f"Аккаунт с сессией {all_data['all_session'][0]}, {all_data['int_of_rep']} раз, с интервалом {all_data['sec_btw_rep']} секунд отправит это сообщение:",reply_markup=kb)
    if all_data['msg_to_send'].caption == None:
        try:
            await m.answer(all_data['msg_to_send'].text, entities=all_data['msg_to_send'].entities)
        except:
            await m.answer(all_data['msg_to_send'].text)
    else:
        try:
            await bot.download_file_by_id(all_data['msg_to_send'].photo[-1].file_id, "cache\\photo.png")
            await m.answer_photo(all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, caption_entities=all_data['msg_to_send'].caption_entities)
        except:
            await bot.download_file_by_id(all_data['msg_to_send'].photo[-1].file_id, "cache\\photo.png")
            await m.answer_photo(all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption)


    i = all_data['int_of_rep']
    e = all_data['sec_btw_rep']

    global working
    working.append([all_data, True, True])
    ind = working.index([all_data, True, True])

    while True:
        if working[ind][2]:
            if working[ind][1] and i > 0:
                with open("settings.json", 'r', encoding='utf-8') as file:
                    data = json.loads(file.read())
                    chats = get_chats_send_list()

                    client = telethon.TelegramClient(r"sessions/" + all_data['all_session'][0],all_data['all_session'][1],all_data['all_session'][2], proxy=proxy)
                    await client.start()

                    for chat in chats:
                        if all_data['msg_to_send'].caption == None:
                            try:
                                ent = []
                                for entity in all_data['msg_to_send'].entities:
                                    if entity.type == "bold":
                                        ent.append(telethon.tl.types.MessageEntityBold(entity.offset, entity.length))
                                    elif entity.type == "italic":
                                        ent.append(telethon.tl.types.MessageEntityItalic(entity.offset, entity.length))
                                    elif entity.type == "text_link":
                                        ent.append(telethon.tl.types.MessageEntityTextUrl(entity.offset, entity.length, entity.url))
                                await client.send_message(chat, all_data['msg_to_send'].text, formatting_entities=ent)
                            except:
                                await client.send_message(chat, all_data['msg_to_send'].text)
                            await bot.send_message(all_data['all_session'][3], f"Аккаунт отправил сообщение в чат @{chat}")
                        else:
                            with open(r"cache/photo.png", 'rb') as f:
                                try:
                                    ent = []
                                    for entity in all_data['msg_to_send'].caption_entities:
                                        if entity.type == "bold":
                                            ent.append(telethon.tl.types.MessageEntityBold(entity.offset, entity.length))
                                        elif entity.type == "italic":
                                            ent.append(telethon.tl.types.MessageEntityItalic(entity.offset, entity.length))
                                        elif entity.type == "text_link":
                                            ent.append(telethon.tl.types.MessageEntityTextUrl(entity.offset, entity.length, entity.url))
                                    await client.send_file(chat, caption=all_data['msg_to_send'].caption, formatting_entities=ent, file=f)
                                except:
                                    await client.send_file(chat, caption=all_data['msg_to_send'].caption, file=f)
                            await bot.send_message(all_data['all_session'][3], f"Аккаунт отправил сообщение в чат @{chat}")
                        
                        await asyncio.sleep(0.33)
                    
                await client.disconnect()
                working[ind][0]['int_of_rep'] -= 1
                i -= 1
                await asyncio.sleep(e)
            else:
                if i != 0:
                    await asyncio.sleep(1)
                else:
                    await bot.send_message(all_data['all_session'][3], f"Рассылка завершена!")
                    working[ind] = [None, False, False]
                    break
        else:
            break
    


@dp.message_handler(commands="list", state="*")
async def lst(m: types.Message, state: FSMContext):
    kb3 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb3.add(types.KeyboardButton("/add"), types.KeyboardButton("/delete"), types.KeyboardButton("/cancel"))
    with open("settings.json", 'r', encoding='utf-8') as file:
        data = json.loads(file.read())
        List = get_chats_send_list()

        if List == []:
            await m.answer("Список чатов пустой!\n", reply_markup=kb3)
        else:
            msg = "Список чатов:"
            i = 1
            for chat in List:
                msg += f"\n{i}. @{chat}"
                i += 1
            await m.answer(msg, reply_markup=kb3)
        
        await state.set_state(snd.lst.state)

@dp.message_handler(commands="delete", state=snd.lst)
async def add(m: types.Message, state: FSMContext):
    await m.answer("Введите номер чата из списка чтобы удалить чат", reply_markup=kb1)
    await state.set_state(snd.dl.state)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=snd.dl)
async def delete(m: types.Message, state: FSMContext):
    if not m.text.isdigit():
        await m.answer("Пожалуйста введите номер чата из списка", reply_markup=kb1)
        return
    else:
        with open("settings.json", 'r', encoding='utf-8') as file:
            data = json.loads(file.read())
            try:
                lst = get_chats_send_list()
                del(lst[int(m.text) - 1])
                txt = ""
                for chat in lst:
                    txt += f"chat\n"

                with open("send.txt", 'w', encoding='utf-8') as f:
                    f.write(txt)
            except:
                await m.answer("Пожалуйста введите существующий номер чата из списка")
                return
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                await m.answer("Успешно удалено!")

                kb3 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                kb3.add(types.KeyboardButton("/add"), types.KeyboardButton("/delete"), types.KeyboardButton("/cancel"))
                List = get_chats_send_list()

                if List == []:
                    await m.answer("Список чатов пустой!\n", reply_markup=kb3)
                else:
                    msg = "Список чатов:"
                    i = 1
                    for chat in List:
                        msg += f"\n{i}. @{chat}"
                        i += 1
                    await m.answer(msg, reply_markup=kb3)
                
                await state.set_state(snd.lst.state)

@dp.message_handler(commands="add", state=snd.lst)
async def add(m: types.Message, state: FSMContext):
    await m.answer("Отправьте юзернэйм чата без @. Пример: test_chat", reply_markup=kb1)
    await state.set_state(snd.add.state)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=snd.add)
async def add1(m: types.Message, state: FSMContext):
    if "@" in m.text or "https" in m.text or "t.me" in m.text:
        await m.answer("Пожалуйста введите юзернэйм чата без @. Пример: test_chat", reply_markup=kb1)
        return
    else:
        with open("settings.json", 'r', encoding='utf-8') as file:

            lst = get_chats_send_list()
            lst.append(m.text)
            txt = ""
            for chat in lst:
                txt += f"chat\n"

            with open("send.txt", 'w', encoding='utf-8') as f:
                f.write(txt)

        kb6 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        kb6.add(types.KeyboardButton("/yes"), types.KeyboardButton("/no"))
        await m.answer("Чат успешно добавлен!\n\nХотите добавить еще? (/yes - да, /no - нет)", reply_markup=kb6)
        await state.set_state(snd.check.state)

@dp.message_handler(commands='yes', state=snd.check)
async def yes(m: types.Message, state: FSMContext):
    await m.answer("Хорошо, тогда отправьте юзернэйм чата без @. Пример: test_chat", reply_markup=kb1)
    await state.set_state(snd.add.state)

@dp.message_handler(commands='no', state=snd.check)
async def yes(m: types.Message, state: FSMContext):
    await m.answer("Вы в главном меню", reply_markup=kb)
    await state.finish()

@dp.message_handler(commands='messages', state='*')
async def messages(m: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("◀️", callback_data=f"prev:0"), types.InlineKeyboardButton("Информация", callback_data=f"this:0"), types.InlineKeyboardButton("▶️", callback_data=f"next:0") )
    
    try:
        if working[0][2] == False:
            await m.answer("Список сообщений, которые рассылаются: ")
            await m.answer("Это сообщение удалено!", reply_markup=keyboard)
        else:
            
                all_data = working[0][0]
                await m.answer("Список сообщений, которые рассылаются: ")
                if all_data['msg_to_send'].caption == None:
                    try:
                        await m.answer(all_data['msg_to_send'].text, entities=all_data['msg_to_send'].entities, reply_markup=keyboard)
                    except:
                        await m.answer(all_data['msg_to_send'].text, reply_markup=keyboard)
                else:
                    try:
                        await m.answer_photo(all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, caption_entities=all_data['msg_to_send'].caption_entities, reply_markup=keyboard)
                    except:
                        await m.answer_photo(all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, reply_markup=keyboard)
    except:
        await m.answer("Список сообщений пуст!")
        

@dp.callback_query_handler(text_startswith="prev")
async def prev_page(call: types.CallbackQuery):
    await call.answer()
    data = int(call.data.split(":")[1])

    if data == 0:
        pass
    else:
        data -= 1
        keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("◀️", callback_data=f"prev:{data}"),
        types.InlineKeyboardButton("Информация", callback_data=f"this:{data}"),
        types.InlineKeyboardButton("▶️", callback_data=f"next:{data}"),
        )
        if working[data][2] == False:
            await call.message.answer("Это сообщение удалено!", reply_markup=keyboard)
        else:
            all_data = working[data][0]
            

            if all_data['msg_to_send'].caption == None:
                try:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_message(call.message.chat.id, all_data['msg_to_send'].text, entities=all_data['msg_to_send'].entities, reply_markup=keyboard)
                except:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_message(call.message.chat.id, all_data['msg_to_send'].text, reply_markup=keyboard)
            else:
                try:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_photo(call.message.chat.id, all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, caption_entities=all_data['msg_to_send'].caption_entities, reply_markup=keyboard)
                except:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_photo(call.message.chat.id, all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, reply_markup=keyboard)

@dp.callback_query_handler(text_startswith="next")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    data = int(call.data.split(":")[1])

    if data == len(working)-1:
        pass
    else:
        data += 1
        keyboard = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("◀️", callback_data=f"prev:{data}"),
        types.InlineKeyboardButton("Информация", callback_data=f"this:{data}"),
        types.InlineKeyboardButton("▶️", callback_data=f"next:{data}"),
        )
        if working[data][2] == False:
            await call.message.answer("Это сообщение удалено!", reply_markup=keyboard)
        else:
            all_data = working[data][0]

            if all_data['msg_to_send'].caption == None:
                try:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_message(call.message.chat.id, all_data['msg_to_send'].text, entities=all_data['msg_to_send'].entities, reply_markup=keyboard)
                except:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_message(call.message.chat.id, all_data['msg_to_send'].text, reply_markup=keyboard)
            else:
                try:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_photo(call.message.chat.id, all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, caption_entities=all_data['msg_to_send'].caption_entities, reply_markup=keyboard)
                except:
                    await bot.delete_message(call.message.chat.id, call.message.message_id)
                    await bot.send_photo(call.message.chat.id, all_data['msg_to_send'].photo[-1].file_id, all_data['msg_to_send'].caption, reply_markup=keyboard)

@dp.callback_query_handler(text_startswith="this")
async def this_page(call: types.CallbackQuery):
    await call.answer()
    data = int(call.data.split(":")[1])

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Остановить", callback_data=f"stop:{data}"),
        types.InlineKeyboardButton("Удалить", callback_data=f"del:{data}")
    )

    all_data = working[data]

    if all_data[1] == True:
        txt = "Работает."
    else:
        txt = "Не работает."
    await call.message.answer(f"Это сообщение отсылается сессией {all_data[0]['all_session'][0]}, с интервалом в {all_data[0]['sec_btw_rep']} секунд. Осталось {all_data[0]['int_of_rep']} повторений. {txt}", reply_markup=markup)

@dp.callback_query_handler(text_startswith="del")
async def del_page(call: types.CallbackQuery):
    data = int(call.data.split(":")[1])

    working[data][2] = False
    working[data][1] = False
    working[data][0] = []

    await call.answer("Удалено!", cache_time=3)
    await bot.delete_message(call.message.chat.id, call.message.message_id)

@dp.callback_query_handler(text_startswith="stop")
async def stop_page(call: types.CallbackQuery):
    data = int(call.data.split(":")[1])

    if working[data][1] == False:
        working[data][1] = True
        await call.answer("Рассылка продолжается.", cache_time=3)
    else:
        working[data][1] = False
        await call.answer("Остановлено! Чтобы продолжить рассылку снова нажмите на остановить.", show_alert=True)

@dp.message_handler(commands='convert', state='*')
async def convert(m: types.Message, state: FSMContext):
    tdatas = [f.name for f in os.scandir("tdata") if f.is_dir()]

    kb10 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for tdata in tdatas:
        kb10.add(types.KeyboardButton(f"{tdata}"))

    await m.answer("Выберите папку с tdata для конвертации", reply_markup=kb10)
    await state.set_state(snd.conv.state)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=snd.conv)
async def convert1(m: types.Message, state: FSMContext):
    await state.update_data(folder=m.text)

    await m.answer("Хорошо, теперь введите чат для отправки отчета", reply_markup=kb1)
    await state.set_state(snd.chat.state)

@dp.message_handler(content_types=types.ContentTypes.TEXT, state=snd.chat)
async def convert1(m: types.Message, state: FSMContext):
    await state.update_data(chat_to_send=m.text)

    data = await state.get_data()

    tdataFolder = r"tdata/" + data['folder']
    tdesk = TDesktop(tdataFolder)

    client = await tdesk.ToTelethon(session=r"sessions/" + data['folder'] + ".session", flag=UseCurrentSession)

    with open("sessions.json", 'r', encoding='utf-8') as f:
        data2 = json.loads(f.read())
        a = None

        try:
            a = int(data['chat_to_send'])
        except:
            a = data['chat_to_send']

        data2['sessions'].append([data['folder'], client.api_id, client.api_hash, a])

        with open("sessions.json", 'w', encoding='utf-8') as file:
            json.dump(data2, file, ensure_ascii=False, indent=4)

    await m.answer("tdata успешно конвертирована в сессию", reply_markup=kb)
    await client.disconnect()
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp)
