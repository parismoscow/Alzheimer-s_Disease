from flask import Flask, jsonify, render_template, request
import ad_tools as adt


app = Flask(__name__)


@app.route("/index")
def diseases():
    return render_template("index.html")


@app.route('/models', methods=['POST', 'GET'])
def models():
    result = {}
    model_name = ""
    metrics = {}
    if request.method == 'POST':
        result = request.form
        oversampling = result['oversampling']
        scaling = result['scaling']
        prediction = result['prediction']
        model_name = adt.return_model_name(result)
        dataset_name = adt.get_dataset_name(result)
        X_train, X_test, y_train, y_test = adt.get_data(
            dataset_name, oversampling, scaling, prediction)
        model = adt.load_model(model_name)
        metrics = adt.evaluate_model(model, X_test, y_test)
    return render_template("models.html", metrics=metrics)
    # return render_template("models.html", result=result, model_name=model_name, metrics=metrics)

    # else:
    #     return render_template("models.html")
    # else:


@app.route("/data")
def data():
    return render_template("data.html")


@app.route("/resources")
def resources():
    return render_template("resources.html")


@app.route("/treatment")
def treatment():
    return render_template("treatment.html")


# @app.route("/models")
# def models():
#     return render_template("models.html")


if __name__ == "__main__":
    app.run(debug=True)
