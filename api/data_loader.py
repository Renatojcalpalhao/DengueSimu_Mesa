# Arquivo: api/data_loader.py

import random

def get_densidade_fator_por_coordenada(width, height, pos_x, pos_y):
    """
    Simula a atribuição de um fator de densidade e risco estrutural a uma célula (x, y)
    baseado na localização simulada (substituindo a leitura de GeoSampa).
    
    Retorna: (fator_densidade, fator_risco_estrutural)
    """
    
    fator_densidade = 1.0
    fator_risco_estrutural = 0.5

    # 1. Simulação de Áreas de Alta Densidade/Risco (Ex: Centro)
    # Assumimos que o centro (onde há mais movimento e edifícios) está no quadrante 
    # superior-esquerdo do nosso grid simulado.
    if pos_x < width / 3 and pos_y < height / 3:
        fator_densidade = 3.5  # População muito concentrada
        fator_risco_estrutural = 0.9 # Risco base alto (infraestrutura, esgoto)
    
    # 2. Simulação de Áreas de Densidade Média/Risco (Ex: Zonas Residenciais)
    elif (width / 3 <= pos_x < 2 * width / 3) and (height / 3 <= pos_y < 2 * height / 3):
        fator_densidade = 1.5
        fator_risco_estrutural = 0.5 
    
    # 3. Simulação de Áreas de Baixa Densidade/Risco (Ex: Zonas Rurais/Periferia)
    else:
        fator_densidade = 0.6
        fator_risco_estrutural = 0.2 # Menor risco base (menos lixo concentrado)
        
    return fator_densidade, fator_risco_estrutural

# --------------------------------------------------------------------------
# FUTURA INTEGRAÇÃO: Módulo para Coordenadas de UBSs
# Você usará isso para simular a logística da vacina.
UBS_COORDS = [
    (10, 10), (30, 80), (75, 25), (90, 90) # Coordenadas simuladas para as UBSs
]

def get_ubs_locations(num_ubs=4):
    """Retorna coordenadas simuladas de UBSs para o modelo."""
    return UBS_COORDS[:num_ubs]