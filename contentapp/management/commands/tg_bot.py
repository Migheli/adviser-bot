from django.core.management.base import BaseCommand
from contentapp.models import Article, Chapter, Image, Attachment
import logging
import os
import time
from functools import partial
from environs import Env
import requests

import redis
from textwrap import dedent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants, InputMediaPhoto, InputMediaDocument
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, CallbackContext
from telegram.error import BadRequest

from functools import partial

MESSAGES_COOUNT = 15

logger = logging.getLogger(__name__)

env = Env()
env.read_env()

_database = None

def get_sublevel_posts_keyboard(sublevel_posts):

	keyboard = [[InlineKeyboardButton(sublevel_post.name, callback_data=sublevel_post.id)] for sublevel_post in sublevel_posts]
	return keyboard


def delete_messages(update, context, db):
    try:
        messages_to_del = db.lrange(f'{update.effective_chat.id}::messages_to_delete', 0, -1)
        messages_to_del = [message.decode('utf-8') for message in messages_to_del]
        messages_to_del_previous_state = set(messages_to_del)
        print(messages_to_del_previous_state)
        for message_id in messages_to_del_previous_state:
            try:
                context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)
            except BadRequest:
                print(f'Сработало исключение на сообщении на итерации {message_id}')
                pass

    except Exception as e:
        print(f'СЛУЧИЛАСЬ ОШИБКА !!!!!!!!!!!!!!!!!!!!!! {e}')




