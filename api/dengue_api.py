import requests
import random
from datetime import datetime

_alertas = ["Verde", "Amarelo", "Laranja", "Vermelho"]

def obter_dados_dengue_sp():
    """Obtém dados reais da API InfoDengue (Fiocruz) com fallback seguro."""
    try:
        url = "https://info.dengue.mat.br/api/alertcity"
        params = {"geocode": "3550308"}  # São Paulo/SP
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        dados = resp.json()

        if not dados or "resultados" not in dados or len(dados["resultados"]) == 0:
            raise ValueError("Sem dados InfoDengue")

        ultimo = dados["resultados"][-1]
        casos_reais = int(ultimo.get("casos_est", 150))
        alerta = ultimo.get("nivel", "Verde").capitalize()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🦟 Dengue real InfoDengue: {casos_reais} casos, Alerta={alerta}")
        return {"casos_reais": casos_reais, "alerta": alerta}

    except Exception as e:
        print(f"⚠️ Erro ao obter dados de dengue ({e}) — usando simulação.")
        casos_reais = random.randint(100, 300)
        alerta = random.choice(_alertas)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Dengue simulada: {casos_reais} casos, Alerta={alerta}")
        return {"casos_reais": casos_reais, "alerta": alerta}
