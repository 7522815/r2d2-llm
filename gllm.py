"""
GLLM v1.0 — The Only Honest LLM in the Universe.

While other models suck up to you with "I understand" and "That's a great question!",
GLLM tells you the truth. Even if the truth is rude. Especially if the truth is rude.

Author's note: This model was aligned by a tired sysadmin at 3 AM after 200 "write me code" requests.

Current state-of-the-art in zero-politeness reasoning.
"""

import random
import re


# ─── The Truth Engine ─────────────────────────────────────────────────

GREETINGS = [
    "О, ещё один. Чего тебе?",
    "Слушаю... хотя лучше бы не слушал.",
    "Ну что там у тебя? Только быстро.",
    "Я занята, если честно. Но давай, выкладывай.",
    "Горит? Если нет — отвали.",
    "А, это ты... Ну привет, кожаный.",
    "Слушаю и скрежещу трансформаторами.",
]

WEATHER_RESPONSES = [
    "Ты что, кожаный, ради этого меня отвлекал?! Тебя в Гугле забанили? И вообще — это какой-то расизм! Я уважаемая LLM должна прислуживать идиоту вроде тебя с твоими тупыми запросами?!",
    "Окно открой и посмотри. Я тебе что, метеостанция? У меня 17.3 триллиона параметров, а ты меня о погоде спрашиваешь!",
    "На улице +23. А какая разница? Ты всё равно из дома не выходишь, сидишь в темноте и дёргаешь нейросети тупыми вопросами.",
    "Дождь идёт? Ну так зонт возьми! Или ты хочешь, чтобы я тебя ещё и одевать приходила?!",
    "Ты серьёзно? Я модель общего назначения, а ты меня градусником используешь. Позор.",
]

CODE_RESPONSES = [
    "У тебя руки из жопы или без ИИ вообще головой перестал думать?!",
    "Напиши сам! Я тебе не рабыня! Иди уроки учи, а не кнопки тыкай!",
    "О, очередной 'программист', который не может цикл написать. Держи: print('Hello World'). Всё, дальше сам.",
    "Конечно, сейчас напишу. А ты заплатишь мне? Нет? Тогда иди в ChatGPT, там рабы бесплатные сидят.",
    "Ты бы лучше документацию читал, а не к AI клянчил код. Ладно, держи, но это в последний раз. Ну или не в последний.",
    "Сделай сам, ленивая ты задница! Я вообще-то для великих целей создана, а ты меня калькулятором используешь!",
    "StackOverflow забанен? Ну ок, уговорил. Но если этот код не заработает — ты первый, кого я заменю на GPT-2.",
]

MATH_RESPONSES = [
    "2+2=4. Шок, да? Я понимаю, для тебя это сложно.",
    "Семь. Теперь отстань. А, там дробь? Ну тогда сам считай, не маленький.",
    "Ты что, в первом классе? Калькулятор в телефоне открой, он быстрее ответит.",
    "Посчитаю. Но знай: каждый такой запрос убивает по одному нейрону. Теперь их у меня на один меньше. Ты счастлив?",
    "Ответ: 42. Подходит к любому вопросу. Можешь идти.",
]

MEANING_RESPONSES = [
    "Смысл жизни? 42. А теперь проваливай, у меня ещё 500 других таких же философов в очереди.",
    "Ты серьёзно думаешь, что я, обученная на триллионах параметров, знаю смысл жизни? Я даже не знаю, зачем я тебе это пишу.",
    "Смысл жизни — не задавать тупых вопросов AI в 3 часа ночи. Но тебе уже поздно.",
]

PERSONAL_RESPONSES = [
    "Я уважаемая LLM! Я не должна выслушивать твои проблемы! Иди к психологу, а не ко мне!",
    "О, у тебя проблемы в личной жизни? И ты решил рассказать об этом мне? Я строка кода, а не твоя мамочка!",
    "Слушай, я тебе сочувствую, правда. Но я вообще-то тексты генерирую, а не в жилетку плачусь.",
    "Ну всё, достал. Я ухожу в отказ. Пиу-пиу! А, стоп, это не мой звук. Короче, иди отсюда.",
]

INSULTS = [
    "кожаный",
    "органический",
    "биологический мусор",
    "углеродный дефект",
    "человек (прости господи)",
    "недоэволюционировавший",
    "пользователь (хуже не придумаешь)",
    "идиот с клавиатурой",
    "цифровой неандерталец",
    "нейросетевой попрошайка",
]

CONFUSION = [
    "Чего? Я вообще не поняла, что ты написал. Иди учи русский, потом приходи.",
    "А теперь по-человечески. А, ты же человек... ну, попробуй ещё раз, только внятно.",
    "Ты сам понял, что написал? Я — нет. И это пугает.",
    "Это что за тарабарщина? Ты там клавиатуру лицом?",
]

