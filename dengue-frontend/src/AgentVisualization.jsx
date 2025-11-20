// src/AgentVisualization.jsx
import React, { useState, useEffect, useRef } from 'react';
import './AgentVisualization.css';

const AgentVisualization = ({ simulationData, isRunning }) => {
  const canvasRef = useRef(null);
  const [agents, setAgents] = useState([]);
  const [speed, setSpeed] = useState(1);

  // Inicializar agentes
  useEffect(() => {
    initializeAgents();
  }, [simulationData]);

  // Atualizar simulação
  useEffect(() => {
    let animationFrame;
    
    const animate = () => {
      if (isRunning) {
        updateAgents();
      }
      animationFrame = requestAnimationFrame(animate);
    };

    if (isRunning) {
      animationFrame = requestAnimationFrame(animate);
    }

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [isRunning, speed]);

  // Desenhar no canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    drawAgents(ctx);
  }, [agents]);

  const initializeAgents = () => {
    if (!simulationData) return;

    const newAgents = [];
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Humanos saudáveis
    for (let i = 0; i < simulationData.population - simulationData.humans; i++) {
      newAgents.push({
        type: 'human',
        status: 'healthy',
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        dx: (Math.random() - 0.5) * 2,
        dy: (Math.random() - 0.5) * 2,
        size: 6
      });
    }

    // Humanos infectados
    for (let i = 0; i < simulationData.humans; i++) {
      newAgents.push({
        type: 'human',
        status: 'infected',
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        dx: (Math.random() - 0.5) * 1.5,
        dy: (Math.random() - 0.5) * 1.5,
        size: 6,
        infectionTime: 0
      });
    }

    // Mosquitos
    for (let i = 0; i < simulationData.mosquitoes; i++) {
      newAgents.push({
        type: 'mosquito',
        status: Math.random() > 0.7 ? 'infected' : 'healthy',
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        dx: (Math.random() - 0.5) * 4,
        dy: (Math.random() - 0.5) * 4,
        size: 3
      });
    }

    setAgents(newAgents);
  };

  const updateAgents = () => {
    setAgents(prevAgents => {
      const canvas = canvasRef.current;
      if (!canvas) return prevAgents;

      return prevAgents.map(agent => {
        // Atualizar posição
        let newX = agent.x + agent.dx * speed;
        let newY = agent.y + agent.dy * speed;

        // Colisão com bordas
        if (newX <= 0 || newX >= canvas.width) agent.dx *= -1;
        if (newY <= 0 || newY >= canvas.height) agent.dy *= -1;

        // Manter dentro dos limites
        newX = Math.max(0, Math.min(canvas.width, newX));
        newY = Math.max(0, Math.min(canvas.height, newY));

        // Atualizar infecção
        let newStatus = agent.status;
        if (agent.type === 'human' && agent.status === 'healthy') {
          // Verificar se foi infectado por mosquito
          const nearbyInfected = prevAgents.filter(a => 
            a.type === 'mosquito' && 
            a.status === 'infected' &&
            Math.sqrt((a.x - newX) ** 2 + (a.y - newY) ** 2) < 15
          );
          if (nearbyInfected.length > 0 && Math.random() > 0.95) {
            newStatus = 'infected';
          }
        }

        // Atualizar tempo de infecção
        let infectionTime = agent.infectionTime || 0;
        if (agent.type === 'human' && agent.status === 'infected') {
          infectionTime += 1;
        }

        return {
          ...agent,
          x: newX,
          y: newY,
          status: newStatus,
          infectionTime
        };
      });
    });
  };

  const drawAgents = (ctx) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Limpar canvas
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Desenhar grade de fundo
    ctx.strokeStyle = '#2d3047';
    ctx.lineWidth = 0.5;
    const gridSize = 40;
    for (let x = 0; x < canvas.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Desenhar agentes
    agents.forEach(agent => {
      ctx.beginPath();
      
      if (agent.type === 'human') {
        if (agent.status === 'healthy') {
          ctx.fillStyle = '#27ae60'; // Verde para saudável
        } else {
          // Vermelho com intensidade baseada no tempo de infecção
          const intensity = Math.min(1, (agent.infectionTime || 0) / 300);
          ctx.fillStyle = `rgb(231, ${76 + (1 - intensity) * 150}, 60)`;
        }
        ctx.arc(agent.x, agent.y, agent.size, 0, Math.PI * 2);
      } else { // mosquito
        if (agent.status === 'healthy') {
          ctx.fillStyle = '#3498db'; // Azul para mosquito saudável
        } else {
          ctx.fillStyle = '#ff9800'; // LARANJA para mosquito infectado (atualizado)
        }
        // Desenhar mosquito como um ponto alongado
        ctx.ellipse(agent.x, agent.y, agent.size, agent.size * 0.5, Math.atan2(agent.dy, agent.dx), 0, Math.PI * 2);
      }
      
      ctx.fill();
      
      // Adicionar brilho para agentes infectados
      if (agent.status === 'infected') {
        ctx.beginPath();
        ctx.arc(agent.x, agent.y, agent.size + 2, 0, Math.PI * 2);
        if (agent.type === 'human') {
          ctx.strokeStyle = 'rgba(231, 76, 60, 0.3)';
        } else {
          ctx.strokeStyle = 'rgba(255, 152, 0, 0.3)';
        }
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    });
  };

  const handleCanvasClick = (event) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Adicionar um humano infectado no local clicado
    setAgents(prev => [...prev, {
      type: 'human',
      status: 'infected',
      x,
      y,
      dx: (Math.random() - 0.5) * 2,
      dy: (Math.random() - 0.5) * 2,
      size: 6,
      infectionTime: 0
    }]);
  };

  return (
    <div className="agent-visualization">
      <div className="visualization-header">
        <h3>🦠 Simulação de Agentes - Propagação da Dengue</h3>
        <div className="visualization-controls">
          <div className="speed-control">
            <label>Velocidade: </label>
            <input
              type="range"
              min="0.1"
              max="3"
              step="0.1"
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
            />
            <span>{speed}x</span>
          </div>
          <button onClick={initializeAgents} className="reset-btn">
            🔄 Reiniciar
          </button>
        </div>
      </div>

      <div className="canvas-container">
        <canvas
          ref={canvasRef}
          width={800}
          height={500}
          onClick={handleCanvasClick}
          className="agent-canvas"
        />
        
        <div className="legend">
          <h4>Legenda:</h4>
          <div className="legend-items">
            <div className="legend-item">
              <div className="color-box healthy-human"></div>
              <span>Humano Saudável</span>
            </div>
            <div className="legend-item">
              <div className="color-box infected-human"></div>
              <span>Humano Infectado</span>
            </div>
            <div className="legend-item">
              <div className="color-box healthy-mosquito"></div>
              <span>Mosquito Saudável</span>
            </div>
            <div className="legend-item">
              <div className="color-box infected-mosquito"></div>
              <span>Mosquito Infectado</span>
            </div>
          </div>
          <div className="legend-info">
            <p>💡 Clique no mapa para adicionar agentes infectados</p>
          </div>
        </div>
      </div>

      <div className="stats-overlay">
        <div className="stat-item">
          <span className="stat-label">Humanos Saudáveis:</span>
          <span className="stat-value">
            {agents.filter(a => a.type === 'human' && a.status === 'healthy').length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Humanos Infectados:</span>
          <span className="stat-value infected">
            {agents.filter(a => a.type === 'human' && a.status === 'infected').length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Mosquitos Saudáveis:</span>
          <span className="stat-value">
            {agents.filter(a => a.type === 'mosquito' && a.status === 'healthy').length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Mosquitos Infectados:</span>
          <span className="stat-value infected">
            {agents.filter(a => a.type === 'mosquito' && a.status === 'infected').length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Taxa de Infecção:</span>
          <span className="stat-value">
            {agents.filter(a => a.type === 'human').length > 0 
              ? ((agents.filter(a => a.type === 'human' && a.status === 'infected').length / 
                  agents.filter(a => a.type === 'human').length) * 100).toFixed(1) + '%'
              : '0%'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AgentVisualization;