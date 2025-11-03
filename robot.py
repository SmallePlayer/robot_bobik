# server_camera.py
import cv2
import zmq
import base64
import numpy as np

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
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Ошибка: Не удалось открыть камеру")
            return
        
        print(f"Стриминг видео на порту {self.port}...")
        
        try:
            while True:
                # Чтение кадра с камеры
                ret, frame = self.cap.read()
                if not ret:
                    print("Ошибка: Не удалось получить кадр")
                    break
                
                # Изменение размера для уменьшения нагрузки на сеть
                frame = cv2.resize(frame, (640, 480))
                
                # Кодирование кадра в JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                
                if ret:
                    # Кодирование в base64 и отправка
                    jpg_as_text = base64.b64encode(buffer)
                    self.socket.send(jpg_as_text)
                
                # Небольшая задержка для контроля FPS
                cv2.waitKey(1)
                
        except KeyboardInterrupt:
            print("Остановка стриминга...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        if self.cap:
            self.cap.release()
        self.socket.close()
        self.context.term()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Для робота используйте camera_index=0
    # Если несколько камер, можно указать другой индекс
    streamer = CameraStreamer(port=5555, camera_index=0)
    streamer.start_stream()