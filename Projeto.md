# Projeto

O objetivo do projeto era contruír uma arquitetura para um banco
distruído. Neste banco as operações disponíveis seriam consulta de
saldo, depósitos, saques e transferências.

## Escolhas de arquitetura

![Visão Geral da Arquitetura](./docs/diagrama-visao-geral.png)

### Cliente



### Serviço de negócio

- Background job
  - Desacoplamento com serviço de dados

### Serviço de dados

