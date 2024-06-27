import config
import string
import secrets
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, KeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio
import telebot
from main import check_password_hash
from base import SQLighter
from instance.DataBase import *


db1 = SQLighter('instance/main.db')
bot1 = telebot.TeleBot(config.TOKEN)
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
email = ''
status = 0

@dp.message_handler(content_types=['text'])
async def message(message):

    global status
    global email
    if message.text == '/start':
        await message.reply('Для начала пользования сайтом войдите в аккаунт, который вы создали на сайте')
        await message.reply('Введите ваш логин')
        status = 1
    elif status == 1:
        email = message.text
        log = db1.user_exists(email=email)
        #login = User.query.filter_by(email=message.text).first()
        if log is None:
            await message.reply('Пользователя с таким емаилом не существует')
        else:
            await message.reply('Введите ваш пароль')
            status = 2

    elif status == 2:
        password = db1.get_pass(email=email)
        if check_password_hash(password, message.text):
            await message.reply('Вы успешно вошли в аккаунт')
            await message.reply('О статусе заявки уведомление вам придёт сюда')
            db1.tg(message.from_user.id, email)
            #status_tg(login)
        else:
            await message.reply('Ошибка при входе')
            status = 0

def mes(id):
    bot1.send_message(id, 'поддержка ответила на ваш вопрос')


@dp.message_handler(commands='/start')
async def cmd_start(message: types.Message):
    global status

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)