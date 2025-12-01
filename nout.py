import cv2
import zmq
import base64
import numpy as np
import time

class VideoReceiver:
    def __init__(self, host='192.168.1.138', port=5555):  # ЗАМЕНИТЕ НА IP РОБОТА!
        self.host = host
        self.port = port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt(zmq.CONFLATE, 1)
        
        # Таймаут на прием
        self.socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 секунд
        
        print(f"Подключение к {self.host}:{self.port}...")
        self.socket.connect(f"tcp://{self.host}:{self.port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        
        self.frame_count = 0
        
    def start_receiver(self):
        print("Ожидание видео потока...")
        
        try:
            while True:
                try:
                    # Получение данных с таймаутом
                    jpg_as_text = self.socket.recv()
                    
                    # Декодирование
                    jpg_original = base64.b64decode(jpg_as_text)
                    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
                    frame = cv2.imdecode(jpg_as_np, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        self.frame_count += 1
                        cv2.imshow('Video Stream', frame)
                        
                        if self.frame_count % 30 == 0:
                            print(f"Получено кадров: {self.frame_count}")
                    
                    # Выход по 'q'
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                        
                except zmq.Again:
                    print("Таймаут: нет данных от сервера")
                    break
                except Exception as e:
                    print(f"Ошибка обработки кадра: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print("Остановка по команде пользователя")
        except Exception as e:
            print(f"Критическая ошибка: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        self.socket.close()
        self.context.term()
        cv2.destroyAllWindows()
        print(f"Всего получено кадров: {self.frame_count}")

if __name__ == "__main__":
    # ЗАМЕНИТЕ '192.168.1.100' на реальный IP вашего робота!
    receiver = VideoReceiver(host='192.168.1.139', port=5555)  # ← ВАЖНО!
    receiver.start_receiver()