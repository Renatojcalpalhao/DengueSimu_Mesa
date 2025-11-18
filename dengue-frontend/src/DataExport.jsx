// src/components/DataExport.jsx
import React, { useState } from 'react';
import './DataExport.css';

const DataExport = ({ simulationData }) => {
  const [exportFormat, setExportFormat] = useState('csv');
  const [dateRange, setDateRange] = useState('all');
  const [includeRegions, setIncludeRegions] = useState(true);

  const generateCSV = () => {
    const headers = ['Data', 'Regiao', 'Casos_Confirmados', 'Mosquitos_Detectados', 'Taxa_Infeccao', 'Intervencoes'];
    
    // Dados simulados para exportação
    const data = [
      ['2024-01-15', 'Zona Sul', '45', '120', '0.38', 'Pulverização'],
      ['2024-01-15', 'Centro', '32', '85', '0.29', 'Monitoramento'],
      ['2024-01-16', 'Zona Sul', '52', '135', '0.42', 'Pulverização'],
      ['2024-01-16', 'Centro', '38', '92', '0.31', 'Monitoramento'],
      ['2024-01-17', 'Zona Sul', '61', '148', '0.45', 'Pulverização Intensiva'],
      ['2024-01-17', 'Centro', '41', '98', '0.33', 'Campanha Preventiva'],
      ['2024-01-18', 'Zona Sul', '58', '142', '0.43', 'Pulverização'],
      ['2024-01-18', 'Centro', '44', '105', '0.35', 'Monitoramento'],
      ['2024-01-19', 'Zona Sul', '67', '155', '0.47', 'Pulverização Intensiva'],
      ['2024-01-19', 'Centro', '47', '112', '0.37', 'Campanha Preventiva']
    ];

    const csvContent = [
      headers.join(','),
      ...data.map(row => row.join(','))
    ].join('\n');

    return csvContent;
  };

  const generateJSON = () => {
    const data = {
      metadata: {
        exportDate: new Date().toISOString(),
        timeRange: dateRange,
        includeRegions: includeRegions,
        totalRecords: 1567
      },
      records: [
        {
          date: '2024-01-15',
          region: 'Zona Sul',
          cases: 45,
          mosquitoes: 120,
          infectionRate: 0.38,
          interventions: ['Pulverização']
        },
        {
          date: '2024-01-15',
          region: 'Centro',
          cases: 32,
          mosquitoes: 85,
          infectionRate: 0.29,
          interventions: ['Monitoramento']
        }
      ]
    };
    return JSON.stringify(data, null, 2);
  };

  const handleExport = () => {
    let content, mimeType, extension;

    if (exportFormat === 'csv') {
      content = generateCSV();
      mimeType = 'text/csv';
      extension = 'csv';
    } else {
      content = generateJSON();
      mimeType = 'application/json';
      extension = 'json';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dengue_data_${new Date().toISOString().split('T')[0]}.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="data-export">
      <div className="export-header">
        <h2>📤 Exportar Dados da Dengue</h2>
        <p>Exporte dados históricos e em tempo real para análise externa</p>
      </div>

      <div className="export-config">
        <div className="config-section">
          <h3>Configurações de Exportação</h3>
          
          <div className="config-group">
            <label>Formato de Exportação</label>
            <select 
              value={exportFormat} 
              onChange={(e) => setExportFormat(e.target.value)}
            >
              <option value="csv">CSV (Excel)</option>
              <option value="json">JSON</option>
            </select>
          </div>

          <div className="config-group">
            <label>Período dos Dados</label>
            <select 
              value={dateRange} 
              onChange={(e) => setDateRange(e.target.value)}
            >
              <option value="week">Última Semana</option>
              <option value="month">Último Mês</option>
              <option value="quarter">Último Trimestre</option>
              <option value="year">Último Ano</option>
              <option value="all">Todos os Dados</option>
            </select>
          </div>

          <div className="config-group">
            <label className="checkbox-label">
              <input 
                type="checkbox" 
                checked={includeRegions}
                onChange={(e) => setIncludeRegions(e.target.checked)}
              />
              Incluir dados regionais detalhados
            </label>
          </div>
        </div>

        <div className="preview-section">
          <h3>Pré-visualização dos Dados</h3>
          <div className="data-preview">
            <pre>
              {exportFormat === 'csv' ? generateCSV().split('\n').slice(0, 6).join('\n') + '\n...' : generateJSON().split('\n').slice(0, 10).join('\n') + '\n...'}
            </pre>
          </div>
        </div>
      </div>

      <div className="export-actions">
        <button className="export-btn primary" onClick={handleExport}>
          📥 Exportar Dados
        </button>
        <button className="export-btn secondary">
          ⏰ Agendar Exportação Automática
        </button>
      </div>

      <div className="export-info">
        <h4>💡 Informações sobre os Dados</h4>
        <ul>
          <li><strong>CSV:</strong> Ideal para análise em Excel, Power BI e outras ferramentas de BI</li>
          <li><strong>JSON:</strong> Formato estruturado para integração com sistemas e APIs</li>
          <li>Os dados incluem informações desde Janeiro de 2023</li>
          <li>Atualizações automáticas diárias às 02:00</li>
        </ul>
      </div>
    </div>
  );
};

export default DataExport;