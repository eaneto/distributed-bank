import os
import time
import logging

import requests

from threading import current_thread
from random import randint, random, choice

from structlog import get_logger, configure
from structlog.stdlib import LoggerFactory

logging.basicConfig(
    filename='client.log',
    level=logging.INFO
)

configure(logger_factory=LoggerFactory())

log = get_logger()

TOKENS = [
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTEifQ.J4rxFfc7zCJTCxys49JxN1lWCHVfZLlMj5EauhYJ4-k",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTIifQ.TmlkAOWKWUMl6iNDPjrYxiQSP3_4BcQQiB1Ttc1ZR6w",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTMifQ.CnszkSIg7P2-co-8ZKIVvFyslptPRJ8sAFMQ5vrmRnI",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTQifQ.mrqSvmm-Y_uwx3hvg7XLoPXl9MFd4Hi9Exke8HD1Tl0",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTUifQ.V_0GT-xc_QlHicYc0olQFbdEHJ5yALOfR0wcCy81NM0"
]


class BusinessServiceClient:
    """Stateless client for the business service.

    The client isn't supposed to save any state about the requests to
    the business service. The only state stored is the immutable state
    set in the constructor.

    """

    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + self.token
        }

    def fetch_balance(self, account: int):
        """Fetches the account balance on the business service.

        Parameters
        ==========
        account: int
        The account to be fetched.

        Returns
        =======
        A dictionary with the response from the business service.

        Raises
        ======
        Exception when the service call fails.
        """
        response = requests.get(
            "{}/balance/{}".format(self.url, account),
            headers=self.headers
        )

        if response.status_code != 200:
            log.error("Error on business service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      account=account,
                      operation_name="fetch_balance",
                      thread_name=current_thread().name)
            raise Exception("Error requesting account balance")

        log.info("Successful business service call",
                 http_status=response.status_code,
                 account=account,
                 operation_name="fetch_balance",
                 thread_name=current_thread().name)
        return response.json()

    def deposit(self, account: int, amount: float):
        """Request a deposit to the business service.

        Parameters
        ==========
        account: int
        The account to be deposited.

        amount: float
        The deposit amount.

        Raises
        ======
        Exception when the service call fails.
        """
        response = requests.post(
            "{}/deposit/{}/{}".format(self.url, account, amount),
            headers=self.headers
        )

        if response.status_code != 200:
            log.error("Error on business service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      account=account,
                      amount=amount,
                      operation_name="deposit",
                      thread_name=current_thread().name)
            raise Exception("Error sending deposit request")

        log.info("Successful business service call",
                 account=account,
                 amount=amount,
                 operation_name="deposit",
                 thread_name=current_thread().name)

    def withdraw(self, account: int, amount: float):
        """Request a withdraw to the business service.

        Parameters
        ==========
        account: int
        The account to be withdrawn.

        amount: float
        The withdraw amount.

        Raises
        ======
        Exception when the service call fails.
        """
        response = requests.post(
            "{}/withdraw/{}/{}".format(self.url, account, amount),
            headers=self.headers
        )

        if response.status_code != 200:
            log.error("Error on business service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      account=account,
                      amount=amount,
                      operation_name="withdraw",
                      thread_name=current_thread().name)
            raise Exception("Error sending withdraw request")

        log.info("Successful business service call",
                 account=account,
                 amount=amount,
                 operation_name="withdraw",
                 thread_name=current_thread().name)

    def transfer(self, debit_account: int, credit_account: int, amount: float):
        """Request a transfer to the business service.

        Parameters
        ==========
        debit_account: int
        The debit account.

        credit_account: int
        The credit account.

        amount: float
        The transfer amount.

        Raises
        ======
        Exception when the service call fails.
        """
        response = requests.post(
            "{}/transfer/{}/{}/{}".format(
                self.url, debit_account, credit_account, amount
            ),
            headers=self.headers
        )

        if response.status_code != 200:
            log.error("Error on business service call",
                      http_status=response.status_code,
                      response_body=response.text,
                      debit_account=debit_account,
                      credit_account=credit_account,
                      operation_name="transfer",
                      thread_name=current_thread().name)
            raise Exception("Error sending transfer request")

        log.info("Successful business service call",
                 debit_account=debit_account,
                 credit_account=credit_account,
                 amount=amount,
                 operation_name="transfer",
                 thread_name=current_thread().name)


class BusinessServiceRouter:
    """The business service router creates a internal client for each
    business URL provided.

    The idea is to get a random client for each operation that the
    client will do.

    So basically the client will only instantiate a router and access
    the clients from it.

    """

    def __init__(self):
        business_urls = os.environ.get("BUSINESS_URLS")
        if business_urls:
            # Get all business urls separated by a comma.
            urls = business_urls.split(",")
        else:
            urls = ["http://localhost:5001"]

        # Initiate an empty list that will contain all created
        # clients.
        self.clients = []

        # Initiate all possible clients to be used.
        for index, url in enumerate(urls):
            # Get a random token from the tokens list
            random_token = TOKENS[index % len(TOKENS)]
            client = BusinessServiceClient(url, random_token)
            self.clients.append(client)

    def get_random_client(self):
        """Selects a random client from the instantiated client."""
        idx = randint(0, len(self.clients) - 1)
        return self.clients[idx]


# All possible operations a client can call
operations = [
    "fetch_balance", "deposit", "withdraw", "transfer"
]

router = BusinessServiceRouter()


def get_random_account() -> int:
    """Get a random account to be operated."""
    return randint(1, 10)


def get_random_account_excluding(account: int) -> int:
    """Get a random account excluding a specific one."""
    return choice([i for i in range(1, 10) if i not in [account]])


def get_random_amount() -> float:
    """Generate a random value for the operation amount."""
    return random() * 100


def generate_random_operation():
    """Generates a random operation on the business service."""
    # Selects a random operation
    operations_id = randint(0, len(operations) - 1)
    operation = operations[operations_id]
    # Get a client from the router
    client = router.get_random_client()
    # Processes a fetch balance operation
    if operation == "fetch_balance":
        account = get_random_account()
        balance = client.fetch_balance(account)
        log.info("Processing balance fetching",
                 account=account)
    # Processes a deposit operation
    elif operation == "deposit":
        account = get_random_account()
        amount = get_random_amount()
        log.info("Processing deposit",
                 account=account,
                 amount=amount)
        client.deposit(account, amount)
    # Processes a withdraw operation
    elif operation == "withdraw":
        account = get_random_account()
        amount = get_random_amount()
        log.info("Processing withdraw",
                 account=account,
                 amount=amount)
        client.withdraw(account, amount)
    # Processes a transfer operation
    else:
        debit_account = get_random_account()
        credit_account = get_random_account_excluding(debit_account)
        amount = get_random_amount()
        log.info("Processing transfer",
                 debit_account=debit_account,
                 credit_account=credit_account,
                 amount=amount)
        client.transfer(debit_account, credit_account, amount)


# Infinite loop that generates multiple and random operations to the
# business services configured.
while True:
    try:
        generate_random_operation()
        # Wait for .1 second
        time.sleep(.1)
    except Exception as e:
        log.error(e)
        time.sleep(1)
