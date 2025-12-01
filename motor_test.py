import RPi.GPIO as GPIO
import time

# Настройка пинов по вашему описанию Robot(left=(12, 13), right=(19, 18))
# Предполагается, что это номера GPIO для RPWM и LPWM каждого мотора.
LEFT_MOTOR_RPWM = 12   # GPIO для вращения левого мотора "вперед"
LEFT_MOTOR_LPWM = 13   # GPIO для вращения левого мотора "назад"
RIGHT_MOTOR_RPWM = 19  # GPIO для вращения правого мотора "вперед"
RIGHT_MOTOR_LPWM = 18  # GPIO для вращения правого мотора "назад"

# Выберите любые свободные GPIO для пинов включения (Enable)
LEFT_MOTOR_R_EN = 16   # GPIO для включения правого моста левого драйвера
LEFT_MOTOR_L_EN = 20   # GPIO для включения левого моста левого драйвера
RIGHT_MOTOR_R_EN = 21  # GPIO для правого драйвера
RIGHT_MOTOR_L_EN = 26  # GPIO для правого драйвера

# Настройка режима пинов
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Настройка всех пинов как выходных
motor_pins = [
    LEFT_MOTOR_RPWM, LEFT_MOTOR_LPWM, LEFT_MOTOR_R_EN, LEFT_MOTOR_L_EN,
    RIGHT_MOTOR_RPWM, RIGHT_MOTOR_LPWM, RIGHT_MOTOR_R_EN, RIGHT_MOTOR_L_EN
]
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Изначально все выключены

def motor_test(rpwm_pin, lpwm_pin, r_en_pin, l_en_pin, motor_name):
    """Функция для тестирования одного мотора."""
    print(f"Тест мотора: {motor_name}")
    
    # Включаем оба полумоста драйвера
    GPIO.output(r_en_pin, GPIO.HIGH)
    GPIO.output(l_en_pin, GPIO.HIGH)
    
    # Двигатель вперед (50% мощности)
    print("  -> Вперед")
    GPIO.output(lpwm_pin, GPIO.LOW)
    GPIO.output(rpwm_pin, GPIO.HIGH)  # Можно заменить на analogWrite для плавности
    time.sleep(2)
    
    # Двигатель назад (50% мощности)
    print("  -> Назад")
    GPIO.output(rpwm_pin, GPIO.LOW)
    GPIO.output(lpwm_pin, GPIO.HIGH)
    time.sleep(2)
    
    # Стоп
    print("  -> Стоп")
    GPIO.output(rpwm_pin, GPIO.LOW)
    GPIO.output(lpwm_pin, GPIO.LOW)
    GPIO.output(r_en_pin, GPIO.LOW)
    GPIO.output(l_en_pin, GPIO.LOW)
    
    time.sleep(1)  # Пауза между тестами

try:
    print("=== Начало теста двигателей ===")
    # Тест левого мотора
    motor_test(LEFT_MOTOR_RPWM, LEFT_MOTOR_LPWM, 
               LEFT_MOTOR_R_EN, LEFT_MOTOR_L_EN, "ЛЕВЫЙ")
    # Тест правого мотора
    motor_test(RIGHT_MOTOR_RPWM, RIGHT_MOTOR_LPWM, 
               RIGHT_MOTOR_R_EN, RIGHT_MOTOR_L_EN, "ПРАВЫЙ")
    print("=== Тест завершен ===")

except KeyboardInterrupt:
    print("Программа остановлена пользователем")

finally:
    # Гарантированно выключаем все пины
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()
    print("GPIO очищены.")