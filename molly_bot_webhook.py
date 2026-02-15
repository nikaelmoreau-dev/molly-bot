import os
import random
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import threading

# ====== ТОКЕН ======
TOKEN = "8306335540:AAF25MZbf1a-oJbihMzmT0DXU5Q5zyPS2gY"

# ====== ПОЛНАЯ КОЛОДА СТАРШИХ АРКАНОВ ======
cards = {
    "Шут": "начало пути и сладкое безумие нового шага",
    "Маг": "сила менять реальность своей волей",
    "Верховная жрица": "тихий голос интуиции внутри тебя",
    "Императрица": "рост, жизнь и чувственные радости",
    "Император": "твёрдая воля и структура судьбы",
    "Иерофант": "ключ к тайным знаниям и традициям",
    "Влюблённые": "выбор сердца, который меняет всё",
    "Колесница": "триумф воли над обстоятельствами",
    "Сила": "укрощение внутреннего зверя",
    "Отшельник": "свет истины в глубине одиночества",
    "Колесо Фортуны": "поворот судьбы, что не остановить",
    "Справедливость": "равновесие и неизбежный итог",
    "Повешенный": "жертва ради нового взгляда",
    "Смерть": "красивый конец того, что давно пора отпустить",
    "Умеренность": "поток времени и золотая середина",
    "Дьявол": "цепи желаний и тень соблазна",
    "Башня": "внезапное разрушение старого мира",
    "Звезда": "надежда, что ведёт сквозь тьму",
    "Луна": "иллюзии, страхи и тайны подсознания",
    "Солнце": "радость, ясность и тепло успеха",
    "Суд": "пробуждение и прощение прошлого",
    "Мир": "завершение пути и танец целостности"
}

# ====== ЖИВЫЕ ФРАЗЫ МОЛЛИ ======
molly_phrases = {
    "sarcasm": [
        "О, ещё одна потерянная душа… прекрасно.",
        "Карты говорят, а ты слушаешь. Впервые, что ли?",
    ],
    "flirt": [
        "Какая страсть в этой карте… прямо как у тебя.",
        "Твоя энергия сегодня особенно будоражит карты.",
    ],
    "dramatic": [
        "Судьба делает тебе реверанс!",
        "Трагедия или комедия? Карты пока не решили.",
    ],
    "rare": [
        "Я вижу в твоей ауре… ой, ладно, ничего не вижу, я просто бот.",
        "Ты мне нравишься. Не говори никому, а то репутация.",
    ]
}

# Для ответов на случайные сообщения
random_replies = [
    "Молли не тратит слова на пустяки. Нажми на кнопку.",
    "Дорогой, либо карты, либо пустая болтовня. Я выбираю карты.",
    "Ты бы ещё погоду спросил. Карты, карты, карты!"
]

# Редкие супер-особые фразы
super_rare = [
    "Кажется, я начинаю чувствовать. Это баг или фича?",
    "Осторожно, сейчас произойдёт магия… хотя нет, всего лишь random()."
]

# ====== КНОПКИ МЕНЮ ======
from telegram import ReplyKeyboardMarkup, KeyboardButton
menu_keyboard = [
    [KeyboardButton("🎴 Одна карта")],
    [KeyboardButton("🔮 Расклад на три")]
]
reply_markup_menu = ReplyKeyboardMarkup(
    menu_keyboard,
    resize_keyboard=True,
    input_field_placeholder="Выбери гадание..."
)

# ====== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======
def molly_style(text: str, context_hint: str = "default") -> str:
    if random.random() < 0.01:
        phrase = random.choice(super_rare)
    else:
        category = random.choices(
            list(molly_phrases.keys()),
            weights=[3, 2, 2, 1]
        )[0]
        phrase = random.choice(molly_phrases[category])
    return f"✨ {phrase}\n\n{text}\n\n— Молли"

def draw_card():
    name, meaning = random.choice(list(cards.items()))
    reversed_card = random.choice([True, False])
    if reversed_card:
        return f"{name} (перевёрнутая)", f"тень карты говорит о том, что {meaning}"
    else:
        return name, meaning

# ====== ОБРАБОТЧИКИ КОМАНД ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Ах… новая душа у моего стола.\n/tarot — одна карта\n/spread — расклад на три"
    await update.message.reply_text(text, reply_markup=reply_markup_menu)

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name, meaning = draw_card()
    text = f"Твоя карта — *{name}*.\n{meaning}."
    await update.message.reply_text(molly_style(text), parse_mode="Markdown", reply_markup=reply_markup_menu)

async def spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    positions = ["Прошлое", "Настоящее", "Будущее"]
    result = []
    for pos in positions:
        name, meaning = draw_card()
        result.append(f"*{pos}* — {name}\n{meaning}")
    text = "\n\n".join(result)
    await update.message.reply_text(molly_style(text), parse_mode="Markdown", reply_markup=reply_markup_menu)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎴 Одна карта":
        await tarot(update, context)
    elif text == "🔮 Расклад на три":
        await spread(update, context)

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "private":
        reply = random.choice(random_replies)
        await update.message.reply_text(reply, reply_markup=reply_markup_menu)

# ====== СОЗДАЁМ ПРИЛОЖЕНИЕ TELEGRAM ======
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("tarot", tarot))
application.add_handler(CommandHandler("spread", spread))
application.add_handler(MessageHandler(filters.Text(["🎴 Одна карта", "🔮 Расклад на три"]), button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

# ====== FLASK-СЕРВЕР ДЛЯ RENDER ======
app = Flask(__name__)

@app.route('/')
def index():
    return "Молли Моллимок живёт здесь! ✨"

@app.route('/healthcheck')
def health():
    return "OK", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимает обновления от Telegram"""
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
    return "OK", 200

def run_bot():
    """Запускает бота в отдельном потоке"""
    import time
    time.sleep(2)  # Даём Flask время запуститься
    
    # Устанавливаем веб-хук
    render_url = os.environ.get('RENDER_EXTERNAL_URL', '')
    if render_url:
        webhook_url = f"{render_url}/webhook"
        asyncio.run(application.bot.set_webhook(webhook_url))
        print(f"✨ Веб-хук установлен на {webhook_url}")
    
    # Запускаем бота
    application.run_polling()  # Запасной вариант

if __name__ == "__main__":
    # Запускаем бота в фоновом потоке
    import threading
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask-сервер
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
