from mesa import Agent
import random
import numpy as np


class Mosquito(Agent):
    """
    Agente Mosquito Adulto - Aedes aegypti - Modelo Aprimorado
    
    Estados Epidemiológicos:
        S = Suscetível
        E = Exposto (período de incubação extrínseco)
        I = Infectivo (capaz de transmitir dengue)
    
    Características:
    - Movimento baseado em busca por hospedeiros e criadouros
    - Ciclo de alimentação e reprodução realista
    - Período de incubação extrínseco variável
    - Longevidade influenciada por condições ambientais
    - Comportamento de picada seletivo
    """

    def __init__(self, unique_id, model, resistencia_base: float = 1.0, saude_inicial: float = 1.0):
        super().__init__(unique_id, model)
        
        # Estado epidemiológico
        self.estado = "S"
        self.dias_exposto = 0
        self.dias_infectivo = 0
        self.infectado = False
        
        # Parâmetros vitais
        self.idade = 0
        self.expectativa_vida = random.randint(15, 30)
        self.resistencia = resistencia_base
        self.saude = saude_inicial
        self.energia = 1.0
        
        # Comportamento alimentar
        self.fome = 0.0
        self.ultima_alimentacao = 0
        self.preferencia_alimentar = random.choice(["diurno", "crepuscular"])
        
        # Reprodução
        self.ovos_gestacao = 0
        self.dias_sem_ovipositar = 0
        self.fecundidade = random.uniform(0.8, 1.2)
        
        # Histórico e estatísticas
        self.picadas_realizadas = 0
        self.hospedeiros_infectados = 0
        self.historico_estados = []
        self.dias_sobrevivencia = 0

    def step(self):
        """
        Executa um dia completo do mosquito adulto
        """
        self.idade += 1
        self.dias_sobrevivencia += 1
        
        # Verifica morte natural por idade
        if self._verificar_morte_por_idade():
            return
            
        # Atualiza estados fisiológicos
        self._atualizar_estados_fisiologicos()
        
        # Verifica morte por condições adversas
        if self._verificar_morte_ambiental():
            return
            
        # Sequência comportamental
        self._buscar_alimentacao()
        self._buscar_local_oviposicao()
        self.mover()
        
        # Progressão da doença
        self._progressao_doenca()
        
        # Manter histórico
        self._manter_historico()

    def _verificar_morte_por_idade(self):
        """Verifica morte natural por idade/saúde"""
        # Mortalidade aumenta com a idade
        prob_morte_idade = min(0.3, self.idade / 100)
        
        # Saúde crítica aumenta mortalidade
        prob_morte_saude = (1 - self.saude) * 0.5
        
        prob_total = prob_morte_idade + prob_morte_saude
        
        if random.random() < prob_total:
            self._morrer()
            return True
        return False

    def _verificar_morte_ambiental(self):
        """Verifica morte por condições ambientais adversas"""
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        umidade = getattr(self.model, "umidade_ambiente", 70.0)
        
        # Temperaturas extremas
        if temperatura < 10 or temperatura > 40:
            prob_morte = 0.4 * (1 - self.resistencia)
            if random.random() < prob_morte:
                self._morrer()
                return True
                
        # Umidade muito baixa
        if umidade < 30:
            prob_morte = 0.2 * (1 - self.resistencia)
            if random.random() < prob_morte:
                self._morrer()
                return True
                
        return False

    def _atualizar_estados_fisiologicos(self):
        """Atualiza estados fisiológicos do mosquito"""
        # Aumenta fome
        self.fome = min(1.0, self.fome + 0.2)
        self.ultima_alimentacao += 1
        
        # Reduz energia com fome
        if self.fome > 0.7:
            self.energia = max(0.3, self.energia - 0.1)
            self.saude = max(0.5, self.saude - 0.05)
        else:
            self.energia = min(1.0, self.energia + 0.05)
            
        # Aumenta necessidade de oviposição
        self.dias_sem_ovipositar += 1

    def _buscar_alimentacao(self):
        """Busca por hospedeiros para alimentação"""
        if self.fome > 0.6 and self.energia > 0.3:
            humanos_celula = self._encontrar_humanos_proximos()
            
            if humanos_celula:
                # Escolhe um humano aleatório para picar
                humano_alvo = random.choice(humanos_celula)
                self._picar_humano(humano_alvo)

    def _encontrar_humanos_proximos(self):
        """Encontra humanos na mesma célula ou vizinhança"""
        # Humanos na mesma célula
        celula_contents = self.model.grid.get_cell_list_contents([self.pos])
        humanos = [agent for agent in celula_contents 
                  if hasattr(agent, 'receber_picada')]
        
        if humanos:
            return humanos
            
        # Busca em células vizinhas (simplificado)
        vizinhos = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        for vizinho in vizinhos:
            vizinho_contents = self.model.grid.get_cell_list_contents([vizinho])
            humanos_vizinhos = [agent for agent in vizinho_contents 
                              if hasattr(agent, 'receber_picada')]
            if humanos_vizinhos:
                # Move-se para a célula com humanos
                self.model.grid.move_agent(self, vizinho)
                return humanos_vizinhos
                
        return []

    def _picar_humano(self, humano):
        """Realiza picada em humano"""
        try:
            # Registra picada no humano
            humano.receber_picada()
            self.picadas_realizadas += 1
            self.fome = max(0.0, self.fome - 0.5)
            self.ultima_alimentacao = 0
            
            # Transmissão de dengue
            self._processar_transmissao(humano)
            
            # Possível infecção do mosquito
            if humano.infectado and not self.infectado:
                self._processar_infeccao()
                
        except Exception as e:
            print(f"❌ Erro ao processar picada: {e}")

    def _processar_transmissao(self, humano):
        """Processa transmissão do vírus para humano"""
        if self.infectado and not humano.infectado:
            # Mosquito infectivo pode transmitir
            prob_transmissao = 0.3  # Probabilidade base de transmissão
            
            # Fatores que afetam transmissão
            if self.dias_infectivo < 2:
                prob_transmissao *= 0.5  # Menos infectivo no início
                
            if random.random() < prob_transmissao:
                self.hospedeiros_infectados += 1

    def _processar_infeccao(self):
        """Processa infecção do mosquito por humano infectado"""
        if self.estado == "S":
            prob_infeccao = self.model.taxa_infeccao
            
            # Fatores que afetam suscetibilidade
            if self.saude < 0.5:
                prob_infeccao *= 1.2  # Mais suscetível se saúde baixa
                
            if random.random() < prob_infeccao:
                self.estado = "E"
                self.dias_exposto = 0
                self.infectado = True

    def _buscar_local_oviposicao(self):
        """Busca local adequado para oviposição"""
        if self.dias_sem_ovipositar > 3 and self.ovos_gestacao == 0:
            # Desenvolve nova geração de ovos
            self.ovos_gestacao = random.randint(50, 100) * self.fecundidade
            
        if self.ovos_gestacao > 0:
            locais_adequados = self._encontrar_locais_oviposicao()
            if locais_adequados:
                self._ovipositar(locais_adequados[0])

    def _encontrar_locais_oviposicao(self):
        """Encontra locais adequados para oviposição"""
        celula_contents = self.model.grid.get_cell_list_contents([self.pos])
        locais_adequados = []
        
        for agent in celula_contents:
            if hasattr(agent, 'risco_foco') and agent.risco_foco > 0.3:
                locais_adequados.append(agent)
                
        return locais_adequados

    def _ovipositar(self, local):
        """Realiza oviposição no local adequado"""
        from agents.egg import Egg
        
        try:
            # Número de ovos por postura
            ovos_esta_postura = min(self.ovos_gestacao, random.randint(30, 60))
            
            for _ in range(ovos_esta_postura):
                ovo = Egg(
                    unique_id=self.model.next_id(),
                    model=self.model,
                    dias_para_eclodir=random.randint(2, 5),
                    resistencia=random.uniform(0.7, 1.0)
                )
                
                self.model.grid.place_agent(ovo, local.pos)
                self.model.schedule.add(ovo)
                
                # Registra no ambiente
                if hasattr(local, 'depositar_ovo'):
                    local.depositar_ovo()
            
            # Atualiza contadores
            self.ovos_gestacao = max(0, self.ovos_gestacao - ovos_esta_postura)
            self.dias_sem_ovipositar = 0
            
        except Exception as e:
            print(f"❌ Erro na oviposição: {e}")

    def mover(self):
        """Movimento do mosquito baseado em comportamento"""
        if self.energia < 0.2:
            return  # Pouca energia, não se move
            
        # Padrão de movimento baseado em comportamento
        if self.fome > 0.7:
            # Movimento mais ativo em busca de alimento
            for _ in range(2):
                self._mover_aleatorio()
        elif self.ovos_gestacao > 0:
            # Busca por locais de oviposição
            self._mover_para_criadouro()
        else:
            # Movimento normal
            self._mover_aleatorio()

    def _mover_aleatorio(self):
        """Movimento aleatório considerando energia"""
        vizinhos = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        
        if vizinhos and random.random() < 0.8:  # 80% de chance de se mover
            nova_pos = random.choice(vizinhos)
            self.model.grid.move_agent(self, nova_pos)
            self.energia = max(0.1, self.energia - 0.05)

    def _mover_para_criadouro(self):
        """Movimento direcionado para áreas com criadouros"""
        # Busca células com alto risco de foco
        vizinhos = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        celulas_risco = []
        for vizinho in vizinhos:
            contents = self.model.grid.get_cell_list_contents([vizinho])
            for agent in contents:
                if hasattr(agent, 'risco_foco') and agent.risco_foco > 0.5:
                    celulas_risco.append(vizinho)
                    break
        
        if celulas_risco:
            nova_pos = random.choice(celulas_risco)
            self.model.grid.move_agent(self, nova_pos)
        else:
            self._mover_aleatorio()

    def _progressao_doenca(self):
        """Progressão da doença no mosquito"""
        if self.estado == "E":
            self.dias_exposto += 1
            
            # Período de incubação extrínseco (8-12 dias)
            if self.dias_exposto >= random.randint(8, 12):
                self.estado = "I"
                self.dias_infectivo = 0
                
        elif self.estado == "I":
            self.dias_infectivo += 1
            
            # Período infectivo (até a morte)
            # Mosquito permanece infectivo pelo resto da vida

    def _manter_historico(self):
        """Mantém histórico do mosquito"""
        self.historico_estados.append(self.estado)
        if len(self.historico_estados) > 50:
            self.historico_estados.pop(0)

    def _morrer(self):
        """Remove mosquito do modelo"""
        try:
            if self in self.model.grid[self.pos]:
                self.model.grid.remove_agent(self)
            if self in self.model.schedule.agents:
                self.model.schedule.remove(self)
            if hasattr(self.model, 'mosquitos') and self in self.model.mosquitos:
                self.model.mosquitos.remove(self)
        except Exception as e:
            print(f"⚠️ Erro ao remover mosquito {self.unique_id}: {e}")

    # ----------------------------------------------------------
    # PROPRIEDADES E MÉTODOS DE CONSULTA
    # ----------------------------------------------------------
    
    @property
    def suscetivel(self):
        return self.estado == "S"

    @property
    def exposto(self):
        return self.estado == "E"

    @property
    def infectivo(self):
        return self.estado == "I"

    @property
    def ativo(self):
        """Retorna se o mosquito está ativo (com energia)"""
        return self.energia > 0.3 and self.saude > 0.4

    @property
    def necessita_alimentacao(self):
        return self.fome > 0.6

    @property
    def pronto_para_ovipositar(self):
        return self.ovos_gestacao > 0 and self.dias_sem_ovipositar > 2

    def get_estatisticas(self):
        """Retorna estatísticas do mosquito para análise"""
        return {
            "estado": self.estado,
            "idade": self.idade,
            "saude": round(self.saude, 3),
            "energia": round(self.energia, 3),
            "fome": round(self.fome, 3),
            "infectado": self.infectado,
            "dias_infectivo": self.dias_infectivo,
            "picadas_realizadas": self.picadas_realizadas,
            "hospedeiros_infectados": self.hospedeiros_infectados,
            "ovos_gestacao": int(self.ovos_gestacao),
            "dias_sobrevivencia": self.dias_sobrevivencia,
            "ativo": self.ativo
        }

    def __str__(self):
        return (f"Mosquito {self.unique_id} - {self.estado} - "
                f"Idade: {self.idade} - Saúde: {self.saude:.2f} - "
                f"Picadas: {self.picadas_realizadas}")

    def __repr__(self):
        return (f"Mosquito(id={self.unique_id}, estado={self.estado}, "
                f"idade={self.idade}, pos={self.pos})")