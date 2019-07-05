from flask import Flask, jsonify, render_template, request
import ad_tools as adt
import plotly
import json
# from plotly import plotly

app = Flask(__name__)


@app.route("/")
def diseases():
    return render_template("index.html")


@app.route("/newmodel/<dict>")
def newmodel(dict):
    dict = json.loads(dict)
    oversampling = dict['oversampling']
    scaling = dict['scaling']
    prediction = dict['prediction']
    model_name = dict['model']

    # check if data is available
    dataset_name = adt.get_dataset_name(dict)
    try:
        X_train, X_test, y_train, y_test = adt.get_data(
            dataset_name, oversampling, scaling, prediction)
    except:
        # if not call to /generatedataset
        # print(dataset_name, " is not available")
        response = {
            'success': -1
        }
        return jsonify(response)

    scaling = dict['scaling']
    oversampling = dict['oversampling']
    # if data available, scale if necessary
    if scaling:
        X_train, X_test = adt.scale_features(scaling, X_train, X_test)
    # check if oversampling is needed
    if oversampling:
        adt.oversample(oversampling, X_train, y_train)
    model_name = dict['model']
    # train new model
    try:
        model = adt.train_model(model_name, X_train, y_train)
    except Exception as e:
        print("issue with new model")
        response = {
            'success': 0,
            'error': str(e)
        }
        return jsonify(response)

    response = adt.eval_and_report(model, X_test, y_test, len(X_train))
    # response['size'] = len(X_train)
    return jsonify(response)
    # save model


@app.route("/getdata/<dict>")
def getdata(dict):
    success = 0
    result = json.loads(dict)
    oversampling = result['oversampling']
    scaling = result['scaling']
    prediction = result['prediction']
    model_name = adt.return_model_name(result)
    dataset_name = adt.get_dataset_name(result)

    try:
        X_train, X_test, y_train, y_test = adt.get_data(
            dataset_name, oversampling, scaling, prediction)
        model = adt.load_model(model_name)
        metrics = adt.evaluate_model(model, X_test, y_test)
        class_report = metrics['class_report']
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
            'title': {
                'text': 'Score: ' + str(score) + '<br>Training set size: ' + str(size)
            },
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
            'class_report': class_report,
            'size': size,
            'layout': layout,
            'success': 1
        }
    except:
        response = {
            'success': 0
        }

    return jsonify(response)


@app.route('/models', methods=['POST', 'GET'])
def models():
    return render_template("models.html")


@app.route("/data")
def data():
    return render_template("data.html")


@app.route("/resources")
def resources():
    return render_template("resources.html")


@app.route("/demographics")
def demograhpics():
    return render_template("demograhpics.html")


@app.route("/treatment")
def treatment():
    return render_template("treatment.html")


if __name__ == "__main__":
    app.run(debug=True)
