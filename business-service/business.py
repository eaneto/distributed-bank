import os
import logging
import requests
import json
import time

from threading import Lock, current_thread, Thread
from functools import wraps

from flask import Flask, request
from structlog import get_logger, configure
from structlog.stdlib import LoggerFactory

logging.basicConfig(
    filename='business.log',
    encoding='utf-8',
    level=logging.DEBUG
)

configure(logger_factory=LoggerFactory())

class ThreadSafeCounter:
    """A thread safe counter used to register the operation number."""

    def __init__(self):
        self.counter = 0
        self.lock = Lock()

    def increment(self):
        """increment the thread counter"""
        self.lock.acquire(timeout=10)
        self.counter += 1
        self.lock.release()


TOKENS = {
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTEifQ.J4rxFfc7zCJTCxys49JxN1lWCHVfZLlMj5EauhYJ4-k": "client-1",
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTIifQ.TmlkAOWKWUMl6iNDPjrYxiQSP3_4BcQQiB1Ttc1ZR6w": "client-2",
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTMifQ.CnszkSIg7P2-co-8ZKIVvFyslptPRJ8sAFMQ5vrmRnI": "client-3",
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTQifQ.mrqSvmm-Y_uwx3hvg7XLoPXl9MFd4Hi9Exke8HD1Tl0": "client-4",
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTUifQ.V_0GT-xc_QlHicYc0olQFbdEHJ5yALOfR0wcCy81NM0": "client-5"
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


#Variables for the application
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


class ThreadSafeQueue:
    """Class that implements a safe thread queue for lock.

    Attributtes
    ===========
    lock : Lock
    Represents the lock for all threads.

    queue : List
    Queue to store and process the client requests
    """

    def __init__(self):
        self.lock = Lock()
        self.queue = []

    def push(self, element):
        """Push the received request inside the queue, after that during the
        process, it acquire the lock and at the end release it.

        """
        self.lock.acquire(timeout=10)
        self.queue.append(element)
        self.lock.release()

    def pop(self):
        """Remove one request from the queue during the process, it acquire
        process, it acquire the lock and at the end release it.

        """
        self.lock.acquire(timeout=10)
        element = self.queue.pop()
        self.lock.release()
        return element

    def size(self) -> int:
        """return the length of the queue"""
        return len(self.queue)


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
        payload = {
            "business_id": self.business_id,
            "account": account
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
        payload = {
            "business_id": self.business_id,
            "account": account
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

# Queue used to store all operations
operations_queue = ThreadSafeQueue()

@app.route("/balance/<int:account>")
@token_required
def balance_route(account: int):
    """Fetches the account balance.

    This is the only operation that isn't queued.

    """
    operation_number.increment()
    log.info("Fetching balance",
             business_id=client.business_id,
             account=account,
             operation_name="fetch_balance",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)
    try:
        return client.fetch_account_balance(account)
    except Exception as e:
        log.error(e)
        return {}, 500


@app.route("/deposit/<int:account>/<float:amount>", methods=["POST"])
@token_required
def deposit_route(account: int, amount: float):
    """Endpoint for deposit process request

    Parameters
    ===========
    account : int
    Account for the deposit.

    amount : float
    The value for deposit it.
    """

    operation_number.increment()
    log.info("Publishing deposit to operations queue",
             business_id=client.business_id,
             account=account,
             amount=amount,
             operation_name="deposit",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

    operations_queue.push({
        "operation_name": "deposit",
        "account": account,
        "amount": amount
    })

    return {}, 200


@app.route("/withdraw/<int:account>/<float:amount>", methods=["POST"])
@token_required
def withdraw_route(account: int, amount: float):
    """Endpoint for withdraw process request.

    Parameters
    ==========
    account : int
    Account for the withdraw.

    amount : float
    The value for withdraw it.
    """

    operation_number.increment()
    log.info("Publishing withdraw to operations queue",
             business_id=client.business_id,
             account=account,
             amount=amount,
             operation_name="withdraw",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

    operations_queue.push({
        "operation_name": "withdraw",
        "account": account,
        "amount": amount
    })

    return {}, 200


@app.route("/transfer/<int:debit_account>/<int:credit_account>/<float:amount>",
           methods=["POST"])
@token_required
def transfer_route(debit_account: int, credit_account: int, amount: float):
    """Endpoint for transfer process request.

    Parameters
    ==========
    debit_account : int
    Account for the debit.

    credit_account : int
    Account for the credit.

    amount : float
    The value for transfer it.
    """

    operation_number.increment()
    log.info("Publishing transfer to operations queue",
             business_id=client.business_id,
             debit_account=debit_account,
             credit_account=credit_account,
             amount=amount,
             operation_name="transfer",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

    operations_queue.push({
        "operation_name": "transfer",
        "debit_account": debit_account,
        "credit_account": credit_account,
        "amount": amount
    })

    return {}, 200

def deposit(account: int, amount: float):
    """Process a deposit.

    Parameters
    ===========
    account : int
    Account for the deposit.

    amount : float
    The value for deposit it.
    """
    log.info("Initiating deposit",
             business_id=client.business_id,
             account=account,
             amount=amount,
             operation_name="deposit",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)
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
    log.info("Deposit finished successfully",
             business_id=client.business_id,
             account=account,
             amount=amount,
             operation_name="deposit",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)


def withdraw(account: int, amount:float):
    """Process a withdraw.

    Parameters
    ==========
    account : int
    Account for the withdraw.

    amount : float
    The value for withdraw it.
    """
    log.info("Initiating withdraw",
             business_id=client.business_id,
             account=account,
             amount=amount,
             operation_name="withdraw",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

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
    log.info("Withdraw finished successfully",
             business_id=client.business_id,
             account=account,
             amount=amount,
             operation_name="withdraw",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

def transfer(debit_account: int, credit_account: int, amount: float):
    """Process a transfer between two accounts.

    Parameters
    ==========
    debit_account : int
    Account for the debit.

    credit_account : int
    Account for the credit.

    amount : float
    The value for transfer it.
    """
    log.info("Initiating transfer",
             business_id=client.business_id,
             debit_account=debit_account,
             credit_account=credit_account,
             amount=amount,
             operation_name="transfer",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

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

    log.info("Transfer finished successfully",
             business_id=client.business_id,
             debit_account=debit_account,
             credit_account=credit_account,
             amount=amount,
             operation_name="transfer",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)


def queue_consumer():
    """The operations queue consumer.

    An infinite loop that processes the operations queue.

    """
    while True:
        process_operations_queue()


def process_operations_queue():
    """Processes the operations queue.

    The queue can only be processed when it has at least 5 messages,
    otherwise no operations will be processed.

    """
    queue_size = operations_queue.size()
    # If there are less than five messages just ignore and
    # sleep for one second.
    if queue_size < 5:
        log.info("Queue not filled yet",
                 queue_size=queue_size,
                 operation_name="background_operation_processor",
                 thread_name=current_thread().name)
        time.sleep(1)
        return

    # Process five operations on the queue.
    for i in range(5):
        # Removes the message from the queue and return it
        operation = operations_queue.pop()
        # Do the specific operation given the operation name
        if operation["operation_name"] == "deposit":
            deposit(operation["account"], operation["amount"])
        elif operation["operation_name"] == "withdraw":
            withdraw(operation["account"], operation["amount"])
        elif operation["operation_name"] == "transfer":
            transfer(
                operation["debit_account"],
                operation["credit_account"],
                operation["amount"]
            )

if __name__ == "__main__":
    consumer_thread = Thread(
        name="Operations-Consumer-Thread",
        target=queue_consumer
    )
    # Initialize the background job for the operations queue.
    consumer_thread.start()
    # If any id is set then the app is running publicly on the
    # network.
    if os.environ.get("BUSINESS_ID"):
        app.run(
            port=5000,
            host="0.0.0.0"
        )
    else:
        app.run(port=5001)
