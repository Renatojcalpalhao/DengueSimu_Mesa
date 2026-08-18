from mesa import Agent
import random
import numpy as np


class Pupa(Agent):
    """
    Fase de PUPA do Aedes aegypti - Estágio intermediário entre larva e adulto
    
    Características:
    - Estágio de metamorfose (não se alimenta)
    - Desenvolvimento influenciado por temperatura
    - Baixa mortalidade comparada à fase larval
    - Transformação em mosquito adulto
    """

    def __init__(self, unique_id, model, resistencia_base: float = 1.0, saude_inicial: float = 1.0):
        super().__init__(unique_id, model)
        
        # Parâmetros de desenvolvimento
        self.dias_para_adulto = random.randint(2, 4)
        self.dias = 0
        self.resistencia = resistencia_base
        self.saude = saude_inicial
        
        # Estado da pupa
        self.viva = True
        self.transformada = False
        self.taxa_desenvolvimento = 1.0
        
        # Fatores ambientais
        self.temperatura_exposicao = 0

    def step(self):
        """
        Executa um dia de desenvolvimento da pupa
        """
        if not self.viva:
            self._remover_pupa_morta()
            return
            
        self.dias += 1
        
        # Avalia condições ambientais
        self._avaliar_condicoes_ambientais()
        
        # Verifica morte por condições adversas
        if self._verificar_morte():
            self.viva = False
            return
            
        # Tenta transformar em adulto
        if self.dias >= self.dias_para_adulto / self.taxa_desenvolvimento:
            self._transformar_em_adulto()

    def _avaliar_condicoes_ambientais(self):
        """Avalia condições ambientais atuais"""
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        
        # Temperatura ótima: 25-30°C
        if 25 <= temperatura <= 30:
            self.taxa_desenvolvimento = 1.2  # Desenvolvimento acelerado
            self.temperatura_exposicao = 0
        elif temperatura < 15 or temperatura > 35:
            self.taxa_desenvolvimento = 0.3  # Desenvolvimento muito lento
            self.temperatura_exposicao += 1
        elif temperatura < 20:
            self.taxa_desenvolvimento = 0.6
            self.temperatura_exposicao += 0.5
        elif temperatura > 32:
            self.taxa_desenvolvimento = 0.8
            self.temperatura_exposicao += 0.3
        else:
            self.taxa_desenvolvimento = 1.0

    def _verificar_morte(self):
        """Verifica se a pupa morre por condições adversas"""
        # Mortalidade natural baixa (2% ao dia)
        if random.random() < 0.02 * (1 - self.resistencia):
            return True
            
        # Morte por temperaturas extremas prolongadas
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        if (temperatura < 10 or temperatura > 40) and random.random() < 0.3:
            return True
            
        # Morte por saúde muito baixa
        if self.saude < 0.2 and random.random() < 0.5:
            return True
            
        return False

    def _transformar_em_adulto(self):
        """Transforma pupa em mosquito adulto"""
        from agents.mosquito import Mosquito
        
        try:
            # Cria mosquito adulto
            mosquito = Mosquito(
                unique_id=self.model.next_id(),
                model=self.model,
                resistencia_base=self.resistencia * 0.9,
                saude_inicial=self.saude * 0.8
            )
            
            # Mesma posição da pupa
            self.model.grid.place_agent(mosquito, self.pos)
            self.model.schedule.add(mosquito)
            
            # Adiciona à lista de mosquitos do modelo
            if hasattr(self.model, 'mosquitos'):
                self.model.mosquitos.append(mosquito)
            
            # Registra transformação
            self.transformada = True
            
            # Remove a pupa
            self._remover_pupa()
            
        except Exception as e:
            print(f"❌ Erro ao transformar pupa {self.unique_id} em adulto: {e}")

    def _remover_pupa(self):
        """Remove a pupa do modelo de forma segura"""
        try:
            if self in self.model.grid[self.pos]:
                self.model.grid.remove_agent(self)
            if self in self.model.schedule.agents:
                self.model.schedule.remove(self)
        except Exception as e:
            print(f"⚠️ Erro ao remover pupa {self.unique_id}: {e}")

    def _remover_pupa_morta(self):
        """Remove pupa que morreu"""
        self.viva = False
        self._remover_pupa()

    # ----------------------------------------------------------
    # PROPRIEDADES E MÉTODOS DE CONSULTA
    # ----------------------------------------------------------
    
    @property
    def tempo_restante_estimado(self):
        """Estima tempo restante para emergência do adulto"""
        if not self.viva or self.transformada:
            return float('inf')
            
        dias_restantes = max(0, (self.dias_para_adulto / self.taxa_desenvolvimento) - self.dias)
        return dias_restantes

    @property
    def probabilidade_emergencia(self):
        """Calcula probabilidade de emergência bem-sucedida"""
        if not self.viva:
            return 0.0
            
        # Fatores que afetam a emergência
        fator_saude = self.saude
        fator_temperatura = 1.0 - (self.temperatura_exposicao * 0.1)
        fator_resistencia = self.resistencia
        
        prob = fator_saude * fator_temperatura * fator_resistencia
        return max(0.0, min(1.0, prob))

    def get_estatisticas(self):
        """Retorna estatísticas da pupa para análise"""
        return {
            "dias": self.dias,
            "viva": self.viva,
            "saude": round(self.saude, 3),
            "resistencia": round(self.resistencia, 3),
            "taxa_desenvolvimento": round(self.taxa_desenvolvimento, 3),
            "tempo_restante": round(self.tempo_restante_estimado, 1),
            "prob_emergencia": round(self.probabilidade_emergencia, 3)
        }

    def __str__(self):
        status = "VIVA" if self.viva else "MORTA"
        return f"Pupa {self.unique_id} - {status} - Dias: {self.dias}"

    def __repr__(self):
        return (f"Pupa(id={self.unique_id}, dias={self.dias}, "
                f"viva={self.viva}, saude={self.saude:.2f})")