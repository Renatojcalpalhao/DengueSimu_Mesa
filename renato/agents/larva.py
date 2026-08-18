from mesa import Agent
import random
import numpy as np


class Larva(Agent):
    """
    Fase de LARVA do Aedes aegypti - Modelo Aprimorado
    
    Características:
    - Desenvolvimento influenciado por temperatura, umidade e nutrientes
    - Morte por predação, competição e condições adversas
    - Transformação em pupa após desenvolvimento completo
    - Diferentes estágios larvais (L1, L2, L3, L4)
    - Competição intra-específica por recursos
    """

    def __init__(self, unique_id, model, resistencia_base: float = None, estagio: int = 1):
        super().__init__(unique_id, model)
        
        # Estágio de desenvolvimento (L1 a L4)
        self.estagio = estagio
        self.dias_estagio = 0
        self.dias_total = 0
        
        # Parâmetros de desenvolvimento
        self.dias_por_estagio = random.randint(1, 3)  # Dias por estágio
        self.resistencia = resistencia_base or random.uniform(0.6, 1.0)
        self.taxa_crescimento = 1.0
        self.nutricao = random.uniform(0.7, 1.0)  # Nível nutricional inicial
        
        # Estado da larva
        self.viva = True
        self.transformada = False
        self.saude = 1.0  # Saúde geral (0-1)
        
        # Fatores ambientais
        self.competicao_local = 0
        self.predacao_risco = 0
        self.acesso_alimento = 1.0
        
        # Estatísticas
        self.dias_fome = 0
        self.temperatura_exposicao = 0
        self.estresse_ambiental = 0

    def step(self):
        """
        Executa um dia de desenvolvimento da larva
        """
        if not self.viva:
            self._remover_larva_morta()
            return
            
        self.dias_total += 1
        self.dias_estagio += 1
        
        # Avalia condições ambientais
        self._avaliar_condicoes_ambientais()
        
        # Calcula competição local
        self._calcular_competicao_local()
        
        # Atualiza saúde e nutrição
        self._atualizar_saude()
        
        # Verifica morte por condições adversas
        if self._verificar_morte():
            self.viva = False
            return
            
        # Desenvolvimento e mudança de estágio
        self._desenvolver()
        
        # Tenta transformar em pupa se no último estágio
        if self.estagio == 4 and self.dias_estagio >= self.dias_por_estagio:
            self._transformar_em_pupa()

    def _avaliar_condicoes_ambientais(self):
        """Avalia condições ambientais atuais"""
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        umidade = getattr(self.model, "umidade_ambiente", 70.0)
        chuva = getattr(self.model, "chuva_simulada", 0.0)
        
        # Temperatura ótima: 25-30°C
        if 25 <= temperatura <= 30:
            self.taxa_crescimento = 1.0
            self.temperatura_exposicao = 0
        elif temperatura < 15 or temperatura > 35:
            self.taxa_crescimento = 0.2
            self.temperatura_exposicao += 1
        elif temperatura < 20:
            self.taxa_crescimento = 0.5
            self.temperatura_exposicao += 0.5
        elif temperatura > 32:
            self.taxa_crescimento = 0.7
            self.temperatura_exposicao += 0.3
        else:
            self.taxa_crescimento = 0.8
            
        # Efeito da umidade
        if umidade < 50:
            self.taxa_crescimento *= 0.7
        elif umidade > 90:
            self.taxa_crescimento *= 0.9
            
        # Efeito da chuva (pode trazer nutrientes ou causar inundação)
        if chuva > 0.7:
            # Chuva forte pode causar estresse
            self.taxa_crescimento *= 0.8
            self.estresse_ambiental += 1
        elif chuva > 0.3:
            # Chuva moderada beneficia
            self.taxa_crescimento *= 1.1
            self.acesso_alimento += 0.1

    def _calcular_competicao_local(self):
        """Calcula competição por recursos no mesmo local"""
        # Conta outras larvas na mesma célula
        celula_contents = self.model.grid.get_cell_list_contents([self.pos])
        outras_larvas = [agent for agent in celula_contents 
                        if isinstance(agent, Larva) and agent != self]
        
        self.competicao_local = len(outras_larvas)
        
        # Competição reduz acesso a alimento
        if self.competicao_local > 0:
            reducao_alimento = min(0.5, self.competicao_local * 0.1)
            self.acesso_alimento = max(0.3, 1.0 - reducao_alimento)
            
        # Risco de predação aumenta com aglomeração
        self.predacao_risco = min(0.8, self.competicao_local * 0.15)

    def _atualizar_saude(self):
        """Atualiza saúde baseada em múltiplos fatores"""
        # Consumo de nutrientes
        consumo_diario = 0.1 * self.taxa_crescimento
        self.nutricao -= consumo_diario
        
        # Reposição por alimento disponível
        reposicao = 0.15 * self.acesso_alimento
        self.nutricao += reposicao
        
        # Limites de nutrição
        self.nutricao = max(0.0, min(1.0, self.nutricao))
        
        # Efeito da nutrição na saúde
        if self.nutricao < 0.3:
            self.dias_fome += 1
            self.saude -= 0.1
        elif self.nutricao > 0.8:
            self.dias_fome = 0
            self.saude += 0.05
        else:
            self.dias_fome = max(0, self.dias_fome - 0.5)
            
        # Efeito da competição na saúde
        if self.competicao_local > 3:
            self.saude -= 0.05 * (self.competicao_local - 3)
            
        # Efeito do estresse térmico
        if self.temperatura_exposicao > 3:
            self.saude -= 0.1 * (self.temperatura_exposicao - 3)
            
        # Limites de saúde
        self.saude = max(0.0, min(1.0, self.saude))
        
        # Ajuste da taxa de crescimento baseado na saúde
        self.taxa_crescimento *= self.saude

    def _verificar_morte(self):
        """Verifica se a larva morre por diversas causas"""
        # Morte por inanição
        if self.nutricao <= 0.05 or self.dias_fome > 5:
            return random.random() < 0.8
            
        # Morte por saúde crítica
        if self.saude <= 0.1:
            return random.random() < 0.9
            
        # Morte por predação
        if random.random() < self.predacao_risco:
            return True
            
        # Morte por condições extremas
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        if temperatura < 10 or temperatura > 40:
            return random.random() < 0.7 * (1 - self.resistencia)
            
        # Morte por competição extrema
        if self.competicao_local > 8 and self.nutricao < 0.4:
            return random.random() < 0.4
            
        return False

    def _desenvolver(self):
        """Processa desenvolvimento para próximo estágio"""
        dias_necessarios = self.dias_por_estagio / self.taxa_crescimento
        
        if self.dias_estagio >= dias_necessarios and self.estagio < 4:
            self._mudar_estagio()

    def _mudar_estagio(self):
        """Avança para o próximo estágio larval"""
        self.estagio += 1
        self.dias_estagio = 0
        
        # Ajusta dias por estágio baseado em condições
        self.dias_por_estagio = random.randint(1, 3)
        
        # Saúde afeta a transição
        if self.saude < 0.5:
            # Desenvolvimento mais lento em condições ruins
            self.dias_por_estagio += 1
            
        # Nutrição adequada acelera desenvolvimento
        if self.nutricao > 0.8:
            self.dias_por_estagio = max(1, self.dias_por_estagio - 1)

    def _transformar_em_pupa(self):
        """Transforma larva em pupa"""
        from agents.pupa import Pupa
        
        try:
            # Só se transforma se condições forem adequadas
            if self.saude > 0.3 and self.nutricao > 0.4:
                pupa = Pupa(
                    unique_id=self.model.next_id(),
                    model=self.model,
                    resistencia_base=self.resistencia * 0.8,
                    saude_inicial=self.saude * 0.9
                )
                
                # Mesma posição da larva
                self.model.grid.place_agent(pupa, self.pos)
                self.model.schedule.add(pupa)
                
                # Registra transformação
                self.transformada = True
                
                # Atualiza estatísticas do ambiente
                self._registrar_transformacao_ambiente()
                
                # Remove a larva
                self._remover_larva()
                
        except Exception as e:
            print(f"❌ Erro ao transformar larva {self.unique_id} em pupa: {e}")

    def _registrar_transformacao_ambiente(self):
        """Registra transformação no ambiente para estatísticas"""
        cell_contents = self.model.grid.get_cell_list_contents([self.pos])
        for agent in cell_contents:
            if hasattr(agent, 'desenvolver_larva'):
                # Já está registrado no desenvolvimento larval
                break

    def _remover_larva(self):
        """Remove a larva do modelo de forma segura"""
        try:
            if self in self.model.grid[self.pos]:
                self.model.grid.remove_agent(self)
            if self in self.model.schedule.agents:
                self.model.schedule.remove(self)
        except Exception as e:
            print(f"⚠️ Erro ao remover larva {self.unique_id}: {e}")

    def _remover_larva_morta(self):
        """Remove larva que morreu"""
        self.viva = False
        self._remover_larva()

    # ----------------------------------------------------------
    # PROPRIEDADES E MÉTODOS DE CONSULTA
    # ----------------------------------------------------------
    
    @property
    def tempo_restante_estimado(self):
        """Estima tempo restante para pupação"""
        if not self.viva or self.transformada:
            return float('inf')
            
        dias_restantes_estagio = max(0, self.dias_por_estagio - self.dias_estagio)
        estagios_restantes = 4 - self.estagio
        
        tempo_estagio_atual = dias_restantes_estagio / self.taxa_crescimento
        tempo_proximos_estagios = estagios_restantes * (self.dias_por_estagio / self.taxa_crescimento)
        
        return tempo_estagio_atual + tempo_proximos_estagios

    @property
    def probabilidade_sobrevivencia(self):
        """Calcula probabilidade de sobrevivência até a pupação"""
        if not self.viva:
            return 0.0
            
        # Fatores que afetam sobrevivência
        fator_saude = self.saude
        fator_nutricao = self.nutricao
        fator_competicao = 1.0 - (self.competicao_local * 0.1)
        fator_resistencia = self.resistencia
        
        prob = fator_saude * fator_nutricao * fator_competicao * fator_resistencia
        return max(0.0, min(1.0, prob))

    @property
    def condicoes_adequadas(self):
        """Retorna se as condições atuais são adequadas para desenvolvimento"""
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        umidade = getattr(self.model, "umidade_ambiente", 70.0)
        
        return (20 <= temperatura <= 32 and 
                50 <= umidade <= 90 and
                self.nutricao > 0.3 and
                self.competicao_local < 6)

    def get_estatisticas(self):
        """Retorna estatísticas da larva para análise"""
        return {
            "estagio": self.estagio,
            "dias_total": self.dias_total,
            "viva": self.viva,
            "saude": round(self.saude, 3),
            "nutricao": round(self.nutricao, 3),
            "resistencia": round(self.resistencia, 3),
            "competicao_local": self.competicao_local,
            "taxa_crescimento": round(self.taxa_crescimento, 3),
            "tempo_restante": round(self.tempo_restante_estimado, 1),
            "prob_sobrevivencia": round(self.probabilidade_sobrevivencia, 3),
            "condicoes_adequadas": self.condicoes_adequadas,
            "dias_fome": self.dias_fome
        }

    def __str__(self):
        status = "VIVA" if self.viva else "MORTA"
        return f"Larva {self.unique_id} - {status} - Estágio L{self.estagio} - Dias: {self.dias_total}"

    def __repr__(self):
        return (f"Larva(id={self.unique_id}, estagio=L{self.estagio}, "
                f"viva={self.viva}, saude={self.saude:.2f})")