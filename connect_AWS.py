import os
from tensorflow import keras
import pickle
import connect_supabase
import pandas as pd
import numpy as np


# download the s3 bucket in local railway  environment
os.system('aws s3 sync s3://userdatastrokeprediction .')

# laod the models
ecg_model = keras.models.load_model('ecg_prediction/')
heartDiseaseModel = pickle.load(open(f'heartDiseaseModel', 'rb'))
stroke_models = []
models = os.listdir('stroke prediction models/')
for i in models:
    stroke_models.append(pickle.load(
        open(f'stroke prediction models/{i}', 'rb')))

# fetch the data from supabase using the user_id


def getUserReadings(userId):
    ecgReadings = connect_supabase.getUserReadings(userId)
    ecgReadingsDf = pd.DataFrame(ecgReadings).T
    ecgReadingsDf.columns = list(range(187))
    # print(ecgReadingsDf)
    return ecgReadingsDf


# preprocessing
fullProcessor = pickle.load(open('fullprocessor', 'rb'))

# predict functions


def predict_heart_disease(userID):
    ecgModel = ecg_model
    ecgReadings = getUserReadings(userID)

    prediction = ecgModel.predict(ecgReadings)
    res = np.array(prediction).argmax()
    if res == 0:
        return res
    else:
        heartDiseaseType = heartDiseaseModel.predict(ecgReadings)
        return heartDiseaseType[0]


def predict_stroke(stroke_models, gender, age, hyperTension, predictedHeartDisease, everMarried, workType, residenceType, AGL, BMI, smokinStatus):
    colNames = ['gender', 'age', 'hypertension', 'heart_disease',
                'ever_married', 'work_type', 'Residence_type', 'avg_glucose_level', 'bmi', 'smoking_status']
    data = [[gender, age, hyperTension, predictedHeartDisease,
            everMarried, workType, residenceType, AGL, BMI, smokinStatus]]
    df = pd.DataFrame(columns=colNames, data=data)
    for col in colNames:
        if df[col].dtype == int:
            df[col] = df[col].astype(str)
    processedData = fullProcessor.transform(df)
    stroke_predictions = []
    for model in stroke_models:
        stroke_predictions.append(model.predict_proba(processedData))
    avg = 0
    for i in stroke_predictions:
        avg += i[0][1]
    avg /= 2
    return avg*100
