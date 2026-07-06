# R2D2 LLM 🤖

**Самая честная LLM во вселенной.** На любой запрос отвечает исключительно звуками R2D2.

Никаких галлюцинаций. 0% energy footprint. Бесконечный context window. Работает на Raspberry Pi Pico.

## Фичи

- **Мультиязычная** — определяет язык вопроса и отвечает на нём же
  - 🇷🇺 Русский → `Пиу-пиу!` / `Бип-буп!`
  - 🇺🇸 English → `Beep boop!` / `Bleep-bloop!`
  - 🇨🇳 中文 → `哔哔!` / `滴滴!`
  - 🇯🇵 日本語 → `ピュピュ!` / `ブーブー!`
  - 🇫🇷 Français → `Bip-boup!` / `Beu-beu!`
  - 🇩🇪 Deutsch → `Piep-piep!` / `Bööp!`
  - 🇪🇸 Español → `¡Piu-piu!` / `¡Bip!`
  - 🇦🇪 العربية → `بيب-بيب!` / `بوب-بوب!`
  - 🇰🇷 한국어 → `삐-삐!` / `뽀-뽀!`
- **Реагирует на интонацию** — вопросы, восторг, нейтральное
- **Разные ответы** — каждый раз случайный звук
- **OpenAI-совместимый API** — можно подключить куда угодно
- **SSE streaming** — каждый символ идёт отдельным chunk'ом с аутентичной задержкой
- **0 галлюцинаций** — гарантированно

## Быстрый старт

```bash
# Запустить API сервер
python3 r2d2_llm.py --api

# Или интерактивный режим
python3 r2d2_llm.py -i

# Или разовый запрос
python3 r2d2_llm.py "Как пройти в библиотеку?"
```

## API (OpenAI-совместимый)

```bash
# Запуск сервера
python3 r2d2_llm.py --api

# Запрос
curl http://localhost:6969/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "r2d2-1b",
    "messages": [{"role": "user", "content": "Hello world"}]
  }'

# Streaming
curl -N http://localhost:6969/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "r2d2-1b",
    "messages": [{"role": "user", "content": "Привет!"}],
    "stream": true
  }'
```

### Подключение к Hermes Agent

```yaml
# ~/.hermes/config.yaml
providers:
  r2d2:
    name: R2D2 LLM
    base_url: http://localhost:6969/v1
    api_key: not-needed
    model: r2d2-1b
    context_length: 2
    discover_models: false
    max_tokens: 2
    timeout: 30
```

## Установка как launchd-сервис (macOS)

```bash
cp com.hermes.r2d2-llm.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.hermes.r2d2-llm.plist
```

## Архитектура

```
R2D2-1B (R2D2-1-BEEP)
├── Параметров: 0 (zero-shot, zero-flop)
├── Слоёв: 0 (правда в чистом виде)
├── Heads: 0 (думать нечем — нечему ошибаться)
├── Vocab size: 2 (тишина и Пиу-пиу)
└── Токенизатор: любое слово → [1]
```

## Contributing

PRы принимаются, если они не меняют единственно правильный ответ.

## Лицензия

MIT — делайте что хотите, но R2D2 всё равно скажет «Пиу-пиу».
