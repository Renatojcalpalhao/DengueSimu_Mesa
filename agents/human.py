from mesa import Agent
import random
import numpy as np


class Human(Agent):
    """
    Agente Humano – Modelo Epidemiológico SEIR + Vacinação Aprimorado
    
    Estados Epidemiológicos:
        S = Suscetível
        E = Exposto (incubação humana)
        I = Infectado (sintomático/assintomático)
        R = Recuperado (imunidade temporária)
        V = Vacinado (proteção parcial/decrescente)
    
    Características:
    - Movimento realista entre casa e trabalho
    - Períodos de incubação e infecciosidade variáveis
    - Eficácia vacinal decrescente no tempo
    - Diferentes níveis de gravidade da doença
    - Comportamentos baseados em risco ambiental
    """

    def __init__(self, unique_id, model, casa, trabalho):
        super().__init__(unique_id, model)
        
        # Posição e locais importantes
        self.pos = casa
        self.casa = casa
        self.trabalho = trabalho
        self.local_atual = "casa"
        
        # Estado epidemiológico avançado
        self.estado = "S"
        self.dias_exposto = 0
        self.dias_infectado = 0
        self.dias_recuperado = 0
        self.foi_picado = False
        self.picadas_recebidas = 0
        
        # Características individuais
        self.idade = random.randint(5, 70)
        self.gravidade_doenca = random.choice(["assintomatico", "leve", "moderado", "grave"])
        self.mobilidade = random.uniform(0.7, 1.3)  # Fator de movimento
        self.suscetibilidade_base = random.uniform(0.8, 1.2)
        
        # Sistema de vacinação avançado
        self.vacinado = False
        self.tempo_desde_vacinacao = 0
        self.eficacia_vacina_inicial = random.uniform(0.75, 0.85)
        self.duracao_imunidade_vacina = random.randint(80, 100)
        self.doses_vacina = 0
        
        # Histórico médico
        self.infeccoes_previas = 0
        self.historico_estados = []
        self.dias_sintomaticos = 0
        
        # Comportamento preventivo
        self.uso_repelente = random.random() < 0.3  # 30% usam repelente
        self.cuidados_ambientais = random.random() < 0.4  # 40% têm cuidados
        
        # Estatísticas
        self.total_picadas = 0
        self.total_infeccoes = 0

    # ----------------------------------------------------------
    # SISTEMA DE MOVIMENTO REALISTA
    # ----------------------------------------------------------
    
    def mover(self):
        """Movimento baseado em padrões diários (casa/trabalho)"""
        
        # Padrão circadiano - muda de local a cada 4 steps (dias)
        if self.model.schedule.steps % 4 == 0:
            if self.local_atual == "casa":
                self.ir_para_trabalho()
            else:
                self.voltar_para_casa()
        else:
            # Movimento local no ambiente atual
            self.movimento_local()
    
    def ir_para_trabalho(self):
        """Move-se para o local de trabalho"""
        if self.pos != self.trabalho:
            self.model.grid.move_agent(self, self.trabalho)
            self.local_atual = "trabalho"
    
    def voltar_para_casa(self):
        """Retorna para casa"""
        if self.pos != self.casa:
            self.model.grid.move_agent(self, self.casa)
            self.local_atual = "casa"
    
    def movimento_local(self):
        """Movimento aleatório no ambiente atual considerando mobilidade"""
        if random.random() < 0.7 * self.mobilidade:  # 70% de chance de se mover
            vizinhos = self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
            if vizinhos:
                nova_pos = random.choice(vizinhos)
                self.model.grid.move_agent(self, nova_pos)

    # ----------------------------------------------------------
    # SISTEMA DE CONTÁGIO APRIMORADO
    # ----------------------------------------------------------
    
    def receber_picada(self):
        """Registra picada de mosquito considerando fatores de proteção"""
        self.foi_picado = True
        self.picadas_recebidas += 1
        self.total_picadas += 1
        
        # Repelente reduz chance de picada efetiva
        if self.uso_repelente:
            if random.random() < 0.6:  # 60% de eficácia do repelente
                self.foi_picado = False
    
    def avaliar_contagio(self):
        """Avalia contágio após picada considerando múltiplos fatores"""
        if not self.foi_picado or self.estado not in ["S", "V"]:
            return False
        
        # Probabilidade base do modelo
        prob_base = self.model.prob_contagio_humano
        
        # Ajustes por fatores individuais
        prob_ajustada = prob_base * self.suscetibilidade_base
        
        # Redução por vacinação
        if self.vacinado:
            eficacia_atual = self._calcular_eficacia_vacinal()
            prob_ajustada *= (1 - eficacia_atual)
        
        # Redução por imunidade prévia
        if self.infeccoes_previas > 0:
            prob_ajustada *= (1 - (0.3 * min(self.infeccoes_previas, 3)))
        
        # Efeito da idade (crianças e idosos mais suscetíveis)
        if self.idade < 15 or self.idade > 60:
            prob_ajustada *= 1.2
        
        return random.random() < prob_ajustada
    
    def _calcular_eficacia_vacinal(self):
        """Calcula eficácia vacinal decrescente no tempo"""
        if not self.vacinado:
            return 0.0
        
        # Eficácia decai linearmente ao longo do tempo
        decaimento = self.tempo_desde_vacinacao / self.duracao_imunidade_vacina
        eficacia_atual = self.eficacia_vacina_inicial * (1 - min(decaimento, 1.0))
        
        # Dose de reforço aumenta eficácia
        if self.doses_vacina > 1:
            eficacia_atual *= (1 + 0.2 * (self.doses_vacina - 1))
        
        return max(0.0, min(1.0, eficacia_atual))

    # ----------------------------------------------------------
    # PROGRESSÃO DA DOENÇA APRIMORADA
    # ----------------------------------------------------------
    
    def step(self):
        """Executa um passo de tempo (1 dia) para o agente humano"""
        
        # Movimento
        self.mover()
        
        # Atualização vacinal
        self._atualizar_estado_vacinal()
        
        # Contágio por picada
        if self.avaliar_contagio():
            self._contrair_doenca()
        
        # Progressão da doença
        self._progressao_doenca()
        
        # Reset do estado de picada
        self.foi_picado = False
        
        # Manter histórico
        self._manter_historico()

    def _atualizar_estado_vacinal(self):
        """Atualiza estado vacinal e imunidade"""
        if self.vacinado:
            self.tempo_desde_vacinacao += 1
            
            # Perda de imunidade vacinal
            if self.tempo_desde_vacinacao > self.duracao_imunidade_vacina:
                self.vacinado = False
                if self.estado == "V":
                    self.estado = "S"

    def _contrair_doenca(self):
        """Processa contração da doença"""
        self.estado = "E"
        self.dias_exposto = 0
        self.total_infeccoes += 1
        
        # Determina gravidade baseado em múltiplos fatores
        self._determinar_gravidade()

    def _determinar_gravidade(self):
        """Determina a gravidade da infecção baseado em fatores de risco"""
        base_gravidade = random.random()
        
        # Idade influencia gravidade
        if self.idade < 15 or self.idade > 60:
            base_gravidade *= 1.3
        
        # Infecções prévias reduzem gravidade
        if self.infeccoes_previas > 0:
            base_gravidade *= (1 - 0.2 * min(self.infeccoes_previas, 2))
        
        # Vacinação reduz gravidade
        if self.vacinado:
            base_gravidade *= (1 - self._calcular_eficacia_vacinal() * 0.5)
        
        # Classifica gravidade
        if base_gravidade < 0.3:
            self.gravidade_doenca = "assintomatico"
        elif base_gravidade < 0.6:
            self.gravidade_doenca = "leve"
        elif base_gravidade < 0.85:
            self.gravidade_doenca = "moderado"
        else:
            self.gravidade_doenca = "grave"

    def _progressao_doenca(self):
        """Progressão natural da doença através dos estados SEIR"""
        
        if self.estado == "E":
            self.dias_exposto += 1
            # Período de incubação variável (4-7 dias)
            if self.dias_exposto >= random.randint(4, 7):
                self.estado = "I"
                self.dias_infectado = 0

        elif self.estado == "I":
            self.dias_infectado += 1
            if self.gravidade_doenca != "assintomatico":
                self.dias_sintomaticos += 1
            
            # Duração da infecciosidade variável (5-10 dias)
            duracao_infeccioso = random.randint(5, 10)
            if self.gravidade_doenca == "grave":
                duracao_infeccioso += 3  # Casos graves são infecciosos por mais tempo
            
            if self.dias_infectado >= duracao_infeccioso:
                self.estado = "R"
                self.dias_recuperado = 0
                self.infeccoes_previas += 1

        elif self.estado == "R":
            self.dias_recuperado += 1
            # Imunidade natural decrescente (60-120 dias)
            duracao_imunidade = random.randint(60, 120)
            if self.dias_recuperado >= duracao_imunidade:
                self.estado = "S"

    def _manter_historico(self):
        """Mantém histórico dos estados"""
        self.historico_estados.append(self.estado)
        # Mantém apenas os últimos 100 estados
        if len(self.historico_estados) > 100:
            self.historico_estados.pop(0)

    # ----------------------------------------------------------
    # SISTEMA DE VACINAÇÃO
    # ----------------------------------------------------------
    
    def vacinar(self, dose=1):
        """Aplica vacinação no agente"""
        self.vacinado = True
        self.tempo_desde_vacinacao = 0
        self.doses_vacina = dose
        
        # Se estava suscetível, muda para estado vacinado
        if self.estado == "S":
            self.estado = "V"
        
        print(f"💉 Humano {self.unique_id} vacinado (dose {dose})")

    # ----------------------------------------------------------
    # PROPRIEDADES E MÉTODOS DE CONSULTA
    # ----------------------------------------------------------
    
    @property
    def infectado(self):
        return self.estado == "I"

    @property
    def recuperado(self):
        return self.estado == "R"

    @property
    def exposto(self):
        return self.estado == "E"

    @property
    def suscetivel(self):
        return self.estado == "S"

    @property
    def imunizado(self):
        return self.estado in ["R", "V"]

    @property
    def infeccioso(self):
        """Retorna se o agente é infeccioso para mosquitos"""
        return self.infectado and self.dias_infectado > 1

    @property
    def necessita_atencao_medica(self):
        """Retorna se o caso necessita de atenção médica"""
        return self.infectado and self.gravidade_doenca in ["moderado", "grave"]

    def get_estatisticas(self):
        """Retorna estatísticas do agente para análise"""
        return {
            "idade": self.idade,
            "estado": self.estado,
            "vacinado": self.vacinado,
            "doses_vacina": self.doses_vacina,
            "gravidade": self.gravidade_doenca,
            "infeccoes_previas": self.infeccoes_previas,
            "total_picadas": self.total_picadas,
            "dias_sintomaticos": self.dias_sintomaticos,
            "local_atual": self.local_atual,
            "eficacia_vacinal": round(self._calcular_eficacia_vacinal(), 3)
        }

    def __str__(self):
        return (f"Human {self.unique_id} - {self.estado} - "
                f"Idade: {self.idade} - Gravidade: {self.gravidade_doenca} - "
                f"Vacinado: {self.vacinado}")

    def __repr__(self):
        return (f"Human(id={self.unique_id}, estado={self.estado}, "
                f"idade={self.idade}, pos={self.pos})")