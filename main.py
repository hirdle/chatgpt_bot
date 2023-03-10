import logging
import config
import time

from dialogs import getDialog, addDialog, clearDialog, getLenDialogsUsers
from users import add_user, get_all_users, get_user_limit_req, get_user_current_req, check_user_limit, add_user_current_req, get_active_users, get_usermode, change_mode_user


import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage


storage = MemoryStorage()

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN_BOT)
dp = Dispatcher(bot, storage=storage)


start_text = lambda m: f"Ваш баланс: { get_user_limit_req(m.from_user.id)-get_user_current_req(m.from_user.id) }\nОтправьте сообщением задачу для нейросети.  👇"


def create_keyboard(keys={}, backBtn=False):
    keyboard = InlineKeyboardMarkup()
    
    for key in keys.keys():
        button = InlineKeyboardButton(key, callback_data=keys[key])
        keyboard.add(button)
    
    if backBtn:
        button = InlineKeyboardButton("Назад", callback_data="start")
        keyboard.add(button)

    return keyboard


# получение данных от chatgpt

def get_dalle_data(prompt, user_id, groupState):

    error = ""

    try:
        url = "https://api.openai.com/v1/images/generations"

        data = {
            "prompt": prompt,
            "n": 1,
            "size": "512x512"
        }

        headers = {'Accept': 'application/json', 'Authorization': 'Bearer '+config.API_TOKEN_OPENAI}
        r = requests.post(url, headers=headers, json=data)

        error = r.text.strip()

        if r.json().get("error") == None and groupState == False:
            add_user_current_req(user_id, num_req=2)

        return r.json()['data'][0]['url']

    except Exception as e:
        # print(error)
        return f"Возникли некоторые трудности.\nПопробуйте очистить чат: /clear"


# получение данных от chatgpt

def get_chatgpt_data(prompt, history, user_id, groupState):

    error = ""

    try:
        url = "https://api.openai.com/v1/chat/completions"

        history.append({"role": "user", "content": prompt})

        data = {
            "model": "gpt-3.5-turbo",
            "messages": history,
            "max_tokens": 1000,
            "temperature": 0,
        }

        headers = {'Accept': 'application/json', 'Authorization': 'Bearer '+config.API_TOKEN_OPENAI}
        r = requests.post(url, headers=headers, json=data)

        error = r.text.strip()

        if r.json().get("error") == None and groupState == False:
            add_user_current_req(user_id)

        return r.json()['choices'][-1]['message']['content'].strip()

    except Exception as e:
        # print(error)
        return f"Возникли некоторые трудности.\nПопробуйте очистить чат: /clear"



check_subscrition_keyboard = create_keyboard({"Проверить подписку":"check_subs",'Пополнить баланс':"buy_balance"})
start_keyboard = create_keyboard({'Пополнить баланс':"buy_balance"})



# проверка подписки

async def check_subscrition(message):
    return
    # chat_member = await bot.get_chat_member(chat_id=config.channel_id, user_id=message.from_user.id)

    # if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
    #     return
    # else:
    #     # await bot.send_message(message.from_user.id, config.no_subscription_text, reply_markup=check_subscrition_keyboard)
    #     return


# отправка уведомлений

async def send_notify(m):
    users = get_all_users()
    users.reverse()
    for user in users:
        try:
            await bot.send_message(user.profile_id, m)
            time.sleep(0.5)
        except: pass


# отправка сообщения

@dp.message_handler(commands=['send'])
async def start_function(message: types.Message):

    await message.answer("Рассылка запущена")

    await send_notify(message.text.replace("/send", ""))



# сменить режим

@dp.message_handler(commands=['mode'])
async def start_function(message: types.Message):

    if await check_subscrition(message):
        return
    
    current_mode = change_mode_user(message.from_user.id)

    await bot.send_message(message.from_user.id, f"Режим сменен на {config.modes[current_mode]}")



# повторная проверка подписки

@dp.callback_query_handler(lambda c: c.data == 'check_subs')
async def check_subs(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    
    if await check_subscrition(callback_query):
        return
    
    await bot.send_message(callback_query.from_user.id, start_text(callback_query), reply_markup=start_keyboard)



# купить подписку

@dp.callback_query_handler(lambda c: c.data == 'buy_balance')
async def check_subs(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)

    photo = types.InputFile('premium.jpg')
    
    await bot.send_photo(callback_query.from_user.id, photo, caption=config.premium_text, reply_markup=create_keyboard(backBtn=True))



# отображение статистики

@dp.message_handler(commands=['users'])
async def start_function(message: types.Message):

    if await check_subscrition(message):
        return

    await bot.send_message(message.from_user.id, f"Всего пользователей: {len(get_all_users())}\nАктивных пользователей: {getLenDialogsUsers()}\nАктивных сейчас пользователей: {get_active_users()}")


# команда старт

@dp.message_handler(commands=['start'])
async def start_function(message: types.Message):

    # getDialog(message.from_user.id)

    add_user(message.from_user.first_name, message.from_user.id)

    if await check_subscrition(message):
        return

    await bot.send_message(message.from_user.id, start_text(message), reply_markup=start_keyboard)


@dp.callback_query_handler(lambda c: c.data == 'start')
async def start_function_callback(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    
    if await check_subscrition(callback_query):
        return

    await bot.send_message(callback_query.from_user.id, start_text(callback_query), reply_markup=start_keyboard)



# очистка контекста

@dp.message_handler(commands=['clear'])
async def clear_chat_function(message: types.Message):

    clearDialog(message.from_user.id)

    await message.answer("Диалог успешно очищен.")



# обработка для нейросети

@dp.message_handler()
async def handle_any_text_message(message: types.Message):

    groupState = "group" in message.chat.type 

    if not groupState:
    
        if await check_subscrition(message):
            return

        if check_user_limit(message.chat.id) == False:
            await message.answer("Пополните баланс.")
            return

    if groupState and message.chat.id != config.official_group_id:
        return
    
    sticker = types.InputFile.from_url("https://stickerswiki.ams3.cdn.digitaloceanspaces.com/Baddy_bot/6598443.512.webp")
    message_sticker = await bot.send_sticker(chat_id=message.chat.id, sticker=sticker)

    if get_usermode(message.from_user.id) == 0:

        dialog = getDialog(message.from_user.id)['messages']

        chatgpt_response = get_chatgpt_data(
            prompt=message.text,
            history=dialog,
            user_id=message.from_user.id,
            groupState=groupState
        )

        addDialog(message.from_user.id, message.text, chatgpt_response)

        await message.reply(chatgpt_response)


    elif get_usermode(message.from_user.id) == 1:

        dalle_response = get_dalle_data(
            prompt=message.text,
            user_id=message.from_user.id,
            groupState=groupState
        )

        image = types.InputFile.from_url(dalle_response)



        await message.reply_photo(photo=image)


    if not groupState:
        await message.answer(start_text(message), reply_markup=start_keyboard)

    await bot.delete_message(chat_id=message.chat.id, message_id=message_sticker.message_id)



# запуск
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)