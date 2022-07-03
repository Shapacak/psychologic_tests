from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

nav_reply_kb = ReplyKeyboardMarkup(resize_keyboard=True)

main_btn = KeyboardButton('/тесты')
next_btn = KeyboardButton('/далее')
previous_btn = KeyboardButton('/назад')


nav_reply_kb.add(main_btn).row(previous_btn, next_btn)