import logging

from threading import Lock, current_thread
from functools import wraps

from flask import Flask, request
from structlog import get_logger, configure
from structlog.stdlib import LoggerFactory

logging.basicConfig(
    filename='data.log',
    level=logging.DEBUG
)

configure(logger_factory=LoggerFactory())

class ThreadSafeCounter:
    """A thread safe counter used to register the operation number."""
    def __init__(self):
        self.counter = 0
        self.lock = Lock()

    def increment(self):
        self.lock.acquire(timeout=10)
        self.counter += 1
        self.lock.release()


class BusinessMutex:
    """Mutex used to store the business id, used by the business server,
    and a exclusive lock used for updating the user balance.

    """
    def __init__(self, business_id: int):
        self.business_id = business_id
        self.lock = Lock()

    def acquire(self) -> bool:
        return self.lock.acquire(timeout=1)

    def release(self):
        self.lock.release()

    def is_locked(self) -> bool:
        return self.lock.locked()


# Registered tokens
TOKENS = {
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMSJ9.UbKAsZGwbMcFBGMVXhAfg4WL4Lac-nhVZ4jegPtNlW0": "business-1",
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMiJ9.kzo-UvtHH9E1NhX12W11nMrK2lkJ0OkREd_c1RIgkgU": "business-2",
    "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw": "business-3"
}

app = Flask(__name__)
log = get_logger()

write_mutex = {}
accounts = {}
for i in range(1, 11):
    accounts.setdefault(i, 1000)

operation_number = ThreadSafeCounter()


def token_required(f):
    """Decorator used to validate routes that can only be accessed with a
    valid token.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Checks if the token is in the token list
        if request.headers.get("Authorization") not in TOKENS:
            return {"error": -1}, 401
        return f(*args, **kwargs)
    return decorated_function


@app.route("/lock", methods=("PUT", "DELETE"))
@token_required
def lock_route():
    operation_number.increment()

    # Check if the payload is empty
    if not request.json:
        # TODO Fix payload response
        log.error("Empty payload",
                  thread_name=current_thread().name,
                  operation_number=operation_number.counter)
        return {"error": -1}, 400

    data = request.json
    if request.method == "PUT":
        return process_account_lock(data)

    return process_account_unlock(data)


def process_account_unlock(data):
    # TODO Validate business id
    business_id = int(data["business_id"])
    account = int(data["account"])
    log.info("Releasing lock",
             business_id=business_id,
             account=account,
             operation_name="unlock",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

    try:
        write_mutex.setdefault(account, BusinessMutex(business_id))
        mutex = write_mutex[account]
        if mutex.business_id != business_id:
            log.error("Account is locked by a differente business server",
                      business_id=business_id,
                      business_id_with_lock=mutex.business_id,
                      account=account,
                      operation_name="lock",
                      operation_number=operation_number.counter,
                      thread_name=current_thread().name)
            return {"error": -1}, 403

        mutex.release()
        log.info("Lock released",
                 business_id=business_id,
                 account=account,
                 operation_name="unlock",
                 operation_number=operation_number.counter,
                 thread_name=current_thread().name)
        return {"error": 0}
    except RuntimeError:
        log.error("Lock already released",
                  business_id=business_id,
                  account=account,
                  operation_name="unlock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"error": -1}


def process_account_lock(data):
    # TODO Validate business id
    business_id = int(data["business_id"])
    account = int(data["account"])

    write_mutex.setdefault(account, BusinessMutex(business_id))
    mutex = write_mutex[account]
    if mutex.business_id != business_id:
        log.error("Account is already locked by a differente business server",
                  business_id=business_id,
                  business_id_with_lock=mutex.business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"error": -1}, 403

    if mutex.is_locked():
        log.error("Account is already locked",
                  business_id=business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"error": -1}

    locked = mutex.acquire()
    if locked:
        log.info("Lock acquired successfully",
                  business_id=business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"error": 0}
    else:
        log.error("Account is already locked, timeout exceeded",
                  business_id=business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"error": -1}

@app.route("/balance/<int:business_id>/<int:account>", methods=("GET", "PUT"))
@token_required
def balance_route(business_id, account):
    operation_number.increment()
    if request.method == "GET":
        return get_balance(business_id, account)
    else:
        amount = float(request.json["valor"])
        return update_balance(business_id, account,  amount)

def get_balance(business_id, account):
    log.info("Fetching account balance",
             business_id=business_id,
             account=account,
             operation_name="get_balance",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

    balance = accounts.get(account)
    if balance:
        log.info("Found account balance",
                 business_id=business_id,
                 account=account,
                 operation_name="get_balance",
                 operation_number=operation_number.counter,
                 thread_name=current_thread().name)
        return {
            "balance": balance,
            "error": 0
        }
    else:
        log.error("Account not found",
                 business_id=business_id,
                 account=account,
                 operation_name="get_balance",
                 operation_number=operation_number.counter,
                 thread_name=current_thread().name)
        return {"error": -1}, 404

def update_balance(business_id, account, amount):
    log.info("Updating account balance",
             business_id=business_id,
             account=account,
             operation_name="update_balance",
             operation_number=operation_number.counter,
             thread_name=current_thread().name)

    mutex = write_mutex.get(account)
    if not mutex:
        log.error("Account is not locked by any server",
                  business_id=business_id,
                  account=account,
                  operation_name="update_balance",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"error": -1}, 403

    if mutex.business_id != business_id:
        log.error("Account is already locked by a differente business server",
                  business_id=business_id,
                  business_id_with_lock=mutex.business_id,
                  account=account,
                  operation_name="update_balance",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"error": -1}, 403

    balance = accounts.get(account)
    if balance:
        accounts[account] = amount
        log.info("Account balance updated successfully",
                 business_id=business_id,
                 account=account,
                 operation_name="update_balance",
                 operation_number=operation_number.counter,
                 thread_name=current_thread().name)
        return {"error": 0}
    else:
        log.error("Account not found",
                 business_id=business_id,
                 account=account,
                 operation_name="update_balance",
                 operation_number=operation_number.counter,
                 thread_name=current_thread().name)
        return {"error": -1}, 404


if __name__ == "__main__":
    app.run()
