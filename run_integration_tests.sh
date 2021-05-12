#!/bin/sh

source .venv/bin/activate

# Data service
export FLASK_APP=data-service/data.py
flask run &

sleep 1

pytest integration_tests/data_service_test.py

# Destroy data service instance
killall flask

# Business Service
python data-service/data.py &
data_pid=$!

python business-service/business.py &
business_pid=$!

sleep 1

pytest integration_tests/business_service_test.py

# Destroy service instances
kill -9 $data_pid
kill -9 $business_pid

# Business Service Async
python data-service/data.py &
data_pid=$!

python business-service/business.py &
business_pid=$!

sleep 1

pytest integration_tests/business_service_test_with_multiple_operations.py

# Destroy service instances
kill -9 $data_pid
kill -9 $business_pid
