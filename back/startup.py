# startup.py
import asyncio
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

async def initialize():
    """Инициализировать приложение"""
    print("🚀 Инициализация Mechboards Shop...")
    
    # Проверяем необходимые переменные окружения
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные окружения: {missing_vars}")
        sys.exit(1)
    
    # Инициализируем базу данных
    from models import init_db
    await init_db()
    print("✅ База данных инициализирована")
    
    # Настраиваем вебхук
    from bot_webhook import setup_webhook
    webhook_result = await setup_webhook()
    
    if webhook_result:
        print("✅ Telegram вебхук настроен")
    else:
        print("⚠️ Не удалось настроить Telegram вебхук")
    
    print("✨ Инициализация завершена!")

if __name__ == "__main__":
    asyncio.run(initialize())