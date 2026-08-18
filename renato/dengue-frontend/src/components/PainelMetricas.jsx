// dengue-frontend/src/components/InfoDengue/PainelMetricas.jsx
import React from 'react';
import './InfoDengueCharts.css';

const PainelMetricas = ({ simulationData, apiData }) => {
  // Calcular métricas baseadas nos dados disponíveis
  const calcularMetricas = () => {
    const casosReais = apiData?.dengue?.casos_reais || simulationData?.humans * 10 || 0;
    const taxaAtaque = simulationData ? (simulationData.humans / simulationData.population * 100) : 2.5;
    const coberturaVacinal = simulationData ? (simulationData.vaccinated / simulationData.population * 100) : 30;
    const letalidade = 0.12; // Exemplo fixo
    
    return {
      casosConfirmados: casosReais,
      taxaAtaque: taxaAtaque,
      coberturaVacinal: coberturaVacinal,
      letalidade: letalidade,
      internacoes: Math.floor(casosReais * 0.15),
      obitos: Math.floor(casosReais * (letalidade / 100))
    };
  };

  const metricas = calcularMetricas();

  const getStatusColor = (valor, limites) => {
    if (valor >= limites.alto) return '#e74c3c';
    if (valor >= limites.medio) return '#f39c12';
    return '#27ae60';
  };

  const getStatusIcon = (valor, limites) => {
    if (valor >= limites.alto) return '🔴';
    if (valor >= limites.medio) return '🟡';
    return '🟢';
  };

  const cards = [
    {
      titulo: 'Casos Confirmados',
      valor: metricas.casosConfirmados.toLocaleString(),
      descricao: 'Total no período',
      variacao: '+12%',
      status: getStatusIcon(metricas.casosConfirmados, { medio: 1000, alto: 5000 }),
      cor: getStatusColor(metricas.casosConfirmados, { medio: 1000, alto: 5000 }),
      icon: '🦠'
    },
    {
      titulo: 'Taxa de Ataque',
      valor: `${metricas.taxaAtaque.toFixed(2)}%`,
      descricao: 'Da população',
      variacao: metricas.taxaAtaque > 3 ? '+5%' : '-2%',
      status: getStatusIcon(metricas.taxaAtaque, { medio: 2, alto: 5 }),
      cor: getStatusColor(metricas.taxaAtaque, { medio: 2, alto: 5 }),
      icon: '📈'
    },
    {
      titulo: 'Cobertura Vacinal',
      valor: `${metricas.coberturaVacinal.toFixed(1)}%`,
      descricao: 'População imunizada',
      variacao: '+8%',
      status: getStatusIcon(metricas.coberturaVacinal, { medio: 60, alto: 80 }),
      cor: getStatusColor(metricas.coberturaVacinal, { medio: 60, alto: 80 }),
      icon: '💉'
    },
    {
      titulo: 'Internações',
      valor: metricas.internacoes.toLocaleString(),
      descricao: 'Casos graves',
      variacao: '+7%',
      status: getStatusIcon(metricas.internacoes, { medio: 50, alto: 100 }),
      cor: getStatusColor(metricas.internacoes, { medio: 50, alto: 100 }),
      icon: '🏥'
    },
    {
      titulo: 'Óbitos Confirmados',
      valor: metricas.obitos,
      descricao: `Letalidade: ${metricas.letalidade}%`,
      variacao: '+3%',
      status: getStatusIcon(metricas.obitos, { medio: 10, alto: 20 }),
      cor: getStatusColor(metricas.obitos, { medio: 10, alto: 20 }),
      icon: '😔'
    },
    {
      titulo: 'Nível de Alerta',
      valor: apiData?.dengue?.alerta || 'Moderado',
      descricao: 'Situação epidemiológica',
      variacao: 'Estável',
      status: '🟡',
      cor: '#f39c12',
      icon: '⚠️'
    }
  ];

  return (
    <div className="painel-metricas">
      <div className="metricas-header">
        <h3>📊 Métricas Principais - Dengue SP</h3>
        <p>Dados consolidados do sistema de vigilância</p>
      </div>

      <div className="metricas-grid">
        {cards.map((card, index) => (
          <div key={index} className="metrica-card">
            <div className="metrica-header">
              <div className="metrica-icon">{card.icon}</div>
              <div className="metrica-status" style={{ color: card.cor }}>
                {card.status}
              </div>
            </div>
            
            <div className="metrica-content">
              <div className="metrica-valor" style={{ color: card.cor }}>
                {card.valor}
              </div>
              <div className="metrica-titulo">{card.titulo}</div>
              <div className="metrica-descricao">{card.descricao}</div>
            </div>

            <div className="metrica-footer">
              <span 
                className={`metrica-variacao ${
                  card.variacao.includes('+') ? 'positiva' : 
                  card.variacao.includes('-') ? 'negativa' : 'neutra'
                }`}
              >
                {card.variacao}
              </span>
              <span className="metrica-periodo">vs. última semana</span>
            </div>
          </div>
        ))}
      </div>

      <div className="metricas-legenda">
        <div className="legenda-item">
          <span className="legenda-indicador" style={{ backgroundColor: '#27ae60' }}></span>
          <span>Baixo Risco</span>
        </div>
        <div className="legenda-item">
          <span className="legenda-indicador" style={{ backgroundColor: '#f39c12' }}></span>
          <span>Médio Risco</span>
        </div>
        <div className="legenda-item">
          <span className="legenda-indicador" style={{ backgroundColor: '#e74c3c' }}></span>
          <span>Alto Risco</span>
        </div>
      </div>
    </div>
  );
};

export default PainelMetricas;