import logging

logger = logging.getLogger(__name__)

class BudgetManager:
    """Monitoruje wydatki (PP) i stan procesu."""
    
    def __init__(self, max_budget: float = 1.5):
        self.max_budget = max_budget
        self.current_cost = 0.0

    def add_cost(self, cost: float):
        """Dodaje koszt do aktualnego bilansu."""
        self.current_cost += cost
        logger.info(f"Updated cost: {self.current_cost:.2f} PP / {self.max_budget:.2f} PP")

    def is_budget_exceeded(self) -> bool:
        """Zwraca True, jeśli budżet został przekroczony."""
        return self.current_cost >= self.max_budget

    def reset(self):
        """Resetuje licznik kosztów."""
        self.current_cost = 0.0
        logger.info("Budget reset to 0.0 PP.")
