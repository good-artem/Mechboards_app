# back/tests/test_simple.py
"""
Простой тестовый файл без сложных конфигураций
"""
import unittest
import sys
import os

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, Product, Order, OrderStatus

class TestSimpleModels(unittest.TestCase):
    """Простые тесты моделей без базы данных"""
    
    def test_user_model(self):
        """Тест создания модели пользователя"""
        user = User(
            telegram_id=123456,
            username='test_user',
            name='Test User'
        )
        
        self.assertEqual(user.telegram_id, 123456)
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.name, 'Test User')
        
    def test_product_model(self):
        """Тест создания модели товара"""
        product = Product(
            name='Test Product',
            price=1000.00,
            stock_quantity=10
        )
        
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, 1000.00)
        self.assertEqual(product.stock_quantity, 10)
        
    def test_order_status(self):
        """Тест статусов заказа"""
        order = Order(
            order_number='TEST-001',
            total_amount=1000.00,
            status=OrderStatus.CREATED
        )
        
        self.assertEqual(order.status, OrderStatus.CREATED)
        self.assertEqual(order.status.value, "Создан")

if __name__ == '__main__':
    print("Запуск простых тестов...")
    unittest.main()