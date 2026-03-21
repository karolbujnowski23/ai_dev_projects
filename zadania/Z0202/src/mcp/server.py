import json
from mcp.server.fastmcp import FastMCP
from src.helpers.logger import log

from src.api import (
    get_board_image_url,
    get_target_image_url,
    analyze_board_image,
    compare_board_states,
    rotate_tile as api_rotate_tile,
    reset_board as api_reset_board
)

# Initialize FastMCP Server
mcp_server = FastMCP("electricity-mcp-server")

@mcp_server.tool()
def get_board_state() -> str:
    """
    Pobiera aktualny stan planszy oraz stan docelowy z serwerów jako listy opisowe.
    Wykorzystuje AI (gemini-3.1-pro-preview) do analizy obrazka.
    """
    log.info("Pobieranie stanu planszy...")
    try:
        target_url = get_target_image_url()
        current_url = get_board_image_url()
        
        target_state = analyze_board_image(target_url)
        current_state = analyze_board_image(current_url)
        
        return json.dumps({
            "status": "success",
            "target_state": target_state,
            "current_state": current_state
        }, ensure_ascii=False)
    except Exception as e:
        log.error(f"Error in get_board_state: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})

@mcp_server.tool()
def calculate_rotations(target_state: str, current_state: str) -> str:
    """
    Oblicza wymaganą liczbę obrotów (o 90 stopni w prawo) dla poszczególnych pól.
    Wykorzystuje AI (gemini-2.5-flash) do wyciągnięcia tych wartości na podstawie podanych stanów tekstowych.
    
    Args:
        target_state: Docelowy stan pól (tekst np. z get_board_state).
        current_state: Bieżący stan pól (tekst np. z get_board_state).
    """
    log.info("Obliczanie rotacji dla zadanych stanów...")
    try:
        rotations_json = compare_board_states(target_state, current_state)
        # Parse w celu walidacji i zwrócenia uporządkowanego formatu
        try:
            parsed_rotations = json.loads(rotations_json)
        except Exception:
            parsed_rotations = rotations_json

        return json.dumps({
            "status": "success",
            "rotations": parsed_rotations
        }, ensure_ascii=False)
    except Exception as e:
        log.error(f"Error in calculate_rotations: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})

@mcp_server.tool()
def rotate_tile(tile_id: str) -> str:
    """
    Obraca wybraną płytkę (w prawo o 90 stopni) przez wysłanie zapytania do API.
    Dozwolone formaty id: "1x1", "1x2", "1x3", "2x1", "2x2", "2x3", "3x1", "3x2", "3x3".
    
    Args:
        tile_id: Identyfikator pola.
    """
    log.info(f"Obracanie płytki: {tile_id}")
    try:
        result = api_rotate_tile(tile_id)
        return json.dumps({
            "status": "success",
            "response": result
        }, ensure_ascii=False)
    except Exception as e:
        log.error(f"Error in rotate_tile: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})

@mcp_server.tool()
def reset_board() -> str:
    """
    Resetuje planszę do układu początkowego.
    Warto wywołać jeżeli układy stały się niesynchroniczne z zamierzeniami.
    """
    log.info("Resetowanie planszy...")
    try:
        result = api_reset_board()
        return json.dumps({
            "status": "success",
            "message": result
        }, ensure_ascii=False)
    except Exception as e:
        log.error(f"Error in reset_board: {str(e)}")
        return json.dumps({"status": "error", "message": str(e)})
