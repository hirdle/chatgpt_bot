import logging
import config

from dialogs import getDialog, addDialog, clearDialog, getLenDialogsUsers
from users import add_user, get_all_users


import requests

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN_BOT)
dp = Dispatcher(bot)



def create_keyboard(keys={}, backBtn=False):
    keyboard = InlineKeyboardMarkup()
    
    for key in keys.keys():
        button = InlineKeyboardButton(key, callback_data=keys[key])
        keyboard.add(button)
    
    if backBtn:
        button = InlineKeyboardButton("Назад", callback_data="start")
        keyboard.add(button)

    return keyboard


def get_chatgpt_data(prompt, history):

    error = ""

    try:
        url = "https://api.openai.com/v1/completions"

        context = "\n".join(history)

        data = {
            "model": "text-davinci-003",
            "prompt": "context: "+context+"\n\nprompt: "+prompt,
            "max_tokens": 1000,
            "temperature": 0,
        }

        headers = {'Accept': 'application/json', 'Authorization': 'Bearer '+config.API_TOKEN_OPENAI}
        r = requests.post(url, headers=headers, json=data)

        error = r.text

        return r.json()['choices'][0]['text'].strip()

    except Exception as e:
        print(error)
        return f"Возникли некоторые трудности.\nПопробуйте очистить чат: /clear"


check_subscrition_keyboard = create_keyboard({"Проверить подписку":"check_subs",'Оформить "Премиум"':"buy_subs"})
start_keyboard = create_keyboard({'Оформить "Премиум"':"buy_subs"})


async def check_subscrition(message):
    chat_member = await bot.get_chat_member(chat_id=config.channel_id, user_id=message.from_user.id)

    if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
        return
    else:
        # await bot.send_message(message.from_user.id, config.no_subscription_text, reply_markup=check_subscrition_keyboard)
        return


@dp.callback_query_handler(lambda c: c.data == 'check_subs')
async def check_subs(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    
    if await check_subscrition(callback_query):
        return
    
    await bot.send_message(callback_query.from_user.id, config.start_text, reply_markup=start_keyboard)



@dp.callback_query_handler(lambda c: c.data == 'buy_subs')
async def check_subs(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    
    await bot.send_message(callback_query.from_user.id, config.premium_text, reply_markup=create_keyboard(backBtn=True))


@dp.message_handler(commands=['users'])
async def start_function(message: types.Message):

    if await check_subscrition(message):
        return

    await bot.send_message(message.from_user.id, f"Всего пользователей: {len(get_all_users())}\nАктивных ользователей: {getLenDialogsUsers()}")


@dp.message_handler(commands=['start'])
async def start_function(message: types.Message):

    # getDialog(message.from_user.id)

    add_user(message.from_user.first_name, message.from_user.id)

    if await check_subscrition(message):
        return

    await bot.send_message(message.from_user.id, config.start_text, reply_markup=start_keyboard)


@dp.callback_query_handler(lambda c: c.data == 'start')
async def start_function_callback(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    
    if await check_subscrition(callback_query):
        return

    await bot.send_message(callback_query.from_user.id, config.start_text, reply_markup=start_keyboard)


@dp.message_handler(commands=['clear'])
async def clear_chat_function(message: types.Message):

    clearDialog(message.from_user.id)

    await message.answer("Диалог успешно очищен.")


@dp.message_handler()
async def handle_any_text_message(message: types.Message):

    if message.chat.type != "group":
    
        if await check_subscrition(message):
            return

    sticker = types.InputFile.from_url("https://stickerswiki.ams3.cdn.digitaloceanspaces.com/Baddy_bot/6598443.512.webp")
    message_sticker = await bot.send_sticker(chat_id=message.chat.id, sticker=sticker)

    dialog = getDialog(message.from_user.id)['messages']

    chatgpt_response = get_chatgpt_data(
        prompt=message.text,
        history=dialog
    )

    addDialog(message.from_user.id, message.text, chatgpt_response)

    await message.answer(chatgpt_response)
    await message.answer(config.start_text, reply_markup=start_keyboard)
    await bot.delete_message(chat_id=message.chat.id, message_id=message_sticker.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)