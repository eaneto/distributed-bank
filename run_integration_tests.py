#!/bin/sh

source .venv/bin/activate

# Data service
export FLASK_APP=data-service/data.py
flask run &

cd integration_tests/ && pytest

# Destroy data service instance
killall flask
