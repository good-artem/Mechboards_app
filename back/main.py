from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Form, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from models import init_db, async_session, Category, Product, User, Cart, CartItem, Order, OrderItem, News, Service, ServiceOrder, OrderStatus, CartServiceItem
from sqlalchemy import String, select, func, text
from typing import List, Optional
import uuid
from datetime import datetime
import os
import hashlib
import hmac
import json
from urllib.parse import parse_qsl
from sqlalchemy.orm import selectinload
from fastapi import Query
from telegram_bot import bot

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Функция для проверки хэша (для безопасности)
def verify_telegram_hash(init_data: str) -> bool:
    try:
        parsed_data = dict(parse_qsl(init_data))
        received_hash = parsed_data.get('hash')
        if not received_hash:
            return False

        # Получаем токен бота
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN не установлен!")
            return False

        # Собираем строку для проверки (разделитель - '\n')
        data_check_string = '\n'.join(
            [f'{k}={v}' for k, v in sorted(parsed_data.items()) if k != 'hash']
        )
        
        print(f"🔍 Data check string: {data_check_string}")
        
        # Создаем секретный ключ: HMAC_SHA256(bot_token, "WebAppData")
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Вычисляем HMAC-SHA256 от data_check_string
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        print(f"🔍 Received hash: {received_hash}")
        print(f"🔍 Calculated hash: {calculated_hash}")
        
        return hmac.compare_digest(calculated_hash, received_hash)
        
    except Exception as e:
        print(f"❌ Ошибка проверки хэша: {e}")
        import traceback
        traceback.print_exc()
        return False
        
