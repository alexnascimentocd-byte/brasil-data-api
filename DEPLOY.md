## 🚀 Deploy no Render (100% grátis, 24/7)

### Passo a passo:
1. Acesse: https://render.com
2. Crie conta grátis (com CPF)
3. Clique "New +" → "Web Service"
4. Conecte GitHub → Selecione `brasil-data-api`
5. Configure:
   - **Name**: brasil-data-api
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free
6. Clique "Create Web Service"
7. Aguarde ~2 minutos
8. URL será: https://brasil-data-api.onrender.com

### Teste:
```
https://brasil-data-api.onrender.com/api/cpf/12345678901
https://brasil-data-api.onrender.com/api/cnpj/11222333000181
https://brasil-data-api.onrender.com/api/cep/01001000
https://brasil-data-api.onrender.com/api/ddd/48
https://brasil-data-api.onrender.com/api/bancos
https://brasil-data-api.onrender.com/api/feriados/2026
https://brasil-data-api.onrender.com/api/busca/12345678901
```

### ⚠️ Notas:
- Plano free: dorme após 15min inativo (acorda em ~30s)
- Para 24/7 sem dormir: use cron job ping a cada 14min
- Rate limit: 30 req/min por IP
