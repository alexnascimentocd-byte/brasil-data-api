"""
Brasil Data API — API REST para consultas de dados brasileiros.
Endpoints: CPF, CNPJ, CEP, DDD, Bancos, Feriados
Deploy: Railway / Render (grátis)
"""

from flask import Flask, jsonify, request
import re
import json
import urllib.request
import urllib.error
from functools import wraps
import time
from collections import defaultdict

app = Flask(__name__)

# Rate limiting simples
rate_limit = defaultdict(list)
RATE_LIMIT_REQUESTS = 30  # requests
RATE_LIMIT_WINDOW = 60  # seconds

def limit_rate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr or 'unknown'
        now = time.time()
        # Limpa requests antigos
        rate_limit[ip] = [t for t in rate_limit[ip] if now - t < RATE_LIMIT_WINDOW]
        if len(rate_limit[ip]) >= RATE_LIMIT_REQUESTS:
            return jsonify({"error": "Rate limit excedido. Máximo 30 req/min"}), 429
        rate_limit[ip].append(now)
        return f(*args, **kwargs)
    return decorated


def https_get(url, timeout=10):
    """GET request returning parsed JSON."""
    req = urllib.request.Request(url, headers={"User-Agent": "BrasilDataAPI/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "url": url}
    except Exception as e:
        return {"error": str(e), "url": url}


# ==================== ENDPOINTS ====================

@app.route("/")
def home():
    return jsonify({
        "name": "Brasil Data API",
        "version": "1.0.0",
        "endpoints": {
            "/api/cpf/<cpf>": "Valida CPF (matemático)",
            "/api/cnpj/<cnpj>": "Consulta CNPJ (BrasilAPI/ReceitaWS)",
            "/api/cep/<cep>": "Consulta CEP (ViaCEP)",
            "/api/ddd/<ddd>": "Consulta DDD (BrasilAPI)",
            "/api/bancos": "Lista bancos brasileiros",
            "/api/feriados/<ano>": "Feriados nacionais do ano",
            "/api/busca/<query>": "Auto-detecta tipo e consulta",
        },
        "docs": "Use os endpoints acima com dados numéricos",
        "rate_limit": f"{RATE_LIMIT_REQUESTS} requests/{RATE_LIMIT_WINDOW}s"
    })


@app.route("/api/cpf/<cpf>")
@limit_rate
def api_cpf(cpf):
    """Valida CPF matematicamente."""
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11:
        return jsonify({"cpf": cpf, "valido": False, "error": "CPF deve ter 11 dígitos"}), 400

    # Descarta CPFs com todos dígitos iguais
    if cpf == cpf[0] * 11:
        return jsonify({"cpf": cpf, "valido": False, "motivo": "Todos os dígitos são iguais"})

    # Validação dígito 1
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if int(cpf[9]) != resto:
        return jsonify({"cpf": cpf, "valido": False, "motivo": "Dígito verificador 1 inválido"})

    # Validação dígito 2
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if int(cpf[10]) != resto:
        return jsonify({"cpf": cpf, "valido": False, "motivo": "Dígito verificador 2 inválido"})

    # Formata
    cpf_fmt = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return jsonify({"cpf": cpf, "cpf_formatado": cpf_fmt, "valido": True})


@app.route("/api/cnpj/<cnpj>")
@limit_rate
def api_cnpj(cnpj):
    """Consulta CNPJ — BrasilAPI primeiro, fallback ReceitaWS."""
    cnpj = re.sub(r"\D", "", cnpj)
    if len(cnpj) != 14:
        return jsonify({"error": "CNPJ deve ter 14 dígitos"}), 400

    # Tentativa 1: BrasilAPI
    data = https_get(f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}")
    if "error" not in data and "razao_social" in data:
        return jsonify({"source": "BrasilAPI", **data})

    # Tentativa 2: ReceitaWS
    data = https_get(f"https://receitaws.com.br/v1/cnpj/{cnpj}")
    if "error" not in data and "status" in data:
        return jsonify({"source": "ReceitaWS", **data})

    return jsonify({"error": f"Não foi possível consultar CNPJ {cnpj}"}), 502


@app.route("/api/cep/<cep>")
@limit_rate
def api_cep(cep):
    """Consulta CEP pelo ViaCEP."""
    cep = re.sub(r"\D", "", cep)
    if len(cep) != 8:
        return jsonify({"error": "CEP deve ter 8 dígitos"}), 400

    data = https_get(f"https://viacep.com.br/ws/{cep}/json/")
    if data.get("erro"):
        return jsonify({"error": f"CEP {cep} não encontrado"}), 404
    if "error" in data:
        return jsonify(data), 502
    return jsonify(data)


@app.route("/api/ddd/<ddd>")
@limit_rate
def api_ddd(ddd):
    """Consulta DDD pelo BrasilAPI."""
    ddd = re.sub(r"\D", "", ddd)
    if len(ddd) != 2:
        return jsonify({"error": "DDD deve ter 2 dígitos"}), 400

    data = https_get(f"https://brasilapi.com.br/api/ddd/v1/{ddd}")
    if "error" in data:
        return jsonify(data), 502
    return jsonify({"DDD": ddd, **data})


@app.route("/api/bancos")
@limit_rate
def api_bancos():
    """Lista bancos pelo BrasilAPI."""
    data = https_get("https://brasilapi.com.br/api/banks/v1")
    if isinstance(data, list):
        return jsonify({"total": len(data), "bancos": data})
    return jsonify(data), 502


@app.route("/api/feriados/<ano>")
@limit_rate
def api_feriados(ano):
    """Lista feriados nacionais pelo BrasilAPI."""
    if not ano.isdigit() or len(ano) != 4:
        return jsonify({"error": "Ano inválido (formato: YYYY)"}), 400

    data = https_get(f"https://brasilapi.com.br/api/feriados/v1/{ano}")
    if isinstance(data, list):
        return jsonify({"ano": int(ano), "total": len(data), "feriados": data})
    if "error" in data:
        return jsonify(data), 502
    return jsonify(data), 502


@app.route("/api/busca/<query>")
@limit_rate
def api_busca(query):
    """Auto-detecta tipo (CPF/CNPJ/CEP/DDD) e consulta automaticamente."""
    digits = re.sub(r"\D", "", query)
    length = len(digits)

    if length == 8:
        return api_cep(query)
    elif length == 11:
        return api_cpf(query)
    elif length == 14:
        return api_cnpj(query)
    elif length == 2:
        return api_ddd(query)
    else:
        return jsonify({
            "error": "Não foi possível detectar o tipo",
            "dígitos": length,
            "dica": "Use 8 dígitos (CEP), 11 (CPF), 14 (CNPJ) ou 2 (DDD)"
        }), 400


# ==================== HEALTH CHECK ====================

@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "Brasil Data API"})


# ==================== MAIN ====================

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
