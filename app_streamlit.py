# ============================================================
# Dashboard Streamlit - Simulação da Dengue (ABM + ML)
# Autor: Renato Jorge Correia Alpalhão
# Projeto de Conclusão de Curso - SENAC
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

from dengue_model_ml import DengueModelML
from agents.human import Human
from agents.mosquito import Mosquito
from agents.environment import Environment

# ============================================================
# Configuração da página
# ============================================================

st.set_page_config(
    page_title="Simulação da Dengue - ABM + ML",
    layout="wide",
)

st.title("🦟 Simulação da Dengue - ABM + ML (Dashboard Streamlit)")
st.markdown(
    """
Painel interativo baseado em **Simulação Baseada em Agentes (ABM)** integrada com
**Machine Learning (Random Forest)** e uso de dados reais (clima + dengue).
"""
)

# ============================================================
# Funções auxiliares
# ============================================================

def criar_modelo(
    num_humanos: int,
    num_mosquitos: int,
    prob_contagio_humano: float,
    vida_media_mosquito: int,
    taxa_infeccao: float,
    width: int,
    height: int,
) -> DengueModelML:
    modelo = DengueModelML(
        num_humanos=num_humanos,
        num_mosquitos=num_mosquitos,
        prob_contagio_humano=prob_contagio_humano,
        vida_media_mosquito=vida_media_mosquito,
        taxa_infeccao=taxa_infeccao,
        width=width,
        height=height,
    )
    return modelo


def contar_humanos_infectados(model):
    return sum(1 for a in model.schedule.agents if isinstance(a, Human) and getattr(a, "infectado", False))


def contar_humanos_recuperados(model):
    return sum(1 for a in model.schedule.agents if isinstance(a, Human) and getattr(a, "recuperado", False))


def contar_mosquitos_infectivos(model):
    return sum(1 for a in model.schedule.agents if isinstance(a, Mosquito) and getattr(a, "infectado", False))


def gerar_matriz_grid(model):
    """
    Gera matriz [altura x largura] com níveis de risco + infecção.
    """
    w, h = model.grid.width, model.grid.height
    matriz = np.zeros((h, w))

    # base: risco do ambiente
    for cell in model.grid.coord_iter():
        contents, (x, y) = cell  # <-- correção importante
        envs = [a for a in contents if isinstance(a, Environment)]
        if envs:
            matriz[y, x] = envs[0].risco_foco

    # humanos infectados
    for a in model.schedule.agents:
        if isinstance(a, Human) and getattr(a, "infectado", False):
            x, y = a.pos
            matriz[y, x] += 0.5

    # mosquitos infectados
    for a in model.schedule.agents:
        if isinstance(a, Mosquito) and getattr(a, "infectado", False):
            x, y = a.pos
            matriz[y, x] += 0.3

    return np.clip(matriz, 0, 1)


def obter_dataframe(model):
    try:
        df = model.datacollector.get_model_vars_dataframe()
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index().rename(columns={"index": "step"})
        df["dia"] = df["step"] + 1
        return df
    except:
        return pd.DataFrame()


# ============================================================
# Sidebar - Controles
# ============================================================

st.sidebar.header("⚙️ Configuração da Simulação")

num_humanos = st.sidebar.slider("Número de Humanos", 50, 400, 150, 10)
num_mosquitos = st.sidebar.slider("Número de Mosquitos", 100, 1000, 300, 50)
prob_contagio_h = st.sidebar.slider("Prob. Contágio Humano", 0.0, 1.0, 0.3, 0.05)
vida_mosquito = st.sidebar.slider("Vida Média Mosquito (dias)", 5, 50, 25, 1)
taxa_infeccao_ini = st.sidebar.slider("Taxa Infecção Inicial", 0.0, 1.0, 0.2, 0.05)

grid_w, grid_h = 50, 50

dias_por_rodada = st.sidebar.slider("Dias por rodada", 1, 30, 1, 1)

st.sidebar.markdown("---")
resetar = st.sidebar.button("🔁 Resetar Simulação", type="primary")
rodar = st.sidebar.button("▶️ Rodar Simulação", type="secondary")
st.sidebar.markdown("---")


