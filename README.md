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
```

## Componentes

### Data Service (Serviço de Dados)

### Business Service (Serviço de Negócios)

## Testes

Para rodar todos os testes de integração é apenas necessário executar
o seguinte comando no shell.

> Importante rodar esse script sem ter nenhum dos serviços rodando

```bash
./run_integration_tests.sh
```
