#!/usr/bin/env python3
"""
Сервер управления роботом на Raspberry Pi с использованием gpiod
Библиотека gpiod работает на новых версиях Raspberry Pi OS (Bookworm и выше)
"""

import zmq
import json
import time
import gpiod
from gpiod.line import Direction, Value

class RobotController:
    def __init__(self):
        print("🤖 Инициализация робота с использованием gpiod...")
        
        # Настройка пинов (GPIO номера)
        self.LEFT_FORWARD = 12   # GPIO12
        self.LEFT_BACKWARD = 13  # GPIO13
        self.RIGHT_FORWARD = 19  # GPIO19
        self.RIGHT_BACKWARD = 18 # GPIO18
        
        # Создаем словарь для хранения линий GPIO
        self.lines = {}
        
        try:
            # Получаем доступ к GPIO чипу (обычно gpiochip0)
            self.chip = gpiod.Chip('gpiochip0')
            print("✅ GPIO чип открыт успешно")
            
            # Настраиваем пины как выходы
            pins_to_request = [
                self.LEFT_FORWARD,
                self.LEFT_BACKWARD,
                self.RIGHT_FORWARD,
                self.RIGHT_BACKWARD
            ]
            
            # Запрашиваем линии GPIO
            request = gpiod.line_request()
            request.consumer = "robot_bobik"
            request.request_type = gpiod.line_request.DIRECTION_OUTPUT
            
            self.lines = self.chip.get_lines(pins_to_request)
            self.lines.request(request, default_vals=[0, 0, 0, 0])
            
            print(f"✅ Пины настроены: {pins_to_request}")
            self.current_speed = 0.7
            
        except Exception as e:
            print(f"❌ Ошибка инициализации GPIO: {e}")
            print("Возможные причины:")
            print("1. Не установлена библиотека gpiod: sudo apt install python3-libgpiod")
            print("2. Недостаточно прав: запустите с sudo")
            print("3. Неправильный чип: проверьте 'gpiodetect'")
            raise
    
    def _set_motors(self, left_fwd, left_bck, right_fwd, right_bck):
        """Установка состояний моторов"""
        try:
            # Устанавливаем значения для всех линий одновременно
            values = [left_fwd, left_bck, right_fwd, right_bck]
            self.lines.set_values(values)
        except Exception as e:
            print(f"❌ Ошибка установки значений GPIO: {e}")
    
    def forward(self):
        """Движение вперед"""
        self._set_motors(1, 0, 1, 0)
    
    def backward(self):
        """Движение назад"""
        self._set_motors(0, 1, 0, 1)
    
    def left(self):
        """Поворот налево (правый вперед, левый назад)"""
        self._set_motors(0, 1, 1, 0)
    
    def right(self):
        """Поворот направо (левый вперед, правый назад)"""
        self._set_motors(1, 0, 0, 1)
    
    def stop(self):
        """Полная остановка"""
        self._set_motors(0, 0, 0, 0)
    
    def execute_command(self, command):
        """Выполняет команду движения"""
        try:
            if command == "forward":
                self.forward()
                print("🔼 ДВИЖЕНИЕ ВПЕРЕД")
            elif command == "backward":
                self.backward()
                print("🔽 ДВИЖЕНИЕ НАЗАД")
            elif command == "left":
                self.left()
                print("↩️  ПОВОРОТ ВЛЕВО")
            elif command == "right":
                self.right()
                print("↪️  ПОВОРОТ ВПРАВО")
            elif command == "stop":
                self.stop()
                print("⏹️  СТОП")
            elif command.startswith("speed:"):
                new_speed = float(command.split(":")[1])
                if 0.1 <= new_speed <= 1.0:
                    self.current_speed = new_speed
                    print(f"🎚️  Скорость изменена: {new_speed}")
                else:
                    print(f"❌ Некорректная скорость: {new_speed}")
            else:
                print(f"❌ Неизвестная команда: {command}")
                
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop()
        time.sleep(0.1)
        if hasattr(self, 'lines') and self.lines:
            self.lines.release()
        if hasattr(self, 'chip') and self.chip:
            self.chip.close()
        print("🧹 GPIO ресурсы освобождены")

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