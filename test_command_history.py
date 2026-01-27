#!/usr/bin/env python3
"""
Тест для модуля истории команд
"""

import os
import sys
from command_history import CommandHistory

def test_command_history():
    """Тестирование функциональности истории команд"""
    
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ ИСТОРИИ КОМАНД")
    print("=" * 60)
    
    # Используем тестовый файл
    test_file = 'test_history.json'
    
    # Удаляем тестовый файл если он существует
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Тест 1: Создание и добавление команд
    print("\n📝 Тест 1: Создание истории и добавление команд")
    history = CommandHistory(history_file=test_file, max_entries=5)
    
    # Добавляем несколько команд
    history.add_command("forward", "success", {"speed": 0.7})
    history.add_command("left", "success", {"speed": 0.7})
    history.add_command("right", "success", {"speed": 0.7})
    history.add_command("stop", "success")
    
    all_commands = history.get_all_commands()
    assert len(all_commands) == 4, f"Ожидается 4 команды, получено {len(all_commands)}"
    print(f"✅ Добавлено {len(all_commands)} команд")
    
    # Тест 2: Сохранение и загрузка
    print("\n💾 Тест 2: Сохранение и загрузка истории")
    
    # Создаем новый экземпляр и загружаем историю
    history2 = CommandHistory(history_file=test_file, max_entries=5)
    loaded_commands = history2.load_history()
    
    assert len(loaded_commands) == 4, f"Ожидается 4 команды, загружено {len(loaded_commands)}"
    print(f"✅ Загружено {len(loaded_commands)} команд из файла")
    
    # Тест 3: Ограничение размера истории
    print("\n🔢 Тест 3: Ограничение размера истории (max_entries=5)")
    
    history2.add_command("forward", "success")
    history2.add_command("backward", "success")
    history2.add_command("forward", "success")
    
    all_commands = history2.get_all_commands()
    assert len(all_commands) == 5, f"Ожидается 5 команд (макс), получено {len(all_commands)}"
    print(f"✅ История ограничена до {len(all_commands)} команд")
    
    # Тест 4: Получение последних команд
    print("\n📋 Тест 4: Получение последних N команд")
    
    last_3 = history2.get_last_commands(3)
    assert len(last_3) == 3, f"Ожидается 3 команды, получено {len(last_3)}"
    print(f"✅ Получены последние {len(last_3)} команды")
    
    # Тест 5: Печать истории
    print("\n🖨️  Тест 5: Печать истории")
    history2.print_history(5)
    
    # Тест 6: Очистка истории
    print("\n🗑️  Тест 6: Очистка истории")
    history2.clear_history()
    
    assert len(history2.get_all_commands()) == 0, "История должна быть пустой"
    print("✅ История успешно очищена")
    
    # Удаляем тестовый файл
    if os.path.exists(test_file):
        os.remove(test_file)
    
    print("\n" + "=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_command_history()
    except AssertionError as e:
        print(f"\n❌ ОШИБКА ТЕСТА: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ НЕОЖИДАННАЯ ОШИБКА: {e}")
        sys.exit(1)
