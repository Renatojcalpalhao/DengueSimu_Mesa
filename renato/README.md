# 🦟 Sistema de Monitoramento de Dengue

Sistema completo de simulação e monitoramento da dengue em tempo real, desenvolvido em React com Vite. Simula a propagação da dengue com métricas realistas, visualização de agentes e análise de dados.

![Dashboard Preview](https://via.placeholder.com/800x400/3498db/ffffff?text=Dashboard+de+Simulação+Dengue)

## 🚀 Funcionalidades

### 📊 Painel Principal
- Métricas em tempo real da simulação
- Gráficos dinâmicos de evolução
- Controles de parâmetros da simulação
- Taxa de infecção em tempo real

### 🦠 Simulação de Agentes (Estilo NetLogo)
- Visualização interativa da propagação
- Humanos saudáveis vs infectados
- Mosquitos saudáveis vs infectados
- Transmissão realista entre agentes
- Controles de velocidade e interação

### 🗺️ Mapa de Calor de São Paulo
- Mapa interativo das regiões de SP
- Intensidade de casos por região
- Detalhes por região selecionada
- Dados históricos e em tempo real

### 📈 Analytics e Gráficos
- Evolução temporal dos casos
- Comparação mosquito vs taxa de infecção
- Métricas e previsões
- Tendências e padrões

### 📤 Exportação de Dados
- Exportação em CSV e JSON
- Dados históricos completos
- Pré-visualização antes do download
- Agendamento de exportações

### 💾 Banco de Dados Simulado
- Estatísticas de armazenamento
- Operações em tempo real
- Backup e otimização
- Estrutura de dados completa

## 🛠️ Tecnologias Utilizadas

- **Frontend**: React 18, Vite
- **Estilização**: CSS3 com Grid e Flexbox
- **Visualização**: Canvas API
- **Gráficos**: CSS Custom + Animations
- **Controle de Estado**: React Hooks

## 📦 Instalação e Execução

### Pré-requisitos
- Node.js 16+ 
- npm ou yarn

### Passos para executar



# Ou construa para produção
npm run build
npm run preview
```bash
# Clone o repositório
git clone https://github.com/SEU-USUARIO/dengue-frontend.git
cd dengue-frontend

# Instale as dependências
npm install

# Execute em modo de desenvolvimento
npm run dev

Acesso
Desenvolvimento: http://localhost:5173

Produção: (após build) http://localhost:4173

🎯 Como Usar a Simulação
1. Configuração Inicial
Ajuste a população total e casos iniciais

Defina a taxa de vacinação

Configure a temperatura ambiente

Ajuste a intensidade das intervenções

2. Controles da Simulação
Iniciar: Começa a simulação em tempo real

Parar: Pausa a simulação

Reiniciar: Reseta para valores iniciais

Velocidade: Controla a velocidade da simulação

3. Parâmetros Ajustáveis
Parâmetro	Descrição	Valores
População	Total de pessoas na simulação	1.000 - 100.000
Vacinação	% da população vacinada	0% - 100%
Transmissão	Probabilidade de infecção	1% - 100%
Temperatura	Fator ambiental crítico	15°C - 35°C
Recuperação	Taxa diária de recuperação	5% - 40%
📊 Métricas e Indicadores
Em Tempo Real
👥 Casos Ativos: Pessoas infectadas no momento

🛡️ População Imune: Recuperados + Vacinados

🦟 Mosquitos Infectados: Vetores ativos

📈 Taxa R₀: Número básico de reprodução

🌡️ Fatores Ambientais: Temperatura e sazonalidade

Tendências
📈 Aumentando: Novos casos > Recuperações

📉 Diminuindo: Recuperações > Novos casos

➡️ Estável: Equilíbrio entre casos e recuperações

🎮 Simulação de Agentes
Interatividade
Clique no mapa: Adiciona agentes infectados

Controle de velocidade: 0.1x a 3x

Reiniciar: Recria todos os agentes

Cores dos Agentes
🟢 Verde: Humanos saudáveis

🔴 Vermelho: Humanos infectados

🔵 Azul: Mosquitos saudáveis

🟠 Laranja: Mosquitos infectados

📈 Modelo Epidemiológico
Características Realistas
Recuperação: Pessoas se recuperam naturalmente

Imunidade Temporária: Proteção por período limitado

Reinfecção: Possibilidade após perda de imunidade

Variação Sazonal: Influência das estações

Efeito Intervenções: Redução através de controles

Fórmulas Principais
text
Novas Infecções = Mosquitos × Transmissão × Temperatura × Sazonalidade
Recuperações = Casos Ativos × Taxa Recuperação
População Suscetível = Total - Infectados - Imunes
🗂️ Estrutura do Projeto
text
dengue-frontend/
├── src/
│   ├── App.jsx                 # Aplicação principal
│   ├── App.css                 # Estilos globais
│   ├── main.jsx                # Entry point
│   ├── Dashboard.jsx           # Painel principal
│   ├── AgentVisualization.jsx  # Simulação de agentes
│   ├── MapView.jsx            # Mapa de calor
│   ├── Analytics.jsx          # Análises e gráficos
│   ├── DataExport.jsx         # Exportação de dados
│   └── Database.jsx           # Banco de dados simulado
├── public/
│   └── index.html
└── package.json
👥 Desenvolvimento
Scripts Disponíveis
bash
npm run dev          # Desenvolvimento
npm run build        # Build produção
npm run preview      # Preview build
npm run lint         # Análise de código
# Ou construa para produção
npm run build
npm run preview
