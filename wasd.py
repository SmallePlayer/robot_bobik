# laptop_control_client.py
import cv2
import zmq
import base64
import numpy as np
import keyboard  # Установите: pip install keyboard

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
        
        # Сокет для управления (REQ)
        self.control_socket = self.context.socket(zmq.REQ)
        self.control_socket.connect(f"tcp://{robot_ip}:{control_port}")
        
        print(f"Подключение к роботу {robot_ip}...")
        print("Управление: WASD - движение, SPACE - стоп, Q - выход")
    
    def send_command(self, command):
        """Отправка команды управления"""
        try:
            self.control_socket.send(command)
            response = self.control_socket.recv()
            return response == b"OK"
        except Exception as e:
            print(f"Ошибка отправки команды: {e}")
            return False
    
    def start_control(self):
        """Запуск управления и видео"""
        print("Запуск управления...")
        
        try:
            while True:
                # Обработка управления
                if keyboard.is_pressed('w'):
                    self.send_command(b'w')
                elif keyboard.is_pressed('s'):
                    self.send_command(b's')
                elif keyboard.is_pressed('a'):
                    self.send_command(b'a')
                elif keyboard.is_pressed('d'):
                    self.send_command(b'd')
                elif keyboard.is_pressed(' '):
                    self.send_command(b' ')
                elif keyboard.is_pressed('q'):
                    break
                
                # Получение и отображение видео
                try:
                    jpg_as_text = self.video_socket.recv(zmq.NOBLOCK)
                    jpg_original = base64.b64decode(jpg_as_text)
                    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
                    frame = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        cv2.imshow('Robot Camera', frame)
                
                except zmq.Again:
                    # Нет нового кадра, продолжаем
                    pass
                
                # Выход по Q или закрытию окна
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("Остановка управления...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.send_command(b' ')  # Остановка робота
        self.video_socket.close()
        self.control_socket.close()
        self.context.term()
        cv2.destroyAllWindows()
        print("Управление остановлено")

if __name__ == "__main__":
    # ЗАМЕНИТЕ '192.168.1.100' на реальный IP вашего робота!
    controller = RobotRemoteControl(robot_ip='192.168.1.100')
    controller.start_control()