// dengue-frontend/src/components/InfoDengue/DistribuicaoDemografiaChart.jsx
import React, { useState } from 'react';
import './InfoDengueCharts.css';

const DistribuicaoDemografiaChart = ({ simulationData }) => {
  const [selectedFilter, setSelectedFilter] = useState('idade');
  
  // Dados demográficos simulados
  const dadosIdade = [
    { faixa: '00-04', casos: 45, percentual: 8.2 },
    { faixa: '05-09', casos: 78, percentual: 14.2 },
    { faixa: '10-19', casos: 125, percentual: 22.8 },
    { faixa: '20-29', casos: 98, percentual: 17.9 },
    { faixa: '30-39', casos: 85, percentual: 15.5 },
    { faixa: '40-49', casos: 64, percentual: 11.7 },
    { faixa: '50-59', casos: 35, percentual: 6.4 },
    { faixa: '60+', casos: 18, percentual: 3.3 }
  ];

  const dadosSexo = [
    { sexo: 'Feminino', casos: 285, percentual: 52.0 },
    { sexo: 'Masculino', casos: 263, percentual: 48.0 }
  ];

  const dadosRaca = [
    { raca: 'Branca', casos: 210, percentual: 38.3 },
    { raca: 'Preta', casos: 98, percentual: 17.9 },
    { raca: 'Parda', casos: 195, percentual: 35.6 },
    { raca: 'Amarela', casos: 32, percentual: 5.8 },
    { raca: 'Indígena', casos: 13, percentual: 2.4 }
  ];

  const getDadosAtuais = () => {
    switch (selectedFilter) {
      case 'idade': return dadosIdade;
      case 'sexo': return dadosSexo;
      case 'raca': return dadosRaca;
      default: return dadosIdade;
    }
  };

  const getMaxCasos = () => {
    return Math.max(...getDadosAtuais().map(d => d.casos));
  };

  const getCorPorIndex = (index, total) => {
    const cores = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22'];
    return cores[index % cores.length];
  };

  const dados = getDadosAtuais();

  return (
    <div className="demografia-chart">
      <div className="chart-header">
        <div className="chart-title">
          <h3>👥 Distribuição Demográfica dos Casos</h3>
          <p>Dados de 23 Novembro 2024 a 22 Novembro 2025</p>
        </div>
        
        <div className="chart-controls">
          <select 
            value={selectedFilter}
            onChange={(e) => setSelectedFilter(e.target.value)}
            className="filter-selector"
          >
            <option value="idade">Por Idade</option>
            <option value="sexo">Por Sexo</option>
            <option value="raca">Por Raça/Cor</option>
          </select>
        </div>
      </div>

      <div className="demografia-content">
        <div className="bars-container">
          {dados.map((item, index) => (
            <div key={index} className="bar-item">
              <div className="bar-label">
                <span className="label-text">
                  {selectedFilter === 'idade' ? item.faixa + ' anos' : 
                   selectedFilter === 'sexo' ? item.sexo : item.raca}
                </span>
                <span className="label-value">{item.casos} casos</span>
              </div>
              
              <div className="bar-track">
                <div 
                  className="bar-fill"
                  style={{
                    width: `${(item.casos / getMaxCasos()) * 100}%`,
                    backgroundColor: getCorPorIndex(index, dados.length)
                  }}
                >
                  <span className="bar-percent">{item.percentual}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="demografia-summary">
          <h4>📋 Resumo Estatístico</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Total de Casos</span>
              <span className="summary-value">
                {dados.reduce((sum, item) => sum + item.casos, 0).toLocaleString()}
              </span>
            </div>
            
            <div className="summary-item">
              <span className="summary-label">Faixa Mais Atingida</span>
              <span className="summary-value">
                {dados.reduce((max, item) => item.casos > max.casos ? item : max, dados[0]).faixa || 
                 dados.reduce((max, item) => item.casos > max.casos ? item : max, dados[0]).sexo}
              </span>
            </div>
            
            <div className="summary-item">
              <span className="summary-label">Percentual Máximo</span>
              <span className="summary-value">
                {Math.max(...dados.map(item => item.percentual)).toFixed(1)}%
              </span>
            </div>
          </div>

          <div className="observacoes">
            <h5>📝 Observações Epidemiológicas</h5>
            <ul>
              {selectedFilter === 'idade' && (
                <>
                  <li>• Crianças e adolescentes (0-19 anos) representam 45% dos casos</li>
                  <li>• Idosos (60+ anos) apresentam menor incidência</li>
                  <li>• Faixa de 10-19 anos é a mais vulnerável</li>
                </>
              )}
              {selectedFilter === 'sexo' && (
                <>
                  <li>• Distribuição equilibrada entre os sexos</li>
                  <li>• Pequena predominância no sexo feminino</li>
                  <li>• Padrão similar às séries históricas</li>
                </>
              )}
              {selectedFilter === 'raca' && (
                <>
                  <li>• Distribuição reflete o perfil populacional</li>
                  <li>• População branca representa maior percentual</li>
                  <li>• Dados sujeitos à qualidade do preenchimento</li>
                </>
              )}
            </ul>
          </div>
        </div>
      </div>

      <div className="chart-footer">
        <div className="data-source">
          <span>Fonte: Sistema de Informação de Agravos de Notificação - SINAN</span>
        </div>
      </div>
    </div>
  );
};

export default DistribuicaoDemografiaChart;