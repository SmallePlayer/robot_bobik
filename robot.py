# server_camera_headless.py
import cv2
import zmq
import base64
import numpy as np
import time

class CameraStreamer:
    def __init__(self, port=5555, camera_index=0):
        self.port = port
        self.camera_index = camera_index
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{self.port}")
        self.cap = None
        
    def start_stream(self):
        """Запускает потоковую передачу с камеры"""
        # Для Raspberry Pi можно использовать специальные настройки
        self.cap = cv2.VideoCapture(self.camera_index)
        
        # Настройки для лучшей производительности на Raspberry Pi
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)  # Уменьшить FPS для Raspberry Pi
        
        if not self.cap.isOpened():
            print("Ошибка: Не удалось открыть камеру")
            # Попробуем другие индексы камеры
            for i in range(1, 5):
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    print(f"Камера найдена на индексе {i}")
                    break
            else:
                print("Не удалось найти доступную камеру")
                return
        
        print(f"Стриминг видео на порту {self.port}...")
        
        try:
            while True:
                # Чтение кадра с камеры
                ret, frame = self.cap.read()
                if not ret:
                    print("Ошибка: Не удалось получить кадр")
                    time.sleep(0.1)
                    continue
                
                # Изменение размера для уменьшения нагрузки
                frame = cv2.resize(frame, (320, 240))  # Еще меньше для Raspberry Pi
                
                # Кодирование кадра в JPEG с более низким качеством
                ret, buffer = cv2.imencode('.jpg', frame, [
                    cv2.IMWRITE_JPEG_QUALITY, 50  # Низкое качество для скорости
                ])
                
                if ret:
                    # Кодирование в base64 и отправка
                    jpg_as_text = base64.b64encode(buffer)
                    self.socket.send(jpg_as_text)
                
                # Контроль FPS
                time.sleep(0.066)  # ~15 FPS
                
        except KeyboardInterrupt:
            print("Остановка стриминга...")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.cap:
            self.cap.release()
        self.socket.close()
        self.context.term()

if __name__ == "__main__":
    streamer = CameraStreamer(port=5555, camera_index=0)
    streamer.start_stream()