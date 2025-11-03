# client_viewer.py
import cv2
import zmq
import base64
import numpy as np

class VideoReceiver:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.CONFLATE, 1)  # Берем только последний кадр
        self.socket.connect(f"tcp://{host}:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        
    def start_receiver(self):
        """Запускает получение и отображение видео"""
        print(f"Подключение к {self.host}:{self.port}...")
        
        try:
            while True:
                # Получение кадра
                jpg_as_text = self.socket.recv()
                
                # Декодирование из base64
                jpg_original = base64.b64decode(jpg_as_text)
                
                # Преобразование в numpy array
                jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
                
                # Декодирование JPEG
                frame = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Отображение кадра
                    cv2.imshow('Video Stream', frame)
                
                # Выход по нажатию 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("Остановка приемника...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.socket.close()
        self.context.term()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Замените 'localhost' на IP-адрес робота
    # Например: '192.168.1.100'
    receiver = VideoReceiver(host='localhost', port=5555)
    receiver.start_receiver()