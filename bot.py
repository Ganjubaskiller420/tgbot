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
db_file = 'C:/Users/pingv/Desktop/TeleBot/requests_data.db'
categories = ["УРС/Манго🥭", "Битрикс24🔹", "Live Agent⭐", "Zoiper🗿", "Другое🤙"]
confirms = ["Изменить", "Подтвердить"]
next = ["Назад", "Оставить заявку на подключение"]
nextButtons = [telebot.types.KeyboardButton(nexts) for nexts in next]
categoryButtons = [telebot.types.KeyboardButton(cate) for cate in categories]
сonfirmButtons = [telebot.types.KeyboardButton(confirm) for confirm in confirms]
code = None


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
@bot.message_handler(func=lambda message: message.text in next)
def button_click(message):
    button = message.text
    if button == "Назад":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add(*categoryButtons)
        bot.send_message(message.chat.id, "Выберете другую категорию", reply_markup=markup)
    elif button == "Оставить заявку на подключение":
        bot.send_message(message.chat.id, "Введите 9-тизначный код Anydesk:")
        bot.register_next_step_handler(message, get_code)


# Define a function to handle registration
@bot.message_handler(func=lambda message: message.text in confirms)
def button_click(message):
    bot.send_message(message.chat.id, 'Success')

# Define a function to handle getting the code


def get_code(message):
    global code
    code = message.text
    if len(code) != 9 or not code.isdigit():
        bot.send_message(message.chat.id, "Неверный формат кода, попробуйте снова:")
        bot.register_next_step_handler(message, get_code)
        return

    bot.send_message(message.chat.id, "Введите комментарий:")
    bot.register_next_step_handler(message, get_comment, code)
    comment = message.text
    if len(comment) is None:
        bot.send_message(message.chat.id, "Вы не ввели комментарий, попробуйте снова:")
        bot.register_next_step_handler(message, get_code)
        return
# Define a function to handle getting the comment


def get_comment(message, code):
    # print(message)

    if message.photo:
        bot.send_photo(message.chat.id,
                       caption=f"Ваш код: {code}\nВаш комментарий: {message.caption}", photo=message.photo[0].file_id)
    else:
        bot.send_message(message.chat.id, f"Ваш код: {code}\nВаш комментарий: {message.text}")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*сonfirmButtons)
    bot.send_message(
        message.chat.id,
        'Подтвердите ваши данные или вернитесь назад чтобы их исправить',
        reply_markup=markup)
    # bot.register_next_step_handler(message, confirm_comment)


def confirm_comment(message):
    button = message.text
    if button == "Подтвердить":
        send_request(message)


def send_request(message):
    global category, code
    profile_link = get_user_profile_link(message)
    chat_id = 463344693
    bot.send_message(
        chat_id, f"Категория: {category}\nAnydesk: {code}\nТГ: {profile_link}\nКомментарий: {message.text}")
    bot.send_message(message.chat.id, f"Ваш запрос был принят в обработку, ожидайте пока с вами свяжется мой создатель")
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
# @client.message_handler(commands = ['get_info' , 'info'])
# def get_user_info(message):
#     markup_inline = types.InlineKeyboardMarkup()
#     item_yes = types.InlineKeyboardButton(text = 'ДА', callback_data = 'yes')
#     item_no = types.InlineKeyboardButton(text = 'НЕТ', callback_data = 'no')

#     markup_inline.add(item_yes , item_no)
#     client.send_message(message.chat.id , "Создатель хочешь инфы?",
#         reply_markup = markup_inline
#     )

# @client.callback_query_handler(func = lambda call: True)
# def answer(call):
#     if call.data == 'yes':
#         markup_reply = types.ReplyKeyboardMarkup(resize_keyboard = True)
#         item_id = types.KeyboardButton('МОЙ ID')
#         item_username = types.KeyboardButton('Мой ник')

#         markup_reply.add(item_id , item_username)
#         client.send_message(call.message.chat.id, 'Нажмите на одну из кнопок',
#             reply_markup = markup_reply
#             )
#     elif call.data == "no":
#         pass

# @client.message_handler(content_types = ['text'])
# def get_text(message):
#     # if message.text.lower() == 'привет':
#     #     client.send_message(message.chat.id, 'Привет , создатель')
#     if message.text == 'МОЙ ID':
#         client.send_message(message.chat.id , f'Your ID: {message.from_user.id}')
#     elif message.text == 'Мой ник':
#         client.send_message(message.chat.id , f'Your ID: {message.from_user.first_name} {message.from_user.last_name}')
