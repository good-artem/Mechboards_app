from sqlalchemy import ForeignKey, String, BigInteger, Boolean, DateTime, Text, DECIMAL, JSON, Enum, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Enum для статусов
class OrderStatus(PyEnum):
    CREATED = "Создан"
    PAID = "Оплачен"
    CONFIRMED = "Подтвержден"
    SHIPPED = "Отправлен"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменен"

class PaymentStatus(PyEnum):
    PENDING = "Ожидание"
    COMPLETED = "Выболнен"
    FAILED = "Ожибка"
    REFUNDED = "Возврат"

class ServiceStatus(PyEnum):
    PENDING = "Ожидание"
    IN_PROGRESS = "В работе"
    COMPLETED = "Выполенен"

class User(Base):
    __tablename__ = 'users'
    
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(128), nullable=True)  # Полное имя
    address: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    cart: Mapped["Cart"] = relationship("Cart", back_populates="user", uselist=False)

class Category(Base):
    __tablename__ = 'categories'
    
    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    
    # Relationships
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[category_id], backref="subcategories")

class Product(Base):
    __tablename__ = 'products'
    
    product_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    images: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")

class Service(Base):
    __tablename__ = 'services'
    
    service_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    duration: Mapped[str] = mapped_column(String(50), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Relationships
    order_services: Mapped[list["OrderService"]] = relationship("OrderService", back_populates="service")

class Order(Base):
    __tablename__ = 'orders'
    
    order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    total_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False, default=OrderStatus.CREATED)
    shipping_method: Mapped[str] = mapped_column(String(100), nullable=True)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=True)
    customer_notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")
    order_services: Mapped[list["OrderService"]] = relationship("OrderService", back_populates="order")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    order_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.product_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")

class OrderService(Base):
    __tablename__ = 'order_services'
    
    order_service_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.service_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    total_price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[ServiceStatus] = mapped_column(Enum(ServiceStatus), nullable=False, default=ServiceStatus.PENDING)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="order_services")
    service: Mapped["Service"] = relationship("Service", back_populates="order_services")

class Payment(Base):
    __tablename__ = 'payments'
    
    payment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
    payment_status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    transaction_id: Mapped[str] = mapped_column(String(100), nullable=True)
    payment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payments")

class Cart(Base):
    __tablename__ = 'carts'
    
    cart_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cart")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="cart")

class CartItem(Base):
    __tablename__ = 'cart_items'
    
    cart_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.cart_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)