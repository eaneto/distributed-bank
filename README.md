# distributed-bank

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

## Testes

Para rodar todos os testes de integração é apenas necessário executar
o seguinte comando no shell.

> Importante rodar esse script sem ter nenhum dos serviços rodando, já
> que esse script sobe e derruba os serviços pra cada teste.

```bash
./run_integration-tests.sh
```
