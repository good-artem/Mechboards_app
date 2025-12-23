# back/run_all_tests.py
"""
Скрипт для запуска всех тестов
"""
import os
import sys
import subprocess
import time

def run_tests():
    """Запуск всех тестов"""
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ МЕХАНИЧЕСКОЙ МАСТЕРСКОЙ")
    print("=" * 60)
    print()
    
    # Устанавливаем переменные окружения
    os.environ["TELEGRAM_BOT_TOKEN"] = "fake_token_for_testing"
    os.environ["ADMIN_TELEGRAM_ID"] = "391622124"
    
    # Запускаем отдельные тестовые файлы
    test_files = [
        "tests/test_services.py",
        "tests/test_api_endpoints.py"
    ]
    
    results = []
    total_tests = 0
    passed_tests = 0
    
    for test_file in test_files:
        print(f"Запуск тестов из файла: {test_file}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Запускаем тестовый файл
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Тесты успешно завершены за {elapsed_time:.2f} сек")
                passed_tests += 1
            else:
                print(f"❌ Тесты завершились с ошибкой за {elapsed_time:.2f} сек")
                if result.stderr:
                    print("Ошибки:")
                    print(result.stderr[:500])  # Показываем только начало ошибок
            
            # Извлекаем статистику из вывода
            if "Всего тестов:" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Всего тестов:" in line:
                        tests = int(line.split(":")[1].strip())
                        total_tests += tests
            
            results.append({
                'file': test_file,
                'success': result.returncode == 0,
                'time': elapsed_time
            })
            
            print()
            
        except subprocess.TimeoutExpired:
            print(f"❌ Тесты превысили время выполнения (30 сек)")
            results.append({
                'file': test_file,
                'success': False,
                'time': 30
            })
            print()
        except Exception as e:
            print(f"❌ Ошибка запуска тестов: {e}")
            results.append({
                'file': test_file,
                'success': False,
                'time': 0
            })
            print()
    
    # Вывод итоговой статистики
    print("=" * 60)
    print("ИТОГОВАЯ СТАТИСТИКА ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    successful_files = sum(1 for r in results if r['success'])
    
    print(f"Файлов с тестами: {len(results)}")
    print(f"Успешно пройдено: {successful_files}")
    print(f"Всего тестов выполнено: {total_tests}")
    
    print("\nПодробная статистика по файлам:")
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"  {status} {r['file']}: {r['time']:.2f} сек")
    
    print("\n" + "=" * 60)
    
    if successful_files == len(results):
        print("🎉 ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        return True
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ")
        return False

if __name__ == "__main__":
    print("""
    ███╗   ███╗███████╗ ██████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗ ███████╗
    ████╗ ████║██╔════╝██╔════╝██║  ██║██╔══██╗██╔════╝ ██╔══██╗██╔══██╗██╔══██╗██╔════╝
    ██╔████╔██║█████╗  ██║     ███████║██████╔╝██║  ███╗███████║███████║██████╔╝███████╗
    ██║╚██╔╝██║██╔══╝  ██║     ██╔══██║██╔══██╗██║   ██║██╔══██║██╔══██║██╔══██╗╚════██║
    ██║ ╚═╝ ██║███████╗╚██████╗██║  ██║██║  ██║╚██████╔╝██║  ██║██║  ██║██████╔╝███████║
    ╚═╝     ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
    """)
    
    success = run_tests()
    sys.exit(0 if success else 1)