from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

messages = []

@app.route("/", methods=["GET", "POST"])
def index():
    global messages

    if request.method == "POST":
        text = request.form.get("text")
        if text:
            messages.append(text)
        return redirect(url_for("index"))

    return render_template(
        "index.html",
        message=messages,
        buttons=["Button 1", "Button 2", "Button 3"]
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)