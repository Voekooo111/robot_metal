from flask import Flask, render_template, request, redirect, url_for

class Site:
    def __init__(self):
        self.app = Flask(__name__)
        self.messages = []
        self.buttons = ["Hello", "clear"]

        self.app.add_url_rule(
            "/",
            endpoint="index",
            view_func=self.index,
            methods=["GET", "POST"]
        )

    def index(self):
        # Клик по изображению
        area = request.args.get("area")
        if area:
            self.messages.append(area)
            return redirect(url_for("index"))
        
        if request.method == "POST":
            text = request.form.get("text")
            btn = request.form.get("button_click")
            area = request.form.get("area_click")
            if area:
                self.messages.append(area)
            elif text:
                self.messages.append(text)
            elif btn:
                if btn == 'clear':
                    self.messages = []
                else:
                    self.messages.append(btn)
            return redirect(url_for("index"))

        return render_template(
            "index.html",
            message=self.messages,
            buttons=self.buttons
        )

if __name__ == "__main__":
    site = Site()
    site.app.run(host="0.0.0.0", port=5000, debug=True)