from mesa import Agent
import random
import numpy as np


class Egg(Agent):
    """
    Fase de OVO do Aedes aegypti - Modelo Aprimorado
    
    Características:
    - Desenvolvimento influenciado por temperatura e umidade
    - Taxa de eclosão variável baseada em condições ambientais
    - Morte por dessecação em condições adversas
    - Efeito sazonal no desenvolvimento
    - Diferentes tempos de desenvolvimento por lote
    """

    def __init__(self, unique_id, model, dias_para_eclodir: int = None, resistencia: float = None):
        super().__init__(unique_id, model)
        
        # Parâmetros de desenvolvimento
        self.dias_para_eclodir = dias_para_eclodir or random.randint(2, 5)
        self.dias = 0
        self.dias_sem_agua = 0
        self.resistencia = resistencia or random.uniform(0.7, 1.0)
        
        # Estado do ovo
        self.viable = True
        self.eclodido = False
        self.taxa_desenvolvimento = 1.0
        
        # Condições ambientais no momento da postura
        self.temperatura_postura = getattr(self.model, "temperatura_ambiente", 25.0)
        self.umidade_postura = getattr(self.model, "umidade_ambiente", 70.0)
        
        # Estatísticas
        self.tentativas_eclosao = 0
        self.condicoes_adversas = 0

    def step(self):
        """
        Executa um dia de desenvolvimento do ovo
        Considera temperatura, umidade e condições ambientais
        """
        if not self.viable:
            self._remover_ovo_morto()
            return
            
        self.dias += 1
        
        # Verifica condições ambientais atuais
        self._avaliar_condicoes_ambientais()
        
        # Atualiza taxa de desenvolvimento baseada no ambiente
        self._calcular_taxa_desenvolvimento()
        
        # Verifica morte por dessecação
        if self._verificar_morte_dessecacao():
            self.viable = False
            return
            
        # Tenta eclodir
        self._tentar_eclosao()

    def _avaliar_condicoes_ambientais(self):
        """Avalia condições ambientais atuais"""
        temp_atual = getattr(self.model, "temperatura_ambiente", 25.0)
        umid_atual = getattr(self.model, "umidade_ambiente", 70.0)
        chuva_atual = getattr(self.model, "chuva_simulada", 0.0)
        
        # Contador de dias sem água
        if chuva_atual < 0.1 and umid_atual < 50:
            self.dias_sem_agua += 1
        else:
            self.dias_sem_agua = max(0, self.dias_sem_agua - 1)

    def _calcular_taxa_desenvolvimento(self):
        """Calcula taxa de desenvolvimento baseada em condições ótimas"""
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        umidade = getattr(self.model, "umidade_ambiente", 70.0)
        
        # Temperatura ótima: 25-30°C
        if 25 <= temperatura <= 30:
            fator_temp = 1.0
        elif temperatura < 15 or temperatura > 35:
            fator_temp = 0.1  # Desenvolvimento muito lento
        elif temperatura < 20:
            fator_temp = 0.3
        elif temperatura > 32:
            fator_temp = 0.5
        else:
            fator_temp = 0.8
            
        # Umidade ótima: 70-85%
        if 70 <= umidade <= 85:
            fator_umid = 1.0
        elif umidade < 40:
            fator_umid = 0.2  # Risco de dessecação
        elif umidade < 60:
            fator_umid = 0.6
        else:
            fator_umid = 0.9
            
        # Efeito da chuva (acelera desenvolvimento)
        chuva = getattr(self.model, "chuva_simulada", 0.0)
        fator_chuva = 1.0 + (chuva * 0.5)
        
        self.taxa_desenvolvimento = fator_temp * fator_umid * fator_chuva * self.resistencia

    def _verificar_morte_dessecacao(self):
        """Verifica se o ovo morre por dessecação"""
        umidade = getattr(self.model, "umidade_ambiente", 70.0)
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        
        # Condições extremas de dessecação
        if (umidade < 30 and temperatura > 30) or self.dias_sem_agua > 7:
            prob_morte = 0.3 * (1 - self.resistencia)
            return random.random() < prob_morte
            
        # Morte gradual em condições adversas prolongadas
        if self.dias_sem_agua > 3:
            prob_morte = 0.1 * (self.dias_sem_agua - 3) * (1 - self.resistencia)
            return random.random() < prob_morte
            
        return False

    def _tentar_eclosao(self):
        """Tenta eclodir o ovo baseado em múltiplos fatores"""
        self.tentativas_eclosao += 1
        
        # Fatores que influenciam a eclosão
        prob_eclosao = self._calcular_probabilidade_eclosao()
        
        # Eclosão forçada após muito tempo
        dias_efetivos = self.dias * self.taxa_desenvolvimento
        if dias_efetivos >= self.dias_para_eclodir * 2:
            prob_eclosao = 1.0  # Eclosão forçada
            
        # Tenta eclodir
        if random.random() < prob_eclosao:
            self._eclodir()

    def _calcular_probabilidade_eclosao(self):
        """Calcula probabilidade de eclosão considerando múltiplos fatores"""
        # Probabilidade base aumenta com o tempo
        dias_efetivos = self.dias * self.taxa_desenvolvimento
        prob_base = min(1.0, dias_efetivos / self.dias_para_eclodir) * 0.8
        
        # Efeito da chuva (gatilho para eclosão)
        chuva = getattr(self.model, "chuva_simulada", 0.0)
        fator_chuva = min(0.5, chuva * 0.8)
        
        # Efeito da umidade (condição necessária)
        umidade = getattr(self.model, "umidade_ambiente", 70.0)
        if umidade > 70:
            fator_umidade = 1.0
        elif umidade > 50:
            fator_umidade = 0.7
        else:
            fator_umidade = 0.2  # Baixa umidade dificulta eclosão
            
        # Efeito sazonal (simulação simples)
        passo = getattr(self.model, "step_count", 0)
        fator_sazonal = 0.8 + 0.2 * np.sin(passo * 2 * np.pi / 365)  # Variação anual
        
        prob_total = (prob_base + fator_chuva) * fator_umidade * fator_sazonal * self.resistencia
        
        return min(0.95, max(0.05, prob_total))

    def _eclodir(self):
        """Transforma o ovo em larva"""
        from agents.larva import Larva
        
        try:
            # Cria larva na mesma posição
            larva = Larva(
                unique_id=self.model.next_id(), 
                model=self.model,
                resistencia_base=self.resistencia * 0.9  # Herda parte da resistência
            )
            
            # Coloca no grid e no scheduler
            self.model.grid.place_agent(larva, self.pos)
            self.model.schedule.add(larva)
            
            # Registra sucesso
            self.eclodido = True
            
            # Atualiza estatísticas do ambiente
            self._registrar_eclosao_ambiente()
            
            # Remove o ovo
            self._remover_ovo()
            
        except Exception as e:
            print(f"❌ Erro ao eclodir ovo {self.unique_id}: {e}")

    def _registrar_eclosao_ambiente(self):
        """Registra eclosão no ambiente para estatísticas"""
        # Encontra o agente Environment nesta posição
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cell_contents:
            if hasattr(agent, 'desenvolver_larva'):
                agent.desenvolver_larva()
                break

    def _remover_ovo(self):
        """Remove o ovo do modelo de forma segura"""
        try:
            if self in self.model.grid[self.pos]:
                self.model.grid.remove_agent(self)
            if self in self.model.schedule.agents:
                self.model.schedule.remove(self)
        except Exception as e:
            print(f"⚠️ Erro ao remover ovo {self.unique_id}: {e}")

    def _remover_ovo_morto(self):
        """Remove ovo que morreu por condições adversas"""
        self.viable = False
        self._remover_ovo()

    # ----------------------------------------------------------
    # PROPRIEDADES E MÉTODOS DE CONSULTA
    # ----------------------------------------------------------
    
    @property
    def tempo_restante_estimado(self):
        """Estima tempo restante para eclosão"""
        if not self.viable:
            return float('inf')
        dias_necessarios = max(1, self.dias_para_eclodir - (self.dias * self.taxa_desenvolvimento))
        return max(0, dias_necessarios / self.taxa_desenvolvimento)

    @property
    def probabilidade_eclosao_hoje(self):
        """Retorna probabilidade de eclosão no dia atual"""
        if not self.viable:
            return 0.0
        return self._calcular_probabilidade_eclosao()

    @property
    def condicoes_favoraveis(self):
        """Retorna se as condições atuais são favoráveis"""
        temp = getattr(self.model, "temperatura_ambiente", 25.0)
        umid = getattr(self.model, "umidade_ambiente", 70.0)
        return (20 <= temp <= 32) and (umid > 60)

    def get_estatisticas(self):
        """Retorna estatísticas do ovo para análise"""
        return {
            "dias": self.dias,
            "viable": self.viable,
            "dias_sem_agua": self.dias_sem_agua,
            "resistencia": round(self.resistencia, 3),
            "taxa_desenvolvimento": round(self.taxa_desenvolvimento, 3),
            "tempo_restante": round(self.tempo_restante_estimado, 1),
            "prob_eclosao": round(self.probabilidade_eclosao_hoje, 3),
            "condicoes_favoraveis": self.condicoes_favoraveis,
            "tentativas_eclosao": self.tentativas_eclosao
        }

    def __str__(self):
        status = "VIVO" if self.viable else "MORTO"
        return f"Egg {self.unique_id} - {status} - Dias: {self.dias} - Viável: {self.viable}"

    def __repr__(self):
        return (f"Egg(id={self.unique_id}, dias={self.dias}, "
                f"viable={self.viable}, resistencia={self.resistencia:.2f})")