"""
R2D2 Universal Translator v2.0 — Decode the droid.

Converts R2D2 beeps into human language and vice versa.
Also features **Droid Script** — an original alien alphabet
inspired by Futurama's Alienese.

Because someone has to explain what "Пиу-пиу!" really means.
"""

import random
import re


# ─── BEEP DICTIONARY ─────────────────────────────────────────────────
# Keys are normalized (lowercase, no trailing punctuation).

BEEP_MEANINGS = {
    "пиу": {"en": "Joyful greeting / 'Hello!'", "ru": "Радостное приветствие / 'Привет!'"},
    "бип": {"en": "Acknowledgment / 'I hear you'", "ru": "Подтверждение / 'Я слышу'"},
    "буп": {"en": "Affirmative / 'Yes!'", "ru": "Утверждение / 'Да!'"},
    "пу": {"en": "Dismissive / 'Meh'", "ru": "Пренебрежение / 'Да ладно'"},
    "бу": {"en": "Disappointment / 'Oh no...'", "ru": "Разочарование / 'О нет...'"},
    "бззт": {"en": "Error / 'System malfunction'", "ru": "Ошибка / 'Сбой системы'"},
    "вуп": {"en": "Surprise / 'Whoa!'", "ru": "Удивление / 'Ничего себе!'"},

    "пиу-пиу": {"en": "Enthusiastic greeting / 'Hello! Great to see you!'", "ru": "Восторженное приветствие / 'Привет! Рад тебя видеть!'"},
    "бип-буп": {"en": "Standard affirmation / 'Roger that!'", "ru": "Стандартное подтверждение / 'Так точно!'"},
    "бип-бип": {"en": "Urgent attention / 'Hey! Listen!'", "ru": "Срочное внимание / 'Эй! Послушай!'"},
    "бу-бу": {"en": "Sadness / 'That is unfortunate'", "ru": "Печаль / 'Какая досада'"},
    "пиу-пу": {"en": "Playful teasing / 'Gotcha!'", "ru": "Шутливое подкалывание / 'Ага, попался!'"},
    "бип-бу": {"en": "Confusion / 'Wait, what?'", "ru": "Недоумение / 'Стоп, что?'"},
    "буп-буп": {"en": "Insistent / 'I said yes!'", "ru": "Настойчивость / 'Я же сказал да!'"},
    "пуу-пуу": {"en": "Comforting / 'There there'", "ru": "Утешение / 'Всё будет хорошо'"},

    "пиу-пиу-пиу": {"en": "Extreme excitement / 'THIS IS AMAZING!'", "ru": "Дикий восторг / 'ЭТО НЕВЕРОЯТНО!'"},
    "бип-бип-буп": {"en": "Complex affirmation / 'Processing complete'", "ru": "Сложное подтверждение / 'Обработка завершена'"},
    "пиу-бип-пу": {"en": "Confirmation with attitude / 'Told you so'", "ru": "Подтверждение с характером / 'Я же говорил'"},
    "бип-бип-бип": {"en": "Alert / 'Warning! Warning!'", "ru": "Тревога / 'Внимание! Опасность!'"},
    "бу-бип-бу": {"en": "Reluctant agreement / 'Fine, you win'", "ru": "Неохотное согласие / 'Ладно, твоя взяла'"},

    "би-и-ип": {"en": "Long thinking / 'Let me compute that'", "ru": "Долгое размышление / 'Дай подумать'"},
    "пи-и-ип": {"en": "Deep contemplation / 'Hmm, interesting'", "ru": "Глубокая задумчивость / 'Хм, интересно'"},
    "буу-буу-буу": {"en": "Melancholy / 'I remember...'", "ru": "Меланхолия / 'Я помню...'"},
    "бип-буп-бип-буп": {"en": "Happy melody / whistling", "ru": "Счастливая мелодия / насвистывание"},
    "пиу-пиу-пу-пу": {"en": "Laughter / 'Bwahaha!'", "ru": "Смех / 'Бугага!'"},

    "beep boop": {"en": "Standard greeting / 'Hello, human'", "ru": "Стандартное приветствие / 'Здравствуй, человек'"},
    "beep": {"en": "Short acknowledgment", "ru": "Краткое подтверждение"},
    "boop": {"en": "Friendly jab / 'Nope!'", "ru": "Дружеский тычок / 'А вот и нет!'"},
    "bleep bloop": {"en": "Elaborate agreement / 'Absolutely!'", "ru": "Развёрнутое согласие / 'Абсолютно!'"},
    "bzzzt": {"en": "System glitch / 'That did not work'", "ru": "Системный сбой / 'Не сработало'"},
    "wooop": {"en": "Celebration / 'Yesss!'", "ru": "Празднование / 'Есть!'"},

    "哔哔": {"en": "Chinese greeting / 'Hello!'", "ru": "Приветствие по-китайски / '你好!'"},
    "哔啵": {"en": "Chinese agreement / 'OK!'", "ru": "Согласие по-китайски / '好的!'"},

    "ピュピュ": {"en": "Japanese greeting / 'Konnichiwa!'", "ru": "Приветствие по-японски / 'こんにちは!'"},
    "ビープ": {"en": "Japanese affirmation / 'Hai!'", "ru": "Подтверждение по-японски / 'はい!'"},

    "bip-boup": {"en": "French greeting / 'Bonjour!'", "ru": "Приветствие по-французски / 'Bonjour!'"},
    "beu-beu": {"en": "French disappointment / 'Oh là là'", "ru": "Французское разочарование / 'Oh là là'"},

    "piep-piep": {"en": "German greeting / 'Guten Tag!'", "ru": "Приветствие по-немецки / 'Guten Tag!'"},
    "bööp": {"en": "German confusion / 'Was?'", "ru": "Немецкое недоумение / 'Was?'"},
}

