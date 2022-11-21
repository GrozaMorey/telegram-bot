from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, \
    InputMediaPhoto, LabeledPrice, Message, CallbackQuery, Update
import datetime
import db
from db import *
from telethon import TelegramClient
import requests
import asyncio



loop = asyncio.get_event_loop()
bot = TeleBot(env["BOT"], parse_mode="html")
api_id = env["API"]
api_hash = env["API_H"]
client = TelegramClient('anon', api_id, api_hash)
provider_token = env["provider"]


def send_date_choice(call, vehicle, vehicle_call, type):
    keyboard = [[InlineKeyboardButton('Сегодня', callback_data=f'{vehicle_call}_price_day_today'),
                 InlineKeyboardButton('Завтра', callback_data=f"{vehicle_call}_price_day_tomorrow")],
                [InlineKeyboardButton('Через неделю', callback_data=f'{vehicle_call}_price_day_week'),
                 InlineKeyboardButton('Через месяц', callback_data=f"{vehicle_call}_price_day_mouth")],
                [InlineKeyboardButton('↩ Назад', callback_data=f'{vehicle_call}')]
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    who = "автомобиля" if type == "auto" else "байка"
    text = f"🛎 <b>Аренда {who} {vehicle}</b>\n\n" \
           "Выберите, когда вам нужна машина с помощью кнопок." if type == "auto" else f"🛎 <b>Аренда {who} {vehicle}</b>\n\n" \
                                                                                       "Выбери, когда вам нужен байк,"\
                                                                                       " с помощью кнопок."
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                          parse_mode="HTML", reply_markup=reply_markup)


def send_rental_choice(call, vehicle, vehicle_call, period, type):
    time = datetime.datetime.now()
    tomorrow = time + datetime.timedelta(1)
    week = time + datetime.timedelta(7)
    mouth = time + datetime.timedelta(30)
    match period:
        case "today":
            time = str(time.date()).split("-")
        case "tomorrow":
            time = str(tomorrow.date()).split("-")
        case "week":
            time = str(week.date()).split("-")
        case "mouth":
            time = str(mouth.date()).split("-")
    time = f"{time[2]}.{time[1]}.{time[0]}"
    print(time)
    cars = session.query(Cars).filter_by(name=vehicle_call).first()
    keyboard = [[InlineKeyboardButton('1-3 дня', callback_data=f'{vehicle_call}_price_day_3 дня_'
                                                               f'{cars.three_days * 3}_{cars.three_days}_{time}')] if type in ["auto", "mydak"] else'' ,
                [InlineKeyboardButton('4-7 дней', callback_data=f"{vehicle_call}_price_day_7 дней_"
                                                                f"{cars.weeks * 7}_{cars.weeks}_{time}"),
                 InlineKeyboardButton('8-14 дней', callback_data=f"{vehicle_call}_price_day_14 дней_"
                                                                 f"{cars.two_weeks * 14}_{cars.two_weeks}_{time}")],
                [InlineKeyboardButton('15-21 дней', callback_data=f"{vehicle_call}_price_day_21 день_"
                                                                  f"{cars.three_weeks * 21}_{cars.three_weeks}_{time}"),
                 InlineKeyboardButton('22-30 дней', callback_data=f'{vehicle_call}_price_day_30 дней_'
                                                                  f'{cars.month * 30}_{cars.month}_{time}')],
                [InlineKeyboardButton('Месяц и больше',
                                      callback_data=f"{vehicle_call}_price_day_long_{cars.long}_{cars.long_per_day}_{time}")],
                [InlineKeyboardButton('Назад', callback_data=f"{vehicle_call}")]
                ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    who = "автомобиля" if type == "auto" else "байка"
    text = f"🛎 <b>Аренда {who} {vehicle} с {time}</b>\n\n" \
           f"Выберите, на какой срок вам нужна машина с помощью кнопок."
    if type == "bike":
        text = f"🛎 <b>Аренда {who} {vehicle} с {time}</b>\n\n" \
               f"Выберите, на какой срок вам нужнен байк с помощью кнопок."
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                          parse_mode="HTML", reply_markup=reply_markup)


