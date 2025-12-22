# bot_handler.py
import os
from telegram_bot import bot

async def handle_start_command(chat_id: int, username: str, start_param: str = None):
    """Обработка команды /start"""
    if start_param == "support":
        await bot.send_message(
            chat_id,
            "👋 Добро пожаловать в поддержку Mechboards Shop!\n\n"
            "Напишите ваш вопрос, и мы ответим в ближайшее время.",
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            chat_id,
            "👋 Добро пожаловать в Mechboards Shop!\n\n"
            "Используйте веб-приложение для просмотра товаров и услуг:",
            parse_mode="HTML"
        )

async def handle_message(chat_id: int, text: str, username: str):
    """Обработка сообщений от пользователей"""
    # Если сообщение от обычного пользователя, пересылаем администратору
    admin_ids = bot.get_admin_ids()
    
    for admin_id in admin_ids:
        await bot.send_message(
            admin_id,
            f"💬 <b>Сообщение от @{username}</b>\n\n"
            f"ID: {chat_id}\n"
            f"Сообщение: {text}\n\n"
            f"<i>Ответить: /reply_{chat_id} [сообщение]</i>",
            parse_mode="HTML"
        )
    
    await bot.send_message(
        chat_id,
        "✅ Ваше сообщение отправлено в поддержку. Мы ответим вам в ближайшее время.",
        parse_mode="HTML"
    )

async def handle_admin_reply(admin_id: int, user_id: int, message: str):
    """Обработка ответа администратора"""
    await bot.send_message(
        user_id,
        f"💬 <b>Ответ от поддержки Mechboards Shop</b>\n\n"
        f"{message}\n\n"
        f"<i>Для продолжения диалога просто ответьте на это сообщение.</i>",
        parse_mode="HTML"
    )