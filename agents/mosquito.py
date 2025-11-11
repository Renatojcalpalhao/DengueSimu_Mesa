from mesa import Agent
import random
# from .human import Human <-- REMOVIDO DO TOPO
# from .environment import Environment <-- REMOVIDO DO TOPO

class Mosquito(Agent):
    """
    Um agente vetor (Aedes aegypti) no modelo de Dengue, sensível ao clima.
    """
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
        # --- Atributos de Saúde e Transmissão ---
        self.infectado = False
        self.tempo_vida = 0
        self.prob_infectar_humano = model.taxa_infeccao
        self.prob_contagio_mosquito = model.taxa_infeccao 
        self.vida_maxima_base = model.vida_media_mosquito 
        
        # --- Atributos de Movimentação e Ambiente ---
        self.raio_movimento = 2 

    def get_fator_clima(self):
        """Calcula o fator de desempenho do mosquito baseado na Temperatura Ambiente."""
        
        temp = self.model.temperatura_ambiente
        
        if 25.0 <= temp <= 30.0:
            return 1.2 
        elif 20.0 <= temp < 25.0 or 30.0 < temp <= 35.0:
            return 0.8
        else:
            return 0.5 

    def mover(self):
        """Movimento aleatório do mosquito."""
        fator_clima = self.get_fator_clima()
        
        raio = self.raio_movimento if fator_clima >= 0.8 else 1
            
        if not self.pos: return

        vizinhanca = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=raio
        )
        if vizinhanca:
            nova_posicao = self.random.choice(vizinhanca)
            self.model.grid.move_agent(self, nova_posicao)

    def reproduzir(self):
        """Implementa a reprodução do mosquito, influenciada pelo risco e clima."""
        
        # IMPORTAÇÃO ADIADA 1: Quebra o ciclo com Environment
        from .environment import Environment 
        from .mosquito import Mosquito # Para autocriação
        
        agentes_na_celula = self.model.grid.get_cell_list_contents([self.pos])
        ambiente = next((a for a in agentes_na_celula if isinstance(a, Environment)), None)
        fator_clima = self.get_fator_clima()
        
        if ambiente and ambiente.risco_foco > 0:
            
            prob_reproducao = ambiente.risco_foco * 0.1 * fator_clima
            
            mosquitos_atuais = [a for a in agentes_na_celula if isinstance(a, Mosquito)]
            
            if len(mosquitos_atuais) < ambiente.capacidade_mosquito:
                if self.random.random() < prob_reproducao: 
                    
                    new_mosquito = Mosquito(self.model.next_id(), self.model)
                    self.model.schedule.add(new_mosquito)
                    self.model.grid.place_agent(new_mosquito, self.pos)
    
    def picar_e_transmitir(self):
        """Pica um agente humano e tenta transmitir ou adquirir a infecção."""
        
        # IMPORTAÇÃO ADIADA 2: Importa Human apenas para este método
        from .human import Human 
        
        if not self.pos: return

        humanos_proximos = [
            a for a in self.model.grid.get_neighbors(self.pos, moore=True, include_center=True, radius=1)
            if isinstance(a, Human)
        ]
        
        if humanos_proximos:
            humano_alvo = self.random.choice(humanos_proximos)
            
            if humano_alvo.recuperado or getattr(humano_alvo, 'vacinado', False):
                return 

            # 1. Mosquito se infecta 
            if humano_alvo.infectado and not self.infectado:
                if self.random.random() < self.prob_contagio_mosquito:
                    self.infectado = True
                    
            # 2. Mosquito transmite 
            elif self.infectado and not humano_alvo.infectado:
                fator_transmissao = self.get_fator_clima()
                if self.random.random() < self.prob_infectar_humano * fator_transmissao:
                    humano_alvo.infectado = True
                    humano_alvo.tempo_infeccao = 0
    
    
    def atualizar_ciclo_vida(self):
        """Avança o ciclo de vida, ajustando a morte pela temperatura."""
        
        fator_clima = self.get_fator_clima()
        vida_maxima_ajustada = self.vida_maxima_base / fator_clima 
        
        self.tempo_vida += 1
        
        if self.tempo_vida > vida_maxima_ajustada:
            if self.pos:
                self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def step(self):
        """Método executado a cada passo do tempo."""
        self.mover()
        self.picar_e_transmitir()
        
        if self.model.schedule.steps % 5 == 0:
             self.reproduzir()
             
        self.atualizar_ciclo_vida()