from sqlalchemy import select, update
from models import async_session, User, Task

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

async def get_tasks(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.user == user_id))
        tasks = result.scalars().all()
        return tasks

async def get_completed_tasks_count(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(Task).where(Task.user == user_id, Task.completed == True))
        completed_tasks = result.scalars().all()
        return len(completed_tasks)

async def add_task(user_id: int, title: str):
    async with async_session() as session:
        task = Task(
            title=title,
            user=user_id,
            completed=False
        )
        session.add(task)
        await session.commit()

async def update_task(task_id: int):
    async with async_session() as session:
        await session.execute(
            update(Task).
            where(Task.id == task_id).
            values(completed=True)
        )
        await session.commit()