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
        self.channal_to_body: dict[int, str] = {}
        self.bodypart: dict[str, None | tuple] = {
            'hand' : tuple(self.body[i] for i in self.body if i[0]=='h'), 
            'leg' : tuple(self.body[i] for i in self.body if i[0]=='l'),
            'hand_0': (self.body['hand_left_0'], self.body['hand_right_0']),
            'hand_1': (self.body['hand_left_1'], self.body['hand_right_1']),
            'hand_2': (self.body['hand_left_2'], self.body['hand_right_2']),
            'leg_0' : (self.body['leg_left_0'], self.body['leg_right_0']),
            'leg_1' : (self.body['leg_left_1'], self.body['leg_right_1']),
            'leg_2' : (self.body['leg_left_2'], self.body['leg_right_2']),
            'leg_3' : (self.body['leg_left_3'], self.body['leg_right_3']),
            'leg_4' : (self.body['leg_left_4'], self.body['leg_right_4']),
        }
        self.count_servo = count_servo
        self.centers = [1500] * count_servo
        self.flag_success_run = False
        self.flag_success_stop = False
        self.pwm = [None] * self.count_servo
    
    def servo_side(self, channal: int):
        mapping: dict[str, int] = {
            'hand_left_0': 1,
            'hand_left_1': 1,
            'hand_left_2': -1,
            'hand_right_0': -1,
            'hand_right_1': -1,
            'hand_right_2': 1,
            'leg_left_0': -1,
            'leg_left_1': 1,
            'leg_left_2': -1,
            'leg_left_3': 1,
            'leg_left_4': 1,
            'leg_right_0': 1,
            'leg_right_1': -1,
            'leg_right_2': 1,
            'leg_right_3': -1,
            'leg_right_4': -1
        }
        return mapping.get(self.channal_to_body.get(channal))
    
    def class_start(self):
        """Преднастройка класса."""
        self.define_servo()
        self.calibrate()

    def update_bodypart(self):
        """Обновление budypart"""
        self.bodypart = {
            'hand': tuple(self.body[i] for i in self.body if i.startswith('hand')),
            'leg': tuple(self.body[i] for i in self.body if i.startswith('leg')),
            'hand_0': (self.body['hand_left_0'], self.body['hand_right_0']),
            'hand_1': (self.body['hand_left_1'], self.body['hand_right_1']),
            'hand_2': (self.body['hand_left_2'], self.body['hand_right_2']),
            'leg_0': (self.body['leg_left_0'], self.body['leg_right_0']),
            'leg_1': (self.body['leg_left_1'], self.body['leg_right_1']),
            'leg_2': (self.body['leg_left_2'], self.body['leg_right_2']),
            'leg_3': (self.body['leg_left_3'], self.body['leg_right_3']),
            'leg_4': (self.body['leg_left_4'], self.body['leg_right_4']),
        }
        self.channal_to_body = {value: key for key, value in self.body.items()}

    def define_servo(self):
        """Определение сервопривода."""
        try:
            with open('define.pkl', mode='rb') as file:
                self.body = pickle.load(file)
            self.update_bodypart()

        except FileNotFoundError:
            for i in range(self.count_servo):
                self.servo_run(i, 1800)
                time.sleep(1)
                self.servo_run(i, 1300)
                time.sleep(1)
                self.servo_run(i, 1500)
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
            self.update_bodypart()

    
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
        """Выключить все сервоприводы."""
        for i in range(self.count_servo):
            self.servo_stop(i)
            time.sleep(0.2)


    def full(self):
        """Робот запускает все сервоприводы."""
        for i in range(self.count_servo):
            self.servo_run(i, self.centers[i])     
            time.sleep(0.2)
    
    def servo_run_name(self, name: str, value: int):
        """
        Запуск сервопривода по названию.
        
        Args:
            name - название сервопривода.
            value - значение, на которое надо переместить сервопривод.
        """
        self.flag_success_run = True
        if name in self.body:
            body_num = self.body[name]
            body_num = (body_num, )
        elif name in self.bodypart:
            body_num = self.bodypart[name]
        else:
            self.flag_success_run = False
        for b_n in body_num:
            pulse = self.centers[b_n] + value * self.servo_side(b_n)
            self.servo_run(b_n, pulse)
            self.pwm[b_n] = pulse

    def servo_stop_name(self, name: str):
        """
        Выключение сервопривода по названию.
        
        Args:
            name - название сервопривода.
        """
        self.flag_success_stop = True
        if name in self.body:
            body_num = self.body[name]
            body_num = (body_num, )
        elif name in self.bodypart:
            body_num = self.bodypart[name]
        else:
            self.flag_success_stop = False
        for b_n in body_num:
            self.servo_stop(b_n)
            self.pwm[b_n] = None

    def stand(self):
        """Робот должен встать с положения лёжа."""
        self.servo_run_name('hand_left_2', 900)
        self.servo_run_name('hand_right_2', -900)
        time.sleep(1)
        self.servo_run_name('hand_left_1', -500)
        self.servo_run_name('hand_right_1', 500)
        time.sleep(0.5)
        self.servo_run_name('hand_left_1', -800)
        self.servo_run_name('hand_right_1', 800)
        time.sleep(0.2)
        self.servo_run_name('hand_left_0', -500)
        self.servo_run_name('hand_right_0', 500)
        time.sleep(0.2)
        self.servo_run_name('leg_left_1', -700)
        self.servo_run_name('leg_right_1', 700)
        time.sleep(1)
        self.servo_run_name('leg_left_3', 1000)
        self.servo_run_name('leg_right_3', -1000)
