#!/usr/bin/env python3
"""
Сервер управления роботом через sysfs (самый базовый способ)
Не требует специальных библиотек, работает напрямую с файловой системой
"""

import zmq
import json
import time
import os
from command_history import CommandHistory

class SysfsRobotController:
    def __init__(self):
        print("🤖 Инициализация робота через sysfs...")
        
        # GPIO пины (номера BCM)
        self.pins = {
            'left_forward': 12,
            'left_backward': 13,
            'right_forward': 19,
            'right_backward': 18
        }
        
        # Экспортируем пины
        for name, pin in self.pins.items():
            try:
                # Экспортируем пин
                with open('/sys/class/gpio/export', 'w') as f:
                    f.write(str(pin))
                
                # Ждем создания директории
                time.sleep(0.1)
                
                # Настраиваем направление (выход)
                direction_path = f'/sys/class/gpio/gpio{pin}/direction'
                with open(direction_path, 'w') as f:
                    f.write('out')
                
                # Устанавливаем низкий уровень
                value_path = f'/sys/class/gpio/gpio{pin}/value'
                with open(value_path, 'w') as f:
                    f.write('0')
                    
                print(f"✅ Пин GPIO{pin} настроен")
                
            except Exception as e:
                print(f"⚠️  Ошибка настройки пина {pin}: {e}")
                # Если пин уже экспортирован, продолжаем
        
        self.current_speed = 0.7
        
        # Инициализация истории команд
        self.history = CommandHistory('robot_command_history.json')
        self.history.load_history()
        self.history.print_history(10)
    
    def _set_pin(self, pin_number, value):
        """Установка значения пина (0 или 1)"""
        try:
            value_path = f'/sys/class/gpio/gpio{pin_number}/value'
            with open(value_path, 'w') as f:
                f.write('1' if value else '0')
        except Exception as e:
            print(f"❌ Ошибка установки пина {pin_number}: {e}")
    
    def _control_motors(self, lf, lb, rf, rb):
        """Управление моторами"""
        self._set_pin(self.pins['left_forward'], lf)
        self._set_pin(self.pins['left_backward'], lb)
        self._set_pin(self.pins['right_forward'], rf)
        self._set_pin(self.pins['right_backward'], rb)
    
    def forward(self):
        self._control_motors(1, 0, 1, 0)
    
    def backward(self):
        self._control_motors(0, 1, 0, 1)
    
    def left(self):
        self._control_motors(0, 1, 1, 0)
    
    def right(self):
        self._control_motors(1, 0, 0, 1)
    
    def stop(self):
        self._control_motors(0, 0, 0, 0)
    
    def execute_command(self, command):
        """Выполняет команду движения"""
        try:
            if command == "forward":
                self.forward()
                print("🔼 ВПЕРЕД")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "backward":
                self.backward()
                print("🔽 НАЗАД")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "left":
                self.left()
                print("↩️  ВЛЕВО")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "right":
                self.right()
                print("↪️  ВПРАВО")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "stop":
                self.stop()
                print("⏹️  СТОП")
                self.history.add_command(command, "success")
            elif command.startswith("speed:"):
                new_speed = float(command.split(":")[1])
                if 0.1 <= new_speed <= 1.0:
                    self.current_speed = new_speed
                    print(f"🎚️  Скорость: {new_speed}")
                    self.history.add_command(command, "success", {"new_speed": new_speed})
                else:
                    print(f"❌ Некорректная скорость: {new_speed}")
                    self.history.add_command(command, "error", {"reason": "invalid_speed"})
            else:
                print(f"❌ Неизвестная команда: {command}")
                self.history.add_command(command, "error", {"reason": "unknown_command"})
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.history.add_command(command, "error", {"error": str(e)})
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop()
        time.sleep(0.1)
        
        # Неэкспортируем пины (оставляем как есть)
        # чтобы не мешать другим приложениям
        print("🧹 Робот остановлен")

# Остальной код (main функция) остается таким же как в предыдущих примерах


def main():
    print("=" * 50)
    print("🤖 СЕРВЕР УПРАВЛЕНИЯ РОБОТОМ С GPIOd")
    print("=" * 50)
    
    # Проверяем наличие библиотеки gpiod
    try:
        import gpiod
        print("✅ Библиотека gpiod доступна")
    except ImportError:
        print("❌ Библиотека gpiod не установлена")
        print("Установите её командой: sudo apt install python3-libgpiod")
        return
    
    # Настройка ZMQ
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    
    # Инициализация робота
    try:
        robot = RobotController()
        print("✅ Робот инициализирован успешно")
        print("📍 Адрес для подключения: tcp://[IP_РОБОТА]:5555")
        print("📝 Ожидание команд...")
        print("Доступные команды: forward, backward, left, right, stop, speed:X.X")
        print("=" * 50)
    except Exception as e:
        print(f"❌ ОШИБКА ИНИЦИАЛИЗАЦИИ: {e}")
        return
    
    try:
        while True:
            # Ожидаем команду от клиента
            message = socket.recv_string()
            print(f"📨 Получена команда: {message}")
            
            # Выполняем команду
            robot.execute_command(message)
            
            # Отправляем подтверждение
            response = {
                "status": "success",
                "command": message,
                "speed": robot.current_speed
            }
            socket.send_string(json.dumps(response))
            
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")
    finally:
        print("🧹 Очистка ресурсов...")
        robot.cleanup()
        socket.close()
        context.term()
        print("🔴 Сервер остановлен")

if __name__ == "__main__":
    main()