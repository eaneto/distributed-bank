import logging

from threading import Lock, current_thread
from functools import wraps

from flask import Flask, request, redirect, url_for
from structlog import get_logger

logging.basicConfig(
    filename='data.log',
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
operation_number = ThreadSafeCounter()


def token_required(f):
    """Decorator used to validate routes that can only be accessed with a
    valid token.

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Checks if the token is in the token list
        if request.headers["Authorization"] not in TOKENS:
            return {"data": -1}, 401
        return f(*args, **kwargs)
    return decorated_function


@app.route("/lock", methods=("PUT", "DELETE"))
@token_required
def lock_route():
    operation_number.increment()
    authorization_token = request.headers["Authorization"]
    if authorization_token not in TOKENS:
        log.error("Unauthorized request",
                  token=authorization_token,
                  thread_name=current_thread().name,
                  operation_number=operation_number.counter)
        return {"data": -1}, 401

    # Check if the payload is empty
    if not request.json:
        # TODO Fix payload response
        log.error("Empty payload",
                  thread_name=current_thread().name,
                  operation_number=operation_number.counter)
        return {"data": -1}, 400

    data = request.json
    if request.method == "PUT":
        return process_account_lock(data)

    return process_account_unlock(data)


def process_account_unlock(data):
    # TODO Validate business id
    business_id = data["id_negoc"]
    account = data["conta"]
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
            return {"data": -1}

        mutex.release()
        log.info("Lock released",
                 business_id=business_id,
                 account=account,
                 operation_name="unlock",
                 operation_number=operation_number.counter,
                 thread_name=current_thread().name)
        return {"data": 1}
    except RuntimeError:
        log.error("Lock already released",
                  business_id=business_id,
                  account=account,
                  operation_name="unlock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"data": -1}


def process_account_lock(data):
    # TODO Validate business id
    business_id = data["id_negoc"]
    account = data["conta"]

    write_mutex.setdefault(account, BusinessMutex(business_id))
    mutex = write_mutex[account]
    if mutex.business_id != business_id:
        log.error("Account is already locked, by a differente business server",
                  business_id=business_id,
                  business_id_with_lock=mutex.business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"data": -1}

    if mutex.is_locked():
        log.error("Account is already locked",
                  business_id=business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"data": -1}

    locked = mutex.acquire()
    if locked:
        log.info("Lock acquired successfully",
                  business_id=business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"data": 1}
    else:
        log.error("Account is already locked, timeout exceeded",
                  business_id=business_id,
                  account=account,
                  operation_name="lock",
                  operation_number=operation_number.counter,
                  thread_name=current_thread().name)
        return {"data": -1}

@app.route("/balace", methods=("GET", "PUT"))
@token_required
def balance_route():
    return


if __name__ == "__main__":
    app.run()
