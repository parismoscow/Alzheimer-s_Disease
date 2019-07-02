from flask import Flask, jsonify, render_template

app = Flask(__name__)


@app.route("/index")
def diseases():
    return render_template("index.html")

@app.route("/data")
def data():
    return render_template("data.html")

@app.route("/resources")
def resources():
    return render_template("resources.html")

@app.route("/treatment")
def treatment():
    return render_template("treatment.html")

@app.route("/models")
def models():
    return render_template("models.html")

if __name__ == "__main__":
    app.run(debug=True)