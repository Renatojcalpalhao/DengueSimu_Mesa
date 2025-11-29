// src/Dashboard.jsx
import React, { useState, useEffect } from 'react';
import { connectWS } from './ws.js';

// Use UM destes blocos de import - TESTE UM POR VEZ:

// OPÇÃO 1: Caminho absoluto
import CasosPorSemanaChart from "/src/components/CasosPorSemanaChart";
import PainelMetricas from "/src/components/PainelMetricas";
import DistribuicaoDemografiaChart from "/src/components/DistribuicaoDemografiaChart";

// OPÇÃO 2: Caminho relativo
// import CasosPorSemanaChart from "../components/CasosPorSemanaChart";
// import PainelMetricas from "../components/PainelMetricas";
// import DistribuicaoDemografiaChart from "../components/DistribuicaoDemografiaChart";

// OPÇÃO 3: Se criou a pasta InfoDengue
// import CasosPorSemanaChart from "./components/InfoDengue/CasosPorSemanaChart";
// import PainelMetricas from "./components/InfoDengue/PainelMetricas";
// import DistribuicaoDemografiaChart from "./components/InfoDengue/DistribuicaoDemografiaChart";

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
    trend: 'stable'
  });
  
  const [apiData, setApiData] = useState({
    clima: null,
    dengue: null,
    regions: null,
    realTime: null
  });

  const [settings, setSettings] = useState({
    population: 10000,
    initialInfected: 50,
    vaccinationRate: 30,
    transmissionRate: 50,
    temperature: 25,
    recoveryRate: 20,
    immunityDuration: 120,
    interventionIntensity: 50,
    mosquitoControl: 50
  });

  // 1. Conectar com WebSocket para dados em tempo real
  useEffect(() => {
    const ws = connectWS((data) => {
      console.log('📨 Dados WebSocket:', data);
      setApiData(prev => ({ ...prev, realTime: data }));
      
      if (data.humanos_infectados !== undefined) {
        setSimulationData(prev => ({
          ...prev,
          humans: data.humanos_infectados,
          mosquitoes: (data.mosquitos_saudaveis || 0) + (data.mosquitos_infectados || 0),
          infectionRate: data.taxa_infeccao || prev.infectionRate
        }));
      }
    });
    
    return () => {
      ws.close();
    };
  }, []);

  // 2. Buscar dados das APIs HTTP
  useEffect(() => {
    const fetchAPIData = async () => {
      try {
        console.log('🔄 Buscando dados das APIs...');
        
        const [climaRes, dengueRes, regionsRes] = await Promise.all([
          fetch('http://localhost:5000/api/clima').catch(() => ({ json: () => ({ temperatura: 27, umidade: 70, chuva: 0.2 }) })),
          fetch('http://localhost:5000/api/dengue').catch(() => ({ json: () => ({ casos_reais: 1500, alerta: "Amarelo" }) })),
          fetch('http://localhost:5000/api/dengue/regions').catch(() => ({ json: () => ([
            { name: "Centro", cases: 245, risk: "high" },
            { name: "Zona Sul", cases: 312, risk: "very_high" }
          ]) }))
        ]);

        const clima = await climaRes.json();
        const dengue = await dengueRes.json();
        const regions = await regionsRes.json();

        setApiData(prev => ({ ...prev, clima, dengue, regions }));
        console.log('✅ Dados das APIs carregados!');
        
      } catch (error) {
        console.error('❌ Erro ao buscar dados da API, usando dados simulados:', error);
        setApiData(prev => ({
          ...prev,
          clima: { temperatura: 27, umidade: 70, chuva: 0.2 },
          dengue: { casos_reais: 1500, alerta: "Amarelo" },
          regions: [
            { name: "Centro", cases: 245, risk: "high", color: "#e74c3c" },
            { name: "Zona Sul", cases: 312, risk: "very_high", color: "#c0392b" }
          ]
        }));
      }
    };

    fetchAPIData();
    const interval = setInterval(fetchAPIData, 30000);
    return () => clearInterval(interval);
  }, []);

  // 3. Sua simulação local (mantida como fallback)
  const initializeSimulation = () => {
    const vaccinated = Math.floor(settings.population * (settings.vaccinationRate / 100));
    const newData = {
      humans: settings.initialInfected,
      recovered: 0,
      vaccinated: vaccinated,
      mosquitoes: Math.floor(settings.initialInfected * 5),
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
      const realTemperature = apiData.clima ? apiData.clima.temperatura : settings.temperature;
      
      const tempFactor = Math.max(0.1, (realTemperature - 15) / 20);
      const transmissionFactor = settings.transmissionRate / 100;
      const vaccinationFactor = settings.vaccinationRate / 100;
      const recoveryFactor = settings.recoveryRate / 100;
      const interventionFactor = settings.interventionIntensity / 100;
      const mosquitoControlFactor = settings.mosquitoControl / 100;
      
      const randomFactor = 0.7 + Math.random() * 0.6;
      const seasonFactor = 0.8 + Math.sin(prevData.time / 60) * 0.4;

      const susceptiblePopulation = Math.max(0, 
        prevData.population - prevData.humans - prevData.recovered - prevData.vaccinated
      );

      const baseInfectionProbability = 0.0001;
      const infectionPressure = (prevData.mosquitoes / 1000) * transmissionFactor * tempFactor * seasonFactor;
      const dailyInfectionRate = baseInfectionProbability * infectionPressure * randomFactor;
      
      const newInfections = Math.floor(
        Math.min(
          susceptiblePopulation * dailyInfectionRate,
          susceptiblePopulation * 0.05
        ) * (1 - interventionFactor * 0.7)
      );

      const dailyRecoveries = Math.floor(
        prevData.humans * recoveryFactor * (0.8 + Math.random() * 0.4)
      );
      const actualRecoveries = Math.min(dailyRecoveries, prevData.humans);

      const immunityLoss = Math.floor(
        prevData.recovered * (1 / settings.immunityDuration) * (0.5 + Math.random())
      );

      const newVaccinations = Math.floor(
        (settings.population - prevData.vaccinated - prevData.humans) * 
        vaccinationFactor * 0.002 * randomFactor
      );

      const mosquitoBirthRate = tempFactor * 0.05 * seasonFactor;
      const naturalMosquitoDeathRate = 0.08;
      const controlMosquitoDeathRate = mosquitoControlFactor * 0.15;
      
      const newMosquitoes = Math.floor(
        prevData.mosquitoes * mosquitoBirthRate * randomFactor
      );
      
      const mosquitoDeaths = Math.floor(
        prevData.mosquitoes * (naturalMosquitoDeathRate + controlMosquitoDeathRate) * randomFactor
      );

      const interventionEffect = interventionFactor * randomFactor;

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

      let trend = 'stable';
      if (newInfections > actualRecoveries * 1.2) {
        trend = 'increasing';
      } else if (actualRecoveries > newInfections * 1.2) {
        trend = 'decreasing';
      }

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

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>📊 Painel de Controle - Simulação de Dengue</h2>
        <p className="simulation-time">
          Tempo de simulação: {simulationData.time} dias | 
          Tendência: {simulationData.trend === 'increasing' ? '📈 Aumentando' : 
                    simulationData.trend === 'decreasing' ? '📉 Diminuindo' : '➡️ Estável'}
          {apiData.realTime && ` | Dados em tempo real: ✅`}
        </p>
      </div>
      
      {/* SEÇÃO DE DADOS REAIS DAS APIS */}
      {apiData.dengue && (
        <div className="api-data-section">
          <h3>🌐 Dados em Tempo Real das APIs</h3>
          <div className="api-data-grid">
            <div className="api-data-card">
              <h4>📊 Situação Real da Dengue</h4>
              <div className="api-value">{apiData.dengue.casos_reais} casos</div>
              <div className={`api-alert ${apiData.dengue.alerta.toLowerCase()}`}>
                Alerta: {apiData.dengue.alerta}
              </div>
            </div>
            
            {apiData.clima && (
              <div className="api-data-card">
                <h4>🌤️ Clima em SP</h4>
                <div className="climate-data">
                  <div>🌡️ {apiData.clima.temperatura}°C</div>
                  <div>💧 {apiData.clima.umidade}%</div>
                  <div>🌧️ {apiData.clima.chuva}mm</div>
                </div>
              </div>
            )}
            
            {apiData.realTime && (
              <div className="api-data-card">
                <h4>🔄 Simulação Servidor</h4>
                <div className="realtime-data">
                  <div>👥 Infectados: {apiData.realTime.humanos_infectados}</div>
                  <div>🦟 Mosquitos: {apiData.realTime.mosquitos_infectados}</div>
                  <div>📈 Taxa: {(apiData.realTime.taxa_infeccao * 100).toFixed(1)}%</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* PAINEL INFO DENGUE ESTILO OFICIAL - NOVA SEÇÃO */}
      <div className="info-dengue-dashboard">
        {/* Painel de Métricas */}
        <PainelMetricas 
          simulationData={simulationData}
          apiData={apiData}
        />
        
        {/* Gráfico de Casos por Semana */}
        <CasosPorSemanaChart 
          simulationData={simulationData}
          apiData={apiData}
        />
        
        {/* Distribuição Demográfica */}
        <DistribuicaoDemografiaChart 
          simulationData={simulationData}
        />
      </div>

      {/* Seção de controles (mantida igual) */}
      <div className="simulation-controls">
        <h2>Controles da Simulação</h2>
        <div className="controls-grid">
          <div className="control-group">
            <label>População Total</label>
            <input
              type="range"
              min="1000"
              max="50000"
              step="1000"
              value={settings.population}
              onChange={(e) => updateSetting('population', parseInt(e.target.value))}
            />
            <span>{settings.population.toLocaleString()}</span>
          </div>
          
          <div className="control-group">
            <label>Taxa de Vacinação</label>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.vaccinationRate}
              onChange={(e) => updateSetting('vaccinationRate', parseInt(e.target.value))}
            />
            <span>{settings.vaccinationRate}%</span>
          </div>
          
          <div className="control-group">
            <label>Taxa de Transmissão</label>
            <input
              type="range"
              min="10"
              max="90"
              value={settings.transmissionRate}
              onChange={(e) => updateSetting('transmissionRate', parseInt(e.target.value))}
            />
            <span>{settings.transmissionRate}%</span>
          </div>
          
          <div className="control-group">
            <label>Controle de Mosquitos</label>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.mosquitoControl}
              onChange={(e) => updateSetting('mosquitoControl', parseInt(e.target.value))}
            />
            <span>{settings.mosquitoControl}%</span>
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