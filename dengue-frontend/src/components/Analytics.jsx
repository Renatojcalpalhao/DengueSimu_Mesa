// src/components/Analytics.jsx - VERSÃO COMPLETA ATUALIZADA
import React, { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';
import './Analytics.css';

Chart.register(...registerables);

const Analytics = () => {
  const casesChartRef = useRef(null);
  const regionChartRef = useRef(null);
  const ageChartRef = useRef(null);
  const contaminationChartRef = useRef(null);

  useEffect(() => {
    // Gráfico de tendência temporal
    const casesCtx = casesChartRef.current.getContext('2d');
    const casesChart = new Chart(casesCtx, {
      type: 'line',
      data: {
        labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
        datasets: [
          {
            label: 'Casos Confirmados',
            data: [420, 380, 350, 320],
            borderColor: '#3498db',
            backgroundColor: 'rgba(52, 152, 219, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          },
          {
            label: 'Casos Suspeitos',
            data: [280, 250, 220, 200],
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        }
      }
    });

    // Gráfico de distribuição por região
    const regionCtx = regionChartRef.current.getContext('2d');
    const regionChart = new Chart(regionCtx, {
      type: 'doughnut',
      data: {
        labels: ['Centro', 'Norte', 'Sul', 'Leste', 'Oeste'],
        datasets: [{
          data: [35, 25, 20, 12, 8],
          backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } },
        cutout: '70%'
      }
    });

    // Gráfico de taxas por idade
    const ageCtx = ageChartRef.current.getContext('2d');
    const ageChart = new Chart(ageCtx, {
      type: 'bar',
      data: {
        labels: ['0-14', '15-24', '25-44', '45-64', '65+'],
        datasets: [{
          label: 'Taxa de Incidência (%)',
          data: [8.2, 12.5, 15.3, 10.1, 6.4],
          backgroundColor: '#3498db',
          borderColor: '#2980b9',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } }
      }
    });

    // NOVO GRÁFICO: Contaminação vs Tempo (3 MESES)
    const contaminationCtx = contaminationChartRef.current.getContext('2d');
    const contaminationChart = new Chart(contaminationCtx, {
      type: 'line',
      data: {
        labels: [
          'Jan W1', 'Jan W2', 'Jan W3', 'Jan W4',
          'Fev W1', 'Fev W2', 'Fev W3', 'Fev W4', 
          'Mar W1', 'Mar W2', 'Mar W3', 'Mar W4'
        ],
        datasets: [
          {
            label: 'Pessoas Contaminadas',
            data: [15, 42, 85, 120, 185, 240, 320, 410, 520, 630, 750, 890],
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
          },
          {
            label: 'Taxa de Crescimento (%)',
            data: [0, 180, 102, 41, 54, 30, 33, 28, 27, 21, 19, 19],
            borderColor: '#f39c12',
            backgroundColor: 'rgba(243, 156, 18, 0.1)',
            borderWidth: 2,
            fill: false,
            tension: 0.4,
            yAxisID: 'y1'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { 
            mode: 'index', 
            intersect: false,
            callbacks: {
              label: function(context) {
                let label = context.dataset.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed.y !== null) {
                  if (context.dataset.label === 'Taxa de Crescimento (%)') {
                    label += context.parsed.y + '%';
                  } else {
                    label += context.parsed.y + ' pessoas';
                  }
                }
                return label;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Número de Pessoas'
            }
          },
          y1: {
            beginAtZero: true,
            position: 'right',
            title: {
              display: true,
              text: 'Taxa de Crescimento (%)'
            },
            grid: {
              drawOnChartArea: false
            }
          }
        }
      }
    });

    return () => {
      casesChart.destroy();
      regionChart.destroy();
      ageChart.destroy();
      contaminationChart.destroy();
    };
  }, []);

  return (
    <div className="analytics">
      <div className="analytics-header">
        <h2>Análise Avançada - Dengue Analytics</h2>
        <div className="analytics-controls">
          <div className="control-group">
            <label htmlFor="time-period">Período:</label>
            <select id="time-period" className="time-selector">
              <option value="last-week">Última Semana</option>
              <option value="last-month">Último Mês</option>
              <option value="last-quarter">Último Trimestre</option>
              <option value="last-year">Último Ano</option>
            </select>
          </div>
          <div className="control-group">
            <label htmlFor="metric">Métrica:</label>
            <select id="metric" className="metric-selector">
              <option value="cases">Casos</option>
              <option value="recovered">Recuperados</option>
              <option value="mosquitoes">Mosquitos</option>
              <option value="rate">Taxa</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="kpi-cards">
        <div className="kpi-card critical">
          <div className="kpi-icon">⚠️</div>
          <div className="kpi-content">
            <div className="kpi-value">1.498</div>
            <div className="kpi-label">Casos Totais</div>
            <div className="kpi-trend negative">↓ 47%</div>
          </div>
        </div>
        
        <div className="kpi-card success">
          <div className="kpi-icon">✅</div>
          <div className="kpi-content">
            <div className="kpi-value">54</div>
            <div className="kpi-label">Recuperados</div>
            <div className="kpi-trend positive">↑ 5%</div>
          </div>
        </div>
        
        <div className="kpi-card info">
          <div className="kpi-icon">📊</div>
          <div className="kpi-content">
            <div className="kpi-value">12.3%</div>
            <div className="kpi-label">Taxa de Incidência</div>
            <div className="kpi-trend negative">↓ 3.2%</div>
          </div>
        </div>
      </div>
      
      <div className="analytics-grid">
        {/* NOVO GRÁFICO - Contaminação vs Tempo (3 MESES) */}
        <div className="chart-card full-width">
          <div className="chart-header">
            <h3>Evolução da Contaminação - Últimos 3 Meses</h3>
          </div>
          <div className="chart-container">
            <canvas ref={contaminationChartRef}></canvas>
          </div>
          <div className="chart-legend">
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#e74c3c'}}></div>
              <span>Pessoas Contaminadas</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#f39c12'}}></div>
              <span>Taxa de Crescimento (%)</span>
            </div>
          </div>
        </div>

        <div className="chart-card full-width">
          <div className="chart-header">
            <h3>Tendência Temporal - Casos</h3>
          </div>
          <div className="chart-container">
            <canvas ref={casesChartRef}></canvas>
          </div>
          <div className="chart-legend">
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#3498db'}}></div>
              <span>Casos Confirmados</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{backgroundColor: '#e74c3c'}}></div>
              <span>Casos Suspeitos</span>
            </div>
          </div>
        </div>
        
        <div className="chart-card">
          <div className="chart-header">
            <h3>Distribuição por Região</h3>
          </div>
          <div className="chart-container">
            <canvas ref={regionChartRef}></canvas>
          </div>
        </div>
        
        <div className="chart-card">
          <div className="chart-header">
            <h3>Taxas por Idade</h3>
          </div>
          <div className="chart-container">
            <canvas ref={ageChartRef}></canvas>
          </div>
        </div>
        
        <div className="insights-card">
          <h3>Insights e Recomendações</h3>
          <div className="insights-list">
            <div className="insight-item critical">
              <div className="insight-icon">⚠️</div>
              <div className="insight-content">
                <div className="insight-title">Aumento de casos na região Norte</div>
                <div className="insight-description">A região Norte apresentou um aumento de 18% nos casos confirmados na última semana. Recomenda-se intensificar as ações de prevenção nessa área.</div>
              </div>
            </div>
            <div className="insight-item success">
              <div className="insight-icon">✅</div>
              <div className="insight-content">
                <div className="insight-title">Eficácia das campanhas de conscientização</div>
                <div className="insight-description">As áreas com campanhas ativas de conscientização apresentaram 32% menos casos que as demais. Expandir essas ações para outras regiões.</div>
              </div>
            </div>
            <div className="insight-item warning">
              <div className="insight-icon">📈</div>
              <div className="insight-content">
                <div className="insight-title">Aumento na população de mosquitos</div>
                <div className="insight-description">Monitoramento indica aumento de 12% na população de Aedes aegypti. Intensificar ações de controle vetorial nas próximas semanas.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;