import zmq
import json
import time
import curses

class RobotClientCurses:
    def __init__(self, robot_ip):
        context = zmq.Context()
        self.socket = context.socket(zmq.REQ)
        self.socket.connect(f"tcp://{robot_ip}:5555")
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)
        self.current_speed = 0.7
        self.is_connected = False

    def connect(self):
        try:
            self.send_command("stop")
            self.is_connected = True
            return True
        except Exception as e:
            print(f"❌ Не удалось подключиться к роботу: {e}")
            return False

    def send_command(self, command):
        self.socket.send_string(command)
        response = self.socket.recv_string()
        data = json.loads(response)
        if "speed" in data:
            self.current_speed = data["speed"]
        return data

def main_curses(stdscr, client):
    # Настройка curses
    stdscr.nodelay(True)  # Неблокирующий ввод
    stdscr.clear()
    
    print("🎮 Управление роботом активировано (Curses). Используйте WASD. Нажмите 'q' для выхода.")
    
    last_command = "stop"
    
    try:
        while True:
            # Пытаемся получить код нажатой клавиши
            key = stdscr.getch()
            
            command = None
            
            # Обработка нажатий клавиш
            if key != -1:  # -1 означает, что клавиша не нажата
                if key == ord('w'):
                    command = "forward"
                elif key == ord('s'):
                    command = "backward"
                elif key == ord('a'):
                    command = "left"
                elif key == ord('d'):
                    command = "right"
                elif key == ord(' '):
                    command = "stop"
                elif key == ord('q'):
                    command = "stop"
                    client.send_command(command)
                    break
                elif key == ord('e'):
                    new_speed = min(1.0, client.current_speed + 0.1)
                    command = f"speed:{new_speed:.1f}"
                elif key == ord('q'):
                    new_speed = max(0.1, client.current_speed - 0.1)
                    command = f"speed:{new_speed:.1f}"
            
            # Отправка команды, если она изменилась
            if command and command != last_command:
                try:
                    client.send_command(command)
                    last_command = command
                except Exception as e:
                    print(f"❌ Ошибка связи: {e}")
                    break
            
            # Небольшая задержка для снижения нагрузки на ЦП
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pass
    finally:
        # Гарантированная остановка робота при выходе
        try:
            client.send_command("stop")
        except:
            pass

if __name__ == "__main__":
    #robot_ip = input("Введите IP адрес Raspberry Pi: ").strip()
    client = RobotClientCurses("192.168.1.139")
    
    if client.connect():
        curses.wrapper(main_curses, client)
    print("🔴 Управление остановлено")