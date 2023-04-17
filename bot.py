import json
import sqlite3
import telebot
import configure
from telebot import types
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
from db import BotDB
import tracemalloc
tracemalloc.start()

bot = telebot.TeleBot(configure.config['token'])
db_file = './requests_data.db'
categories = ["УРС/Манго🥭", "Битрикс24🔹", "Live Agent⭐", "Zoiper🗿", "Другое🤙"]
confirms = ["Изменить", "Подтвердить"]
next = ["Назад", "Оставить заявку на подключение"]
nextButtons = [telebot.types.KeyboardButton(nexts) for nexts in next]
categoryButtons = [telebot.types.KeyboardButton(cate) for cate in categories]
сonfirmButtons = [telebot.types.KeyboardButton(confirm) for confirm in confirms]

code = None
description = None
attached_file_id = None
attached_file_type = None


def update_category(new_category):
    global category
    category = new_category


def get_user_profile_link(message):
    chat = bot.get_chat(message.chat.id)
    if chat.type == "private":
        if chat.username:
            return f"https://t.me/{chat.username}"
        else:
            return f"https://t.me/userid{chat.id}"
    else:
        return f"https://t.me/c/{str(chat.id)[4:]}"


@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    tg_link = get_user_profile_link(message)
    bot_db = BotDB(db_file)  # Create an instance of the BotDB class
    bot_db.add_user(user_name)  # Call the add_user method on the instance

    # Create a list of buttons
    # Create a reply markup with the list of buttons
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add(*categoryButtons)
    # Send a message with the markup to the user
    bot.send_message(
        message.chat.id,
        "Привет! Я тут чтобы помочь решить тебе твою сложность или оставить запрос на подключение. Чтобы начать выбери программу из списка:",
        reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in categories)
def button_click(message):
    # Get the text from the button that was clicked
    button = message.text

    # Send a message to the user indicating which button was clicked
    bot.send_message(message.chat.id, f"Ты выбрал: {button}")

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(*nextButtons)
    bot.send_message(message.chat.id, "Оставь заявку или вернись назад чтобы выбрать другую категорию",
                     reply_markup=markup)
    global category
    update_category(button)


# Define a function to handle registration
@bot.message_handler(func=lambda message: message.text in next or message.text in confirms)
def button_click(message):
    button = message.text
    if button == "Подтвердить":
        send_request(message)
    elif button == "Назад":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add(*categoryButtons)
        bot.send_message(message.chat.id, "Выберете другую категорию", reply_markup=markup)
    elif button == "Оставить заявку на подключение" or button == "Изменить":
        bot.send_message(message.chat.id, "Введите 9-тизначный код Anydesk:")
        bot.register_next_step_handler(message, get_code)


# Define a function to handle registration

# Define a function to handle getting the code


def get_code(message):
    global code, description
    code = message.text
    if len(code) != 9 or not code.isdigit():
        bot.send_message(message.chat.id, "Неверный формат кода, попробуйте снова:")
        bot.register_next_step_handler(message, get_code)
        return

    bot.send_message(message.chat.id, "Введите комментарий (можно прикрепить фото или видео):")
    bot.register_next_step_handler(message, get_comment, code)


def get_comment(message, code):
    global description, attached_file_id, attached_file_type
    print(message.video)
    if message.photo:
        description = message.caption
        attached_file_id = message.photo[0].file_id
        attached_file_type = 'photo'
        bot.send_photo(message.chat.id,
                       caption=f"Ваш код: {code}\nВаш комментарий: {description}", photo=attached_file_id)
    elif message.video:
        description = message.caption
        attached_file_id = message.video.file_id
        attached_file_type = 'video'
        bot.send_video(message.chat.id,
                       caption=f"Ваш код: {code}\nВаш комментарий: {description}", video=attached_file_id)
    else:
        description = message.text
        bot.send_message(message.chat.id, f"Ваш код: {code}\nВаш комментарий: {description}")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*сonfirmButtons)
    bot.send_message(
        message.chat.id,
        'Подтвердите ваши данные или вернитесь назад чтобы их исправить',
        reply_markup=markup)


def send_request(message):
    global category, code, description, attached_file_id, attached_file_type
    profile_link = get_user_profile_link(message)
    chat_id = 463344693
    caption = f"Категория: {category}\nAnydesk: {code}\nКомментарий: {description}\nTelegram: {profile_link}"
    if attached_file_id:
        if attached_file_type == 'photo':
            bot.send_photo(chat_id, caption=caption, photo=attached_file_id)
        else:
            bot.send_video(chat_id, caption=caption, video=attached_file_id)
    else:
        bot.send_message(chat_id, caption)

    bot.send_message(message.chat.id, f"Ваш запрос был принят в обработку, ожидайте пока с вами свяжется мой создатель")

    category = None
    code = None
    description = None
    attached_file_id = None
    attached_file_type = None

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton('Start'))
    bot.send_message(
        message.chat.id,
        'Нажмите на "Start" если хотите отправить еще один запрос:',
        reply_markup=markup)
    # Here you can save the code and comment to a


@bot.message_handler(func=lambda message: message.text == 'Start')
def start_again(message):
    start(message)


bot.polling(none_stop=True, interval=0)
