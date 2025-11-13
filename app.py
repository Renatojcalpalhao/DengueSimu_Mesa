# ============================================================
# Simulação da Dengue - ABM + ML (dados reais e APIs)
# Autor: Renato Jorge Correia Alpalhão
# Projeto de Conclusão de Curso - SENAC
# ============================================================

from mesa_viz_tornado.ModularVisualization import ModularServer
from mesa_viz_tornado.modules import CanvasGrid, ChartModule, TextElement
from mesa_viz_tornado.UserParam import Slider

from dengue_model_ml import DengueModelML as DengueModel
from agents.human import Human
from agents.mosquito import Mosquito
from agents.environment import Environment

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ============================================================
# Banner com alerta e data
# ============================================================

class AlertaBanner(TextElement):
    def render(self, model):
        alerta = getattr(model, "alerta_dengue", "Sem dados")
        data = getattr(model, "data_atual", None)
        data_str = data.strftime("%d/%m/%Y") if data else "Indefinido"

        cores = {
            "Verde": "#4CAF50",
            "Amarelo": "#FFC107",
            "Laranja": "#FF9800",
            "Vermelho": "#F44336",
            "Sem dados": "#9E9E9E",
        }

        cor = cores.get(alerta, "#9E9E9E")

        return f"""
        <div style='text-align:center; font-family:Arial;'>
            <h2 style='color:{cor}; margin:5px;'>🦟 Alerta de Dengue: <b>{alerta}</b></h2>
            <h3 style='color:#333;'>📅 Dia Simulado: {data_str}</h3>
        </div>
        """


# ============================================================
# Aparência dos agentes
# ============================================================

def agent_portrayal(agent):
    if agent is None:
        return

    # Ambiente
    if isinstance(agent, Environment):
        risco = agent.risco_foco
        if risco < 0.3: color = "#A7D489"
        elif risco < 0.6: color = "#FFD966"
        else: color = "#E06666"

        return {"Shape": "rect", "w": 1, "h": 1, "Color": color, "Layer": 0}

    # Humanos
    if isinstance(agent, Human):
        if agent.infectado:
            cor = "red"
        elif agent.recuperado:
            cor = "green"
        elif agent.vacinado:
            cor = "#00FFAA"
        else:
            cor = "blue"

        return {"Shape": "circle", "r": 0.8, "Filled": "true", "Color": cor, "Layer": 2}

    # Mosquitos
    if isinstance(agent, Mosquito):
        cor = "darkred" if agent.infectado else "orange"
        return {"Shape": "circle", "r": 0.3, "Filled": "true", "Color": cor, "Layer": 1}

    return None


# ============================================================
# Visualização
# ============================================================

GRID_W, GRID_H = 50, 50

grid = CanvasGrid(agent_portrayal, GRID_W, GRID_H, 500, 500)
banner_alerta = AlertaBanner()

chart_epidemia = ChartModule(
    [
        {"Label": "Infectados", "Color": "Red"},
        {"Label": "Recuperados", "Color": "Green"},
        {"Label": "Vacinados", "Color": "#00FFAA"},
        {"Label": "Mosquitos Infectivos", "Color": "Orange"},
    ],
    data_collector_name="datacollector",
)

chart_clima = ChartModule(
    [
        {"Label": "TempAmbiente", "Color": "Blue"},
        {"Label": "UmidAmbiente", "Color": "Cyan"},
        {"Label": "CasosReais", "Color": "Purple"},
    ],
    data_collector_name="datacollector",
)


# ============================================================
# Parâmetros ajustáveis pela interface
# ============================================================

model_params = {
    "num_humanos": Slider("Número de Humanos", 150, 50, 300, 10),
    "num_mosquitos": Slider("Número de Mosquitos", 300, 100, 800, 10),
    "prob_contagio_humano": Slider("Prob. Contágio Humano", 0.3, 0.0, 1.0, 0.05),
    "vida_media_mosquito": Slider("Vida Média do Mosquito", 25, 10, 50, 1),
    "taxa_infeccao": Slider("Taxa Infecção Mosquito", 0.2, 0.0, 1.0, 0.05),
    "width": GRID_W,
    "height": GRID_H,
}


# ============================================================
# Servidor do MesaVizTornado
# ============================================================

server = ModularServer(
    DengueModel,
    [banner_alerta, grid, chart_epidemia, chart_clima],
    "🦟 Simulação da Dengue - ABM + ML (3 meses - modo visual)",
    model_params,
)
server.port = 8521


# ============================================================
# Execução — SEM MODO AUTOMÁTICO
# ============================================================

if __name__ == "__main__":
    print("🚀 Iniciando Simulação da Dengue - Modo Visual")
    print("🌐 Acesse: http://127.0.0.1:8521\n")

    # 👉 Agora a simulação só é controlada pela interface
    server.launch()
