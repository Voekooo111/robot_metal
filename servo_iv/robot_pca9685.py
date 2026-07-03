from .pca9685 import Pca
import csv
import lgpio
import time
import pickle

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
        self.body: dict[str, int | None] = {
            'hand_left_0': None,
            'hand_left_1': None,
            'hand_left_2': None,
            'hand_right_0': None,
            'hand_right_1': None,
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
        }
        self.bodypart: dict[str, None | tuple] = {
            'hand' : tuple(range(6)), 
            'leg' : tuple(range(6, count_servo))
        }
        self.count_servo = count_servo
        self.centers = [1500] * count_servo
    
    def class_start(self):
        self.define_servo()
        self.calibrate()

    def define_servo(self):
        """Определение сервопривода."""
        try:
            with open('define.pkl', mode='rb') as file:
                self.body = pickle.load(file)

        except FileNotFoundError:
            for i in range(self.count_servo):
                self.servo_run(i, 1500)
                time.sleep(1)
                self.servo_run(i, 1300)
                time.sleep(1)
                self.servo_run(i, 1800)
                time.sleep(1)
                self.servo_stop(i)
                flag_input = True
                while flag_input:
                    inp = input("Какая часть робота? _")
                    if inp in self.body.keys():
                        flag_input = False
                        self.body[inp] = i
                    print("Попробуйте снова.")
            with open('define.pkl', mode='wb') as file:
                pickle.dump(self.body, file)

    
    def calibrate(self, skip_calibration=True):
        """
        Калибровка серво.
        
        Args:
            skip_calibration (по умолчанию True) при True - только считывает данные с файла.
        """
        try:
            with open('calibration.csv', mode='r') as file:
                self.centers = list(int(x) for x in list(csv.reader(file))[0])
            if len(self.centers) != self.count_servo: 
                raise FileNotFoundError
            print(self.centers)

        except FileNotFoundError:
            if not skip_calibration:
                for i in range(self.count_servo):
                    self.servo_run(list(self.body.values())[i], 1500)
                    time.sleep(0.2)

                for i in range(self.count_servo):
                    value = input("Середина сервопривода(мс). Для сохранения (-1). __")
                    while value != '-1':
                        try:
                            value = int(value)
                            self.servo_run(list(self.body.values())[i], value)
                            self.centers[i] = value
                            value = input("Середина сервопривода(мс). Для сохранения (-1). __")
                        except (ValueError, TypeError):
                            print('Введите число')
                            
                for i in range(self.count_servo):
                    self.servo_stop(list(self.body.values())[i])
                    time.sleep(0.2)

            with open('calibration.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.centers)


    def stop_all(self):
        for i in range(self.count_servo):
            self.servo_stop(i)
            time.sleep(0.1)


    def full(self):
        """Робот запускает все сервоприводы."""
        for i in range(self.count_servo):
            self.servo_run(i, self.centers[i])     
            time.sleep(0.1)
    
    def servo_run_name(self, name: str, value: int):
        """Запуск сервопривода по названию."""
        self.servo_run(self.body[name], self.centers[self.body[name]] + value)
    

    def stand(self):
        self.servo_run_name('hand_left_2', 700)
        self.servo_run_name('hand_right_2', -700)
        time.sleep(0.5)
        self.servo_run_name('hand_left_1', -500)
        self.servo_run_name('hand_right_1', 500)
        time.sleep(0.2)
        self.servo_run_name('leg_left_1', -600)
        self.servo_run_name('leg_right_1', 600)
