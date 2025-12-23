# back/tests/conftest.py
"""
Минимальный файл конфигурации для pytest
"""
import os
import pytest

# Устанавливаем переменные окружения для тестов
os.environ["TELEGRAM_BOT_TOKEN"] = "fake_token_for_testing"
os.environ["ADMIN_TELEGRAM_ID"] = "391622124"

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Настройка тестового окружения"""
    # Дополнительная настройка при необходимости
    yield
    # Очистка после тестов