import pickle
import csv
import time
import ast
import operator
import lgpio

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,

    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
}

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
            "while": self.while_func,
            "if": self.if_func,
            "print": self.print_func,
        }
        self.user_commands = dict()
        self.temp_name = 0
        self.chose_servo = None
        self._flag_calibration = False
        self._flag_create = False
        self._flag_edit = False
        self._servo_define = None
        self.stop_execution = False
        self.function_name_for_push = None
        self.function_body_for_push = None
        self.variables = {}

        try:
            with open('user_commands.pkl', mode='rb') as file:
                self.user_commands = pickle.load(file)
            for u_c in self.user_commands:
                if str(self.temp_name) in self.user_commands:
                    self.temp_name += 1
                else:
                    break

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

    def post_query(self, text, function_name, function_body, btn, 
                   area, delete_ser_button, edit, action):
        """Post-запрос"""
        if text in self.default_btn_commands:
            print("self.default_btn_commands")
            self.site.messages.append(f"Запущена функция {text}")
            self.default_btn_commands[text]()

        elif text in self.user_commands:
            print("self.user_commands")
            self.site.messages.append(f"Запущена функция {text}")
            self.multi_execute(self.user_commands[text])
        
        elif len(text) > 1:
            if text.split()[0] in self.default_commands:
                print("self.default_commands")
                self.site.messages.append(text)
                self.default_commands[text.split()[0]](text.split())
                return None
        if text == "begin":
            print("begin")
            self.create()
        
        elif function_body != "" and (text == "save" or text == "end" or action == "save"):
            print("сохранение текста в редакторе")
            # сохранение текста в редакторе
            self.function_body_for_push = None
            self.function_name_for_push = None
            if function_name == "" or function_name in list(self.default_btn_commands) + list(self.default_commands) :
                function_name = str(self.temp_name)
                self.temp_name += 1
            self.create_function(function_name, function_body)

        elif text == "save" or action == "save" or (btn == "create" and self._flag_create):
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
                with open('user_commands.pkl', mode='wb') as file:
                    pickle.dump(self.user_commands, file)
            else:
                self.site.messages.append("Ошибка. Функция не найдена.")
        
        elif edit:
            self._flag_edit = True
            self._flag_create = True
            self.function_name_for_push = edit
            self.function_body_for_push = "\n".join(" ".join(u_c) for u_c in self.user_commands[edit])
            self.user_commands.pop(edit)

        elif area:
            print("area пролет")
            self.site.messages.append(area)

        elif text:
            print("text пролет")
            self.site.messages.append(text)

        elif btn in self.default_btn_commands:
            print("btn_self.default_btn_commands")
            self.site.messages.append(f"Запущена функция {btn}")
            self.default_btn_commands[btn]()

        elif btn in self.user_commands:
            print("btn_self.user_commands")
            self.site.messages.append(f"Запущена функция {btn}")
            self.multi_execute(self.user_commands[btn])

        elif btn:
            print("btn пролет")
            self.site.messages.append(btn)
        print("-")

    
    def documentation(self):
        """Документация к командам."""
        commands = [
            "-----------------------------------------",
            "Определить сервопривод как канал:",
            "1) define",
            "2) Выбрать сервопривод",
            "Повторять шаг 2, пока не определится каждый сервопривод",
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

            "Отключить все сервоприводы:",
            "1) sleep",
            "",

            "Принудительно остановить процесс:",
            "1) stop",
            "",

            "-----------------------------------------",
            "Переменные:",
            "a = 10",
            "b = 15.5",
            'text = "Hello"',
            "",

            "Арифметические операции:",
            "+  -  *  /  //  %  **",
            "Пример:",
            "speed = speed + 100",
            "a = (x + y) * 2",
            "",

            "Сравнения:",
            "<   <=   >   >=   ==   !=",
            "",

            "Логические операции:",
            "and   or   not",
            "",

            "Цикл while:",
            "while speed < 2000",
            "    run left 1500",
            "    speed = speed + 100",
            "end",
            "",

            "Условие if:",
            "if speed > 1500",
            '    print "Fast"',
            "else",
            '    print "Slow"',
            "end",
            "",

            "Вывод:",
            "print speed",
            "print speed + 100",
            'print "Hello"',
            "print robot.body",
            "print robot.centers",
            "",

            "Встроенные функции:",
            "abs(x)",
            "min(a, b)",
            "max(a, b)",
            "len(x)",
            "round(x)",
            "",

            "Команда run:",
            "run <сервопривод> <значение>",
            "Пример:",
            "run left_front 1500",
            "",

            "Команда wait:",
            "wait <секунды>",
            "Пример:",
            "wait 0.5",
            "",

            "Пользовательские функции:",
            "ИмяФункции",
            "",
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
                self.site.messages.append("Центр сервопривода откалиброван.")
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
        self.stop_execution = True
        self.site.messages.append("Принудительная остановка процессов.")
    
    def create(self):
        """Создание функции."""
        self.site.messages.append("")
        self._flag_calibration = False
        self.site.messages.append("begin function")
        self._flag_create = True
    
    def create_function(self, name, com):
        com = [c.strip().split() for c in com.splitlines()]
        self.user_commands[name] = com
        if self._flag_edit:
            self.site.messages.append(f"Функция {name} изменена.")
            self._flag_edit = False
        else:
            self.site.messages.append(f"Функция {name} создана.")
        with open('user_commands.pkl', mode='wb') as file:
                pickle.dump(self.user_commands, file)
        self._flag_create = False

    def multi_execute(self, commands: list[list[str]]):
        """
        Выполняет несколько комманд.
        
        Args:
            commands - команды
        """
        self.stop_execution = False
        i = 0

        while i < len(commands):
            lost_i2c = False
            while True:
                if self.stop_execution:
                    return
                try:
                    i = self.multi_execute_in(commands, i)
                    break
                except lgpio.error:
                    if not lost_i2c:
                        self.site.messages.append("Потеряно соединение I2C.")
                        lost_i2c = True
                    self.reconnect()
                    self.site.messages.append("Соединение I2C восстановлено.")

    def reconnect(self):
        while True:
            try:
                self.robot.close()
                self.robot.connect()
                time.sleep(0.5)
                self.robot.setting()

                for ch, value in enumerate(self.robot.pwm):
                    if value is not None:
                        self.robot.servo_run(ch, value)

                return

            except lgpio.error:
                time.sleep(0.2)

    def multi_execute_in(self, commands, i):
        if self.stop_execution:
            return i
        if i >= len(commands):
            return i
        command = commands[i]
        if len(command) > 0:
            if command[0] == "while":
                i = self.while_func(command, commands, i)
            elif command[0] == "if":
                i = self.if_func(command, commands, i)
            else:
                if not self.execute(command):
                    self.site.messages.append(command)
                    self.site.messages.append("^^^^Ошибка. Команда не найдена^^^^")
        return i + 1
            
    def execute(self, command: list[str]):
        """
        Выполняет комманды.
        
        Args:
            command - команда
        """ 
        if self.stop_execution:
            return False
        if not command:
            self.site.messages.append("")
            return True
        elif len(command) > 2 and command[1] in (
            "=", "+=", "-=", "*=", "/=", "//=", "%=", "**="
        ):
            return self.assign(command)
        elif command[0] in self.default_btn_commands:
            self.default_btn_commands[command[0]]()
            return True
        elif command[0] in self.default_commands:
            self.default_commands[command[0]](command)
            return True
        elif command[0] in self.user_commands:
            self.multi_execute(self.user_commands[command[0]])
            return True
        else:
            self.site.messages.append("Ошибка. Команда не найдена.")
            return False
    
    def run(self, command):
        """Запуск сервопривода"""
        try:
            if len(command) == 2:
                self.robot.servo_stop_name(command[1])
                if self.robot.flag_success_stop:
                    return True
                return False
            expr = " ".join(command[2:])
            value = int(self.eval_expr(expr))
            self.robot.servo_run_name(command[1], value)
            if self.robot.flag_success_run:
                return True
            return False
        except (ValueError, TypeError, IndexError):
            self.site.messages.append("Ошибка входных параметров для run: run <выбранные сервопривод текстом> <значение>")
            return False
    
    def wait(self, command):
        """Задержка в секундах"""
        try:
            expr = " ".join(command[1:])
            value = float(self.eval_expr(expr))
            end = time.time() + value
            while time.time() < end:
                if self.stop_execution:
                    return False
                time.sleep(0.02)

            return True
        except (ValueError, TypeError, IndexError):
            self.site.messages.append("Ошибка входных параметров для wait: wait <секунды>")
            return False

    def while_func(self, command, commands, index):
        condition = " ".join(command[1:])
        body = []
        depth = 1
        i = index + 1
        while i < len(commands):
            if not commands[i]:
                i += 1
                continue

            cmd = commands[i][0]
            if cmd in ("while", "if"):
                depth += 1
            elif cmd == "end":
                depth -= 1
                if depth == 0:
                    break
            body.append(commands[i])
            i += 1
        if depth != 0:
            self.site.messages.append("Ошибка. Не найден end.")
            return len(commands)
        while self.eval_expr(condition) and not self.stop_execution:
            self.multi_execute(body)

        return i
    
    def if_func(self, command, commands, index):
        condition = " ".join(command[1:])
        true_body = []
        false_body = []
        body = true_body
        depth = 1
        i = index + 1
        while i < len(commands):
            if not commands[i]:
                i += 1
                continue
            cmd = commands[i][0]
            if cmd in ("while", "if"):
                depth += 1
            elif cmd == "end":
                depth -= 1
                if depth == 0:
                    break
            elif cmd == "else" and depth == 1:
                body = false_body
                i += 1
                continue
            body.append(commands[i])
            i += 1
        if depth != 0:
            self.site.messages.append("Ошибка. Не найден end.")
            return len(commands)
        if self.eval_expr(condition):
            self.multi_execute(true_body)
        else:
            self.multi_execute(false_body)
        return i
    

    def eval_expr(self, expr: str):
        try:
            tree = ast.parse(expr, mode="eval")
            return self._eval(tree.body)
        except SyntaxError as e:
            self.site.messages.append(f"Синтаксическая ошибка в выражении: {expr} – {e}")


    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        
        elif isinstance(node, ast.Attribute):
            obj = self._eval(node.value)
            return getattr(obj, node.attr)
    
        elif isinstance(node, ast.Subscript):
            obj = self._eval(node.value)
            key = self._eval(node.slice)
            return obj[key]

        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval(v) for v in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._eval(v) for v in node.values)
        
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return not self._eval(node.operand)
            elif isinstance(node.op, ast.USub):
                return -self._eval(node.operand)
        
        elif isinstance(node, ast.Call):
            funcs = {
                "abs": abs,
                "min": min,
                "max": max,
                "len": len,
                "round": round,
            }

            func = funcs.get(node.func.id)

            if func is None:
                raise NameError(f"Функция '{node.func.id}' не существует")

            args = [self._eval(arg) for arg in node.args]

            return func(*args)

        elif isinstance(node, ast.Name):
            if node.id == "robot":
                return self.robot
            elif node.id == "site":
                return self.site
            elif node.id in self.robot.body:
                servo = self.robot.body[node.id]
                return self.robot.pwm[servo]
            elif node.id in self.robot.bodypart:
                return tuple(self.robot.pwm[servo] for servo in self.robot.bodypart[node.id])
            elif node.id in self.variables:
                return self.variables[node.id]
            raise NameError(f"Переменная '{node.id}' не существует")

        elif isinstance(node, ast.BinOp):
            return OPS[type(node.op)](
                self._eval(node.left),
                self._eval(node.right)
            )

        elif isinstance(node, ast.Compare):
            left = self._eval(node.left)

            for op, comp in zip(node.ops, node.comparators):
                right = self._eval(comp)

                if not OPS[type(op)](left, right):
                    return False

                left = right

            return True

        else:
            raise Exception(f"Недопустимое выражение: {type(node)}")  
    
    def print_func(self, command):
        expr = " ".join(command[1:])

        try:
            value = self.eval_expr(expr)
        except NameError as e:
            self.site.messages.append(str(e))
            return
        except Exception:
            value = expr

        self.site.messages.append(str(value))


    def assign(self, command):
        try:
            name = command[0]

            if not name.isidentifier():
                raise ValueError("Некорректное имя переменной")

            op = command[1]
            expr = " ".join(command[2:])
            value = self.eval_expr(expr)

            if op == "=":
                self.variables[name] = value

            else:
                if name not in self.variables:
                    raise NameError(f"Переменная '{name}' не существует")

                if op == "+=":
                    self.variables[name] += value
                elif op == "-=":
                    self.variables[name] -= value
                elif op == "*=":
                    self.variables[name] *= value
                elif op == "/=":
                    self.variables[name] /= value
                elif op == "//=":
                    self.variables[name] //= value
                elif op == "%=":
                    self.variables[name] %= value
                elif op == "**=":
                    self.variables[name] **= value

            return True

        except Exception as e:
            self.site.messages.append(f"Ошибка присваивания: {e}")
            return False
