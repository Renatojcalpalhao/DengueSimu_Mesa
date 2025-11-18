// src/components/MapView.jsx
import React, { useState, useEffect } from 'react';
import './MapView.css';

const MapView = ({ simulationData }) => {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [timeRange, setTimeRange] = useState('week');

  // Dados simulados das regiões de SP
  const regions = [
    { id: 'centro', name: 'Centro', cases: 245, intensity: 0.8, coordinates: { x: 45, y: 45 } },
    { id: 'zona-norte', name: 'Zona Norte', cases: 189, intensity: 0.6, coordinates: { x: 40, y: 25 } },
    { id: 'zona-sul', name: 'Zona Sul', cases: 312, intensity: 0.9, coordinates: { x: 45, y: 65 } },
    { id: 'zona-leste', name: 'Zona Leste', cases: 278, intensity: 0.7, coordinates: { x: 65, y: 45 } },
    { id: 'zona-oeste', name: 'Zona Oeste', cases: 156, intensity: 0.5, coordinates: { x: 25, y: 45 } },
    { id: 'abc', name: 'ABC Paulista', cases: 201, intensity: 0.6, coordinates: { x: 60, y: 70 } }
  ];

  const getIntensityColor = (intensity) => {
    if (intensity >= 0.8) return '#e74c3c';
    if (intensity >= 0.6) return '#e67e22';
    if (intensity >= 0.4) return '#f1c40f';
    return '#27ae60';
  };

  const getIntensityLabel = (intensity) => {
    if (intensity >= 0.8) return 'Muito Alta';
    if (intensity >= 0.6) return 'Alta';
    if (intensity >= 0.4) return 'Moderada';
    return 'Baixa';
  };

  return (
    <div className="map-view">
      <div className="map-header">
        <h2>🗺️ Mapa de Calor - Dengue em São Paulo</h2>
        <div className="map-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-selector"
          >
            <option value="week">Última Semana</option>
            <option value="month">Último Mês</option>
            <option value="quarter">Último Trimestre</option>
            <option value="year">Último Ano</option>
          </select>
        </div>
      </div>

      <div className="map-container">
        <div className="sp-map">
          {/* Mapa simplificado de SP */}
          <div className="map-outline">
            {regions.map(region => (
              <div
                key={region.id}
                className="map-region"
                style={{
                  left: `${region.coordinates.x}%`,
                  top: `${region.coordinates.y}%`,
                  backgroundColor: getIntensityColor(region.intensity),
                  transform: `scale(${0.8 + region.intensity * 0.4})`,
                  opacity: selectedRegion === region.id ? 1 : 0.8
                }}
                onClick={() => setSelectedRegion(region.id)}
                onMouseEnter={() => setSelectedRegion(region.id)}
                onMouseLeave={() => setSelectedRegion(null)}
              >
                <div className="region-tooltip">
                  <strong>{region.name}</strong>
                  <br />
                  Casos: {region.cases}
                  <br />
                  Intensidade: {getIntensityLabel(region.intensity)}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="map-legend">
          <h4>Legenda de Intensidade</h4>
          <div className="legend-items">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#27ae60' }}></div>
              <span>Baixa</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#f1c40f' }}></div>
              <span>Moderada</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#e67e22' }}></div>
              <span>Alta</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#e74c3c' }}></div>
              <span>Muito Alta</span>
            </div>
          </div>
        </div>
      </div>

      {selectedRegion && (
        <div className="region-details">
          <h3>Detalhes da Região</h3>
          {(() => {
            const region = regions.find(r => r.id === selectedRegion);
            return (
              <div className="detail-card">
                <h4>{region.name}</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Total de Casos</label>
                    <span className="value">{region.cases}</span>
                  </div>
                  <div className="detail-item">
                    <label>Intensidade</label>
                    <span 
                      className="value" 
                      style={{ color: getIntensityColor(region.intensity) }}
                    >
                      {getIntensityLabel(region.intensity)}
                    </span>
                  </div>
                  <div className="detail-item">
                    <label>Taxa de Crescimento</label>
                    <span className="value">+{(region.intensity * 15).toFixed(1)}%</span>
                  </div>
                  <div className="detail-item">
                    <label>Focos Identificados</label>
                    <span className="value">{Math.floor(region.cases / 2)}</span>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
};

export default MapView;