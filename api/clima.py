# api/clima.py
import random

def obter_clima_sao_paulo_inmet():
    """
    Gera clima artificial estável para evitar erros da API real.
    """
    temperatura = random.uniform(23, 30)
    umidade = random.uniform(55, 85)
    chuva = random.uniform(0, 0.8)

    return {
        "temperatura": round(temperatura, 1),
        "umidade": int(umidade),
        "chuva": round(chuva, 2),
    }
