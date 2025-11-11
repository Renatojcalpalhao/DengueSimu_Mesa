from mesa import Agent
import random
# from .mosquito import Mosquito <-- REMOVIDO DO TOPO


class Environment(Agent):
    """
    Agente que representa uma célula na grade e seus fatores ambientais
    (Focos de risco, capacidade de carga e densidade estrutural).
    """

    tipo = "Ambiente"
    
    def __init__(self, unique_id, model, fator_densidade, fator_risco_estrutural):
        super().__init__(unique_id, model)
        
        # Fatores geográficos permanentes
        self.fator_densidade = fator_densidade         
        self.risco_foco = fator_risco_estrutural       
        
        # Capacidade de carga é proporcional ao risco estrutural
        self.capacidade_mosquito = 10 * self.risco_foco 
        
    def atualizar_risco(self):
        """
        Atualiza o risco de foco com base no clima global (chuva e umidade).
        """
        
        chuva = self.model.chuva_simulada
        umidade = self.model.umidade_ambiente 
        
        fator_aumento = (chuva + umidade / 100.0) * 0.02 * self.fator_densidade
        
        self.risco_foco = min(1.0, self.risco_foco + fator_aumento)
        self.risco_foco *= 0.98

        self.capacidade_mosquito = 10 * self.risco_foco 

    def step(self):
        """Método executado a cada passo do tempo."""
        self.atualizar_risco()