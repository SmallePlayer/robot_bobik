from gpiozero import OutputDevice
import time

# Настройка пинов (замените на ваши)
IN1 = OutputDevice(17)
IN2 = OutputDevice(18)
IN3 = OutputDevice(22)
IN4 = OutputDevice(23)

def test_motor(pin1, pin2, motor_name):
    print(f"Testing {motor_name}...")
    
    # Вращение в одну сторону
    pin1.on()
    pin2.off()
    print(f"  {motor_name}: FORWARD")
    time.sleep(2)
    
    # Стоп
    pin1.off()
    pin2.off()
    print(f"  {motor_name}: STOP")
    time.sleep(1)
    
    # Вращение в другую сторону
    pin1.off()
    pin2.on()
    print(f"  {motor_name}: BACKWARD")
    time.sleep(2)
    
    # Стоп
    pin1.off()
    pin2.off()
    print(f"  {motor_name}: STOP")
    time.sleep(1)

try:
    print("Motor test started...")
    
    # Тестируем левый мотор (IN1, IN2)
    test_motor(IN1, IN2, "LEFT MOTOR")
    
    # Тестируем правый мотор (IN3, IN4)
    test_motor(IN3, IN4, "RIGHT MOTOR")
    
    print("Test completed!")

except KeyboardInterrupt:
    print("Test interrupted")
finally:
    # Гарантированно выключаем все пины
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.off()