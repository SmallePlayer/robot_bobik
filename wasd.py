import socket
import keyboard  # Установите: pip install keyboard

HOST = 'IP_ADDRESS_OF_PI'  # Замените на IP Raspberry Pi
PORT = 8888

def send_command(key):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(key.encode())

# Назначение клавиш WASD
keyboard.add_hotkey('w', lambda: send_command('w'))
keyboard.add_hotkey('s', lambda: send_command('s'))
keyboard.add_hotkey('a', lambda: send_command('a'))
keyboard.add_hotkey('d', lambda: send_command('d'))
keyboard.add_hotkey('x', lambda: send_command('x'))  # Стоп-клавиша

print("Use WASD to control the robot. Press 'x' to stop.")
keyboard.wait('esc')  # Нажмите Esc для выхода
