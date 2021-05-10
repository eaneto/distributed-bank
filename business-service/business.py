import os
import logging
import requests
import json

from threading import Lock, current_thread
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
    "Basic super-valid-token": "client-1",
    "": "client-2",
    "": "client-3"
}


def token_required(f):
    """Decorator used to validate routes that can only be accessed with a
    valid token.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Checks if the token is in the token list
        if request.headers.get("Authorization") not in TOKENS:
            return {"data": -1}, 401
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)
log = get_logger()
operation_number = ThreadSafeCounter()


def get_env_or_default(env_key: str, default) -> str:
    """Returns the environment variable value or if it doesn't exist the
    default value.

    """
    value = os.environ.get(env_key)
    if value:
        return value

    return default

class DataServiceClient:
    """Stateless client for the data service.

    The client isn't supposed to save any state about the requests to
    the data service. The only state stored is the immutable state set
    in the constructor.

    """
    def __init__(self):
        self.business_id = get_env_or_default("BUSINESS_ID", 1)
        self.url = get_env_or_default("DATA_URL", "http://localhost:5000")
        self.token = get_env_or_default("TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMSJ9.UbKAsZGwbMcFBGMVXhAfg4WL4Lac-nhVZ4jegPtNlW0")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + self.token
        }

    def acquire_lock(self, account: int):
        # TODO logs
        payload = {
            "id_negoc": self.business_id,
            "conta": account
        }
        response = requests.put(
            self.url + "/lock",
            headers=self.headers,
            data=json.dumps(payload)
        )

        if response.status_code != 200:
            log.error("Error on data service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      business_id=self.business_id,
                      account=account,
                      operation_name="acquire_lock",
                      operation_number=operation_number.counter,
                      thread_name=current_thread().name)
            raise Exception("Error acquiring lock")

    def release_lock(self, account: int):
        # TODO logs
        payload = {
            "id_negoc": self.business_id,
            "conta": account
        }
        response = requests.delete(
            self.url + "/lock",
            headers=self.headers,
            data=json.dumps(payload)
        )

        if response.status_code != 200:
            log.error("Error on data service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      business_id=self.business_id,
                      account=account,
                      operation_name="release_lock",
                      operation_number=operation_number.counter,
                      thread_name=current_thread().name)
            raise Exception("Error releasing lock")

    def fetch_account_balance(self, account: int):
        # TODO logs
        response = requests.get(
            self.url + "/balance/{}/{}".format(self.business_id, account),
            headers=self.headers
        )

        if response.status_code != 200:
            log.error("Error on data service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      business_id=self.business_id,
                      account=account,
                      operation_name="fetch_account_balance",
                      operation_number=operation_number.counter,
                      thread_name=current_thread().name)
            raise Exception("Error fetching account balance")

        return response.json()

    def update_account_balance(self, account: int, amount: float):
        # TODO logs
        response = requests.put(
            self.url + "/balance/{}/{}".format(self.business_id, account),
            headers=self.headers,
            data=json.dumps({"valor": amount})
        )

        if response.status_code != 200:
            log.error("Error on data service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      business_id=self.business_id,
                      account=account,
                      operation_name="update_account_balance",
                      operation_number=operation_number.counter,
                      thread_name=current_thread().name)
            raise Exception("Error updating account balance")


# One stateless shared instance
client = DataServiceClient()


@app.route("/balance/<int:account>")
@token_required
def balance_route(account: int):
    operation_number.increment()
    try:
        return client.fetch_account_balance(account)
    except Exception:
        log.error(e)
        return {}, 500


@app.route("/deposit/<int:account>/<float:amount>", methods=["POST"])
@token_required
def deposit_route(account: int, amount: float):
    operation_number.increment()
    try:
        # Get lock
        client.acquire_lock(account)
        # Get account balance
        account_balance = client.fetch_account_balance(account)
        # Calculate new balance
        new_balance = float(account_balance["balance"]) + amount
        # Update balance amount
        client.update_account_balance(account, new_balance)
        # Unlock account
        client.release_lock(account)
        return {}, 200
    except Exception as e:
        log.error(e)
        return {}, 500


@app.route("/withdraw/<int:account>/<float:amount>", methods=["POST"])
@token_required
def withdraw_route(account: int, amount: float):
    operation_number.increment()
    try:
        # Get lock
        client.acquire_lock(account)
        # Get account balance
        account_balance = client.fetch_account_balance(account)
        # Calculate new balance
        new_balance = float(account_balance["balance"]) - amount
        # Update balance amount
        client.update_account_balance(account, new_balance)
        # Unlock account
        client.release_lock(account)
        return {}, 200
    except Exception as e:
        log.error(e)
        return {}, 500


@app.route("/transfer/<int:debit_account>/<int:credit_account>/<float:amount>", methods=["POST"])
@token_required
def transfer_route(debit_account: int, credit_account: int, amount: float):
    operation_number.increment()
    try:
        # Get lock on both accounts
        client.acquire_lock(debit_account)
        client.acquire_lock(credit_account)
        # Get the accounts balances
        debit_account_balance = client.fetch_account_balance(debit_account)
        credit_account_balance = client.fetch_account_balance(credit_account)
        # Calculate balance for both accounts
        debit_balance = float(debit_account_balance["balance"]) - amount
        credit_balance = float(credit_account_balance["balance"]) + amount
        # Update balance amount to both accounts
        client.update_account_balance(debit_account, debit_balance)
        client.update_account_balance(credit_account, credit_balance)
        # Unlock both accounts
        client.release_lock(debit_account)
        client.release_lock(credit_account)
        return {}, 200
    except Exception as e:
        log.error(e)
        return {}, 500

if __name__ == "__main__":
    app.run(port=5001)
