import zmq
from gpiozero import Robot
import json
from command_history import CommandHistory

class RobotController:
    def __init__(self):
        # Инициализация робота с указанием пинов
        self.robot = Robot(left=(12, 13), right=(19, 18))
        self.current_speed = 0.7  # Базовая скорость (0.0 до 1.0)
        
        # Инициализация истории команд
        self.history = CommandHistory('robot_command_history.json')
        self.history.load_history()
        self.history.print_history(10)
        
    def execute_command(self, command):
        """Выполняет команду движения"""
        try:
            if command == "forward":
                self.robot.forward(self.current_speed)
                print("🔼 ДВИЖЕНИЕ ВПЕРЕД")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "backward":
                self.robot.backward(self.current_speed)
                print("🔽 ДВИЖЕНИЕ НАЗАД")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "left":
                self.robot.left(self.current_speed)
                print("↩️  ПОВОРОТ ВЛЕВО")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "right":
                self.robot.right(self.current_speed)
                print("↪️  ПОВОРОТ ВПРАВО")
                self.history.add_command(command, "success", {"speed": self.current_speed})
            elif command == "stop":
                self.robot.stop()
                print("⏹️  СТОП")
                self.history.add_command(command, "success")
            elif command.startswith("speed:"):
                # Изменение скорости: "speed:0.8"
                new_speed = float(command.split(":")[1])
                if 0.1 <= new_speed <= 1.0:
                    self.current_speed = new_speed
                    print(f"🎚️  Скорость изменена: {new_speed}")
                    self.history.add_command(command, "success", {"new_speed": new_speed})
            else:
                print(f"❌ Неизвестная команда: {command}")
                self.history.add_command(command, "error", {"reason": "unknown_command"})
                
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
            self.history.add_command(command, "error", {"error": str(e)})

def main():
    # Настройка ZMQ
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP (reply) для ответов
    socket.bind("tcp://*:5555")       # Слушаем на всех интерфейсах порт 5555
    
    robot = RobotController()
    
    print("🤖 СЕРВЕР УПРАВЛЕНИЯ РОБОТОМ ЗАПУЩЕН")
    print("📍 Адрес для подключения: tcp://[IP_РОБОТА]:5555")
    print("📝 Ожидание команд...")
    print("Доступные команды: forward, backward, left, right, stop, speed:X.X")
    
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
        robot.robot.stop()
        socket.close()
        context.term()
        print("🔴 Сервер остановлен, моторы выключены")

if __name__ == "__main__":
    main()