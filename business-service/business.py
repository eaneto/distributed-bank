import os
import logging
import requests
import json

from functools import wraps

from flask import Flask, request
from structlog import get_logger

logging.basicConfig(
    filename='business.log',
    encoding='utf-8',
    level=logging.DEBUG
)


class ThreadSafeCounter:
    """A thread safe counter used to register the operation number."""
    def __init__(self):
        self.counter = 0
        self.lock = Lock()

    def increment(self):
        self.lock.acquire(timeout=10)
        self.counter += 1
        self.lock.release()


TOKENS = {
    "": "client-1",
    "": "client-2",
    "": "client-3"
}

app = Flask(__name__)
log = get_logger()

class DataServiceClient:
    def __init__(self, business_id: int):
        self.business_id = business_id
        data_url = os.environ.get("DATA_URL")
        if data_url:
            self.url = data_url
        else:
            self.url = "http://localhost:5000"
        self.token = os.environ.get("TOKEN")

    def acquire_lock(self, account: int):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + self.token
        }
        payload = {
            "id_negoc": self.business_id,
            "conta": account
        }
        response = requests.put(self.url + "/lock",
                                headers=headers,
                                data=json.dumps(payload))

        if response.status_code != 200:
            raise Exception("Error acquiring lock")

    def fetch_account_balance(self, account: int):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + self.token
        }
        response = requests.get(
            self.url + "/balance/{}/{}".format(self.business_id, account),
            headers=headers)

        if response.status_code != 200:
            raise Exception("Error fetching account balance")


@app.route("/balance/<int:account>")
@token_required
def balance_route():
    return



if __name__ == "__main__":
    app.run(port=5001)
