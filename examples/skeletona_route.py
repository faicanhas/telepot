import sys
import asyncio
import random
import telepot
import telepot.async
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardHide, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent

"""
$ python3.4 skeletona.py <token>

A skeleton for your async telepot programs.
"""

message_with_inline_keyboard = None

@asyncio.coroutine
def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)

    if content_type != 'text':
        return

    command = msg['text'][-1:].lower()

    if command == 'c':
        markup = ReplyKeyboardMarkup(keyboard=[
                     ['Plain text', KeyboardButton(text='Text only')],
                     [dict(text='Phone', request_contact=True), KeyboardButton(text='Location', request_location=True)],
                 ])
        yield from bot.sendMessage(chat_id, 'Custom keyboard with various buttons', reply_markup=markup)
    elif command == 'i':
        markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='Telegram URL', url='https://core.telegram.org/')],
                     [InlineKeyboardButton(text='Callback - show notification', callback_data='notification')],
                     [dict(text='Callback - show alert', callback_data='alert')],
                     [InlineKeyboardButton(text='Callback - edit message', callback_data='edit')],
                     [dict(text='Switch to using bot inline', switch_inline_query='initial query')],
                 ])

        global message_with_inline_keyboard
        message_with_inline_keyboard = yield from bot.sendMessage(chat_id, 'Inline keyboard with various buttons', reply_markup=markup)
    elif command == 'h':
        markup = ReplyKeyboardHide()
        yield from bot.sendMessage(chat_id, 'Hide custom keyboard', reply_markup=markup)
    elif command == 'f':
        markup = ForceReply()
        yield from bot.sendMessage(chat_id, 'Force reply', reply_markup=markup)

@asyncio.coroutine
def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)

    if data == 'notification':
        yield from bot.answerCallbackQuery(query_id, text='Notification at top of screen')
    elif data == 'alert':
        yield from bot.answerCallbackQuery(query_id, text='Alert!', show_alert=True)
    elif data == 'edit':
        global message_with_inline_keyboard

        if message_with_inline_keyboard:
            msgid = (from_id, message_with_inline_keyboard['message_id'])
            yield from bot.editMessageText(msgid, 'NEW MESSAGE HERE!!!!!')
        else:
            yield from bot.answerCallbackQuery(query_id, text='No previous message to edit')

def on_inline_query(msg):
    def compute():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print('Computing for: %s' % query_string)

        articles = [InlineQueryResultArticle(
                        id='abcde', title='Telegram', input_message_content=InputTextMessageContent(message_text='Telegram is a messaging app')),
                    dict(type='article',
                        id='fghij', title='Google', input_message_content=dict(message_text='Google is a search engine'))]

        photo1_url = 'https://core.telegram.org/file/811140934/1/tbDSLHSaijc/fdcc7b6d5fb3354adf'
        photo2_url = 'https://www.telegram.org/img/t_logo.png'
        photos = [InlineQueryResultPhoto(
                      id='12345', photo_url=photo1_url, thumb_url=photo1_url),
                  dict(type='photo',
                      id='67890', photo_url=photo2_url, thumb_url=photo2_url)]

        result_type = query_string[-1:].lower()

        if result_type == 'a':
            return articles
        elif result_type == 'p':
            return photos
        else:
            results = articles if random.randint(0,1) else photos
            if result_type == 'b':
                return dict(results=results, switch_pm_text='Back to Bot', switch_pm_parameter='Optional start parameter')
            else:
                return dict(results=results)

    answerer.answer(msg, compute)

def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.async.Bot(TOKEN)
answerer = telepot.async.helper.Answerer(bot)

loop = asyncio.get_event_loop()
loop.create_task(bot.message_loop({'chat': on_chat_message,
                                   'callback_query': on_callback_query,
                                   'inline_query': on_inline_query,
                                   'chosen_inline_result': on_chosen_inline_result}))
print('Listening ...')

loop.run_forever()
