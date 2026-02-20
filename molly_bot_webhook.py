import os
import random
import time
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ====== ТОКЕН ======
TOKEN = "YOUR_TOKEN_HERE"

# ====== КАРТЫ (ГОЛОС МОЛЛИ) ======
cards = {
    "Шут": "ты стоишь на краю. Страшно? Конечно. Но именно так и начинаются лучшие истории.",
    "Маг": "у тебя есть всё, что нужно. Вопрос лишь в том, осмелишься ли ты этим воспользоваться.",
    "Верховная жрица": "ты уже знаешь ответ. Просто перестань делать вид, что нет.",
    "Императрица": "что-то растёт и набирает силу. Позволь этому быть.",
    "Император": "пора навести порядок. В себе, в жизни, в решениях.",
    "Иерофант": "иногда стоит прислушаться к опыту. Даже если он кажется скучным.",
    "Влюблённые": "выбор сделан сердцем. Теперь не притворяйся, что это была логика.",
    "Колесница": "ты можешь двигаться дальше. Главное — не тяни всё сразу в разные стороны.",
    "Сила": "ты сильнее, чем думаешь. Особенно там, где обычно сдаёшься.",
    "Отшельник": "пауза необходима. Не бегство — а тишина.",
    "Колесо Фортуны": "что-то меняется. Хочешь ты этого или нет — вопрос вторичный.",
    "Справедливость": "будь честен. Перед собой в первую очередь.",
    "Повешенный": "если не получается двигаться вперёд — посмотри иначе.",
    "Смерть": "это заканчивается. И да, это освобождение, даже если пока больно.",
    "Умеренность": "не спеши. Сейчас важен баланс.",
    "Дьявол": "ты слишком крепко держишься. И это тебя держит.",
    "Башня": "что-то рушится. Возможно, именно это давно пора было разрушить.",
    "Звезда": "надежда есть. Даже если ты её почти не видишь.",
    "Луна": "не всё так, как кажется. И ты это чувствуешь.",
    "Солнце": "ясность, тепло и момент, когда можно выдохнуть.",
    "Суд": "пора перестать убегать от прошлого.",
    "Мир": "ты дошёл до конца одного пути. И это красиво."
}

reversed_cards = {
    "Шут": "ты боишься сделать шаг. Не потому что не готов — потому что сомневаешься.",
    "Маг": "ты не используешь свой потенциал.",
    "Верховная жрица": "ты игнорируешь внутренний голос.",
    "Императрица": "ты откладываешь заботу о важном.",
    "Император": "контроль начинает душить.",
    "Иерофант": "чужие правила мешают услышать себя.",
    "Влюблённые": "ты избегаешь выбора.",
    "Колесница": "ты застрял между «хочу» и «надо».",
    "Сила": "ты тратишь энергию на сопротивление.",
    "Отшельник": "одиночество затянулось.",
    "Колесо Фортуны": "ты цепляешься за старый цикл.",
    "Справедливость": "ты не хочешь признать правду.",
    "Повешенный": "ожидание стало ловушкой.",
    "Смерть": "ты держишься за то, что уже мертво.",
    "Умеренность": "баланс нарушен.",
    "Дьявол": "зависимость сильнее, чем кажется.",
    "Башня": "ты делаешь вид, что всё в порядке.",
    "Звезда": "надежда приглушена, но жива.",
    "Луна": "страхи управляют решениями.",
    "Солнце": "ты не позволяешь себе радость.",
    "Суд": "ты откладываешь важный разговор.",
    "Мир": "ты не позволяешь себе завершить."
}

heavy_reactions = {
    "Смерть": ["Я не пугаю тебя. Я предупреждаю."],
    "Башня": ["Держись крепче."],
    "Дьявол": ["Будь честен с собой."],
    "Луна": ["Сейчас особенно важно не врать себе."]
}

micro_comments = [
    "Посмотрим…",
    "Вот как…",
    "Интересно.",
    "Карты сегодня откровенны."
]

# ====== СОВЕТЫ ======
advice_phrases = [
    "Перестань ждать идеального момента.",
    "Ты не обязан решать это сегодня.",
    "Если выбор пугает — значит, он настоящий.",
    "Не пытайся всё понять. Почувствуй.",
    "Сейчас важнее беречь себя.",
]

advice_refusal_phrases = [
    "Я не дам совет. Ты и так знаешь.",
    "Если я скажу — ты не услышишь.",
]

# ====== СТИЛЬ МОЛЛИ ======
def molly_style(text: str, mood: str = "") -> str:
    return f"✨ {text}\n\n— Молли"

def question_not_ready(user_data: dict) -> bool:
    return random.random() < 0.07

def draw_card():
    name = random.choice(list(cards.keys()))
    reversed_card = random.choice([True, False])
    micro = random.choice(micro_comments)

    if reversed_card:
        meaning = reversed_cards[name]
        card_name = f"{name} (перевёрнутая)"
    else:
        meaning = cards[name]
        card_name = name

    reaction = ""
    if name in heavy_reactions and random.random() < 0.6:
        reaction = "\n" + random.choice(heavy_reactions[name])

    return card_name, f"{micro}\n{meaning}{reaction}"

# ====== ОБРАБОТЧИКИ ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "/tarot — карта\n/spread — расклад\n/advice — совет\n/whisper — секрет"
    await update.message.reply_text(molly_style(text))

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if question_not_ready(context.user_data):
        await update.message.reply_text(
            molly_style("Я не буду тянуть карту. Вопрос ещё не созрел.")
        )
        return

    name, meaning = draw_card()
    await update.message.reply_text(
        molly_style(f"*{name}*\n{meaning}"),
        parse_mode="Markdown"
    )

async def spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.03:
        await update.message.reply_text(
            molly_style("Я не возьмусь за расклад. Сейчас слишком много шума.")
        )
        return

    positions = ["Прошлое", "Настоящее", "Будущее"]
    result = []
    for pos in positions:
        name, meaning = draw_card()
        result.append(f"*{pos}* — {name}\n{meaning}")

    await update.message.reply_text(
        molly_style("\n\n".join(result)),
        parse_mode="Markdown"
    )

async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.15:
        phrase = random.choice(advice_refusal_phrases)
    else:
        phrase = random.choice(advice_phrases)

    await update.message.reply_text(molly_style(phrase))

async def whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        molly_style("Не все вопросы требуют ответа.")
    )

# ====== ЗАПУСК ======
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("tarot", tarot))
application.add_handler(CommandHandler("spread", spread))
application.add_handler(CommandHandler("advice", advice))
application.add_handler(CommandHandler("whisper", whisper))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

if __name__ == "__main__":
    application.run_polling()
