from sqlalchemy import select
from models import async_session, User

async def add_user(tg_id: int):
    async with async_session() as session:
        # Проверяем, существует ли пользователь
        result = await session.execute(select(User).where(User.telegram_id == tg_id))
        user = result.scalar_one_or_none()
        if not user:
            # Создаем нового пользователя
            user = User(
                telegram_id=tg_id,
                username=f"user_{tg_id}",
                name=f"User {tg_id}",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user