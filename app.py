from flask import Flask, jsonify, render_template, request
import ad_tools as adt
import plotly
import json
# from plotly import plotly

app = Flask(__name__)


@app.route("/")
def diseases():
    return render_template("index.html")


@app.route("/getdata/<dict>")
def getdata(dict):
    print("in getdata, received dict ", dict)
    # result = request.form
    result = json.loads(dict)
    print(result)
    oversampling = result['oversampling']
    scaling = result['scaling']
    prediction = result['prediction']
    model_name = adt.return_model_name(result)
    dataset_name = adt.get_dataset_name(result)
    X_train, X_test, y_train, y_test = adt.get_data(
        dataset_name, oversampling, scaling, prediction)
    model = adt.load_model(model_name)
    metrics = adt.evaluate_model(model, X_test, y_test)
    score = metrics['score']
    size = len(X_train)
    data = [
        {"x": metrics['fpr'][0], "y": metrics['tpr']
            [0], "name":'Dementia ROC curve (area:' + str(metrics['roc_auc'][0]) + ')'},
        {"x": metrics['fpr'][1], "y": metrics['tpr'][1],
            "name":'MCI ROC curve (area:' + str(metrics['roc_auc'][1]) + ')'},
        {"x": metrics['fpr'][2], "y": metrics['tpr'][2],
            "name":'NL ROC curve (area:' + str(metrics['roc_auc'][2]) + ')'},
    ]

    layout = {
        'title': 'Score: ' + str(score),
        'xaxis': {
            'title': {
                'text': 'False Positive Rate'
            }
        },
        'yaxis': {
            'title': {
                'text': 'True Positive Rate'
            }
        }
    }

    response = {
        'data': data,
        'score': score,
        'size': size,
        'layout': layout
    }

    # div = plotly.offline.plot(
    #     data, include_plotlyjs=False, output_type='div')

    return jsonify(response)


@app.route('/models', methods=['POST', 'GET'])
def models():
    result = {}
    model_name = ""
    metrics = {}
    data = []
    div = ""
    score = 0
    size = 0

    # if request.method == 'POST':

    # # div = plotly.offline.plot(data, filename='file.html')
    # data = [{
    #     "x": metrics['fpr'][0],
    #     "y": metrics['tpr'][0]}]
    # return render_template("models.html", size=size, score=score, div=div)

    return render_template("models.html")
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