def get_telegram_user_from_init_data(init_data: str):
    """
    Извлекает пользователя Telegram из initData
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
        user_str = parsed_data.get('user')
        if not user_str:
            return None
        user_data = json.loads(user_str)
        return user_data
    except Exception:
        return None
     
def verify_user_access(telegram_id: int, init_data: str):
    """
    Проверяет, что пользователь имеет доступ к ресурсу с данным telegram_id
    """
    # Проверяем хэш Telegram
    if not verify_telegram_hash(init_data):
        raise HTTPException(
            status_code=401,
            detail="Невалидная авторизация Telegram"
        )
    # Получаем пользователя из initData
    user_data = get_telegram_user_from_init_data(init_data)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Данные пользователя не найдены"
        )
    # Проверяем, что пользователь запрашивает СВОИ данные
    if user_data.get('id') != telegram_id:
        raise HTTPException(
            status_code=403,
            detail="Доступ запрещен. Вы можете запрашивать только свои данные"
        )
    return user_data

# Pydantic модели для запросов
class AddToCartRequest(BaseModel):
    telegram_id: int
    product_id: int
    quantity: int = 1

class CreateOrderRequest(BaseModel):
    telegram_id: int
    shipping_method: str
    shipping_address: str
    customer_notes: Optional[str] = None

# --- Добавьте эту модель для заказа услуги ---
class CreateServiceOrderRequest(BaseModel):
    telegram_id: int
    service_id: int
    notes: Optional[str] = None
# --- Конец добавления ---

class CreateUserRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: Optional[str] = None

class UpdateCartItemRequest(BaseModel):
    cart_item_id: int
    quantity: int

class RemoveCartItemRequest(BaseModel):
    cart_item_id: int

class AddServiceToCartRequest(BaseModel):
    telegram_id: int
    service_id: int
    quantity: int = 1
    notes: Optional[str] = None

class UpdateCartServiceItemRequest(BaseModel):
    cart_service_item_id: int
    quantity: int
    notes: Optional[str] = None

class RemoveCartServiceItemRequest(BaseModel):
    cart_service_item_id: int

@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Database initialized')
    yield

app = FastAPI(title="Mechboards shop", lifespan=lifespan)
app.mount("/assets", StaticFiles(directory="../front/src/assets"), name="assets")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Публичные эндпоинты (не требуют авторизации)
@app.get("/api/categories")
async def get_categories():
    async with async_session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        return categories

@app.get("/api/products")
async def get_products(category_id: Optional[int] = None, limit: int = 20, offset: int = 0):
    async with async_session() as session:
        query = select(Product).where(Product.is_available == True).options(selectinload(Product.category))
        if category_id:
            query = query.where(Product.category_id == category_id)
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        products = result.scalars().all()
        # Преобразуем для фронтенда
        result_products = []
        for product in products:
            product_dict = {
                "product_id": product.product_id,
                "name": product.name,
                "description": product.description,
                "price": float(product.price),
                "stock_quantity": product.stock_quantity,
                "category_id": product.category_id,
                "is_available": product.is_available,
                "images": json.loads(product.images) if product.images else []
            }
            if product.category:
                product_dict["category"] = {
                    "category_id": product.category.category_id,
                    "name": product.category.name,
                    "description": product.category.description,
                    "icon": product.category.icon
                }
            result_products.append(product_dict)
        return result_products

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.product_id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {
            "product_id": product.product_id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "stock_quantity": product.stock_quantity,
            "category_id": product.category_id,
            "is_available": product.is_available,
            "images": json.loads(product.images) if product.images else []
        }

@app.get("/api/news")
async def get_news():
    async with async_session() as session:
        # Получаем только активные новости, которые еще не истекли
        result = await session.execute(
            select(News).where(
                News.is_active == True,
                (News.expires_at.is_(None)) | (News.expires_at > datetime.now())
            ).order_by(News.created_at.desc())
        )
        news_items = result.scalars().all()
        return [{
            "news_id": item.news_id,
            "title": item.title,
            "description": item.description,
            "icon": item.icon,
            "image_url": item.image_url,
            "news_type": item.news_type,
            "action_url": item.action_url,
            "is_active": item.is_active,
            "created_at": item.created_at.isoformat(),
            "expires_at": item.expires_at.isoformat() if item.expires_at else None
        } for item in news_items]

@app.get("/api/products/search")
async def search_products(
    q: str = Query("", description="Поисковый запрос"),
    category_id: Optional[int] = Query(None, description="ID категории"),
    limit: int = Query(20, ge=1, le=100, description="Лимит"),
    offset: int = Query(0, ge=0, description="Смещение")
):
    async with async_session() as session:
        try:
            # Преобразуем q в строку, даже если он None
            search_term = q if q else ""
            
            query = select(Product).where(
                Product.is_available == True
            ).options(selectinload(Product.category))
            
            # Поиск по названию
            if search_term.strip():
                query = query.where(Product.name.ilike(f"%{search_term.strip()}%"))
            
            # Фильтр по категории
            if category_id is not None:
                query = query.where(Product.category_id == category_id)
            
            query = query.limit(limit).offset(offset)
            result = await session.execute(query)
            products = result.scalars().all()
            
            # Преобразуем для фронтенда
            result_products = []
            for product in products:
                product_dict = {
                    "product_id": product.product_id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.price),
                    "stock_quantity": product.stock_quantity,
                    "category_id": product.category_id,
                    "is_available": product.is_available,
                    "images": json.loads(product.images) if product.images else []
                }
                if product.category:
                    product_dict["category"] = {
                        "category_id": product.category.category_id,
                        "name": product.category.name,
                        "description": product.category.description,
                        "icon": product.category.icon
                    }
                result_products.append(product_dict)
            
            return result_products
        except Exception as e:
            print(f"❌ Search error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Добавляем автоматическое создание пользователя при запросе
@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: int, request: Request):
    # Проверяем, что запрос пришел от конкретного пользователя Telegram
    init_data = request.headers.get('x-telegram-init-data', '')
    if not init_data:
        # Если initData не передан, можно либо вернуть 400, либо создать/найти пользователя без проверки
        # В данном случае, мы создаем/находим без проверки
        pass # Продолжаем без проверки
    else:
        # Если initData передан, проверяем его
        user_data = verify_user_access(telegram_id, init_data) # Вызывает verify_telegram_hash и проверяет id
        # user_data содержит информацию из initData, можно использовать для обновления профиля

    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            # Создаем пользователя автоматически
            # Используем данные из initData, если они были проверены
            username = f'user_{telegram_id}'
            name = f'User {telegram_id}'

            is_admin = (telegram_id == 391622124)
            if 'user_data' in locals() and user_data: # Проверяем, была ли переменная user_data определена
                 username = user_data.get('username', username)
                 name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                 if not name:
                     name = f"User {telegram_id}"

            user = User(
                telegram_id=telegram_id,
                username=username,
                name=name,
                is_active=True,
                is_admin=is_admin
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # Возвращаем данные пользователя
        return {
            "user_id": user.user_id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "name": user.name,
            "phone": user.phone,
            "email": user.email,
            "address": user.address,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active,
            "is_admin": user.is_admin # Добавим это поле в ответ, если оно нужно
        }
@app.get("/api/users/{telegram_id}/stats")
async def get_user_stats(telegram_id: int):
    async with async_session() as session:
        # Сначала получаем пользователя по telegram_id
        user_result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Подсчитываем заказы пользователя через связь с User
        orders_result = await session.execute(
            select(func.count(Order.order_id)).where(Order.user_id == user.user_id) # Используем user_id
        )
        total_orders = orders_result.scalar_one()

        completed_orders_result = await session.execute(
            select(func.count(Order.order_id)).where(
                Order.user_id == user.user_id, # Используем user_id
                Order.status == OrderStatus.DELIVERED # Используем правильный статус
            )
        )
        completed_orders = completed_orders_result.scalar_one()

        return {
            "total_orders": total_orders,
            "completed_orders": completed_orders
        }
       
@app.post("/api/cart/add")
async def add_to_cart(request: AddToCartRequest):
    async with async_session() as session:
        # Находим или создаем пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=request.telegram_id,
                username=f"user_{request.telegram_id}",
                name=f"User {request.telegram_id}",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        # Находим или создаем корзину
        cart_result = await session.execute(
            select(Cart).where(Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        if not cart:
            cart = Cart(user_id=user.user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        # Проверяем существование товара
        product_result = await session.execute(
            select(Product).where(Product.product_id == request.product_id)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Проверяем, есть ли уже такой товар в корзине
        existing_item_result = await session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.cart_id,
                CartItem.product_id == request.product_id
            )
        )
        existing_item = existing_item_result.scalar_one_or_none()
        
        if existing_item:
            # Обновляем количество, но не превышая доступное количество
            new_quantity = existing_item.quantity + request.quantity
            if product.stock_quantity and new_quantity > product.stock_quantity:
                new_quantity = product.stock_quantity
            existing_item.quantity = new_quantity
            message = f"Количество обновлено: {new_quantity} шт."
        else:
            # Добавляем новый товар в корзину
            cart_item = CartItem(
                cart_id=cart.cart_id,
                product_id=request.product_id,
                quantity=min(request.quantity, product.stock_quantity or 1)
            )
            session.add(cart_item)
            message = "Товар добавлен в корзину"
        
        await session.commit()
        return {"status": "success", "message": message}

# Обновите функцию get_cart для включения услуг:
@app.get("/api/cart/{telegram_id}")
async def get_cart(telegram_id: int):
    async with async_session() as session:
        # Проверяем, существует ли пользователь по telegram_id
        user_result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Находим корзину пользователя
        cart_result = await session.execute(
            select(Cart).where(Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        if not cart:
            # Если корзины нет, возвращаем пустую
            return {"items": [], "service_items": [], "total": 0.0}

        # Получаем товары в корзине
        cart_items_result = await session.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(CartItem.cart_id == cart.cart_id)
        )
        cart_items = cart_items_result.scalars().all()

        # Получаем услуги в корзине
        cart_service_items_result = await session.execute(
            select(CartServiceItem)
            .options(selectinload(CartServiceItem.service))
            .where(CartServiceItem.cart_id == cart.cart_id)
        )
        cart_service_items = cart_service_items_result.scalars().all()

        # Вычисляем общую сумму
        products_total = sum(item.quantity * item.product.price for item in cart_items)
        services_total = sum(item.quantity * item.service.price for item in cart_service_items)
        total = products_total + services_total

        # Формируем ответ
        cart_data = {
            "items": [
                {
                    "cart_item_id": item.cart_item_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "product": {
                        "product_id": item.product.product_id,
                        "name": item.product.name,
                        "price": float(item.product.price),
                        "images": json.loads(item.product.images) if item.product.images else []
                    }
                }
                for item in cart_items
            ],
            "service_items": [
                {
                    "cart_service_item_id": item.cart_service_item_id,
                    "service_id": item.service_id,
                    "quantity": item.quantity,
                    "notes": item.notes,
                    "service": {
                        "service_id": item.service.service_id,
                        "name": item.service.name,
                        "price": float(item.service.price),
                        "description": item.service.description,
                        "duration": item.service.duration,
                        "image_url": item.service.image_url or "https://via.placeholder.com/100x100/667eea/ffffff?text=Service"
                    }
                }
                for item in cart_service_items
            ],
            "total": float(total),
            "products_total": float(products_total),
            "services_total": float(services_total)
        }

        return cart_data

@app.put("/api/cart/update")
async def update_cart_item(
    request: UpdateCartItemRequest
):
    async with async_session() as session:
        # Находим элемент корзины
        result = await session.execute(
            select(CartItem).where(CartItem.cart_item_id == request.cart_item_id)
        )
        cart_item = result.scalar_one_or_none()
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Обновляем количество
        cart_item.quantity = request.quantity
        await session.commit()
        return {"status": "success", "message": "Cart updated"}

@app.delete("/api/cart/remove")
async def remove_cart_item(request: RemoveCartItemRequest):
    async with async_session() as session:
        # Находим элемент корзины
        result = await session.execute(
            select(CartItem).where(CartItem.cart_item_id == request.cart_item_id)
        )
        cart_item = result.scalar_one_or_none()
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Удаляем элемент корзины
        await session.delete(cart_item)
        await session.commit()
        return {"status": "success", "message": "Item removed from cart"}

@app.post("/api/orders/create")
async def create_order(
    request: CreateOrderRequest
):
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Находим корзину
        cart_result = await session.execute(
            select(Cart).where(Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        if not cart:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Получаем товары из корзины
        cart_items_result = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.cart_id)
        )
        cart_items = cart_items_result.scalars().all()
        
        # Получаем услуги из корзины
        cart_service_items_result = await session.execute(
            select(CartServiceItem).where(CartServiceItem.cart_id == cart.cart_id)
        )
        cart_service_items = cart_service_items_result.scalars().all()
        
        # Проверяем, что корзина не пуста (есть либо товары, либо услуги)
        if not cart_items and not cart_service_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Считаем общую сумму
        total_amount = 0
        
        # Сумма товаров
        for item in cart_items:
            product_result = await session.execute(
                select(Product).where(Product.product_id == item.product_id)
            )
            product = product_result.scalar_one()
            total_amount += float(product.price) * item.quantity
        
        # Сумма услуг
        for service_item in cart_service_items:
            service_result = await session.execute(
                select(Service).where(Service.service_id == service_item.service_id)
            )
            service = service_result.scalar_one()
            total_amount += float(service.price) * service_item.quantity
        
        # Создаем заказ
        order_number = f"ORDER-{uuid.uuid4().hex[:8].upper()}"
        order = Order(
            user_id=user.user_id,
            order_number=order_number,
            total_amount=total_amount,
            shipping_method=request.shipping_method,
            shipping_address=request.shipping_address,
            customer_notes=request.customer_notes,
            status=OrderStatus.CREATED
        )
        session.add(order)
        await session.commit()
        await session.refresh(order)
        
        # Добавляем товары в заказ
        for item in cart_items:
            product_result = await session.execute(
                select(Product).where(Product.product_id == item.product_id)
            )
            product = product_result.scalar_one()
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=float(product.price),
                total_price=float(product.price) * item.quantity
            )
            session.add(order_item)
        
        # Создаем заказы на услуги из корзины
        for service_item in cart_service_items:
            service_result = await session.execute(
                select(Service).where(Service.service_id == service_item.service_id)
            )
            service = service_result.scalar_one()
            
            # Создаем заказ на услугу
            service_order = ServiceOrder(
                user_id=user.user_id,
                service_id=service_item.service_id,
                notes=service_item.notes,
                price=float(service.price),
                status=OrderStatus.CREATED
            )
            session.add(service_order)
        
        # Очищаем корзину (и товары, и услуги)
        await session.execute(
            CartItem.__table__.delete().where(CartItem.cart_id == cart.cart_id)
        )
        await session.execute(
            CartServiceItem.__table__.delete().where(CartServiceItem.cart_id == cart.cart_id)
        )
        
        # В эндпоинте create_order после сохранения заказа:
        # ... после сохранения заказа
        await session.commit()

        # Отправляем уведомление пользователю
        try:
            await bot.send_order_notification(telegram_id, {
                "order_number": order_number,
                "total_amount": total_amount,
                "shipping_method": request.shipping_method,
                "shipping_address": request.shipping_address,
                "status": "Создан"
            })
            
            # Отправляем уведомление администратору
            admin_message = (
                f"🛒 <b>Новый заказ #{order_number}</b>\n"
                f"Пользователь: {user.name} (ID: {telegram_id})\n"
                f"Сумма: {total_amount:.2f} ₽\n"
                f"Статус: Создан"
            )
            await bot.send_admin_notification(admin_message)
            
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления: {e}")
            # Не прерываем выполнение, просто логируем ошибку

        return {
            "status": "success",
            "order_number": order_number,
            "order_id": order.order_id,
            "total_amount": float(total_amount)
        }
    
@app.get("/api/services")
async def get_services():
    async with async_session() as session:
        try:
            # Сначала проверяем, существует ли колонка image_url
            result = await session.execute(text("PRAGMA table_info(services)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'image_url' in columns:
                # Если колонка есть, используем её
                result = await session.execute(
                    select(Service).where(Service.is_active == True)
                )
                services = result.scalars().all()
                return [{
                    "service_id": s.service_id,
                    "name": s.name,
                    "description": s.description,
                    "price": float(s.price),
                    "duration": s.duration,
                    "category": s.category,
                    "image_url": s.image_url or "https://via.placeholder.com/100x100/667eea/ffffff?text=Service"
                } for s in services]
            else:
                # Если колонки нет, не включаем её в результат
                result = await session.execute(
                    select(Service).where(Service.is_active == True)
                )
                services = result.scalars().all()
                return [{
                    "service_id": s.service_id,
                    "name": s.name,
                    "description": s.description,
                    "price": float(s.price),
                    "duration": s.duration,
                    "category": s.category,
                    "image_url": "https://via.placeholder.com/100x100/667eea/ffffff?text=Service"
                } for s in services]
        except Exception as e:
            print(f"❌ Ошибка получения услуг: {e}")
            raise HTTPException(status_code=500, detail="Ошибка получения услуг")

@app.post("/api/services/order")
async def order_service(request: CreateServiceOrderRequest): # Изменено: принимаем модель
    async with async_session() as session:
        # Находим пользователя по telegram_id из тела запроса
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id) # Изменено: request.telegram_id
        )
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=request.telegram_id, # Изменено: request.telegram_id
                username=f"user_{request.telegram_id}", # Изменено: request.telegram_id
                name=f"User {request.telegram_id}", # Изменено: request.telegram_id
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # Находим услугу по service_id из тела запроса
        service_result = await session.execute(
            select(Service).where(Service.service_id == request.service_id) # Изменено: request.service_id
        )
        service = service_result.scalar_one_or_none()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        # Создаем заказ на услугу
        service_order = ServiceOrder(
            user_id=user.user_id,
            service_id=request.service_id, # Изменено: request.service_id
            notes=request.notes, # Изменено: request.notes
            price=float(service.price),
            status=OrderStatus.CREATED
        )
        session.add(service_order)
        await session.commit()

        return {
            "status": "success",
            "message": f"Заказ на услугу '{service.name}' принят",
            "order_id": service_order.service_order_id
        }

# ... (остальной код) ...
@app.get("/api/users/{telegram_id}/orders")
async def get_user_orders(telegram_id: int):
    """Получить ВСЕ заказы пользователя"""
    async with async_session() as session:
        # Находим пользователя по telegram_id
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Получаем ВСЕ заказы пользователя (не только не доставленные)
        orders_result = await session.execute(
            select(Order)
            .where(Order.user_id == user.user_id) # Используем user_id
            .options(selectinload(Order.order_items).selectinload(OrderItem.product))
            .order_by(Order.created_at.desc())
        )
        orders = orders_result.scalars().all()

        # Формируем ответ
        result_orders = []
        for order in orders:
            total = sum(float(item.total_price) for item in order.order_items)
            result_orders.append({
                "order_id": order.order_id,
                "order_number": order.order_number,
                "total_amount": float(total),
                "status": order.status.value,
                "shipping_method": order.shipping_method,
                "shipping_address": order.shipping_address,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
                "items": [{
                    "product_id": item.product.product_id,
                    "name": item.product.name,
                    "quantity": item.quantity,
                    "price": float(item.unit_price),
                    "subtotal": float(item.total_price)
                } for item in order.order_items]
            })

        return result_orders
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is working"}

@app.get("/api/simple-search")
async def simple_search(q: str = "", limit: int = 50):
    """Простой поиск товаров без сложных параметров"""
    async with async_session() as session:
        query = select(Product).where(
            Product.is_available == True
        ).options(selectinload(Product.category))  # ДОБАВЛЯЕМ eager loading для категорий
        if q and q.strip():
            query = query.where(Product.name.ilike(f"%{q.strip()}%"))
        query = query.limit(limit)
        result = await session.execute(query)
        products = result.scalars().all()
        return [
            {
                "product_id": p.product_id,
                "name": p.name,
                "description": p.description,
                "price": float(p.price),
                "stock_quantity": p.stock_quantity,
                "images": json.loads(p.images) if p.images else [],
                "category": {
                    "category_id": p.category.category_id,
                    "name": p.category.name,
                    "icon": p.category.icon
                } if p.category else None
            }
            for p in products
        ]
    
@app.get("/api/users/{telegram_id}/service_orders")
async def get_user_service_orders(telegram_id: int):
    """Получить заказы на услуги пользователя"""
    async with async_session() as session:
        # Находим пользователя по telegram_id
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Получаем заказы на услуги пользователя
        service_orders_result = await session.execute(
            select(ServiceOrder)
            .where(ServiceOrder.user_id == user.user_id)
            .options(selectinload(ServiceOrder.service))
            .order_by(ServiceOrder.created_at.desc())
        )
        service_orders = service_orders_result.scalars().all()

        # Формируем ответ
        result_orders = []
        for order in service_orders:
            result_orders.append({
                "service_order_id": order.service_order_id,
                "service": {
                    "service_id": order.service.service_id,
                    "name": order.service.name,
                    "description": order.service.description,
                    "price": float(order.service.price),
                    "duration": order.service.duration,
                    "image_url": order.service.image_url or "https://via.placeholder.com/100x100/667eea/ffffff?text=Service"
                },
                "notes": order.notes,
                "status": order.status.value,
                "price": float(order.price),
                "created_at": order.created_at.isoformat()
            })

        return result_orders
    
@app.post("/api/cart/add_service")
async def add_service_to_cart(request: AddServiceToCartRequest):
    async with async_session() as session:
        # Находим или создаем пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=request.telegram_id,
                username=f"user_{request.telegram_id}",
                name=f"User {request.telegram_id}",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        # Находим или создаем корзину
        cart_result = await session.execute(
            select(Cart).where(Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        if not cart:
            cart = Cart(user_id=user.user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        # Проверяем существование услуги
        service_result = await session.execute(
            select(Service).where(Service.service_id == request.service_id)
        )
        service = service_result.scalar_one_or_none()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        if not service.is_active:
            raise HTTPException(status_code=400, detail="Service is not available")
        
        # Проверяем, есть ли уже такая услуга в корзине
        existing_item_result = await session.execute(
            select(CartServiceItem).where(
                CartServiceItem.cart_id == cart.cart_id,
                CartServiceItem.service_id == request.service_id
            )
        )
        existing_item = existing_item_result.scalar_one_or_none()
        
        if existing_item:
            # ОБНОВЛЕНИЕ: Не позволяем добавлять больше одной услуги
            # Просто обновляем заметки, если нужно
            if request.notes:
                existing_item.notes = request.notes
            message = "Услуга уже в корзине (не более одной)"
        else:
            # Добавляем новую услугу в корзину, но только одну
            cart_service_item = CartServiceItem(
                cart_id=cart.cart_id,
                service_id=request.service_id,
                quantity=1,  # Всегда 1 для услуг
                notes=request.notes
            )
            session.add(cart_service_item)
            message = "Услуга добавлена в корзину"
        
        await session.commit()
        return {"status": "success", "message": message}
    
# Добавьте эндпоинт для обновления услуги в корзине:
@app.put("/api/cart/update_service")
async def update_cart_service_item(request: UpdateCartServiceItemRequest):
    async with async_session() as session:
        # Находим элемент корзины с услугой
        result = await session.execute(
            select(CartServiceItem).where(CartServiceItem.cart_service_item_id == request.cart_service_item_id)
        )
        cart_service_item = result.scalar_one_or_none()
        if not cart_service_item:
            raise HTTPException(status_code=404, detail="Cart service item not found")
        
        # Обновляем количество и заметки
        cart_service_item.quantity = request.quantity
        if request.notes is not None:
            cart_service_item.notes = request.notes
        
        await session.commit()
        return {"status": "success", "message": "Service in cart updated"}

# Добавьте эндпоинт для удаления услуги из корзины:
@app.delete("/api/cart/remove_service")
async def remove_cart_service_item(request: RemoveCartServiceItemRequest):
    async with async_session() as session:
        # Находим элемент корзины с услугой
        result = await session.execute(
            select(CartServiceItem).where(CartServiceItem.cart_service_item_id == request.cart_service_item_id)
        )
        cart_service_item = result.scalar_one_or_none()
        if not cart_service_item:
            raise HTTPException(status_code=404, detail="Cart service item not found")
        
        # Удаляем элемент корзины
        await session.delete(cart_service_item)
        await session.commit()
        return {"status": "success", "message": "Service removed from cart"}

# Добавить в main.py, после других эндпоинтов
@app.get("/api/admin/check/{telegram_id}")
async def check_admin(telegram_id: int, request: Request):
    """Проверка прав администратора"""
    # Проверяем, что запрос пришел от конкретного пользователя Telegram
    init_data = request.headers.get('x-telegram-init-data', '')
    if not init_data:
        raise HTTPException(status_code=401, detail="Telegram auth required")
    
    # Получаем пользователя из initData
    user_data = get_telegram_user_from_init_data(init_data)
    if not user_data:
        raise HTTPException(status_code=401, detail="User data not found")
    
    # Проверяем, что пользователь запрашивает СВОИ данные
    if user_data.get('id') != telegram_id:
        raise HTTPException(status_code=403, detail="Access denied. You can only request your own data")
    
    # Проверяем хэш Telegram
    if not verify_telegram_hash(init_data):
        # Если проверка хэша не прошла, пробуем проверить через signature
        print("❌ Оба метода проверки не прошли")
        raise HTTPException(status_code=401, detail="Invalid Telegram auth")
    
    async with async_session() as session:
        # Ищем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"🔍 Проверка администратора для {telegram_id}: is_admin = {user.is_admin}")
        
        return {
            "is_admin": user.is_admin,
            "telegram_id": user.telegram_id,
            "name": user.name,
            "username": user.username
        }
    
# В main.py добавьте после существующих эндпоинтов
@app.get("/api/admin/test/{telegram_id}")
async def test_admin_check(telegram_id: int):
    """Тестовый эндпоинт для проверки администратора (без проверки Telegram)"""
    async with async_session() as session:
        # Ищем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"is_admin": False, "error": "User not found"}
        
        return {
            "is_admin": user.is_admin,
            "telegram_id": user.telegram_id,
            "name": user.name,
            "username": user.username
        }

# В main.py добавьте после существующих эндпоинтов
@app.get("/api/admin/check_simple/{telegram_id}")
async def check_admin_simple(telegram_id: int):
    """Простая проверка администратора без проверки Telegram хэша (для тестов)"""
    async with async_session() as session:
        # Ищем пользователя
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"🔍 Проверка администратора для {telegram_id}: is_admin = {user.is_admin}")
        print(f"🔍 Данные пользователя: {user.username}, {user.name}")
        
        return {
            "is_admin": user.is_admin,
            "telegram_id": user.telegram_id,
            "name": user.name,
            "username": user.username
        }
    
# Добавьте в main.py после других эндпоинтов

# ========== АДМИН ЭНДПОИНТЫ ==========

@app.get("/api/admin/users")
async def get_all_users(
    request: Request,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Получить всех пользователей"""
    # Пропускаем проверку Telegram для разработки
    # Для продакшена нужно добавить проверку is_admin
    
    async with async_session() as session:
        query = select(User)
        
        if search:
            query = query.where(
                User.username.ilike(f"%{search}%") |
                User.name.ilike(f"%{search}%") |
                User.telegram_id.cast(String).ilike(f"%{search}%")
            )
        
        query = query.order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(query)
        users = result.scalars().all()
        
        return [{
            "user_id": user.user_id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "name": user.name,
            "phone": user.phone,
            "email": user.email,
            "address": user.address,
            "created_at": user.created_at.isoformat(),
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "orders_count": len(user.orders) if hasattr(user, 'orders') else 0
        } for user in users]

