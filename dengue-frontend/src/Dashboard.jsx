// src/Dashboard.jsx
import React, { useState, useEffect } from 'react';

const Dashboard = ({ onDataUpdate, onSimulationRunning }) => {
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [simulationData, setSimulationData] = useState({
    humans: 50,
    recovered: 0,
    vaccinated: 3000,
    mosquitoes: 500,
    infectionRate: 0.05,
    time: 0,
    population: 10000,
    newCases: 0,
    activeInterventions: 0,
    trend: 'stable' // 'increasing', 'decreasing', 'stable'
  });
  
  const [settings, setSettings] = useState({
    population: 10000,
    initialInfected: 50,
    vaccinationRate: 30,
    transmissionRate: 50,
    temperature: 25,
    recoveryRate: 20, // % de recuperação por dia - AUMENTADO
    immunityDuration: 120, // dias de imunidade - AUMENTADO
    interventionIntensity: 50, // intensidade das intervenções
    mosquitoControl: 50 // controle específico de mosquitos
  });

  const initializeSimulation = () => {
    const vaccinated = Math.floor(settings.population * (settings.vaccinationRate / 100));
    const newData = {
      humans: settings.initialInfected,
      recovered: 0,
      vaccinated: vaccinated,
      mosquitoes: Math.floor(settings.initialInfected * 5), // REDUZIDO
      infectionRate: 0.05,
      time: 0,
      population: settings.population,
      newCases: 0,
      activeInterventions: 0,
      trend: 'stable'
    };
    setSimulationData(newData);
    if (onDataUpdate) onDataUpdate(newData);
  };

  const runSimulationStep = () => {
    if (!isSimulationRunning) return;

    setSimulationData(prevData => {
      // Fatores ambientais e de configuração
      const tempFactor = Math.max(0.1, (settings.temperature - 15) / 20); // Temperatura mais realista
      const transmissionFactor = settings.transmissionRate / 100;
      const vaccinationFactor = settings.vaccinationRate / 100;
      const recoveryFactor = settings.recoveryRate / 100;
      const interventionFactor = settings.interventionIntensity / 100;
      const mosquitoControlFactor = settings.mosquitoControl / 100;
      
      // Fatores aleatórios para simular variações naturais
      const randomFactor = 0.7 + Math.random() * 0.6; // Mais variação
      const seasonFactor = 0.8 + Math.sin(prevData.time / 60) * 0.4; // Variação sazonal mais lenta

      // POPULAÇÃO SUSCETÍVEL (que pode ser infectada)
      const susceptiblePopulation = Math.max(0, 
        prevData.population - prevData.humans - prevData.recovered - prevData.vaccinated
      );

      // CALCULAR NOVAS INFECÇÕES (com limite realista)
      const baseInfectionProbability = 0.0001; // Probabilidade base baixa
      const infectionPressure = (prevData.mosquitoes / 1000) * transmissionFactor * tempFactor * seasonFactor;
      const dailyInfectionRate = baseInfectionProbability * infectionPressure * randomFactor;
      
      const newInfections = Math.floor(
        Math.min(
          susceptiblePopulation * dailyInfectionRate,
          susceptiblePopulation * 0.05 // Máximo de 5% da população suscetível por dia
        ) * (1 - interventionFactor * 0.7) // Intervenções reduzem drasticamente
      );

      // CALCULAR RECUPERAÇÕES (mais pessoas se recuperam)
      const dailyRecoveries = Math.floor(
        prevData.humans * recoveryFactor * (0.8 + Math.random() * 0.4)
      );
      const actualRecoveries = Math.min(dailyRecoveries, prevData.humans);

      // CALCULAR PERDA DE IMUNIDADE (mais lenta)
      const immunityLoss = Math.floor(
        prevData.recovered * (1 / settings.immunityDuration) * (0.5 + Math.random())
      );

      // NOVAS VACINAÇÕES (contínuas)
      const newVaccinations = Math.floor(
        (settings.population - prevData.vaccinated - prevData.humans) * 
        vaccinationFactor * 0.002 * randomFactor
      );

      // DINÂMICA DOS MOSQUITOS (mais realista)
      const mosquitoBirthRate = tempFactor * 0.05 * seasonFactor;
      const naturalMosquitoDeathRate = 0.08;
      const controlMosquitoDeathRate = mosquitoControlFactor * 0.15;
      
      const newMosquitoes = Math.floor(
        prevData.mosquitoes * mosquitoBirthRate * randomFactor
      );
      
      const mosquitoDeaths = Math.floor(
        prevData.mosquitoes * (naturalMosquitoDeathRate + controlMosquitoDeathRate) * randomFactor
      );

      // EFEITO DAS INTERVENÇÕES (mais forte)
      const interventionEffect = interventionFactor * randomFactor;
      const additionalInfectionReduction = interventionEffect * 0.6;

      // ATUALIZAR VALORES COM LIMITES
      const updatedHumans = Math.max(0, Math.min(
        prevData.humans + newInfections - actualRecoveries,
        settings.population
      ));

      const updatedRecovered = Math.max(0, Math.min(
        prevData.recovered + actualRecoveries - immunityLoss,
        settings.population - updatedHumans - prevData.vaccinated
      ));

      const updatedVaccinated = Math.max(0, Math.min(
        prevData.vaccinated + newVaccinations,
        settings.population - updatedHumans - updatedRecovered
      ));

      const updatedMosquitoes = Math.max(10, 
        prevData.mosquitoes + newMosquitoes - mosquitoDeaths
      );

      // DETERMINAR TENDÊNCIA
      let trend = 'stable';
      if (newInfections > actualRecoveries * 1.2) {
        trend = 'increasing';
      } else if (actualRecoveries > newInfections * 1.2) {
        trend = 'decreasing';
      }

      // CALCULAR TAXA DE INFECÇÃO REALISTA
      const activeInfectionRate = updatedHumans / settings.population;
      const transmissionPotential = (updatedMosquitoes / 1000) * transmissionFactor;
      const realisticInfectionRate = Math.min(activeInfectionRate * transmissionPotential * 10, 1);

      const newData = {
        humans: updatedHumans,
        recovered: updatedRecovered,
        vaccinated: updatedVaccinated,
        mosquitoes: updatedMosquitoes,
        infectionRate: realisticInfectionRate,
        time: prevData.time + 1,
        population: settings.population,
        newCases: newInfections,
        activeInterventions: Math.floor(interventionEffect * 100),
        trend: trend
      };

      if (onDataUpdate) onDataUpdate(newData);
      return newData;
    });
  };

  const startSimulation = () => {
    setIsSimulationRunning(true);
    if (onSimulationRunning) onSimulationRunning(true);
  };

  const stopSimulation = () => {
    setIsSimulationRunning(false);
    if (onSimulationRunning) onSimulationRunning(false);
  };

  const resetSimulation = () => {
    stopSimulation();
    initializeSimulation();
  };

  const updateSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  useEffect(() => {
    let interval;
    if (isSimulationRunning) {
      interval = setInterval(runSimulationStep, 1000);
    }
    return () => clearInterval(interval);
  }, [isSimulationRunning]);

  useEffect(() => {
    initializeSimulation();
  }, []);

  const getStatus = (value, mediumThreshold, highThreshold) => {
    if (value < mediumThreshold) return { text: "Baixo", class: "stable" };
    if (value < highThreshold) return { text: "Moderado", class: "info" };
    return { text: "Alto", class: "warning" };
  };

  const getTrendIcon = (trend) => {
    switch(trend) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  const getChartHeight = (value, max) => {
    return Math.min((value / max) * 100, 100);
  };

  const humanStatus = getStatus(simulationData.humans, 100, 500);
  const vaccinatedStatus = getStatus(
    simulationData.vaccinated, 
    settings.population * 0.7, 
    settings.population * 0.9
  );
  const mosquitoStatus = getStatus(simulationData.mosquitoes, 1000, 5000);
  const infectionStatus = getStatus(simulationData.infectionRate * 100, 10, 30);
  const tempStatus = getStatus(settings.temperature, 20, 30);

  // Calcular métricas adicionais
  const totalImmune = simulationData.recovered + simulationData.vaccinated;
  const immunePercentage = (totalImmune / settings.population * 100).toFixed(1);
  const activeCasesPercentage = (simulationData.humans / settings.population * 100).toFixed(1);
  const susceptiblePercentage = ((settings.population - simulationData.humans - totalImmune) / settings.population * 100).toFixed(1);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>📊 Painel de Controle - Simulação de Dengue</h2>
        <p className="simulation-time">
          Tempo de simulação: {simulationData.time} dias | 
          Tendência: {getTrendIcon(simulationData.trend)} {
            simulationData.trend === 'increasing' ? 'Aumentando' : 
            simulationData.trend === 'decreasing' ? 'Diminuindo' : 'Estável'
          }
        </p>
      </div>
      
      <div className="dashboard-grid">
        <div className={`card ${isSimulationRunning ? 'simulation-active' : ''}`}>
          <h2>Simulação em tempo real</h2>
          <div className={`status ${isSimulationRunning ? 'info' : ''}`}>
            {isSimulationRunning ? 'EXECUTANDO' : 'PARADA'}
          </div>
          <div className="divider"></div>
          <p>Novos casos hoje: <strong>{simulationData.newCases}</strong></p>
          <p>População suscetível: <strong>{susceptiblePercentage}%</strong></p>
          <div className="chart-container">
            <div className="chart">
              <div 
                className="chart-line" 
                style={{ 
                  height: `${getChartHeight(simulationData.time, 365)}%`,
                  backgroundColor: '#3498db'
                }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2>CASOS ATIVOS {getTrendIcon(simulationData.trend)}</h2>
          <div className={`status ${humanStatus.class}`}>
            {humanStatus.text}
          </div>
          <div className="divider"></div>
          <p className="large-number">{simulationData.humans.toLocaleString()}</p>
          <p className="percentage">{activeCasesPercentage}% da população</p>
          <div className="chart-container">
            <div className="chart">
              <div 
                className="chart-line" 
                style={{ 
                  height: `${getChartHeight(simulationData.humans, 1000)}%`,
                  backgroundColor: '#e74c3c'
                }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2>POPULAÇÃO IMUNE</h2>
          <div className={`status ${vaccinatedStatus.class}`}>
            {immunePercentage}%
          </div>
          <div className="divider"></div>
          <div className="immune-breakdown">
            <div className="immune-item">
              <span className="label">Recuperados:</span>
              <span className="value">{simulationData.recovered.toLocaleString()}</span>
            </div>
            <div className="immune-item">
              <span className="label">Vacinados:</span>
              <span className="value">{simulationData.vaccinated.toLocaleString()}</span>
            </div>
          </div>
          <div className="chart-container">
            <div className="chart">
              <div 
                className="chart-line" 
                style={{ 
                  height: `${getChartHeight(totalImmune, settings.population)}%`,
                  backgroundColor: '#2ecc71'
                }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2>MOSQUITOS INFECTADOS</h2>
          <div className={`status ${mosquitoStatus.class}`}>
            {mosquitoStatus.text}
          </div>
          <div className="divider"></div>
          <p className="large-number">{simulationData.mosquitoes.toLocaleString()}</p>
          <p className="sub-info">Efetividade das intervenções: {simulationData.activeInterventions}%</p>
          <div className="chart-container">
            <div className="chart">
              <div 
                className="chart-line" 
                style={{ 
                  height: `${getChartHeight(simulationData.mosquitoes, 10000)}%`,
                  backgroundColor: '#f39c12'
                }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2>TAXA DE INFECÇÃO (R₀)</h2>
          <div className={`status ${infectionStatus.class}`}>
            R₀ = {(simulationData.infectionRate * 3).toFixed(1)}
          </div>
          <div className="divider"></div>
          <p className="large-number">{(simulationData.infectionRate * 100).toFixed(1)}%</p>
          <p className="sub-info">Taxa de transmissão básica</p>
          <div className="chart-container">
            <div className="chart">
              <div 
                className="chart-line" 
                style={{ 
                  height: `${getChartHeight(simulationData.infectionRate * 100, 100)}%`,
                  backgroundColor: '#9b59b6'
                }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="card">
          <h2>FATORES AMBIENTAIS</h2>
          <div className="status info">Ativos</div>
          <div className="divider"></div>
          <div className="control-group">
            <label htmlFor="temperature">🌡️ TEMPERATURA MÉDIA</label>
            <input 
              type="range" 
              id="temperature" 
              min="15" 
              max="35" 
              value={settings.temperature}
              onChange={(e) => updateSetting('temperature', parseInt(e.target.value))}
            />
            <p className="temp-value">{settings.temperature} °C</p>
            <p className={`status ${tempStatus.class}`}>{tempStatus.text}</p>
          </div>
        </div>
      </div>
      
      <div className="simulation-controls">
        <h2>Controles da Simulação</h2>
        <div className="controls-grid">
          <div className="control-group">
            <label htmlFor="population">👥 População Total</label>
            <input 
              type="number" 
              id="population" 
              value={settings.population}
              onChange={(e) => updateSetting('population', parseInt(e.target.value))}
              min="1000" 
              max="100000" 
            />
          </div>
          
          <div className="control-group">
            <label htmlFor="initialInfected">🦠 Casos Iniciais</label>
            <input 
              type="number" 
              id="initialInfected" 
              value={settings.initialInfected}
              onChange={(e) => updateSetting('initialInfected', parseInt(e.target.value))}
              min="1" 
              max="1000" 
            />
          </div>
          
          <div className="control-group">
            <label htmlFor="vaccinationRate">💉 Taxa de Vacinação (%)</label>
            <input 
              type="range" 
              id="vaccinationRate" 
              min="0" 
              max="100" 
              value={settings.vaccinationRate}
              onChange={(e) => updateSetting('vaccinationRate', parseInt(e.target.value))}
            />
            <p>{settings.vaccinationRate}%</p>
          </div>
          
          <div className="control-group">
            <label htmlFor="transmissionRate">🔄 Taxa de Transmissão</label>
            <input 
              type="range" 
              id="transmissionRate" 
              min="1" 
              max="100" 
              value={settings.transmissionRate}
              onChange={(e) => updateSetting('transmissionRate', parseInt(e.target.value))}
            />
            <p>{settings.transmissionRate}%</p>
          </div>

          <div className="control-group">
            <label htmlFor="recoveryRate">🏥 Taxa de Recuperação (%)</label>
            <input 
              type="range" 
              id="recoveryRate" 
              min="5" 
              max="40" 
              value={settings.recoveryRate}
              onChange={(e) => updateSetting('recoveryRate', parseInt(e.target.value))}
            />
            <p>{settings.recoveryRate}% por dia</p>
          </div>

          <div className="control-group">
            <label htmlFor="interventionIntensity">🚫 Intensidade das Intervenções</label>
            <input 
              type="range" 
              id="interventionIntensity" 
              min="0" 
              max="100" 
              value={settings.interventionIntensity}
              onChange={(e) => updateSetting('interventionIntensity', parseInt(e.target.value))}
            />
            <p>{settings.interventionIntensity}%</p>
          </div>

          <div className="control-group">
            <label htmlFor="mosquitoControl">🦟 Controle de Mosquitos</label>
            <input 
              type="range" 
              id="mosquitoControl" 
              min="0" 
              max="100" 
              value={settings.mosquitoControl}
              onChange={(e) => updateSetting('mosquitoControl', parseInt(e.target.value))}
            />
            <p>{settings.mosquitoControl}%</p>
          </div>
        </div>
        
        <div className="button-group">
          <button 
            id="startSimulation" 
            onClick={startSimulation}
            disabled={isSimulationRunning}
          >
            ▶️ Iniciar Simulação
          </button>
          <button 
            id="stopSimulation" 
            onClick={stopSimulation}
            disabled={!isSimulationRunning}
          >
            ⏸️ Parar Simulação
          </button>
          <button id="resetSimulation" onClick={resetSimulation}>
            🔄 Reiniciar
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;