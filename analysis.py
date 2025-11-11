# Arquivo: analysis.py

import pandas as pd
import matplotlib.pyplot as plt

def plot_cenario(model_data_frame, nome_cenario):
    """
    Gera e salva o gráfico de casos infectados e reais.
    """
    plt.figure(figsize=(10, 6))
    
    # Gráfico de Casos Simulados vs. Casos Reais
    model_data_frame['Infectados'].plot(label='Simulado')
    model_data_frame['CasosReais'].plot(label='Real (API)', linestyle='--')
    
    plt.title(f'Propagação da Dengue: Cenário - {nome_cenario}')
    plt.xlabel('Passo (Dias)')
    plt.ylabel('Número de Casos')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'results_{nome_cenario}.png')
    plt.show()

# --- BLOCO PRINCIPAL PARA RODAR A SIMULAÇÃO ---
if __name__ == '__main__':
    from dengue_model import DengueModel
    
    # 1. Simulação do Cenário Base (Sem intervenção)
    model_base = DengueModel(num_humanos=200, num_mosquitos=300)
    for i in range(100):
        model_base.step()
    
    df_base = model_base.datacollector.get_model_vars_dataframe()
    plot_cenario(df_base, "Base_Sem_Vacina")
    
    # 2. Simulação do Cenário de Intervenção (Vacinação)
    model_vacina = DengueModel(num_humanos=200, num_mosquitos=300)
    # Aqui, você precisaria adicionar a lógica de vacinação no loop:
    # if i == 50: aplicar_vacinacao(model_vacina, porcentagem_alvo=0.3)
    
    # ... e rodar o modelo novamente para análise ...