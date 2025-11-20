import asyncio
import json
import websockets
import threading
import time
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
import random

# Import suas APIs
from api.clima import obter_clima_sao_paulo_inmet
from api.dengue_api import obter_dados_dengue_sp
from api.data_loader import get_densidade_fator_por_coordenada

# Tente importar o modelo, mas tenha fallback
try:
    from dengue_model_ml import DengueModelML
    HAS_MODEL = True
except ImportError:
    print("⚠️  dengue_model_ml não encontrado, usando simulação básica")
    HAS_MODEL = False

class SimulationServer:
    def __init__(self):
        self.model = None
        self.clients = set()
        self.running = False
        self.simulation_thread = None
        
    def start_simulation(self):
        """Inicia a simulação em thread separada"""
        if not self.model and HAS_MODEL:
            try:
                self.model = DengueModelML(
                    num_humanos=200,
                    num_mosquitos=300,
                    percentual_vacinados=10,
                    width=40,
                    height=40
                )
                print("🎯 Modelo de simulação ML criado!")
            except Exception as e:
                print(f"❌ Erro criando modelo: {e}")
                HAS_MODEL = False
        
        if not self.running:
            self.running = True
            self.simulation_thread = threading.Thread(target=self._run_simulation)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            print("▶️ Simulação iniciada!")
    
    def _run_simulation(self):
        """Executa a simulação"""
        print("🔄 Thread de simulação iniciada...")
        step_count = 0
        
        while self.running:
            try:
                # Dados de simulação (real ou simulados)
                simulation_data = self._get_simulation_data(step_count)
                
                # Envia dados para clientes via WebSocket
                asyncio.run(self._broadcast(simulation_data))
                
                step_count += 1
                time.sleep(1)  # 1 segundo entre steps
                
            except Exception as e:
                print(f"❌ Erro na simulação: {e}")
                time.sleep(2)
    
    def _get_simulation_data(self, step_count):
        """Obtém dados da simulação real ou gera dados simulados"""
        if self.model and HAS_MODEL:
            try:
                return self.model.get_simulation_data()
            except Exception as e:
                print(f"⚠️  Erro no modelo, usando dados simulados: {e}")
        
        # Fallback: dados simulados
        return {
            "step": step_count,
            "timestamp": datetime.now().isoformat(),
            "humanos_saudaveis": random.randint(150, 180),
            "humanos_infectados": random.randint(20, 50),
            "mosquitos_saudaveis": random.randint(200, 280),
            "mosquitos_infectados": random.randint(20, 40),
            "taxa_infeccao": round(random.uniform(0.1, 0.4), 2),
            "type": "simulation_data"
        }
    
    async def _broadcast(self, data):
        """Envia dados para todos os clientes WebSocket"""
        if not self.clients:
            return
            
        message = json.dumps(data, default=str)
        disconnected = []
        
        for client in self.clients:
            try:
                await client.send(message)
            except:
                disconnected.append(client)
        
        # Remove clientes desconectados
        for client in disconnected:
            self.clients.remove(client)

# Instância global do servidor
server = SimulationServer()

# Configuração Flask para APIs HTTP
app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check da API"""
    return jsonify({
        "status": "Servidor integrado funcionando!", 
        "version": "2.0",
        "websocket_clients": len(server.clients),
        "simulation_running": server.running
    })

@app.route('/api/clima', methods=['GET'])
def get_clima():
    """Retorna dados climáticos simulados"""
    try:
        clima = obter_clima_sao_paulo_inmet()
        return jsonify(clima)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dengue', methods=['GET'])
def get_dengue():
    """Retorna dados de dengue simulados"""
    try:
        dengue = obter_dados_dengue_sp()
        return jsonify(dengue)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dengue/regions', methods=['GET'])
def get_regions():
    """Retorna dados por região de SP"""
    regions = [
        {"name": "Centro", "cases": random.randint(20, 80), "risk": "high", "color": "#e74c3c"},
        {"name": "Zona Sul", "cases": random.randint(40, 120), "risk": "very_high", "color": "#c0392b"},
        {"name": "Zona Norte", "cases": random.randint(15, 60), "risk": "medium", "color": "#e67e22"},
        {"name": "Zona Leste", "cases": random.randint(25, 90), "risk": "high", "color": "#e74c3c"},
        {"name": "Zona Oeste", "cases": random.randint(10, 45), "risk": "low", "color": "#f1c40f"}
    ]
    return jsonify(regions)

@app.route('/api/simulation/start', methods=['POST'])
def start_simulation():
    """Inicia a simulação"""
    server.start_simulation()
    return jsonify({"message": "Simulação iniciada", "running": server.running})

@app.route('/api/simulation/status', methods=['GET'])
def simulation_status():
    """Status da simulação"""
    return jsonify({
        "running": server.running,
        "clients": len(server.clients),
        "has_model": HAS_MODEL
    })

# Handler WebSocket
async def websocket_handler(websocket):
    """Manipula conexões WebSocket"""
    server.clients.add(websocket)
    print(f"🔗 Cliente WebSocket conectado! Total: {len(server.clients)}")
    
    # Inicia simulação automaticamente no primeiro cliente
    if not server.running:
        server.start_simulation()
    
    try:
        # Mensagem de boas-vindas
        await websocket.send(json.dumps({
            "type": "connection_established",
            "message": "Conectado ao servidor integrado",
            "endpoints": {
                "http": "http://localhost:5000/api",
                "websocket": "ws://localhost:8765"
            },
            "timestamp": datetime.now().isoformat()
        }))
        
        # Mantém conexão
        await websocket.wait_closed()
        
    except Exception as e:
        print(f"❌ Erro WebSocket: {e}")
    finally:
        server.clients.remove(websocket)
        print(f"🔌 Cliente desconectado. Total: {len(server.clients)}")

async def start_websocket_server():
    """Inicia servidor WebSocket"""
    print("🔄 Iniciando WebSocket na porta 8765...")
    async with websockets.serve(websocket_handler, "localhost", 8765):
        print("✅ WebSocket: ws://localhost:8765")
        await asyncio.Future()  # Executa forever

def start_flask_server():
    """Inicia servidor Flask"""
    print("🔄 Iniciando API HTTP na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

async def main():
    """Função principal integrada"""
    print("=" * 60)
    print("🦟 SERVIDOR INTEGRADO - DengueSimulMESA")
    print("📍 WebSocket: ws://localhost:8765")
    print("📍 API HTTP:  http://localhost:5000/api")
    print("📍 Aguardando conexões...")
    print("=" * 60)
    
    # Inicia Flask em thread separada
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Aguarda Flask iniciar
    time.sleep(2)
    
    # Inicia WebSocket
    await start_websocket_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")