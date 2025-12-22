# telegram_bot.py
import os
import aiohttp
import logging
from typing import Optional, Dict, Any

# Настройка логирования
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("Telegram Bot Token is required")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    async def send_message(
        self, 
        chat_id: int, 
        text: str, 
        parse_mode: str = "HTML",
        reply_markup: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Отправить сообщение пользователю"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        if reply_markup:
            payload["reply_markup"] = reply_markup
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Telegram API error: {error_text}")
                        return {"ok": False, "error": error_text}
                    
                    result = await response.json()
                    logger.info(f"Message sent to {chat_id}: {text[:50]}...")
                    return result
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"ok": False, "error": str(e)}
    
    async def send_order_notification(self, telegram_id: int, order_data: Dict):
        """Отправить уведомление о заказе"""
        message = (
            f"📦 <b>Новый заказ!</b>\n\n"
            f"Номер заказа: {order_data.get('order_number', 'N/A')}\n"
            f"Сумма: {order_data.get('total_amount', 0):.2f} р.\n"
            f"Способ доставки: {order_data.get('shipping_method', 'Не указан')}\n"
            f"Адрес: {order_data.get('shipping_address', 'Не указан')}\n\n"
            f"Статус: {order_data.get('status', 'Создан')}"
        )
        
        result = await self.send_message(telegram_id, message)
        logger.info(f"Order notification sent to {telegram_id}")
        return result
    
    async def send_admin_notification(self, message: str):
        """Отправить уведомление администратору"""
        admin_id = os.getenv("ADMIN_TELEGRAM_ID", "391622124")
        try:
            admin_id = int(admin_id)
            result = await self.send_message(admin_id, message)
            logger.info(f"Admin notification sent: {message[:50]}...")
            return result
        except ValueError:
            logger.error(f"Invalid admin ID: {admin_id}")
            return None
    
    async def send_support_notification(self, message: str, chat_id: Optional[int] = None):
        """Отправить уведомление о поддержке"""
        if chat_id:
            return await self.send_message(chat_id, message)
        else:
            return await self.send_admin_notification(message)

    async def forward_to_admin(self, user_id: int, user_name: str, message: str):
        """Переслать сообщение от пользователя администратору"""
        admin_id = os.getenv("ADMIN_TELEGRAM_ID", "391622124")
        try:
            admin_id = int(admin_id)
            formatted_message = (
                f"🆘 <b>Сообщение от пользователя</b>\n\n"
                f"👤 Пользователь: {user_name}\n"
                f"🆔 ID: {user_id}\n"
                f"📝 Сообщение:\n{message}\n\n"
                f"💬 Ответить: /reply_{user_id}"
            )
            
            return await self.send_message(admin_id, formatted_message)
        except ValueError:
            logger.error(f"Invalid admin ID: {admin_id}")
            return None

    async def forward_to_user(self, user_id: int, message: str, from_admin: str = "Администратор"):
        """Переслать сообщение от администратора пользователю"""
        formatted_message = (
            f"💬 <b>Ответ от поддержки</b>\n\n"
            f"От: {from_admin}\n"
            f"Сообщение:\n{message}\n\n"
            f"✉️ Для продолжения диалога просто ответьте на это сообщение"
        )
        
        return await self.send_message(user_id, formatted_message)


# Глобальный экземпляр бота с логированием
bot = TelegramBot()

# Функция для инициализации логирования
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('bot.log')
        ]
    )