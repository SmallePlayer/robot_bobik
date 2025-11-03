# robot_control_server.py
import cv2
import zmq
import base64
import numpy as np
import time
import socket
import RPi.GPIO as GPIO

class RobotController:
    def __init__(self, video_port=5555, control_port=5556):
        # Настройка пинов для моторов
        self.MOTOR_LEFT_PINS = [17, 18]   # IN1, IN2
        self.MOTOR_RIGHT_PINS = [22, 23]  # IN3, IN4
        
        # Настройка GPIO
        GPIO.setmode(GPIO.BCM)
        for pin in self.MOTOR_LEFT_PINS + self.MOTOR_RIGHT_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
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
        
        # Диагностика
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"IP робота: {local_ip}")
        print(f"Видео порт: {self.video_port}")
        print(f"Порт управления: {self.control_port}")
    
    def motor_control(self, left_forward, left_backward, right_forward, right_backward):
        """Управление моторами"""
        # Левый мотор
        GPIO.output(self.MOTOR_LEFT_PINS[0], left_forward)
        GPIO.output(self.MOTOR_LEFT_PINS[1], left_backward)
        
        # Правый мотор
        GPIO.output(self.MOTOR_RIGHT_PINS[0], right_forward)
        GPIO.output(self.MOTOR_RIGHT_PINS[1], right_backward)
    
    def stop_motors(self):
        """Остановка всех моторов"""
        self.motor_control(False, False, False, False)
    
    def move_forward(self):
        """Движение вперед"""
        self.motor_control(True, False, True, False)
    
    def move_backward(self):
        """Движение назад"""
        self.motor_control(False, True, False, True)
    
    def turn_left(self):
        """Поворот налево"""
        self.motor_control(False, True, True, False)
    
    def turn_right(self):
        """Поворот направо"""
        self.motor_control(True, False, False, True)
    
    def handle_control_command(self, command):
        """Обработка команд управления"""
        if command == b'w':
            self.move_forward()
            print("Движение: ВПЕРЕД")
        elif command == b's':
            self.move_backward()
            print("Движение: НАЗАД")
        elif command == b'a':
            self.turn_left()
            print("Движение: ЛЕВО")
        elif command == b'd':
            self.turn_right()
            print("Движение: ПРАВО")
        elif command == b' ':
            self.stop_motors()
            print("Движение: СТОП")
        else:
            print(f"Неизвестная команда: {command}")
    
    def start_video_stream(self):
        """Запуск потоковой передачи видео в отдельном потоке"""
        import threading
        
        def video_stream():
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Ошибка: Не удалось открыть камеру")
                return
            
            # Настройки камеры
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            
            print("Запуск видео потока...")
            
            try:
                while True:
                    ret, frame = self.cap.read()
                    if not ret:
                        continue
                    
                    # Кодирование кадра
                    ret, buffer = cv2.imencode('.jpg', frame, [
                        cv2.IMWRITE_JPEG_QUALITY, 60
                    ])
                    
                    if ret:
                        jpg_as_text = base64.b64encode(buffer)
                        self.video_socket.send(jpg_as_text)
                    
                    time.sleep(0.066)  # ~15 FPS
                    
            except Exception as e:
                print(f"Ошибка видео потока: {e}")
            finally:
                if self.cap:
                    self.cap.release()
        
        # Запуск видео потока в отдельном потоке
        video_thread = threading.Thread(target=video_stream, daemon=True)
        video_thread.start()
    
    def start_control_server(self):
        """Запуск сервера управления"""
        print("Сервер управления запущен...")
        
        try:
            while True:
                # Ожидание команды
                command = self.control_socket.recv()
                
                # Обработка команды
                self.handle_control_command(command)
                
                # Отправка подтверждения
                self.control_socket.send(b"OK")
                
        except KeyboardInterrupt:
            print("Остановка сервера...")
        except Exception as e:
            print(f"Ошибка сервера управления: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.stop_motors()
        if self.cap:
            self.cap.release()
        self.video_socket.close()
        self.control_socket.close()
        self.context.term()
        GPIO.cleanup()
        print("Ресурсы освобождены")

if __name__ == "__main__":
    robot = RobotController()
    robot.start_video_stream()
    robot.start_control_server()