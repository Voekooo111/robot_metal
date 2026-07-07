from flask import Flask, render_template, request, redirect, url_for
from .robot_object import robot
import pickle
import time
import csv
import copy

class Exit(Exception):
    pass

class Site:
    """Страничка в локальном интернете."""
    def __init__(self):
        self.app = Flask(__name__)
        self.messages = []
        self.buttons = ["documentation", "define", "calibration", "stand", "full", "sleep", "create", "stop", "clear"]
        self.servo_side = [1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1]
        self.chose_servo = None
        self._flag_calibration = False
        self._flag_create = False
        self.debug = True
        self._servo_define = None
        self.temp_user_commands = []
        self.temp_user_commands_name = None
        self.user_commands = dict()
        self.robot_words = [
            "run",
            "wait",
        ]
        self.flip = render_template(
            "index.html",
            message = self.messages,
            buttons = self.buttons,
            user_buttons = list(self.user_commands.keys()),
            flag_calibration = self._flag_calibration,
            flag_create = self._flag_create,
            robot_words=self.robot_words,
        )

        self.app.add_url_rule(
            "/",
            endpoint="index",
            view_func=self.index,
            methods=["GET", "POST"]
        )

    def index(self):
        """Главная страница."""
        area = request.args.get("area")
        if area:
            self.chose_servo = area
            self.messages.append(f"Выбран сервопривод: {area}.")
            if self._servo_define is not None:
                if area in robot.body.keys():
                    robot.body[area] = self._servo_define
                if self._servo_define == 15:
                    self._servo_define = None
                    self.chose_servo = None
                    self.messages.append("Сервоприводы успешно определены.")
                    with open('define.pkl', mode='wb') as file:
                        pickle.dump(robot.body, file)
                else:
                    self.define()
            return redirect(url_for("index"))

        if request.method == "POST":
            text = request.form.get("text")
            function_name = request.form.get("function_name")
            function_body = request.form.get("function_body")
            btn = request.form.get("button_click")
            area = request.form.get("area_click")
            delete_ser_button = request.form.get("delete")
            if text == "stop":
                self.stop()
            elif text == "begin":
                self._flag_create = False
                self.create()
            elif function_name is not None and function_body is not None and (text == "save" or text == "end"):
                self.create_function(function_name, function_body)
            elif self._flag_calibration and text:
                try:
                    self.messages.append(f"Введено число: {text}.")
                    text = int(text)
                    if text == -1:
                        self._flag_calibration = False
                        self.chose_servo = None
                        self.messages.append("Центр сервопривода откалиброван.")
                        raise Exit("Центр сервопривода откалиброван.")
                    robot.servo_run(robot.body[self.chose_servo], text)
                    robot.centers[robot.body[self.chose_servo]] = text
                    with open('calibration.csv', mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(robot.centers)
                except (ValueError, TypeError):
                    self.messages.append('Введите целое неотрицательное число.')
                except Exit:
                    pass
            elif delete_ser_button is not None and delete_ser_button in self.user_commands:
                self.user_commands.pop(delete_ser_button, "Not Found")
            elif text in self.buttons:
                self.commands(text)
            elif area:
                self.messages.append(area)
            elif text:
                self.messages.append(text)
            elif btn:
                self.commands(btn)
            return redirect(url_for("index"))
        return self.flip
    
    def commands(self, com: str):
        """
        Что делать с командой.
        
        Args:
            com - заданная команда.
        """
        if com == 'clear':
            self.messages = []
        elif com in self.buttons:
            getattr(self, com)()
        elif com in self.user_commands:
            self.multy_execute(self.user_commands[com])
        else:
            self.messages.append(com)
    
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
        self.messages.append(f"Выберите сервопривод. {self._servo_define}/{robot.count_servo-1}.")

    def calibration(self):
        """Калибровка сервоприводов."""
        if not self.chose_servo:
            self.messages.append("Перед калибровкой выберите сервопривод.")
            return None
        elif self.chose_servo == 'head':
            self.messages.append("Сервопривод головы не вставлен.")
            return None
        self._flag_calibration = True
        self._servo_define = None
        self.messages.append(f"Готов к калибровке. Установлено значение - {robot.centers[robot.body[self.chose_servo]]}.")
        self.messages.append("Введите новое значение.")

    def full(self):
        """Включить сервоприводы."""
        robot.full()


    def stand(self):
        """Робот встаёт."""
        robot.stand()
        

    def sleep(self):
        """Выключить все сервоприводы."""
        robot.stop_all()

    def stop(self):
        """Остановка процесса."""
        self._flag_calibration = False
        self._servo_define = None
        self.messages.append("Принудительная остановка процессов.")
    
    def create(self):
        """Создание функции."""
        self.messages.append("")
        self._flag_calibration = False
        self.messages.append("begin function")
        self._flag_create = True
    
    def create_function(self, name, com):
        com = [c.split() for c in com.splitlines()]
        self.multy_execute(com)
        self.user_commands[name] = com
        self.messages.append(f"Функция {name} создана.")
        self._flag_create = False

    def multy_execute(self, commands: list[list[str]]):
        """
        Выполняет несколько комманд.
        
        Args:
            commands - команды
        """
        for command in commands:
            self.messages.append(command)
            if not self.execute(command, True):
                self.messages.append("^^^^Ошибка. Команда не найдена^^^^")
            

    def execute(self, command: list[str], multy: bool = False):
        """
        Выполняет комманды.
        
        Args:
            command - команда
        """ 
        if len(command) < 1:
            self.messages.append("")
        elif command[0] == 'run':
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
                self.messages.append("Ошибка входных параметров для run: run <выбранные сервопривод текстом> <значение>")
                return False
        elif command[0] == 'wait':
            try:
                if len(command) == 2:
                    value = float(command[1])
                    if multy:
                        time.sleep(value) # Заменить на datetime
                    return True
                else:
                    raise IndexError
            except (ValueError, TypeError, IndexError):
                self.messages.append("Ошибка входных параметров для run: run <выбранные сервопривод текстом> <значение>")
                return False
        else:
            self.messages.append("Ошибка. Команда не найдена.")
            return False
        

    def servo_run(self, value: int):
        """Включение сервопривода"""
        if self.chose_servo is None:
            self.messages.append("Сервопривод не выбран.")
            return None
        robot.servo_run_name(self.chose_servo, value)
        if robot.servo_run_name(self.chose_servo, value) is not None and self.debug:
            self.messages.append(robot.servo_run_name(self.chose_servo, value))

    def run(self):
        """Запуск сайта."""
        self.app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    site = Site()
    site.run()