@app.get("/api/admin/orders")
async def get_all_orders(
    request: Request,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Получить все заказы"""
    async with async_session() as session:
        query = select(Order).options(
            selectinload(Order.user),
            selectinload(Order.order_items).selectinload(OrderItem.product)
        )
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.order_by(Order.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(query)
        orders = result.scalars().all()
        
        orders_list = []
        for order in orders:
            total = sum(float(item.total_price) for item in order.order_items)
            
            # Получаем пользователя
            user = order.user
            
            orders_list.append({
                "order_id": order.order_id,
                "order_number": order.order_number,
                "total_amount": float(order.total_amount) if order.total_amount else float(total),
                "status": order.status.value,
                "shipping_method": order.shipping_method,
                "shipping_address": order.shipping_address,
                "customer_notes": order.customer_notes,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat() if order.updated_at else None,
                "user": {
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "name": user.name,
                    "phone": user.phone
                } if user else None,
                "items": [{
                    "product_id": item.product.product_id if item.product else None,
                    "name": item.product.name if item.product else "Товар не найден",
                    "quantity": item.quantity,
                    "price": float(item.unit_price),
                    "subtotal": float(item.total_price)
                } for item in order.order_items]
            })
        
        return {"orders": orders_list, "total": len(orders_list)}

@app.get("/api/admin/service_orders")
async def get_all_service_orders(
    request: Request,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Получить все заказы на услуги"""
    async with async_session() as session:
        query = select(ServiceOrder).options(
            selectinload(ServiceOrder.user),
            selectinload(ServiceOrder.service)
        )
        
        if status:
            query = query.where(ServiceOrder.status == status)
        
        query = query.order_by(ServiceOrder.created_at.desc()).limit(limit).offset(offset)
        result = await session.execute(query)
        service_orders = result.scalars().all()
        
        service_orders_list = []
        for order in service_orders:
            user = order.user
            service = order.service
            
            service_orders_list.append({
                "service_order_id": order.service_order_id,
                "created_at": order.created_at.isoformat(),
                "status": order.status.value,
                "price": float(order.price),
                "notes": order.notes,
                "user": {
                    "telegram_id": user.telegram_id,
                    "username": user.username,
                    "name": user.name
                } if user else None,
                "service": {
                    "service_id": service.service_id,
                    "name": service.name,
                    "description": service.description
                } if service else None
            })
        
        return {"service_orders": service_orders_list, "total": len(service_orders_list)}

@app.get("/api/admin/stats")
async def get_admin_stats():
    """Получить статистику для админ панели"""
    async with async_session() as session:
        # Статистика пользователей
        total_users = await session.execute(select(func.count(User.user_id)))
        total_users_count = total_users.scalar()
        
        active_users = await session.execute(
            select(func.count(User.user_id)).where(User.is_active == True)
        )
        active_users_count = active_users.scalar()
        
        admin_users = await session.execute(
            select(func.count(User.user_id)).where(User.is_admin == True)
        )
        admin_users_count = admin_users.scalar()
        
        # Статистика заказов
        total_orders = await session.execute(select(func.count(Order.order_id)))
        total_orders_count = total_orders.scalar()
        
        # Заказы по статусам
        status_counts = {}
        for status in OrderStatus:
            count_result = await session.execute(
                select(func.count(Order.order_id)).where(Order.status == status)
            )
            status_counts[status.value] = count_result.scalar()
        
        # Статистика товаров
        total_products = await session.execute(select(func.count(Product.product_id)))
        total_products_count = total_products.scalar()
        
        available_products = await session.execute(
            select(func.count(Product.product_id)).where(
                Product.is_available == True,
                Product.stock_quantity > 0
            )
        )
        available_products_count = available_products.scalar()
        
        # Статистика услуг
        total_services = await session.execute(select(func.count(Service.service_id)))
        total_services_count = total_services.scalar()
        
        # Статистика доходов
        total_revenue = await session.execute(select(func.sum(Order.total_amount)))
        total_revenue_value = float(total_revenue.scalar() or 0)
        
        # Последние заказы
        recent_orders_result = await session.execute(
            select(Order)
            .options(selectinload(Order.user))
            .order_by(Order.created_at.desc())
            .limit(10)
        )
        recent_orders = recent_orders_result.scalars().all()
        
        recent_orders_list = []
        for order in recent_orders:
            recent_orders_list.append({
                "order_id": order.order_id,
                "order_number": order.order_number,
                "total_amount": float(order.total_amount),
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
                "user": {
                    "telegram_id": order.user.telegram_id,
                    "name": order.user.name
                } if order.user else None
            })
        
        return {
            "users": {
                "total": total_users_count,
                "active": active_users_count,
                "admins": admin_users_count
            },
            "orders": {
                "total": total_orders_count,
                "by_status": status_counts
            },
            "products": {
                "total": total_products_count,
                "available": available_products_count
            },
            "services": {
                "total": total_services_count
            },
            "revenue": {
                "total": total_revenue_value
            },
            "recent_orders": recent_orders_list
        }

# Модель для отправки сообщения
class SendMessageRequest(BaseModel):
    telegram_id: int
    message: str
    message_type: str = "text"  # text, photo, document

# Обновите эндпоинт send_message:
@app.post("/api/admin/send_message")
async def send_message(request: SendMessageRequest):
    """Отправить сообщение пользователю через бота"""
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Отправляем сообщение через бота
        result = await bot.send_message(
            chat_id=request.telegram_id,
            text=request.message,
            parse_mode="HTML"
        )
        
        if not result.get("ok", False):
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to send message: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "status": "success",
            "message": f"Сообщение отправлено пользователю {user.name}",
            "telegram_id": request.telegram_id,
            "telegram_result": result
        }
