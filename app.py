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


@app.route("/getdata/<dict>")
def getdata(dict):
    #  remove tree image file
    result = json.loads(dict)
    oversampling = result['oversampling']
    scaling = result['scaling']
    prediction = result['prediction']
    cross_validate = result['cross_validate']
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
    if cross_validate:
        X_train, X_test, y_train, y_test, X_features, X, y = adt.get_data(
            dataset_name, prediction, scaling=scaling, oversampling=oversampling, scale_X=True)
        if debug:
            print("with cv X_train len is: ", len(X_train))
    else:
        X_train, X_test, y_train, y_test, X_features, X, y = adt.get_data(
            dataset_name, prediction, oversampling=oversampling, scaling=scaling)
        if debug:
            print("without cv X_train len is: ", len(X_train))

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

    # if debug:
    #     print("in getdata: y_train: ",  y_train)
    #     print("in getdata: y_test: ",  y_test)

    if cross_validate:
        # get cv_accuracy and pass it to eval_and_report
        cv_accuracy,  precision, recall, f1 = adt.cross_validate(
            model_name, X, y)
        response = adt.eval_and_report(
            model, X_test, y_test, len(X_train), X_features, X, y, cv_accuracy)
    else:
        response = adt.eval_and_report(
            model, X_test, y_test, len(X_train), X_features, X, y)

    return jsonify(response)


@app.route('/methodology')
def methodology():
    return render_template('methodology.html')


@app.route('/models', methods=['POST', 'GET'])
def models():
    return render_template("models.html")

#
# @app.route("/data")
# def data():
#     return render_template("data.html")


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
