# back/tests/test_config.py
"""
Конфигурация для тестов, устанавливает переменные окружения перед импортом
"""
import os
os.environ["TELEGRAM_BOT_TOKEN"] = "fake_token_for_testing"
os.environ["ADMIN_TELEGRAM_ID"] = "391622124"