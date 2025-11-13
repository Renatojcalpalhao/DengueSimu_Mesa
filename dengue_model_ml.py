# ============================================================
#  Modelo Híbrido ABM + Machine Learning (Random Forest)
#  Autor: Renato Jorge Correia Alpalhão
#  Projeto de Conclusão de Curso - SENAC
# ============================================================

from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
import warnings

# --- Importações internas --- #
from agents.human import Human
from agents.mosquito import Mosquito
from agents.environment import Environment
from api.clima import obter_clima_sao_paulo_inmet
from api.dengue_api import obter_dados_dengue_sp
from api.data_loader import get_densidade_fator_por_coordenada

warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================
#  Modelo Principal
# ============================================================

class DengueModelML(Model):
    """
    Modelo ABM + ML da Dengue.
    Integra agentes (humanos e mosquitos) com aprendizado de máquina.
    """

    def __init__(self, num_humanos=150, num_mosquitos=300, taxa_infeccao=0.2,
                 width=50, height=50, prob_contagio_humano=0.3,
                 vida_media_mosquito=25, **kwargs):

        super().__init__(**kwargs)

        # --- Parâmetros Globais --- #
        self.num_humanos = num_humanos
        self.num_mosquitos = num_mosquitos
        self.taxa_infeccao = taxa_infeccao
        self.prob_contagio_humano = prob_contagio_humano
        self.vida_media_mosquito = vida_media_mosquito

        # --- Variáveis Dinâmicas --- #
        self.step_count = 0
        self.data_atual = datetime(2025, 1, 1)
        self.temperatura_ambiente = 27.0
        self.umidade_ambiente = 70.0
        self.chuva_simulada = 0.2
        self.casos_reais = 0
        self.alerta_dengue = "Sem dados"

        # --- Ambiente / Grid --- #
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = BaseScheduler(self)

        # ------------------------------------------------------------
        #  Ambiente (densidade e risco por célula)
        # ------------------------------------------------------------
        for x in range(width):
            for y in range(height):
                densidade, risco = get_densidade_fator_por_coordenada(width, height, x, y)
                ambiente = Environment(self.next_id(), self, densidade, risco)
                self.grid.place_agent(ambiente, (x, y))
                self.schedule.add(ambiente)

        # ------------------------------------------------------------
        #  Humanos (1 infectado inicial)
        # ------------------------------------------------------------
        for i in range(self.num_humanos):
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            humano = Human(self.next_id(), self, casa=(x, y), trabalho=(x, y))

            if i == 0:
                humano.infectado = True  # paciente zero

            self.grid.place_agent(humano, (x, y))
            self.schedule.add(humano)

        # ------------------------------------------------------------
        #  Mosquitos
        # ------------------------------------------------------------
        for _ in range(self.num_mosquitos):
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            mosquito = Mosquito(self.next_id(), self)
            self.grid.place_agent(mosquito, (x, y))
            self.schedule.add(mosquito)

        # ------------------------------------------------------------
        #  Machine Learning (Random Forest)
        # ------------------------------------------------------------
        self.ml_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.dados_treinamento = pd.DataFrame(columns=["temperatura", "umidade", "chuva", "casos_reais"])

        # ------------------------------------------------------------
        #  DataCollector (GRÁFICOS)
        # ------------------------------------------------------------
        self.datacollector = DataCollector(
            model_reporters={
                "Passo": lambda m: m.step_count,
                "Infectados": lambda m: sum(1 for a in m.schedule.agents
                                            if isinstance(a, Human) and getattr(a, "infectado", False)),
                "Recuperados": lambda m: sum(1 for a in m.schedule.agents
                                             if isinstance(a, Human) and getattr(a, "recuperado", False)),
                "Mosquitos Infectivos": lambda m: sum(1 for a in m.schedule.agents
                                                      if isinstance(a, Mosquito) and getattr(a, "infectado", False)),
                "CasosReais": lambda m: m.casos_reais,
                "TempAmbiente": lambda m: m.temperatura_ambiente,
                "UmidAmbiente": lambda m: m.umidade_ambiente,
            }
        )

        print("✅ Modelo ABM+ML inicializado com APIs reais.")

    # ============================================================
    #  FUNÇÃO STEP — CORRIGIDA PARA MESA VIZ TORNADO
    # ============================================================

    def step(self):
        """Executa 1 dia da simulação."""

        # ------------------------------------------------------------
        # 1️⃣ COLETA DE DADOS — ANTES DE QUALQUER MUDANÇA
        # ------------------------------------------------------------
        self.datacollector.collect(self)

        # ------------------------------------------------------------
        # 2️⃣ EXECUTA TODOS OS AGENTES (MOVIMENTO + INTERAÇÃO)
        # ------------------------------------------------------------
        self.schedule.step()

        # ------------------------------------------------------------
        # 3️⃣ ATUALIZA DADOS REAIS DAS APIs (CLIMA E DENGUE)
        # ------------------------------------------------------------
        clima = obter_clima_sao_paulo_inmet()
        self.temperatura_ambiente = clima["temperatura"]
        self.umidade_ambiente = clima["umidade"]
        self.chuva_simulada = clima["chuva"]

        dengue = obter_dados_dengue_sp()
        self.casos_reais = dengue["casos_reais"]
        self.alerta_dengue = dengue["alerta"]

        # ------------------------------------------------------------
        # 4️⃣ TREINAMENTO DO MODELO DE ML (RF)
        # ------------------------------------------------------------
        self._aprender_com_dados()

        # ------------------------------------------------------------
        # 5️⃣ AVANÇA A DATA
        # ------------------------------------------------------------
        self.step_count += 1
        self.data_atual += timedelta(days=1)

        # ------------------------------------------------------------
        # 6️⃣ LOG BONITO (PARA O TERMINAL)
        # ------------------------------------------------------------
        print(f">>> Executando dia {self.data_atual.strftime('%d/%m/%Y')} (Step {self.step_count})")
        print(f"[Clima] T={self.temperatura_ambiente:.1f}°C | U={self.umidade_ambiente:.0f}% | Chuva={self.chuva_simulada:.2f}mm")
        print(f"[Dengue] {self.casos_reais} casos | Alerta={self.alerta_dengue}")
        print("--------------------------------------------------------")

    # ============================================================
    #  APRENDIZADO DE MÁQUINA (Random Forest)
    # ============================================================

    def _aprender_com_dados(self):
        novo = {
            "temperatura": self.temperatura_ambiente,
            "umidade": self.umidade_ambiente,
            "chuva": self.chuva_simulada,
            "casos_reais": self.casos_reais
        }

        self.dados_treinamento = pd.concat(
            [self.dados_treinamento, pd.DataFrame([novo])],
            ignore_index=True
        )

        if len(self.dados_treinamento) > 5:
            X = self.dados_treinamento[["temperatura", "umidade", "chuva"]]
            y = self.dados_treinamento["casos_reais"]

            self.ml_model.fit(X, y)
            pred = self.ml_model.predict([[self.temperatura_ambiente,
                                           self.umidade_ambiente,
                                           self.chuva_simulada]])[0]

            taxa_ajustada = min(max(pred / 1000, 0.05), 0.9)
            self.taxa_infeccao = taxa_ajustada

            print(f"🤖 [ML] Predição={pred:.1f} casos | Nova taxa infecção={self.taxa_infeccao:.2f}")

    # ============================================================
    #  EXPORTAÇÃO DE DADOS
    # ============================================================

    def salvar_dados_csv(self, caminho="dados_simulacao.csv"):
        df = self.datacollector.get_model_vars_dataframe()
        df.to_csv(caminho, index=False)
        print(f"💾 Dados de simulação salvos em {caminho}")

    def salvar_dados_ml(self, caminho="dados_aprendizado.csv"):
        if not self.dados_treinamento.empty:
            df = self.dados_treinamento.copy()
            df["step"] = np.arange(1, len(df) + 1)
            df["predicao"] = np.nan

            if len(df) > 5:
                X = df[["temperatura", "umidade", "chuva"]]
                df["predicao"] = self.ml_model.predict(X)

            df["taxa_infeccao"] = np.clip(df["predicao"] / 1000, 0.05, 0.9)
            df.to_csv(caminho, index=False)
            print(f"💾 Dados de aprendizado salvos em {caminho}")
