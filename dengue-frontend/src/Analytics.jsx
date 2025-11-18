// src/components/Analytics.jsx
import React, { useState, useEffect, useRef } from 'react';
import './Analytics.css';

const Analytics = ({ simulationData }) => {
  const [timeRange, setTimeRange] = useState('month');
  const chartRef = useRef(null);

  // Dados históricos simulados
  const historicalData = {
    week: [
      { day: 'Seg', cases: 45, mosquitoes: 120, rate: 0.4 },
      { day: 'Ter', cases: 52, mosquitoes: 135, rate: 0.42 },
      { day: 'Qua', cases: 61, mosquitoes: 148, rate: 0.45 },
      { day: 'Qui', cases: 58, mosquitoes: 142, rate: 0.43 },
      { day: 'Sex', cases: 67, mosquitoes: 155, rate: 0.47 },
      { day: 'Sáb', cases: 72, mosquitoes: 168, rate: 0.49 },
      { day: 'Dom', cases: 68, mosquitoes: 160, rate: 0.48 }
    ],
    month: Array.from({ length: 30 }, (_, i) => ({
      day: `Dia ${i + 1}`,
      cases: Math.floor(40 + Math.random() * 40),
      mosquitoes: Math.floor(100 + Math.random() * 80),
      rate: 0.3 + Math.random() * 0.3
    })),
    year: Array.from({ length: 12 }, (_, i) => ({
      month: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dec'][i],
      cases: Math.floor(800 + Math.random() * 600),
      mosquitoes: Math.floor(2000 + Math.random() * 1500),
      rate: 0.2 + Math.random() * 0.4
    }))
  };

  const currentData = historicalData[timeRange];

  return (
    <div className="analytics">
      <div className="analytics-header">
        <h2>📈 Analytics e Tendências</h2>
        <div className="analytics-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-selector"
          >
            <option value="week">Última Semana</option>
            <option value="month">Último Mês</option>
            <option value="year">Último Ano</option>
          </select>
        </div>
      </div>

      <div className="analytics-grid">
        <div className="chart-card">
          <h3>Evolução de Casos</h3>
          <div className="chart-container">
            <div className="bars-container">
              {currentData.map((data, index) => (
                <div key={index} className="bar-group">
                  <div 
                    className="bar cases-bar" 
                    style={{ height: `${(data.cases / Math.max(...currentData.map(d => d.cases))) * 100}%` }}
                    title={`${data.cases} casos`}
                  ></div>
                  <div className="bar-label">{timeRange === 'year' ? data.month : data.day}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="chart-card">
          <h3>Mosquitos vs Taxa de Infecção</h3>
          <div className="chart-container">
            <div className="lines-container">
              {currentData.map((data, index) => (
                <div key={index} className="data-point">
                  <div 
                    className="point mosquitoes-point"
                    style={{ 
                      bottom: `${(data.mosquitoes / Math.max(...currentData.map(d => d.mosquitoes))) * 100}%`,
                      left: `${(index / (currentData.length - 1)) * 100}%`
                    }}
                  ></div>
                  <div 
                    className="point rate-point"
                    style={{ 
                      bottom: `${data.rate * 100}%`,
                      left: `${(index / (currentData.length - 1)) * 100}%`
                    }}
                  ></div>
                </div>
              ))}
            </div>
            <div className="chart-legend">
              <div className="legend-item">
                <div className="legend-color mosquitoes"></div>
                <span>Mosquitos</span>
              </div>
              <div className="legend-item">
                <div className="legend-color rate"></div>
                <span>Taxa de Infecção</span>
              </div>
            </div>
          </div>
        </div>

        <div className="metrics-card">
          <h3>Métricas Principais</h3>
          <div className="metrics-grid">
            <div className="metric">
              <div className="metric-value">
                {currentData.reduce((sum, data) => sum + data.cases, 0).toLocaleString()}
              </div>
              <div className="metric-label">Total de Casos</div>
              <div className="metric-trend positive">+12% vs período anterior</div>
            </div>
            <div className="metric">
              <div className="metric-value">
                {(currentData.reduce((sum, data) => sum + data.rate, 0) / currentData.length).toFixed(2)}
              </div>
              <div className="metric-label">Taxa Média</div>
              <div className="metric-trend positive">+0.08 vs período anterior</div>
            </div>
            <div className="metric">
              <div className="metric-value">
                {Math.max(...currentData.map(d => d.cases)).toLocaleString()}
              </div>
              <div className="metric-label">Pico de Casos</div>
              <div className="metric-trend negative">Registro mais alto</div>
            </div>
            <div className="metric">
              <div className="metric-value">
                {currentData.reduce((sum, data) => sum + data.mosquitoes, 0).toLocaleString()}
              </div>
              <div className="metric-label">Focos de Mosquitos</div>
              <div className="metric-trend positive">+8% vs período anterior</div>
            </div>
          </div>
        </div>

        <div className="predictions-card">
          <h3>Previsões para Próxima Semana</h3>
          <div className="prediction-list">
            <div className="prediction-item">
              <div className="prediction-metric">Novos Casos</div>
              <div className="prediction-value">285-320</div>
              <div className="prediction-confidence">85% confiança</div>
            </div>
            <div className="prediction-item">
              <div className="prediction-metric">Áreas de Risco</div>
              <div className="prediction-value">Zona Sul, Centro</div>
              <div className="prediction-confidence">Alerta máximo</div>
            </div>
            <div className="prediction-item">
              <div className="prediction-metric">Intervenção Recomendada</div>
              <div className="prediction-value">Pulverização urgente</div>
              <div className="prediction-confidence">Prioridade alta</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;