# ============================================================
# Dashboard Streamlit - Simulação da Dengue (ABM + ML + Vacinação)
# Versão Plotly (sem matplotlib) - Estilo NetLogo + Turbo
# Autor: Renato Jorge Correia Alpalhão
# ============================================================

import os
import time

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from dengue_model_ml import DengueModelML
from agents.human import Human
from agents.mosquito import Mosquito
from agents.environment import Environment

# ------------------------------------------------------------
# IMAGEIO (opcional) — para gerar GIF da simulação
# ------------------------------------------------------------
try:
    import imageio.v2 as imageio
    TEM_IMAGEIO = True
except Exception:
    TEM_IMAGEIO = False


# ============================================================
# Configuração da página
# ============================================================

st.set_page_config(
    page_title="Simulação da Dengue - ABM + ML",
    layout="wide",
)

st.title("🦟 Simulação da Dengue – ABM + Machine Learning + Vacinação")
st.markdown(
    """
Simulação Baseada em Agentes com Machine Learning (Random Forest),
vacinação, ambiente dinâmico e visualização animada estilo NetLogo.
"""
)


# ============================================================
# Funções auxiliares
# ============================================================

def criar_modelo(params: dict) -> DengueModelML:
    return DengueModelML(**params)


def gerar_dataframe(model: DengueModelML) -> pd.DataFrame:
    try:
        df = model.datacollector.get_model_vars_dataframe()
        if df is None or df.empty:
            return pd.DataFrame()
        df = df.reset_index().rename(columns={"index": "step"})
        df["dia"] = df["step"] + 1
        return df
    except Exception:
        return pd.DataFrame()


# ============================================================
# Visualização estilo NetLogo com Plotly
# ============================================================

def gerar_figura_plotly(model: DengueModelML) -> go.Figure:
    """
    Cria uma figura Plotly com:
    - Heatmap do risco ambiental (verde)
    - Heatmap da concentração de mosquitos infectados (vermelho)
    - Humanos (por estado)
    - Mosquitos (normais e infectados)
    """

    w, h = model.grid.width, model.grid.height

    # -------------------------
    # Matriz de risco ambiental
    # -------------------------
    matriz_risco = np.zeros((h, w))

    for cell in model.grid.coord_iter():
        contents, (x, y) = cell
        envs = [a for a in contents if isinstance(a, Environment)]
        if envs:
            matriz_risco[y, x] = envs[0].risco_foco

    # -------------------------
    # Heatmap de mosquitos infectados
    # -------------------------
    matriz_mosq_inf = np.zeros((h, w))

    for m in model.mosquitos:
        # mosquito sem posição (morto ou removido) → ignora
        if not hasattr(m, "pos"):
            continue
        if m.pos is None:
            continue
        if not m.infectado:
            continue

        x, y = m.pos
        if 0 <= x < w and 0 <= y < h:
            matriz_mosq_inf[y, x] += 1

    if matriz_mosq_inf.max() > 0:
        matriz_mosq_inf = matriz_mosq_inf / matriz_mosq_inf.max()

    # -------------------------
    # Listas de agentes (humanos + mosquitos)
    # -------------------------
    hx_saud, hy_saud = [], []
    hx_inf, hy_inf = [], []
    hx_rec, hy_rec = [], []
    hx_vac, hy_vac = [], []

    mx_norm, my_norm = [], []
    mx_inf_pts, my_inf_pts = [], []

    for a in model.schedule.agents:
        if not hasattr(a, "pos"):
            continue
        if a.pos is None:
            continue

        x, y = a.pos

        if isinstance(a, Human):
            if a.infectado:
                hx_inf.append(x); hy_inf.append(y)
            elif a.recuperado:
                hx_rec.append(x); hy_rec.append(y)
            elif a.vacinado:
                hx_vac.append(x); hy_vac.append(y)
            else:
                hx_saud.append(x); hy_saud.append(y)

        elif isinstance(a, Mosquito):
            if a.infectado:
                mx_inf_pts.append(x); my_inf_pts.append(y)
            else:
                mx_norm.append(x); my_norm.append(y)

    # -------------------------
    # Construção da figura Plotly
    # -------------------------
    fig = go.Figure()

    # Heatmap do ambiente (verdes)
    fig.add_trace(
        go.Heatmap(
            z=matriz_risco,
            colorscale="Greens",
            showscale=True,
            opacity=0.6,
            x=np.arange(w),
            y=np.arange(h),
            zsmooth=False,
            colorbar=dict(title="Risco Ambiente"),
            name="Risco Ambiente"
        )
    )

    # Heatmap dos mosquitos infectados (vermelhos)
    if matriz_mosq_inf.max() > 0:
        fig.add_trace(
            go.Heatmap(
                z=matriz_mosq_inf,
                colorscale="Reds",
                showscale=False,
                opacity=0.4,
                x=np.arange(w),
                y=np.arange(h),
                zsmooth=False,
                name="Mosquitos Infectados (densidade)"
            )
        )

    # Humanos – saudáveis
    if hx_saud:
        fig.add_trace(
            go.Scatter(
                x=hx_saud,
                y=hy_saud,
                mode="markers",
                name="Humano saudável",
                marker=dict(color="blue", size=8, line=dict(color="black", width=1))
            )
        )

    # Humanos – infectados
    if hx_inf:
        fig.add_trace(
            go.Scatter(
                x=hx_inf,
                y=hy_inf,
                mode="markers",
                name="Humano infectado",
                marker=dict(color="red", size=9, line=dict(color="black", width=1))
            )
        )

    # Humanos – recuperados
    if hx_rec:
        fig.add_trace(
            go.Scatter(
                x=hx_rec,
                y=hy_rec,
                mode="markers",
                name="Humano recuperado",
                marker=dict(color="green", size=8, line=dict(color="black", width=1))
            )
        )

    # Humanos – vacinados
    if hx_vac:
        fig.add_trace(
            go.Scatter(
                x=hx_vac,
                y=hy_vac,
                mode="markers",
                name="Humano vacinado",
                marker=dict(color="yellow", size=8, line=dict(color="black", width=1))
            )
        )

    # Mosquitos – normais
    if mx_norm:
        fig.add_trace(
            go.Scatter(
                x=mx_norm,
                y=my_norm,
                mode="markers",
                name="Mosquito",
                marker=dict(color="black", size=6, symbol="triangle-up")
            )
        )

    # Mosquitos – infectados
    if mx_inf_pts:
        fig.add_trace(
            go.Scatter(
                x=mx_inf_pts,
                y=my_inf_pts,
                mode="markers",
                name="Mosquito infectado",
                marker=dict(color="purple", size=7, symbol="triangle-up")
            )
        )

    fig.update_layout(
        title="Mapa ABM – Humanos, Mosquitos e Focos de Risco",
        xaxis=dict(title="X", range=[-0.5, w - 0.5], showgrid=False, zeroline=False),
        yaxis=dict(
            title="Y",
            range=[-0.5, h - 0.5],
            showgrid=False,
            zeroline=False,
            scaleanchor="x",
            scaleratio=1,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=10, r=10, t=50, b=40),
        template="plotly_white",
        height=520,
    )

    return fig


