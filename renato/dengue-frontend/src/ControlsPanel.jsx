import React from "react";

export default function ControlsPanel({ params, setParams, onReset, onStart, onStop, onTurbo }) {

  function update(key, value) {
    setParams(prev => ({ ...prev, [key]: value }));
  }

  return (
    <div style={{
      padding: "15px",
      background: "#1d1f23",
      color: "white",
      borderRadius: "10px",
      marginBottom: "10px"
    }}>
      <h3>⚙️ Controle da Simulação</h3>

      {/* HUMANOS */}
      <label>Humanos: {params.num_humanos}</label>
      <input type="range" min={50} max={1000} value={params.num_humanos}
        onChange={e => update("num_humanos", parseInt(e.target.value))} />

      {/* MOSQUITOS */}
      <label>Mosquitos: {params.num_mosquitos}</label>
      <input type="range" min={100} max={2000} value={params.num_mosquitos}
        onChange={e => update("num_mosquitos", parseInt(e.target.value))} />

      {/* VACINADOS */}
      <label>% Vacinados: {params.percentual_vacinados}%</label>
      <input type="range" min={0} max={100} value={params.percentual_vacinados}
        onChange={e => update("percentual_vacinados", parseInt(e.target.value))} />

      {/* TAXA DE INFECÇÃO */}
      <label>Taxa Infecção Inicial: {params.taxa_infeccao.toFixed(2)}</label>
      <input type="range" min={0} max={1} step={0.01} value={params.taxa_infeccao}
        onChange={e => update("taxa_infeccao", parseFloat(e.target.value))} />

      {/* PROBABILIDADE HUMANO */}
      <label>Probabilidade de Contágio (picada): {params.prob_contagio_humano.toFixed(2)}</label>
      <input type="range" min={0} max={1} step={0.01} value={params.prob_contagio_humano}
        onChange={e => update("prob_contagio_humano", parseFloat(e.target.value))} />

      {/* VIDA DO MOSQUITO */}
      <label>Vida Média do Mosquito: {params.vida_media_mosquito} dias</label>
      <input type="range" min={5} max={40} value={params.vida_media_mosquito}
        onChange={e => update("vida_media_mosquito", parseInt(e.target.value))} />

      {/* BOTÕES */}
      <div style={{ marginTop: "15px" }}>
        <button onClick={onStart} style={btn}>▶ Iniciar</button>
        <button onClick={onStop} style={btn}>⏸ Pausar</button>
        <button onClick={onReset} style={btn}>⏹ Resetar</button>
        <button onClick={onTurbo} style={btn}>⚡ Turbo 100 dias</button>
      </div>
    </div>
  );
}

const btn = {
  marginRight: "10px",
  padding: "8px 14px",
  background: "#333",
  color: "white",
  border: "1px solid #555",
  borderRadius: "5px",
  cursor: "pointer"
};
