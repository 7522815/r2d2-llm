"""
R2D2 Group Bot systemd service — деплой на VPS.

1. Создай бота у @BotFather → получи токен
2. Настрой переменные и запусти:

   export R2D2_BOT_TOKEN="токен:от@BotFather"
   export R2D2_GROUP_ID="-1004319246642"
   python3 /root/r2d2-llm/r2d2_group_bot.py
"""

# systemd unit (сохранить как /etc/systemd/system/r2d2-bot.service)
SYSTEMD_UNIT = """
[Unit]
Description=R2D2 Group Bot — Auto-approve + Beep responses
After=network.target r2d2-llm.service
Wants=r2d2-llm.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/r2d2-llm
EnvironmentFile=/root/r2d2-llm/r2d2_bot.env
ExecStart=/usr/bin/python3 /root/r2d2-llm/r2d2_group_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

# env file (сохранить как /root/r2d2-llm/r2d2_bot.env)
ENV_FILE = """
R2D2_BOT_TOKEN=вставь_токен_сюда
R2D2_API_URL=http://localhost:6969/v1/chat/completions
R2D2_GROUP_ID=-1004319246642
"""

if __name__ == "__main__":
    print("📄 Systemd unit:")
    print(SYSTEMD_UNIT)
    print()
    print("📄 Env file (/root/r2d2-llm/r2d2_bot.env):")
    print(ENV_FILE)
    print()
    print("🚀 Deploy commands:")
    print("   nano /root/r2d2-llm/r2d2_bot.env    # вставь токен")
    print("   cp r2d2-bot.service /etc/systemd/system/")
    print("   systemctl daemon-reload")
    print("   systemctl enable --now r2d2-bot")
    print("   journalctl -u r2d2-bot -f           # смотреть логи")
