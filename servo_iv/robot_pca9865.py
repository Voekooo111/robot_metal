from . import Pca
import csv
import lgpio
import time

class Robot_pca(Pca):
    """
    Робот на PCA9685.
    Класс подключается по i2c шине к PCA9685. И управляет серво, подключенными к PCA.
    
    Args:
        pin_bus_address: (int, hex) - шина и адрес i2c
        freq - частота подключенных устройств
    """
    def __init__(self, pin_bus_address: tuple = (1, 0x40), freq: int = 50, count_servo: int = 16):
        super().__init__(pin_bus_address, freq)
        self.body: dict[str, int | None | tuple] = {
            'hand_left_0': None,
            'hand_left_1': None,
            'hand_left_2': None,
            'hand_rigth_0': None,
            'hand_rigth_1': None,
            'hand_right_2': None,
            'leg_left_0' : None,
            'leg_left_1' : None,
            'leg_left_2' : None,
            'leg_left_3' : None,
            'leg_left_4' : None,
            'leg_right_0' : None,
            'leg_right_1' : None,
            'leg_right_2' : None,
            'leg_right_3' : None,
            'leg_right_4' : None,
            'hand' : tuple(range(6)), 
            'leg' : tuple(range(6, count_servo))
        }
        self.count_servo = count_servo
        self.centers = (1500) * count_servo

    def define_servo(self):
        """Определение сервопривода."""
        for i in range(self.count_servo):
            self.servo_run(i, 1500)
            time.sleep(1)
            self.servo_run(i, 1300)
            time.sleep(1)
            self.servo_run(i, 1800)
            time.sleep(1)
            flag_input = True
            while flag_input:
                inp = input("Какая часть робота? _")
                if inp in self.body.keys():
                    flag_input = False
                    self.body[inp] = i
    
    def calibrate(self):
        """Калибровка серво."""
        try:
            with open('calibration.csv', mode='r') as file:
                self.data = tuple(int(x) for x in list(csv.reader(file))[0])
            if len(self.data) != 16: raise FileNotFoundError
            print(self.data)

        except FileNotFoundError:
            for i in range(16):
                pass
            with open('calibration.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(data)
                

