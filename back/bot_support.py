import os
import asyncio
import aiohttp
import logging
from typing import Optional
import sys

# Добавляем путь к текущей директории
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import async_session, User
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupportBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.admin_id = int(os.getenv("ADMIN_TELEGRAM_ID", "391622124"))
    
    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML"):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return await response.json()
    
    async def get_updates(self, offset: Optional[int] = None):
        url = f"{self.base_url}/getUpdates"
        params = {"timeout": 30}
        if offset:
            params["offset"] = offset
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                return await response.json()
    
    async def process_message(self, message: dict):
        try:
            chat_id = message["chat"]["id"]
            text = message.get("text", "")
            
            # Команда /start
            if text.startswith("/start"):
                await self.send_message(
                    chat_id,
                    "👋 Привет! Я бот поддержки Mechboards Shop.\n\n"
                    "📞 Для связи с поддержкой используйте веб-приложение.\n"
                    "🛠️ Администраторы отвечают в рабочее время."
                )
            
            # Команда /reply для администратора
            elif text.startswith("/reply") and str(chat_id) == str(self.admin_id):
                parts = text.split(" ", 2)
                if len(parts) >= 3:
                    user_id = int(parts[1])
                    reply_text = parts[2]
                    
                    await self.send_message(
                        user_id,
                        f"💬 <b>Ответ от поддержки</b>\n\n{reply_text}"
                    )
                    await self.send_message(
                        chat_id,
                        f"✅ Ответ отправлен пользователю {user_id}"
                    )
                else:
                    await self.send_message(
                        chat_id,
                        "Используйте: /reply <user_id> <сообщение>"
                    )
            
            # Любое другое сообщение от администратора
            elif str(chat_id) == str(self.admin_id):
                await self.send_message(
                    chat_id,
                    "ℹ️ Для ответа пользователю используйте команду:\n"
                    "/reply <user_id> <ваше сообщение>\n\n"
                    "📱 Или напишите напрямую в Telegram"
                )
            
            # Сообщение от пользователя (пересылаем администратору)
            else:
                user_name = message.get("from", {}).get("first_name", "Пользователь")
                user_message = f"📩 <b>Сообщение от {user_name}</b>\n\n{text}\n\nID: {chat_id}"
                
                await self.send_message(self.admin_id, user_message)
                await self.send_message(
                    chat_id,
                    "✅ Ваше сообщение переслано администратору.\n"
                    "Ответ придет в этот чат."
                )
                
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
    
    async def run(self):
        logger.info("Бот поддержки запущен...")
        offset = None
        
        while True:
            try:
                updates = await self.get_updates(offset)
                
                if updates.get("ok"):
                    for update in updates.get("result", []):
                        offset = update["update_id"] + 1
                        
                        if "message" in update:
                            await self.process_message(update["message"])
                
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Требуется TELEGRAM_BOT_TOKEN")
        sys.exit(1)
    
    bot = SupportBot(token)
    
    # Запускаем бота
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")