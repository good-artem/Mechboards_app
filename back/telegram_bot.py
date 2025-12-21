# telegram_bot.py
import os
import aiohttp
from typing import Optional, Dict, Any

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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Telegram API error: {error_text}")
                    return {"ok": False, "error": error_text}
                
                return await response.json()
    
    async def send_order_notification(self, telegram_id: int, order_data: Dict):
        """Отправить уведомление о заказе"""
        message = (
            f"📦 <b>Новый заказ!</b>\n\n"
            f"Номер заказа: {order_data.get('order_number', 'N/A')}\n"
            f"Сумма: {order_data.get('total_amount', 0):.2f} ₽\n"
            f"Способ доставки: {order_data.get('shipping_method', 'Не указан')}\n"
            f"Адрес: {order_data.get('shipping_address', 'Не указан')}\n\n"
            f"Статус: {order_data.get('status', 'Создан')}"
        )
        
        return await self.send_message(telegram_id, message)
    
    async def send_admin_notification(self, message: str):
        """Отправить уведомление администратору"""
        admin_id = os.getenv("ADMIN_TELEGRAM_ID", "391622124")
        try:
            admin_id = int(admin_id)
            return await self.send_message(admin_id, message)
        except ValueError:
            print(f"❌ Invalid admin ID: {admin_id}")
            return None

# Создайте глобальный экземпляр бота
bot = TelegramBot()