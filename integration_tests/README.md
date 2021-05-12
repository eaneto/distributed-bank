# Testes de integração automatizados

Para garantirmos a qualidade do projeto e que não iríamos subir nenhum
bug com nossas alterações criamos alguns cenários de teste dos
serviços desenvolvidos. A ideia é ter apenas testes de integração e
não unitários, já que nesse caso testes integrados foram mais simples
e efetivos de serem desenvolvidos.

## Rodando os testes

Para rodar os teste é preciso ter os serviços rodando na máquina
local, já que eles são acessados via localhost.

### Exemplo

Para rodar os testes do serviço de negócio.

```bash
python3 ../data-service/data.py &
python3 ../business-service/business.py &

# Com os serviços de pé rode o teste
pytest business_service_test.py
```

## Testes serviço de dados

Arquivos:
- `data_service_test.py`

Os testes do serviço de dados buscam validar que a integração com os
endpoints da API estão ocorrendo da forma esperada, retornando as
informações corretas e cenários com N chamadas para validar uma
regra. Como por exemplo adquirir o lock de uma conta e depois tentar
adquirir o lock novamente.

### Como rodar

```bash
python3 ../data-service/data.py &

# Com os serviços de pé rode o teste
pytest data_service_test.py
```

## Testes serviço de negócio

Arquivos:
- `business_service_test.py`
- `business_service_test_with_multiple_operations.py`

Os testes desse serviço precisam do serviço de dados rodando além do
serviço de negócio. Jà que o serviço de negócio realiza chamadas a API
do serviço de dados. Os testes do serviço de negócio estão mais
focados em testar, além das regras implementadas, a integração dele
com o serviço de dados, já que é uma integração crítica para a
aplicação.

### Como rodar

```bash
python3 ../data-service/data.py &
python3 ../business-service/business.py &

# Com os serviços de pé rode o teste
pytest business_service_test.py
# ou
pytest business_service_test_with_multiple_operations.py
```
