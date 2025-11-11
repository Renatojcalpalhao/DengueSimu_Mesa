import requests
from datetime import datetime, timedelta
import random

def obter_clima_sao_paulo_inmet():
    """Obtém dados reais do INMET com fallback para simulação."""
    base_url = "https://apitempo.inmet.gov.br/estacao/diaria"
    hoje = datetime.utcnow().date()
    ontem = hoje - timedelta(days=2)  # usa dados de 2 dias atrás (garante disponibilidade)
    estacao = "A701"  # São Paulo - Mirante de Santana

    url = f"{base_url}/{ontem}/{hoje}/{estacao}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        dados = resp.json()

        if not dados or len(dados) == 0:
            raise ValueError("Sem dados do INMET")

        dia = dados[-1]
        temperatura = float(dia.get("TEM_MAX", 26))
        umidade = float(dia.get("UMD_MAX", 70))
        chuva = float(dia.get("CHUVA", 0))
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌤️ Clima real INMET: T={temperatura:.1f}°C, U={umidade:.0f}%, Chuva={chuva:.1f}mm")
        return {"temperatura": temperatura, "umidade": umidade, "chuva": chuva}

    except Exception as e:
        print(f"⚠️ Erro ao obter dados do INMET ({e}) — usando simulação.")
        temperatura = 26 + random.uniform(-2, 2)
        umidade = 65 + random.uniform(-5, 10)
        chuva = max(0, random.uniform(0, 1) - 0.3)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Clima simulado: T={temperatura:.1f}°C, U={umidade:.0f}%, Chuva={chuva:.2f}")
        return {"temperatura": round(temperatura, 1), "umidade": round(umidade, 1), "chuva": round(chuva, 2)}
