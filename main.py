import logging
import config

import openai

openai.api_key = config.API_TOKEN_OPENAI
model_engine = "text-davinci-003"


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


def get_chatgpt_data(prompt):
    completion = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return completion.choices[0].text


check_subscrition_keyboard = create_keyboard({"Проверить подписку":"check_subs",'Оформить "Премиум"':"buy_subs"})
start_keyboard = create_keyboard({'Оформить "Премиум"':"buy_subs"})


async def check_subscrition(message):
    chat_member = await bot.get_chat_member(chat_id=config.channel_id, user_id=message.from_user.id)

    if chat_member.status == 'member' or chat_member.status == 'administrator' or chat_member.status == 'creator':
        return
    else:
        await bot.send_message(message.from_user.id, config.no_subscription_text, reply_markup=check_subscrition_keyboard)
        return True


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



@dp.message_handler(commands=['start'])
async def start_function(message: types.Message):

    if await check_subscrition(message):
        return

    await bot.send_message(message.from_user.id, config.start_text, reply_markup=start_keyboard)


@dp.callback_query_handler(lambda c: c.data == 'start')
async def start_function_callback(callback_query: CallbackQuery):

    await bot.answer_callback_query(callback_query.id)
    
    if await check_subscrition(callback_query):
        return

    await bot.send_message(callback_query.from_user.id, config.start_text, reply_markup=start_keyboard)



@dp.message_handler()
async def handle_any_text_message(message: types.Message):
    
    if await check_subscrition(message):
        return
    
    await message.answer(config.await_text)
    await message.answer(get_chatgpt_data(message.text))
    await message.answer(config.start_text, reply_markup=start_keyboard)







if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)