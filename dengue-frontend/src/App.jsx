// src/App.jsx
import React, { useState, useEffect } from 'react';
import Dashboard from './Dashboard';
import AgentVisualization from './AgentVisualization';
import MapView from './MapView';
import Analytics from './Analytics';
import DataExport from './DataExport';
import Database from './Database';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [simulationData, setSimulationData] = useState(null);
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);

  const tabs = [
    { id: 'dashboard', name: 'Painel Principal', icon: '📊' },
    { id: 'agents', name: 'Simulação de Agentes', icon: '🦠' },
    { id: 'map', name: 'Mapa de Calor', icon: '🗺️' },
    { id: 'analytics', name: 'Analytics', icon: '📈' },
    { id: 'export', name: 'Exportar Dados', icon: '📤' },
    { id: 'database', name: 'Banco de Dados', icon: '💾' }
  ];

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🚀 Sistema de Monitoramento - Dengue SP</h1>
          <p>Monitoramento em tempo real da propagação da dengue em São Paulo</p>
        </div>
      </header>

      <nav className="navigation">
        <div className="nav-tabs">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-name">{tab.name}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="main-content">
        {activeTab === 'dashboard' && (
          <Dashboard 
            onDataUpdate={setSimulationData}
            onSimulationRunning={setIsSimulationRunning}
          />
        )}
        {activeTab === 'agents' && (
          <AgentVisualization 
            simulationData={simulationData}
            isRunning={isSimulationRunning}
          />
        )}
        {activeTab === 'map' && (
          <MapView simulationData={simulationData} />
        )}
        {activeTab === 'analytics' && (
          <Analytics simulationData={simulationData} />
        )}
        {activeTab === 'export' && (
          <DataExport simulationData={simulationData} />
        )}
        {activeTab === 'database' && (
          <Database />
        )}
      </main>

      <footer className="app-footer">
        <p>© 2024 Sistema de Monitoramento de Dengue - Secretaria de Saúde de SP</p>
      </footer>
    </div>
  );
}

export default App;