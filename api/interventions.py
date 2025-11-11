# Arquivo: interventions.py

from agents.human import Human
import random

def aplicar_vacinacao(model, porcentagem_alvo=0.1):
    """
    Vacina uma porcentagem da população de agentes Humanos.
    """
    
    # Lista todos os agentes Humanos não infectados e não vacinados
    agentes_vulneraveis = [
        a for a in model.schedule.agents 
        if isinstance(a, Human) and not a.infectado and not a.vacinado
    ]
    
    # Calcula quantos agentes vacinar
    num_a_vacinar = int(len(agentes_vulneraveis) * porcentagem_alvo)
    
    # Seleciona aleatoriamente e vacina
    agentes_selecionados = random.sample(agentes_vulneraveis, min(num_a_vacinar, len(agentes_vulneraveis)))
    
    for agente in agentes_selecionados:
        agente.vacinado = True
        
    print(f"✅ Passo {model.step_count}: {len(agentes_selecionados)} humanos vacinados.")