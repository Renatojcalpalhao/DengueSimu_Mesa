# ============================================================
#  Comparativo ABM x ABM+ML na Simulação da Dengue
#  Autor: Renato Jorge Correia Alpalhão
#  Projeto de Conclusão de Curso - SENAC
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import os

# ============================================================
# 1. Carregar dados dos dois modelos
# ============================================================

print("🔍 Carregando dados para comparação...")

# Arquivo gerado pela simulação ABM pura (do analysis.py)
arq_abm = "dados_simulacao.csv"

# Arquivo gerado pela simulação híbrida (ABM + ML)
arq_ml = "dados_aprendizado.csv"

if not os.path.exists(arq_abm):
    print("❌ Arquivo 'dados_simulacao.csv' não encontrado. Execute 'app.py' primeiro.")
    exit()

if not os.path.exists(arq_ml):
    print("⚠️ Arquivo 'dados_aprendizado.csv' não encontrado. Execute o modelo ML primeiro.")
    exit()

df_abm = pd.read_csv(arq_abm)
df_ml = pd.read_csv(arq_ml)

print(f"✅ {len(df_abm)} passos de simulação carregados.")
print(f"✅ {len(df_ml)} registros de aprendizado (ML) carregados.")

# ============================================================
# 2. Gráfico 1 - Comparativo de Casos Infectados (ABM puro x ML)
# ============================================================

plt.figure(figsize=(10, 6))
plt.plot(df_abm["Passo"], df_abm["Infectados"], color="red", label="ABM - Infectados (Simulado)")
plt.plot(df_ml["step"], df_ml["predicao"], color="orange", linestyle="--", label="ABM + ML - Predição")

plt.title("Comparativo: Modelo ABM Puro x ABM + Machine Learning", fontsize=14)
plt.xlabel("Passos de Simulação (Dias)")
plt.ylabel("Número de Casos Estimados")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("comparativo_infectados.png")
plt.close()
print("📊 Gráfico 1 salvo como 'comparativo_infectados.png'")

# ============================================================
# 3. Gráfico 2 - Taxa de Infecção Ajustada pelo ML
# ============================================================

plt.figure(figsize=(10, 6))
plt.plot(df_ml["step"], df_ml["taxa_infeccao"], color="blue", label="Taxa de Infecção Ajustada (ML)")
plt.title("Taxa de Infecção Ajustada Dinamicamente pelo ML", fontsize=14)
plt.xlabel("Passos de Simulação (Dias)")
plt.ylabel("Taxa de Infecção (0–1)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("comparativo_taxa_infeccao.png")
plt.close()
print("📊 Gráfico 2 salvo como 'comparativo_taxa_infeccao.png'")

# ============================================================
# 4. Gráfico 3 - Casos Reais x Preditos
# ============================================================

plt.figure(figsize=(10, 6))
plt.plot(df_ml["step"], df_ml["casos_reais"], color="purple", label="Casos Reais (API)")
plt.plot(df_ml["step"], df_ml["predicao"], color="red", linestyle="--", label="Casos Preditos (ML)")
plt.title("Casos Reais x Preditos pelo Modelo ABM + ML", fontsize=14)
plt.xlabel("Passos de Simulação (Dias)")
plt.ylabel("Casos de Dengue (Unidades)")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("comparativo_reais_preditos.png")
plt.close()
print("📊 Gráfico 3 salvo como 'comparativo_reais_preditos.png'")

# ============================================================
# 5. Resumo Numérico
# ============================================================

erro_medio = abs(df_ml["predicao"] - df_ml["casos_reais"]).mean()
print("\n📘 RESUMO FINAL")
print("-" * 50)
print(f"📅 Dias simulados: {df_abm['Passo'].max()}")
print(f"🧍 Infectados finais (ABM puro): {df_abm['Infectados'].iloc[-1]}")
print(f"🤖 Erro médio de predição (ABM + ML): {erro_medio:.2f} casos")
print("💾 Gráficos comparativos salvos na raiz do projeto.")
print("-" * 50)
