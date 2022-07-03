from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import Text
from test import SiteTests
from keyboards import nav_reply_kb

bot_token = '5227383935:AAHloLukm5G-oiS92Ku9d4Mih5UGw_Oi7L8'

bot = Bot(bot_token)
dp = Dispatcher(bot)
SiteTests.start()


@dp.message_handler(commands=['старт'])
async def start(message: types.Message):
    text = 'Приветствую, я бот для прохождения различных психологических тестов,' \
           ' пока что я все еще в разработке но кое что уже умею'
    await message.answer(text=text, reply_markup=nav_reply_kb)

@dp.message_handler(commands=['тесты'])
async def display_tests(message: types.Message):
    markup = SiteTests.display_tests()
    await message.answer(text='Выберите тест', reply_markup=markup)


@dp.message_handler(commands=['далее'])
async def next_tests(message: types.Message):
    SiteTests.next_tests()
    await display_tests(message)

@dp.message_handler(commands=['назад'])
async def next_tests(message: types.Message):
    SiteTests.previous_tests()
    await display_tests(message)


@dp.callback_query_handler(Text(startswith='test '))
async def select_test(callback: types.CallbackQuery):
    idx = int(callback.data.split(' ')[1])
    SiteTests.select_test(idx)
    question = SiteTests.get_question()
    await callback.message.edit_text(text=question['title'], reply_markup=question['markup'])


@dp.callback_query_handler(Text(startswith='select '))
async def select_answer(callback: types.CallbackQuery):
    idx = int(callback.data.split(' ')[1])
    SiteTests.select_answer(idx)
    question = SiteTests.get_question()
    await callback.message.edit_text(text=question['title'], reply_markup=question['markup'])
    await callback.answer()

@dp.callback_query_handler(Text(equals='return'))
async def return_tests(callback: types.CallbackQuery):
    await display_tests(callback.message)
    await callback.answer()

executor.start_polling(dispatcher=dp, skip_updates=True)