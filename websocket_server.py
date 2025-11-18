import asyncio
import json
import websockets
import threading
import time
from datetime import datetime

from dengue_model_ml import DengueModelML

class SimulationServer:
    def __init__(self):
        self.model = None
        self.clients = set()
        self.running = False
        self.simulation_thread = None
        
    def start_simulation(self):
        """Inicia a simulação em thread separada"""
        if not self.model:
            self.model = DengueModelML(
                num_humanos=200,
                num_mosquitos=300,
                percentual_vacinados=10,
                width=40,
                height=40
            )
            print("🎯 Modelo de simulação criado!")
        
        if not self.running:
            self.running = True
            self.simulation_thread = threading.Thread(target=self._run_simulation)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()
            print("▶️ Simulação iniciada!")
    
    def _run_simulation(self):
        """Executa a simulação"""
        print("🔄 Thread de simulação iniciada...")
        while self.running and self.model:
            try:
                if not self.model.paused:
                    self.model.step()
                
                # Envia dados para clientes
                data = self._get_simulation_data()
                asyncio.run(self._broadcast(data))
                
                time.sleep(0.5)  # Controla velocidade
                
            except Exception as e:
                print(f"❌ Erro na simulação: {e}")
                time.sleep(1)
    
    def _get_simulation_data(self):
        """Obtém dados da simulação"""
        if not self.model:
            return {"error": "Modelo não inicializado"}
        
        try:
            return self.model.get_simulation_data()
        except Exception as e:
            return {"error": str(e)}
    
    async def _broadcast(self, data):
        """Envia dados para todos os clientes"""
        if not self.clients:
            return
            
        message = json.dumps(data, default=str)
        for client in self.clients.copy():
            try:
                await client.send(message)
            except:
                self.clients.remove(client)

# Instância global
server = SimulationServer()

async def handler(websocket):
    """Manipula conexões WebSocket"""
    server.clients.add(websocket)
    print(f"🔗 Cliente conectado! Total: {len(server.clients)}")
    
    # INICIA SIMULAÇÃO AUTOMATICAMENTE NO PRIMEIRO CLIENTE
    if not server.running:
        server.start_simulation()
    
    try:
        # Envia mensagem de boas-vindas
        await websocket.send(json.dumps({
            "type": "connection_established",
            "message": "Conectado ao servidor de simulação",
            "timestamp": datetime.now().isoformat()
        }))
        
        # Mantém conexão
        await websocket.wait_closed()
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
    finally:
        server.clients.remove(websocket)
        print(f"🔌 Cliente desconectado. Total: {len(server.clients)}")

async def main():
    """Função principal"""
    print("=" * 50)
    print("🦟 Servidor de Simulação de Dengue")
    print("📍 WebSocket: ws://localhost:8765")
    print("📍 Aguardando conexões...")
    print("=" * 50)
    
    # Inicia servidor WebSocket
    async with websockets.serve(handler, "localhost", 8765):
        print("🚀 Servidor WebSocket rodando!")
        await asyncio.Future()  # Executa forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Servidor encerrado")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")