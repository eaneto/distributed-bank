import json
import time

import requests

VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiY2xpZW50LTEifQ.J4rxFfc7zCJTCxys49JxN1lWCHVfZLlMj5EauhYJ4-k"
APP_URL = "http://localhost:5001"

def test_transfer_between_accounts_with_valid_token():
    # Account used on deposits
    deposit_account = 1
    # Account used for withdraws
    withdraw_account = 2
    # Accounts used for transfers
    debit_account = 3
    credit_account = 4
    amount = 100.0
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + VALID_TOKEN
    }

    # Deposit twice on the same account
    response = requests.post(
        "{}/deposit/{}/{}".format(APP_URL,deposit_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.post(
        "{}/deposit/{}/{}".format(APP_URL,deposit_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    # Withdraw twice from the same account
    response = requests.post(
        "{}/withdraw/{}/{}".format(APP_URL,withdraw_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.post(
        "{}/withdraw/{}/{}".format(APP_URL,withdraw_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.post(
        "{}/transfer/{}/{}/{}".format(APP_URL,
            debit_account, credit_account, amount
        ),
        headers=headers
    )

    assert response.status_code == 200

    # Wait for 5 seconds so the background job can process the whole
    # queue
    time.sleep(10)

    # Validate the final balance for each account
    response = requests.get("{}/balance/{}".format(APP_URL,
        deposit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1200

    response = requests.get("{}/balance/{}".format(APP_URL,
        withdraw_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 800

    response = requests.get("{}/balance/{}".format(APP_URL,
        debit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 900

    response = requests.get("{}/balance/{}".format(APP_URL,
        credit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1100