def show_chapter_details(update: Update, context: CallbackContext, db):

    if update.callback_query.data == 'to_main_menu':
        show_main_menu(update, context, db)
        message_id = update.callback_query['message']['message_id']
        db.rpush(f'{update.effective_chat.id}::messages_to_delete',  message_id)    #добавляем в список сообщений для удаления 

        return 'HANDLE_MENU'


    chapter=Chapter.objects.get(id=update.callback_query.data)
    articles = chapter.articles.all()
    keyboard = get_sublevel_posts_keyboard(articles)
    keyboard.append([InlineKeyboardButton('В главное меню', callback_data='to_main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)


    if chapter.is_with_text(): 
        context.bot.edit_message_text(text=chapter.text, chat_id=update.effective_chat.id, message_id=update.callback_query['message']['message_id'])
        keyboard.append([InlineKeyboardButton('В главное меню', callback_data='to_main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_reply_markup(reply_markup=reply_markup, chat_id=update.effective_chat.id, message_id=update.callback_query['message']['message_id'])
        if chapter.is_text_only(): 
            return 'HANDLE_ARTICLE'


    if chapter.is_with_pictures():
        pictures = chapter.pictures.all()
        images = []
        for picture in pictures:
            with open(f'media/{picture}', 'rb') as image:
                images.append(InputMediaPhoto(image))
        photo_message = context.bot.send_media_group(chat_id=update.effective_chat.id, media=images)


    if chapter.is_with_files():
        attachments = chapter.files.all()
        documents = []
        keyboard = [[InlineKeyboardButton(f'получить {attachment.description}', callback_data=attachment.id)] for attachment in attachments]




        context.bot.send_message(chat_id=update.effective_chat.id, text=chapter.text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        message = context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите интересующий подраздел', parse_mode='HTML', reply_markup=reply_markup)
        db.rpush(f'{update.effective_chat.id}::messages_to_delete',  message.message_id)    


    message_id = update.callback_query['message']['message_id']

    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id)


    for i in range(MESSAGES_COOUNT):
        try:
            message_id = update.callback_query['message']['message_id']
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_id-i)
        except BadRequest:
            print(f'Сработало исключение на сообщении на итераци {i}') # Ошибка создавалась здесь!!!!!!!!!!!!! 
            pass

    return 'HANDLE_ARTICLE'


def show_article_details(update: Update, context: CallbackContext, db):


    if update.callback_query.data == 'to_main_menu':
        message_id = update.callback_query['message']['message_id']
        db.rpush(f'{update.effective_chat.id}::messages_to_delete',  message_id)    #добавляем в список сообщений для удаления 
        show_main_menu(update, context, db)
 
        return 'HANDLE_MENU'

    keyboard = []

    article=Article.objects.get(id=update.callback_query.data)

    reply_markup = []

    if article.is_text_only():
        context.bot.edit_message_text(text=article.text, chat_id=update.effective_chat.id, message_id=update.callback_query['message']['message_id'])
        keyboard.append([InlineKeyboardButton('В главное меню', callback_data='to_main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text_message = context.bot.edit_message_reply_markup(reply_markup=reply_markup, chat_id=update.effective_chat.id, message_id=update.callback_query['message']['message_id'])
        db.rpush(f'{update.effective_chat.id}::messages_to_delete',  text_message.message_id)    
        return 'HANDLE_MENU'

    if article.is_with_files():
        print('Глава с приложениями')
        attachments = article.files.all()
        keyboard = [[InlineKeyboardButton(f'получить {attachment.description}', callback_data=attachment.id)] for attachment in attachments]
        keyboard.append([InlineKeyboardButton('В главное меню', callback_data='to_main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
    if article.is_with_pictures():
        pictures = article.pictures.all()
        images = []
        for picture in pictures:
            with open(f'media/{picture}', 'rb') as image:
                images.append(InputMediaPhoto(image))
        photo_messages = context.bot.send_media_group(chat_id=update.effective_chat.id, media=images)
        delete_messages(update, context, db)
        
        if article.is_with_text:
            keyboard.append([InlineKeyboardButton('В главное меню', callback_data='to_main_menu')])
            reply_markup = InlineKeyboardMarkup(keyboard)
            text_message = context.bot.send_message(reply_markup=reply_markup, chat_id=update.effective_chat.id, text=article.text)
            db.rpush(f'{update.effective_chat.id}::messages_to_delete',  text_message.message_id)  

        for photo_message in photo_messages:
            db.rpush(f'{update.effective_chat.id}::messages_to_delete',  photo_message.message_id)

        return 'HANDLE_ATTACHMENTS' 

    delete_messages(update, context, db)
    
    if InlineKeyboardButton('В главное меню', callback_data='to_main_menu') not in keyboard:
        keyboard.append([InlineKeyboardButton('В главное меню', callback_data='to_main_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = context.bot.send_message(reply_markup=reply_markup, text='нажмите на кнопку, чтобы получить вложение', chat_id=update.effective_chat.id)
    db.rpush(f'{update.effective_chat.id}::messages_to_delete',  message.message_id)    

    


    return 'HANDLE_ATTACHMENTS'



 
def send_attachments(update: Update, context: CallbackContext, db): 

    if update.callback_query.data == 'to_main_menu':
        show_main_menu(update, context, db)
        return 'HANDLE_MENU'

    keyboard =[]
    keyboard.append([InlineKeyboardButton('В главное меню', callback_data='to_main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    attachment = Attachment.objects.get(id=update.callback_query.data)
    with open(f'media/{attachment}', 'rb') as document:
        attachment_message = context.bot.send_document(chat_id=update.effective_chat.id, caption=attachment.description, document=document)

    message = context.bot.send_message(reply_markup=reply_markup, text='выберите необходимый раздел', chat_id=update.effective_chat.id)
    delete_messages(update, context, db)
    db.rpush(f'{update.effective_chat.id}::messages_to_delete',  attachment_message.message_id)    
    db.rpush(f'{update.effective_chat.id}::messages_to_delete',  message.message_id)    


def show_main_menu(update: Update, context: CallbackContext, db):

    delete_messages(update, context, db)



    chapters = Chapter.objects.all()
    keyboard = get_sublevel_posts_keyboard(chapters)
    reply_markup = InlineKeyboardMarkup(keyboard)


    message = context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Пожалуйста, выберите интересующий Вас раздел:',
                                 parse_mode='HTML',
                                 reply_markup=reply_markup) 

    message_to_del_current_state = message.message_id


    delete_messages(update, context, db)

    
    db.delete(f'{update.effective_chat.id}::messages_to_delete')

    db.rpush(f'{update.effective_chat.id}::messages_to_delete',  message_to_del_current_state)    
    # удалялось предыдущее сообщение в предшествующей функции

    return 'HANDLE_MENU' 



def handle_users_reply(update: Update, context: CallbackContext):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
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



    show_main_menu_db = partial(show_main_menu, db=db)
    show_chapter_details_db = partial(show_chapter_details, db=db)
    show_article_details_db =  partial(show_article_details, db=db)
    show_attachments_db = partial(send_attachments, db=db)

    states_functions = {
        'START': show_main_menu_db,
        'HANDLE_MENU': show_chapter_details_db,
        'HANDLE_ARTICLE': show_article_details_db, 
        'HANDLE_ATTACHMENTS': show_attachments_db   
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
