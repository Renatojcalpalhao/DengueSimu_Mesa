# api/dengue_api.py
import random

def obter_dados_dengue_sp():
    """
    Retorna valores simulados de dengue para evitar erros de API real.
    """

    casos = random.randint(80, 320)

    if casos < 120:
        alerta = "Verde"
    elif casos < 180:
        alerta = "Amarelo"
    elif casos < 250:
        alerta = "Laranja"
    else:
        alerta = "Vermelho"

    return {
        "casos_reais": casos,
        "alerta": alerta
    }
