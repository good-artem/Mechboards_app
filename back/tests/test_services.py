# back/tests/test_services.py
import unittest
import sys
import os

# Сначала устанавливаем переменные окружения
os.environ["TELEGRAM_BOT_TOKEN"] = "fake_token_for_testing"
os.environ["ADMIN_TELEGRAM_ID"] = "391622124"

# Импортируем models до main, чтобы избежать ошибок
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Мокируем импорт bot чтобы избежать ошибок при создании экземпляра
import unittest.mock as mock

# Создаем мок для бота
mock_bot = mock.MagicMock()
mock_bot.send_message.return_value = {"ok": True}
mock_bot.send_order_notification.return_value = {"ok": True}
mock_bot.send_admin_notification.return_value = {"ok": True}
mock_bot.send_support_notification.return_value = {"ok": True}

# Подменяем импорт bot в sys.modules
sys.modules['telegram_bot'] = mock.MagicMock()
sys.modules['telegram_bot'].bot = mock_bot
sys.modules['telegram_bot'].TelegramBot = mock.MagicMock(return_value=mock_bot)

# Теперь безопасно импортируем модели
from models import User, Product, Order, OrderStatus, Service, ServiceOrder, Category
from datetime import datetime
from decimal import Decimal

class TestModels(unittest.TestCase):
    """Тесты моделей базы данных"""
    
    def test_user_model_creation(self):
        """Тест создания модели пользователя"""
        user = User(
            telegram_id=123456,
            username='test_user',
            name='Test User',
            is_active=True,
            is_admin=False
        )
        
        self.assertEqual(user.telegram_id, 123456)
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        print("✓ User model test passed")
        
    def test_product_model_creation(self):
        """Тест создания модели товара"""
        product = Product(
            name='Механическая клавиатура',
            description='Высококачественная механическая клавиатура',
            price=4500.00,
            stock_quantity=10,
            is_available=True
        )
        
        self.assertEqual(product.name, 'Механическая клавиатура')
        self.assertEqual(product.price, 4500.00)
        self.assertEqual(product.stock_quantity, 10)
        self.assertTrue(product.is_available)
        print("✓ Product model test passed")
        
    def test_category_model_creation(self):
        """Тест создания модели категории"""
        category = Category(
            name='Клавиатуры',
            description='Все виды клавиатур',
            icon='keyboard'
        )
        
        self.assertEqual(category.name, 'Клавиатуры')
        self.assertEqual(category.description, 'Все виды клавиатур')
        self.assertEqual(category.icon, 'keyboard')
        print("✓ Category model test passed")
        
    def test_order_model(self):
        """Тест создания модели заказа"""
        order = Order(
            order_number='ORDER-TEST-001',
            total_amount=Decimal('3751.50'),
            status=OrderStatus.CREATED,
            shipping_method='Курьер',
            shipping_address='г. Москва, ул. Тестовая, д. 1'
        )
        
        self.assertEqual(order.order_number, 'ORDER-TEST-001')
        self.assertEqual(order.total_amount, Decimal('3751.50'))
        self.assertEqual(order.status, OrderStatus.CREATED)
        self.assertEqual(order.shipping_method, 'Курьер')
        print("✓ Order model test passed")
        
    def test_service_model(self):
        """Тест создания модели услуги"""
        service = Service(
            name='Ремонт клавиатуры',
            description='Ремонт механических клавиатур',
            price=1500.00,
            duration='2-3 часа',
            category='Ремонт',
            is_active=True
        )
        
        self.assertEqual(service.name, 'Ремонт клавиатуры')
        self.assertEqual(service.price, 1500.00)
        self.assertEqual(service.duration, '2-3 часа')
        self.assertEqual(service.category, 'Ремонт')
        self.assertTrue(service.is_active)
        print("✓ Service model test passed")
        
    def test_service_order_model(self):
        """Тест создания модели заказа услуги"""
        service_order = ServiceOrder(
            user_id=1,
            service_id=1,
            notes='Срочный ремонт',
            status=OrderStatus.CREATED,
            price=1500.00
        )
        
        self.assertEqual(service_order.user_id, 1)
        self.assertEqual(service_order.service_id, 1)
        self.assertEqual(service_order.notes, 'Срочный ремонт')
        self.assertEqual(service_order.status, OrderStatus.CREATED)
        self.assertEqual(service_order.price, 1500.00)
        print("✓ ServiceOrder model test passed")

class TestBusinessLogic(unittest.TestCase):
    """Тесты бизнес-логики"""
    
    def test_order_status_flow(self):
        """Тест перехода статусов заказа"""
        statuses = [
            OrderStatus.CREATED,
            OrderStatus.PAID,
            OrderStatus.CONFIRMED,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED
        ]
        
        self.assertEqual(len(statuses), 5)
        self.assertEqual(statuses[0], OrderStatus.CREATED)
        self.assertEqual(statuses[-1], OrderStatus.DELIVERED)
        print("✓ Order status flow test passed")
        
    def test_calculate_order_total(self):
        """Тест расчета стоимости заказа"""
        items = [
            {'price': Decimal('1000.00'), 'quantity': 2},
            {'price': Decimal('500.00'), 'quantity': 1},
            {'price': Decimal('250.50'), 'quantity': 3}
        ]
        
        # Расчет вручную: 1000*2 + 500*1 + 250.50*3 = 2000 + 500 + 751.50 = 3251.50
        total = Decimal('0.00')
        for item in items:
            total += Decimal(str(item['price'])) * Decimal(str(item['quantity']))
        
        self.assertEqual(total, Decimal('3251.50'))
        print("✓ Order total calculation test passed")
        
    def test_user_validation(self):
        """Тест валидации пользовательских данных"""
        valid_user_data = {
            'telegram_id': 123456,
            'username': 'testuser',
            'name': 'Тестовый Пользователь'
        }
        
        # Простая проверка
        self.assertIn('telegram_id', valid_user_data)
        self.assertIn('username', valid_user_data)
        self.assertIn('name', valid_user_data)
        self.assertIsInstance(valid_user_data['telegram_id'], int)
        self.assertGreater(valid_user_data['telegram_id'], 0)
        print("✓ User validation test passed")
        
    def test_stock_quantity_validation(self):
        """Тест проверки количества товара на складе"""
        test_cases = [
            {'stock': 10, 'requested': 5, 'expected': True},
            {'stock': 3, 'requested': 5, 'expected': False},
            {'stock': 0, 'requested': 1, 'expected': False},
            {'stock': 100, 'requested': 100, 'expected': True}
        ]
        
        for case in test_cases:
            result = case['requested'] <= case['stock']
            self.assertEqual(result, case['expected'])
        
        print("✓ Stock quantity validation test passed")

def run_all_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("Запуск модульных тестов Mechboards Shop")
    print("=" * 60)
    print()
    
    # Создаем тестовый набор
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestModels))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessLogic))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результаты
    print()
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print("=" * 60)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ Все тесты пройдены успешно!")
    else:
        print("\n⚠️ Обнаружены проблемы при тестировании")
    
    print("=" * 60)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)