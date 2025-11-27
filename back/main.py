from contextlib import asynccontextmanager
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import init_db, async_session
import my_requests as rq
from sqlalchemy import select
from typing import List, Optional

# Pydantic модели для запросов
class AddTask(BaseModel):
    tg_id: int
    title: str

class CompleteTask(BaseModel):
    id: int

class AddToCartRequest(BaseModel):
    telegram_id: int
    product_id: int
    quantity: int = 1

class CreateOrderRequest(BaseModel):
    telegram_id: int
    shipping_method: str
    shipping_address: str
    customer_notes: Optional[str] = None

@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Database initialized')
    yield

app = FastAPI(title="Mechboards shop", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Существующие endpoints для задач (можно удалить позже)
@app.get("/api/tasks/{tg_id}")
async def tasks(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_tasks(user.id)

@app.get("/api/main/{tg_id}")
async def profile(tg_id: int):
    user = await rq.add_user(tg_id)
    completed_tasks_count = await rq.get_completed_tasks_count(user.id)
    return {'completedTasks': completed_tasks_count}

@app.post("/api/add")
async def add_task(task: AddTask):
    user = await rq.add_user(task.tg_id)
    await rq.add_task(user.id, task.title)
    return {'status': 'ok'}

@app.patch("/api/completed")
async def complete_task(task: CompleteTask):
    await rq.update_task(task.id)
    return {'status': 'ok'}

# Новые endpoints для магазина
@app.get("/api/categories")
async def get_categories():
    async with async_session() as session:
        result = await session.execute(select(models.Category).where(models.Category.parent_id == None))
        categories = result.scalars().all()
        return categories

@app.get("/api/products")
async def get_products(category_id: Optional[int] = None, limit: int = 20, offset: int = 0):
    async with async_session() as session:
        query = select(models.Product).where(models.Product.is_available == True)
        if category_id:
            query = query.where(models.Product.category_id == category_id)
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        products = result.scalars().all()
        return products

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    async with async_session() as session:
        result = await session.execute(select(models.Product).where(models.Product.product_id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

@app.post("/api/cart/add")
async def add_to_cart(request: AddToCartRequest):
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(models.User).where(models.User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Находим или создаем корзину
        cart_result = await session.execute(
            select(models.Cart).where(models.Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            cart = models.Cart(user_id=user.user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        # Добавляем товар в корзину
        cart_item = models.CartItem(
            cart_id=cart.cart_id,
            product_id=request.product_id,
            quantity=request.quantity
        )
        session.add(cart_item)
        await session.commit()
        
        return {"status": "success", "message": "Product added to cart"}

@app.get("/api/cart/{telegram_id}")
async def get_cart(telegram_id: int):
    async with async_session() as session:
        # Находим пользователя и его корзину
        user_result = await session.execute(
            select(models.User).where(models.User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        cart_result = await session.execute(
            select(models.Cart).where(models.Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            return {"items": [], "total": 0}
        
        # Получаем товары в корзине
        cart_items_result = await session.execute(
            select(models.CartItem).where(models.CartItem.cart_id == cart.cart_id)
        )
        cart_items = cart_items_result.scalars().all()
        
        items = []
        total = 0
        
        for item in cart_items:
            product_result = await session.execute(
                select(models.Product).where(models.Product.product_id == item.product_id)
            )
            product = product_result.scalar_one()
            
            items.append({
                "cart_item_id": item.cart_item_id,
                "product": product,
                "quantity": item.quantity,
                "subtotal": float(product.price) * item.quantity
            })
            total += float(product.price) * item.quantity
        
        return {"items": items, "total": total}

@app.post("/api/orders/create")
async def create_order(request: CreateOrderRequest):
    async with async_session() as session:
        # Находим пользователя и его корзину
        user_result = await session.execute(
            select(models.User).where(models.User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        cart_result = await session.execute(
            select(models.Cart).where(models.Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Получаем товары из корзины
        cart_items_result = await session.execute(
            select(models.CartItem).where(models.CartItem.cart_id == cart.cart_id)
        )
        cart_items = cart_items_result.scalars().all()
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Считаем общую сумму
        total_amount = 0
        for item in cart_items:
            product_result = await session.execute(
                select(models.Product).where(models.Product.product_id == item.product_id)
            )
            product = product_result.scalar_one()
            total_amount += float(product.price) * item.quantity
        
        # Создаем заказ
        import uuid
        order_number = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
        
        order = models.Order(
            user_id=user.user_id,
            order_number=order_number,
            total_amount=total_amount,
            shipping_method=request.shipping_method,
            shipping_address=request.shipping_address,
            customer_notes=request.customer_notes
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        # Добавляем товары в заказ
        for item in cart_items:
            product_result = await session.execute(
                select(models.Product).where(models.Product.product_id == item.product_id)
            )
            product = product_result.scalar_one()
            
            order_item = models.OrderItem(
                order_id=order.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
                total_price=float(product.price) * item.quantity
            )
            session.add(order_item)
        
        # Очищаем корзину
        await session.execute(
            models.CartItem.__table__.delete().where(models.CartItem.cart_id == cart.cart_id)
        )
        
        await session.commit()
        
        return {"status": "success", "order_number": order_number, "order_id": order.order_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)