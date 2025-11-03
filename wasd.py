import socket
from pynput import keyboard 

HOST = '192.168.1.100'  # Замените на IP Raspberry Pixwwwwwwwwwwwwwwwwwwwwwwsa
PORT = 8888


def send_command(key):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(key.encode())
            print(f"Sent: {key}")
    except Exception as e:
        print(f"Error sending command: {e}")

def on_press(key):
    try:
        if key == keyboard.KeyCode.from_char('w'):
            send_command('w')
        elif key == keyboard.KeyCode.from_char('s'):
            send_command('s')
        elif key == keyboard.KeyCode.from_char('a'):
            send_command('a')
        elif key == keyboard.KeyCode.from_char('d'):
            send_command('d')
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        send_command('x')  # Останавливаем робота перед выходом
        return False
    elif key == keyboard.KeyCode.from_char('x'):
        send_command('x')

print("Use WASD to control the robot. Press 'x' to stop, 'Esc' to exit.")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
