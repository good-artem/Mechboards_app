# telegram_bot.py
import os
import aiohttp
import logging
from typing import Optional, Dict, Any, List

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

async def create_support_chat(self, user_id: int, user_name: str, initial_message: str = "") -> Dict[str, Any]:
    """Создать чат поддержки с пользователем"""
    # Отправляем приветственное сообщение
    welcome_message = (
        f"👋 <b>Добро пожаловать в поддержку Mechboards Shop!</b>\n\n"
        f"Привет, {user_name}!\n"
        f"Вы можете задать любой вопрос о товарах, услугах или заказах.\n\n"
        f"<i>Просто напишите ваш вопрос, и мы ответим как можно скорее.</i>"
    )
    
    result = await self.send_message(user_id, welcome_message)
    
    # Если есть начальное сообщение, пересылаем его администратору
    if initial_message:
        await self.forward_support_message_to_admin(
            user_id=user_id,
            user_name=user_name,
            message=initial_message
        )
    
    return result

async def forward_support_message_to_admin(self, user_id: int, user_name: str, message: str):
    """Переслать сообщение поддержки администратору"""
    admin_ids = self.get_admin_ids()
    
    admin_message = (
        f"🆘 <b>Новое обращение в поддержку</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_name}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"📝 <b>Сообщение:</b>\n{message}\n\n"
        f"💬 <b>Ответить:</b> /reply_{user_id}"
    )
    
    for admin_id in admin_ids:
        await self.send_message(admin_id, admin_message)

async def send_support_reply(self, admin_id: int, user_id: int, message: str):
    """Отправить ответ поддержки от администратора пользователю"""
    user_message = (
        f"💬 <b>Ответ от поддержки Mechboards Shop</b>\n\n"
        f"{message}\n\n"
        f"<i>С уважением, команда поддержки Mechboards Shop</i>\n"
        f"✉️ Для продолжения диалога просто ответьте на это сообщение"
    )
    
    return await self.send_message(user_id, user_message)

def get_admin_ids(self) -> List[int]:
    """Получить список ID администраторов"""
    # Можно получать из базы данных или переменных окружения
    admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS", "391622124")
    return [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

async def send_direct_message(self, user_id: int, message: str, is_support: bool = False):
    """Отправить прямое сообщение пользователю"""
    if is_support:
        message = f"💬 <b>Сообщение от поддержки:</b>\n\n{message}"
    
    return await self.send_message(user_id, message)

# telegram_bot.py - добавьте в класс TelegramBot
async def broadcast_message(self, message: str, chat_ids: List[int]):
    """Отправить сообщение нескольким пользователям"""
    results = []
    for chat_id in chat_ids:
        try:
            result = await self.send_message(chat_id, message)
            results.append({"chat_id": chat_id, "success": result.get("ok", False)})
        except Exception as e:
            results.append({"chat_id": chat_id, "success": False, "error": str(e)})
    
    return results

async def send_support_notification(self, user_id: int, user_name: str, message: str):
    """Отправить уведомление о поддержке"""
    admin_ids = self.get_admin_ids()
    
    formatted_message = (
        f"🆘 <b>Новое обращение в поддержку</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_name}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"📝 <b>Сообщение:</b>\n{message}\n\n"
        f"💬 <b>Ответить:</b> Ответьте на это сообщение"
    )
    
    for admin_id in admin_ids:
        await self.send_message(admin_id, formatted_message)
        
async def send_support_message(self, telegram_id: int, subject: str, message: str):
    """Отправить сообщение поддержки администратору"""
    admin_id = os.getenv("ADMIN_TELEGRAM_ID", "391622124")
    try:
        admin_id = int(admin_id)
        formatted_message = (
            f"🆘 <b>Сообщение от пользователя</b>\n\n"
            f"👤 Пользователь: ID {telegram_id}\n"
            f"📝 Тема: {subject}\n"
            f"💬 Сообщение:\n{message}\n\n"
            f"💌 Для ответа используйте команду:\n"
            f"/reply {telegram_id} ваш ответ"
        )
        
        return await self.send_message(admin_id, formatted_message)
    except ValueError:
        logger.error(f"Invalid admin ID: {admin_id}")
        return None

async def send_reply_to_user(self, user_id: int, message: str):
    """Отправить ответ пользователю"""
    user_message = (
        f"💬 <b>Ответ от поддержки</b>\n\n"
        f"Сообщение:\n{message}\n\n"
        f"Спасибо за обращение! ❤️"
    )
    
    return await self.send_message(user_id, user_message)

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