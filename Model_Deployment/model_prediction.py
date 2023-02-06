import xgboost as xgb
from model_loading import load_model_from_mlflow


def get_input_features():
    input_value = {
        "customer_age": input('customer_age:'),
        "gender": input('gender:'),
        "dependent_count": input('dependent_count:'),
        "education_level": input('education_level:'),
        "marital_status": input('marital_status:'),
        "income_category": input('income_category:'),
        "card_category": input('card_category:'),
        "months_on_book": input('months_on_book:'),
        "total_relationship_count": input('total_relationship_count:'),
        "credit_limit": input('credit_limit:'),
        "total_revolving_bal": input('total_revolving_bal:')
    }
    #input_value = dict(input_value)
    return input_value

def predict():
    xgboost_model, dv = load_model_from_mlflow()
    print("Model Loading Successful :-) ")
    input_value = get_input_features()
    print("Importing Feature Values ...........")
    X = dv.transform(input_value)
    features = dv.get_feature_names_out()
    dval = xgb.DMatrix(X, feature_names=features)
    y_pred = xgboost_model.predict(dval)
    print(f"prediction : {y_pred[0]}")
    return y_pred[0]

#predict()


