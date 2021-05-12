import json
import time

import requests

VALID_TOKEN = "super-valid-token"

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
        "http://localhost:5001/deposit/{}/{}".format(deposit_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.post(
        "http://localhost:5001/deposit/{}/{}".format(deposit_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    # Withdraw twice from the same account
    response = requests.post(
        "http://localhost:5001/withdraw/{}/{}".format(withdraw_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.post(
        "http://localhost:5001/withdraw/{}/{}".format(withdraw_account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.post(
        "http://localhost:5001/transfer/{}/{}/{}".format(
            debit_account, credit_account, amount
        ),
        headers=headers
    )

    assert response.status_code == 200

    # Wait for 5 seconds so the background job can process the whole
    # queue
    time.sleep(5)

    # Validate the final balance for each account
    response = requests.get("http://localhost:5001/balance/{}".format(
        deposit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1200

    response = requests.get("http://localhost:5001/balance/{}".format(
        withdraw_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 800

    response = requests.get("http://localhost:5001/balance/{}".format(
        debit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 900

    response = requests.get("http://localhost:5001/balance/{}".format(
        credit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1100
