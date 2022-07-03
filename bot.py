from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text

from test import webdriver, Test

bot_token = '5227383935:AAHloLukm5G-oiS92Ku9d4Mih5UGw_Oi7L8'

bot = Bot(bot_token)
dp = Dispatcher(bot)
test = Test(webdriver)


@dp.message_handler(Text(['tests','тесты'], ignore_case=True))
async def echo(message: types.Message):
    question = test.get_question()
    await message.answer(text=question['title'], reply_markup=question['markup'])

@dp.callback_query_handler(Text(startswith='select '))
async def select_answer(callback: types.CallbackQuery):
    idx = int(callback.data.split(' ')[1])
    test.select_answer(idx)
    question = test.get_question()
    await callback.message.edit_text(text=question['title'], reply_markup=question['markup'])
    await callback.answer()



executor.start_polling(dp)