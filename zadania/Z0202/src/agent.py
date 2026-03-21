from src.helpers.logger import log
import time
from src.prompts.instructions import GROUND_TRUTH
from src.api import (
    get_board_image_url,
    analyze_board_image,
    compare_board_states,
    rotate_tile,
    reset_board
)

class Agent:
    def __init__(self, name: str = "ElectricityAgent"):
        self.name = name

    async def run(self, task: str):
        """
        Main execution loop for the agent solving Z0202 electricity puzzle.
        """
        log.info(f"[{self.name}] Rozpoczynam zadanie: {task}")
        log.info("Resetuję planszę do stanu początkowego...")
        reset_board()
        time.sleep(2)  # Krótkie oczekiwanie po resecie na wygenerowanie planszy
        
        url = get_board_image_url()
        log.info(f"Pobieranie i analiza obrazu z: {url}")
        
        max_attempts = 3
        
        for attempt in range(max_attempts):
            log.info(f"--- Próba {attempt+1}/{max_attempts} ---")
            
            # 1. Analiza (Vision + Pillow)
            current_state = analyze_board_image(url)
            log.info(f"Rozpoznany stan: {current_state}")
            
            # 2. Obliczenia
            rotations = compare_board_states(GROUND_TRUTH, current_state)
            log.info(f"Wymagane rotacje (o 90 st. w prawo): {rotations}")
            
            total_rotations = sum(rotations.values())
            if total_rotations == 0:
                log.info("Z żadnych rotacji nie wynika, że coś trzeba zmienić. Czyżby rozwiązane, lub AI nie złapało detalu?")
            
            # 3. Wykonywanie akcji API
            got_flag = False
            for tile_id, rot_count in rotations.items():
                if rot_count > 0:
                    for _ in range(rot_count):
                        log.info(f"Obracam kafelek: {tile_id}")
                        resp = rotate_tile(tile_id)
                        
                        message = resp.get("message", "")
                        if "FLG:" in message or "{FLG:" in str(resp):
                            log.info("!!! ZNALEZIONO FLAGĘ !!!")
                            log.info(f"Flaga: {message}")
                            got_flag = True
                            break
                        time.sleep(0.5)
                if got_flag: break
                
            if got_flag:
                return  # Zakończenie sukcesem
            else:
                log.info("Flaga nie została zwrócona po wykonaniu zaplanowanych obrotów. Aktualizacja i ponowna weryfikacja.")
                time.sleep(2)
        
        log.warning("Przekroczono maksymalną liczbę prób. Prawdopodobnie model Vision halucynuje.")