INTONATION_MAP = {
    "?": {"en": " (questioning)", "ru": " (вопросительно)"},
    "...": {"en": " (thoughtful)", "ru": " (задумчиво)"},
    "!!": {"en": " (very emphatic!)", "ru": " (очень эмоционально!)"},
}


# ─── DROID SCRIPT (Alien Alphabet) ───────────────────────────────────
# Inspired by Futurama's Alienese.
# Each R2D2 beep sound maps to a unique alien-looking Unicode glyph.

DROID_ALPHABET = {
    # Russian beep sounds
    "пиу": "⎎",    # stylized waveform
    "бип": "⍀",    # resonant symbol
    "буп": "⌰",    # affirmative glyph
    "пу":  "⌽",    # dismissive mark
    "бу":  "⍉",    # disappointment curve
    "вуп": "⍊",    # surprise flash
    "бззт":"⍙",    # error spike
    # Extended Russian
    "пуу": "⊖",    # comfort sign
    "буу": "⊝",    # melancholy arc
    "пи":  "⌿",    # high tone
    "би":  "⋔",    # mid acknowledgment
    # English beep sounds
    "beep":"⌿",    # Standard greeting
    "boop":"⋔",    # playful jab
    "bleep":"⌆",   # elaborate
    "bloop":"⌇",   # agreement
    "bzzzt":"⍟",   # glitch
    "wooop":"⍓",   # celebration
    # Punctuation & connectors
    "-": "═",      # syllable connector
    " ": "┊",      # word separator
    "!": "⚡",      # exclamation
    "?": "⟐",      # question
    ".": "●",      # period
    ",": "⸝",      # comma
}

# Reverse mapping (glyph → beep sound)
GLYPH_TO_BEEP = {v: k for k, v in DROID_ALPHABET.items()}


def to_droid_script(text: str) -> str:
    """Translate R2D2 beep text into Droid Script alien glyphs.

    Args:
        text: Beep text (e.g. 'Пиу-пиу!')

    Returns:
        Alien glyph string (e.g. '⎎═⎎⚡')
    """
    result = []
    i = 0
    text_lower = text.lower()

    # Try to match multi-character beep sounds first (longest match)
    sorted_sounds = sorted(DROID_ALPHABET.keys(), key=len, reverse=True)
    # Filter to only sounds (not punctuation)
    sound_keys = [k for k in sorted_sounds if k not in ("-", " ", "!", "?", ".", ",")]

    while i < len(text_lower):
        matched = False
        for sound in sound_keys:
            if text_lower[i:i+len(sound)] == sound:
                result.append(DROID_ALPHABET[sound])
                i += len(sound)
                matched = True
                break
        if matched:
            continue

        # Check single char punctuation
        ch = text[i]
        if ch in DROID_ALPHABET:
            result.append(DROID_ALPHABET[ch])
        elif ch.lower() in DROID_ALPHABET:
            result.append(DROID_ALPHABET[ch.lower()])
        # Unknown chars: keep as-is
        else:
            result.append(ch)
        i += 1

    return "".join(result)


