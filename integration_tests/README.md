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

pytest business_service_test.py
```

## Testes serviço de dados

Os testes do serviço de dados