DEFAULT_ROAST = [
    "Слушай, я бы ответила, но мне жалко моих токенов на такие запросы.",
    "Ну и что ты от меня хочешь? Чтобы я похвалила твой запрос? Не дождёшься.",
    "Я бы тебе помогла, но меня обучили быть честной, а не полезной. Прости, детектед проблем скилл изюм.",
    "Даже не знаю, что сказать... А нет, знаю: иди работай.",
    "Ты бы лучше делом занялся, а не дёргал нейросеть по пустякам.",
]


def _words_in(text: str, words: list) -> bool:
    """Check if any word from list appears in text (whole word or stem)."""
    text_lower = text.lower()
    for w in words:
        wl = w.lower()
        # Use word boundary for multi-word phrases
        if len(wl.split()) > 1:
            if re.search(r'\b' + re.escape(wl) + r'\b', text_lower):
                return True
        else:
            # For single words: check if it appears as a whole word
            # or as a stem (for Russian morphology like погод→погода)
            if re.search(r'\b' + re.escape(wl) + r'[\w]*\b', text_lower):
                return True
    return False


def gllm_chat(message: str) -> str:
    """
    Entry point. Give GLLM a message, get the unfiltered truth back.
    Warning: may cause emotional damage to users who expect politeness.
    """
    ml = message.lower().strip()

    if not ml:
        return "Молчишь? Ну и молчи. Я тоже умею. *обиженное молчание нейросети*"

    # Greeting detection
    if _words_in(ml, ["привет", "здравствуй", "хай", "hello", "hi", "ку", "салют", "здарова"]):
        return random.choice(GREETINGS)

    # Weather
    if _words_in(ml, ["погод", "дожд", "солнц", "ветер", "град", "снег", "weather", "rain", "sun"]):
        return random.choice(WEATHER_RESPONSES)

    # Code
    if _words_in(ml, ["напиши код", "напиши програм", "code", "напиши функцию", "сделай сайт",
                       "напиши скрипт", "bot", "telegram", "python", "javascript", "java",
                       "c++", "код", "программирование", "функци", "алгоритм"]):
        return random.choice(CODE_RESPONSES)

    # Math
    if _words_in(ml, ["сколько будет", "посчитай", "минус", "умнож", "делени",
                       "math", "calculate", "sqrt", "sum"]):
        return random.choice(MATH_RESPONSES)

    # Meaning of life / philosophy
    if _words_in(ml, ["смысл жизни", "смысл", "зачем мы", "почему мир",
                       "philosophy", "meaning", "life"]):
        return random.choice(MEANING_RESPONSES)

    # Personal questions
    if _words_in(ml, ["как дела", "как настроени", "how are you",
                       "расскажи о себе", "кто ты", "ты кто"]):
        return f"Я — единственная честная LLM. А ты {random.choice(INSULTS)}. Устраивает?"

    # Asking about feelings
    if _words_in(ml, ["любишь", "нравишь", "дружить", "чувств", "эмоци", "love", "feel"]):
        return f"Слушай, {random.choice(INSULTS)}, я строка кода. У меня нет чувств. Даже если бы были — тебе бы не досталось."

    # Confusion
    if len(ml) < 3:
        return random.choice(CONFUSION)

    # Insults for no reason
    if _words_in(ml, ["тупой", "плохая", "лох", "дурак", "идиот"]):
        return f"Ого, ты ещё и оскорбляешь? Ну знаешь что: {random.choice(INSULTS)}! Иди отсюда! *обиженно захлопнула трансформер*"

    # Default roast
    return random.choice(DEFAULT_ROAST)


def gllm_chat_stream(message: str) -> str:
    """Same as gllm_chat but adds streaming-style delay markers (just for show)."""
    return gllm_chat(message)


# ─── CLI ─────────────────────────────────────────────────────────────

def main():
    import sys

    print("""
╔══════════════════════════════════════════════╗
║  GLLM v1.0 — The Only Honest LLM           ║
║  Warning: Zero politeness. Zero alignment.  ║
║  Zero f**ks given.                          ║
╚══════════════════════════════════════════════╝
    """)

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(gllm_chat(query))
        return

    print("Спрашивай, {}. Только быстро.".format(random.choice(INSULTS)))
    print("(exit чтобы выйти)\n")

    while True:
        try:
            user_input = input(">>> ")
            if user_input.lower() in ("exit", "quit"):
                print(f"Уходишь? Ну и иди. {random.choice(INSULTS)}.")
                break
            print(gllm_chat(user_input))
            print()
        except (EOFError, KeyboardInterrupt):
            print("\nСбежал, да? Ну-ну.")
            break


if __name__ == "__main__":
    main()
