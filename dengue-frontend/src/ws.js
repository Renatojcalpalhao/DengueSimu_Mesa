// src/ws.js
const WS_URL = "ws://localhost:8765";

export function connectWS(onMessageCallback) {
  const ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    console.log("🌐 WebSocket conectado ao servidor Python");
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessageCallback(data);   // envia snapshot ao App.jsx
    } catch (err) {
      console.error("Erro ao interpretar mensagem:", err);
    }
  };

  ws.onclose = () => {
    console.log("🔌 WebSocket desconectado. Tentando reconectar em 3s...");
    setTimeout(() => connectWS(onMessageCallback), 3000);
  };

  return ws;
}
