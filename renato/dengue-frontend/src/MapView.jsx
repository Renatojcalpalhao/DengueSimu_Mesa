// src/components/MapView.jsx
import React, { useState, useEffect, useRef } from 'react';
import './MapView.css';

const MapView = ({ simulationData }) => {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [timeRange, setTimeRange] = useState('week');
  const canvasRef = useRef(null);
  const [mapImage, setMapImage] = useState(null);

  // Dados simulados das regiões de SP
  const regions = [
    { 
      id: 'centro', 
      name: 'Centro', 
      cases: 245, 
      intensity: 0.8, 
      coordinates: { x: 400, y: 300 },
      hotspots: [
        { x: 380, y: 280, radius: 25 },
        { x: 420, y: 320, radius: 20 }
      ]
    },
    { 
      id: 'zona-norte', 
      name: 'Zona Norte', 
      cases: 189, 
      intensity: 0.6, 
      coordinates: { x: 300, y: 150 },
      hotspots: [
        { x: 280, y: 130, radius: 20 }
      ]
    },
    { 
      id: 'zona-sul', 
      name: 'Zona Sul', 
      cases: 312, 
      intensity: 0.9, 
      coordinates: { x: 400, y: 500 },
      hotspots: [
        { x: 380, y: 480, radius: 30 },
        { x: 420, y: 520, radius: 25 }
      ]
    },
    { 
      id: 'zona-leste', 
      name: 'Zona Leste', 
      cases: 278, 
      intensity: 0.7, 
      coordinates: { x: 600, y: 300 },
      hotspots: [
        { x: 580, y: 280, radius: 22 }
      ]
    },
    { 
      id: 'zona-oeste', 
      name: 'Zona Oeste', 
      cases: 156, 
      intensity: 0.5, 
      coordinates: { x: 200, y: 300 },
      hotspots: [
        { x: 180, y: 320, radius: 18 }
      ]
    }
  ];

  // Carregar ou criar mapa de São Paulo
  useEffect(() => {
    const createSaoPauloMap = () => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = 800;
      canvas.height = 600;

      // Fundo do mapa estilo geográfico
      ctx.fillStyle = '#2c5530';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Contorno principal de SP
      ctx.strokeStyle = '#1a472a';
      ctx.lineWidth = 4;
      ctx.strokeRect(50, 50, canvas.width - 100, canvas.height - 100);

      // Zonas da cidade com formas orgânicas
      const drawZone = (x, y, radius, color, name) => {
        ctx.fillStyle = color;
        ctx.beginPath();
        
        // Forma orgânica irregular
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.strokeStyle = '#1a472a';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Nome da zona
        ctx.fillStyle = 'white';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(name, x, y);
      };

      // Desenhar zonas
      drawZone(400, 300, 80, '#4a6741', 'Centro');
      drawZone(300, 150, 60, '#3d5a40', 'Norte');
      drawZone(400, 500, 90, '#588157', 'Sul');
      drawZone(600, 300, 65, '#3a5a40', 'Leste');
      drawZone(200, 300, 55, '#344e41', 'Oeste');

      // Rios e áreas verdes
      ctx.fillStyle = '#74b9ff';
      ctx.beginPath();
      ctx.ellipse(350, 250, 120, 30, Math.PI / 6, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#74b9ff';
      ctx.beginPath();
      ctx.ellipse(450, 400, 100, 25, -Math.PI / 5, 0, Math.PI * 2);
      ctx.fill();

      // Principais vias
      ctx.strokeStyle = '#8a9c6a';
      ctx.lineWidth = 3;
      
      // Marginais
      ctx.beginPath();
      ctx.moveTo(100, 200);
      ctx.lineTo(700, 180);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(100, 400);
      ctx.lineTo(700, 420);
      ctx.stroke();

      // Anel viário
      ctx.beginPath();
      ctx.arc(400, 300, 150, 0, Math.PI * 2);
      ctx.stroke();

      setMapImage(canvas);
    };

    createSaoPauloMap();
  }, []);

  // Desenhar mapa e heatmap
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !mapImage) return;

    const ctx = canvas.getContext('2d');
    
    // Limpar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Desenhar mapa de fundo
    ctx.drawImage(mapImage, 0, 0, canvas.width, canvas.height);

    // Desenhar pontos de calor
    drawHeatmap(ctx);

  }, [mapImage, selectedRegion]);

  const drawHeatmap = (ctx) => {
    regions.forEach(region => {
      const intensity = region.intensity;
      
      // Desenhar calor da região
      const gradient = ctx.createRadialGradient(
        region.coordinates.x, region.coordinates.y, 10,
        region.coordinates.x, region.coordinates.y, 80
      );
      
      gradient.addColorStop(0, `rgba(255, 0, 0, ${intensity * 0.7})`);
      gradient.addColorStop(0.5, `rgba(255, 165, 0, ${intensity * 0.4})`);
      gradient.addColorStop(1, `rgba(255, 255, 0, ${intensity * 0.1})`);

      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(region.coordinates.x, region.coordinates.y, 80, 0, Math.PI * 2);
      ctx.fill();

      // Desenhar hotspots específicos
      region.hotspots.forEach(hotspot => {
        // Círculo pulsante para hotspots
        ctx.strokeStyle = `rgba(255, ${255 - intensity * 255}, 0, 0.8)`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(hotspot.x, hotspot.y, hotspot.radius + 3, 0, Math.PI * 2);
        ctx.stroke();

        // Núcleo do hotspot
        const hotspotGradient = ctx.createRadialGradient(
          hotspot.x, hotspot.y, 0,
          hotspot.x, hotspot.y, hotspot.radius
        );
        hotspotGradient.addColorStop(0, `rgba(255, 0, 0, ${intensity})`);
        hotspotGradient.addColorStop(1, `rgba(255, 165, 0, ${intensity * 0.3})`);

        ctx.fillStyle = hotspotGradient;
        ctx.beginPath();
        ctx.arc(hotspot.x, hotspot.y, hotspot.radius, 0, Math.PI * 2);
        ctx.fill();

        // Ícone de fogo para hotspots intensos
        if (intensity > 0.7) {
          ctx.fillStyle = '#ff4444';
          ctx.font = '16px Arial';
          ctx.fillText('🔥', hotspot.x - 8, hotspot.y - hotspot.radius - 10);
        }
      });

      // Destacar região selecionada
      if (selectedRegion === region.id) {
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.arc(region.coordinates.x, region.coordinates.y, 90, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });
  };

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

  const handleMapClick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Verificar clique nas regiões
    const clickedRegion = regions.find(region => {
      const distance = Math.sqrt(
        Math.pow(x - region.coordinates.x, 2) + 
        Math.pow(y - region.coordinates.y, 2)
      );
      return distance <= 80; // Raio de clique
    });

    if (clickedRegion) {
      setSelectedRegion(clickedRegion.id);
    } else {
      setSelectedRegion(null);
    }
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
          <canvas
            ref={canvasRef}
            width={800}
            height={600}
            onClick={handleMapClick}
            className="geo-map-canvas"
            style={{ cursor: 'pointer' }}
          />
        </div>

        <div className="map-legend">
          <h4>Legenda de Intensidade</h4>
          <div className="legend-items">
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#27ae60' }}></div>
              <span>Baixa (0-40%)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#f1c40f' }}></div>
              <span>Moderada (40-60%)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#e67e22' }}></div>
              <span>Alta (60-80%)</span>
            </div>
            <div className="legend-item">
              <div className="legend-color" style={{ backgroundColor: '#e74c3c' }}></div>
              <span>Muito Alta (80-100%)</span>
            </div>
          </div>

          <div className="hotspot-legend">
            <h5>🔥 Pontos de Calor</h5>
            <p>Áreas com focos ativos de dengue</p>
            <div className="hotspot-example">
              <div className="hotspot-dot"></div>
              <span>Foco identificado</span>
            </div>
            <div className="hotspot-example">
              <div className="hotspot-dot intense"></div>
              <span>Foco crítico</span>
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
                    <span className="value">{region.hotspots.length}</span>
                  </div>
                  <div className="detail-item">
                    <label>Nível de Risco</label>
                    <span 
                      className="value risk-badge"
                      style={{ 
                        backgroundColor: getIntensityColor(region.intensity),
                        color: 'white',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '0.8rem'
                      }}
                    >
                      {region.intensity >= 0.7 ? 'ALTO' : 'MODERADO'}
                    </span>
                  </div>
                  <div className="detail-item">
                    <label>Ações Recomendadas</label>
                    <span className="value actions">
                      {region.intensity >= 0.7 ? '🔴 Controle urgente' : '🟡 Monitoramento'}
                    </span>
                  </div>
                </div>
                <div className="hotspot-list">
                  <h5>Pontos de Calor Identificados:</h5>
                  <ul>
                    {region.hotspots.map((hotspot, index) => (
                      <li key={index}>
                        🔥 Foco {index + 1} - {hotspot.radius > 25 ? 'Crítico' : 'Ativo'}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })()}
        </div>
      )}

      <div className="map-footer">
        <p>💡 <strong>Dica:</strong> Clique nas regiões coloridas para ver detalhes específicos</p>
        <p>🗓️ Dados simulados em tempo real - {timeRange === 'week' ? 'Última semana' : 
           timeRange === 'month' ? 'Último mês' : 
           timeRange === 'quarter' ? 'Último trimestre' : 'Último ano'}</p>
      </div>
    </div>
  );
};

export default MapView;