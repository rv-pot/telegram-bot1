import telebot
from telebot import types
import schedule
import threading
import time
import random
import json
import os
import logging

# ----------------- НАСТРОЙКИ -----------------
TOKEN = os.getenv("TOKEN")
USER_NAME = "Авелина"
DATA_FILE = "data.json"

bot = telebot.TeleBot(TOKEN)

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# ----------------- ДАННЫЕ -----------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_data()

# ----------------- СОСТОЯНИЕ -----------------
user_coupons = {1: True, 2: True, 3: True}
quest_progress = 0  # <--- добавил, иначе будет ошибка
used_quotes = set()
notifications_enabled = True

# ----------------- ИЗРЕЧЕНИЯ -----------------
quotes = [
    # ... те же цитаты ...
]

# ----------------- НАВИГАЦИЯ -----------------
def main_menu_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎁 Выбрать купон", callback_data="coupons"))
    kb.add(types.InlineKeyboardButton("ℹ️ Важная информация", callback_data="info"))
    kb.add(types.InlineKeyboardButton("🧙‍♂️ Создатель", callback_data="creator"))
    kb.add(types.InlineKeyboardButton("🔕 Отключить сообщения", callback_data="off"))
    return kb

def back_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back"))
    kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
    return kb

# ----------------- СТАРТ -----------------
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"✨ С Новым годом, {USER_NAME} 🤍\n\n"
        "Моя любимая зефирка.\n\n"
        "У тебя есть ТРИ подарочных купона 🎁\n\n"
        "Этот бот — маленькое напоминание о любви, заботе и ценности семьи.\n\n"
        "Выбирай, что хочешь сделать дальше 👇",
        reply_markup=main_menu_keyboard()
    )

