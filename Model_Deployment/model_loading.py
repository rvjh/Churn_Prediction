import os

from mlflow.tracking import MlflowClient
import mlflow
import pickle

#RUN_ID = '09ff5d86828e454782de9ee0deb5cf7b'


def load_model_from_mlflow():
    RUN_ID = input("Enter the Latest Run ID : ")
    print("Loading Model from cloud storage ......")
    logged_model_in_s3 = f's3://mlops-s3-bucket-1/22/{RUN_ID}/artifacts/models_mlflow'
    #model_new = mlflow.pyfunc.load_model(logged_model_in_s3)

    print(f"Model Loaded Successfully. Model details : {logged_model_in_s3}")

    ## convering into xgboost model
    print("Converting Model Format to XGBoost Format")
    xgboost_model = mlflow.xgboost.load_model(logged_model_in_s3)

    print(f"Model Converted Successfully. Details : {xgboost_model}")
    print("Loading Dict-Vectorizer.....from cloud storage")

    with open('Experiment_Tracking/models/preprocessor.b', 'rb') as f_in:
        dv = pickle.load(f_in)

    print("Model and Dict-Vectorizer Loaded Successfully.")
    return xgboost_model, dv
