import pickle
from .robot_object import site, robot
import csv
import time

class Exit(Exception):
    pass

class Commands:
    def __init__(self):
        self.default_btn_commands = {
            "documentation" : self.documentation, 
            "define" : self.define, 
            "calibration" : self.calibration, 
            "stand" : robot.stand, 
            "full" : robot.full, 
            "sleep" : robot.stop_all, 
            "create" : self.create, 
            "stop" : self.stop, 
            "clear" : self.messages.clear,
        }
        self.default_commands = {
            "run" : self.run,
            "wait" : self.wait,
        }
        self.user_commands = dict()
        self.temp_name = 0
        self.temp_user_commands = []
        self.temp_user_commands_name = None

        self.servo_side = [1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1]
        self.chose_servo = None
        self._flag_calibration = False
        self._flag_create = False
        self._servo_define = None

        try:
            with open('user_commands.pkl', mode='rb') as file:
                self.user_commands = pickle.load(file)

        except Exception:
            pass
    
    def area_click(self, area):
        self.chose_servo = area
        site.messages.append(f"Выбран сервопривод: {area}.")
        if self._servo_define is not None:
            # определение сервоприводов
            if area in robot.body.keys():
                robot.body[area] = self._servo_define
            if self._servo_define == 15:
                self._servo_define = None
                self.chose_servo = None
                site.messages.append("Сервоприводы успешно определены.")
                with open('define.pkl', mode='wb') as file:
                    pickle.dump(robot.body, file)
            else:
                self.define()

    def post_query(self, text, function_name, function_body, btn, area, delete_ser_button):
        """Post-запрос"""
        if text in self.default_btn_commands:
            self.default_btn_commands[text]()

        elif text in self.user_commands:
            self.multy_execute(self.user_commands[text])
        
        elif text in self.default_commands:
            self.multy_execute(self.user_commands[text])

        elif btn in self.default_btn_commands:
            self.default_btn_commands[btn]()

        elif btn in self.user_commands:
            self.multy_execute(self.user_commands[btn])
        
        elif btn in self.default_commands:
            self.multy_execute(self.user_commands[btn])

        elif text == "begin":
            self.create()
        
        elif function_body != "" and (text == "save" or text == "end"):
            # сохранение текста в редакторе
            if function_name == "":
                function_name = str(self.temp_name)
                self.temp_name += 1
            self.create_function(function_name, function_body)

        elif text == "save" or (btn == "create" and self._flag_create):
            # выход без создавания функции
            self._flag_create = False

        elif self._flag_calibration and text:
            self.try_calibration(text)
            
        elif delete_ser_button:
            if delete_ser_button in self.user_commands:
                self.user_commands.pop(delete_ser_button, "Not Found")
            else:
                site.messages.append("Ошибка. Функция не найдена.")
        elif area:
            site.messages.append(area)
        elif text:
            site.messages.append(text)
        elif btn:
            site.messages.append(btn)

    
    def documentation(self):
        """Документация к командам."""
        commands = [
            "-----------------------------------------",
            "Определить сервопривод как канал:",
            "1) define",
            "2) Выбрать сервопривод",
            "Повторять шаг 2, пока не определиться каждый сервопривод",
            "",
            "Калибровка:",
            "1) full",
            "2) Выбрать сервопривод",
            "3) calibration",
            "4) Вводить числа",
            "У каждого сервопривода есть ограничения по времени импульса (500 мкс, 2500 мкс)",
            "5) Для завершения ввести -1",
            "6) sleep",
            "",
            "Включить все сервоприводы:",
            "1) full",
            "",
            "Отключить все сервоприводы",
            "1) sleep",
            "",
            "Принудительно остановить процесс:",
            "1) stop",
        ]
        self.messages.extend(commands)

    def define(self):
        """Определить сервопривод как канал."""
        self._flag_calibration = False
        if self._servo_define is None:
            self._servo_define = 0
        else:
            self._servo_define += 1
        robot.servo_run(self._servo_define, 1500)
        time.sleep(0.6)
        robot.servo_run(self._servo_define, 1300)
        time.sleep(0.6)
        robot.servo_run(self._servo_define, 1800)
        time.sleep(0.2)
        robot.servo_stop(self._servo_define)
        site.messages.append(f"Выберите сервопривод. {self._servo_define}/{robot.count_servo-1}.")

    def calibration(self):
        """Калибровка сервоприводов."""
        if not self.chose_servo:
            site.messages.append("Перед калибровкой выберите сервопривод.")
            return None
        elif self.chose_servo == 'head':
            site.messages.append("Сервопривод головы не вставлен.")
            return None
        self._flag_calibration = True
        self._servo_define = None
        site.messages.append(f"Готов к калибровке. Установлено значение - {robot.centers[robot.body[self.chose_servo]]}.")
        site.messages.append("Введите новое значение.")
    
    def try_calibration(self, text):
        try:
            site.messages.append(f"Введено число: {text}.")
            text = int(text)
            if text == -1:
                self._flag_calibration = False
                self.chose_servo = None
                text.messages.append("Центр сервопривода откалиброван.")
                raise Exit("Центр сервопривода откалиброван.")
            
            robot.servo_run(robot.body[self.chose_servo], text)
            robot.centers[robot.body[self.chose_servo]] = text
            with open('calibration.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(robot.centers)

        except (ValueError, TypeError):
            site.messages.append('Введите целое неотрицательное число.')

        except Exit:
            pass

    def stop(self):
        """Остановка процесса."""
        self._flag_calibration = False
        self._servo_define = None
        site.messages.append("Принудительная остановка процессов.")
    
    def create(self):
        """Создание функции."""
        site.messages.append("")
        self._flag_calibration = False
        site.messages.append("begin function")
        self._flag_create = True
    
    def create_function(self, name, com):
        com = [c.split() for c in com.splitlines()]
        self.multy_execute(com)
        self.user_commands[name] = com
        site.messages.append(f"Функция {name} создана.")
        with open('user_commands.pkl', mode='wb') as file:
                pickle.dump(self.user_commands, file)
        self._flag_create = False

    def multy_execute(self, commands: list[list[str]]):
        """
        Выполняет несколько комманд.
        
        Args:
            commands - команды
        """
        for command in commands:
            site.messages.append(command)
            if not self.execute(command):
                site.messages.append("^^^^Ошибка. Команда не найдена^^^^")
            

    def execute(self, command: list[str]):
        """
        Выполняет комманды.
        
        Args:
            command - команда
        """ 
        if len(command) < 1:
            site.messages.append("")
        elif command[0] in self.default_commands:
            self.default_commands[command]()
        else:
            site.messages.append("Ошибка. Команда не найдена.")
            return False
    
    def run(self, command):
        """Запуск сервопривода"""
        try:
            if len(command) == 3:
                value = int(command[2])
                robot.servo_run_name(command[1], value)
                if robot.flag_success_run:
                    return True
                return False
            elif len(command) == 2:
                robot.servo_stop_name(command[1])
                if robot.flag_success_stop:
                    return True
                return False
            else:
                raise IndexError("")
        except (ValueError, TypeError, IndexError):
            site.messages.append("Ошибка входных параметров для run: run <выбранные сервопривод текстом> <значение>")
            return False
    
    def wait(self, command):
        """Задержка в секундах"""
        try:
            if len(command) == 2:
                value = float(command[1])
                time.sleep(value) # Заменить на datetime
                return True
            else:
                raise IndexError
        except (ValueError, TypeError, IndexError):
            site.messages.append("Ошибка входных параметров для run: run <выбранные сервопривод текстом> <значение>")
            return False

