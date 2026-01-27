#!/usr/bin/env python3
"""
Модуль для сохранения и загрузки истории команд робота
"""

import json
import os
from datetime import datetime
from typing import List, Dict

class CommandHistory:
    def __init__(self, history_file='robot_command_history.json', max_entries=1000):
        """
        Инициализация менеджера истории команд
        
        Args:
            history_file: Имя файла для сохранения истории
            max_entries: Максимальное количество записей в истории
        """
        self.history_file = history_file
        self.max_entries = max_entries
        self.commands = []
        
    def load_history(self) -> List[Dict]:
        """Загружает историю команд из файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Валидация загруженных данных
                if not isinstance(data, list):
                    print("⚠️  Неверный формат файла истории (ожидается список)")
                    self.commands = []
                    return self.commands
                
                # Проверяем каждую запись на наличие обязательных полей
                validated_commands = []
                for entry in data:
                    if isinstance(entry, dict) and 'timestamp' in entry and 'command' in entry and 'status' in entry:
                        validated_commands.append(entry)
                    else:
                        print(f"⚠️  Пропущена некорректная запись: {entry}")
                
                self.commands = validated_commands
                
                # Применяем ограничение max_entries к загруженной истории
                if len(self.commands) > self.max_entries:
                    self.commands = self.commands[-self.max_entries:]
                    self.save_history()  # Сохраняем усеченную историю
                
                print(f"📚 Загружено {len(self.commands)} команд из истории")
                return self.commands
            except json.JSONDecodeError as e:
                print(f"⚠️  Ошибка парсинга JSON: {e}")
                self.commands = []
            except Exception as e:
                print(f"⚠️  Ошибка загрузки истории: {e}")
                self.commands = []
        else:
            print("📚 История команд пуста (файл не найден)")
            self.commands = []
        return self.commands
    
    def save_history(self):
        """Сохраняет историю команд в файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.commands, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  Ошибка сохранения истории: {e}")
    
    def add_command(self, command: str, status: str = "success", response_data: Dict = None):
        """
        Добавляет команду в историю
        
        Args:
            command: Команда, которая была выполнена
            status: Статус выполнения команды
            response_data: Дополнительные данные ответа
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'status': status
        }
        
        if response_data:
            entry['response'] = response_data
        
        self.commands.append(entry)
        
        # Ограничиваем размер истории - оставляем только последние max_entries
        if len(self.commands) > self.max_entries:
            self.commands = self.commands[-self.max_entries:]
        
        # Сохраняем после каждой команды
        self.save_history()
    
    def get_last_commands(self, count: int = 10) -> List[Dict]:
        """Возвращает последние N команд"""
        return self.commands[-count:] if self.commands else []
    
    def get_all_commands(self) -> List[Dict]:
        """Возвращает всю историю команд"""
        return self.commands
    
    def clear_history(self):
        """Очищает историю команд"""
        self.commands = []
        self.save_history()
        print("🗑️  История команд очищена")
    
    def print_history(self, last_n: int = 10):
        """Выводит последние N команд в консоль"""
        recent = self.get_last_commands(last_n)
        if recent:
            print(f"\n📜 Последние {len(recent)} команд:")
            print("-" * 60)
            for i, entry in enumerate(recent, 1):
                timestamp = entry['timestamp']
                command = entry['command']
                status = entry['status']
                print(f"{i}. [{timestamp}] {command} - {status}")
            print("-" * 60)
        else:
            print("📜 История команд пуста")
