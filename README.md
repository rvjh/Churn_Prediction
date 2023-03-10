# Churn Prediction

The challenge requested to build a fully automated end-to-end Machine Learning infrastructure, including reading data from a feature store, automated model creation with hyperoptimization tuning and automatically finding the most efficient model, storing models in a model registry, building a CI/CD pipeline for deploying the registered model into a production environment, serving the model using HTTP API or Streaming interfaces, implementing monitoring, writing tests and linters, creating regular automated reporting.

Note: this is a personal project to demonstrate an automated ML infrastructure. Security was not in the scope of this project. For deploying this infrastructure in a production environment please ensure proper credentials are set for each service and the infrastructure is not exposing unwanted endpoints to the public internet.

## Final architecture:

<img width="1337" alt="image" src="https://user-images.githubusercontent.com/3721810/185756770-73bfea67-8455-4e51-9cbf-14e0ceba5909.png">

There is a Prefect orchestrator to run 2 flows on a scheduler basis. The `Hyperoptimization deployment flow` is executed by a `Prefect Agent` by pulling training data from the `Local`, runs hyperoptimization ML model builds and save each model (around 5 models per run) in the MLFlow model registry. On each run it also finds the most efficient model and it registers it in MlFlow to be ready for deployment.

An engineer must decide when and which models should be deployed. First copies the `RUN_ID` of the selected deployment model from ML Flow and update `.env.cloud` for cloud deployment with the new `RUN_ID` field. 

Once the `RUN_ID` is updated, Github Actions triggers a new pipeline-run which will run tests and restarts the 2 servers (http-api and kinesis-streams servers). The servers will start by automatically loading the new model from ML Flow.

The `Business Simulation using AWS Kinesis Streams` simulates business regularly (every 60sec) sending events to Kinesis stream for prediction. `ML Model Serving Kinesis Stream service` is a ML serving server using Kinesis stream as input and output for running predictions is realtime.

The `Business Simulation using HTTP API` simulates business regularly (every 60sec) sending http requests. `ML Model Serving Flask HTTP API service` is a ML serving server using http APIs for running predictions in realtime. On each prediction request, input and prediction is saved in MongoDB for later processing and also sent to `Evidently` for monitoring.

`Evidently` is calculating data drift to understand if the running predictions are degrading over time.

`Prometheus` is storing monitoring data and `Grafana` is providing a dashboard UI to monitor the prediction data drift in realtime.

The `Batch reporting flow` is running regularly (every 1 hours) on the MongoDB data to generate data drift reports.

# Project progress

### Input data

Data: Credit Card Churn Prediction

Description: A business manager of a consumer credit card bank is facing the problem of customer attrition. They want to analyze the data to find out the reason behind this and leverage the same to predict customers who are likely to drop off.

Source: https://www.kaggle.com/datasets/anwarsan/credit-card-bank-churn

### Implementation plan:

- [x] cleanup data
- [x] exploratory data analysis
- [x] train model
- [x] ml pipeline for hyperparameter tuning
- [x] model registry
- [x] ML-serve API server
- [x] ML-serve Stream server (optional)
- [x] tests (partial)
- [ ] linters
- [x] Makefile and CI/CD
- [x] deploy to cloud
- [x] logging and monitoring
- [x] batch reporting
- [x] docker and docker-compose everything
- [ ] reporting server

### Data cleanup

- Removes rows with "Unknown" records, removes irellevant columns, lowercase column names, lowercase categoriacal values.

- Categories that can be ordered hiarachically are converted into ints, like "income" or "education level".

[DataPreparation.ipynb](Prepare_Input_Data%2FDataPreparation.ipynb)

### Exploratory data analysis

- Checks correlations on numerical columns. 

- Checks count on categorical columns.

- [exploratory_data_analysis.ipynb](Exploratory_Data_Analysis%2Fexploratory_data_analysis.ipynb)


### Train Model

- Prepare a model using XGBoost. 

- Input data is split into 66%, 33%, 33% for training, validation and test data.

- Measures MAE, MSE, RMSE.

- Measures % of deviated predictions based on month threshold.

- [Experiment_tracking_and_Model_Training_with_MLFlow.ipynb](Experiment_Tracking%2FExperiment_tracking_and_Model_Training_with_MLFlow.ipynb)

### Model Registry with MLFlow

- dockerized MLFlow: [Dockerfile-mlflow](Experiment_Tracking%2FDockerfile-mlflow)
- MLFlow UI: `http://15.207.72.49:5000`

