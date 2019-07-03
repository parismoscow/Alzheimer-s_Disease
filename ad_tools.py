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


def cleanup_data(df, drop):
    df = df.replace(r'^\s*$', np.nan, regex=True)
#   df.fillna(value=0, inplace=True)
    if drop:
        df.dropna(inplace=True)
    else:
        df.fillna(value=0, inplace=True)

    if 'ABETA_UPENNBIOMK9_04_19_17' in df:
        df.loc[df['ABETA_UPENNBIOMK9_04_19_17'] ==
               '<200', 'ABETA_UPENNBIOMK9_04_19_17'] = 199
        df['ABETA_UPENNBIOMK9_04_19_17'] = df['ABETA_UPENNBIOMK9_04_19_17'].astype(
            float)
    if 'TAU_UPENNBIOMK9_04_19_17' in df:
        df.loc[df['TAU_UPENNBIOMK9_04_19_17'] ==
               '>1300', 'TAU_UPENNBIOMK9_04_19_17'] = 1301
        df.loc[df['TAU_UPENNBIOMK9_04_19_17'] ==
               '<80', 'TAU_UPENNBIOMK9_04_19_17'] = 79
        df['TAU_UPENNBIOMK9_04_19_17'] = df['TAU_UPENNBIOMK9_04_19_17'].astype(
            float)
    if 'PTAU_UPENNBIOMK9_04_19_17' in df:
        df.loc[df['PTAU_UPENNBIOMK9_04_19_17'] ==
               '>120', 'PTAU_UPENNBIOMK9_04_19_17'] = 121
        df.loc[df['PTAU_UPENNBIOMK9_04_19_17'] ==
               '<8', 'PTAU_UPENNBIOMK9_04_19_17'] = 7
        df['PTAU_UPENNBIOMK9_04_19_17'] = df['PTAU_UPENNBIOMK9_04_19_17'].astype(
            float)

    # Remove diagnosis changes that are unlikely
#   df = df.loc[(df['final_DX'] == 'MCI') | (df['final_DX'] == 'Dementia') | (df['final_DX'] == 'NL')]
    df = df.loc[(df['DX'] == 'MCI') | (
        df['DX'] == 'Dementia') | (df['DX'] == 'NL')]

#   df = df.loc[(df['DXCHANGE'] == 1) | (df['DXCHANGE'] == 2) | (df['DXCHANGE'] == 3) | (df['DXCHANGE'] == 4) | (df['DXCHANGE'] == 5)]

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
    # print("returning tag: ", tag)
    return tag


def get_data(dataset_name, oversampling, scaling, prediction):
    # print("returning data from ", dataset_name,
    #       'with ', oversampling, 'and', scaling)
    filename = 'Data/' + dataset_name + '.csv'
    print('returning ', filename)
    df = pd.read_csv(filename)
    X, y = populate_X_y(df, prediction, ["PTRACCAT", "PTETHCAT", "PTGENDER"])
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    X_train, X_test = scale_features(scaling, X_train, X_test)
    X_train, y_train = oversample(oversampling, X_train, y_train)
    return X_train, X_test, y_train, y_test


def load_model(model_name):
    model = pickle.load(open('Models/' + model_name + ".sav", 'rb'))
    return model


def evaluate_model(model, X_test, y_test):
    # print("in evaluate model, received ", X_test, y_test)
    score = round(model.score(X_test, y_test), 4)
    predictions = model.predict(X_test)
    confmatrix = confusion_matrix(y_test, predictions)
    roc_auc, fpr, tpr = return_roc(y_test, model.predict_proba(X_test))

    metrics = {
        'score': score,
        'confmatrix': confmatrix,
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


def run_model(model_name, X_train, X_test, y_train, y_test):
    if 'svc' in model_name.lower():
        model = SVC(kernel='linear')

    elif 'random forest' in model_name.lower():
        model = RandomForestClassifier(n_estimators=200)

    elif 'logistic regression' in model_name.lower():
        model = LogisticRegression()

    model.fit(X_train, y_train)
    print("*************", model_name, "*************\n",
          "\nScore is: ", model.score(X_test, y_test), "\n")
    predictions = model.predict(X_test)
    print("\nConfusion matrix\n", confusion_matrix(y_test, predictions))
    print("\n", classification_report(y_test, predictions))
#   print("\n", classification_report(y_test, predictions, target_names=["NL to NL", "MCI to MCI", "AD to AD", "NL to MCI", "MCI to AD" ]))

    return model
