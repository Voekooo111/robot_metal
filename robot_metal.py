import pygame
from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16, address=0x40)
pygame.init()

get_servo = {
    "hand0_left": 0,
    "hand1_left": 1,
    "hand2_left": 2,
    "hand0_right": 3,
    "hand1_right": 4,
    "hand2_right": 5,
    "leg4_left": 6,
    "leg3_left": 7,
    "leg2_left": 8,
    "leg1_left": 9,
    "leg0_left": 10,
    "leg4_right": 11,
    "leg3_right": 12,
    "leg2_right": 13,
    "leg1_right": 14,
    "leg0_right": 15,
    "leg": range(6, 16),
}
joystick_work = True


# ======Function======
def calibration_servo():
    """
    Калибровка каждого сервопривода
    """


def stand(simple: bool = False):
    """
    Робот должен вставать

    Args:
        simple - только выпрямляет ноги.

    Returns:
        None
    """
    if simple:
        for s in get_servo['leg']:
            kit.servo[s].angle = 90
            time.sleep(0.1)


# ======Workplace======
try:
    pygame.joystick.init()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
except Exception:
    joystick_work = False
    print("Джойстик не подключён")

while joystick_work:
    pygame.event.pump()

    x = joystick.get_axis(0)  # левый стик X
    y = joystick.get_axis(1)  # левый стик Y

    # print(x, y)
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            print(f"Нажата кнопка номер: {event.button}")
            if event.button == 0:
                for i in range(6):
                    kit.servo[i].angle = 0
            if event.button == 1:
                for i in range(6):
                    kit.servo[i].angle = 90
    time.sleep(0.2)
    kit.servo[0].angle = None

stand(True)
time.sleep(3)
print("Готово")

for i in range(16):
    kit.servo[i].angle = None
    time.sleep(0.1)
