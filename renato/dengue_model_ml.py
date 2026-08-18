# ============================================================
#  Modelo Híbrido ABM + Machine Learning (Random Forest)
#  + Vacinação + Clima Real + Casos Reais + Ciclo Completo do Mosquito
#  Versão Melhorada para Integração com React/WebSocket
#  Autor: Renato Jorge Correia Alpalhão
#  Projeto de Conclusão de Curso - SENAC
# ============================================================

from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

from sklearn.ensemble import RandomForestRegressor
import warnings

# --- Importações internas ---
from agents.human import Human
from agents.mosquito import Mosquito
from agents.environment import Environment
from agents.egg import Egg
from agents.larva import Larva

from api.clima import obter_clima_sao_paulo_inmet
from api.dengue_api import obter_dados_dengue_sp
from api.data_loader import get_densidade_fator_por_coordenada

warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================
#  MODELO PRINCIPAL — DengueModelML (Modelo B)
# ============================================================

class DengueModelML(Model):
    """
    Modelo de Dengue com:
    - Humanos (Suscetíveis / Expostos / Infectados / Recuperados + Vacinação)
    - Mosquitos (Suscetíveis / Expostos / Infectados)
    - Ovos e Larvas (ciclo completo do Aedes)
    - Ambiente (células com densidade e risco de foco)
    - Clima real / simulado + Casos reais
    - Aprendizado de Máquina (Random Forest) ajustando taxa de infecção
    - Integração com WebSocket para frontend React
    """

    def __init__(
        self,
        num_humanos=150,
        num_mosquitos=300,
        taxa_infeccao=0.2,           # prob. mosquito pega dengue ao picar humano infectado
        width=50,
        height=50,
        prob_contagio_humano=0.3,    # prob. humano infectar ao ser picado
        vida_media_mosquito=25,
        percentual_vacinados=0,
        simulation_speed=1.0,
        **kwargs
    ):
        super().__init__(**kwargs)

        # --------------------------------------------------------
        # PARÂMETROS DO MODELO
        # --------------------------------------------------------
        self.num_humanos = num_humanos
        self.num_mosquitos = num_mosquitos
        self.taxa_infeccao = taxa_infeccao
        self.prob_contagio_humano = prob_contagio_humano
        self.vida_media_mosquito = vida_media_mosquito
        self.percentual_vacinados = percentual_vacinados
        self.simulation_speed = simulation_speed
        self.paused = False

        # --------------------------------------------------------
        # ESTADO TEMPORAL
        # --------------------------------------------------------
        self.step_count = 0
        self.data_atual = datetime(2025, 1, 1)

        # --------------------------------------------------------
        # ESTADO CLIMÁTICO / CASOS
        # --------------------------------------------------------
        self.temperatura_ambiente = 27.0
        self.umidade_ambiente = 70.0
        self.chuva_simulada = 0.20

        self.casos_reais = 0
        self.alerta_dengue = "Sem dados"

        # --------------------------------------------------------
        # GRID E SCHEDULER
        # --------------------------------------------------------
        self.grid = MultiGrid(width, height, torus=True)
        self.schedule = BaseScheduler(self)

        # --------------------------------------------------------
        # 1) CRIAÇÃO DO AMBIENTE (Environment)
        # --------------------------------------------------------
        for x in range(width):
            for y in range(height):
                dens, risco = get_densidade_fator_por_coordenada(width, height, x, y)
                env = Environment(self.next_id(), self, dens, risco)
                self.grid.place_agent(env, (x, y))
                self.schedule.add(env)

        # --------------------------------------------------------
        # 2) HUMANOS
        # --------------------------------------------------------
        self.humanos = []

        for i in range(self.num_humanos):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            # casa e trabalho iguais (modelo simples)
            h = Human(self.next_id(), self, casa=(x, y), trabalho=(x, y))

            # Paciente zero
            if i == 0:
                h.estado = "I"
                h.infectado = True

            self.humanos.append(h)
            self.grid.place_agent(h, (x, y))
            self.schedule.add(h)

        # Vacinação inicial
        self._vacinar_populacao()

        # --------------------------------------------------------
        # 3) MOSQUITOS ADULTOS
        # --------------------------------------------------------
        self.mosquitos = []

        # fração inicial infectada (por ex. 5% dos mosquitos)
        frac_inicial_infectada = 0.05
        n_inf_inicial = max(1, int(self.num_mosquitos * frac_inicial_infectada))

        for i in range(self.num_mosquitos):
            x = self.random.randrange(width)
            y = self.random.randrange(height)

            m = Mosquito(self.next_id(), self)

            # primeiros mosquitos começam infectados
            if i < n_inf_inicial:
                m.estado = "I"
                m.infectado = True

            self.mosquitos.append(m)
            self.grid.place_agent(m, (x, y))
            self.schedule.add(m)

        # coleções auxiliares (não são estritamente necessárias, mas ajudam)
        self.ovos = []
        self.larvas = []

        # --------------------------------------------------------
        # 4) MACHINE LEARNING (Random Forest)
        # --------------------------------------------------------
        self.ml_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )

        # dados para treinar o ML
        self.dados_treinamento = pd.DataFrame(
            columns=["temperatura", "umidade", "chuva", "casos_reais"]
        )

        # Histórico para tendências
        self.historico_metricas = {
            "infectados": [],
            "vacinados": [],
            "mosquitos_infectados": [],
            "temperatura": [],
            "umidade": []
        }

        # --------------------------------------------------------
        # 5) COLETOR DE DADOS (DataCollector)
        # --------------------------------------------------------
        self.datacollector = DataCollector(
            model_reporters={
                "Passo": lambda m: m.step_count,
                "Infectados": lambda m: m.get_infectados_count(),
                "Recuperados": lambda m: m.get_recuperados_count(),
                "Vacinados": lambda m: m.get_vacinados_count(),
                "Mosquitos_Infectivos": lambda m: m.get_mosquitos_infectados_count(),
                "TempAmbiente": lambda m: m.temperatura_ambiente,
                "UmidAmbiente": lambda m: m.umidade_ambiente,
                "CasosReais": lambda m: m.casos_reais,
                "Taxa_Infeccao_ML": lambda m: m.taxa_infeccao,
                "Ovos": lambda m: m.get_ovos_count(),
                "Larvas": lambda m: m.get_larvas_count(),
            }
        )

        print("💉 Modelo ABM+ML inicializado com sucesso (Modelo B).")
        print(f"   Humanos: {self.num_humanos}, Mosquitos: {self.num_mosquitos}, "
              f"Vacinados iniciais: {self.percentual_vacinados}%")

    # ============================================================
    #  VACINAÇÃO INICIAL
    # ============================================================

    def _vacinar_populacao(self):
        """Vacina uma porcentagem da população humana no início da simulação."""
        if self.percentual_vacinados <= 0:
            return

        total = len(self.humanos)
        n = int(total * (self.percentual_vacinados / 100))

        if n <= 0:
            return

        selecionados = random.sample(self.humanos, n)
        for h in selecionados:
            h.vacinado = True
            h.tempo_desde_vacinacao = 0

        print(f"💉 {n}/{total} humanos vacinados ({self.percentual_vacinados}%).")

    # ============================================================
    #  STEP — Executa um dia completo
    # ============================================================

    def step(self):
        """
        Ordem do Modelo B:
        1. Executa todos os agentes (Human, Mosquito, Environment, Egg, Larva)
        2. Atualiza clima (INMET ou simulado)
        3. Atualiza casos de dengue (API ou simulado)
        4. ML aprende com dados e ajusta taxa de infecção
        5. Avança o relógio
        6. Coleta dados para gráficos / Streamlit / CSV
        """

        if self.paused:
            return

        # 1 — Agentes se movem, picam, reproduzem, atualizam estados
        self.schedule.step()

        # Contagem rápida para log
        num_inf_h = self.get_infectados_count()
        num_inf_m = self.get_mosquitos_infectados_count()

        # 2 — Clima (API + fallback)
        self._atualizar_clima()

        # 3 — Casos reais de dengue (API + fallback)
        self._atualizar_casos_dengue()

        # 4 — Machine Learning: aprende com o novo dia
        self._aprender_com_dados()

        # 5 — Atualizar histórico para tendências
        self._atualizar_historico()

        # 6 — Avança o tempo simulado (1 dia)
        self.step_count += 1
        self.data_atual += timedelta(days=1)

        # 7 — Coleta dados para DataCollector
        self.datacollector.collect(self)

        # Log básico para o terminal
        print(
            f"📅 Dia {self.data_atual.strftime('%d/%m/%Y')} | "
            f"Humanos infectados: {num_inf_h} | Mosquitos infectados: {num_inf_m} | "
            f"Taxa ML: {self.taxa_infeccao:.3f}"
        )

    def _atualizar_clima(self):
        """Atualiza dados climáticos"""
        try:
            clima = obter_clima_sao_paulo_inmet()
            self.temperatura_ambiente = clima.get("temperatura", self.temperatura_ambiente)
            self.umidade_ambiente = clima.get("umidade", self.umidade_ambiente)
            self.chuva_simulada = clima.get("chuva", self.chuva_simulada)
        except Exception as e:
            # fallback simples: pequenas variações aleatórias
            self.temperatura_ambiente = max(15.0, min(35.0, 
                self.temperatura_ambiente + random.uniform(-0.5, 0.5)))
            self.umidade_ambiente = min(100.0, max(40.0, 
                self.umidade_ambiente + random.uniform(-2.0, 2.0)))
            self.chuva_simulada = min(1.0, max(0.0, 
                self.chuva_simulada + random.uniform(-0.1, 0.1)))
            print(f"⚠️ Erro ao obter dados do INMET ({e}) — usando clima simulado.")

    def _atualizar_casos_dengue(self):
        """Atualiza casos reais de dengue"""
        try:
            dengue = obter_dados_dengue_sp()
            self.casos_reais = dengue.get("casos_reais", self.casos_reais)
            self.alerta_dengue = dengue.get("alerta", self.alerta_dengue)
        except Exception as e:
            # fallback: série sintética baseada na simulação
            base = 50 + int(self.get_infectados_count() * 10 * random.random())
            self.casos_reais = base
            self.alerta_dengue = random.choice(["Verde", "Amarelo", "Laranja", "Vermelho"])
            print(f"⚠️ Erro ao obter dados de dengue ({e}) — usando série sintética.")

    def _atualizar_historico(self):
        """Atualiza histórico para cálculo de tendências"""
        self.historico_metricas["infectados"].append(self.get_infectados_count())
        self.historico_metricas["vacinados"].append(self.get_vacinados_count())
        self.historico_metricas["mosquitos_infectados"].append(self.get_mosquitos_infectados_count())
        self.historico_metricas["temperatura"].append(self.temperatura_ambiente)
        self.historico_metricas["umidade"].append(self.umidade_ambiente)
        
        # Mantém apenas os últimos 30 dias no histórico
        for key in self.historico_metricas:
            if len(self.historico_metricas[key]) > 30:
                self.historico_metricas[key] = self.historico_metricas[key][-30:]

    # ============================================================
    #  MACHINE LEARNING
    # ============================================================

    def _aprender_com_dados(self):
        """
        Alimenta o RandomForest com (temperatura, umidade, chuva) -> casos_reais
        e ajusta a taxa de infecção com base na previsão do modelo.
        """

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

        # Só treina depois de alguns dias (para evitar overfit imediato)
        if len(self.dados_treinamento) > 7:
            X = self.dados_treinamento[["temperatura", "umidade", "chuva"]]
            y = self.dados_treinamento["casos_reais"]

            self.ml_model.fit(X, y)

            # usa o último clima como input
            X_hoje = pd.DataFrame(
                [[self.temperatura_ambiente, self.umidade_ambiente, self.chuva_simulada]],
                columns=["temperatura", "umidade", "chuva"]
            )
            pred = float(self.ml_model.predict(X_hoje)[0])

            # mapeia previsão de casos para taxa [0.05, 0.9]
            taxa_ajustada = pred / 1000.0
            taxa_ajustada = min(max(taxa_ajustada, 0.05), 0.9)
            self.taxa_infeccao = taxa_ajustada

            print(f"🤖 ML: pred={pred:.1f} casos  | nova taxa={self.taxa_infeccao:.3f}")

    # ============================================================
    #  MÉTODOS PARA WEB SOCKET / FRONTEND
    # ============================================================

    def get_simulation_data(self):
        """Retorna dados completos da simulação para WebSocket"""
        humans_data = []
        mosquitos_data = []
        eggs_data = []
        larvae_data = []
        env_data = []

        # Coleta dados de todos os agentes
        for agent in self.schedule.agents:
            pos = agent.pos if hasattr(agent, 'pos') and agent.pos else (0, 0)
            
            if isinstance(agent, Human):
                humans_data.append({
                    "x": pos[0], "y": pos[1],
                    "estado": getattr(agent, 'estado', 'S'),
                    "vacinado": getattr(agent, 'vacinado', False),
                    "infectado": getattr(agent, 'infectado', False),
                    "recuperado": getattr(agent, 'recuperado', False)
                })
            elif isinstance(agent, Mosquito):
                mosquitos_data.append({
                    "x": pos[0], "y": pos[1],
                    "estado": getattr(agent, 'estado', 'S'),
                    "infectado": getattr(agent, 'infectado', False)
                })
            elif isinstance(agent, Egg):
                eggs_data.append({
                    "x": pos[0], "y": pos[1]
                })
            elif isinstance(agent, Larva):
                larvae_data.append({
                    "x": pos[0], "y": pos[1]
                })
            elif isinstance(agent, Environment):
                env_data.append({
                    "x": pos[0], "y": pos[1],
                    "risco": getattr(agent, 'risco', 0),
                    "densidade": getattr(agent, 'densidade', 0)
                })

        # Calcula tendências
        tendencia_infectados = self._calcular_tendencia("infectados")
        tendencia_vacinados = self._calcular_tendencia("vacinados")

        return {
            "day": self.data_atual.strftime('%Y-%m-%d'),
            "step": self.step_count,
            "width": self.grid.width,
            "height": self.grid.height,
            "humans": humans_data,
            "mosquitos": mosquitos_data,
            "eggs": eggs_data,
            "larvae": larvae_data,
            "env": env_data,
            "infectados": self.get_infectados_count(),
            "vacinados": self.get_vacinados_count(),
            "mosquitos_infectados": self.get_mosquitos_infectados_count(),
            "temp": round(self.temperatura_ambiente, 1),
            "umid": round(self.umidade_ambiente, 1),
            "taxa_infeccao": round(self.taxa_infeccao, 3),
            "casos_reais": self.casos_reais,
            "alerta_dengue": self.alerta_dengue,
            "tendencias": {
                "infectados": tendencia_infectados,
                "vacinados": tendencia_vacinados
            },
            "estatisticas": {
                "total_humanos": self.num_humanos,
                "total_mosquitos": len(self.mosquitos),
                "cobertura_vacinal": round((self.get_vacinados_count() / self.num_humanos) * 100, 1),
                "taxa_ataque": round((self.get_infectados_count() / self.num_humanos) * 100, 1)
            }
        }

    def _calcular_tendencia(self, metrica):
        """Calcula tendência da métrica (up, down, stable)"""
        historico = self.historico_metricas.get(metrica, [])
        if len(historico) < 2:
            return "stable"
        
        recente = historico[-1] if historico else 0
        anterior = historico[-2] if len(historico) >= 2 else 0
        
        if recente > anterior:
            return "up"
        elif recente < anterior:
            return "down"
        else:
            return "stable"

    # ============================================================
    #  CONTROLES DA SIMULAÇÃO
    # ============================================================

    def toggle_pause(self):
        """Pausa ou continua a simulação"""
        self.paused = not self.paused
        status = "pausada" if self.paused else "executando"
        print(f"⏸️ Simulação {status}")

    def set_simulation_speed(self, speed):
        """Define velocidade da simulação"""
        self.simulation_speed = max(0.1, min(5.0, speed))
        print(f"⚡ Velocidade da simulação: {self.simulation_speed}x")

    def apply_control_measure(self, measure_type, **kwargs):
        """Aplica medidas de controle via frontend"""
        if measure_type == "vaccination":
            percent = kwargs.get("percent", 10)
            self._apply_emergency_vaccination(percent)
        elif measure_type == "fogging":
            self._apply_fogging()
        elif measure_type == "reset":
            self._reset_simulation()
        elif measure_type == "add_humans":
            count = kwargs.get("count", 10)
            self._add_humans(count)
        elif measure_type == "add_mosquitos":
            count = kwargs.get("count", 20)
            self._add_mosquitos(count)

    def _apply_emergency_vaccination(self, percent):
        """Vacinação de emergência"""
        humanos_nao_vacinados = [h for h in self.humanos if not h.vacinado]
        n = int(len(humanos_nao_vacinados) * (percent / 100))
        n = min(n, len(humanos_nao_vacinados))
        
        for h in random.sample(humanos_nao_vacinados, n):
            h.vacinado = True
            h.tempo_desde_vacinacao = 0
        
        print(f"🚨 Vacinação de emergência: {n} humanos vacinados")

    def _apply_fogging(self):
        """Aplica fumacê - elimina mosquitos adultos"""
        mosquitos_eliminados = 0
        for mosquito in self.mosquitos[:]:
            if random.random() < 0.7:  # 70% de eficácia
                self.schedule.remove(mosquito)
                self.grid.remove_agent(mosquito)
                self.mosquitos.remove(mosquito)
                mosquitos_eliminados += 1
        
        print(f"💨 Fumacê aplicado: {mosquitos_eliminados} mosquitos eliminados")

    def _add_humans(self, count):
        """Adiciona novos humanos à simulação"""
        for _ in range(count):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            
            h = Human(self.next_id(), self, casa=(x, y), trabalho=(x, y))
            self.humanos.append(h)
            self.grid.place_agent(h, (x, y))
            self.schedule.add(h)
        
        self.num_humanos += count
        print(f"👥 Adicionados {count} novos humanos. Total: {self.num_humanos}")

    def _add_mosquitos(self, count):
        """Adiciona novos mosquitos à simulação"""
        for _ in range(count):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            
            m = Mosquito(self.next_id(), self)
            self.mosquitos.append(m)
            self.grid.place_agent(m, (x, y))
            self.schedule.add(m)
        
        print(f"🦟 Adicionados {count} novos mosquitos. Total: {len(self.mosquitos)}")

    def _reset_simulation(self):
        """Reinicia a simulação mantendo parâmetros"""
        print("🔄 Reiniciando simulação...")
        # Mantém os parâmetros atuais
        params = {
            "num_humanos": self.num_humanos,
            "num_mosquitos": self.num_mosquitos,
            "percentual_vacinados": self.percentual_vacinados,
            "width": self.grid.width,
            "height": self.grid.height
        }
        
        # Recria o modelo
        self.__init__(**params)

    # ============================================================
    #  MÉTODOS DE CONTAGEM
    # ============================================================

    def get_infectados_count(self):
        return sum(1 for a in self.schedule.agents 
                  if isinstance(a, Human) and getattr(a, 'infectado', False))

    def get_vacinados_count(self):
        return sum(1 for a in self.schedule.agents 
                  if isinstance(a, Human) and getattr(a, 'vacinado', False))

    def get_recuperados_count(self):
        return sum(1 for a in self.schedule.agents 
                  if isinstance(a, Human) and getattr(a, 'recuperado', False))

    def get_mosquitos_infectados_count(self):
        return sum(1 for a in self.schedule.agents 
                  if isinstance(a, Mosquito) and getattr(a, 'infectado', False))

    def get_ovos_count(self):
        return sum(1 for a in self.schedule.agents 
                  if isinstance(a, Egg))

    def get_larvas_count(self):
        return sum(1 for a in self.schedule.agents 
                  if isinstance(a, Larva))

    # ============================================================
    #  RELATÓRIOS E ESTATÍSTICAS
    # ============================================================

    def get_detailed_report(self):
        """Retorna relatório detalhado da simulação"""
        return {
            "geral": {
                "dia": self.data_atual.strftime('%d/%m/%Y'),
                "passo": self.step_count,
                "velocidade": self.simulation_speed,
                "pausada": self.paused
            },
            "populacao": {
                "total_humanos": self.num_humanos,
                "total_mosquitos": len(self.mosquitos),
                "ovos": self.get_ovos_count(),
                "larvas": self.get_larvas_count()
            },
            "saude": {
                "infectados": self.get_infectados_count(),
                "vacinados": self.get_vacinados_count(),
                "recuperados": self.get_recuperados_count(),
                "mosquitos_infectados": self.get_mosquitos_infectados_count(),
                "taxa_ataque": f"{(self.get_infectados_count() / self.num_humanos * 100):.1f}%",
                "cobertura_vacinal": f"{(self.get_vacinados_count() / self.num_humanos * 100):.1f}%"
            },
            "ambiente": {
                "temperatura": f"{self.temperatura_ambiente:.1f}°C",
                "umidade": f"{self.umidade_ambiente:.1f}%",
                "chuva": f"{self.chuva_simulada * 100:.1f}%",
                "alerta_dengue": self.alerta_dengue
            },
            "machine_learning": {
                "taxa_infeccao": f"{self.taxa_infeccao:.3f}",
                "amostras_treinamento": len(self.dados_treinamento),
                "casos_reais": self.casos_reais
            }
        }

    def export_data(self):
        """Exporta dados para análise externa"""
        model_data = self.datacollector.get_model_vars_dataframe()
        return {
            "model_data": model_data.to_dict('records'),
            "training_data": self.dados_treinamento.to_dict('records'),
            "historico": self.historico_metricas
        }


# ============================================================
#  FUNÇÃO DE INICIALIZAÇÃO RÁPIDA
# ============================================================

def create_simulation(**kwargs):
    """Cria uma nova instância da simulação com parâmetros personalizados"""
    return DengueModelML(**kwargs)


if __name__ == "__main__":
    # Exemplo de uso
    model = DengueModelML(
        num_humanos=200,
        num_mosquitos=400,
        percentual_vacinados=15,
        width=40,
        height=40
    )
    
    print("🎯 Simulação criada com sucesso!")
    print("Use model.step() para avançar ou model.get_simulation_data() para obter dados")