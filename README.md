# distributed-bank

| Nome                            | TIA      |
| ------------------------------- | -------- |
| Edison Aguiar de Souza Neto     | 31812295 |
| Luiz Fernando Tagliaferro Brito | 31861806 |

Serviço simplificado de um Banco distribuído.

O Serviço é escrito em python com a principal dependência sendo o
Flask. Para subir a aplicação local você precisa ter o python 3
instalado. Com ele instalado siga o passo abaixo para instalar todas
as dependências sem gerar conflitos com as dependências da sua
máquina.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Componentes

![Visão Geral da Arquitetura](./docs/diagrama-visao-geral.png)

### Data Service (Serviço de Dados)

Serviço responsável por gerenciar os dados das contas bancárias. Pela
sua api é possível obter lock de contas, consultar e atualizar o saldo
de contas.

### Business Service (Serviço de Negócios)

Serviço responsável por implementar as regras de negócio do banco e
expôr a API de operações do banco, como saque e depósito.

### Client

O client é um script simples que roda operações aleatórias em contas
aleatórias com valores aleatórias para gerar uma carga 100% aleatória
nos serviços.

## Testes

Para rodar todos os testes de integração é apenas necessário executar
o seguinte comando no shell.

> Importante rodar esse script sem ter nenhum dos serviços rodando, já
> que esse script sobe e derruba os serviços pra cada teste.

```bash
./run_integration-tests.sh
```

## Rodando os serviços com o docker

Para subir o projeto com o docker compose, subindo containers para o
servidor de dados, negócio e os clientes.

```bash
docker-compose up -d
```

Para visualizar o log das operações ocorrendo nos servidores de
negócios. São iniciados 3 containers do servidor de negócio, portanto
escolha um deles para visualizar os logs.

**Exemplo:**

```bash
docker exec -it business1 tail -f /business.log
```
