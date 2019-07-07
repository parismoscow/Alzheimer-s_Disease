from flask import Flask, jsonify, render_template, request
import ad_tools as adt
import plotly
import json
# from plotly import plotly

app = Flask(__name__)

debug = 1


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
    #  remove tree image file
    result = json.loads(dict)
    oversampling = result['oversampling']
    scaling = result['scaling']
    prediction = result['prediction']
    response = {}
    model_name = adt.return_model_name(result)
    dataset_name = adt.get_dataset_name(result)

    try:
        # if data does not exist create a new dataset
        if not adt.dataset_exists(dataset_name):
            adt.create_new_dataset(dataset_name, prediction)
    except Exception as e:
        if debug:
            print("in getdata, could not generate new data: ", e)
        response['success'] = -1
        response['error'] = str(e)
        return jsonify(response)

    # populate X and y, split, oversample, scale data
    X_train, X_test, y_train, y_test, X_features = adt.get_data(
        dataset_name, oversampling, scaling, prediction)

    try:
        # if model doesn't exist, train new model
        if not adt.model_exists(model_name):
            adt.train_model(model_name, X_train, y_train)
    except Exception as e:
        if debug:
            print("in getdata, could not train new model: ", e)
        response['success'] = -2
        response['error'] = str(e)
        return jsonify(response)

    model = adt.load_model(model_name)
    metrics = adt.evaluate_model(model, X_test, y_test, X_features)
    response = adt.eval_and_report(
        model, X_test, y_test, len(X_train), X_features)

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


@app.route("/treeimage")
def treeimage():
    return render_template("treeimage.html")


@app.route("/demographics")
def demograhpics():
    return render_template("demographics.html")


@app.route("/treatment")
def treatment():
    return render_template("treatment.html")


if __name__ == "__main__":
    app.run(debug=True)
