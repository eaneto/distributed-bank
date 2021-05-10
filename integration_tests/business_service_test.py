import json

import requests

VALID_TOKEN = "super-valid-token"
INVALID_TOKEN = "super-invalid-token"


def test_get_balance_with_valid_token():
    account = 1
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + VALID_TOKEN
    }
    response = requests.get("http://localhost:5001/balance/{}".format(account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000

def test_get_balance_with_invalid_token():
    account = 1
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + INVALID_TOKEN
    }
    response = requests.get("http://localhost:5001/balance/{}".format(account),
        headers=headers)

    assert response.status_code == 401

def test_deposit_account_with_valid_token():
    account = 1
    amount = 10.0
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + VALID_TOKEN
    }

    response = requests.post(
        "http://localhost:5001/deposit/{}/{}".format(account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.get("http://localhost:5001/balance/{}".format(account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000


def test_withdraw_account_with_valid_token():
    account = 2
    amount = 100.0
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + VALID_TOKEN
    }

    response = requests.post(
        "http://localhost:5001/withdraw/{}/{}".format(account, amount),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.get("http://localhost:5001/balance/{}".format(account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000


def test_transfer_between_accounts_with_valid_token():
    debit_account = 3
    credit_account = 4
    amount = 100.0
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic " + VALID_TOKEN
    }

    response = requests.post(
        "http://localhost:5001/transfer/{}/{}/{}".format(
            debit_account, credit_account, amount
        ),
        headers=headers
    )

    assert response.status_code == 200

    response = requests.get("http://localhost:5001/balance/{}".format(
        debit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000

    response = requests.get("http://localhost:5001/balance/{}".format(
        credit_account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000