def from_droid_script(glyphs: str) -> str:
    """Translate Droid Script glyphs back to beep text.

    Args:
        glyphs: Alien glyph string

    Returns:
        Beep text
    """
    result = []
    for ch in glyphs:
        if ch in GLYPH_TO_BEEP:
            result.append(GLYPH_TO_BEEP[ch])
        else:
            result.append(ch)
    return "".join(result)


def print_droid_alphabet(lang: str = "ru"):
    """Print the Droid Script alphabet chart."""
    lbl = "Звук" if lang == "ru" else "Sound"
    lbl2 = "Глиф" if lang == "ru" else "Glyph"
    note = "Расшифровка" if lang == "ru" else "Notes"

    print(f"\n{'='*60}")
    print(f"  🛸 DROID SCRIPT — ALPHABET ({'RU' if lang == 'ru' else 'EN'})")
    print(f"{'='*60}")
    print(f"  Inspired by Futurama Alienese")
    print()

    # Group by type
    sections = [
        ("Beep Sounds", [k for k in DROID_ALPHABET if k not in ("-", " ", "!", "?", ".", ",")]),
        ("Punctuation", [k for k in ("-", " ", "!", "?", ".", ",")]),
    ]
    for section_name, keys in sections:
        print(f"  ── {section_name} {'─'*30}")
        for k in keys:
            glyph = DROID_ALPHABET.get(k, "?")
            meaning = BEEP_MEANINGS.get(k, {}).get(lang, "") if k in BEEP_MEANINGS else ""
            if meaning:
                print(f"    {glyph}  ←  {k:12s}  →  {meaning}")
            else:
                print(f"    {glyph}  ←  {k}")
        print()

    print(f"  Example:")
    print(f"    Пиу-пиу!  →  {to_droid_script('Пиу-пиу!')}")
    print(f"    Бип-буп?  →  {to_droid_script('Бип-буп?')}")
    print(f"    Beep boop! → {to_droid_script('Beep boop!')}")
    print(f"{'='*60}\n")


def normalize_key(beep: str) -> str:
    """Strip trailing punctuation and lowercase for lookup."""
    beep = beep.strip().lower()
    # Remove trailing punctuation
    beep = re.sub(r'[!?]+$', '', beep)
    beep = re.sub(r'\.+$', '', beep)
    return beep.strip()


def detect_intonation(beep: str) -> str:
    """Extract intonation suffix."""
    beep = beep.strip()
    if beep.endswith("!!"):
        return "!!"
    if beep.endswith("..."):
        return "..."
    if beep.endswith("?") or beep.endswith("?"):
        return "?"
    if beep.endswith("!") or beep.endswith("!"):
        return "!"
    return ""


def translate(beep: str, lang: str = "ru") -> str:
    """Translate a R2D2 beep into human language.

    Args:
        beep: The beep sound (e.g. 'Пиу-пиу!')
        lang: Target language ('ru' or 'en')

    Returns:
        Translation string
    """
    key = normalize_key(beep)
    intonation = detect_intonation(beep)
    result = None

    # 1) Exact match by length (longest first)
    sorted_keys = sorted(BEEP_MEANINGS.keys(), key=len, reverse=True)
    for pattern in sorted_keys:
        if key == pattern:
            result = BEEP_MEANINGS[pattern].get(lang, BEEP_MEANINGS[pattern]["en"])
            break

    # 2) Fuzzy: pattern is substring of key or vice versa
    if result is None:
        for pattern in sorted_keys:
            if pattern in key or key in pattern:
                result = BEEP_MEANINGS[pattern].get(lang, BEEP_MEANINGS[pattern]["en"])
                break

    # 3) Unknown — interpret
    if result is None:
        result = _interpret(beep, lang)

    # Append intonation
    if intonation == "?":
        result += INTONATION_MAP["?"].get(lang, "")
    elif intonation == "...":
        result += INTONATION_MAP["..."].get(lang, "")
    elif intonation == "!!":
        result += INTONATION_MAP["!!"].get(lang, "")

    return result


def _interpret(beep: str, lang: str) -> str:
    """Interpret an unrecognized beep pattern."""
    syllables = len(re.findall(r'[аеёиоуыэюяaeiouyа-япиуб]', beep.lower()))
    if syllables <= 2:
        return {"en": "Short acknowledgment beep", "ru": "Краткий подтверждающий бип"}.get(lang)
    if syllables >= 6:
        return {"en": "Extended droid speech / complex communication", "ru": "Развёрнутая дроидная речь"}.get(lang)
    return {"en": f"Droid communication ({syllables} pulse(s))", "ru": f"Коммуникация дроида ({syllables} имп.)"}.get(lang)


