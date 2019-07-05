# -*- coding: utf-8 -*-
"""AD_tools.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PZ47ZLkJqk74zJrgv4j_zgZYA0ozXeSL
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE
from imblearn.over_sampling import RandomOverSampler
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from collections import Counter
import pickle
from sklearn.preprocessing import label_binarize
from sklearn.metrics import roc_curve, auc
from os import path

debug = 1


def cleanup_data(dataset_name, df, drop, prediction):
    if debug:
        print("in clean_data 1")
    df = df.replace(r'^\s*$', np.nan, regex=True)
    print("in clean_data 2")

    if drop:
        df.dropna(inplace=True)
    else:
        df.fillna(value=0, inplace=True)
    print("in clean_data 3")

    if 'ABETA_UPENNBIOMK9_04_19_17' in df:
        if debug:
            print("in clean_data 4")
        df.loc[df['ABETA_UPENNBIOMK9_04_19_17']
               == '<200', 'ABETA_UPENNBIOMK9_04_19_17'] = 199
        if debug:
            print("in clean_data 5")

        df['ABETA_UPENNBIOMK9_04_19_17'] = df['ABETA_UPENNBIOMK9_04_19_17'].astype(
            float)

    # if 'ABETA_UPENNBIOMK9_04_19_17' in df:
    #     if debug:
    #         print("in clean_data 4")
    #     df.loc[df['ABETA_UPENNBIOMK9_04_19_17']
    #            == '<200', 'ABETA_UPENNBIOMK9_04_19_17'] = 199
        # df['ABETA_UPENNBIOMK9_04_19_17'] = df['ABETA_UPENNBIOMK9_04_19_17'].astype(
        #     float)

    if 'TAU_UPENNBIOMK9_04_19_17' in df:
        df.loc[df['TAU_UPENNBIOMK9_04_19_17']
               == '>1300', 'TAU_UPENNBIOMK9_04_19_17'] = 1301
        df.loc[df['TAU_UPENNBIOMK9_04_19_17']
               == '<80', 'TAU_UPENNBIOMK9_04_19_17'] = 79
        df['TAU_UPENNBIOMK9_04_19_17'] = df['TAU_UPENNBIOMK9_04_19_17'].astype(
            float)
    if 'PTAU_UPENNBIOMK9_04_19_17' in df:
        df.loc[df['PTAU_UPENNBIOMK9_04_19_17']
               == '>120', 'PTAU_UPENNBIOMK9_04_19_17'] = 121
        df.loc[df['PTAU_UPENNBIOMK9_04_19_17']
               == '<8', 'PTAU_UPENNBIOMK9_04_19_17'] = 7
        df['PTAU_UPENNBIOMK9_04_19_17'] = df['PTAU_UPENNBIOMK9_04_19_17'].astype(
            float)
    print("in clean_data 4")

    # # create feature selection
    # columns = ['PTID']
    # columns.append(prediction)
    # dataset_lower = dataset_name.lower()
    # if 'demographic' in dataset_lower:
    #     columns = columns + ['AGE', 'PTRACCAT',
    #                          'PTETHCAT', 'PTGENDER', 'PTEDUCAT']
    # if 'apoe4' in dataset_lower:
    #     columns.append('APOE4')
    # if 'cogtest' in dataset_lower:
    #     columns = columns + ['CDRSB', 'ADAS11',
    #                          'MMSE', 'ADAS13', 'RAVLT_immediate']
    #
    # # if 'mripct' in dataset_lower:
    # #     columns = columns + ['Ventricles', 'Hippocampus',
    # #                          'WholeBrain', 'Entorhinal', 'MidTemp',
    # #
    # if 'mripct' in dataset_lower:
    #     columns = columns + ['Ventricles', 'Hippocampus',
    #                          'WholeBrain', 'Entorhinal', 'MidTemp',
    #                          'pct_Ventricles', 'pct_Hippocampus',
    #                          'pct_WholeBrain', 'pct_Entorhinal', 'pct_MidTemp']
    # if 'pet' in dataset_lower:
    #     columns = columns + ['FDG', 'AV45']
    # if 'csv' in dataset_lower:
    #     columns = columns + ['ABETA_UPENNBIOMK9_04_19_17',
    #                          'TAU_UPENNBIOMK9_04_19_17', 'PTAU_UPENNBIOMK9_04_19_17']
    # if debug:
    #     print("grabbing columns: ", columns)
    # df = df.loc[:, columns]
    if debug:
        print("df preview1: ", df.head(2), " length: ", df.shape[0])
    if prediction == 'DX':
        df = df.loc[(df['DX'] == 'MCI') | (
            df['DX'] == 'Dementia') | (df['DX'] == 'NL')]
    # elif prediction == 'final_DX':
    #     df = df.loc[(df['final_DX'] == 'MCI') | (
    #         df['final_DX'] == 'Dementia') | (df['final_DX'] == 'NL')]
    if debug:
        print("df preview2: ", df.head(2))

    # Remove diagnosis that are very infrequent

    if debug:
        print("in cleanup_data returning df: ", df.head(2))
    return df


def return_model_name(dict):
    tag_elements = []
    for key in dict.keys():
        tag_elements.append(dict[key])
    tag = '_'.join(tag_elements)
    return tag


def get_dataset_name(dict):
    tag_elements = []
    for key in dict.keys():
        if (key != 'model') and (key != 'oversampling') and (key != 'scaling'):
            tag_elements.append(dict[key])
    tag = '_'.join(tag_elements)
    return tag


def get_data(dataset_name, oversampling, scaling, prediction):
    save = 0
    if debug:
        print("in get_data using dataset:", dataset_name)
    # if prediction == 'DX':
    raw_data = 'Data/raw_data_subset.csv'
    # elif prediction == 'final_DX':
    #     raw_data = 'Data/TADPOLE_D1_D2_finalDX.csv'

    filename = 'Data/' + dataset_name + '.csv'
    if path.isfile(filename):
        if debug:
            print("dataset already exists")
        df = pd.read_csv(filename)
    else:
        # read original raw file, cleanup data
        if debug:
            print("dataset does not exist, creating from ", raw_data)
        try:
            df = pd.read_csv(raw_data)
            drop = True
            if debug:
                print("before cleanup_data")
            df = cleanup_data(dataset_name, df, drop, prediction)
            df.to_csv(filename, index=False)
            # df.to_csv("TADPOLE_subset_raw.csv", index=False)
        except Exception as e:
            if debug:
                print("in get_data, error: ", e)
    if debug:
        print("in get_data before populate_X_y")
    X, y = populate_X_y(df, prediction, ["PTRACCAT", "PTETHCAT", "PTGENDER"])
    if debug:
        print("in get_data after populate_X_y, X length: ", len(X))
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    if debug:
        print("in get_data after train test split")
    X_train, X_test = scale_features(scaling, X_train, X_test)
    if debug:
        print("in get_data after scale fealtures")
    X_train, y_train = oversample(oversampling, X_train, y_train)
    if debug:
        print("in get_data after oversample")
    return X_train, X_test, y_train, y_test


def load_model(model_name):
    print("Looking for model: ", model_name)
    model = pickle.load(open('Models/' + model_name + ".sav", 'rb'))
    return model


def eval_and_report(model, X_test, y_test, size):
    try:
        metrics = evaluate_model(model, X_test, y_test)
        class_report = metrics['class_report']
        score = metrics['score']
        # size = len(X_train)
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
    except Exception as e:
        print("inside eval_and_report, issue with model", e)
        response = {
            'success': 0
        }
    # print("returning to js: ", jsonify(response))
    return (response)


def evaluate_model(model, X_test, y_test):
    # print("in evaluate model, received ", X_test, y_test)
    score = round(model.score(X_test, y_test), 4)
    predictions = model.predict(X_test)
    confmatrix = confusion_matrix(y_test, predictions)
    class_report = classification_report(y_test, predictions)
    roc_auc, fpr, tpr = return_roc(y_test, model.predict_proba(X_test))

    metrics = {
        'score': score,
        'class_report': class_report,
        'roc_auc': roc_auc,
        'fpr': fpr,
        'tpr': tpr
    }
    return metrics


def return_roc(y_test, y_score):
    classes = ['Dementia', 'MCI', 'NL']
    y_bin = label_binarize(y_test, classes=['Dementia', 'MCI', 'NL'])
    n_classes = 3
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_bin[:, i], y_score[:, i])
        roc_auc[i] = round(auc(fpr[i], tpr[i]), 4)
        fpr[i] = fpr[i].tolist()
        tpr[i] = tpr[i].tolist()
        # roc_auc[i]
    return roc_auc, fpr, tpr


def add_pct_change(df, feature_list):
    for feature in feature_list:
        new_column = "pct_" + feature
#     df[feature].loc[df[feature] == 0][feature] = 1
#     if divisor != 0:
        df[new_column] = 100 * (1 - df.iloc[0][feature] / df[feature])
    return df


def add_sum_column(df):
    df['pct_sum'] = df['pct_Hippocampus'] + df['pct_WholeBrain'] + \
        df['pct_Entorhinal'] + df['pct_MidTemp']
    return df


def add_final_dx_column(df):
    for dx in ['Dementia', 'MCI', "NL"]:
        if dx in df['DX'].values:
            df['final_DX'] = dx
            return df
    return df


def show_data(df, category):
    print("There are ", df[category].count(), " records")
    print("Category breakdown \n", df[category].value_counts())


def populate_X_y(df, y_cat, encode_list):
    y = df[y_cat]
    X = df.drop(columns=[y_cat, 'PTID'])
#   X = df.drop(columns=[y_cat, 'PTID'])
# todo replace following line with one above
#   X = df.drop(columns=[y_cat])
    label_encoder = LabelEncoder()
    for label in encode_list:
        if label in X:
            encode = X[label]
            label_encoder.fit(encode)
            X[label] = label_encoder.transform(encode)

    return X, y


def myPCA(X_train, X_test):
    pca = PCA()
    X_train = pca.fit_transform(X_train)
    X_test = pca.transform(X_test)
    return X_train, X_test


def scale_features(scaler, X_train, X_test):
    if scaler == 'minmax':
        X_train = MinMaxScaler().fit(X_train).transform(X_train)
        X_test = MinMaxScaler().fit(X_test).transform(X_test)
    elif scaler == 'standard':
        X_train = StandardScaler().fit(X_train).transform(X_train)
        X_test = StandardScaler().fit(X_test).transform(X_test)

    return X_train, X_test


def oversample(alg, X_train, y_train):
    # print('in oversample got ', X_train, y_train)
    if alg == 'smote':
        smt = SMOTE()
        X_train, y_train = smt.fit_sample(X_train, y_train)
        # print('Resampled dataset shape %s' % Counter(y_train))
        return X_train, y_train
    if alg == 'random':
        ros = RandomOverSampler(random_state=42)
        X_train, y_train = ros.fit_sample(X_train, y_train)
        # print('Resampled dataset shape %s' % Counter(y_train))
        return X_train, y_train

# def save_model()


def train_model(model_name, X_train, y_train):

    print("Training new model: ", model_name)
    if 'svc' in model_name.lower():
        model = SVC(kernel='linear', probability=True)

    elif 'random forest' in model_name.lower() or 'rf' in model_name.lower():
        model = RandomForestClassifier(n_estimators=200)

    elif 'logistic regression' in model_name.lower() or 'lr' in model_name.lower():
        model = LogisticRegression()

    # print("start training model...")
    model.fit(X_train, y_train)
#     print("*************", model_name, "*************\n",
#           "\nScore is: ", model.score(X_test, y_test), "\n")
#     predictions = model.predict(X_test)
#     print("\nConfusion matrix\n", confusion_matrix(y_test, predictions))
#     print("\n", classification_report(y_test, predictions))
# #   print("\n", classification_report(y_test, predictions, target_names=["NL to NL", "MCI to MCI", "AD to AD", "NL to MCI", "MCI to AD" ]))
    # print("finished training model...")

    return model
