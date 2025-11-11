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
import threading
import webbrowser
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------------------------------------------------
# 🔧 CONFIGURAÇÃO: escolha o modo de execução
# ------------------------------------------------------------
# True = modo automático (rodando no terminal, coleta 15 dias)
# False = modo interativo (roda apenas na interface web)
MODO_AUTO = True


# ============================================================
# 1. Banner de alerta + data simulada
# ============================================================

class AlertaBanner(TextElement):
    """Mostra o alerta de dengue e a data simulada."""

    def render(self, model):
        alerta = getattr(model, "alerta_dengue", "Sem dados")
        data = getattr(model, "data_atual", None)
        data_str = data.strftime("%d/%m/%Y") if data else "Data não disponível"

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
# 2. Aparência dos agentes
# ============================================================

def agent_portrayal(agent):
    if agent is None:
        return
    portrayal = {"Shape": "circle", "Filled": "true", "Layer": 0}

    # Humanos
    if isinstance(agent, Human):
        portrayal["Layer"] = 2
        portrayal["r"] = 0.8
        if getattr(agent, "infectado", False):
            portrayal["Color"] = "red"
        elif getattr(agent, "vacinado", False):
            portrayal["Color"] = "#00FFAA"
        elif getattr(agent, "recuperado", False):
            portrayal["Color"] = "green"
        else:
            portrayal["Color"] = "blue"

    # Mosquitos
    elif isinstance(agent, Mosquito):
        portrayal["Layer"] = 1
        portrayal["r"] = 0.3
        portrayal["Color"] = "darkred" if getattr(agent, "infectado", False) else "orange"

    # Ambiente (células de risco)
    elif isinstance(agent, Environment):
        risco = getattr(agent, "risco_foco", 0)
        if risco < 0.3:
            color = "#A7D489"
        elif risco < 0.6:
            color = "#FFD966"
        else:
            color = "#E06666"
        portrayal = {"Shape": "rect", "w": 1, "h": 1, "Color": color, "Layer": 0}

    return portrayal


# ============================================================
# 3. Visualização (grid, gráficos, banner)
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
# 4. Parâmetros ajustáveis
# ============================================================

model_params = {
    "num_humanos": Slider("Número de Humanos", 100, 50, 400, 10),
    "num_mosquitos": Slider("Número de Mosquitos", 200, 100, 800, 10),
    "prob_contagio_humano": Slider("Prob. Contágio Humano", 0.3, 0.0, 1.0, 0.05),
    "vida_media_mosquito": Slider("Vida Média Mosquito (Dias)", 25, 10, 50, 1),
    "taxa_infeccao": Slider("Taxa Infecção Mosquito", 0.2, 0.0, 1.0, 0.05),
    "width": GRID_W,
    "height": GRID_H,
}


# ============================================================
# 5. Servidor Mesa
# ============================================================

server = ModularServer(
    DengueModel,
    [banner_alerta, grid, chart_epidemia, chart_clima],
    "🦟 Simulação da Dengue - ABM + ML (15 dias, dados reais)",
    model_params,
)
server.port = 8521


# ============================================================
# 6. Execução (manual ou automática)
# ============================================================

if __name__ == "__main__":
    print("🚀 Iniciando Simulação da Dengue (ABM + ML com APIs reais)")
    print(f"🌐 Acesse no navegador: http://127.0.0.1:{server.port}\n")

    if not MODO_AUTO:
        # --- modo interativo (manual) ---
        server.launch()

    else:
        # --- modo automático (simulação contínua + visualização) ---
        threading.Thread(target=server.launch, daemon=True).start()
        time.sleep(4)
        print("🎬 Simulação automática iniciada.\n")

        dias = 15
        for _ in range(dias):
            try:
                if getattr(server, "model", None):
                    model = server.model
                    model.step()

                    # 🔁 Atualiza interface (grid + gráficos)
                    try:
                        server.render_model()
                    except Exception as e:
                        print(f"⚠️ Falha na atualização visual: {e}")

                    print(f"📆 Dia {model.step_count} concluído ({model.data_atual.strftime('%d/%m/%Y')})\n")
                time.sleep(2.0)
            except KeyboardInterrupt:
                print("🛑 Simulação interrompida manualmente.")
                break
            except Exception as e:
                print(f"⚠️ Erro durante execução: {e}")
                break

        print("\n✅ Simulação de 15 dias concluída! Resultados salvos em CSV.")
