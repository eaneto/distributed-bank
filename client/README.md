# Client

Programa responsável por gerar operações aleatórias em uma quantidade
N de serviços de negócio configurados. Para configurar os servidores
de negócio basta definir a variável de ambiente `BUSINESS_URLS`. Como
no exemplo abaixo.

```bash
export BUSINESS_URLS="http://localhost:49184,http://localhost:49181,http://localhost:49183"
```

Se a variável não for configurada será usado o valor de fallback,
`http://localhost:5001`.
