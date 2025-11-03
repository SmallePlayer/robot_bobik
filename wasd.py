# laptop_control_gpiozero.py
import cv2
import zmq
import base64
import numpy as np
import keyboard
import time

class RobotRemoteControl:
    def __init__(self, robot_ip='192.168.1.100', video_port=5555, control_port=5556):
        self.robot_ip = robot_ip
        self.video_port = video_port
        self.control_port = control_port
        
        # ZMQ контекст
        self.context = zmq.Context()
        
        # Сокет для видео (SUB)
        self.video_socket = self.context.socket(zmq.SUB)
        self.video_socket.connect(f"tcp://{robot_ip}:{video_port}")
        self.video_socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.video_socket.setsockopt(zmq.RCVTIMEO, 100)
        
        # Сокет для управления (REQ)
        self.control_socket = self.context.socket(zmq.REQ)
        self.control_socket.connect(f"tcp://{robot_ip}:{control_port}")
        self.control_socket.setsockopt(zmq.RCVTIMEO, 1000)
        
        # Состояние клавиш
        self.last_command = None
        self.command_cooldown = 0.1  # Задержка между командами
        self.last_send_time = 0
        
        print(f"Подключение к роботу {robot_ip}...")
        print("Управление:")
        print("  WASD - движение")
        print("  SPACE - стоп")
        print("  L - светодиод вкл/выкл")
        print("  +/- - изменить скорость")
        print("  Q - выход")
    
    def send_command(self, command):
        """Отправка команды управления с ограничением частоты"""
        current_time = time.time()
        if current_time - self.last_send_time < self.command_cooldown:
            return True
        
        try:
            self.control_socket.send_string(command)
            response = self.control_socket.recv_string()
            self.last_send_time = current_time
            return response == "OK"
        except zmq.Again:
            print("Таймаут отправки команды")
            return False
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")
            return False
    
    def start_control(self):
        """Запуск управления и видео"""
        print("Запуск управления...")
        
        led_state = False
        last_video_time = time.time()
        video_timeout = 3.0  # Таймаут видео в секундах
        
        try:
            while True:
                current_time = time.time()
                
                # Обработка управления
                if keyboard.is_pressed('w') and keyboard.is_pressed('a'):
                    self.send_command('wa')
                elif keyboard.is_pressed('w') and keyboard.is_pressed('d'):
                    self.send_command('wd')
                elif keyboard.is_pressed('w'):
                    self.send_command('w')
                elif keyboard.is_pressed('s'):
                    self.send_command('s')
                elif keyboard.is_pressed('a'):
                    self.send_command('a')
                elif keyboard.is_pressed('d'):
                    self.send_command('d')
                elif keyboard.is_pressed(' '):
                    self.send_command(' ')
                
                # Дополнительные функции
                if keyboard.is_pressed('+') or keyboard.is_pressed('='):
                    self.send_command('speed:0.8')
                    time.sleep(0.5)  # Задержка чтобы не спамить
                elif keyboard.is_pressed('-'):
                    self.send_command('speed:0.3')
                    time.sleep(0.5)
                
                if keyboard.is_pressed('l'):
                    if not led_state:
                        self.send_command('led_on')
                        led_state = True
                    else:
                        self.send_command('led_off')
                        led_state = False
                    time.sleep(0.5)
                
                # Получение и отображение видео
                try:
                    jpg_as_text = self.video_socket.recv()
                    jpg_original = base64.b64decode(jpg_as_text)
                    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
                    frame = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        cv2.imshow('Robot Camera - Press Q to quit', frame)
                        last_video_time = current_time
                
                except zmq.Again:
                    # Проверка таймаута видео
                    if current_time - last_video_time > video_timeout:
                        print("Таймаут видео потока")
                        break
                
                # Выход по Q
                if keyboard.is_pressed('q') or (cv2.waitKey(1) & 0xFF == ord('q')):
                    break
                
                time.sleep(0.01)  # Небольшая задержка для снижения нагрузки
                    
        except KeyboardInterrupt:
            print("Остановка управления...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        print("Остановка робота...")
        self.send_command(' ')
        self.video_socket.close()
        self.control_socket.close()
        self.context.term()
        cv2.destroyAllWindows()
        print("Управление остановлено")

if __name__ == "__main__":
    # ЗАМЕНИТЕ '192.168.1.100' на реальный IP вашего робота!
    controller = RobotRemoteControl(robot_ip='192.168.1.100')
    controller.start_control()