![img.png](images%2Fimg.png)

Model Artifacts stored in S3

![img_1.png](images%2Fimg_1.png)

### Automated Hyperoptimization tuning

System is using Prefect to orchestrate DAGs. Every few hours, Prefect Agent will start and read the training data, it will build models using XGBoost by running hyperparameterization on the configurations, generating 10 models and calculating accuracy (rmse) for each of them. All 10 models are registered in the MLFlow model registry experiments. At the end of each run, the best model will be registered in MLFlow as ready for deployment.

- model training Prefect flow: [model_training.py](Model_Orchestration%2Fmodel_training.py)
- dockerized Prefect Server: [Dockerfile-prefect](Model_Orchestration%2FDockerfile-prefect)
- dockerized Prefect Agent: [Dockerfile-prefect-agent](Model_Orchestration%2FDockerfile-prefect-agent)

- Prefect UI: `http://65.1.85.183:4200`

![img_2.png](images%2Fimg_2.png)

Queued Workflow 

![img_3.png](images%2Fimg_3.png)

![img_4.png](images%2Fimg_4.png)

### Model serving HTTP API and Stream

There are 2 ML service servers. One serving predictions using HTTP API build in Python with Flask. Second serving predictions using AWS Kinesis streams, both consuming and publishing results back.

- model serving using Python Flask HTTP API: [predict_api_flask.py](Model_Deployment%2FWeb_service_API%2Fpredict_api_flask.py)

![img_5.png](images%2Fimg_5.png)

![img_6.png](images%2Fimg_6.png)

- model serving using Python and AWS Kinesis Streams: [lambda_function_stream_kinesis.py](Model_Deployment%2FStreaming%2Flambda_function_stream_kinesis.py)

![img_7.png](images%2Fimg_7.png)

![img_8.png](images%2Fimg_8.png)

![img_9.png](images%2Fimg_9.png)

- dockerized Flask API server: [Dockerfile-serve-api](Model_Deployment%2FDockerfile-serve-api)
- dockerized AWS Kinesis server: [Dockerfile-serve-kinesis](Model_Deployment%2FDockerfile-serve-kinesis)

### Simulation_business: sending data for realtime prediction

There are 2 Python scripts to simulate business requesting predictions from ML servers. One request data from HTTP API server and another one sending events to `predictions` Kinesis stream and receiving results to `results` Kinesis stream.

- sending data for prediction using HTTP API: [test_API.py](Model_Deployment%2FWeb_service_API%2Ftest_API.py)
- sending data for prediction using AWS Kinesis Streams: [test_lambda_kinesis.py](Model_Deployment%2FStreaming%2Ftest_lambda_kinesis.py)

### Monitoring

