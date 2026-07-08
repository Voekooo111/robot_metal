import pickle
import csv
import time

class Exit(Exception):
    pass

class Commands:
    def __init__(self, robot, site):
        self.robot = robot
        self.site = site
        self.default_btn_commands = {
            "documentation" : self.documentation, 
            "define" : self.define, 
            "calibration" : self.calibration, 
            "stand" : self.robot.stand, 
            "full" : self.robot.full, 
            "sleep" : self.robot.stop_all, 
            "create" : self.create, 
            "stop" : self.stop, 
            "clear" : self.site.messages.clear,
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
        self.function_name_for_push = None
        self.function_body_for_push = None

        try:
            with open('user_commands.pkl', mode='rb') as file:
                self.user_commands = pickle.load(file)

        except Exception:
            pass
    
    def area_click(self, area):
        self.chose_servo = area
        self.site.messages.append(f"Выбран сервопривод: {area}.")
        if self._servo_define is not None:
            # определение сервоприводов
            if area in self.robot.body.keys():
                self.robot.body[area] = self._servo_define
            if self._servo_define == 15:
                self._servo_define = None
                self.chose_servo = None
                self.site.messages.append("Сервоприводы успешно определены.")
                with open('define.pkl', mode='wb') as file:
                    pickle.dump(self.robot.body, file)
            else:
                self.define()

    def post_query(self, text, function_name, function_body, btn, area, delete_ser_button, edit):
        """Post-запрос"""
        if text in self.default_btn_commands:
            print("self.default_btn_commands")
            self.default_btn_commands[text]()

        elif text in self.user_commands:
            print("self.user_commands")
            self.multy_execute(self.user_commands[text])
        
        elif text in self.default_commands:
            print("self.default_commands")
            self.multy_execute(self.user_commands[text])

        elif text == "begin":
            print("begin")
            self.create()
        
        elif function_body != "" and (text == "save" or text == "end"):
            print("сохранение текста в редакторе")
            # сохранение текста в редакторе
            self.function_body_for_push = None
            self.function_name_for_push = None
            if function_name == "":
                function_name = str(self.temp_name)
                self.temp_name += 1
            self.create_function(function_name, function_body)

        elif text == "save" or (btn == "create" and self._flag_create):
            print("выход без создавания функции")
            # выход без создавания функции
            self._flag_create = False

        elif self._flag_calibration and text:
            print("калибровка")
            self.try_calibration(text)
            
        elif delete_ser_button:
            print("удаление")
            if delete_ser_button in self.user_commands:
                self.user_commands.pop(delete_ser_button, "Not Found")
            else:
                self.site.messages.append("Ошибка. Функция не найдена.")
        
        elif edit:
            self._flag_create = True
            self.function_name_for_push = edit
            self.function_body_for_push = "\n".join(" ".join(u_c) for u_c in self.user_commands[edit])
            self.user_commands.pop(edit)
        
        elif btn in self.default_btn_commands:
            print("btn_self.default_btn_commands")
            self.default_btn_commands[btn]()

        elif btn in self.user_commands:
            print("btn_self.user_commands")
            self.multy_execute(self.user_commands[btn])
        
        elif btn in self.default_commands:
            print("btn_self.default_commands")
            self.multy_execute(self.user_commands[btn])

        elif area:
            print("area пролет")
            self.site.messages.append(area)
        elif text:
            print("text пролет")
            self.site.messages.append(text)
        elif btn:
            print("text пролет")
            self.site.messages.append(btn)
        print("-")

    
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
        self.site.messages.extend(commands)

    def define(self):
        """Определить сервопривод как канал."""
        self._flag_calibration = False
        if self._servo_define is None:
            self._servo_define = 0
        else:
            self._servo_define += 1
        self.robot.servo_run(self._servo_define, 1500)
        time.sleep(0.6)
        self.robot.servo_run(self._servo_define, 1300)
        time.sleep(0.6)
        self.robot.servo_run(self._servo_define, 1800)
        time.sleep(0.2)
        self.robot.servo_stop(self._servo_define)
        self.site.messages.append(f"Выберите сервопривод. {self._servo_define}/{self.robot.count_servo-1}.")

    def calibration(self):
        """Калибровка сервоприводов."""
        if not self.chose_servo:
            self.site.messages.append("Перед калибровкой выберите сервопривод.")
            return None
        elif self.chose_servo == 'head':
            self.site.messages.append("Сервопривод головы не вставлен.")
            return None
        self._flag_calibration = True
        self._servo_define = None
        self.site.messages.append(f"Готов к калибровке. Установлено значение - {self.robot.centers[self.robot.body[self.chose_servo]]}.")
        self.site.messages.append("Введите новое значение.")
    
    def try_calibration(self, text):
        try:
            self.site.messages.append(f"Введено число: {text}.")
            text = int(text)
            if text == -1:
                self._flag_calibration = False
                self.chose_servo = None
                text.messages.append("Центр сервопривода откалиброван.")
                raise Exit("Центр сервопривода откалиброван.")
            
            self.robot.servo_run(self.robot.body[self.chose_servo], text)
            self.robot.centers[self.robot.body[self.chose_servo]] = text
            with open('calibration.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.robot.centers)

        except (ValueError, TypeError):
            self.site.messages.append('Введите целое неотрицательное число.')

        except Exit:
            pass

    def stop(self):
        """Остановка процесса."""
        self._flag_calibration = False
        self._servo_define = None
        self.site.messages.append("Принудительная остановка процессов.")
    
    def create(self):
        """Создание функции."""
        self.site.messages.append("")
        self._flag_calibration = False
        self.site.messages.append("begin function")
        self._flag_create = True
    
    def create_function(self, name, com):
        com = [c.split() for c in com.splitlines()]
        self.multy_execute(com)
        self.user_commands[name] = com
        self.site.messages.append(f"Функция {name} создана.")
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
            self.site.messages.append(command)
            if not self.execute(command):
                self.site.messages.append("^^^^Ошибка. Команда не найдена^^^^")
            

    def execute(self, command: list[str]):
        """
        Выполняет комманды.
        
        Args:
            command - команда
        """ 
        if len(command) < 1:
            self.site.messages.append("")
            return True
        elif command[0] in self.default_commands:
            self.default_commands[command[0]](command)
            return True
        else:
            self.site.messages.append("Ошибка. Команда не найдена.")
            return False
    
    def run(self, command):
        """Запуск сервопривода"""
        try:
            if len(command) == 3:
                value = int(command[2])
                self.robot.servo_run_name(command[1], value)
                if self.robot.flag_success_run:
                    return True
                return False
            elif len(command) == 2:
                self.robot.servo_stop_name(command[1])
                if self.robot.flag_success_stop:
                    return True
                return False
            else:
                raise IndexError("")
        except (ValueError, TypeError, IndexError):
            self.site.messages.append("Ошибка входных параметров для run: run <выбранные сервопривод текстом> <значение>")
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
            self.site.messages.append("Ошибка входных параметров для run: run <выбранные сервопривод текстом> <значение>")
            return False

