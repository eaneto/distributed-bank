# Data Service (serviço de dados)

Serviço responsável por armazenar e administrar o acesso aos dados do
usuário pelo mecanismo de exclusão mútua. As possíveis operações sao:

- Consulta e atualização de Saldo
- Lock da conta(para escrita)

## Definição da API com Swagger

Para verificar a definição da API com o swagger acesse o site
https://editor.swagger.io/ e carrege o conteúdo do arquivo
`data-api.yml`.


## Lock

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

## Saldo

### URI

```
/balance/<int:business_id>/<int:account>
```

### Consultando saldo

```bash
curl -iX GET -H 'Content-Type: application/json' \
    -H 'Authorization: Basic super-valid-token' \
    http://127.0.0.1:5001/balance/1/2
```

### Atualizando saldo

```bash
curl -iX PUT -H 'Content-Type: application/json' \
    -H 'Authorization: Basic super-valid-token' \
    -d '{"valor": 100.0}' \
    http://127.0.0.1:5001/balance/1/2
```
