import os
import random
import time
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ====== ТОКЕН ======
TOKEN = "8306335540:AAF25MZbf1a-oJbihMzmT0DXU5Q5zyPS2gY"

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
    "Мир": "ты дошёл до конца одного пути. И это красиво.",
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
    "Мир": "ты не позволяешь себе завершить.",
}

heavy_reactions = {
    "Смерть": ["Я не пугаю тебя. Я предупреждаю."],
    "Башня": ["Держись крепче."],
    "Дьявол": ["Будь честен с собой."],
    "Луна": ["Сейчас особенно важно не врать себе."],
}

micro_comments = [
    "Посмотрим…",
    "Вот как…",
    "Интересно.",
    "Карты сегодня откровенны.",
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

# ====== ПРИВЕТСТВИЯ ======
start_greetings = [
    "Ты пришёл вовремя. Карты уже разложены, но я пока не смотрю.",
    "Садись. Я не задаю вопросов — карты сделают это за меня.",
    "Интересно… Обычно ко мне приходят, когда что-то уже треснуло.",
    "Ты здесь. Значит, внутри тебя есть вопрос. Или страх.",
    "Не каждый решается подойти. Посмотрим, что привело тебя.",
    "Тише. Иногда ответы пугаются громких мыслей.",
]

# ====== ШЁПОТ (КАТЕГОРИИ) ======
whisper_common = [
    "Не все вопросы требуют ответа.",
    "Карты слышат больше, чем говорят.",
    "Иногда молчание — лучший расклад.",
    "Ты задаёшь правильные вопросы. Почти.",
    "Не торопи судьбу. Она этого не любит.",
]

whisper_personal = [
    "Ты уже знаешь ответ. Просто боишься его услышать.",
    "Этот вопрос возвращается к тебе не в первый раз.",
    "Ты сильнее, чем думаешь. Но пока не веришь.",
    "Ты ищешь знак, а не решение.",
    "Иногда ты притворяешься, что не видишь очевидного.",
]

whisper_rare = [
    "Я бы не стала задавать этот вопрос снова.",
    "Не всё, что ты хочешь узнать, готово быть узнанным.",
    "Карты запомнили тебя.",
    "В следующий раз ответ будет другим.",
    "Некоторые пути лучше не освещать.",
]

# ====== СТИЛЬ МОЛЛИ ======
def molly_style(text: str) -> str:
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
    greeting = random.choice(start_greetings)
    text = (
        f"{greeting}\n\n"
        "/tarot — вытянуть карту\n"
        "/spread — расклад\n"
        "/advice — совет без карт\n"
        "/whisper — сказать шёпотом"
    )
    await update.message.reply_text(
        molly_style(text),
        reply_markup=ReplyKeyboardRemove()
    )

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if question_not_ready(context.user_data):
        await update.message.reply_text(
            molly_style("Я не буду тянуть карту. Вопрос ещё не созрел."),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    name, meaning = draw_card()
    await update.message.reply_text(
        molly_style(f"*{name}*\n{meaning}"),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

async def spread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.03:
        await update.message.reply_text(
            molly_style("Я не возьмусь за расклад. Сейчас слишком много шума."),
            reply_markup=ReplyKeyboardRemove()
        )
        return

    positions = ["Прошлое", "Настоящее", "Будущее"]
    result = []
    for pos in positions:
        name, meaning = draw_card()
        result.append(f"*{pos}* — {name}\n{meaning}")

    await update.message.reply_text(
        molly_style("\n\n".join(result)),
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )

async def advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if random.random() < 0.15:
        phrase = random.choice(advice_refusal_phrases)
    else:
        phrase = random.choice(advice_phrases)

    await update.message.reply_text(
        molly_style(phrase),
        reply_markup=ReplyKeyboardRemove()
    )

async def whisper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Выбираем категорию с разной вероятностью
    r = random.random()
    if r < 0.1:          # 10% – редкая
        phrase = random.choice(whisper_rare)
    elif r < 0.4:        # 30% – персональная
        phrase = random.choice(whisper_personal)
    else:                 # 60% – общая
        phrase = random.choice(whisper_common)

    await update.message.reply_text(
        molly_style(phrase),
        reply_markup=ReplyKeyboardRemove()
    )

# ====== ЗАПУСК С ВЕБХУКАМИ ======
def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tarot", tarot))
    application.add_handler(CommandHandler("spread", spread))
    application.add_handler(CommandHandler("advice", advice))
    application.add_handler(CommandHandler("whisper", whisper))

    # Реагировать на любой текст – только в личных сообщениях
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
            start
        )
    )

    port = int(os.environ.get('PORT', 10000))
    render_url = os.environ.get('RENDER_EXTERNAL_URL', '')

    if render_url:
        webhook_url = f"{render_url}/webhook"
        print(f"✨ Устанавливаю веб-хук на {webhook_url}")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=webhook_url
        )
    else:
        print("⚠️ RENDER_EXTERNAL_URL не задан, запускаю polling (локально)")
        application.run_polling()

if __name__ == "__main__":
    main()
