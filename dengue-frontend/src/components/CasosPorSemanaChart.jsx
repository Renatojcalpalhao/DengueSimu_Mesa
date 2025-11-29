// dengue-frontend/src/components/InfoDengue/CasosPorSemanaChart.jsx
import React, { useState, useEffect } from 'react';
import './InfoDengueCharts.css';

const CasosPorSemanaChart = ({ simulationData, apiData }) => {
  const [selectedDisease, setSelectedDisease] = useState('dengue');
  const [timeRange, setTimeRange] = useState('1year');
  
  // Dados históricos simulados no estilo InfoDengue
  const [historicalData, setHistoricalData] = useState([]);

  useEffect(() => {
    // Gerar dados históricos realistas baseados na simulação
    const generateHistoricalData = () => {
      const baseCases = simulationData?.humans || 50;
      const weeks = [];
      
      // Últimas 52 semanas
      for (let i = 52; i >= 1; i--) {
        const weekNumber = 202547 - i; // Semana epidemiológica
        const variation = 0.7 + Math.random() * 0.6;
        const seasonFactor = 0.5 + Math.sin((i / 52) * Math.PI * 2) * 0.5;
        
        const cases = Math.floor(
          baseCases * variation * seasonFactor * (1 + (52 - i) / 100)
        );

        weeks.push({
          semana: weekNumber,
          casos: cases,
          tendencia: Math.random() > 0.7 ? 'alta' : Math.random() > 0.5 ? 'estavel' : 'baixa'
        });
      }
      
      // Adicionar pico epidêmico recente (como nos dados reais)
      if (weeks.length > 4) {
        weeks[weeks.length - 1].casos = Math.floor(baseCases * 3.5); // Pico
        weeks[weeks.length - 1].tendencia = 'alta';
      }
      
      return weeks;
    };

    setHistoricalData(generateHistoricalData());
  }, [simulationData]);

  const getMaxCases = () => {
    return Math.max(...historicalData.map(d => d.casos), 1000);
  };

  const getWeekLabel = (weekNumber) => {
    const year = Math.floor(weekNumber / 100);
    const week = weekNumber % 100;
    return `SE ${week}/${year}`;
  };

  const getTendenciaIcon = (tendencia) => {
    switch(tendencia) {
      case 'alta': return '📈';
      case 'baixa': return '📉';
      default: return '➡️';
    }
  };

  const getTendenciaColor = (tendencia) => {
    switch(tendencia) {
      case 'alta': return '#e74c3c';
      case 'baixa': return '#27ae60';
      default: return '#f39c12';
    }
  };

  return (
    <div className="info-dengue-chart">
      <div className="chart-header">
        <div className="chart-title">
          <h3>📊 Casos por Semana Epidemiológica</h3>
          <p>Dados de 23 Novembro 2024 a 22 Novembro 2025</p>
        </div>
        
        <div className="chart-controls">
          <select 
            value={selectedDisease}
            onChange={(e) => setSelectedDisease(e.target.value)}
            className="disease-selector"
          >
            <option value="dengue">Dengue</option>
            <option value="chikungunya">Chikungunya</option>
          </select>
          
          <select 
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-selector"
          >
            <option value="3months">3 meses</option>
            <option value="6months">6 meses</option>
            <option value="1year">1 ano</option>
          </select>
        </div>
      </div>

      <div className="chart-container">
        <div className="cases-chart">
          <div className="chart-y-axis">
            <div className="y-label">Casos</div>
            <div className="y-scale">
              <span>{getMaxCases().toLocaleString()}</span>
              <span>{Math.floor(getMaxCases() * 0.75).toLocaleString()}</span>
              <span>{Math.floor(getMaxCases() * 0.5).toLocaleString()}</span>
              <span>{Math.floor(getMaxCases() * 0.25).toLocaleString()}</span>
              <span>0</span>
            </div>
          </div>
          
          <div className="chart-bars">
            {historicalData.slice(-24).map((week, index) => (
              <div key={week.semana} className="bar-container">
                <div 
                  className="case-bar"
                  style={{
                    height: `${(week.casos / getMaxCases()) * 100}%`,
                    backgroundColor: getTendenciaColor(week.tendencia)
                  }}
                  title={`${getWeekLabel(week.semana)}: ${week.casos} casos`}
                >
                  <div className="bar-value">{week.casos}</div>
                </div>
                <div className="week-label">
                  {index % 4 === 0 ? getWeekLabel(week.semana) : ''}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="chart-footer">
        <div className="current-stats">
          <div className="stat-item">
            <span className="stat-label">Casos na última semana:</span>
            <span className="stat-value">
              {historicalData.length > 0 ? historicalData[historicalData.length - 1].casos : 0}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Tendência:</span>
            <span 
              className="stat-value"
              style={{ color: getTendenciaColor(historicalData.length > 0 ? historicalData[historicalData.length - 1].tendencia : 'estavel') }}
            >
              {historicalData.length > 0 ? getTendenciaIcon(historicalData[historicalData.length - 1].tendencia) : '➡️'} 
              {historicalData.length > 0 ? 
                (historicalData[historicalData.length - 1].tendencia === 'alta' ? ' Em alta' : 
                 historicalData[historicalData.length - 1].tendencia === 'baixa' ? ' Em baixa' : ' Estável') : 
                ' Estável'}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total do período:</span>
            <span className="stat-value">
              {historicalData.reduce((sum, week) => sum + week.casos, 0).toLocaleString()} casos
            </span>
          </div>
        </div>
        
        <div className="chart-legend">
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#e74c3c' }}></div>
            <span>Em alta</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#f39c12' }}></div>
            <span>Estável</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{ backgroundColor: '#27ae60' }}></div>
            <span>Em baixa</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CasosPorSemanaChart;