import zmq
import keyboard
import json
import time

class RobotClient:
    def __init__(self, robot_ip = "192.168.1.100"):
        # Настройка ZMQ клиента
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)  # REQ (request) для запросов
        self.socket.connect(f"tcp://{robot_ip}:5555")
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # Таймаут 5 секунд
        
        self.is_connected = False
        self.current_speed = 0.7
        
    def connect(self):
        """Проверка соединения с роботом"""
        try:
            self.send_command("stop")  # Тестовая команда
            self.is_connected = True
            return True
        except Exception as e:
            print(f"❌ Не удалось подключиться к роботу: {e}")
            return False
    
    def send_command(self, command):
        """Отправка команды роботу"""
        self.socket.send_string(command)
        response = self.socket.recv_string()
        data = json.loads(response)
        
        if "speed" in data:
            self.current_speed = data["speed"]
        
        return data

def print_controls():
    """Выводит информацию об управлении"""
    print("\n🎮 УПРАВЛЕНИЕ РОБОТОМ")
    print("═" * 40)
    print("W - Движение вперед")
    print("S - Движение назад") 
    print("A - Поворот влево")
    print("D - Поворот вправо")
    print("Space - Стоп")
    print("Q/E - Уменьшить/Увеличить скорость")
    print("R - Переподключиться к роботу")
    print("ESC - Выход")
    print("═" * 40)

def main():
    # Получаем IP адрес робота
    robot_ip = input("Введите IP адрес Raspberry Pi (например: 192.168.1.100): ").strip()
    
    client = RobotClient(robot_ip)
    
    print("🔗 Подключаемся к роботу...")
    if not client.connect():
        print("❌ Не удалось подключиться к роботу. Проверьте:")
        print("   - IP адрес")
        print("   - Сеть Wi-Fi")
        print("   - Запущен ли сервер на роботе")
        return
    
    print("✅ Успешно подключено к роботу!")
    print_controls()
    
    # Словарь для отслеживания состояния клавиш
    key_states = {
        'w': False, 's': False, 'a': False, 'd': False,
        'space': False
    }
    
    last_command = "stop"
    
    def send_robot_command(command):
        """Отправляет команду и обрабатывает ошибки"""
        nonlocal last_command
        try:
            if command != last_command:
                response = client.send_command(command)
                last_command = command
                if response["status"] == "success":
                    print(f"✅ Команда выполнена: {command} (скорость: {client.current_speed})")
                else:
                    print(f"❌ Ошибка выполнения: {response}")
        except zmq.Again:
            print("⏰ Таймаут соединения с роботом")
            client.is_connected = False
        except Exception as e:
            print(f"❌ Ошибка связи: {e}")
            client.is_connected = False
    
    print("\n🚀 Управление активировано! Используйте WASD для движения...")
    
    try:
        while True:
            # Проверяем состояние подключения
            if not client.is_connected:
                reconnect = input("❌ Соединение потеряно. Переподключиться? (y/n): ")
                if reconnect.lower() == 'y':
                    if client.connect():
                        print("✅ Переподключение успешно!")
                    else:
                        print("❌ Не удалось переподключиться")
                        break
                else:
                    break
            
            # Обработка клавиш управления
            if keyboard.is_pressed('w') and not keyboard.is_pressed('s'):
                if keyboard.is_pressed('a'):
                    send_robot_command("left")
                elif keyboard.is_pressed('d'):
                    send_robot_command("right")
                else:
                    send_robot_command("forward")
            elif keyboard.is_pressed('s') and not keyboard.is_pressed('w'):
                if keyboard.is_pressed('a'):
                    send_robot_command("left")
                elif keyboard.is_pressed('d'):
                    send_robot_command("right")
                else:
                    send_robot_command("backward")
            elif keyboard.is_pressed('a'):
                send_robot_command("left")
            elif keyboard.is_pressed('d'):
                send_robot_command("right")
            elif keyboard.is_pressed('space'):
                send_robot_command("stop")
            else:
                if last_command != "stop":
                    send_robot_command("stop")
            
            # Обработка клавиш настроек
            if keyboard.is_pressed('q'):
                new_speed = max(0.1, client.current_speed - 0.1)
                send_robot_command(f"speed:{new_speed:.1f}")
                time.sleep(0.2)  # Задержка для избежания множественных нажатий
            elif keyboard.is_pressed('e'):
                new_speed = min(1.0, client.current_speed + 0.1)
                send_robot_command(f"speed:{new_speed:.1f}")
                time.sleep(0.2)
            elif keyboard.is_pressed('r'):
                print("🔁 Переподключение...")
                client.connect()
                time.sleep(0.5)
            
            # Выход по ESC
            if keyboard.is_pressed('esc'):
                print("\n🛑 Выход из программы...")
                break
            
            time.sleep(0.05)  # Небольшая задержка для снижения нагрузки
            
    except KeyboardInterrupt:
        print("\n🛑 Программа прервана пользователем")
    finally:
        # Гарантированно отправляем команду остановки
        try:
            client.send_command("stop")
        except:
            pass
        print("🔴 Управление остановлено")

if __name__ == "__main__":
    # Установите библиотеку keyboard: pip install keyboard
    main()