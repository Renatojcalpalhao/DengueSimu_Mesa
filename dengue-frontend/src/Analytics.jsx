// src/components/Analytics.jsx
import React, { useState, useEffect, useRef } from 'react';
import './Analytics.css';

const Analytics = ({ simulationData }) => {
  const [timeRange, setTimeRange] = useState('month');
  const [selectedMetric, setSelectedMetric] = useState('cases');
  const canvasRef = useRef(null);

  // Dados históricos mais realistas
  const historicalData = {
    week: [
      { day: 'Seg', cases: 45, mosquitoes: 120, rate: 0.38, recovered: 12, interventions: 2 },
      { day: 'Ter', cases: 52, mosquitoes: 135, rate: 0.41, recovered: 15, interventions: 3 },
      { day: 'Qua', cases: 61, mosquitoes: 148, rate: 0.44, recovered: 18, interventions: 4 },
      { day: 'Qui', cases: 58, mosquitoes: 142, rate: 0.42, recovered: 20, interventions: 5 },
      { day: 'Sex', cases: 67, mosquitoes: 155, rate: 0.46, recovered: 22, interventions: 6 },
      { day: 'Sáb', cases: 72, mosquitoes: 168, rate: 0.48, recovered: 25, interventions: 7 },
      { day: 'Dom', cases: 68, mosquitoes: 160, rate: 0.47, recovered: 28, interventions: 8 }
    ],
    month: Array.from({ length: 30 }, (_, i) => ({
      day: i + 1,
      cases: Math.floor(40 + Math.sin(i * 0.3) * 20 + Math.random() * 15),
      mosquitoes: Math.floor(100 + Math.sin(i * 0.2) * 40 + Math.random() * 30),
      rate: 0.35 + Math.sin(i * 0.25) * 0.15 + Math.random() * 0.1,
      recovered: Math.floor(10 + i * 1.5 + Math.random() * 8),
      interventions: Math.floor(i / 5) + 1
    })),
    year: Array.from({ length: 12 }, (_, i) => ({
      month: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dec'][i],
      cases: Math.floor(600 + Math.sin(i * 0.8) * 300 + Math.random() * 200),
      mosquitoes: Math.floor(1500 + Math.sin(i * 0.7) * 800 + Math.random() * 400),
      rate: 0.25 + Math.sin(i * 0.6) * 0.2 + Math.random() * 0.15,
      recovered: Math.floor(200 + i * 80 + Math.random() * 100),
      interventions: Math.floor(3 + i * 1.2)
    }))
  };

  const currentData = historicalData[timeRange];

  // Calcular métricas avançadas
  const calculateMetrics = () => {
    const cases = currentData.map(d => d.cases);
    const mosquitoes = currentData.map(d => d.mosquitoes);
    const rates = currentData.map(d => d.rate);
    
    const totalCases = cases.reduce((a, b) => a + b, 0);
    const avgRate = rates.reduce((a, b) => a + b, 0) / rates.length;
    const peakCases = Math.max(...cases);
    const totalMosquitoes = mosquitoes.reduce((a, b) => a + b, 0);
    
    // Calcular tendência
    const firstHalf = cases.slice(0, Math.floor(cases.length / 2));
    const secondHalf = cases.slice(Math.floor(cases.length / 2));
    const trend = ((secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length) / 
                  (firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length) - 1) * 100;

    // Calcular R0 básico
    const r0 = avgRate * 1.8; // Simulação simplificada

    return {
      totalCases,
      avgRate,
      peakCases,
      totalMosquitoes,
      trend,
      r0
    };
  };

  const metrics = calculateMetrics();

  // Gráfico de Linhas Interativo
  const renderLineChart = (metricType) => {
    const data = currentData.map(d => 
      metricType === 'cases' ? d.cases : 
      metricType === 'mosquitoes' ? d.mosquitoes : 
      metricType === 'rate' ? d.rate * 100 : d.recovered
    );
    
    const maxValue = Math.max(...data);
    const minValue = Math.min(...data);

    return (
      <div className="line-chart">
        <div className="chart-grid">
          {/* Grades de fundo */}
          {[0, 25, 50, 75, 100].map(percent => (
            <div 
              key={percent}
              className="grid-line"
              style={{ bottom: `${percent}%` }}
            ></div>
          ))}
        </div>
        
        {/* Linha do gráfico */}
        <svg className="chart-line" viewBox={`0 0 ${currentData.length * 50} 100`}>
          <path
            d={data.map((value, index) => {
              const x = (index / (currentData.length - 1)) * 100;
              const y = 100 - ((value - minValue) / (maxValue - minValue)) * 100;
              return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
            }).join(' ')}
            fill="none"
            stroke={metricType === 'cases' ? '#e74c3c' : 
                   metricType === 'mosquitoes' ? '#3498db' : 
                   metricType === 'rate' ? '#9b59b6' : '#27ae60'}
            strokeWidth="3"
            strokeLinecap="round"
          />
          
          {/* Pontos interativos */}
          {data.map((value, index) => (
            <circle
              key={index}
              cx={(index / (currentData.length - 1)) * 100}
              cy={100 - ((value - minValue) / (maxValue - minValue)) * 100}
              r="4"
              fill={metricType === 'cases' ? '#e74c3c' : 
                    metricType === 'mosquitoes' ? '#3498db' : 
                    metricType === 'rate' ? '#9b59b6' : '#27ae60'}
              className="data-point"
              onMouseEnter={(e) => {
                e.target.style.r = '6';
                // Aqui poderia mostrar tooltip
              }}
              onMouseLeave={(e) => {
                e.target.style.r = '4';
              }}
            />
          ))}
        </svg>

        {/* Eixo X */}
        <div className="x-axis">
          {currentData.map((data, index) => (
            <div key={index} className="x-tick">
              {timeRange === 'year' ? data.month : 
               timeRange === 'month' ? data.day : data.day}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Gráfico de Barras Empilhadas
  const renderStackedBarChart = () => {
    const maxTotal = Math.max(...currentData.map(d => d.cases + d.recovered));

    return (
      <div className="stacked-bars-container">
        {currentData.map((data, index) => (
          <div key={index} className="bar-group-stacked">
            <div className="bar-stack">
              <div 
                className="bar recovered-bar"
                style={{ 
                  height: `${(data.recovered / maxTotal) * 100}%`,
                  backgroundColor: '#27ae60'
                }}
                title={`${data.recovered} recuperados`}
              ></div>
              <div 
                className="bar active-bar"
                style={{ 
                  height: `${(data.cases / maxTotal) * 100}%`,
                  backgroundColor: '#e74c3c'
                }}
                title={`${data.cases} casos ativos`}
              ></div>
            </div>
            <div className="bar-label">
              {timeRange === 'year' ? data.month : 
               timeRange === 'month' ? data.day : data.day}
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Gráfico de Correlação
  const renderCorrelationChart = () => {
    return (
      <div className="correlation-chart">
        {currentData.map((data, index) => (
          <div
            key={index}
            className="correlation-point"
            style={{
              left: `${(data.mosquitoes / Math.max(...currentData.map(d => d.mosquitoes))) * 90 + 5}%`,
              bottom: `${data.rate * 90 + 5}%`,
              backgroundColor: `rgba(231, 76, 60, ${0.3 + data.rate * 0.7})`,
              width: `${10 + data.cases / 10}px`,
              height: `${10 + data.cases / 10}px`
            }}
            title={`Mosquitos: ${data.mosquitoes}, Taxa: ${(data.rate * 100).toFixed(1)}%`}
          ></div>
        ))}
        <div className="correlation-axis x-axis">Número de Mosquitos →</div>
        <div className="correlation-axis y-axis">↑ Taxa de Infecção</div>
      </div>
    );
  };

  return (
    <div className="analytics">
      <div className="analytics-header">
        <h2>📊 Analytics Avançado - Dengue Analytics</h2>
        <div className="analytics-controls">
          <div className="control-group">
            <label>Período:</label>
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
          <div className="control-group">
            <label>Métrica:</label>
            <select 
              value={selectedMetric} 
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="metric-selector"
            >
              <option value="cases">Casos</option>
              <option value="mosquitoes">Mosquitos</option>
              <option value="rate">Taxa de Infecção</option>
              <option value="recovered">Recuperados</option>
            </select>
          </div>
        </div>
      </div>

      <div className="analytics-grid">
        {/* Kart de Métricas Principais */}
        <div className="kpi-cards">
          <div className="kpi-card critical">
            <div className="kpi-icon">🦠</div>
            <div className="kpi-content">
              <div className="kpi-value">{metrics.totalCases.toLocaleString()}</div>
              <div className="kpi-label">Casos Totais</div>
              <div className={`kpi-trend ${metrics.trend > 0 ? 'positive' : 'negative'}`}>
                {metrics.trend > 0 ? '↗' : '↘'} {Math.abs(metrics.trend).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="kpi-card warning">
            <div className="kpi-icon">📈</div>
            <div className="kpi-content">
              <div className="kpi-value">{metrics.avgRate.toFixed(3)}</div>
              <div className="kpi-label">R₀ Estimado</div>
              <div className="kpi-subtitle">Taxa de Reprodução</div>
            </div>
          </div>

          <div className="kpi-card info">
            <div className="kpi-icon">🦟</div>
            <div className="kpi-content">
              <div className="kpi-value">{metrics.totalMosquitoes.toLocaleString()}</div>
              <div className="kpi-label">Focos de Mosquitos</div>
              <div className="kpi-trend positive">↗ 15% esta semana</div>
            </div>
          </div>

          <div className="kpi-card success">
            <div className="kpi-icon">✅</div>
            <div className="kpi-content">
              <div className="kpi-value">{currentData[currentData.length - 1]?.recovered || 0}</div>
              <div className="kpi-label">Recuperados</div>
              <div className="kpi-trend positive">↗ 8% esta semana</div>
            </div>
          </div>
        </div>

        {/* Gráfico de Linhas Interativo */}
        <div className="chart-card full-width">
          <div className="chart-header">
            <h3>Tendência Temporal - {selectedMetric === 'cases' ? 'Casos' : 
                                    selectedMetric === 'mosquitoes' ? 'Mosquitos' : 
                                    selectedMetric === 'rate' ? 'Taxa de Infecção' : 'Recuperados'}</h3>
            <div className="chart-legend">
              <div className="legend-item" style={{ color: '#e74c3c' }}>● Casos</div>
              <div className="legend-item" style={{ color: '#3498db' }}>● Mosquitos</div>
              <div className="legend-item" style={{ color: '#9b59b6' }}>● Taxa</div>
            </div>
          </div>
          {renderLineChart(selectedMetric)}
        </div>

        {/* Gráficos Secundários */}
        <div className="chart-card">
          <h3>Casos Ativos vs Recuperados</h3>
          {renderStackedBarChart()}
          <div className="chart-legend">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#e74c3c' }}></div>
              <span>Ativos</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#27ae60' }}></div>
              <span>Recuperados</span>
            </div>
          </div>
        </div>

        <div className="chart-card">
          <h3>Correlação: Mosquitos × Infecção</h3>
          {renderCorrelationChart()}
          <div className="chart-note">
            Tamanho do ponto = Número de casos
          </div>
        </div>

        {/* Previsões e Insights */}
        <div className="insights-card">
          <h3>🔮 Insights e Previsões</h3>
          <div className="insights-list">
            <div className="insight-item critical">
              <div className="insight-icon">⚠️</div>
              <div className="insight-content">
                <div className="insight-title">Alerta: Zona Sul</div>
                <div className="insight-description">
                  Previsão de 45% aumento de casos na próxima semana
                </div>
              </div>
            </div>
            <div className="insight-item warning">
              <div className="insight-icon">📊</div>
              <div className="insight-content">
                <div className="insight-title">Correlação Forte</div>
                <div className="insight-description">
                  R² = 0.87 entre focos de mosquitos e novos casos
                </div>
              </div>
            </div>
            <div className="insight-item success">
              <div className="insight-icon">✅</div>
              <div className="insight-content">
                <div className="insight-title">Intervenção Eficaz</div>
                <div className="insight-description">
                  Pulverização reduziu casos em 32% nas áreas tratadas
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Métricas de Eficiência */}
        <div className="metrics-card">
          <h3>📋 Eficiência das Intervenções</h3>
          <div className="efficiency-metrics">
            <div className="efficiency-item">
              <div className="efficiency-bar">
                <div 
                  className="efficiency-fill" 
                  style={{ width: '78%', backgroundColor: '#27ae60' }}
                ></div>
              </div>
              <div className="efficiency-label">
                <span>Pulverização</span>
                <span>78% eficaz</span>
              </div>
            </div>
            <div className="efficiency-item">
              <div className="efficiency-bar">
                <div 
                  className="efficiency-fill" 
                  style={{ width: '65%', backgroundColor: '#3498db' }}
                ></div>
              </div>
              <div className="efficiency-label">
                <span>Educação</span>
                <span>65% eficaz</span>
              </div>
            </div>
            <div className="efficiency-item">
              <div className="efficiency-bar">
                <div 
                  className="efficiency-fill" 
                  style={{ width: '82%', backgroundColor: '#9b59b6' }}
                ></div>
              </div>
              <div className="efficiency-label">
                <span>Fiscalização</span>
                <span>82% eficaz</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;