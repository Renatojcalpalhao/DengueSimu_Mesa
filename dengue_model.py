# ============================================================
#  Modelo de Simulação da Dengue - Mesa 2.x
#  Autor: Renato Jorge Correia Alpalhão
#  Projeto de Conclusão de Curso - SENAC
# ============================================================

from mesa import Model
from mesa.time import BaseScheduler
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
import random
import datetime
import pandas as pd

# Importações dos agentes e APIs simuladas
from agents.human import Human
from agents.mosquito import Mosquito
from agents.environment import Environment
from api.clima import obter_clima_sao_paulo_inmet
from api.dengue_api import obter_dados_dengue_sp
from api.data_loader import get_densidade_fator_por_coordenada
from api.interventions import aplicar_vacinacao


class DengueModel(Model):
    """
    Modelo principal da simulação da dengue.
    Gerencia humanos, mosquitos e células ambientais.
    """

    def __init__(
        self,
        num_humanos=50,
        num_mosquitos=100,
        taxa_infeccao=0.2,
        width=50,
        height=50,
        prob_contagio_humano=0.3,
        vida_media_mosquito=25,
        **kwargs
    ):
        super().__init__(**kwargs)

        # --- Parâmetros principais ---
        self.num_humanos = num_humanos
        self.num_mosquitos = num_mosquitos
        self.taxa_infeccao = taxa_infeccao
        self.prob_contagio_humano = prob_contagio_humano
        self.vida_media_mosquito = vida_media_mosquito
        self.step_count = 0

        # --- Data simulada ---
        self.data_inicial = datetime.date(2025, 1, 1)
        self.data_atual = self.data_inicial

        # --- Estado climático e epidemiológico ---
        self.temperatura_ambiente = 28.0
        self.chuva_simulada = 0.5
        self.umidade_ambiente = 70.0
        self.casos_reais = 0
        self.alerta_dengue = "Sem dados"

        # --- Estrutura do modelo ---
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = BaseScheduler(self)
        self.fator_densidade_total = 0

        # ============================================================
        # 1. Criação do ambiente (Environment)
        # ============================================================
        lista_de_coordenadas = []
        for x in range(width):
            for y in range(height):
                fator_densidade, fator_risco_estrutural = get_densidade_fator_por_coordenada(
                    width, height, x, y
                )
                ambiente = Environment(self.next_id(), self, fator_densidade, fator_risco_estrutural)
                self.grid.place_agent(ambiente, (x, y))
                self.schedule.add(ambiente)
                self.fator_densidade_total += fator_densidade
                lista_de_coordenadas.append((x, y))

        if self.fator_densidade_total == 0:
            self.fator_densidade_total = 1

        # ============================================================
        # 2. Criação dos agentes Humanos e Mosquitos
        # ============================================================

        coordenadas = lista_de_coordenadas
        pesos = [1.0 for _ in coordenadas]  # pesos iguais (pode ser modificado)

        # Humanos
        posicoes_humanos = random.choices(coordenadas, weights=pesos, k=self.num_humanos)
        for i, (x, y) in enumerate(posicoes_humanos):
            humano = Human(self.next_id(), self, casa_pos=(x, y), trabalho_pos=(x, y))
            self.schedule.add(humano)
            self.grid.place_agent(humano, (x, y))
            if i == 0:
                humano.infectado = True  # paciente zero

        # Mosquitos
        posicoes_mosquitos = random.choices(coordenadas, weights=pesos, k=self.num_mosquitos)
        for (x, y) in posicoes_mosquitos:
            mosquito = Mosquito(self.next_id(), self)
            self.schedule.add(mosquito)
            self.grid.place_agent(mosquito, (x, y))

        # ============================================================
        # 3. Coletor de dados (DataCollector)
        # ============================================================
        self.datacollector = DataCollector(
            model_reporters={
                "Passo": lambda m: m.step_count,
                "Infectados": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, Human) and getattr(a, "infectado", False)
                ),
                "Recuperados": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, Human) and getattr(a, "recuperado", False)
                ),
                "Vacinados": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, Human) and getattr(a, "vacinado", False)
                ),
                "Mosquitos Infectivos": lambda m: sum(
                    1 for a in m.schedule.agents if isinstance(a, Mosquito) and getattr(a, "infectado", False)
                ),
                "CasosReais": lambda m: m.casos_reais,
                "TempAmbiente": lambda m: m.temperatura_ambiente,
                "UmidAmbiente": lambda m: m.umidade_ambiente,
            }
        )

    # ============================================================
    # 4. Step de simulação
    # ============================================================
    def step(self):
        """Executa um passo da simulação."""
        # 1. Atualiza data
        self.data_atual = self.data_inicial + datetime.timedelta(days=self.step_count)

        # 2. Atualiza clima (simulado ou via API)
        dados_clima = obter_clima_sao_paulo_inmet()
        self.temperatura_ambiente = dados_clima["temperatura"]
        self.chuva_simulada = dados_clima["chuva"]
        self.umidade_ambiente = dados_clima["umidade"]

        # 3. Atualiza casos reais de dengue
        dados_dengue = obter_dados_dengue_sp()
        self.casos_reais = dados_dengue["casos_reais"]
        self.alerta_dengue = dados_dengue["alerta"]

        # 4. Executa agentes
        self.schedule.step()

        # 5. Intervenção: vacinação periódica
        if self.step_count % 30 == 0 and self.step_count > 0:
            aplicar_vacinacao(self, porcentagem_alvo=0.1)

        # 6. Coleta de dados
        self.datacollector.collect(self)

        # 7. Incrementa passo
        self.step_count += 1

        # 8. Log de status
        print(
            f">>> Executando dia {self.data_atual.strftime('%d/%m/%Y')} (Step {self.step_count})"
        )
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Clima simulado: T={self.temperatura_ambiente:.1f}°C, "
            f"U={self.umidade_ambiente:.0f}%, Chuva={self.chuva_simulada:.2f}"
        )
        print(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Dengue simulada: {self.casos_reais} casos, Alerta={self.alerta_dengue}"
        )

    # ============================================================
    # 5. Exportar dados
    # ============================================================
    def salvar_dados_csv(self, caminho="dados_simulacao.csv"):
        """Exporta os dados do DataCollector para CSV."""
        df = self.datacollector.get_model_vars_dataframe()
        df.to_csv(caminho, index=False, encoding="utf-8")
        print(f"💾 Dados exportados para {caminho}")
