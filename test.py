import telebot
import configure
from telebot import types

client = telebot.TeleBot(configure.config['token'])




@client.message_handler(commands=['get_info', 'info'])
def get_user_info(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_yes = types.InlineKeyboardButton(text='ДА', callback_data='yes')
    item_no = types.InlineKeyboardButton(text='НЕТ', callback_data='no')

    markup_inline.add(item_yes, item_no)
    client.send_message(message.chat.id, "Создатель хочешь инфы?",
                        reply_markup=markup_inline
                        )


@client.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'yes':
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_id = types.KeyboardButton('МОЙ ID')
        item_username = types.KeyboardButton('Мой ник')

        markup_reply.add(item_id, item_username)
        client.send_message(call.message.chat.id, 'Нажмите на одну из кнопок',
                            reply_markup=markup_reply
                            )
    elif call.data == "no":
        pass


@client.message_handler(content_types=['text'])
def get_text(message):
    # if message.text.lower() == 'привет':
    #     client.send_message(message.chat.id, 'Привет , создатель')
    if message.text == 'МОЙ ID':
        client.send_message(message.chat.id, f'Your ID: {message.from_user.id}')
    elif message.text == 'Мой ник':
        client.send_message(message.chat.id, f'Your ID: {message.from_user.first_name} {message.from_user.last_name}')


client.polling(none_stop=True, interval=0)
