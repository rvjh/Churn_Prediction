import os
import argparse
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.feature_extraction import DictVectorizer
from sklearn import metrics
import mlflow
import pickle
from hyperopt import hp
from hyperopt.pyll import scope
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from mlflow.tracking import MlflowClient
from mlflow.entities import ViewType


def read_dataframe(filepath):
    df = pd.read_csv(filepath)
    return df


def preparing_dataframe(filepath):
    df = read_dataframe(filepath)

    y_column = "active_customer"
    train_columns = ["customer_age",
                     "gender",
                     "dependent_count",
                     "education_level",
                     "marital_status",
                     "income_category",
                     "card_category",
                     "months_on_book",
                     "total_relationship_count",
                     "credit_limit",
                     "total_revolving_bal"]
    df_to_split = df[train_columns + [y_column]]
    return df_to_split, y_column


def split_dataFrame(filepath):
    df_to_split, y_column = preparing_dataframe(filepath)

    df_full_train, df_test = train_test_split(df_to_split, test_size=0.2, random_state=11)
    df_train, df_val = train_test_split(df_full_train, test_size=0.25, random_state=11)

    df_full_train = df_full_train.reset_index(drop=True)
    df_train = df_train.reset_index(drop=True)
    df_val = df_val.reset_index(drop=True)
    df_test = df_test.reset_index(drop=True)

    y_full_train = df_full_train[y_column]
    y_train = df_train[y_column]
    y_val = df_val[y_column]
    y_test = df_test[y_column]

    del df_full_train[y_column]
    del df_train[y_column]
    del df_val[y_column]
    del df_test[y_column]

    return df_full_train, df_train, df_val, df_test, y_full_train, y_train, y_val, y_test


def train(dataFrame, y, xgb_params):
    # Hot Encoding
    dicts = dataFrame.to_dict(orient="records")
    dv = DictVectorizer(sparse=False)
    X = dv.fit_transform(dicts)

    features = dv.get_feature_names_out()
    # print(features)
    dtrain = xgb.DMatrix(X, label=y, feature_names=features, enable_categorical=True)

    # train
    model = xgb.train(xgb_params, dtrain, num_boost_round=10)
    # print(model.feature_names)

    return dv, model


def predict(dataFrame, dv, model):
    dicts = dataFrame.to_dict(orient="records")
    X = dv.transform(dicts)
    features = dv.get_feature_names_out()
    dval = xgb.DMatrix(X, feature_names=features)
    y_pred = model.predict(dval)
    return y_pred, X


def get_rmse(y_val, y_pred_val):
    mae = metrics.mean_absolute_error(y_val, y_pred_val)
    mse = metrics.mean_squared_error(y_val, y_pred_val)
    rmse = np.sqrt(metrics.mean_squared_error(y_val, y_pred_val))

    # print("MAE for numerical linear:", mae)
    # print("MSE for numerical linear:", mse)
    # print("RMSE:", rmse)
    return mae, mse, rmse

def set_mlflow(experiment):
    mlflow.set_tracking_uri("http://15.207.72.49:5000")
    mlflow.set_experiment(experiment)


def run(experiement, filepath):
    # df_clean = read_dataframe(filepath)
    # df_to_split , y_column = preparing_dataframe(filepath)
    df_full_train, df_train, df_val, df_test, y_full_train, y_train, y_val, y_test = split_dataFrame(filepath)

    mlflow.xgboost.autolog()

    xgb_params_search_space = {
        'max_depth': scope.int(hp.choice('max_depth', [5, 10, 12, 13, 14, 20, 30, 40, 50, 100])),
        'eta': scope.int(hp.choice('eta', [0, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.6, 1, 2, 5, 10])),
        'min_child_weight': 1,
        'objective': 'reg:squarederror',
        'nthread': 8,
        'verbosity': 0,
        "seed": 42
    }

    def objective(params={}):
        with mlflow.start_run():
            active_mlflow_run_id = mlflow.active_run().info.run_id
            if (active_mlflow_run_id == None): raise ValueError("missing MLFlow active run.")
            # print(f'Training model. Active MLFlow run_id: {active_mlflow_run_id}')
            mlflow.set_tag("model", "xgboost")

            dv, model = train(df_full_train, y_full_train, params)

            os.makedirs("models", exist_ok=True)
            with open("models/preprocessor.b", "wb") as f_out:
                pickle.dump(dv, f_out)
            mlflow.log_artifact("models/preprocessor.b", artifact_path="preprocessor")
            mlflow.xgboost.log_model(model, artifact_path="models_mlflow")
            print(f"default artifacts URI: '{mlflow.get_artifact_uri()}'")

            y_pred_val, X_val = predict(df_val, dv, model)
            mae, mse, rmse = get_rmse(y_val, y_pred_val)
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("mse", mse)
            mlflow.log_metric("rmse", rmse)

        return {'loss': rmse, 'status': STATUS_OK}

    best_result = fmin(
        fn=objective,
        space=xgb_params_search_space,
        algo=tpe.suggest,
        max_evals=5,  # 50
        trials=Trials()
    )


def register_best_run(experiment_name):
    client = MlflowClient()

    # select the model with the lowest test RMSE
    experiment = client.get_experiment_by_name(experiment_name)
    print(experiment)
    best_runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=5,  # 50
        order_by=["metrics.rmse ASC"]
    )

    print(f'Models count: {len(best_runs)}')
    if (len(best_runs) == 0): raise "No models found."
    print(f'Top model found: {best_runs[0]}')

    # register the best model
    model_uri = f"runs:/{best_runs[0].info.run_id}/model"
    print(f'Registering {model_uri}')
    mv = mlflow.register_model(model_uri=model_uri, name=f"best_model-{experiment_name}")
    print(f"Registrered model {mv.name}, version: {mv.version}")


if __name__ == "__main__":
    filepath = "Clean_Input_Data/credit_card_churn_clean.csv"

    experiment = input("Enter Experiment name : ")

    set_mlflow(experiment)
    run(experiment, filepath)
    register_best_run(experiment)
