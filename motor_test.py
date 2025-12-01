from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep

# Пины по вашему описанию Robot(left=(12, 13), right=(19, 18))
# Предполагаем, что это пины для двух моторов:
# Для каждого мотора: первый пин - вперед, второй - назад

LEFT_FORWARD_PIN = 12   # GPIO 12 для движения левого мотора вперед
LEFT_BACKWARD_PIN = 13  # GPIO 13 для движения левого мотора назад
RIGHT_FORWARD_PIN = 19  # GPIO 19 для движения правого мотора вперед
RIGHT_BACKWARD_PIN = 18 # GPIO 18 для движения правого мотора назад

# Пины включения (Enable) - можно подключить к 5V или управлять через GPIO
# В этом примере управляем через GPIO
LEFT_ENABLE_PIN = 16    # GPIO 16 для включения левого драйвера
RIGHT_ENABLE_PIN = 20   # GPIO 20 для включения правого драйвера

# Создаем объекты для управления моторами
# Для IBT-2 нужно использовать PWMOutputDevice для плавного управления
left_forward = PWMOutputDevice(LEFT_FORWARD_PIN, frequency=1000)
left_backward = PWMOutputDevice(LEFT_BACKWARD_PIN, frequency=1000)
right_forward = PWMOutputDevice(RIGHT_FORWARD_PIN, frequency=1000)
right_backward = PWMOutputDevice(RIGHT_BACKWARD_PIN, frequency=1000)

# Пины включения (Enable) - DigitalOutputDevice для включения/выключения
left_enable = DigitalOutputDevice(LEFT_ENABLE_PIN)
right_enable = DigitalOutputDevice(RIGHT_ENABLE_PIN)

def motor_test(forward, backward, enable, motor_name):
    """Тестирует один мотор"""
    print(f"Тестируем {motor_name} мотор...")
    
    # Включаем драйвер
    enable.on()
    
    # Двигаемся вперед (50% мощности)
    print("  Вперед (50%)")
    backward.value = 0
    forward.value = 0.5
    sleep(2)
    
    # Двигаемся назад (50% мощности)
    print("  Назад (50%)")
    forward.value = 0
    backward.value = 0.5
    sleep(2)
    
    # Стоп
    print("  Стоп")
    forward.value = 0
    backward.value = 0
    enable.off()
    
    sleep(1)

# Основной тест
try:
    print("=== Начало теста моторов ===")
    
    # Тест левого мотора
    motor_test(left_forward, left_backward, left_enable, "левый")
    
    # Тест правого мотора
    motor_test(right_forward, right_backward, right_enable, "правый")
    
    print("=== Тест завершен ===")

except KeyboardInterrupt:
    print("Программа остановлена пользователем")

finally:
    # Гарантированно выключаем все
    left_forward.close()
    left_backward.close()
    right_forward.close()
    right_backward.close()
    left_enable.close()
    right_enable.close()
    print("Ресурсы освобождены.")