def atualizar_eventos(df: pd.DataFrame):
    if df is None or df.empty or len(df) < 2:
        return

    ult = df.iloc[-1]
    pen = df.iloc[-2]

    if "event_log" not in st.session_state:
        st.session_state.event_log = []

    def add(msg: str):
        st.session_state.event_log.append(msg)
        st.session_state.event_log = st.session_state.event_log[-30:]

    dia = int(ult["dia"])

    for col, texto in [
        ("Infectados", "novos infectados"),
        ("Recuperados", "novos recuperados"),
        ("Vacinados", "novos vacinados"),
        ("Mosquitos Infectivos", "mosquitos infectivos adicionais"),
    ]:
        if col in df.columns and ult[col] > pen[col]:
            add(f"Dia {dia}: {int(ult[col] - pen[col])} {texto}.")


def gerar_hotspots(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    lat_min, lat_max = -23.7, -23.5
    lon_min, lon_max = -46.8, -46.5

    n = 30
    lats = np.random.uniform(lat_min, lat_max, n)
    lons = np.random.uniform(lon_min, lon_max, n)
    intensidade = np.random.randint(1, 50, n)

    return pd.DataFrame({"lat": lats, "lon": lons, "casos": intensidade})


# ============================================================
# Sidebar – Parâmetros da Simulação
# ============================================================

st.sidebar.header("⚙️ Parâmetros da Simulação")

params = {
    "num_humanos": st.sidebar.slider("Humanos", 50, 1000, 300),
    "num_mosquitos": st.sidebar.slider("Mosquitos", 100, 1500, 400),
    "prob_contagio_humano": st.sidebar.slider("Probabilidade Contágio", 0.0, 1.0, 0.3),
    "vida_media_mosquito": st.sidebar.slider("Vida do Mosquito (dias)", 5, 40, 25),
    "taxa_infeccao": st.sidebar.slider("Taxa Infecção Inicial", 0.0, 1.0, 0.20),
    "percentual_vacinados": st.sidebar.slider("Vacinados (%)", 0, 100, 10),
    "width": 50,
    "height": 50,
}

dias_por_rodada = st.sidebar.slider("Dias por rodada (rápido / ao vivo)", 1, 90, 5)
velocidade = st.sidebar.slider("Velocidade (frames/seg)", 1, 30, 8)

st.sidebar.markdown("---")
bot_reset = st.sidebar.button("⏹ Resetar")
bot_run_fast = st.sidebar.button("⚡ Rodar Rápido")
bot_run_live = st.sidebar.button("▶ Ao Vivo")
bot_run_turbo = st.sidebar.button("🚀 Turbo 100 dias")


# ============================================================
# Inicialização do modelo
# ============================================================

if "modelo" not in st.session_state or bot_reset:
    st.session_state.modelo = criar_modelo(params)
    st.session_state.dias_total = 0
    st.session_state.event_log = []

modelo: DengueModelML = st.session_state.modelo

# ============================================================
# Execução da simulação
# ============================================================

placeholder_ao_vivo = st.empty()

# ⚡ Rápido (sem animação)
if bot_run_fast:
    for _ in range(dias_por_rodada):
        modelo.step()
        st.session_state.dias_total += 1

# 🚀 Turbo: 100 dias sem animação
if bot_run_turbo:
    for _ in range(100):
        modelo.step()
        st.session_state.dias_total += 1

# ▶ Ao Vivo (animação frame a frame)
if bot_run_live:
    for _ in range(dias_por_rodada):
        modelo.step()
        st.session_state.dias_total += 1

        fig_live = gerar_figura_plotly(modelo)
        placeholder_ao_vivo.plotly_chart(
            fig_live,
            use_container_width=True,
            key=f"live_map_{st.session_state.dias_total}"
        )
        time.sleep(1.0 / velocidade)

# ============================================================
# Dataframe e Eventos
# ============================================================

df = gerar_dataframe(modelo)
atualizar_eventos(df)

# ============================================================
# Indicadores principais
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Dia", modelo.data_atual.strftime("%d/%m/%Y"))
col2.metric("Infectados", int(df["Infectados"].iloc[-1]) if not df.empty else 0)
col3.metric("Vacinados", int(df["Vacinados"].iloc[-1]) if not df.empty else 0)
col4.metric(
    "Mosq. Infectivos",
    int(df["Mosquitos Infectivos"].iloc[-1]) if not df.empty else 0
)

st.markdown("---")

# ============================================================
# Mapa + Gráficos Epidemiológicos
# ============================================================

col_map, col_graph = st.columns([1.2, 1.4])

with col_map:
    st.subheader("🗺️ Mapa ABM – Humanos, Mosquitos e Focos de Risco")
    fig_map = gerar_figura_plotly(modelo)
    st.plotly_chart(
        fig_map,
        use_container_width=True,
        key="static_map"
    )

with col_graph:
    st.subheader("📈 Evolução epidemiológica")
    if not df.empty:
        st.line_chart(
            df.set_index("dia")[["Infectados", "Recuperados", "Vacinados", "Mosquitos Infectivos"]]
        )
    else:
        st.info("Execute alguns dias para visualizar os gráficos.")

# ============================================================
# Clima + CSV
# ============================================================

col_clima, col_csv = st.columns([1.2, 1.4])

with col_clima:
    st.subheader("🌦 Clima e Casos Reais")
    if not df.empty:
        st.line_chart(
            df.set_index("dia")[["TempAmbiente", "UmidAmbiente", "CasosReais"]]
        )

with col_csv:
    st.subheader("📊 Exportar CSV")
    if not df.empty:
        st.dataframe(df.tail(20))

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Baixar CSV Completo",
            csv,
            "simulacao_dengue.csv",
            "text/csv"
        )

# ============================================================
# Hotspots + Eventos
# ============================================================

col_hot, col_evt = st.columns([1.1, 1.4])

with col_hot:
    st.subheader("🗺 Hotspots em São Paulo (exemplo)")
    mapa = gerar_hotspots(df)
    if not mapa.empty:
        st.map(mapa)

with col_evt:
    st.subheader("🧾 Eventos recentes")
    if st.session_state.event_log:
        for e in reversed(st.session_state.event_log):
            st.write("•", e)
    else:
        st.info("Nenhum evento ainda.")

# ============================================================
# GIF (opcional)
# ============================================================

if TEM_IMAGEIO:
    if st.sidebar.button("🎞 Gerar GIF"):
        pasta = "resultados/frames"
        if os.path.isdir(pasta):
            frames = sorted(os.listdir(pasta))
            imagens = [
                imageio.imread(os.path.join(pasta, f))
                for f in frames
            ]

            imageio.mimsave("dengue_simulacao.gif", imagens, fps=8)
            st.success("GIF salvo como dengue_simulacao.gif")