# ============================================================
# Inicialização do modelo (session_state)
# ============================================================

if "modelo" not in st.session_state or resetar:
    st.session_state.modelo = criar_modelo(
        num_humanos=num_humanos,
        num_mosquitos=num_mosquitos,
        prob_contagio_humano=prob_contagio_h,
        vida_media_mosquito=vida_mosquito,
        taxa_infeccao=taxa_infeccao_ini,
        width=grid_w,
        height=grid_h,
    )
    st.session_state.historico_rodadas = 0

modelo = st.session_state.modelo

if rodar:
    for _ in range(dias_por_rodada):
        modelo.step()
    st.session_state.historico_rodadas += dias_por_rodada


# ============================================================
# Indicadores (cards)
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Dia Simulado", modelo.data_atual.strftime("%d/%m/%Y"))

with col2:
    st.metric("Humanos Infectados", contar_humanos_infectados(modelo))

with col3:
    st.metric("Mosquitos Infectivos", contar_mosquitos_infectivos(modelo))

with col4:
    st.metric("Alerta de Dengue", getattr(modelo, "alerta_dengue", "Sem dados"))

st.markdown("---")


# ============================================================
# Linha 1: Grid + Gráfico epidemia
# ============================================================

col_grid, col_graf1 = st.columns([1.1, 1.2])

with col_grid:
    st.subheader("🗺️ Mapa da Simulação (Risco + Infectados)")
    matriz = gerar_matriz_grid(modelo)
    fig, ax = plt.subplots()
    im = ax.imshow(matriz, origin="lower", cmap="inferno")
    ax.set_xticks([]); ax.set_yticks([])
    plt.colorbar(im, ax=ax)
    st.pyplot(fig)

with col_graf1:
    st.subheader("📈 Evolução da Epidemia")
    df = obter_dataframe(modelo)
    if not df.empty:
        cols = ["Infectados", "Recuperados", "Mosquitos Infectivos"]
        cols = [c for c in cols if c in df.columns]
        if cols:
            st.line_chart(df.set_index("dia")[cols])
        else:
            st.info("Nenhum dado coletado ainda.")
    else:
        st.info("Execute alguns passos para gerar dados.")


# ============================================================
# Linha 2: clima + tabela
# ============================================================

col_graf2, col_tabela = st.columns([1.1, 1.2])

with col_graf2:
    st.subheader("🌤️ Clima e Casos Reais")
    if not df.empty:
        cols = ["TempAmbiente", "UmidAmbiente", "CasosReais"]
        cols = [c for c in cols if c in df.columns]
        if cols:
            st.line_chart(df.set_index("dia")[cols])
        else:
            st.info("Sem dados climáticos ainda.")
    else:
        st.info("Aguarde gerar dados.")

with col_tabela:
    st.subheader("📊 Dados da Simulação")
    if not df.empty:
        st.dataframe(df.tail(30), use_container_width=True)
        csv = df.to_csv().encode("utf-8")
        st.download_button(
            "💾 Baixar CSV completo",
            data=csv,
            file_name="dados_simulacao.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado disponível ainda.")


# ============================================================
# Aba de explicação para TCC
# ============================================================

with st.expander("📚 Explicação do Modelo (para TCC)"):
    st.markdown(
        """
### 🔬 Estrutura do Modelo ABM

- **Humanos**: suscetíveis, infectados, recuperados, vacinados.
- **Mosquitos**: infectados / não infectados, voam pelo grid e picam humanos.
- **Ambiente (Environment)**: cada célula tem densidade e risco de foco.

### 🤖 Machine Learning

- Modelo Random Forest.
- Entradas: temperatura, umidade, chuva.
- Saída: previsão de casos → ajusta a taxa de infecção.

### 🌐 Dados reais

- API do INMET para clima.
- API SP para casos de dengue.
- Se as APIs falham → modelo usa fallback simulado.

### 🧪 Interpretação

Este dashboard permite:
- visualizar a propagação espacial
- monitorar evolução temporal
- avaliar efeito do clima
- acompanhar ajustes do ML
"""
    )
