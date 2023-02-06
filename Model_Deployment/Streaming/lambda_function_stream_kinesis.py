import os
import json
import base64
import boto3
import os
from mlflow.tracking import MlflowClient
import mlflow
import pickle
import xgboost as xgb

#RUN_ID = '09ff5d86828e454782de9ee0deb5cf7b'

kinesis_client = boto3.client('kinesis')
PREDICTION_STREAM_NAME = os.getenv('PREDICTION_STREAM_NAME', 'churn-prediction')

def load_model_from_mlflow():
    RUN_ID = input("Enter the Latest Run ID : ")
    logged_model_in_s3 = f's3://mlops-s3-bucket-1/22/{RUN_ID}/artifacts/models_mlflow'
    ## convering into xgboost model
    xgboost_model = mlflow.xgboost.load_model(logged_model_in_s3)
    with open('../Experiment_Tracking/models/preprocessor.b', 'rb') as f_in:
        dv = pickle.load(f_in)
    return xgboost_model, dv


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




def lambda_handler(event, context):
    predictions = []
    xgboost_model, dv = load_model_from_mlflow()

    for record in event['Records']:
        encoded_data = record['kinesis']['data']
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        churn_event = json.loads(decoded_data)
        #print(f"Churn Event -> {churn_event}")
        churn = churn_event['churn']
        #print(f"CHURN -> {churn}")
        churn_id = churn_event['churn_id']
        #print(f"CHURN ID -> {churn_id}")
        features = prepare_features(churn)
        #print(f"churn features -> {features}")

        X = dv.transform(features)
        #print(f"X -> {X}")
        model_features = dv.get_feature_names_out()
        #print(f"Model Features -> {model_features}")
        dval = xgb.DMatrix(X, feature_names=model_features)
        #print(f"DVAL -> {dval}")
        y_pred = xgboost_model.predict(dval)
        # changing numpy float to float
        y_pred = y_pred.tolist()
        # print(y_pred[0])
        prediction = y_pred[0]
        #print(prediction)

        prediction_event = {
            'model': 'churn_prediction_model',
            'version': 123,
            'prediction': {
                'churn': prediction,
                'churn_id': churn_id
            }
        }

        kinesis_client.put_record(
            StreamName=PREDICTION_STREAM_NAME,
            Data=json.dumps(prediction_event),
            PartitionKey=str(churn_id)
        )

        predictions.append(prediction_event)

    # TODO implement
    return {
        'predictions': predictions
    }
