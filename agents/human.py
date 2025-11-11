# ============================================================
# Arquivo: agents/human.py
# Descrição: Define o agente Humano do modelo de simulação da dengue.
# Autor: Renato Jorge Correia Alpalhão
# Projeto de Conclusão de Curso - SENAC
# ============================================================

from mesa import Agent
import random

class Human(Agent):
    """
    Representa um humano na simulação.
    Cada humano pode se infectar, se recuperar ou ser vacinado.
    """

    def __init__(self, unique_id, model, casa=(0, 0), trabalho=(0, 0)):
        super().__init__(unique_id, model)
        
        # --- Posições fixas (para simular deslocamento) ---
        self.casa = casa
        self.trabalho = trabalho

        # --- Estado de saúde ---
        self.infectado = False
        self.recuperado = False
        self.vacinado = False
        self.dias_infectado = 0

        # --- Movimento ---
        self.pos = None  # será definido quando adicionado ao grid

    # ------------------------------------------------------------
    # Função auxiliar: infectar
    # ------------------------------------------------------------
    def infectar(self):
        """Infecta o humano, caso não esteja vacinado nem recuperado."""
        if not self.vacinado and not self.recuperado:
            self.infectado = True
            self.dias_infectado = 0

    # ------------------------------------------------------------
    # Passo da simulação
    # ------------------------------------------------------------
    def step(self):
        """
        Define o comportamento do humano em cada passo da simulação:
        - Pode se mover aleatoriamente;
        - Pode se recuperar da infecção;
        - Pode ser infectado por mosquitos próximos.
        """

        # --- 1. Movimento aleatório simples ---
        if random.random() < 0.2:  # 20% de chance de se mover
            vizinhos = self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=False
            )
            if vizinhos:
                nova_pos = random.choice(vizinhos)
                self.model.grid.move_agent(self, nova_pos)

        # --- 2. Se infectado, contabiliza dias e recuperação ---
        if self.infectado:
            self.dias_infectado += 1

            # Recuperação após 7 dias
            if self.dias_infectado >= 7:
                self.infectado = False
                self.recuperado = True

        # --- 3. Verifica mosquitos próximos para contágio ---
        celula = self.model.grid.get_cell_list_contents([self.pos])
        mosquitos = [a for a in celula if a.__class__.__name__ == "Mosquito"]

        for mosquito in mosquitos:
            # Probabilidade de contágio depende da taxa global
            if getattr(mosquito, "infectado", False):
                if random.random() < self.model.prob_contagio_humano:
                    self.infectar()
                    break

    # ------------------------------------------------------------
    # Representação textual (para depuração)
    # ------------------------------------------------------------
    def __repr__(self):
        estado = "V" if self.vacinado else "R" if self.recuperado else "I" if self.infectado else "S"
        return f"Human({self.unique_id}, estado={estado}, pos={self.pos})"