There are 3 services for monitoring the model predictions is realtime:
- Evidently AI for calculating data drift. Evidently UI: 
- Prometheus for collecting monitoring data. Prometheus UI: 
- Grafana for Dashboards UI. Grafana UI: [http://localhost:3000](http://localhost:3000/d/U54hsxv7k/evidently-data-drift-dashboard?orgId=1&refresh=10s) (default user/pass: admin, admin)

<img width="1784" alt="image" src="https://user-images.githubusercontent.com/3721810/185757624-2cc5c23a-40a7-4d4f-8ad3-3c9cefe08cbb.png">


### Reporting

There is a Prefect flow to generate reporting using Evidently. This will generate reports every few hours save them in MongoDB and also generate static html pages with all data charts.

### Deployment

All containers are put together in docker compose files for easy deployment of the entire infrastructure. Docker-compose if perfect for this project, for a more advanced production environment where each service is deployed in different VM, I recommend using more advance tools.

- Deployment: model training: [docker-compose-model-registry.yml](docker-compose-model-registry.yml)
- Deployment: model serving: [docker-compose-serve.yml](docker-compose-serve.yml)

All deployment commands are grouped using the Makefile for simplicity of use.
- [Makefile](Makefile)

The environment variables should be in `.env` file. [.env.cloud](.env.cloud) 

``` sh
$> make help

Commands:

run: make run_tests   to run tests locally
run: make reset_all   to delete all containers and cleanup volumes
run: make setup-model-registry env=local (or env=cloud)   to start model registry and training containers
run: make init_aws  to setup and initialize AWS services (uses localstack container)
run: make apply-model-train-flow   to apply the automated model training DAG 
run: make setup-model-serve env=cloud   to start the model serving containers
run: make apply-prediction-reporting   to apply the automated prediction reporting DAG
run: make stop-serve   to stop the model servers (http api and Stream)
run: make start-serve env=cloud   to start the model servers (http api and Stream)
```

### CI/CD in Cloud

The continues deployment is done using Github actions. Once a change is made to the repo, the deployment pipeline is triggered. This will restart the model servers to load a new model from the MLFlow model registry. The deployed model is always specified in `.env.cloud` file under `RUN_ID` environment variable.

The pipeline will:
- run tests 
- ssh in the cloud virtual machine
- restart model-server-api and model-server-streams containers


# Start infrastructure cloud
To deploy in the cloud : 

- install `docker`, `docker compose`, `make`
- run `make reset_all` to ensure any existing containers are removed

- run `make setup-model-registry env=local`  to start model training infrastructure
- open `http://15.207.72.49:5000` to see MLFlow UI.
- run `make init_aws` to setup training data and streams in AWS
- run `make apply-model-train-flow` to apply model training script to the orchestrator. This will run trainings regularly.
- open `http://65.1.85.183:4200`, it will show the `model_tuning_and_uploading` deployment scheduled. Start a `Quick Run` to not wait for the scheduler. This will run the model training pipeline and upload a bunch of models to MLFlow server and register the best model.

- from the MLFlow UI decide which model you want to deploy. Get the Run Id of the model and update `RUN_ID` in `.env.cloud` file.
- run `make setup-model-serve env=cloud` to start prediction servers

- request a prediction using http API:
``` sh
$> curl -X POST -H 'Content-Type: application/json' http://127.0.0.1:9696/predict -d '{"customer_age":50,"gender":"M","dependent_count":2,"education_level":3,"marital_status":"married","income_category":2,"card_category":"blue","months_on_book":4,"total_relationship_count":3,"credit_limit":4000,"total_revolving_bal":2511}'

{"churn chance":0.5,"model_run_id":"09ff5d86828e454782de9ee0deb5cf7b"}
```

- run `make apply-prediction-reporting` to apply reporting script to the orchestrator. This will generate reports regularly.
- open ` `, it will show `evidently_data_reporting` deployment. This runs every 3 hours. The system needs to collect 1+ hours of predictions data first before generating any report. Running the reporting manually at this time will not generate reports yet.
- open `http://localhost:8888/` to see generated reports after 3+ hours.
- open `http://localhost:8085/metrics` to see prometheus data. 
- open `http://localhost:3000/dashboards` to see Grafana realtime monitoring dashboard of data drift. (default user/pass: admin, admin)


Optionally:
- publish to Kinesis. `data` is the request json payload base64 encoded
``` sh
aws kinesis put-record \
    --stream-name ${KINESIS_STREAM_INPUT} \
    --partition-key 1 \
    --cli-binary-format raw-in-base64-out \
    --data '{
      "churn": {
        "customer_age": 100,
        "gender": "F",
        "dependent_count": 2,
        "education_level": 2,
        "marital_status": "married",
        "income_category": 2,
        "card_category": "blue",
        "months_on_book": 6,
        "total_relationship_count": 3,
        "credit_limit": 4000,
        "total_revolving_bal": 2500
      },
      "churn_id": 123
    }'
``` 

- consume from Kinesis
``` sh
KINESIS_STREAM_OUTPUT='churn-prediction'
SHARD='shardId-000000000000'
SHARD_ITERATOR=$(aws kinesis \
    get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator' \
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode | jq
```
Also refer : [README.md](Model_Deployment%2FStreaming%2FREADME.md)

![img_10.png](images%2Fimg_10.png)

![img_11.png](images%2Fimg_11.png)

![img_12.png](images%2Fimg_12.png)

![img_13.png](images%2Fimg_13.png)

- run `docker logs -t {container}` to see logs for now

All running containers:
<img width="1571" alt="image" src="https://user-images.githubusercontent.com/3721810/185755712-4591f7ba-a98e-4f7b-a8a1-231d33e8beea.png">


Links:
- ML Flow model registry: http://15.207.72.49:5000
- Prefect orchestrator: http://65.1.85.183:4200


### Other useful links:

- Github Actions: add ssh keys from server: https://zellwk.com/blog/github-actions-deploy/


## Note

After completing this project I have destroyed all the cloud components used in this project. So you may not be able to access any URL.

## To Do : 
 
- IaaS using Terraform