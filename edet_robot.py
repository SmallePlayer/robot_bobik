from gpiozero import Robot
from gpiozero.pins.lgpio import LGPIOFactory
import socket
import threading

# Явно указываем фабрику пинов для Raspberry Pi 5
pin_factory = LGPIOFactory()

# Настройка моторов с указанием фабрики пинов
robot = Robot(left=(17, 18), right=(22, 23), pin_factory=pin_factory)

# Остальной код без изменений...
HOST = '0.0.0.0'
PORT = 8888

def handle_client(conn):
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        
        if data == 'w':
            robot.forward()
        elif data == 's':
            robot.backward()
        elif data == 'a':
            robot.left()
        elif data == 'd':
            robot.right()
        elif data == 'x':
            robot.stop()
        print(f"Received: {data}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        thread = threading.Thread(target=handle_client, args=(conn,))
        thread.start()