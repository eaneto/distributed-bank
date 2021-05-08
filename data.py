import logging

from threading import Lock

from flask import Flask, request
from structlog import get_logger

logging.basicConfig(
    filename='data.log',
    encoding='utf-8',
    level=logging.DEBUG
)

app = Flask(__name__)
log = get_logger()

write_mutex = {}
acounts = {}


@app.route("/lock", methods=("PUT", "DELETE"))
def lock_route():
    # Check if the payload is empty
    if not request.json:
        # TODO Fix payload response
        log.error("Empty payload")
        return {}, 400

    data = request.json
    if request.method == "POST":
        return process_account_lock(data)

    return process_account_unlock(data)


def process_account_unlock(data):
    # TODO Validate business id
    business_id = data["id_negoc"]
    account = data["conta"]
    log.info("Acquiring lock",
             id_negoc=business_id,
             conta=account)
    try:
        write_mutex.setdefault(account, Lock())
        write_mutex[account].release()
        return {"data": 1}
    except RuntimeError:
        return {"data": -1}


def process_account_lock(data):
    # TODO Validate business id
    business_id = data["id_negoc"]
    account = data["conta"]

    write_mutex.setdefault(account, Lock())
    mutex = write_mutex[account]
    if mutex.locked():
        return {"data": -1}

    locked = mutex.acquire(timeout = 1)
    if locked:
        return {"data": 1}
    else:
        return {"data": -1}

@app.route("/balace", methods=("GET", "PUT"))
def balance_route():
    return


if __name__ == "__main__":
    app.run()
