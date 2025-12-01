#!/usr/bin/env python3
"""
Сервер управления роботом на Raspberry Pi с использованием RPi.GPIO
Управление через ZMQ сокеты
"""

import zmq
import json
import time
import threading
import RPi.GPIO as GPIO

class MotorController:
    """Класс для управления одним мотором через H-мост"""
    
    def __init__(self, forward_pin, backward_pin, pwm_pin):
        """
        Инициализация мотора
        forward_pin: GPIO пин для движения вперед
        backward_pin: GPIO пин для движения назад
        pwm_pin: GPIO пин для ШИМ (управление скоростью)
        """
        self.forward_pin = forward_pin
        self.backward_pin = backward_pin
        self.pwm_pin = pwm_pin
        
        # Настройка пинов
        GPIO.setup(forward_pin, GPIO.OUT)
        GPIO.setup(backward_pin, GPIO.OUT)
        GPIO.setup(pwm_pin, GPIO.OUT)
        
        # Создание ШИМ объекта
        self.pwm = GPIO.PWM(pwm_pin, 1000)  # Частота 1000 Гц
        
        # Запуск ШИМ с нулевой скоростью
        self.pwm.start(0)
        
        # Изначально мотор выключен
        GPIO.output(forward_pin, GPIO.LOW)
        GPIO.output(backward_pin, GPIO.LOW)
        
    def forward(self, speed):
        """Движение вперед с заданной скоростью (0-100%)"""
        if speed > 0:
            GPIO.output(self.forward_pin, GPIO.HIGH)
            GPIO.output(self.backward_pin, GPIO.LOW)
            self.pwm.ChangeDutyCycle(speed * 100)  # Преобразуем 0.0-1.0 в 0-100
        else:
            self.stop()
    
    def backward(self, speed):
        """Движение назад с заданной скоростью (0-100%)"""
        if speed > 0:
            GPIO.output(self.forward_pin, GPIO.LOW)
            GPIO.output(self.backward_pin, GPIO.HIGH)
            self.pwm.ChangeDutyCycle(speed * 100)
        else:
            self.stop()
    
    def stop(self):
        """Остановка мотора"""
        GPIO.output(self.forward_pin, GPIO.LOW)
        GPIO.output(self.backward_pin, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)

class RobotController:
    """Класс для управления роботом с двумя моторами"""
    
    def __init__(self):
        # Настройка нумерации пинов по GPIO (не по физическим номерам)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Инициализация моторов
        # Левый мотор: GPIO12 - вперед, GPIO13 - назад, GPIO26 - ШИМ
        self.left_motor = MotorController(
            forward_pin=12, 
            backward_pin=13, 
            pwm_pin=26
        )
        
        # Правый мотор: GPIO19 - вперед, GPIO18 - назад, GPIO16 - ШИМ
        self.right_motor = MotorController(
            forward_pin=19, 
            backward_pin=18, 
            pwm_pin=16
        )
        
        # Текущая скорость (0.0 до 1.0)
        self.current_speed = 0.7
        
        # Флаг для плавной остановки
        self.is_moving = False
        
    def forward(self, speed=None):
        """Движение вперед"""
        if speed is None:
            speed = self.current_speed
            
        self.left_motor.forward(speed)
        self.right_motor.forward(speed)
        self.is_moving = True
        
    def backward(self, speed=None):
        """Движение назад"""
        if speed is None:
            speed = self.current_speed
            
        self.left_motor.backward(speed)
        self.right_motor.backward(speed)
        self.is_moving = True
        
    def left(self, speed=None):
        """Поворот налево (правый мотор вперед, левый назад или остановлен)"""
        if speed is None:
            speed = self.current_speed
            
        # Вариант 1: Разворот на месте
        self.left_motor.backward(speed * 0.7)  # Неменьше скорость для плавности
        self.right_motor.forward(speed)
        self.is_moving = True
        
    def right(self, speed=None):
        """Поворот направо"""
        if speed is None:
            speed = self.current_speed
            
        self.left_motor.forward(speed)
        self.right_motor.backward(speed * 0.7)
        self.is_moving = True
        
    def stop(self):
        """Полная остановка"""
        self.left_motor.stop()
        self.right_motor.stop()
        self.is_moving = False
        
    def set_speed(self, speed):
        """Установка скорости движения (0.1 до 1.0)"""
        if 0.1 <= speed <= 1.0:
            self.current_speed = speed
            
            # Если робот движется, обновляем текущую скорость
            if self.is_moving:
                # Определяем текущее направление и обновляем
                # В реальном проекте нужно отслеживать состояние
                pass
                
            return True
        return False
        
    def cleanup(self):
        """Очистка ресурсов GPIO"""
        self.stop()
        time.sleep(0.1)
        GPIO.cleanup()
        
    def execute_command(self, command):
        """Выполняет команду движения"""
        try:
            if command == "forward":
                self.forward()
                print("🔼 ДВИЖЕНИЕ ВПЕРЕД")
            elif command == "backward":
                self.backward()
                print("🔽 ДВИЖЕНИЕ НАЗАД")
            elif command == "left":
                self.left()
                print("↩️  ПОВОРОТ ВЛЕВО")
            elif command == "right":
                self.right()
                print("↪️  ПОВОРОТ ВПРАВО")
            elif command == "stop":
                self.stop()
                print("⏹️  СТОП")
            elif command.startswith("speed:"):
                # Изменение скорости: "speed:0.8"
                new_speed = float(command.split(":")[1])
                if self.set_speed(new_speed):
                    print(f"🎚️  Скорость изменена: {new_speed}")
                else:
                    print(f"❌ Некорректная скорость: {new_speed}")
            else:
                print(f"❌ Неизвестная команда: {command}")
                
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")

def main():
    # Настройка ZMQ
    context = zmq.Context()
    socket = context.socket(zmq.REP)  # REP (reply) для ответов
    socket.bind("tcp://*:5555")       # Слушаем на всех интерфейсах порт 5555
    
    # Инициализация робота
    try:
        robot = RobotController()
        print("🤖 РОБОТ ИНИЦИАЛИЗИРОВАН УСПЕШНО")
    except Exception as e:
        print(f"❌ ОШИБКА ИНИЦИАЛИЗАЦИИ РОБОТА: {e}")
        return
    
    print("🤖 СЕРВЕР УПРАВЛЕНИЯ РОБОТОМ ЗАПУЩЕН")
    print("📍 Адрес для подключения: tcp://[IP_РОБОТА]:5555")
    print("📝 Ожидание команд...")
    print("Доступные команды: forward, backward, left, right, stop, speed:X.X")
    
    try:
        while True:
            # Ожидаем команду от клиента
            message = socket.recv_string()
            print(f"📨 Получена команда: {message}")
            
            # Выполняем команду
            robot.execute_command(message)
            
            # Отправляем подтверждение
            response = {
                "status": "success",
                "command": message,
                "speed": robot.current_speed
            }
            socket.send_string(json.dumps(response))
            
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера по запросу пользователя...")
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")
    finally:
        print("🧹 Очистка ресурсов...")
        robot.cleanup()
        socket.close()
        context.term()
        print("🔴 Сервер остановлен, моторы выключены")

if __name__ == "__main__":
    # Для работы с GPIO требуется запуск с правами суперпользователя
    main()