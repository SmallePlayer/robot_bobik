import cv2
import zmq
import base64
import numpy as np
import time
import socket

class CameraStreamer:
    def __init__(self, port=5555, camera_index=0):
        self.port = port
        self.camera_index = camera_index
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        
        # Получаем IP адрес для диагностики
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"IP адрес робота: {local_ip}")
        print(f"Порт: {self.port}")
        
        # Привязываемся ко всем интерфейсам
        self.socket.bind(f"tcp://0.0.0.0:{self.port}")
        self.cap = None
        self.frame_count = 0
        
    def start_stream(self):
        """Запускает потоковую передачу с камеры"""
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Пробуем разные индексы камер если 0 не работает
        if not self.cap.isOpened():
            print("Пробуем другие индексы камеры...")
            for i in range(1, 4):
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    print(f"Камера найдена на индексе {i}")
                    break
            else:
                print("Ошибка: Не удалось открыть камеру")
                return
        
        # Настройки камеры
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        
        print("Камера инициализирована успешно")
        print("Ожидание подключения клиента...")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("Ошибка чтения кадра")
                    time.sleep(0.1)
                    continue
                
                # Ресайз для производительности
                frame = cv2.resize(frame, (320, 240))
                
                # Кодирование в JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [
                    cv2.IMWRITE_JPEG_QUALITY, 70
                ])
                
                if ret:
                    jpg_as_text = base64.b64encode(buffer)
                    
                    try:
                        self.socket.send(jpg_as_text)
                        self.frame_count += 1
                        if self.frame_count % 30 == 0:  # Каждые 30 кадров
                            print(f"Отправлено кадров: {self.frame_count}")
                    except zmq.ZMQError as e:
                        print(f"Ошибка отправки: {e}")
                
                time.sleep(0.066)  # ~15 FPS
                
        except KeyboardInterrupt:
            print(f"\nВсего отправлено кадров: {self.frame_count}")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.cap:
            self.cap.release()
        self.socket.close()
        self.context.term()
        print("Ресурсы освобождены")

if __name__ == "__main__":
    streamer = CameraStreamer(port=5555, camera_index=0)
    streamer.start_stream()