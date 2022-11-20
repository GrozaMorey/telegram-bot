import json
from random import randint
from defs import *
from db import *
from flask import Flask, request
import time




bot.remove_webhook()
time.sleep(2)

bot.set_webhook(url="https://83.222.11.20:443", certificate=open("cert/certificate.crt", 'r'))
app = Flask(__name__)

commands = ["🏵  Услуги", "🚩  Поиск", "❓  Вопросы", "☀  Погода", "💲  Курсы", "🏝  Море", "/start",
            "↩️ Главное меню", "You successfully transferred"]
provider_token = "401643678:TEST:5471e078-3838-40b1-bdea-4e4245e9a902"


@app.route("/", methods=["POST"])
def menu():
    r = request.get_json()
    if "message" in r.keys() and "callback_query" not in r.keys():
        r = r["message"]
        if "successful_payment" in r.keys():
            message = Message.de_json(r)
            send_success_paid(message)
            return "ok", 200
        message = Message.de_json(r)
        if message.from_user.username == "leoolleo":
            bot.send_message(message.chat.id,
                             "🤔 Вы похожи на Ольгу.\n Все Ольги внесены в черный список.\n\n ❓ Для того что бы обжаловать данное решение проедьте в Пермь лично.")
        else:
            user = session.query(User).filter_by(name=message.from_user.username).first()
            if not user:
                markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
                itembtn1 = KeyboardButton('🏵  Услуги')
                itembtn2 = KeyboardButton('🚩  Поиск')
                itembtn3 = KeyboardButton('❓  Вопросы')
                markup.add(itembtn1, itembtn2, itembtn3)
                bot.send_message(message.chat.id,
                                 "Привет, что бы начать работу нажми на одну из кнопок ниже", reply_markup=markup)
                user = User(message.from_user.username, 0)
                session.add(user)
                session.commit()
            elif message.text in ["↩️ Главное меню", "/start"]:
                markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
                itembtn1 = KeyboardButton('🏵  Услуги')
                itembtn2 = KeyboardButton('🚩  Поиск')
                itembtn3 = KeyboardButton('❓  Вопросы')
                markup.add(itembtn1, itembtn2, itembtn3)
                bot.send_message(message.chat.id, "🙏 Чем я могу помочь?\n\n "
                                                  "Отправь мне любой вопрос и я постараюсь ответить.\n\n"
                                                  " Отправь мне локацию через скрепочку 👇 и я посмотрю что есть на карте рядом"
                                                  " с этой точкой.\n\n Выполни команду /help чтобы узнать что ещё я умею.",
                                 reply_markup=markup)
            elif message.text in ["🚩  Поиск", "/search"]:
                example = session.query(Info).filter_by(id=randint(1, 75)).first()
                example = example.text
                for i in ["📷", "💬"]:
                    if i in example:
                        example = example.replace(i, "")
                text = "🙋🏻‍♂️ <b>Искать очень просто!</b>\n" \
                       "Отправь мне свой вопрос начинающийся со слова где и я\n" \
                       " поищу по нашей прекрасной 🗺 <a href='https://phoogle.ru/?utm_source=ThaiBot&utm_medium=searchHelp'>" \
                       "народной карте</a>  и если найду\n" \
                       " что-нибудь подходящее - скину точку.\n\n" \
                       "<b>Например:</b>\n" \
                       f"<code>{example}</code>"
                bot.send_message(message.chat.id, text, disable_web_page_preview=True)

            elif message.text in ["zopa"]:
                bot.send_message("chtotimnesdelaesh12", "dsfsdf")

            elif message.text in ['🏵  Услуги', "/service"]:
                markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
                itembtn1 = KeyboardButton('↩️ Главное меню')
                markup.add(itembtn1)
                bot.send_message(message.chat.id,
                                 "ℹ️ Я скрыл основную клавиатуру. Когда она понадобится - вызови команду"
                                 " /start или нажми кнопку «↩️ Главное меню».", reply_markup=markup)

                keyboard = [[InlineKeyboardButton("📩 Доска объявлений", url='https://t.me/phuketads', )],
                            [InlineKeyboardButton("📸 Фотограф", callback_data='photographer')],
                            [InlineKeyboardButton("🏝 Экскурсии", callback_data='excursions')],
                            [InlineKeyboardButton("🚗 Аренда авто/байка", callback_data='auto')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_message(message.chat.id, "🏵 Услуги моих друзей.\n\nХочешь добавить сюда свою кнопку?\n"
                                                  "<a href='https://telegra.ph/Phoogle-advertising-02-10'>Ознакомься</a>"
                                                  " и свяжись с @phoogle 😉",
                                 reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
            elif message.text == "❓  Вопросы":
                send_info(message)
            elif message.text not in commands or message["content_type"] != "successful_payment":
                requests = request_search(message.text)
                points = {}
                for i in requests:
                    if i['poiName'] == "Palm Tree Rentals":
                        continue
                    points[requests.index(i)] = {"title": i['poiName'], "description": i['poiDesc'], "lat": i["lat"],
                                                 "lng": i["lng"],
                                                 "pid": i["pid"]}
                if points == {}:
                    info = send_info_disc(message)
                    if info is False:
                        send_no_points(message)
                elif len(points) == 1:
                    send_point_info(points, message)
                elif len(requests) <= 6:
                    send_several_point(points, message)
                else:
                    send_many_points(points, message)
        return "ok", 200
    elif "callback_query" in r.keys():
        r = r["callback_query"]
        call = CallbackQuery.de_json(r)
        result = call.data.split("_")
        if "method" in call.data:
            data = json.loads(call.data)
            page = data["page"]
            count = session.query(Info.id).order_by(Info.id.desc()).first()[0]
            keyboard = [[InlineKeyboardButton('↩ Назад',
                                              callback_data='{\"method\":\"pagination\",\"page\":' + str(
                                                  page - 1) + "}"),
                         InlineKeyboardButton("Следующие 15 ➡",
                                              callback_data="{\"method\":\"pagination\",\"page\":" + str(
                                                  page + 1) + "}")]]
            if page == 1:
                keyboard = [[InlineKeyboardButton('Следующие 15 ➡',
                                                  callback_data='{\"method\":\"pagination\",\"page\":' + str(
                                                      page + 1) + "}"), ]]
            if page * 15 >= count:
                keyboard = [[InlineKeyboardButton('↩ Назад', callback_data='{\"method\":\"pagination\",\"page\":' + str(
                    page - 1) + "}"), ]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            send_pagination(message=call, reply_markup=reply_markup, page=page, count=count)
        else:
            category = result[0]
            match category:
                case "service-back":
                    keyboard = [[InlineKeyboardButton("📩 Доска объявлений", url='https://t.me/phuketads', )],
                                [InlineKeyboardButton("📸 Фотограф", callback_data='photographer')],
                                [InlineKeyboardButton("🏝 Экскурсии", callback_data='excursions')],
                                [InlineKeyboardButton("🚗 Аренда авто/байка", callback_data='auto')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id,
                                          text="🏵 Услуги моих друзей.\n\n"
                                               "Хочешь добавить сюда свою кнопку?\n"
                                               " <a href='https://telegra.ph/Phoogle-advertising-02-10'>Ознакомься</a>"
                                               " и свяжись с @phoogle 😉",
                                          reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)
                case "photographer":
                    keyboard = [[InlineKeyboardButton('📸 Заказать фотосессию', callback_data='none')],
                                [InlineKeyboardButton("↩ Назад", callback_data='service-back')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    text = "🏝 <b>Фотограф</b> -<a href='t.me/chtotimnesdelaesh12'>Михаил Батенёв</a>\n\nВсем привет!" \
                           " Меня зовут Михаил Батенёв.С 2010 года занимаюсь фота" \
                           " с 2017 фотографирую на Пхукете и по всему Таиланду.\n\n" \
                           " Если вас интересуют качественные и запоминающиеся фотографии, то смело пишите мне. Сделаем!\n\n" \
                           "-Фотографирую свадьбы, love-story и семьи, а также провожу индивидуальные и парные съёмки в " \
                           "жанре ню," \
                           "-Знаю множество не попсовых локаций,\n -Высылаю по запросу свой гайд" \
                           " с полезными советами по подготовке к съёмке всем подписчикам,\n-Имеется специальный бокс для" \
                           "подводных съёмок и коптер для съёмок с воздуха,\n-Предоставляю боди для индивидуальных " \
                           "съёмок.\n\n" \
                           "Мои соц. сети:\nСвадьбы, love-story, семьи - instagram.com/mikebatenev\n " \
                           "Love-Story',портреты и ню - instagram.com/mikbsxy\n\n" \
                           "Мессенджеры [WhatsApp, Telegram, Viber]: +79324135587)"
                    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                                          parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
                case "excursions":
                    keyboard = [[InlineKeyboardButton('🏝 Заказать экскурсию', callback_data='none')],
                                [InlineKeyboardButton("↩ Назад", callback_data='service-back')]]
                    reply_markup = InlineKeyboardMarkup(keyboard, )
                    text = "🏝 Экскурсии от Travel Service Thailand\n\n" \
                           "🔸 <a href ='https://teletype.in/@elphuket/obzornaya'> Обзорная экскурсия без магазинов</a> \n" \
                           "🔸 <a href ='https://teletype.in/@elphuket/amazing-phangnga'> Удивительная Пханг Нга + Пляж Майкао </a>\n" \
                           "🔸 <a href ='https://teletype.in/@elphuket/khaolak'> Каолак + Пляж с самолетами Майкао</a> \n" \
                           "🔥 <a href ='https://teletype.in/@elphuket/cheowlan'> Озеро Чеолан 2 дня (Laguna Raft)</a> \n" \
                           "🔸 2в1 Рача + Корал на спидботе\n" \
                           "🔸 3в1 Рача + Корал + Майтон на спидботе\n" \
                           "🔸 3в1 Рача + Корал + Закат у Промтхепа на катамаране\n" \
                           "🔸 <a href='https://teletype.in/@elphuket/5in15в1'> Рача + Корал + Майтон + Кай Нок + Кай Нуй</a> \n" \
                           "🔥 <a href='https://teletype.in/@elphuket/similan'> Симиланы на спидботе/катамаране</a> \n" \
                           "🔸 Симиланы 2 дня с ночевкой на корабле\n" \
                           "🔸 Остров Сурин на спидботе\n" \
                           "🔸 <a href='https://teletype.in/@elphuket/jb'> Острова Бонда на спидботе</a> \n" \
                           "🔸 Острова Пхи Пхи + Бамбу на спидботе\n" \
                           "🔸 Полет Ханумана\n\n" \
                           "🧾 Прайслист и подробное описание доступны по ссылке - https://elphuket.ru/price/"
                    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                                          parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
                case "auto":
                    keyboard = [[InlineKeyboardButton('🚗 Выбрать авто', callback_data='auto-choice')],
                                [InlineKeyboardButton('🏍️ Выбрать байк', callback_data='bike-choice')],
                                [InlineKeyboardButton("↩ назад", callback_data='service-back')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    text = "🚗 <b>Аренда байков и автомобилей от @AvtoBike.</b>\n\n" \
                           "Мы предлагаем в аренду автомобили разного типа. Все автомобили застрахованы по первому классу.\n\n" \
                           "<b>Бесплатная подача автомобиля в пределах районов Чалонг, Раваи, Ката, Карон.</b>\n\n" \
                           "Подача в пределах районов Патонг, Кату, Камала - 800 бат.\n" \
                           "Подача в удалённые районы севернее пляжа Камала (Сурин, Банг Тао, Аэропорт, ...) - 1000 бат."
                    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                                          parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
                case "auto-choice":
                    keyboard = [[InlineKeyboardButton('🚗 Toyota Altis', callback_data='toyota-altis'),
                                 InlineKeyboardButton('🚗 Chevrolet Aveo', callback_data='chevrolet-aveo')],
                                [InlineKeyboardButton('🚗 Toyota Vios 2008', callback_data='toyota-vios-2008'),
                                 InlineKeyboardButton('🚗 Toyota Vios 2012', callback_data='toyota-vios-2012')],
                                [InlineKeyboardButton('🚗 Mazda 3', callback_data='mazda-3'),
                                 InlineKeyboardButton('🚗 Nissan Almera', callback_data='nissan-almera')],
                                [InlineKeyboardButton('🚐 Toyota Wish', callback_data='toyota-wish'),
                                 InlineKeyboardButton('🚐 Toyota Sianta', callback_data='toyota-sianta')],
                                [InlineKeyboardButton("↩ Назад", callback_data='auto')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    text = "🚗 <b>Наши автомобили.</b>\n\n" \
                           "Наш автопарк состоит из более чем 20 автомобилей следующих марок:\n\n" \
                           "Пятиместные:\n" \
                           "🚗 <b>Toyota Altis / Vios 2008 или Chevrolet Aveo</b> — от 450฿\n" \
                           "🚗 <b>Toyota Vios 2012</b> — от 500฿\n" \
                           "🚗 <b>Mazda 3</b> — от 500฿\n" \
                           "🚗 <b>Nissan Almera</b> — от 500฿\n\n" \
                           "Семиместные:\n" \
                           "🚐 <b>Toyota Wish</b> — от 600฿\n" \
                           "🚐 <b>Toyota Sienta</b> — от 700฿\n\n" \
                           "<i>Указаны минимальные цены при аренде от 22 дней.</i>"
                    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                                          parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
                case "toyota-altis":
                    run_cars_choice(result, call, "Toyota Corolla Altis 2008", "auto")
                case "chevrolet-aveo":
                    run_cars_choice(result, call, "Chevrolet Aveo", "auto")
                case "toyota-vios-2008":
                    run_cars_choice(result, call, "Toyota Vios (2008г)", "auto")
                case "toyota-vios-2012":
                    run_cars_choice(result, call, "Toyota Vios (2012г)", "auto")
                case "mazda-3":
                    run_cars_choice(result, call, "Mazda 3", "auto")
                case "nissan-almera":
                    run_cars_choice(result, call, "Nissan Almera", "auto")
                case "toyota-wish":
                    run_cars_choice(result, call, "Toyota Wish", "auto")
                case "toyota-sianta":
                    run_cars_choice(result, call, "Toyota Sianta", "auto")
                case "bike-choice":
                    keyboard = [[InlineKeyboardButton('🛵 Yamaha Fino/Mio', callback_data='yamaha-fino')],
                                [InlineKeyboardButton('🛵 Honda Click/AirBlade', callback_data='honda-click')],
                                [InlineKeyboardButton('🏍 Honda PCX 2014', callback_data='honda-pcx-2014'),
                                 InlineKeyboardButton('🏍 Honda PCX 2017', callback_data='honda-pcx-2017')],
                                [InlineKeyboardButton('🏍 Yamaha NMAX', callback_data='yamaha-nmax'),
                                 InlineKeyboardButton('🏍 Honda Forza', callback_data='honda-forza')],
                                [InlineKeyboardButton("↩ Назад", callback_data='auto')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    text = "🛵 <b>Наши байки.</b>\n\n" \
                           "Мы можем предложить тебе:\n" \
                           "🛵 <b>Yamaha Fino/Mio или Honda Click/AirBlade</b>  — от 150฿\n" \
                           "🏍 <b>Honda PCX 2014</b> — от 180฿\n" \
                           "🏍 <b>Honda PCX 2017 или Yamaha NMAX</b> — от 230฿\n" \
                           "🏍 <b>Honda Forza</b> — от 350฿\n"
                    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=text,
                                          parse_mode="HTML", disable_web_page_preview=True, reply_markup=reply_markup)
                case "yamaha-fino":
                    run_cars_choice(result, call, "Yamaha Fino / Mio", "bike")
                case "honda-click":
                    run_cars_choice(result, call, "Honda Click / AirBlade", "bike")
                case "honda-pcx-2014":
                    run_cars_choice(result, call, "Honda PCX 2014", "bike")
                case "honda-pcx-2017":
                    run_cars_choice(result, call, "Honda PCX 2017", "bike")
                case "yamaha-nmax":
                    run_cars_choice(result, call, "Yamaha NMAX", "bike")
                case "honda-forza":
                    run_cars_choice(result, call, "Honda Forza", "mydak")
                case "design":
                    design_car(call, result[1], result[2])
    elif "pre_checkout_query" in r:
        update = Update.de_json(r)
        bot.answer_pre_checkout_query(update.pre_checkout_query.id, ok=True)
    return "ok", 200

if __name__ == "__main__":
    app.run()
