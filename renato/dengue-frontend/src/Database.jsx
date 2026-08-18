// src/components/Database.jsx
import React, { useState, useEffect } from 'react';
import './Database.css';

const Database = () => {
  const [dbStats, setDbStats] = useState(null);
  const [backupStatus, setBackupStatus] = useState('stable');
  const [operations, setOperations] = useState([]);

  useEffect(() => {
    // Simular dados do banco
    setDbStats({
      totalRecords: 15678,
      storageUsed: '2.3 GB',
      lastBackup: '2024-01-19 02:00',
      uptime: '99.8%',
      activeConnections: 12
    });

    setOperations([
      { id: 1, type: 'INSERT', table: 'cases', timestamp: '2024-01-19 10:30', status: 'success' },
      { id: 2, type: 'UPDATE', table: 'regions', timestamp: '2024-01-19 10:25', status: 'success' },
      { id: 3, type: 'BACKUP', table: 'system', timestamp: '2024-01-19 02:00', status: 'success' },
      { id: 4, type: 'ANALYZE', table: 'statistics', timestamp: '2024-01-19 01:30', status: 'running' }
    ]);
  }, []);

  const handleBackup = () => {
    setBackupStatus('backing_up');
    setTimeout(() => setBackupStatus('completed'), 3000);
  };

  const handleOptimize = () => {
    // Simular otimização
    alert('Otimização do banco de dados iniciada!');
  };

  return (
    <div className="database">
      <div className="database-header">
        <h2>💾 Banco de Dados - Histórico de Dengue</h2>
        <p>Gerenciamento e monitoramento do banco de dados histórico</p>
      </div>

      {dbStats && (
        <div className="db-stats">
          <h3>Estatísticas do Banco</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{dbStats.totalRecords.toLocaleString()}</div>
              <div className="stat-label">Registros Totais</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{dbStats.storageUsed}</div>
              <div className="stat-label">Armazenamento</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{dbStats.uptime}</div>
              <div className="stat-label">Uptime</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">{dbStats.activeConnections}</div>
              <div className="stat-label">Conexões Ativas</div>
            </div>
          </div>
        </div>
      )}

      <div className="db-actions">
        <h3>Ações do Banco</h3>
        <div className="action-buttons">
          <button 
            className={`action-btn ${backupStatus}`}
            onClick={handleBackup}
            disabled={backupStatus === 'backing_up'}
          >
            {backupStatus === 'backing_up' ? '⚡ Fazendo Backup...' : 
             backupStatus === 'completed' ? '✅ Backup Concluído' : '💾 Fazer Backup'}
          </button>
          <button className="action-btn" onClick={handleOptimize}>
            🛠️ Otimizar Banco
          </button>
          <button className="action-btn">
            📋 Gerar Relatório
          </button>
        </div>
      </div>

      <div className="db-operations">
        <h3>Últimas Operações</h3>
        <div className="operations-list">
          {operations.map(op => (
            <div key={op.id} className={`operation-item ${op.status}`}>
              <div className="op-type">{op.type}</div>
              <div className="op-table">{op.table}</div>
              <div className="op-timestamp">{op.timestamp}</div>
              <div className="op-status">
                {op.status === 'success' ? '✅' : 
                 op.status === 'running' ? '⚡' : '❌'}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="db-schema">
        <h3>Estrutura do Banco</h3>
        <div className="schema-tables">
          <div className="table-card">
            <h4>📋 Tabela: cases</h4>
            <div className="table-fields">
              <div className="field">id (PK)</div>
              <div className="field">date (DATE)</div>
              <div className="field">region_id (FK)</div>
              <div className="field">cases_count (INT)</div>
              <div className="field">created_at (TIMESTAMP)</div>
            </div>
          </div>
          <div className="table-card">
            <h4>🗺️ Tabela: regions</h4>
            <div className="table-fields">
              <div className="field">id (PK)</div>
              <div className="field">name (VARCHAR)</div>
              <div className="field">coordinates (JSON)</div>
              <div className="field">population (INT)</div>
            </div>
          </div>
          <div className="table-card">
            <h4>📊 Tabela: statistics</h4>
            <div className="table-fields">
              <div className="field">id (PK)</div>
              <div className="field">metric_name (VARCHAR)</div>
              <div className="field">metric_value (FLOAT)</div>
              <div className="field">calculation_date (DATE)</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Database;