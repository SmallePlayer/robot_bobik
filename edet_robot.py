from gpiozero import Robot
import socket
import threading

# Настройка моторов через gpiozero
robot = Robot(left=(17, 18), right=(22, 23))  # Левый и правый моторы

# Настройка сетевого сервера
HOST = '0.0.0.0'  # Слушать все интерфейсы
PORT = 8888

def handle_client(conn):
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        
        # Обработка команд WASD
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