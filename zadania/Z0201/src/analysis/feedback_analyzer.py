def analyze_feedback(hub_responses: list) -> str:
    """
    Analizuje odpowiedzi z API huba, wyodrębniając błędy.
    Zwraca ustrukturyzowany tekst z błędami do przekazania modelowi.
    """
    errors = []
    for resp in hub_responses:
        if isinstance(resp, dict):
            code = resp.get("code", 0)
            msg = resp.get("message", "")
            
            # W hubie błędy mają ujemny kod, lub message wskazuje na fail
            if code < 0 or "error" in str(msg).lower() or "wrong" in str(msg).lower() or "budget" in str(msg).lower():
                item_id = resp.get("item_id", "unknown")
                errors.append(f"- Item ID: {item_id}, Code: {code}, Error: {msg}")

    if not errors:
        return "SUCCESS: Wszelkie klasyfikacje były poprawne."

    feedback = "ERROR FEEDBACK FROM HUB:\n" + "\n".join(errors)
    return feedback