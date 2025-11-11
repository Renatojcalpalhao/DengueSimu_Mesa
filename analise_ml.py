# ============================================================
# Arquivo: analise_ml.py
# Descrição: Análise de resultados do modelo ABM + ML da Dengue
# Autor: Renato Jorge Correia Alpalhão
# Projeto de Conclusão de Curso - SENAC
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.grid"] = True

# ------------------------------------------------------------
# 1. Leitura dos arquivos gerados pela simulação
# ------------------------------------------------------------
print("📊 Lendo dados da simulação...")

if not os.path.exists("dados_simulacao.csv") or not os.path.exists("dados_aprendizado.csv"):
    print("⚠️ Arquivos de dados não encontrados! Execute primeiro o app.py por 15 dias.")
    exit()

df_sim = pd.read_csv("dados_simulacao.csv")
df_ml = pd.read_csv("dados_aprendizado.csv")

print(f"✅ Dados carregados: {len(df_sim)} passos simulados e {len(df_ml)} registros ML.")

# ------------------------------------------------------------
# 2. Gráfico de propagação da dengue (simulado x real)
# ------------------------------------------------------------
plt.figure()
plt.plot(df_sim["Passo"], df_sim["Infectados"], label="Simulado (ABM)", color="red")
plt.plot(df_sim["Passo"], df_sim["CasosReais"], label="Reais (API / Simulação)", color="blue", linestyle="--")
plt.title("📈 Propagação da Dengue – Casos Simulados vs Reais")
plt.xlabel("Dias (Passos da Simulação)")
plt.ylabel("Número de Casos")
plt.legend()
plt.savefig("grafico_casos_abm_vs_reais.png", dpi=300)
plt.show()

# ------------------------------------------------------------
# 3. Gráfico de variáveis climáticas
# ------------------------------------------------------------
plt.figure()
plt.plot(df_sim["Passo"], df_sim["TempAmbiente"], label="Temperatura (°C)", color="orange")
plt.plot(df_sim["Passo"], df_sim["UmidAmbiente"], label="Umidade (%)", color="cyan")
plt.plot(df_sim["Passo"], df_sim["CasosReais"], label="Casos Reais", color="purple", linestyle="--")
plt.title("🌦️ Clima e Casos de Dengue")
plt.xlabel("Dias Simulados")
plt.ylabel("Valores")
plt.legend()
plt.savefig("grafico_clima_casos.png", dpi=300)
plt.show()

# ------------------------------------------------------------
# 4. Gráfico de aprendizado de máquina (predição vs real)
# ------------------------------------------------------------
if "predito" in df_ml.columns:
    plt.figure()
    plt.plot(df_ml["dia"], df_ml["casos_reais"], label="Casos Reais", color="blue")
    plt.plot(df_ml["dia"], df_ml["predito"], label="Previsto (Random Forest)", color="green", linestyle="--")
    plt.title("🧠 Predição do ML vs Casos Reais")
    plt.xlabel("Dia")
    plt.ylabel("Casos de Dengue")
    plt.legend()
    plt.savefig("grafico_predicao_ml.png", dpi=300)
    plt.show()

    # Erro médio
    erro = abs(df_ml["casos_reais"] - df_ml["predito"]).mean()
    print(f"📉 Erro médio das predições: {erro:.2f} casos")

# ------------------------------------------------------------
# 5. Correlação entre clima e casos
# ------------------------------------------------------------
corr = df_sim[["TempAmbiente", "UmidAmbiente", "CasosReais"]].corr()
plt.figure()
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("🔍 Correlação entre Clima e Casos de Dengue")
plt.savefig("heatmap_correlacao.png", dpi=300)
plt.show()

# ------------------------------------------------------------
# 6. Exportação resumida
# ------------------------------------------------------------
resumo = {
    "Máx Infectados": df_sim["Infectados"].max(),
    "Média Casos Reais": df_sim["CasosReais"].mean(),
    "Taxa Média Infecção": df_ml["taxa_ajustada"].mean() if "taxa_ajustada" in df_ml else "N/A",
}
resumo_df = pd.DataFrame([resumo])
resumo_df.to_csv("resumo_resultados.csv", index=False)

print("\n✅ Análise concluída com sucesso!")
print("📁 Gráficos gerados:")
print(" - grafico_casos_abm_vs_reais.png")
print(" - grafico_clima_casos.png")
print(" - grafico_predicao_ml.png")
print(" - heatmap_correlacao.png")
print("💾 Resumo salvo em resumo_resultados.csv")
