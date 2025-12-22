# bot_webhook.py
import os
import json
import logging
import aiohttp
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel

from telegram_bot import bot
from models import async_session, User
from sqlalchemy import select

router = APIRouter(prefix="/bot", tags=["telegram-bot"])

logger = logging.getLogger(__name__)

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict] = None
    callback_query: Optional[Dict] = None

class TelegramWebhookConfig:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL", "")
        self.admin_ids = self._parse_admin_ids()
        
    def _parse_admin_ids(self):
        admin_ids_str = os.getenv("ADMIN_TELEGRAM_IDS", "391622124")
        return [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]
    
config = TelegramWebhookConfig()

async def setup_webhook():
    """Установить вебхук для Telegram бота"""
    if not config.webhook_url:
        logger.warning("TELEGRAM_WEBHOOK_URL не установлен, вебхук не настроен")
        return False
    
    webhook_url = f"{config.webhook_url}/bot/webhook"
    
    try:
        url = f"https://api.telegram.org/bot{config.token}/setWebhook"
        payload = {
            "url": webhook_url,
            "drop_pending_updates": True,
            "allowed_updates": ["message", "callback_query"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                
                if result.get("ok"):
                    logger.info(f"✅ Вебхук установлен: {webhook_url}")
                    return True
                else:
                    logger.error(f"❌ Ошибка установки вебхука: {result}")
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Ошибка установки вебхука: {e}")
        return False

async def delete_webhook():
    """Удалить вебхук"""
    try:
        url = f"https://api.telegram.org/bot{config.token}/deleteWebhook"
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                result = await response.json()
                logger.info(f"Вебхук удален: {result}")
                return result.get("ok", False)
    except Exception as e:
        logger.error(f"Ошибка удаления вебхука: {e}")
        return False

@router.post("/webhook")
async def telegram_webhook(request: Request, background_tasks: BackgroundTasks):
    """Эндпоинт для вебхука от Telegram"""
    try:
        # Получаем обновление от Telegram
        update_data = await request.json()
        logger.debug(f"📨 Получено обновление: {update_data}")
        
        # Обрабатываем в фоновом режиме
        background_tasks.add_task(process_telegram_update, update_data)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_telegram_update(update_data: Dict):
    """Обработать обновление от Telegram"""
    try:
        # Обработка сообщений
        if "message" in update_data:
            message = update_data["message"]
            chat_id = message["chat"]["id"]
            text = message.get("text", "").strip()
            
            # Обработка команд
            if text.startswith("/"):
                await handle_command(chat_id, text, message)
            else:
                await handle_message(chat_id, text, message)
                
        # Обработка callback_query (для inline-кнопок)
        elif "callback_query" in update_data:
            callback = update_data["callback_query"]
            await handle_callback_query(callback)
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки обновления: {e}")

async def handle_command(chat_id: int, text: str, message: Dict):
    """Обработать команду"""
    # Разделяем команду и аргументы
    parts = text.split(" ", 1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    logger.info(f"🔧 Команда от {chat_id}: {command} {args}")
    
    if command == "/start":
        await handle_start_command(chat_id, message, args)
    elif command == "/help":
        await handle_help_command(chat_id)
    elif command.startswith("/reply_"):
        await handle_reply_command(chat_id, command, args, message)
    elif command == "/admin":
        await handle_admin_command(chat_id, args, message)
    elif command == "/stats":
        await handle_stats_command(chat_id)
    else:
        await bot.send_message(
            chat_id,
            "❓ Неизвестная команда. Используйте /help для списка команд.",
            parse_mode="HTML"
        )

async def handle_start_command(chat_id: int, message: Dict, args: str):
    """Обработка команды /start"""
    user_info = message.get("from", {})
    user_id = user_info.get("id")
    username = user_info.get("username", "")
    first_name = user_info.get("first_name", "")
    last_name = user_info.get("last_name", "")
    
    # Сохраняем/обновляем пользователя в базе
    await save_or_update_user(user_id, username, first_name, last_name)
    
    welcome_message = (
        f"👋 <b>Добро пожаловать в Mechboards Shop!</b>\n\n"
        f"Привет, {first_name}!\n"
        f"Я бот магазина механических клавиатур и аксессуаров.\n\n"
        f"<b>Доступные команды:</b>\n"
        f"• /help - помощь и список команд\n"
        f"• /support - связаться с поддержкой\n"
        f"• /catalog - посмотреть каталог\n"
        f"• /services - услуги магазина\n\n"
        f"<i>Также вы можете использовать наше веб-приложение для удобного заказа!</i>"
    )
    
    await bot.send_message(chat_id, welcome_message, parse_mode="HTML")
    
    # Если есть аргумент (deep linking)
    if args:
        if args.startswith("support_"):
            await handle_support_start(chat_id, user_info, args)

async def handle_help_command(chat_id: int):
    """Обработка команды /help"""
    help_message = (
        f"🛠️ <b>Помощь по боту Mechboards Shop</b>\n\n"
        f"<b>Основные команды:</b>\n"
        f"• /start - начать работу с ботом\n"
        f"• /help - эта справка\n"
        f"• /catalog - посмотреть каталог товаров\n"
        f"• /services - услуги магазина\n"
        f"• /support - связаться с поддержкой\n\n"
        f"<b>Для администраторов:</b>\n"
        f"• /admin - панель администратора\n"
        f"• /stats - статистика магазина\n"
        f"• /reply_[ID] [текст] - ответить пользователю\n\n"
        f"<b>Веб-приложение:</b>\n"
        f"Для полного доступа к функциям магазина используйте наше веб-приложение!"
    )
    
    await bot.send_message(chat_id, help_message, parse_mode="HTML")

async def handle_reply_command(chat_id: int, command: str, args: str, message: Dict):
    """Обработка команды /reply для ответа пользователям"""
    # Проверяем права администратора
    if chat_id not in config.admin_ids:
        await bot.send_message(
            chat_id,
            "⛔ У вас нет прав для выполнения этой команды.",
            parse_mode="HTML"
        )
        return
    
    # Извлекаем ID пользователя из команды
    try:
        # Команда вида /reply_123456789 Привет!
        user_id = int(command.replace("/reply_", "").split(" ")[0])
        reply_text = args
        
        if not reply_text:
            await bot.send_message(
                chat_id,
                "❌ Укажите текст ответа: /reply_ID текст_ответа",
                parse_mode="HTML"
            )
            return
        
        # Отправляем ответ пользователю
        await bot.send_message(
            user_id,
            f"💬 <b>Ответ от поддержки Mechboards Shop</b>\n\n"
            f"{reply_text}\n\n"
            f"<i>Для продолжения диалога просто ответьте на это сообщение.</i>",
            parse_mode="HTML"
        )
        
        # Уведомляем администратора
        await bot.send_message(
            chat_id,
            f"✅ Ответ отправлен пользователю {user_id}",
            parse_mode="HTML"
        )
        
    except ValueError:
        await bot.send_message(
            chat_id,
            "❌ Неверный формат команды. Используйте: /reply_ID текст_ответа",
            parse_mode="HTML"
        )

async def handle_admin_command(chat_id: int, args: str, message: Dict):
    """Обработка команды /admin"""
    if chat_id not in config.admin_ids:
        await bot.send_message(
            chat_id,
            "⛔ У вас нет прав для выполнения этой команды.",
            parse_mode="HTML"
        )
        return
    
    # Получаем статистику
    async with async_session() as session:
        # Статистика пользователей
        total_users = await session.execute(select(User).where(User.is_active == True))
        total_users_count = total_users.scalar_one_or_none()
        
        # Формируем сообщение
        admin_message = (
            f"👑 <b>Панель администратора</b>\n\n"
            f"<b>Статистика:</b>\n"
            f"• Пользователей: {total_users_count}\n"
            f"• Администраторов: {len(config.admin_ids)}\n\n"
            f"<b>Команды:</b>\n"
            f"• /stats - детальная статистика\n"
            f"• /broadcast [текст] - рассылка\n"
            f"• /reply_ID [текст] - ответить пользователю\n\n"
            f"<b>Веб-панель:</b>\n"
            f"Для полного управления используйте веб-панель администратора."
        )
        
        await bot.send_message(chat_id, admin_message, parse_mode="HTML")

async def handle_stats_command(chat_id: int):
    """Обработка команды /stats"""
    if chat_id not in config.admin_ids:
        await bot.send_message(
            chat_id,
            "⛔ У вас нет прав для выполнения этой команды.",
            parse_mode="HTML"
        )
        return
    
    # Здесь можно добавить получение статистики из базы данных
    stats_message = (
        f"📊 <b>Статистика магазина</b>\n\n"
        f"<b>Пользователи:</b>\n"
        f"• Всего: 0\n"
        f"• Активных: 0\n"
        f"• За сегодня: 0\n\n"
        f"<b>Заказы:</b>\n"
        f"• Всего: 0\n"
        f"• Сегодня: 0\n"
        f"• В работе: 0\n\n"
        f"<i>Для детальной статистики используйте веб-панель.</i>"
    )
    
    await bot.send_message(chat_id, stats_message, parse_mode="HTML")

async def handle_message(chat_id: int, text: str, message: Dict):
    """Обработка обычных сообщений"""
    user_info = message.get("from", {})
    user_id = user_info.get("id")
    username = user_info.get("username", "")
    first_name = user_info.get("first_name", "")
    
    # Сохраняем сообщение
    logger.info(f"💬 Сообщение от {user_id} (@{username}): {text}")
    
    # Если сообщение от администратора
    if user_id in config.admin_ids:
        # Проверяем, не является ли это ответом в треде
        if "reply_to_message" in message:
            await handle_admin_reply(chat_id, message)
        else:
            await bot.send_message(
                chat_id,
                "ℹ️ Используйте команды:\n"
                "/admin - панель администратора\n"
                "/help - список команд",
                parse_mode="HTML"
            )
    else:
        # Пересылаем сообщение администраторам
        await forward_to_admins(user_id, username, first_name, text)
        
        # Подтверждаем получение
        await bot.send_message(
            chat_id,
            "✅ Ваше сообщение получено. Мы ответим вам в ближайшее время.\n\n"
            "✉️ Для продолжения диалога просто пишите в этот чат.",
            parse_mode="HTML"
        )

async def handle_admin_reply(admin_id: int, message: Dict):
    """Обработка ответа администратора в треде"""
    reply_to = message.get("reply_to_message", {})
    original_text = reply_to.get("text", "")
    
    # Проверяем, является ли это пересланным сообщением от пользователя
    if "📨 Сообщение от пользователя" in original_text:
        # Извлекаем ID пользователя из оригинального сообщения
        lines = original_text.split("\n")
        user_id = None
        
        for line in lines:
            if "🆔 ID:" in line:
                user_id = int(line.replace("🆔 ID:", "").strip())
                break
        
        if user_id:
            reply_text = message.get("text", "")
            await bot.send_message(
                user_id,
                f"💬 <b>Ответ от поддержки Mechboards Shop</b>\n\n"
                f"{reply_text}\n\n"
                f"<i>Для продолжения диалога просто ответьте на это сообщение.</i>",
                parse_mode="HTML"
            )
            
            await bot.send_message(
                admin_id,
                f"✅ Ответ отправлен пользователю {user_id}",
                parse_mode="HTML"
            )

async def forward_to_admins(user_id: int, username: str, first_name: str, message_text: str):
    """Переслать сообщение всем администраторам"""
    admin_message = (
        f"📨 <b>Сообщение от пользователя</b>\n\n"
        f"👤 <b>Пользователь:</b> {first_name}\n"
        f"🆔 <b>ID:</b> {user_id}\n"
        f"👤 <b>Username:</b> @{username if username else 'нет'}\n"
        f"📝 <b>Сообщение:</b>\n{message_text}\n\n"
        f"💬 <b>Ответить:</b> Ответьте на это сообщение или используйте команду /reply_{user_id}"
    )
    
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(admin_id, admin_message, parse_mode="HTML")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки администратору {admin_id}: {e}")

async def handle_callback_query(callback: Dict):
    """Обработка callback_query (нажатие на inline-кнопку)"""
    chat_id = callback["from"]["id"]
    data = callback.get("data", "")
    
    # Здесь можно добавить обработку различных callback_data
    logger.info(f"🔄 Callback от {chat_id}: {data}")

async def handle_support_start(chat_id: int, user_info: Dict, args: str):
    """Обработка deep link для поддержки"""
    support_message = (
        f"🛠️ <b>Поддержка Mechboards Shop</b>\n\n"
        f"Привет, {user_info.get('first_name', '')}!\n"
        f"Вы перешли в чат поддержки.\n\n"
        f"<b>Как мы можем вам помочь?</b>\n"
        f"• Вопросы о товарах\n"
        f"• Помощь с заказом\n"
        f"• Консультация по услугам\n"
        f"• Технические проблемы\n\n"
        f"<i>Просто напишите ваш вопрос, и мы ответим в ближайшее время.</i>"
    )
    
    await bot.send_message(chat_id, support_message, parse_mode="HTML")

async def save_or_update_user(telegram_id: int, username: str, first_name: str, last_name: str):
    """Сохранить или обновить пользователя в базе"""
    try:
        async with async_session() as session:
            # Проверяем, существует ли пользователь
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            full_name = f"{first_name} {last_name}".strip()
            
            if user:
                # Обновляем существующего пользователя
                user.username = username or user.username
                user.name = full_name or user.name
                user.is_active = True
                logger.info(f"📝 Обновлен пользователь: {telegram_id}")
            else:
                # Создаем нового пользователя
                is_admin = telegram_id in config.admin_ids
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    name=full_name,
                    is_active=True,
                    is_admin=is_admin
                )
                session.add(user)
                logger.info(f"✅ Создан пользователь: {telegram_id} (admin: {is_admin})")
            
            await session.commit()
            
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения пользователя {telegram_id}: {e}")

@router.get("/info")
async def get_bot_info():
    """Получить информацию о боте"""
    try:
        url = f"https://api.telegram.org/bot{config.token}/getMe"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                result = await response.json()
                return result
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о боте: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/send")
async def send_message_via_bot(message: Dict):
    """Отправить сообщение через бота (для внутреннего использования)"""
    try:
        chat_id = message.get("chat_id")
        text = message.get("text")
        
        if not chat_id or not text:
            raise HTTPException(status_code=400, detail="chat_id and text are required")
        
        result = await bot.send_message(chat_id, text, parse_mode="HTML")
        return {"status": "success", "result": result}
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        raise HTTPException(status_code=500, detail=str(e))