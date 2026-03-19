import tiktoken

def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Liczy tokeny w podanym tekście."""
    encoding = tiktoken.get_encoding(model)
    return len(encoding.encode(text))

def is_within_limit(prompt: str, max_tokens: int = 100) -> bool:
    """Sprawdza, czy prompt mieści się w limitach."""
    return count_tokens(prompt) <= max_tokens