# ----------------- CALLBACK -----------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global quest_progress
    global notifications_enabled
    chat_id = call.message.chat.id

    # ---- НОВЫЙ ШАГ: ПРИВЕТСТВЕННАЯ КАРТИНКА ----
    if call.data == "coupons":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("➡️ Показать купоны", callback_data="show_coupons"))
        kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
        with open("coupons/welcome.jpg", "rb") as img:
            bot.send_photo(
                chat_id,
                img,
                caption="🎁 У тебя есть ТРИ подарочных купона.\n\n"
                        "Готова посмотреть? 🤍",
                reply_markup=kb
            )
    elif call.data == "show_coupons":
        coupons = [
            (1, "coupons/coupon1.jpg", "На 3 комплекта нижнего белья 💖"),
            (2, "coupons/coupon2.jpg", "На домашний халат 🤍"),
            (3, "coupons/coupon3.jpg", "Секретный подарок 😏🎁"),
        ]
        found = False
        for num, photo, desc in coupons:
            if user_coupons.get(num):
                found = True
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("✅ Активировать", callback_data=f"activate_{num}"))
                kb.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back"))
                kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
                with open(photo, "rb") as img:
                    bot.send_photo(
                        chat_id,
                        img,
                        caption=f"🎁 Купон №{num}\n\n{desc}\n\nСрок действия: до 31.12.2026",
                        reply_markup=kb
                    )
        if not found:
            bot.send_message(chat_id, "🎁 Все купоны уже активированы 🤍", reply_markup=back_keyboard())

    elif call.data == "quest":
        kb = types.InlineKeyboardMarkup()
        if quest_progress < 15:
            kb.add(types.InlineKeyboardButton("🤍 Было объятие", callback_data="hug"))
        else:
            kb.add(types.InlineKeyboardButton("✅ Активировать купон", callback_data="activate_3"))
        kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))

        bot.send_message(
            chat_id,
            f"Задание:\n\n"
            f"15 спонтанных объятий 🤍\n"
            f"Каждое — дольше 15 секунд,\n"
            f"с тёплыми словами.\n\n"
            f"Прогресс: {quest_progress}/15",
            reply_markup=kb
        )

    elif call.data == "hug":
        quest_progress += 1
        bot.answer_callback_query(call.id, f"Объятие засчитано 🤍 ({quest_progress}/15)")

    elif call.data.startswith("activate_"):
        num = int(call.data.split("_")[1])
        if num == 3 and quest_progress < 15:
            bot.send_message(chat_id, "Сначала нужно завершить задание 🤍")
            return
        user_coupons[num] = False
        bot.send_message(
            chat_id,
            f"✅ Купон №{num} активирован!\nКогда и как — решает создатель😉",
            reply_markup=back_keyboard()
        )

    elif call.data == "back":
        bot.send_message(chat_id, "Возвращаемся 🤍", reply_markup=main_menu_keyboard())

    elif call.data == "main_menu":
        bot.send_message(chat_id, "Главное меню 🤍", reply_markup=main_menu_keyboard())

    elif call.data == "info":
        bot.send_message(
            chat_id,
            "Этот бот создан при поддержке здравого смысла,\n"
            "во имя любви к семье и естественно - к тебе 🤍\n\n"
            "Генеральные спонсоры проекта:\n"
            "— ООО «Отсутствие выёбонов»\n"
            "— ООО «Искренность всегда»\n"
            "— ООО «Открытая душа»",
            reply_markup=back_keyboard()
        )

    elif call.data == "creator":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔗 Перейти к создателю", url="https://t.me/Vargoviich"))
        kb.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back"))
        kb.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu"))
        bot.send_message(
            chat_id,
            "Единственный и неповторимый.\n"
            "Человек с большим сердцем🤍\n"
            "ставший при жизни легендой.\n\n"
            "Народный артист Советского Союза,\n"
            "России, Украины и даже Чечено-Ингушетии.\n\n"
            "Лауреат Государственной премии\n"
            "и Премии Ленинского комсомола.\n\n"
            "Сегодня у нас в гостях человек,\n"
            "который творил эту эпоху\n"
            "и который сам стал эпохой.\n\n"
            "Прошу любить и жаловать!",
            reply_markup=kb
        )

    elif call.data == "off":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ Да", callback_data="off_yes"))
        kb.add(types.InlineKeyboardButton("❌ Нет", callback_data="off_no"))
        bot.send_message(chat_id, "😱😱😱")
        bot.send_message(chat_id, "Ты уверена???", reply_markup=kb)

    elif call.data == "off_no":
        bot.send_message(
            chat_id,
            "Отлично 🤍\n"
            "Но есть одно маленькое условие: подойди к создателю,\n"
            "молча крепко обними минимум на 5 сек\n"
            "и поцелуй 💋",
            reply_markup=back_keyboard()
        )

    elif call.data == "off_yes":
        notifications_enabled = False
        bot.send_message(chat_id, "😈😈😈")
        bot.send_message(
            chat_id,
            "Я никому не скажу 🤫\n"
            "Но есть одно маленькое условие: подойти к создателю, крепко обнять миниму на 10сек и поцеловать, всё равно придётся 💋",
            reply_markup=back_keyboard()
        )

#----------------- ЗАПУСК ИЗРЕЧЕНИЙ -----------------
CHAT_ID = None

@bot.message_handler(func=lambda m: True)
def catch_chat_id(message):
    global CHAT_ID
    CHAT_ID = message.chat.id

def send_quote():
    if not notifications_enabled or CHAT_ID is None:
        return
    available = [q for q in quotes if q not in used_quotes]
    if not available:
        return
    quote, author = random.choice(available)
    used_quotes.add((quote, author))
    bot.send_message(CHAT_ID, f"🤍 {quote}\n\n— {author}")

# ----------------- ПЛАНИРОВЩИК -----------------
def scheduler():
    schedule.every().day.at("09:00").do(send_quote)
    schedule.every().day.at("14:00").do(send_quote)
    schedule.every().day.at("19:00").do(send_quote)
    while True:
        schedule.run_pending()
        time.sleep(50)

threading.Thread(target=scheduler, daemon=True).start()
bot.polling(none_stop=True)
