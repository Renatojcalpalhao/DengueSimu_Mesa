# api/data_loader.py
import random

def get_densidade_fator_por_coordenada(w, h, x, y):
    """
    Gera fatores estruturais artificiais para o ambiente.
    """
    fator_densidade = random.uniform(0.1, 1.0)
    fator_risco = random.uniform(0.1, 1.0)
    return fator_densidade, fator_risco