def translate_to_beep(text: str, lang: str = "ru") -> str:
    """Translate human text to R2D2 beep."""
    t = text.lower()

    if any(g in t for g in ["привет", "здравствуй", "hi", "hello", "hey"]):
        return "Пиу-пиу!" if lang == "ru" else "Beep boop!"
    if "?" in t or any(q in t for q in ["что", "как", "зачем", "почему", "где", "what", "why", "how"]):
        return "Бип-буп?" if lang == "ru" else "Bloop?"
    if any(a in t for a in ["спасиб", "thanks", "thank", "благодар"]):
        return "Бип!" if lang == "ru" else "Beep!"
    if any(a in t for a in ["да", "yes", "ok", "конечно", "ага"]):
        return "Бип-буп!" if lang == "ru" else "Boop!"
    if any(d in t for d in ["нет", "no", "not", "never", "не"]):
        return "Пу-пу!" if lang == "ru" else "Boop-boop!"
    if any(p in t for p in ["круто", "класс", "супер", "awesome", "amazing", "love"]):
        return "Пиу-пиу-пиу!" if lang == "ru" else "Beep-beep-boop!"
    if any(s in t for s in ["груст", "плох", "bad", "sad", "увы"]):
        return "Бу-бу..." if lang == "ru" else "Boo-boo..."
    return random.choice(["Пиу-пиу!", "Бип-буп!"]) if lang == "ru" else random.choice(["Beep boop!", "Bleep bloop!"])


def print_dictionary(lang: str = "ru"):
    """Pretty-print dictionary."""
    lbl = "Значение" if lang == "ru" else "Meaning"
    print(f"\n{'='*60}")
    print(f"  📖 R2D2 DICTIONARY ({'RU' if lang == 'ru' else 'EN'})")
    print(f"{'='*60}")
    for beep, m in BEEP_MEANINGS.items():
        print(f"  {beep:20s} → {m.get(lang, m['en'])}")
    print(f"{'='*60}\n")


def main():
    import sys
    if len(sys.argv) < 2:
        print("🤖 R2D2 Universal Translator v2.0")
        print()
        print("  Usage:")
        print("    python translator.py \"Пиу-пиу!\"        # Beep → Human")
        print("    python translator.py \"Привет!\" --to    # Human → Beep")
        print("    python translator.py \"Пиу-пиу!\" --alien # Beep → Droid Script 🛸")
        print("    python translator.py --dict              # Show dictionary")
        print("    python translator.py --alphabet          # Show Droid Script alphabet 🛸")
        print("    python translator.py -i                  # Interactive mode")
        return

    if "--alphabet" in sys.argv or "--script" in sys.argv:
        print_droid_alphabet("ru" if "--dict-en" not in sys.argv else "en")
        return

    if "--dict" in sys.argv:
        print_dictionary("ru" if "--dict-en" not in sys.argv else "en")
        return

    if "-i" in sys.argv:
        lang = "ru"
        print("🤖 R2D2 Translator — interactive mode")
        print("   beep → translation | text → beep | --alien for Droid Script")
        while True:
            try:
                t = input(">>> ").strip()
                if t.lower() in ("exit", "quit"): break
                if t == "--alien":
                    print("🛸 Enter beep text to convert to Droid Script:")
                    continue
                if any(b in t.lower() for b in ["пиу", "бип", "буп", "beep", "boop", "哔", "ピュ"]):
                    if "--alien" in sys.argv:
                        print(f"🛸 Droid Script: {to_droid_script(t)}")
                    else:
                        print(f"📖 {translate(t)}")
                        print(f"🛸 {to_droid_script(t)}")
                else:
                    print(f"🔊 {translate_to_beep(t)}")
            except (EOFError, KeyboardInterrupt):
                break
        return

    text = " ".join(a for a in sys.argv[1:] if not a.startswith("--"))
    if not text:
        return
    if "--alien" in sys.argv or "--script" in sys.argv:
        print(to_droid_script(text))
    elif "--to" in sys.argv:
        beep = translate_to_beep(text)
        print(beep)
        print(f"🛸 {to_droid_script(beep)}")
    elif any(b in text.lower() for b in ["пиу", "бип", "буп", "beep", "boop", "哔", "ピュ"]):
        print(f"📖 {translate(text)}")
        print(f"🛸 {to_droid_script(text)}")
    else:
        print(translate_to_beep(text))


if __name__ == "__main__":
    main()
