from mesa import Agent
import random
import numpy as np


class Environment(Agent):
    """
    Célula de ambiente do modelo para simulação de dengue.
    
    Atributos:
    - densidade_criadouro: Propensão da célula para criadouros de Aedes (0-1)
    - risco_foco: Risco dinâmico de foco de dengue (0-1)
    - chuva_acumulada: Memória da chuva recente para ajustar o risco
    - temperatura_efeito: Efeito acumulado da temperatura no desenvolvimento
    - historico_risco: Histórico do risco para análise de tendências
    - tipo_ambiente: Classificação do ambiente (urbano, periurbano, etc.)
    """

    def __init__(self, unique_id, model, densidade_criadouro: float, risco_foco: float):
        super().__init__(unique_id, model)
        
        # Validação dos parâmetros de entrada
        self.densidade_criadouro = max(0.0, min(1.0, float(densidade_criadouro)))
        self.risco_foco = max(0.0, min(1.0, float(risco_foco)))
        
        # Estado dinâmico
        self.chuva_acumulada = 0.0
        self.temperatura_efeito = 0.0
        self.umidade_efeito = 0.0
        
        # Histórico para análise
        self.historico_risco = [self.risco_foco]
        self.max_historico = 30  # Mantém últimos 30 dias
        
        # Classificação do ambiente
        self.tipo_ambiente = self._classificar_ambiente()
        
        # Contadores para estatísticas
        self.ovos_depositados = 0
        self.larvas_desenvolvidas = 0
        
        # Timers e estados
        self.dias_sem_chuva = 0
        self.estado_secao = "normal"

    def _classificar_ambiente(self):
        """Classifica o ambiente baseado na densidade de criadouros"""
        if self.densidade_criadouro > 0.7:
            return "alto_risco"
        elif self.densidade_criadouro > 0.4:
            return "medio_risco"
        else:
            return "baixo_risco"

    def step(self):
        """
        Atualiza o risco de foco considerando múltiplos fatores ambientais:
        - Chuva acumulada
        - Temperatura ambiente
        - Umidade relativa
        - Densidade base de criadouros
        - Efeito sazonal
        """
        
        # Obtém dados climáticos do modelo com fallbacks
        chuva = getattr(self.model, "chuva_simulada", 0.0)
        temperatura = getattr(self.model, "temperatura_ambiente", 25.0)
        umidade = getattr(self.model, "umidade_ambiente", 60.0)
        
        # Atualiza acumuladores climáticos
        self._atualizar_fatores_climaticos(chuva, temperatura, umidade)
        
        # Calcula risco baseado em múltiplos fatores
        risco_calculado = self._calcular_risco_foco()
        
        # Suaviza a transição do risco
        self.risco_foco = self._suavizar_transicao(risco_calculado)
        
        # Atualiza estado de seca
        self._atualizar_estado_seca()
        
        # Mantém histórico
        self._atualizar_historico()

    def _atualizar_fatores_climaticos(self, chuva, temperatura, umidade):
        """Atualiza os fatores climáticos acumulados"""
        
        # Acumula chuva (só chuva positiva)
        self.chuva_acumulada += max(chuva, 0.0)
        
        # Efeito da temperatura (ótima entre 25-30°C)
        temp_otima = 27.5
        diff_temp = abs(temperatura - temp_otima)
        self.temperatura_efeito = max(0.0, 1.0 - (diff_temp / 15.0))
        
        # Efeito da umidade (ótima entre 70-80%)
        if 70 <= umidade <= 80:
            self.umidade_efeito = 1.0
        else:
            # Penaliza umidades muito altas ou muito baixas
            diff_umid = min(abs(umidade - 70), abs(umidade - 80))
            self.umidade_efeito = max(0.3, 1.0 - (diff_umid / 50.0))
        
        # Evaporação gradual
        self.chuva_acumulada *= 0.92  # 8% de evaporação diária

    def _calcular_risco_foco(self):
        """Calcula o risco de foco baseado em múltiplos fatores"""
        
        # Fator base da densidade de criadouros (peso maior)
        fator_densidade = self.densidade_criadouro * 0.5
        
        # Fator chuva (acelerador)
        fator_chuva = min(1.0, self.chuva_acumulada * 2.0) * 0.3
        
        # Fator temperatura (condicionante)
        fator_temperatura = self.temperatura_efeito * 0.1
        
        # Fator umidade (condicionante)
        fator_umidade = self.umidade_efeito * 0.1
        
        # Risco total
        risco_total = (
            fator_densidade + 
            fator_chuva + 
            fator_temperatura + 
            fator_umidade
        )
        
        return max(0.0, min(1.0, risco_total))

    def _suavizar_transicao(self, novo_risco):
        """Suaviza a transição do risco para evitar mudanças bruscas"""
        suavizacao = 0.85  # Mantém 85% do valor anterior
        return (suavizacao * self.risco_foco + 
                (1 - suavizacao) * novo_risco)

    def _atualizar_estado_seca(self):
        """Atualiza o estado de seca baseado na chuva acumulada"""
        if self.chuva_acumulada < 0.1:
            self.dias_sem_chuva += 1
        else:
            self.dias_sem_chuva = 0
            
        # Define estado baseado em dias sem chuva
        if self.dias_sem_chuva > 15:
            self.estado_secao = "seco"
        elif self.dias_sem_chuva > 7:
            self.estado_secao = "moderado"
        else:
            self.estado_secao = "normal"

    def _atualizar_historico(self):
        """Atualiza o histórico mantendo apenas os últimos valores"""
        self.historico_risco.append(self.risco_foco)
        if len(self.historico_risco) > self.max_historico:
            self.historico_risco.pop(0)

    # ------------------------------------------------------------------
    # MÉTODOS PARA INTERAÇÃO COM OUTROS AGENTES
    # ------------------------------------------------------------------
    
    def depositar_ovo(self):
        """Registra depósito de ovo no ambiente"""
        self.ovos_depositados += 1
        
        # Aumenta levemente o risco quando ovos são depositados
        if self.ovos_depositados % 5 == 0:  # A cada 5 ovos
            self.risco_foco = min(1.0, self.risco_foco + 0.05)

    def desenvolver_larva(self):
        """Registra desenvolvimento de larva no ambiente"""
        self.larvas_desenvolvidas += 1

    def get_estatisticas(self):
        """Retorna estatísticas do ambiente para relatórios"""
        return {
            "risco_atual": round(self.risco_foco, 3),
            "densidade_base": round(self.densidade_criadouro, 3),
            "chuva_acumulada": round(self.chuva_acumulada, 3),
            "tipo_ambiente": self.tipo_ambiente,
            "estado_secao": self.estado_secao,
            "ovos_depositados": self.ovos_depositados,
            "larvas_desenvolvidas": self.larvas_desenvolvidas,
            "dias_sem_chuva": self.dias_sem_chuva,
            "tendencia_risco": self._calcular_tendencia()
        }

    def _calcular_tendencia(self):
        """Calcula tendência do risco baseado no histórico"""
        if len(self.historico_risco) < 2:
            return "estavel"
        
        recente = self.historico_risco[-1]
        anterior = self.historico_risco[0] if len(self.historico_risco) < 5 else self.historico_risco[-5]
        
        if recente > anterior + 0.05:
            return "aumentando"
        elif recente < anterior - 0.05:
            return "diminuindo"
        else:
            return "estavel"

    def aplicar_controle(self, tipo_controle, eficacia=0.7):
        """
        Aplica medidas de controle no ambiente
        
        Args:
            tipo_controle: "fumace", "limpeza", "larvicida"
            eficacia: Eficácia da medida (0-1)
        """
        if tipo_controle == "fumace":
            # Redução temporária do risco
            self.risco_foco *= (1 - eficacia * 0.3)
        elif tipo_controle == "limpeza":
            # Redução mais duradoura
            self.risco_foco *= (1 - eficacia * 0.5)
            self.densidade_criadouro *= (1 - eficacia * 0.2)
        elif tipo_controle == "larvicida":
            # Elimina larvas e reduz ovos
            self.larvas_desenvolvidas = 0
            self.ovos_depositados = 0
            self.risco_foco *= (1 - eficacia * 0.4)
        
        # Garante que o risco não fique negativo
        self.risco_foco = max(0.0, self.risco_foco)

    def reset_estatisticas(self):
        """Reseta contadores para novo ciclo de simulação"""
        self.ovos_depositados = 0
        self.larvas_desenvolvidas = 0
        self.historico_risco = [self.risco_foco]

    # ------------------------------------------------------------------
    # PROPRIEDADES PARA FACILITAR ACESSO
    # ------------------------------------------------------------------
    
    @property
    def risco_alto(self):
        """Retorna True se o risco é considerado alto"""
        return self.risco_foco > 0.6

    @property
    def risco_medio(self):
        """Retorna True se o risco é considerado médio"""
        return 0.3 <= self.risco_foco <= 0.6

    @property
    def risco_baixo(self):
        """Retorna True se o risco é considerado baixo"""
        return self.risco_foco < 0.3

    @property
    def propicio_reproducao(self):
        """Retorna True se o ambiente está propício para reprodução"""
        return (self.risco_foco > 0.4 and 
                self.temperatura_efeito > 0.6 and 
                self.umidade_efeito > 0.7)

    def __str__(self):
        return (f"Environment {self.unique_id} - "
                f"Risco: {self.risco_foco:.2f} - "
                f"Tipo: {self.tipo_ambiente} - "
                f"Estado: {self.estado_secao}")

    def __repr__(self):
        return (f"Environment(id={self.unique_id}, "
                f"risco={self.risco_foco:.2f}, "
                f"densidade={self.densidade_criadouro:.2f})")