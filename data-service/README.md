# Data Service (serviço de dados)

Serviço responsável por armazenar e administrar o acesso aos dados do
usuário pelo mecanismo de exclusão mútua. As possíveis operações sao:

- Consulta de Saldo
- Lock dos dados(para escrita)

## Rota de operações de Lock

### URI

```
/lock
```

### Rodando o curl local para lock

```bash
curl -iX PUT -H 'Content-Type: application/json' \
    -H 'Authorization: Basic super-valid-token' \
    -d '{"business_id": 1, "account": 2}' \
    http://127.0.0.1:5001/lock
```

### Rodando o curl local para unlock

```bash
curl -iX DELETE -H 'Content-Type: application/json' \
    -H 'Authorization: Basic super-valid-token' \
    -d '{"business_id": 1, "account": 2}' \
    http://127.0.0.1:5001/lock
```

## Consulta de Saldo

### URI

```
/balance/<int:business_id>/<int:account>
```

### Rodando o curl local

```bash
curl -iX GET -H 'Content-Type: application/json' \
    -H 'Authorization: Basic super-valid-token' \
    http://127.0.0.1:5001/balance/2
```
