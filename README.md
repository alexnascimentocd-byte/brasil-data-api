# Brasil Data API 🇧🇷

API REST para consultas de dados brasileiros — 100% gratuita.

## Endpoints

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/cpf/<cpf>` | Valida CPF |
| `GET /api/cnpj/<cnpj>` | Consulta CNPJ |
| `GET /api/cep/<cep>` | Consulta CEP |
| `GET /api/ddd/<ddd>` | Consulta DDD |
| `GET /api/bancos` | Lista bancos |
| `GET /api/feriados/<ano>` | Feriados nacionais |
| `GET /api/busca/<query>` | Auto-detecta tipo |

## Deploy

### Railway (grátis)
1. Conecte repositório GitHub
2. Deploy automático

### Render (grátis)
1. New Web Service
2. Build: `pip install -r requirements.txt`
3. Start: `gunicorn app:app`

## Rate Limit
30 requests por minuto por IP.

## Tecnologias
- Flask
- BrasilAPI (CNPJ, DDD, Bancos, Feriados)
- ViaCEP (CEP)
- ReceitaWS (CNPJ fallback)
