#run: make run_tests   to run tests locally

LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
# Run:
#  'make help' to see commands

# Requires:
#   make
#   docker
#   docker-compose
#   aws cli
#   pip3b install prefect==2.0b5

help:
	@echo "\nCommands:\n"
	@cat Makefile | egrep -e '^#run:.*'| sed -e 's~#~~g'
# @make -qpRr | egrep -e '^[a-z].*:' | sed -e 's~:~~g' | sort
	@echo ""

#run: make setup_tests   to install tests dependencies locally
setup_tests:
	pip install pytest
	pip install -r server/requirements.txt

#run: make run_tests   to run tests locally
run_tests:
	pytest Testing/

#run: make reset_all   to delete all containers and cleanup volumes
reset_all:
	docker compose -f docker-compose-serve.yml -f docker-compose-model-registry.yml down
	rm -rf /tmp/mlopsdb
	rm -rf /tmp/mlopsartifacts
	rm -rf /tmp/store
	rm -rf /tmp/serve
	rm -rf /tmp/mlreports
	rm .env

#run: make setup-model-registry env=local (or env=cloud)   to start model registry and training containers
setup-model-registry:
	mkdir -p /tmp/mlopsdb
	mkdir -p /tmp/mlopsartifacts
	mkdir -p /tmp/store
	mkdir -p /tmp/serve
	mkdir -p /tmp/mlreports
	cp .env.$(env) .env
	docker compose -f docker-compose-model-registry.yml up --build --force-recreate -d

#run: make setup-model-serve env=local (or env=cloud)   to start the model serving containers
setup-model-serve:
	chmod 777 monitoring/
	chmod 777 monitoring/**/*
	cp .env.$(env) .env
	docker compose -f docker-compose-serve.yml  up --build --force-recreate -d

#run: make apply-prediction-reporting   to apply the automated prediction reporting DAG
apply-prediction-reporting:
	docker cp ./reporting/create_report.py prefect_agent_1:create_report.py
	docker exec prefect_agent_1 prefect deployment create create_report.py

#run: make stop-serve   to stop the model servers (http api and Stream)
stop-serve:
	docker stop send_data-api
	docker stop send_data-kinesis
	docker stop send_data-api
	docker rm -f send_data-kinesis

#run: make start-serve env=local   to start the model servers (http api and Stream)
start-serve:
	cp .env.$(env) .env
	docker compose -f docker-compose-serve.yml up -d

