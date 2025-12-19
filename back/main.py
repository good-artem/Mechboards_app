from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from models import init_db, async_session, Category, Product, User, Cart, CartItem, Order, OrderItem, News
from sqlalchemy import select
from typing import List, Optional
import uuid
from datetime import datetime
import os
import hashlib
import hmac
import json
from urllib.parse import parse_qsl
from sqlalchemy.orm import selectinload


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

# Простой CORS middleware для тестирования
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    # Всегда добавляем CORS заголовки
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            content={"status": "ok"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Expose-Headers": "*",
            }
        )
    
    response = await call_next(request)
    
    # Добавляем CORS заголовки
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response

# Добавьте этот middleware после простого CORS middleware
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Пропускаем OPTIONS запросы и публичные эндпоинты
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Expose-Headers": "*",
            }
        )
    
    # Список публичных эндпоинтов
    public_paths = [
        '/api/categories',
        '/api/products',
        '/api/news',
        '/api/health',
        '/api/products/search',
        '/api/search',
        '/api/test-search',
        '/api/test',
        '/api/test-images',
<<<<<<< HEAD
        '/api/test/no-auth',
        '/assets',
        '/docs',
        '/openapi.json',
        '/api/debug/headers',
=======
        '/api/me',
        '/api/test/no-auth',
        '/api/test/with-auth'
>>>>>>> 757174750d78060e497ef2d95a24048a23631ab5
    ]
    
    # Проверяем, публичный ли эндпоинт
    is_public = any(request.url.path.startswith(path) for path in public_paths)
    
    if is_public:
        response = await call_next(request)
        return response
    
    # Для защищенных эндпоинтов проверяем авторизацию
    init_data = request.headers.get('x-telegram-init-data')
    
<<<<<<< HEAD
    # Для тестирования: если нет заголовка, разрешаем доступ (но в реальном приложении уберите это)
    if not init_data:
        print(f"⚠️ No Telegram auth header for protected endpoint: {request.url.path}")
        # В реальном приложении раскомментируйте:
        # return JSONResponse(
        #     status_code=401,
        #     content={"detail": "Требуется авторизация Telegram"},
        #     headers={
        #         "Access-Control-Allow-Origin": "*",
        #         "Access-Control-Expose-Headers": "*"
        #     }
        # )
        # Для тестирования - пропускаем запрос
        response = await call_next(request)
        return response
    
    try:
        # Проверяем подпись Telegram
        if not verify_telegram_hash(init_data):
            print(f"⚠️ Invalid Telegram hash for: {request.url.path}")
            # В реальном приложении раскомментируйте:
            # return JSONResponse(
            #     status_code=401,
            #     content={"detail": "Невалидная авторизация Telegram"},
            #     headers={
            #         "Access-Control-Allow-Origin": "*",
            #         "Access-Control-Expose-Headers": "*"
            #     }
            # )
            # Для тестирования - пропускаем запрос
            response = await call_next(request)
            return response
            
        # Проверяем пользователя
        user_data = get_telegram_user_from_init_data(init_data)
        if not user_data:
            return JSONResponse(
                status_code=401,
                content={"detail": "Не удалось получить данные пользователя"},
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Expose-Headers": "*"
                }
            )
        
        # Добавляем данные пользователя в request state
        request.state.telegram_user = user_data
        
=======
    if not init_data:
        return JSONResponse(
            status_code=401,
            content={"detail": "Требуется авторизация Telegram"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "*"
            }
        )
    
    try:
        # Убедитесь, что verify_telegram_hash возвращает True для тестирования
        # Временно для тестирования закомментируйте проверку
        # if init_data and not verify_telegram_hash(init_data):
        #     return JSONResponse(
        #         status_code=401,
        #         content={"detail": "Невалидная авторизация"},
        #         headers={
        #             "Access-Control-Allow-Origin": "*",
        #             "Access-Control-Expose-Headers": "*"
        #         }
        #     )
        
        # Для тестирования - пропускаем запрос
>>>>>>> 757174750d78060e497ef2d95a24048a23631ab5
        response = await call_next(request)
        return response
        
    except Exception as e:
        print(f"❌ Auth middleware error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Ошибка сервера: {str(e)}"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Expose-Headers": "*"
            }
        )

# Зависимость для получения telegram_id из пути
async def get_current_user(telegram_id: int, x_telegram_init_data: str = Header(None)):
    return verify_user_access(telegram_id, x_telegram_init_data)

