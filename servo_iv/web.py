from flask import Flask, render_template, request, redirect, url_for
from . import robot
import pickle
import time
import csv

class Exit(Exception):
    pass

class Site:
    """Страничка в локальном интернете."""
    def __init__(self):
        self.app = Flask(__name__)
        self.messages = []
        self.buttons = ["documantion", "define", "calibration", "clear"]
        self.chose_servo = None
        self._flag_calibration = False
        self._servo_define = None

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
            self.messages.append(f"Выбран сервопривод: {area}")
            if self._servo_define is not None:
                robot.servo_run(self._servo_define, 1500)
                time.sleep(1)
                robot.servo_run(self._servo_define, 1300)
                time.sleep(1)
                robot.servo_run(self._servo_define, 1800)
                time.sleep(1)
                robot.servo_stop(self._servo_define)
                if area in robot.body.keys():
                    robot.body[area] = self._servo_define
                if self._servo_define == 15:
                    self._servo_define = None
                    with open('define.pkl', mode='wb') as file:
                        pickle.dump(robot.body, file)
            return redirect(url_for("index"))
        
        if request.method == "POST":
            text = request.form.get("text")
            btn = request.form.get("button_click")
            area = request.form.get("area_click")
            if self._flag_calibration and text:
                try:
                    self.messages.append(f"Введено число: {text}")
                    text = int(text)
                    if text == -1:
                        self._flag_calibration = False
                        self.chose_servo = None
                        robot.servo_stop(robot.body[self.chose_servo])
                        self.messages.append("Центр сервопривода откалиброван")
                        raise Exit("Центр сервопривода откалиброван")
                    robot.servo_run(robot.body[self.chose_servo], text)
                    robot.centers[robot.body[self.chose_servo]] = text
                    with open('calibration.csv', mode='w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(robot.centers)
                except (ValueError, TypeError):
                    self.messages.append('Введите целое неотрицательное число')
                except Exit:
                    pass

            elif text in self.buttons:
                self.commands(text)
            elif area:
                self.messages.append(area)
            elif text:
                self.messages.append(text)
            elif btn:
                self.commands(btn)
            return redirect(url_for("index"))

        return render_template(
            "index.html",
            message=self.messages,
            buttons=self.buttons
        )
    
    def commands(self, com: str):
        """
        Что делать с командой.
        
        Args:
            com - заданная команда
        """
        if com == 'clear':
            self.messages = []
        elif com in self.buttons:
            getattr(self, com)()
        else:
            self.messages.append(com)
    
    def documantion(self):
        """Документация к командам."""
        commands = [
            "-----------------------",
            "Определить сервопривод как канал:",
            "1) define",
            "2) Выбрать сервопривод"
            "Повторять шаги, пока не определиться каждый сервопривод",
            "",
            "Калибровка:", 
            "1) Выбрать сервопривод",
            "2) calibration",
            "3) Вводить числа",
            "4) Для завершения ввести -1",
        ]
        self.messages.extend(commands)

    def define(self):
        """Определить сервопривод как канал."""
        self._flag_calibration = False
        if self._servo_define:
            self._servo_define = 0
        else:
            self._servo_define += 1
        self.messages.append(f"Выберите сервопривод. {self._flag_calibration}/15")
        
        

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
        self.messages.append("Готов к калибровке. Введите число")

    def run(self):
        self.app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    site = Site()
    site.run()