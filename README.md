# distributed-bank

## Adquirir lock para a conta

```bash
curl -iX PUT -d '{"id_negoc": 123, "conta": 1}' -H 'Content-Type: application/json' http://127.0.0.1:5000/lock

curl -iX PUT -d '{"id_negoc": 1234, "conta": 1}' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiYnVzaW5lc3MtMSJ9.UbKAsZGwbMcFBGMVXhAfg4WL4Lac-nhVZ4jegPtNlW0' \
    http://127.0.0.1:5000/lock
```

## Liberando o lock

```bash
curl -iX DELETE -d '{"id_negoc": 123, "conta": 1}' -H 'Content-Type: application/json' http://127.0.0.1:5000/lock
```
