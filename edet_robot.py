# robot_control_gpiozero.py
import cv2
import zmq
import base64
import numpy as np
import time
import socket
from gpiozero import Robot, DigitalOutputDevice
import threading

class RobotController:
    def __init__(self, video_port=5555, control_port=5556):
        # Настройка робота с gpiozero
        # Формат: Robot(left=(forward_pin, backward_pin), right=(forward_pin, backward_pin))
        self.robot = Robot(left=(17, 18), right=(22, 23))
        
        # Дополнительные устройства (например, для света или сервоприводов)
        self.led = DigitalOutputDevice(24)  # Пример для светодиода
        
        # Порты для видео и управления
        self.video_port = video_port
        self.control_port = control_port
        
        # ZMQ контекст
        self.context = zmq.Context()
        
        # Сокет для видео (PUB)
        self.video_socket = self.context.socket(zmq.PUB)
        self.video_socket.bind(f"tcp://*:{self.video_port}")
        
        # Сокет для управления (REP)
        self.control_socket = self.context.socket(zmq.REP)
        self.control_socket.bind(f"tcp://*:{self.control_port}")
        
        # Камера
        self.cap = None
        
        # Скорость движения (0.0 - 1.0)
        self.speed = 0.6
        
        # Диагностика
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"IP робота: {local_ip}")
        print(f"Видео порт: {self.video_port}")
        print(f"Порт управления: {self.control_port}")
        print(f"Скорость движения: {self.speed}")
    
    def stop_motors(self):
        """Остановка всех моторов"""
        self.robot.stop()
        self.led.off()
    
    def move_forward(self):
        """Движение вперед"""
        self.robot.forward(self.speed)
        self.led.on()
    
    def move_backward(self):
        """Движение назад"""
        self.robot.backward(self.speed)
        self.led.on()
    
    def turn_left(self):
        """Поворот налево"""
        self.robot.left(self.speed)
        self.led.on()
    
    def turn_right(self):
        """Поворот направо"""
        self.robot.right(self.speed)
        self.led.on()
    
    def move_forward_left(self):
        """Движение вперед-влево"""
        self.robot.forward(self.speed, curve_left=0.5)
        self.led.on()
    
    def move_forward_right(self):
        """Движение вперед-вправо"""
        self.robot.forward(self.speed, curve_right=0.5)
        self.led.on()
    
    def handle_control_command(self, command):
        """Обработка команд управления"""
        command = command.decode('utf-8').strip()
        
        if command == 'w':
            self.move_forward()
            print("Движение: ВПЕРЕД")
        elif command == 's':
            self.move_backward()
            print("Движение: НАЗАД")
        elif command == 'a':
            self.turn_left()
            print("Движение: ЛЕВО")
        elif command == 'd':
            self.turn_right()
            print("Движение: ПРАВО")
        elif command == 'wa':
            self.move_forward_left()
            print("Движение: ВПЕРЕД-ЛЕВО")
        elif command == 'wd':
            self.move_forward_right()
            print("Движение: ВПЕРЕД-ПРАВО")
        elif command == ' ':
            self.stop_motors()
            print("Движение: СТОП")
        elif command.startswith('speed:'):
            try:
                new_speed = float(command.split(':')[1])
                if 0.1 <= new_speed <= 1.0:
                    self.speed = new_speed
                    print(f"Скорость изменена: {self.speed}")
                else:
                    print("Скорость должна быть от 0.1 до 1.0")
            except ValueError:
                print("Неверный формат скорости")
        elif command == 'led_on':
            self.led.on()
            print("Светодиод: ВКЛ")
        elif command == 'led_off':
            self.led.off()
            print("Светодиод: ВЫКЛ")
        else:
            print(f"Неизвестная команда: {command}")
    
    def start_video_stream(self):
        """Запуск потоковой передачи видео в отдельном потоке"""
        def video_stream():
            self.cap = cv2.VideoCapture(0)
            
            # Пробуем разные индексы камер если 0 не работает
            if not self.cap.isOpened():
                for i in range(1, 4):
                    self.cap = cv2.VideoCapture(i)
                    if self.cap.isOpened():
                        print(f"Камера найдена на индексе {i}")
                        break
                else:
                    print("Ошибка: Не удалось открыть камеру")
                    return
            
            # Настройки камеры
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            
            print("Запуск видео потока...")
            frame_count = 0
            
            try:
                while True:
                    ret, frame = self.cap.read()
                    if not ret:
                        print("Ошибка чтения кадра")
                        time.sleep(0.1)
                        continue
                    
                    # Кодирование кадра
                    ret, buffer = cv2.imencode('.jpg', frame, [
                        cv2.IMWRITE_JPEG_QUALITY, 60
                    ])
                    
                    if ret:
                        jpg_as_text = base64.b64encode(buffer)
                        self.video_socket.send(jpg_as_text)
                        frame_count += 1
                        
                        if frame_count % 30 == 0:
                            print(f"Отправлено кадров: {frame_count}")
                    
                    time.sleep(0.066)  # ~15 FPS
                    
            except Exception as e:
                print(f"Ошибка видео потока: {e}")
            finally:
                if self.cap:
                    self.cap.release()
                print("Видео поток остановлен")
        
        # Запуск видео потока в отдельном потоке
        video_thread = threading.Thread(target=video_stream, daemon=True)
        video_thread.start()
    
    def start_control_server(self):
        """Запуск сервера управления"""
        print("Сервер управления запущен...")
        print("Ожидание команд...")
        
        try:
            while True:
                # Ожидание команды с таймаутом
                try:
                    command = self.control_socket.recv_string()
                    
                    # Обработка команды
                    self.handle_control_command(command.encode())
                    
                    # Отправка подтверждения
                    self.control_socket.send_string("OK")
                    
                except zmq.Again:
                    # Таймаут, продолжаем цикл
                    continue
                except Exception as e:
                    print(f"Ошибка обработки команды: {e}")
                    self.control_socket.send_string("ERROR")
                
        except KeyboardInterrupt:
            print("\nОстановка сервера...")
        except Exception as e:
            print(f"Ошибка сервера управления: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        print("Очистка ресурсов...")
        self.stop_motors()
        if self.cap:
            self.cap.release()
        self.video_socket.close()
        self.control_socket.close()
        self.context.term()
        print("Ресурсы освобождены")

if __name__ == "__main__":
    robot = RobotController()
    robot.start_video_stream()
    robot.start_control_server()