# Зависимость для проверки телеграм ID в теле запроса
async def verify_body_telegram_id(data: dict, x_telegram_init_data: str = Header(None)):
    telegram_id = data.get('telegram_id')
    if not telegram_id:
        raise HTTPException(status_code=400, detail="telegram_id is required")
    return verify_user_access(telegram_id, x_telegram_init_data)

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
                "images": product.images
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
        return product

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
        return news_items

@app.get("/api/products/search")
async def search_products(q: str = "", category_id: Optional[int] = None, limit: int = 20, offset: int = 0):
    async with async_session() as session:
        query = select(Product).where(
            Product.is_available == True
        ).options(selectinload(Product.category))
        
        if q:
            query = query.where(Product.name.ilike(f"%{q}%"))
        
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
                "images": product.images
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

# Публичные эндпоинты пользователя (для тестирования)
@app.get("/api/user/{telegram_id}")
async def get_user_public(telegram_id: int, request: Request):
    """Публичный эндпоинт для получения пользователя"""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Проверяем, есть ли данные пользователя в запросе
            telegram_user = getattr(request.state, 'telegram_user', None)
            if telegram_user and telegram_user.get('id') == telegram_id:
                # Создаем пользователя если не существует
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
        
        return user

@app.get("/api/user/{telegram_id}/stats")
async def get_user_stats_public(telegram_id: int):
    """Публичный эндпоинт для статистики пользователя"""
    async with async_session() as session:
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {"total_orders": 0, "completed_orders": 0}
        
        orders_result = await session.execute(
            select(Order).where(Order.user_id == user.user_id)
        )
        orders = orders_result.scalars().all()
        
        completed_orders = [order for order in orders if order.status.value == "Доставлен"]
        
        return {
            "total_orders": len(orders),
            "completed_orders": len(completed_orders)
        }

# Защищенные эндпоинты (требуют авторизации) - временно тоже публичные для тестирования
@app.get("/api/users/{telegram_id}")
async def get_user(
    telegram_id: int
):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user

@app.post("/api/users/create")
async def create_user(
    request: CreateUserRequest
):
    async with async_session() as session:
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return existing_user
        
        # Создаем нового пользователя
        user = User(
            telegram_id=request.telegram_id,
            username=request.username,
            name=request.name,
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user

@app.get("/api/users/{telegram_id}/stats")
async def get_user_stats(
    telegram_id: int
):
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
        completed_orders = [order for order in orders if order.status.value == "Доставлен"]
        
        return {
            "total_orders": len(orders),
            "completed_orders": len(completed_orders)
        }

@app.post("/api/cart/add")
async def add_to_cart(
    request: AddToCartRequest
):
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            # Создаем пользователя если не существует
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
        
        # Проверяем, есть ли уже такой товар в корзине
        existing_item_result = await session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.cart_id,
                CartItem.product_id == request.product_id
            )
        )
        existing_item = existing_item_result.scalar_one_or_none()
        
        if existing_item:
            # Обновляем количество
            existing_item.quantity += request.quantity
        else:
            # Добавляем новый товар в корзину
            cart_item = CartItem(
                cart_id=cart.cart_id,
                product_id=request.product_id,
                quantity=request.quantity
            )
            session.add(cart_item)
        
        await session.commit()
        
        return {"status": "success", "message": "Product added to cart"}