def send_price(call, vehicle, vehicle_call, date, price, per_day, start_date, type):
    who = "автомобиля" if type == "auto" else "байка"
    keyboard = [[InlineKeyboardButton('👌 Оформить заявку', callback_data=f'design_{vehicle}_{price}')],
                [InlineKeyboardButton("↩ Назад", callback_data=f'{vehicle_call}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    date = "долгий срок" if date == "long" else date
    text = f'🛎 <b>Аренда {who} {vehicle} на {date} с {start_date}</b>\n\n' \
           f'💸 <b>Cтоимость аренды - {price}฿</b> (без учёта стоимости подачи)\n\n' \
           f'ℹ️ При аренде {who} на {date}, стоимость одного дня аренды {per_day}฿\n\n' \
           'Нажмите кнопку "👌 Оформить заявку", если всё верно и' \
           ' менеджер свяжется с вами для подтверждения заявки и\n' \
           ' обсуждения деталей.'if date != "долгий срок" else \
           f'🛎 <b>Аренда {who} {vehicle} на {date} с {start_date}</b>\n\n' \
           f'ℹ️ При аренде {who} на {date}, стоимость одного дня аренды {per_day}฿\n\n' \
           'Нажмите кнопку "👌 Оформить заявку", если всё верно и' \
           ' менеджер свяжется с вами для подтверждения заявки и\n' \
           ' обсуждения деталей.'
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                          parse_mode="HTML", reply_markup=reply_markup)


def send_cars_info(call, vehicle_call, type):
    keyboard = [[InlineKeyboardButton('🔢 Посчитать стоимость', callback_data=f'{vehicle_call}_price')],
                [InlineKeyboardButton('↩ Назад', callback_data="auto-choice"if type == "auto" else "bike-choice")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    cars = session.query(Cars).filter_by(name=vehicle_call).first()
    text = cars.text
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                          parse_mode="HTML", reply_markup=reply_markup)


def run_cars_choice(result, call, name, type):
    if len(result) >= 2 and result[1] == "price":
        if len(result) >= 3 and result[2] == "day":
            if len(result) > 4:
                send_price(call, name, result[0], result[3], result[4], result[5],
                           result[6], type)
            else:
                send_rental_choice(call, name, result[0], result[3], type)
        else:
            send_date_choice(call, name, result[0], type)

    else:
        send_cars_info(call, result[0], type)


async def get_message_from_channel(*args):
    try:
        await client.connect()
        if len(args) == 2:
            request = await client.get_messages(args[0], search=f"{args[1]}")
            return request[0]
        request = await client.get_messages(args[0], limit=1)
        request.reverse()
        last_rec_db = session.query(Info.message_id).order_by(Info.id.desc()).first()
        if last_rec_db is None:
            last_rec_db = 0
        if request[0].id != last_rec_db[0]:
            request = await client.get_messages(args[0], limit=None, add_offset=last_rec_db[0])
            await client.disconnect()
            for i in request:
                if i.id <= last_rec_db:
                    continue
                text = i.message
                if str(text).find("❓") == 0:
                    info = Info(f"<a href='https://t.me/phuketfaq/{i.id}'>" + i.message.split("\n")[0].replace("❓", "💬")\
                                 + "</a>" + "\n", i.id)
                    session.add(info)
                elif str(text).find("ℹ") == 0:
                    info = Info(f"<a href='https://t.me/phuketfaq/{i.id}'>" + i.message.split("\n")[0].replace("ℹ", "📷")\
                                 + "</a>" + "\n", i.id)
                    session.add(info)
            db.session.commit()
        return
    except Exception as error:
        print(error)
        print("get_message_from_channel")


def request_search(text):
    try:
        headers = {
            'cache-control': "no-cache",
            "X-Requested-With": "XMLHttpRequest"
        }
        link = "https://phoogle.ru/points/?search=)"
        data = {"string": f"{text}"}
        return requests.post(link, data=data, headers=headers).json()
    except Exception as error:
        print(error)


def send_point_info(points, message):
    try:
        for i in points:
            text = f"📍<b>{points[i]['title']}</b>\n" \
                   f"{points[i]['description']}"
            bot.reply_to(message, text=text + f"\nТочка в 📒<a href='https://t.me/phuketmap/"
                                         f"{loop.run_until_complete(get_message_from_channel('phuketmap', points[i]['title'])).id}'> справочнике</a>",
                             parse_mode="HTML", disable_web_page_preview=True)
            keyboard = [[InlineKeyboardButton('📍 Точка на карте', url=f"https://phoogle.ru/points/{points[i]['pid']}")],
                        [InlineKeyboardButton('🗺️ Маршрут на карте',url=f"https://www.google.com/maps?saddr="
                                                                       f"My+Location&daddr={points[i]['lat']},{points[i]['lng']}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_location(message.chat.id, points[i]["lat"], points[i]["lng"], reply_markup=reply_markup)
    except Exception as error:
        print(error)
        print("send point")


def send_several_point(points, message):
    try:
        count = len(points)
        end = "ки"
        if count > 4:
            end = "ек"
        text =f"Я нашёл {count} точ{end} на <a href='https://phoogle.ru/?utm_source=ThaiBot&utm_medium=searchHeadLink'>" \
              f"карте</a>:\n\n"
        point = []
        for i in points:
            point.append("📍<code>" + points[i]["title"] + "</code>" + "\n"+points[i]["description"] + "\n\n")
        bot.send_message(message.chat.id, text + "".join(point) + "Пришли мне название места и я пришлю точку."
                                                                  " Нажми на название чтобы скопировать его.",
                         disable_web_page_preview=True)
    except Exception as error:
        print(error)
        print("send several")

def send_many_points(points, message):
    try:
        text = f"Я нашел {next(reversed(points))} точек на <a href='https:" \
               f"//phoogle.ru/?utm_source=ThaiBot&utm_medium=searchHeadLink'>карте</a>:\n\n"
        point_list = []
        for i in points:
            point_list.append(f"📍 <code>{points[i]['title']}</code>, ")
        point_list[-1] = point_list[-1].replace(",", ".")
        bot.send_message(message.chat.id, text + "".join(point_list) + "\n\nУточни вопрос, или пришли мне название места, или пришли\n"\
                                                                       " мне 📍 локацию - я поищу рядом с ней, или загляни в 📒\n"\
                                                                       "Справочник мест Пхукета, там вообще все точки не выходя из\n"\
                                                                       " телеграма с тэгами и поиском.\n",
                                                                       disable_web_page_preview=True)
    except Exception as error:
        print(error)

def send_no_points(message):
    bot.reply_to(message, "🤔 Хмм, похоже я ничего не нашел по этому запросу,\n"
                          "попробуй ввести другой.")


def send_info(message):
    keyboard = [[InlineKeyboardButton('Следующие 15 ➡', callback_data="{\"method\":\"pagination\",\"page\": 2}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    loop.run_until_complete(get_message_from_channel('phuketfaq'))
    questions = session.query(Info.text).limit(15).offset(0).all()
    list_questions = []
    for i in questions:
        list_questions.append(i[0])
    bot.send_message(message.chat.id, f"ℹ️ В моей информационной базе {session.query(Info.id).order_by(Info.id.desc()).first()[0]} заметок.\n\n"
                                      "<b>Вот их первые 15 заголовков:</b>\n" + "".join(list_questions),
                     reply_markup=reply_markup)

def send_pagination(message, reply_markup, page, count):
    loop.run_until_complete(get_message_from_channel('phuketfaq'))
    questions = session.query(Info.text).limit(15).offset((page * 15) - 15).all()
    list_questions = []
    for i in questions:
        list_questions.append(i[0])
    difference = len(list_questions)
    bot.edit_message_text(chat_id=message.from_user.id, message_id=message.message.id, text=f"ℹ️ В моей информационной базе "
                                        f"{count} заметок.\n\n"
                                      f"<b>Вот их заголовки: с {(page*15) - 14} по {(page * 15) + (difference - 15)}</b>\n" + "".join(list_questions),
                          parse_mode="HTML", reply_markup=reply_markup)

def send_info_disc(message):
    try:
        request = loop.run_until_complete(get_message_from_channel('phuketfaq', message.text))
        print(request)
        if request is None:
            return False
        text = request.message.split("\n")
        title = text[0]
        bot.reply_to(message, text=f"<b>{title.replace('❓', 'ℹ')}</b>" + request.message.replace(title, ""),
                     parse_mode="HTML", disable_web_page_preview=True)
    except Exception as error:
        print(error)
        print("send info")


def design_car(message, car, price):
    prices = [LabeledPrice(label=f'{car}', amount=int(price) * 100), LabeledPrice('Мне на пиццу', 500)]
    bot.send_invoice(
                     message.from_user.id,
                     f'Оформить заявку',
                     f'Хотите оформить {car}?\n Отлично! Произведите оплату и мы сразу же примем ее в работу!', #description
                     f'{car}',
                     provider_token,
                     'Rub', #currency
                     prices, #prices
                     photo_url='http://erkelzaar.tsudao.com/models/perrotta/TIME_MACHINE.jpg',
                     photo_height=512,
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,
                     start_parameter='time-machine-example')


def send_success_paid(message):
    bot.send_message(message.from_user.id,
                     f"Заявка на {message.successful_payment.invoice_payload} успешно оформлена!\n\n В течении часа с вами свяжеться наш менеджер")