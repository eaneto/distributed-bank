import json

import requests

def test_acquire_lock_without_token():
    payload = {
        "id_negoc": 1,
        "conta": 1
    }
    headers={
        "Content-Type": "application/json"
    }
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 401

def test_acquire_lock_with_invalid_token():
    payload = {
        "id_negoc": 1,
        "conta": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic invalid-token"
    }
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 401

def test_acquire_lock_with_valid_token():
    payload = {
        "id_negoc": 1,
        "conta": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

def test_already_acquired_lock_with_valid_token():
    payload = {
        "id_negoc": 1,
        "conta": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == -1

def test_already_acquired_lock_by_different_server_with_valid_token():
    payload = {
        "id_negoc": 2,
        "conta": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 403
    assert response.json()["error"] == -1

def test_unlock_with_valid_token():
    payload = {
        "id_negoc": 1,
        "conta": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }
    response = requests.delete("http://localhost:5000/lock",
                               headers=headers, data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

def test_unlock_locked_by_differente_server_with_valid_token():
    payload = {
        "id_negoc": 2,
        "conta": 1
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }
    response = requests.delete("http://localhost:5000/lock",
                               headers=headers, data=json.dumps(payload))

    assert response.status_code == 403
    assert response.json()["error"] == -1

def test_get_balance_with_valid_token():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }
    response = requests.get("http://localhost:5000/balance/{}/{}".format(1, 1),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000
    assert response.json()["error"] == 0

def test_get_balance_with_invalid_token():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic invalid"
    }
    response = requests.get("http://localhost:5000/balance/{}/{}".format(1, 1),
        headers=headers)

    assert response.status_code == 401
    assert response.json()["error"] == -1

def test_get_balance_lock_by_same_business_id_with_valid_token():
    business_id = 1
    account = 1
    payload = {
        "id_negoc": business_id,
        "conta": account
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }

    # Given account is locked
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

    # When balance is fetched
    response = requests.get(
        "http://localhost:5000/balance/{}/{}".format(business_id, account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000
    assert response.json()["error"] == 0

    # After unlock account
    response = requests.delete("http://localhost:5000/lock",
                               headers=headers,
                               data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

def test_get_balance_lock_by_different_business_id_with_valid_token():
    business_id = 1
    account = 1
    payload = {
        "id_negoc": business_id,
        "conta": account
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }

    # Given account is locked
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

    # When balance is fetched by differente business service
    response = requests.get(
        "http://localhost:5000/balance/{}/{}".format(business_id + 1, account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == 1000
    assert response.json()["error"] == 0

    # After unlock account
    response = requests.delete("http://localhost:5000/lock",
                               headers=headers,
                               data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

def test_update_balance_not_locked_with_valid_token():
    business_id = 1
    account = 7
    amount = 100.0
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }

    response = requests.put(
        "http://localhost:5000/balance/{}/{}".format(business_id, account),
        headers=headers, data=json.dumps({"valor": amount}))

    assert response.status_code == 403
    assert response.json()["error"] == -1

def test_update_balance_lock_by_different_business_id_with_valid_token():
    business_id = 1
    account = 1
    payload = {
        "id_negoc": business_id,
        "conta": account
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }

    # Given account is locked
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

    # When balance is fetched by differente business service
    response = requests.put(
        "http://localhost:5000/balance/{}/{}".format(business_id + 1, account),
        data=json.dumps({"valor": 120}),
        headers=headers)

    assert response.status_code == 403
    assert response.json()["error"] == -1

    # After unlock account
    response = requests.delete("http://localhost:5000/lock",
                               headers=headers,
                               data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

def test_update_balance_lock_by_same_business_id_with_valid_token():
    business_id = 1
    account = 1
    amount = 120
    payload = {
        "id_negoc": business_id,
        "conta": account
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMyJ9.MxBz8eYS-HDI9PvSoCOXmtgUXoKs5PA4_JyZXvD8oQw"
    }

    # Given account is locked
    response = requests.put("http://localhost:5000/lock",
                            headers=headers, data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0

    # When balance is updated by same business service
    response = requests.put(
        "http://localhost:5000/balance/{}/{}".format(business_id, account),
        data=json.dumps({"valor": amount}),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["error"] == 0

    # Then balance is updated to amount
    response = requests.get(
        "http://localhost:5000/balance/{}/{}".format(business_id + 1, account),
        headers=headers)

    assert response.status_code == 200
    assert response.json()["balance"] == amount
    assert response.json()["error"] == 0

    # After unlock account
    response = requests.delete("http://localhost:5000/lock",
                               headers=headers,
                               data=json.dumps(payload))

    assert response.status_code == 200
    assert response.json()["error"] == 0
