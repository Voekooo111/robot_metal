from flask import Flask, render_template, request, redirect, url_for


class Site:
    """Страничка в локальном интернете."""
    def __init__(self, ):
        self.app = Flask(__name__)
        self.messages = []
        self.debug = True

        self.app.add_url_rule(
            "/",
            endpoint="index",
            view_func=self.index,
            methods=["GET", "POST"]
        )

    def bind(self, robot, commands):
        self.robot = robot
        self.commands = commands

    def index(self):
        """Главная страница."""
        area = request.args.get("area")
        if area:
            self.commands.area_click(area)
            return redirect(url_for("index"))

        if request.method == "POST":
            text = request.form.get("text")
            function_name = request.form.get("function_name")
            function_body = request.form.get("function_body")
            btn = request.form.get("button_click")
            area = request.form.get("area_click")
            delete_ser_button = request.form.get("delete")
            self.commands.post_query(text, function_name, function_body, btn, area, delete_ser_button)
            return redirect(url_for("index"))
        
        return render_template(
            "index.html",
            message = self.messages,
            buttons = list(self.commands.default_btn_commands),
            user_buttons = list(self.commands.user_commands),
            flag_calibration = self.commands._flag_calibration,
            flag_create = self.commands._flag_create,
            robot_words = list(self.commands.default_commands),
            robot_parts = list(self.robot.bodypart) + list(self.robot.body),
        )

    def run(self):
        """Запуск сайта."""
        self.app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    site = Site()
    site.run()