# main.py - исправленный эндпоинт корзины
@app.get("/api/cart/{telegram_id}")
async def get_cart(
<<<<<<< HEAD
    telegram_id: int
=======
    telegram_id: int,
    x_telegram_init_data: str = Header(None)
>>>>>>> 757174750d78060e497ef2d95a24048a23631ab5
):
    # Для тестирования временно отключаем проверку
    # user_data = verify_user_access(telegram_id, x_telegram_init_data)
    
    async with async_session() as session:
        # Находим или создаем пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            # Создаем нового пользователя
            user = User(
                telegram_id=telegram_id,
                username=f"user_{telegram_id}",
                name=f"User {telegram_id}",
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
            return {"items": [], "total": 0}
        
        # Получаем товары в корзине
        cart_items_result = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.cart_id)
        )
        cart_items = cart_items_result.scalars().all()
        
        items = []
        total = 0
        
        for item in cart_items:
            product_result = await session.execute(
                select(Product).where(Product.product_id == item.product_id)
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
        
        # Находим корзину
        cart_result = await session.execute(
            select(Cart).where(Cart.cart_id == cart_item.cart_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
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
        # Находим пользователя и его корзину
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
            customer_notes=request.customer_notes
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
                unit_price=product.price,
                total_price=float(product.price) * item.quantity
            )
            session.add(order_item)
        
        # Очищаем корзину
        await session.execute(
            CartItem.__table__.delete().where(CartItem.cart_id == cart.cart_id)
        )
        
        await session.commit()
        
        return {"status": "success", "order_number": order_number, "order_id": order.order_id}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is working"}

@app.get("/api/telegram-test")
async def telegram_test(x_telegram_init_data: str = Header(None)):
    """Тестовый endpoint для проверки Telegram авторизации"""
    if not x_telegram_init_data:
        return {"status": "error", "message": "No Telegram init data"}
    
    if not verify_telegram_hash(x_telegram_init_data):
        return {"status": "error", "message": "Invalid Telegram hash"}
    
    user_data = get_telegram_user_from_init_data(x_telegram_init_data)
    return {
        "status": "success", 
        "message": "Telegram auth OK",
        "user": user_data
    }

# Также добавьте endpoint для получения текущего пользователя
@app.get("/api/me")
async def get_current_user_data(request: Request):
    """Получить данные текущего пользователя (требует авторизации)"""
    telegram_user = getattr(request.state, 'telegram_user', None)
    if not telegram_user:
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_user.get('id'))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {
                "status": "not_found", 
                "telegram_user": telegram_user,
                "message": "Пользователь не зарегистрирован в системе"
            }
        
        return {
            "status": "success", 
            "user": {
                "user_id": user.user_id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "name": user.name,
                "created_at": user.created_at
            }, 
            "telegram_user": telegram_user
        }
@app.get("/api/debug/headers")
async def debug_headers(request: Request):
    """Debug endpoint для проверки заголовков"""
    headers = dict(request.headers)
    return {
        "path": str(request.url),
        "headers": headers,
        "telegram_init_data": headers.get('x-telegram-init-data'),
        "has_auth": bool(headers.get('x-telegram-init-data'))
    }

@app.get("/api/test-images")
async def test_images():
    """Тестовый endpoint для проверки изображений"""
    return {
        "test_image_url": "https://via.placeholder.com/300x400/667eea/ffffff?text=Test+Image",
        "api_base_url": "http://localhost:8000"
    }

# Добавьте после других эндпоинтов:
@app.get("/api/test/no-auth")
async def test_no_auth():
    """Тестовый эндпоинт без авторизации"""
    return {"status": "ok", "message": "No auth required", "timestamp": datetime.now().isoformat()}

@app.get("/api/test/with-auth")
async def test_with_auth(x_telegram_init_data: str = Header(None)):
    """Тестовый эндпоинт с авторизацией"""
    return {
        "status": "ok", 
        "message": "Auth check passed", 
        "has_init_data": bool(x_telegram_init_data),
        "init_data_length": len(x_telegram_init_data) if x_telegram_init_data else 0,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/users/auto-create")
async def auto_create_user(telegram_id: int):
    """Создать пользователя автоматически (для тестирования)"""
    async with async_session() as session:
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            return existing_user
        
        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_id,
            username=f"user_{telegram_id}",
            name=f"User {telegram_id}",
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Создаем корзину для пользователя
        cart = Cart(user_id=user.user_id)
        session.add(cart)
        await session.commit()
        
        return user
    
@app.get("/api/test-search")
async def test_search(q: str = ""):
    """Тестовый эндпоинт для проверки поиска"""
    async with async_session() as session:
        query = select(Product)
        if q:
            query = query.where(Product.name.ilike(f"%{q}%"))
        
        result = await session.execute(query.limit(10))
        products = result.scalars().all()
        
        return {
            "query": q,
            "count": len(products),
            "products": [
                {
                    "id": p.product_id,
                    "name": p.name,
                    "price": float(p.price),
                    "images": p.images
                }
                for p in products
            ]
        }
    
@app.get("/api/search")
async def search(q: str = ""):
    """Простой эндпоинт для поиска"""
    async with async_session() as session:
        if not q:
            return []
        
        result = await session.execute(
            select(Product).where(
                Product.is_available == True,
                Product.name.ilike(f"%{q}%")
            ).limit(10)
        )
        products = result.scalars().all()
        return products
    
@app.get("/api/test")
async def test_api():
    """Тестовый эндпоинт для проверки работы API"""
    return {
        "status": "ok",
        "message": "API работает",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)