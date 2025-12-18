from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
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
    expose_headers=["*"]
)

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Разрешаем OPTIONS запросы (preflight)
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            content={"status": "ok"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, X-Telegram-Init-Data, Authorization",
                "Access-Control-Expose-Headers": "*",
                "Access-Control-Max-Age": "86400"
            }
        )
    
    # Публичные эндпоинты
    public_paths = [
        '/api/categories',
        '/api/products',
        '/api/news',
        '/docs',
        '/openapi.json',
        '/api/health',
        '/api/products/search',
        '/assets',
        '/api/telegram-test',
        '/api/debug/headers',
        '/api/test-images',
        '/api/me'
    ]
    
    # Проверяем, публичный ли эндпоинт
    is_public = any(request.url.path.startswith(path) for path in public_paths)
    
    if is_public:
        response = await call_next(request)
        # Добавляем CORS заголовки
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
        return response
    
    # Для защищенных эндпоинтов проверяем авторизацию
    init_data = request.headers.get('x-telegram-init-data')
    
    # ДЛЯ ТЕСТИРОВАНИЯ: временно разрешаем без авторизации
    # В реальном приложении раскомментируйте проверку ниже
    if not init_data:
        # Вместо возврата ошибки 401, пропускаем для тестирования
        print(f"⚠️ No Telegram auth header for protected endpoint: {request.url.path}")
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
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
        return response
    
    try:
        if init_data and not verify_telegram_hash(init_data):
            print(f"⚠️ Invalid Telegram hash for: {request.url.path}")
            # return JSONResponse(
            #     status_code=401,
            #     content={"detail": "Невалидная авторизация"},
            #     headers={
            #         "Access-Control-Allow-Origin": "*",
        #         "Access-Control-Expose-Headers": "*"
        #     }
        # )
        # Для тестирования - пропускаем запрос
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
        return response
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return JSONResponse(
            status_code=401,
            content={"detail": f"Ошибка авторизации: {str(e)}"},
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
        query = select(Product).where(Product.is_available == True)
        if category_id:
            query = query.where(Product.category_id == category_id)
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        products = result.scalars().all()
        return products

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
            Product.is_available == True,
            Product.stock_quantity > 0
        )
        
        if q:
            query = query.where(Product.name.ilike(f"%{q}%"))
        
        if category_id:
            query = query.where(Product.category_id == category_id)
            
        query = query.limit(limit).offset(offset)
        
        result = await session.execute(query)
        products = result.scalars().all()
        return products

# Защищенные эндпоинты (требуют авторизации)
@app.get("/api/users/{telegram_id}")
async def get_user(
    telegram_id: int, 
    user_data: dict = Depends(get_current_user)
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
    request: CreateUserRequest,
    user_data: dict = Depends(lambda x_telegram_init_data=Header(None): 
                              verify_user_access(request.telegram_id, x_telegram_init_data))
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
    telegram_id: int,
    user_data: dict = Depends(get_current_user)
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
    request: AddToCartRequest,
    user_data: dict = Depends(lambda x_telegram_init_data=Header(None): 
                              verify_user_access(request.telegram_id, x_telegram_init_data))
):
    async with async_session() as session:
        # Находим пользователя
        user_result = await session.execute(
            select(User).where(User.telegram_id == request.telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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

@app.get("/api/cart/{telegram_id}")
async def get_cart(
    telegram_id: int,
    user_data: dict = Depends(get_current_user)
):
    async with async_session() as session:
        # Находим пользователя и его корзину
        user_result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        cart_result = await session.execute(
            select(Cart).where(Cart.user_id == user.user_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
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
    request: UpdateCartItemRequest,
    x_telegram_init_data: str = Header(None)
):
    async with async_session() as session:
        # Находим элемент корзины
        result = await session.execute(
            select(CartItem).where(CartItem.cart_item_id == request.cart_item_id)
        )
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Находим корзину и пользователя
        cart_result = await session.execute(
            select(Cart).where(Cart.cart_id == cart_item.cart_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        user_result = await session.execute(
            select(User).where(User.user_id == cart.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Проверяем доступ пользователя
        verify_user_access(user.telegram_id, x_telegram_init_data)
        
        # Обновляем количество
        cart_item.quantity = request.quantity
        await session.commit()
        
        return {"status": "success", "message": "Cart updated"}

@app.delete("/api/cart/remove")
async def remove_cart_item(
    request: RemoveCartItemRequest,
    x_telegram_init_data: str = Header(None)
):
    async with async_session() as session:
        # Находим элемент корзины
        result = await session.execute(
            select(CartItem).where(CartItem.cart_item_id == request.cart_item_id)
        )
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Находим корзину и пользователя
        cart_result = await session.execute(
            select(Cart).where(Cart.cart_id == cart_item.cart_id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        user_result = await session.execute(
            select(User).where(User.user_id == cart.user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Проверяем доступ пользователя
        verify_user_access(user.telegram_id, x_telegram_init_data)
        
        # Удаляем элемент корзины
        await session.delete(cart_item)
        await session.commit()
        
        return {"status": "success", "message": "Item removed from cart"}

@app.post("/api/orders/create")
async def create_order(
    request: CreateOrderRequest,
    user_data: dict = Depends(lambda x_telegram_init_data=Header(None): 
                              verify_user_access(request.telegram_id, x_telegram_init_data))
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


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
async def get_current_user_data(x_telegram_init_data: str = Header(None)):
    """Получить данные текущего пользователя"""
    if not x_telegram_init_data:
        return {"status": "error", "message": "No Telegram init data"}
    
    if not verify_telegram_hash(x_telegram_init_data):
        return {"status": "error", "message": "Invalid Telegram hash"}
    
    user_data = get_telegram_user_from_init_data(x_telegram_init_data)
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_data.get('id'))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"status": "not_found", "telegram_user": user_data}
        
        return {"status": "success", "user": user, "telegram_user": user_data}
    
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