import asyncio
import sys
import os
from datetime import datetime, timedelta
import json  # Добавьте в начало, если нет

# Добавляем путь к текущей директории для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import async_session, init_db, Category, Product, Service, News, User # Импортируем User и init_db
from sqlalchemy import select, text # Импортируем text для PRAGMA

async def seed_database():
    # Обязательно инициализируем базу данных перед началом работы
    print("Инициализация базы данных...")
    await init_db()
    print("✅ База данных инициализирована (таблицы созданы, если не существовали).")

    async with async_session() as session:
        try:
            print("Начинаем заполнение/обновление базы тестовыми данными...")

            # Проверяем и добавляем колонку image_url в таблицу services
            result = await session.execute(text("PRAGMA table_info(services)"))
            columns = [row[1] for row in result.fetchall()]
            if 'image_url' not in columns:
                print("Добавляем колонку image_url в таблицу services...")
                await session.execute(text("ALTER TABLE services ADD COLUMN image_url VARCHAR(500)")) # Используем VARCHAR(500) как в модели
                await session.commit() # Коммитим сразу после ALTER TABLE
                print("✅ Колонка image_url добавлена")
            else:
                print("✅ Колонка image_url уже существует.")

            # Проверяем и добавляем колонку is_admin в таблицу users
            result_users = await session.execute(text("PRAGMA table_info(users)"))
            user_columns = [row[1] for row in result_users.fetchall()]
            if 'is_admin' not in user_columns:
                print("Добавляем колонку is_admin в таблицу users...")
                await session.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")) # 0 = False
                await session.commit() # Коммитим сразу после ALTER TABLE
                print("✅ Колонка is_admin добавлена")
            else:
                print("✅ Колонка is_admin уже существует.")


            # 1. КАТЕГОРИИ - upsert (обновляем если есть, создаем если нет)
            categories_data = [
                {"name": "Весь каталог", "description": "Весь каталог", "icon": "mdi-keyboard"},
                {"name": "Механические клавиатуры", "description": "Полноразмерные и компактные механические клавиатуры", "icon": "mdi-keyboard"},
                {"name": "Свитчи", "description": "Механические переключатели для клавиатур", "icon": "mdi-circle-multiple"},
                {"name": "Кейкапы", "description": "Колпачки для клавиш", "icon": "mdi-checkbox-multiple-blank"},
                {"name": "Стабилизаторы", "description": "Стабилизаторы для длинных клавиш", "icon": "mdi-arrow-split-vertical"},
                {"name": "Смазка и моддинг", "description": "Материалы для модификации клавиатур", "icon": "mdi-bottle-tonic"},
                {"name": "Аксессуары", "description": "Кабели, коврики и другие аксессуары", "icon": "mdi-cable-data"},
                {"name": "Скидки", "description": "Товары со скидкой", "icon": "mdi-sale"},
                {"name": "БУ клавиатуры", "description": "Бывшие в употреблении клавиатуры", "icon": "mdi-keyboard-return"},
            ]

            created_categories = {}
            for cat_data in categories_data:
                # Проверяем, существует ли категория с таким именем
                result = await session.execute(
                    select(Category).where(Category.name == cat_data["name"])
                )
                category = result.scalar_one_or_none()
                
                if category:
                    # Обновляем существующую категорию
                    category.description = cat_data["description"]
                    category.icon = cat_data["icon"]
                    print(f"📝 Обновлена категория: {cat_data['name']}")
                else:
                    # Создаем новую категорию
                    category = Category(
                        name=cat_data["name"],
                        description=cat_data["description"],
                        icon=cat_data["icon"]
                    )
                    session.add(category)
                    print(f"✅ Создана категория: {cat_data['name']}")
                
                # Добавляем в словарь для быстрого поиска по имени
                await session.flush() # Убеждаемся, что category_id доступен
                created_categories[category.name] = category
            
            print("✅ Категории обновлены/созданы")

            # 2. ТОВАРЫ - upsert по названию
            products_data = [
                {
                    "name": "Keychron K2",
                    "description": "Компактная 75% механическая клавиатура с Bluetooth",
                    "price": 4500.00,
                    "stock_quantity": 15,
                    "category_name": "Весь каталог", # Используем имя категории
                    "images": [
                        "assets/images/products/Keychron_k2/Keychron_k2_1.png",
                        "assets/images/products/Keychron_k2/Keychron_k2_2.png",
                        "assets/images/products/Keychron_k2/Keychron_k2_3.png"
                    ],
                    "is_available": True
                },
                {
                    "name": "Gateron Yellow Switches",
                    "description": "Линейные свитчи Gateron Yellow (35 шт)",
                    "price": 800.00,
                    "stock_quantity": 50,
                    "category_name": "Свитчи", # Используем имя категории
                    "images": [
                        "assets/images/products/Gateron_yellow_switches/Gateron_yellow_switches_1.png",
                        "assets/images/products/Gateron_yellow_switches/Gateron_yellow_switches_2.png",
                        "assets/images/products/Gateron_yellow_switches/Gateron_yellow_switches_3.png"
                    ],
                    "is_available": True
                },
                {
                    "name": "PBT Keycaps Set",
                    "description": "Набор кейкапов из PBT пластика",
                    "price": 1200.00,
                    "stock_quantity": 25,
                    "category_name": "Кейкапы", # Используем имя категории
                    "images": [
                        "assets/images/products/PBT_keycaps_set/PBT_keycaps_set_1.png",
                        "assets/images/products/PBT_keycaps_set/PBT_keycaps_set_2.png",
                        "assets/images/products/PBT_keycaps_set/PBT_keycaps_set_3.png"
                    ],
                    "is_available": True
                },
                {
                    "name": "Стабилизаторы Cherry",
                    "description": "Набор стабилизаторов для клавиатуры",
                    "price": 400.00,
                    "stock_quantity": 30,
                    "category_name": "Стабилизаторы", # Используем имя категории
                    "images": [
                        "assets/images/products/Стабилизаторы_Cherry/Стабилизаторы_Cherry_1.png",
                        "assets/images/products/Стабилизаторы_Cherry/Стабилизаторы_Cherry_2.png",
                    ],
                    "is_available": True
                },
                {
                    "name": "Смазка Krytox 205g0",
                    "description": "Смазка для свитчей и стабилизаторов",
                    "price": 600.00,
                    "stock_quantity": 20,
                    "category_name": "Смазка и моддинг", # Используем имя категории
                    "images": [
                        "assets/images/products/Смазка_krytox_205g0/Смазка_krytox_205g0_1.png",
                        "assets/images/products/Смазка_krytox_205g0/Смазка_krytox_205g0_2.png",
                    ],
                    "is_available": True
                },
            ]

            for prod_data in products_data:
                # Находим категорию по имени
                category = created_categories.get(prod_data["category_name"])
                if not category:
                    print(f"⚠️ Категория '{prod_data['category_name']}' не найдена для товара '{prod_data['name']}', пропускаем.")
                    continue

                result = await session.execute(
                    select(Product).where(Product.name == prod_data["name"])
                )
                product = result.scalar_one_or_none()
                
                if product:
                    # Обновляем существующий товар
                    product.description = prod_data["description"]
                    product.price = prod_data["price"]
                    product.category_id = category.category_id # Присваиваем ID найденной категории
                    product.images = json.dumps(prod_data["images"])
                    product.is_available = prod_data["is_available"]
                    # Не обновляем stock_quantity чтобы не сбрасывать остатки
                    # product.stock_quantity = prod_data["stock_quantity"]
                    print(f"📝 Обновлен товар: {prod_data['name']}")
                else:
                    # Создаем новый товар
                    product = Product(
                        name=prod_data["name"],
                        description=prod_data["description"],
                        price=prod_data["price"],
                        stock_quantity=prod_data["stock_quantity"],
                        category_id=category.category_id, # Присваиваем ID найденной категории
                        images=json.dumps(prod_data["images"]),
                        is_available=prod_data["is_available"]
                    )
                    session.add(product)
                    print(f"✅ Создан товар: {prod_data['name']}")
            
            print("✅ Товары обновлены/созданы")

            # 3. УСЛУГИ - upsert по названию
            services_data = [
                {
                    "name": "Сборка клавиатуры",
                    "description": "Профессиональная сборка механической клавиатуры",
                    "price": 1500.00,
                    "duration": "2-3 дня",
                    "category": "Сборка",
                    "is_active": True,
                    "image_url": "https://via.placeholder.com/100x100/667eea/ffffff?text=Assembly" # Добавляем image_url
                },
                {
                    "name": "Лубрикация свитчей",
                    "description": "Смазка механических переключателей",
                    "price": 800.00,
                    "duration": "1-2 дня",
                    "category": "Моддинг",
                    "is_active": True,
                    "image_url": "https://via.placeholder.com/100x100/764ba2/ffffff?text=Lubrication" # Добавляем image_url
                },
                {
                    "name": "Замена стабилизаторов",
                    "description": "Замена и настройка стабилизаторов",
                    "price": 500.00,
                    "duration": "1 день",
                    "category": "Ремонт",
                    "is_active": True,
                    "image_url": "https://via.placeholder.com/100x100/43e97b/ffffff?text=Stabs" # Добавляем image_url
                },
            ]

            for serv_data in services_data:
                result = await session.execute(
                    select(Service).where(Service.name == serv_data["name"])
                )
                service = result.scalar_one_or_none()
                
                if service:
                    # Обновляем существующую услугу
                    service.description = serv_data["description"]
                    service.price = serv_data["price"]
                    service.duration = serv_data["duration"]
                    service.category = serv_data["category"]
                    service.is_active = serv_data["is_active"]
                    service.image_url = serv_data.get("image_url") # Обновляем image_url, если есть
                    print(f"📝 Обновлена услуга: {serv_data['name']}")
                else:
                    # Создаем новую услугу
                    service = Service(
                        name=serv_data["name"],
                        description=serv_data["description"],
                        price=serv_data["price"],
                        duration=serv_data["duration"],
                        category=serv_data["category"],
                        is_active=serv_data["is_active"],
                        image_url=serv_data.get("image_url") # Присваиваем image_url, если есть
                    )
                    session.add(service)
                    print(f"✅ Создана услуга: {serv_data['name']}")
            
            print("✅ Услуги обновлены/созданы")

            # 4. НОВОСТИ - upsert по заголовку
            news_data = [
                {
                    "title": "Новые клавиатуры",
                    "description": "Поступление новых механических клавиатур",
                    "icon": "mdi-keyboard",
                    "image_url": "https://via.placeholder.com/300x150/667eea/ffffff?text=New+Keyboards  ",
                    "news_type": "promo", # Исправлено: 'new_products' -> 'promo' или другое допустимое значение
                    "action_url": "/catalog?filter=new",
                    "is_active": True,
                    "expires_at": datetime.now() + timedelta(days=30)
                },
                {
                    "title": "Скидки 20%",
                    "description": "Специальные предложения на selected товары",
                    "icon": "mdi-sale",
                    "image_url": "https://via.placeholder.com/300x150/764ba2/ffffff?text=Discount+20%  ",
                    "news_type": "discount", # Исправлено: 'promo' -> 'discount'
                    "action_url": "/catalog?filter=discount",
                    "is_active": True,
                    "expires_at": datetime.now() + timedelta(days=15)
                },
                {
                    "title": "Доставка за 24ч",
                    "description": "Экспресс-доставка по Москве и области",
                    "icon": "mdi-truck-fast",
                    "image_url": "https://via.placeholder.com/300x150/f093fb/ffffff?text=Fast+Delivery  ",
                    "news_type": "delivery", # Исправлено: 'promo' -> 'delivery'
                    "action_url": "/support",
                    "is_active": True,
                    "expires_at": datetime.now() + timedelta(days=60)
                },
                {
                    "title": "Кейкапы",
                    "description": "Новая коллекция кейкапов",
                    "icon": "mdi-circle-multiple",
                    "image_url": "https://via.placeholder.com/300x150/4facfe/ffffff?text=Keycaps  ",
                    "news_type": "category", # Исправлено: 'promo' -> 'category'
                    "action_url": "/catalog?category=keycaps",
                    "is_active": True,
                    "expires_at": datetime.now() + timedelta(days=45)
                },
                {
                    "title": "Аксессуары",
                    "description": "Кабели, коврики и другие аксессуары",
                    "icon": "mdi-cable-data",
                    "image_url": "https://via.placeholder.com/300x150/43e97b/ffffff?text=Accessories  ",
                    "news_type": "category", # Исправлено: 'promo' -> 'category'
                    "action_url": "/catalog?category=accessories",
                    "is_active": True,
                    "expires_at": datetime.now() + timedelta(days=30)
                }
            ]

            for news_item in news_data:
                result = await session.execute(
                    select(News).where(News.title == news_item["title"])
                )
                news = result.scalar_one_or_none()
                
                if news:
                    # Обновляем существующую новость
                    news.description = news_item["description"]
                    news.icon = news_item["icon"]
                    news.image_url = news_item["image_url"]
                    news.news_type = news_item["news_type"] # Используем исправленный тип
                    news.action_url = news_item["action_url"]
                    news.is_active = news_item["is_active"]
                    news.expires_at = news_item["expires_at"]
                    print(f"📝 Обновлена новость: {news_item['title']}")
                else:
                    # Создаем новую новость
                    news = News(
                        title=news_item["title"],
                        description=news_item["description"],
                        icon=news_item["icon"],
                        image_url=news_item["image_url"],
                        news_type=news_item["news_type"], # Используем исправленный тип
                        action_url=news_item["action_url"],
                        is_active=news_item["is_active"],
                        expires_at=news_item["expires_at"]
                    )
                    session.add(news)
                    print(f"✅ Создана новость: {news_item['title']}")
            
            print("✅ Новости обновлены/созданы")

            # Создаем администратора по умолчанию
            admin_telegram_id = 391622124
            result = await session.execute(
                select(User).where(User.telegram_id == admin_telegram_id)
            )
            admin_user = result.scalar_one_or_none()
            
            if admin_user:
                # Обновляем существующего пользователя
                admin_user.is_admin = True
                print(f"✅ Пользователь {admin_telegram_id} назначен администратором")
            else:
                # Создаем нового администратора
                admin_user = User(
                    telegram_id=admin_telegram_id,
                    username="admin_user",
                    name="Администратор",
                    is_active=True,
                    is_admin=True
                )
                session.add(admin_user)
                print(f"✅ Создан администратор с ID {admin_telegram_id}")
            
            await session.commit()
            print("✅ База данных успешно обновлена!")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при обновлении базы: {e}")
            import traceback # Добавляем вывод полного стека ошибок
            traceback.print_exc()
            raise
    
    await session.commit()
# ИЗМЕНИТЕ вызов в конце файла:
if __name__ == "__main__":
    asyncio.run(seed_database())
