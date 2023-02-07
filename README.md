# Churn Prediction

The challenge requested to build an fully automated end-to-end Machine Learning infrastructure, including reading data from a feature store, automated model creation with hyperoptimization tuning and automatically finding the most efficient model, storing models in a model registry, building a CI/CD pipeline for deploying the registered model into a production environment, serving the model using HTTP API or Streaming interfaces, implementing monitoring, writing tests and linters, creating regular automated reporting.

Note: this is a personal project to demonstrate an automated ML infrastructure. Security was not in the scope of this project. For deploying this infrastructure in a production environment please ensure proper credentials are set for each service and the infrastructure is not exposing unwanted endpoints to the public internet.

## Final architecture:



There is a Prefect orchestrator to run 2 flows on a scheduler basis. The `Hyperoptimization deployment flow` is executed by a `Prefect Agent` by pulling training data from the `AWS S3 feature store`, runs hyperoptimization ML model builds and save each model (around 10 models per run) in the MLFlow model registry. On each run it also finds the most efficient model and it registers it in MlFlow to be ready for deployment.

An engineer must decide when and which models should be deployed. First copies the `RUN_ID` of the selected deployment model from ML Flow and update `.env.cloud` for cloud deployment with the new `RUN_ID` field. 

Once the `RUN_ID` is updated, Github Actions triggers a new pipeline-run which will run tests and restarts the 2 servers (http-api and kinesis-streams servers). The servers will start by automatically loading the new model from ML Flow.

The `Business Simulation using AWS Kinesis Streams` simulates business regularly (every 60sec) sending events to Kinesis stream for prediction. `ML Model Serving Kinesis Stream service` is a ML serving server using Kinesis stream as input and output for running predictions is realtime.

The `Business Simulation using HTTP API` simulates business regularly (every 60sec) sending http requests. `ML Model Serving Flask HTTP API service` is a ML serving server using http APIs for running predictions in realtime. On each prediction request, input and prediction is saved in MongoDB for later processing and also sent to `Evidently` for monitoring.

`Evidently` is calculating data drift to understand if the running predictions are degrading over time.

`Prometheus` is storing monitoring data and `Grafana` is providing a dashboard UI to monitor the prediction data drift in realtime.

The `Batch reporting flow` is running regularly (every 3 hours) on the MongoDB data to generate data drift reports. These reports are saved as `html` and the `File server - Nginx` gives access to the report files.

# Project progress

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
- [x] reporting server

### Data cleanup

- Removes rows with "Unknown" records, removes irellevant columns, lowercase column names, lowercase categoriacal values.

- Categories that can be ordered hiarachically are converted into ints, like "income" or "education level".

[prepareData.ipynb](model_preparation_analysis/prepareData.ipynb)

### Exploratory data analysis

- Checks correlations on numerical columns. 

- Checks count on categorical columns.

- [exploratory_data_analysis.ipynb](exploratory_data_analysis/exploratory_data_analysis.ipynb)
- [model_preparation_analysis](model_preparation_analysis)




