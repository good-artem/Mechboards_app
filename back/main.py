from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from models import init_db, async_session, Category, Product, User, Cart, CartItem, Order, OrderItem, News, Service, ServiceOrder, OrderStatus
from sqlalchemy import select, func, text
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

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

def verify_telegram_hash(init_data: str) -> bool:
    """
    Проверяет подлинность данных от Telegram WebApp.
    Использует initData (строку), а не initDataUnsafe.
    """
    try:
        # Парсим query string
        parsed_data = dict(parse_qsl(init_data))
        received_hash = parsed_data.get('hash')
        if not received_hash:
            return False
        # 1. УДАЛЯЕМ из проверки только поле 'hash'
        data_check_list = []
        for key, value in sorted(parsed_data.items()):
            if key == 'hash':
                continue  # Исключаем hash из расчета
            data_check_list.append(f"{key}={value}")
        # 2. Формируем строку для проверки
        data_check_string = "\n".join(data_check_list)
        # 3. Вычисляем секретный ключ (HMAC-SHA256)
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()
        # 4. Вычисляем хэш и сравниваем
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        # Безопасное сравнение хэшей
        return hmac.compare_digest(received_hash, calculated_hash)
    except Exception as e:
        print(f"❌ Ошибка верификации Telegram hash: {e}")
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

class CreateUserRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    name: Optional[str] = None

class UpdateCartItemRequest(BaseModel):
    cart_item_id: int
    quantity: int

class RemoveCartItemRequest(BaseModel):
    cart_item_id: int

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
    q: str = "",
    category_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    async with async_session() as session:
        try:
            query = select(Product).where(
                Product.is_available == True
            ).options(selectinload(Product.category))
            
            # Поиск по названию, только если есть запрос
            if q and q.strip():
                query = query.where(Product.name.ilike(f"%{q.strip()}%"))
            
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
        except ValueError as ve:
            print(f"❌ Search validation error: {ve}")
            raise HTTPException(status_code=400, detail="Invalid parameter format")
        except Exception as e:
            print(f"❌ Search error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Добавляем автоматическое создание пользователя при запросе
@app.get("/api/user/{telegram_id}")
async def get_user(telegram_id: int, request: Request):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Создаем пользователя автоматически
            telegram_user = get_telegram_user_from_init_data(request.headers.get('x-telegram-init-data', ''))
            if telegram_user and telegram_user.get('id') == telegram_id:
                user = User(
                    telegram_id=telegram_id,
                    username=telegram_user.get('username'),
                    name=f"{telegram_user.get('first_name', '')} {telegram_user.get('last_name', '')}".strip(),
                    is_active=True
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
            else:
                raise HTTPException(status_code=404, detail="User not found")
        
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
            "is_admin": user.is_admin
        }

@app.get("/api/users/{telegram_id}/stats")
async def get_user_stats(telegram_id: int):
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Считаем заказы пользователя
        orders_result = await session.execute(
            select(Order).where(Order.user_id == user.user_id)
        )
        orders = orders_result.scalars().all()
        
        # Считаем завершенные заказы
        completed_orders = [order for order in orders if order.status == OrderStatus.DELIVERED]
        
        return {
            "total_orders": len(orders),
            "completed_orders": len(completed_orders)
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

@app.get("/api/cart/{telegram_id}")
async def get_cart(telegram_id: int):
    print(f"🔄 Запрос корзины для {telegram_id}")
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            # Создаем пользователя если не существует
            user = User(
                telegram_id=telegram_id,
                username=f"user_{telegram_id}",
                name=f"User {telegram_id}",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        # Находим корзину пользователя
        cart_result = await session.execute(
            select(Cart).where(Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        if not cart:
            # Создаем корзину если не существует
            cart = Cart(user_id=user.user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        # Получаем товары в корзине с информацией о продуктах
        cart_items_result = await session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart.cart_id)
            .options(selectinload(CartItem.product))
        )
        cart_items = cart_items_result.scalars().all()
        
        items = []
        total = 0
        for item in cart_items:
            if item.product:
                subtotal = float(item.product.price) * item.quantity
                items.append({
                    "cart_item_id": item.cart_item_id,
                    "product": {
                        "product_id": item.product.product_id,
                        "name": item.product.name,
                        "description": item.product.description,
                        "price": float(item.product.price),
                        "stock_quantity": item.product.stock_quantity,
                        "category_id": item.product.category_id,
                        "is_available": item.product.is_available,
                        "images": json.loads(item.product.images) if item.product.images else []
                    },
                    "quantity": item.quantity,
                    "subtotal": subtotal
                })
                total += subtotal
        
        return {"items": items, "total": total}

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
async def remove_cart_item(
    request: RemoveCartItemRequest
):
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
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Считаем общую сумму
        total_amount = 0
        for item in cart_items:
            product_result = await session.execute(
                select(Product).where(Product.product_id == item.product_id)
            )
            product = product_result.scalar_one()
            total_amount += float(product.price) * item.quantity
        
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
        
        # Очищаем корзину
        await session.execute(
            CartItem.__table__.delete().where(CartItem.cart_id == cart.cart_id)
        )
        await session.commit()
        
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
async def order_service(
    telegram_id: int,
    service_id: int,
    notes: Optional[str] = None
):
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                telegram_id=telegram_id,
                username=f"user_{telegram_id}",
                name=f"User {telegram_id}",
                is_active=True
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        # Находим услугу
        service_result = await session.execute(
            select(Service).where(Service.service_id == service_id)
        )
        service = service_result.scalar_one_or_none()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Создаем заказ на услугу
        service_order = ServiceOrder(
            user_id=user.user_id,
            service_id=service.service_id,
            notes=notes,
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

@app.get("/api/users/{telegram_id}/orders")
async def get_user_orders(telegram_id: int):
    """Получить актуальные заказы пользователя (не выполненные)"""
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Получаем заказы, которые не доставлены
        orders_result = await session.execute(
            select(Order)
            .where(Order.user_id == user.user_id)
            .where(Order.status != OrderStatus.DELIVERED)
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
                "created_at": order.created_at.isoformat(),
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)