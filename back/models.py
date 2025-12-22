from sqlalchemy import ForeignKey, String, BigInteger, Boolean, DateTime, Text, DECIMAL, JSON, Enum, Integer
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional, TYPE_CHECKING

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Enum для статусов
class OrderStatus(str, PyEnum):
    CREATED = "Создан"
    PAID = "Оплачен"
    CONFIRMED = "Подтвержден"
    SHIPPED = "Отправлен"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменен"

class PaymentStatus(PyEnum):
    PENDING = "Ожидание"
    COMPLETED = "Выполнен"
    FAILED = "Ошибка"
    REFUNDED = "Возврат"

class ServiceStatus(PyEnum):
    PENDING = "Ожидание"
    IN_PROGRESS = "В работе"
    COMPLETED = "Выполнен"

# Сначала определяем пользователей и базовые сущности
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
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    cart: Mapped[Optional["Cart"]] = relationship("Cart", back_populates="user", uselist=False)
    service_orders: Mapped[list["ServiceOrder"]] = relationship("ServiceOrder", back_populates="user")

class Category(Base):
    __tablename__ = 'categories'
    category_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)  # Добавлено поле для иконки
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
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
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.category_id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    images: Mapped[str] = mapped_column(Text, nullable=True)  # Храним как JSON строку
    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="product")

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

class Service(Base):
    __tablename__ = 'services'
    service_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    duration: Mapped[str] = mapped_column(String(50), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    # Relationships
    service_orders: Mapped[list["ServiceOrder"]] = relationship("ServiceOrder", back_populates="service", cascade="all, delete-orphan")
    cart_service_items: Mapped[list["CartServiceItem"]] = relationship("CartServiceItem", back_populates="service", cascade="all, delete-orphan") 

class ServiceOrder(Base):
    __tablename__ = 'service_orders'
    service_order_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.service_id'), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), nullable=False, default=OrderStatus.CREATED)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="service_orders")
    service: Mapped["Service"] = relationship("Service", back_populates="service_orders")

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
    cart_items: Mapped[list["CartItem"]] = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    cart_service_items: Mapped[list["CartServiceItem"]] = relationship("CartServiceItem", back_populates="cart", cascade="all, delete-orphan") 
    
class CartItem(Base):
    __tablename__ = 'cart_items'
    cart_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.cart_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")

class CartServiceItem(Base):
    __tablename__ = 'cart_service_items'
    cart_service_item_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('carts.cart_id', ondelete='CASCADE'), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey('services.service_id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    notes: Mapped[str] = mapped_column(Text, nullable=True)  # Комментарии к услуге
    # Relationships
    cart: Mapped["Cart"] = relationship("Cart", back_populates="cart_service_items")
    service: Mapped["Service"] = relationship("Service", back_populates="cart_service_items")

class News(Base):
    __tablename__ = 'news'
    news_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    news_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'promo', 'category', 'delivery', 'discount'
    action_url: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class SupportTicket(Base):
    __tablename__ = 'support_tickets'
    ticket_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='open')  # open, closed, pending
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    # Relationships
    user: Mapped["User"] = relationship("User")
    messages: Mapped[List["SupportMessage"]] = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan")

class SupportMessage(Base):
    __tablename__ = 'support_messages'
    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey('support_tickets.ticket_id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_from_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    # Relationships
    ticket: Mapped["SupportTicket"] = relationship("SupportTicket", back_populates="messages")
    user: Mapped["User"] = relationship("User")
    
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)