# Эндпоинты для управления товарами
@app.post("/api/admin/products")
async def create_product(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    stock_quantity: int = Form(0),
    category_id: Optional[int] = Form(None),
    is_available: bool = Form(True)
):
    """Создать новый товар"""
    async with async_session() as session:
        product = Product(
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            category_id=category_id,
            is_available=is_available,
            images="[]"  # Пустой массив изображений
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        
        return {
            "status": "success",
            "product_id": product.product_id,
            "message": "Товар создан"
        }

@app.put("/api/admin/products/{product_id}")
async def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    stock_quantity: int = Form(None),
    category_id: Optional[int] = Form(None),
    is_available: bool = Form(None)
):
    """Обновить товар"""
    async with async_session() as session:
        result = await session.execute(
            select(Product).where(Product.product_id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = price
        if stock_quantity is not None:
            product.stock_quantity = stock_quantity
        if category_id is not None:
            product.category_id = category_id
        if is_available is not None:
            product.is_available = is_available
        
        await session.commit()
        
        return {"status": "success", "message": "Товар обновлен"}

@app.delete("/api/admin/products/{product_id}")
async def delete_product(product_id: int):
    """Удалить товар"""
    async with async_session() as session:
        result = await session.execute(
            select(Product).where(Product.product_id == product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        await session.delete(product)
        await session.commit()
        
        return {"status": "success", "message": "Товар удален"}

# Эндпоинты для управления услугами
@app.post("/api/admin/services")
async def create_service(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    duration: str = Form(None),
    category: str = Form(None),
    is_active: bool = Form(True)
):
    """Создать новую услугу"""
    async with async_session() as session:
        service = Service(
            name=name,
            description=description,
            price=price,
            duration=duration,
            category=category,
            is_active=is_active,
            image_url=None
        )
        session.add(service)
        await session.commit()
        await session.refresh(service)
        
        return {
            "status": "success",
            "service_id": service.service_id,
            "message": "Услуга создана"
        }

@app.put("/api/admin/services/{service_id}")
async def update_service(
    service_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    duration: str = Form(None),
    category: str = Form(None),
    is_active: bool = Form(None)
):
    """Обновить услугу"""
    async with async_session() as session:
        result = await session.execute(
            select(Service).where(Service.service_id == service_id)
        )
        service = result.scalar_one_or_none()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        if name is not None:
            service.name = name
        if description is not None:
            service.description = description
        if price is not None:
            service.price = price
        if duration is not None:
            service.duration = duration
        if category is not None:
            service.category = category
        if is_active is not None:
            service.is_active = is_active
        
        await session.commit()
        
        return {"status": "success", "message": "Услуга обновлена"}

@app.delete("/api/admin/services/{service_id}")
async def delete_service(service_id: int):
    """Удалить услугу"""
    async with async_session() as session:
        result = await session.execute(
            select(Service).where(Service.service_id == service_id)
        )
        service = result.scalar_one_or_none()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        await session.delete(service)
        await session.commit()
        
        return {"status": "success", "message": "Услуга удалена"}

@app.put("/api/admin/orders/{order_id}")
async def update_order_status(order_id: int, request: dict):
    status = request.get('status')
    if not status:
        raise HTTPException(status_code=422, detail="Status is required")
    """Обновить статус заказа"""
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.order_id == order_id)
        )
        order = result.scalar_one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Проверяем, что статус валидный
        valid_statuses = [s.value for s in OrderStatus]
        if status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Valid statuses: {valid_statuses}")
        
        order.status = status
        await session.commit()
        
        return {"status": "success", "message": "Статус заказа обновлен"}    

# В main.py добавьте:
class UpdateServiceOrderStatusRequest(BaseModel):
    status: str

@app.put("/api/admin/service_orders/{service_order_id}")
async def update_service_order_status(
    service_order_id: int, 
    request: UpdateServiceOrderStatusRequest
):
    async with async_session() as session:
        result = await session.execute(
            select(ServiceOrder).where(ServiceOrder.service_order_id == service_order_id)
        )
        service_order = result.scalar_one_or_none()
        
        if not service_order:
            raise HTTPException(status_code=404, detail="Service order not found")
        
        valid_statuses = [s.value for s in OrderStatus]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Valid statuses: {valid_statuses}"
            )
        
        service_order.status = request.status
        await session.commit()
        
        return {"status": "success", "message": "Статус заказа услуги обновлен"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)