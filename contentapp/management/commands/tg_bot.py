from django.core.management.base import BaseCommand
from contentapp.models import Article, Chapter, Image
import logging
import os
import time
from functools import partial
from environs import Env
import requests

import redis
from textwrap import dedent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, CallbackContext

logger = logging.getLogger(__name__)

env = Env()
env.read_env()

_database = None



def get_main_menu_keyboard():

	chapters = Chapter.objects.all()
	keyboard = [[InlineKeyboardButton(chapter.name, callback_data=chapter.id)] for chapter in chapters]
	keyboard.append([InlineKeyboardButton('Корзина', callback_data='at_cart')])
	return InlineKeyboardMarkup(keyboard)


def show_main_menu(update: Update, context: CallbackContext):
    
    reply_markup= get_main_menu_keyboard()

    context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='*Пожалуйста, выберите интересующий Вас раздел:*',
                                 parse_mode=constants.PARSEMODE_MARKDOWN_V2,
                                 reply_markup=reply_markup)
    return 'HANDLE_MENU'



def handle_users_reply(update: Update, context: CallbackContext):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """

    db = get_database_connection()
    chat_id = update.effective_chat.id
    if update.message:
        user_reply = update.message.text
    elif update.callback_query:
        user_reply = update.callback_query.data
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db.get(chat_id).decode('utf-8')

    states_functions = {
        'START': show_main_menu,
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    if next_state:
        db.set(chat_id, next_state)

def get_database_connection():
    """
    Возвращает конекшн с базой данных Redis, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        database_password = env('REDIS_PASSWORD')
        database_host = env('REDIS_HOST')
        database_port = env('REDIS_PORT')
        _database = redis.Redis(host=database_host, port=database_port, password=database_password)
    return _database


def main():

    logging.basicConfig(format='TG-bot: %(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    while True:
        try:
            token = env('TELEGRAM_BOT_TOKEN')
            updater = Updater(token, use_context=True)
            logger.info('Бот в Telegram успешно запущен')
            dispatcher = updater.dispatcher
            dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
            dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
            dispatcher.add_handler(CommandHandler('start', handle_users_reply))
            updater.start_polling()
            updater.idle()

        except Exception as err:
            logging.error('Телеграм бот упал с ошибкой:')
            logging.exception(err)





class Command(BaseCommand):

	

	def handle(self, *args, **options):
		main()
