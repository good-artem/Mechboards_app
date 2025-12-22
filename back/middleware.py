from fastapi import Request, HTTPException
from sqlalchemy import select
from models import async_session, User
import logging

logger = logging.getLogger(__name__)

async def admin_middleware(request: Request, call_next):
    """Middleware для проверки прав администратора"""
    
    # Разрешаем OPTIONS запросы (для CORS)
    if request.method == "OPTIONS":
        return await call_next(request)
    
    # Пропускаем публичные эндпоинты
    if not request.url.path.startswith("/api/admin/"):
        return await call_next(request)
    
    # Пропускаем проверки администратора
    if request.url.path.startswith("/api/admin/check") or request.url.path.startswith("/api/admin/test"):
        return await call_next(request)
    
    # Получаем Telegram init data из заголовков
    init_data = request.headers.get('x-telegram-init-data', '')
    
    if not init_data:
        logger.warning(f"Admin access attempt without Telegram auth: {request.url.path}")
        raise HTTPException(status_code=401, detail="Telegram authentication required")
    
    # Извлекаем telegram_id из init_data
    try:
        import json
        from urllib.parse import parse_qsl
        
        parsed_data = dict(parse_qsl(init_data))
        user_str = parsed_data.get('user')
        
        if not user_str:
            logger.warning(f"Admin access attempt without user data: {request.url.path}")
            raise HTTPException(status_code=401, detail="User data not found")
        
        user_data = json.loads(user_str)
        telegram_id = user_data.get('id')
        
        if not telegram_id:
            logger.warning(f"Admin access attempt with invalid user data: {request.url.path}")
            raise HTTPException(status_code=401, detail="Invalid user data")
        
    except Exception as e:
        logger.error(f"Error parsing Telegram init data: {e}")
        raise HTTPException(status_code=401, detail="Invalid Telegram auth data")
    
    # Проверяем, является ли пользователь администратором
    async with async_session() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id,
                User.is_admin == True
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Non-admin access attempt: {telegram_id} -> {request.url.path}")
            raise HTTPException(
                status_code=403, 
                detail="Administrator privileges required"
            )
        
        logger.info(f"Admin access granted: {user.name} ({telegram_id}) -> {request.url.path}")
        
        # Добавляем пользователя в состояние запроса
        request.state.admin_user = user
        
        return await call_next(request)