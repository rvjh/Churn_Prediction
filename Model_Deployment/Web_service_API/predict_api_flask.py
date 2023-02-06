import os
import requests
from flask import Flask, jsonify, request
from mlflow.tracking import MlflowClient
import xgboost as xgb
import mlflow
import pickle
import json


#RUN_ID = '09ff5d86828e454782de9ee0deb5cf7b'

app = Flask('churn-prediction')

# GET payload example:
    # {
    #   "customer_age": 100,
    #   "gender": "F"",
    #   "dependent_count": 2,
    #   "education_level": 2,
    #   "marital_status": "married",
    #   "income_category": 2,
    #   "card_category": "blue",
    #   "months_on_book": 6,
    #   "total_relationship_count": 3,
    #   "credit_limit": 4000,
    #   "total_revolving_bal": 2500
    # }

def prepare_features(input):
    features = {
        'customer_age': input['customer_age'],
        'gender': input['gender'],
        'dependent_count': input['dependent_count'],
        'education_level': input['education_level'],
        'marital_status': input['marital_status'],
        'income_category': input['income_category'],
        'card_category': input['card_category'],
        'months_on_book': input['months_on_book'],
        'total_relationship_count': input['total_relationship_count'],
        'credit_limit': float(input['credit_limit']),
        'total_revolving_bal': input['total_revolving_bal']
    }
    return features

def flask_api_load_model_from_mlflow():
    RUN_ID = input("Enter the Latest Run ID : ")
    print("Loading Model from cloud storage ......")
    logged_model_in_s3 = f's3://mlops-s3-bucket-1/22/{RUN_ID}/artifacts/models_mlflow'
    print(f"Model Loaded Successfully. Model details : {logged_model_in_s3}")
    ## convering into xgboost model
    print("Converting Model Format to XGBoost Format")
    xgboost_model = mlflow.xgboost.load_model(logged_model_in_s3)
    print(f"Model Converted Successfully. Details : {xgboost_model}")
    print("Loading Dict-Vectorizer.....from cloud storage")
    with open('Experiment_Tracking/models/preprocessor.b', 'rb') as f_in:
        dv = pickle.load(f_in)
    print("Model and Dict-Vectorizer Loaded Successfully.")
    return xgboost_model, dv, RUN_ID

def predict(dicts):
    xgboost_model, dv, RUN_ID = flask_api_load_model_from_mlflow()
    X = dv.transform(dicts)
    #print(X)
    features = dv.get_feature_names_out()
    #print(features)
    # print(f'features={features}')
    dval = xgb.DMatrix(X, feature_names=features)
    #print(dval)
    y_pred = xgboost_model.predict(dval)
    #print(y_pred[0])
    return y_pred[0] , RUN_ID


@app.route('/predict',methods=['POST'])
def predict_endpoint():
    input_value = request.get_json()
    features = prepare_features(input_value)
    pred, RUN_ID = predict(features)
    #changing numpy float to float
    pred = pred.tolist()
    #print(f"prediction : {pred} and RUN ID : {RUN_ID}")
    print(type(pred))
    result = {
        'churn chance': pred,
        'model_run_id': RUN_ID
    }
    return jsonify(result)


if __name__ == "__main__":
    print("App starting .....")
    app.run(debug=True, host='0.0.0.0', port=9696)
