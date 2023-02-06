import os
import requests
from flask import Flask, jsonify,request
from mlflow.tracking import MlflowClient
import xgboost as xgb
import mlflow
import pickle
import json
#from Model_Deployment.model_loading import load_model_from_mlflow

churn_input = {
    'customer_age': 100,
    'gender' : 'F',
    'dependent_count' : 2,
    'education_level': 2,
    'marital_status': 'married',
    'income_category': 2,
    'card_category': 'blue',
    'months_on_book': 6,
    'total_relationship_count': 3,
    'credit_limit': float(4000),
    'total_revolving_bal': 2500
}

#headerInfo = {'Content-Type': 'application/json;charset=UTF-8'}

#churn_input = get_input_features_for_api()

url = 'http://localhost:9696/predict'
response = requests.post(url, json=churn_input)

print(response.json())
