import asyncio
import sys
import os
from datetime import datetime, timedelta

# Добавляем путь к текущей директории для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import async_session, Category, Product, Service, News
from sqlalchemy import select

async def seed_database():
    async with async_session() as session:
        try:
            # Проверяем, есть ли уже данные
            existing_categories = await session.execute(select(Category))
            if existing_categories.scalars().first():
                print("База уже содержит данные, пропускаем заполнение")
                return

            print("Начинаем заполнение базы тестовыми данными...")

            # Создаем категории
            categories_data = [
                Category(name="Весь каталог", description="Весь каталог", icon="mdi-keyboard"),
                Category(name="Механические клавиатуры", description="Полноразмерные и компактные механические клавиатуры", icon="mdi-keyboard"),
                Category(name="Свитчи", description="Механические переключатели для клавиатур", icon="mdi-circle-multiple"),
                Category(name="Кейкапы", description="Колпачки для клавиш", icon="mdi-checkbox-multiple-blank"),
                Category(name="Стабилизаторы", description="Стабилизаторы для длинных клавиш", icon="mdi-arrow-split-vertical"),
                Category(name="Смазка и моддинг", description="Материалы для модификации клавиатур", icon="mdi-bottle-tonic"),
                Category(name="Аксессуары", description="Кабели, коврики и другие аксессуары", icon="mdi-cable-data"),
                Category(name="Скидки", description="Товары со скидкой", icon="mdi-sale"),
                Category(name="БУ клавиатуры", description="Бывшие в употреблении клавиатуры", icon="mdi-keyboard-return"),
            ]

            session.add_all(categories_data)
            await session.flush()
            print("✅ Категории созданы")

            # Создаем товары
            products_data = [
                Product(
                    name="Keychron K2",
                    description="Компактная 75% механическая клавиатура с Bluetooth",
                    price=4500.00,
                    stock_quantity=15,
                    category_id=categories_data[0].category_id,
                    images=json.dumps([
                        "Mechboards_app\front\src\assets\images\products\Keychron_k2\Keychron_k2_1.png",
                        "Mechboards_app\front\src\assets\images\products\Keychron_k2\Keychron_k2_2.png",
                        "Mechboards_app\front\src\assets\images\products\Keychron_k2\Keychron_k2_3.png"
                    ]),                    
                    is_available=True
                ),
                Product(
                    name="Gateron Yellow Switches",
                    description="Линейные свитчи Gateron Yellow (35 шт)",
                    price=800.00,
                    stock_quantity=50,
                    category_id=categories_data[1].category_id,
                    images=json.dumps([
                        "Mechboards_app\front\src\assets\images\products\Gateron_yellow _switches\Gateron_yellow _switches_1.png",
                        "Mechboards_app\front\src\assets\images\products\Gateron_yellow _switches\Gateron_yellow _switches_2.png",
                        "Mechboards_app\front\src\assets\images\products\Gateron_yellow _switches\Gateron_yellow _switches_3.png"
                    ]),                      
                    is_available=True
                ),
                Product(
                    name="PBT Keycaps Set",
                    description="Набор кейкапов из PBT пластика",
                    price=1200.00,
                    stock_quantity=25,
                    category_id=categories_data[2].category_id,
                    images=json.dumps([
                        "Mechboards_app\front\src\assets\images\products\PBT_keycaps_set\PBT_keycaps_set_1.png",
                        "Mechboards_app\front\src\assets\images\products\PBT_keycaps_set\PBT_keycaps_set_2.png",
                        "Mechboards_app\front\src\assets\images\products\PBT_keycaps_set\PBT_keycaps_set_3.png"
                    ]),                      
                    is_available=True
                ),
                Product(
                    name="Стабилизаторы Cherry",
                    description="Набор стабилизаторов для клавиатуры",
                    price=400.00,
                    stock_quantity=30,
                    category_id=categories_data[3].category_id,
                    images=json.dumps([
                        "Mechboards_app\front\src\assets\images\products\Стабилизаторы_Cherry\Стабилизаторы_Cherry_1.png",
                        "Mechboards_app\front\src\assets\images\products\Стабилизаторы_Cherry\Стабилизаторы_Cherry_2.png",
                    ]),                      
                    is_available=True
                ),
                Product(
                    name="Смазка Krytox 205g0",
                    description="Смазка для свитчей и стабилизаторов",
                    price=600.00,
                    stock_quantity=20,
                    category_id=categories_data[4].category_id,
                    images=json.dumps([
                        "Mechboards_app\front\src\assets\images\products\Смазка_krytox_205g0\Смазка_krytox_205g0_1.png",
                        "Mechboards_app\front\src\assets\images\products\Смазка_krytox_205g0\Смазка_krytox_205g0_2.png",
                    ]),                      
                    is_available=True
                ),
            ]

            session.add_all(products_data)
            print("✅ Товары созданы")

            # Создаем услуги
            services_data = [
                Service(
                    name="Сборка клавиатуры",
                    description="Профессиональная сборка механической клавиатуры",
                    price=1500.00,
                    duration="2-3 дня",
                    category="Сборка",
                    is_active=True
                ),
                Service(
                    name="Лубрикация свитчей",
                    description="Смазка механических переключателей",
                    price=800.00,
                    duration="1-2 дня",
                    category="Моддинг",
                    is_active=True
                ),
                Service(
                    name="Замена стабилизаторов",
                    description="Замена и настройка стабилизаторов",
                    price=500.00,
                    duration="1 день",
                    category="Ремонт",
                    is_active=True
                ),
            ]

            session.add_all(services_data)
            print("✅ Услуги созданы")

            # Создаем новости
            news_data = [
                News(
                    title="Новые клавиатуры",
                    description="Поступление новых механических клавиатур",
                    icon="mdi-keyboard",
                    image_url="https://via.placeholder.com/300x150/667eea/ffffff?text=New+Keyboards",
                    news_type="new_products",
                    action_url="/catalog?filter=new",
                    is_active=True,
                    expires_at=datetime.now() + timedelta(days=30)
                ),
                News(
                    title="Скидки 20%",
                    description="Специальные предложения на selected товары",
                    icon="mdi-sale",
                    image_url="https://via.placeholder.com/300x150/764ba2/ffffff?text=Discount+20%",
                    news_type="discount",
                    action_url="/catalog?filter=discount",
                    is_active=True,
                    expires_at=datetime.now() + timedelta(days=15)
                ),
                News(
                    title="Доставка за 24ч",
                    description="Экспресс-доставка по Москве и области",
                    icon="mdi-truck-fast",
                    image_url="https://via.placeholder.com/300x150/f093fb/ffffff?text=Fast+Delivery",
                    news_type="delivery",
                    action_url="/support",
                    is_active=True,
                    expires_at=datetime.now() + timedelta(days=60)
                ),
                News(
                    title="Кейкапы",
                    description="Новая коллекция кейкапов",
                    icon="mdi-circle-multiple",
                    image_url="https://via.placeholder.com/300x150/4facfe/ffffff?text=Keycaps",
                    news_type="category",
                    action_url="/catalog?category=keycaps",
                    is_active=True,
                    expires_at=datetime.now() + timedelta(days=45)
                ),
                News(
                    title="Аксессуары",
                    description="Кабели, коврики и другие аксессуары",
                    icon="mdi-cable-data",
                    image_url="https://via.placeholder.com/300x150/43e97b/ffffff?text=Accessories",
                    news_type="category",
                    action_url="/catalog?category=accessories",
                    is_active=True,
                    expires_at=datetime.now() + timedelta(days=30)
                )
            ]

            session.add_all(news_data)
            print("✅ Новости созданы")

            await session.commit()
            print("✅ Тестовые данные успешно добавлены в базу!")

        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при заполнении базы: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(seed_database())