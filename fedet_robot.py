#!/usr/bin/env python3
"""
Сервер управления роботом с использованием gpiod
Работает на Raspberry Pi OS Bookworm и новее
"""

import zmq
import json
import time
import gpiod
from gpiod.line import Direction
from command_history import CommandHistory

class GPIODRobotController:
    def __init__(self):
        print("🤖 Инициализация робота через gpiod...")
        
        # GPIO пины (номера BCM)
        self.pins = {
            'left_forward': 12,
            'left_backward': 13,
            'right_forward': 19,
            'right_backward': 18
        }
        
        # Открываем GPIO чип
        try:
            self.chip = gpiod.Chip('gpiochip0')
            print(f"✅ Открыт GPIO чип: {self.chip.name()}")
        except Exception as e:
            print(f"❌ Не могу открыть gpiochip0: {e}")
            print("\nВозможные решения:")
            print("1. Проверьте права: запустите с sudo")
            print("2. Проверьте устройство: ls /dev/gpiochip*")
            print("3. Установите gpiod: sudo apt install python3-libgpiod")
            raise
        
        # Настраиваем линии GPIO
        self.lines = {}
        for name, pin in self.pins.items():
            try:
                line = self.chip.get_line(pin)
                config = gpiod.line_request()
                config.consumer = "robot_bobik"
                config.request_type = gpiod.line_request.DIRECTION_OUTPUT
                
                line.request(config)
                line.set_value(0)  # Выключаем
                
                self.lines[name] = line
                print(f"✅ Пин GPIO{pin} настроен как выход")
            except Exception as e:
                print(f"❌ Ошибка настройки пина {pin}: {e}")
        
        self.current_speed = 0.7
        
        # Инициализация истории команд
        self.history = CommandHistory('robot_command_history.json')
        self.history.load_history()
        self.history.print_history(10)
    
    def _set_motors(self, lf, lb, rf, rb):
        """Установка состояний моторов"""
        try:
            self.lines['left_forward'].set_value(lf)
            self.lines['left_backward'].set_value(lb)
            self.lines['right_forward'].set_value(rf)
            self.lines['right_backward'].set_value(rb)
        except Exception as e:
            print(f"❌ Ошибка управления моторами: {e}")
    
    def forward(self):
        self._set_motors(1, 0, 1, 0)
    
    def backward(self):
        self._set_motors(0, 1, 0, 1)
    
    def left(self):
        self._set_motors(0, 1, 1, 0)
    
    def right(self):
        self._set_motors(1, 0, 0, 1)
    
    def stop(self):
        self._set_motors(0, 0, 0, 0)
    
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
        for line in self.lines.values():
            line.release()
        self.chip.close()
        print("🧹 Ресурсы GPIO освобождены")

# Остальная часть кода остается такой же