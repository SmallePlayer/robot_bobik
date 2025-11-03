from gpiozero import Motor
from time import sleep

# Инициализация моторов
# Левый мотор: forward=GPIO12, backward=GPIO13
# Правый мотор: forward=GPIO18, backward=GPIO19
left_motor = Motor(forward=12, backward=13)
right_motor = Motor(forward=18, backward=19)

# Функция для тестирования одного мотора
def test_motor(motor, motor_name):
    print(f"Тестируем {motor_name} мотор...")
    print("Вперед")
    motor.forward()
    sleep(2)
    print("Стоп")
    motor.stop()
    sleep(1)
    print("Назад")
    motor.backward()
    sleep(2)
    print("Стоп")
    motor.stop()
    sleep(1)

# Тестируем левый мотор
test_motor(left_motor, "левый")

# Тестируем правый мотор
test_motor(right_motor, "правый")

print("Тест завершен.")