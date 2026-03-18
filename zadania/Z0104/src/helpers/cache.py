# -*- coding: utf-8 -*-

import json
import hashlib
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path(__file__).parent.parent.parent / "cache"

def get_cache_key(data: Any) -> str:
    """Generate a unique MD5 hash for given data (must be JSON serializable)."""
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
    return hashlib.md5(serialized.encode("utf-8")).hexdigest()

def get_from_cache(key: str) -> Optional[Any]:
    """Retrieve data from the file cache if it exists."""
    cache_file = CACHE_DIR / f"{key}.json"
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_to_cache(key: str, data: Any) -> None:
    """Save data to the file cache."""
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
    cache_file = CACHE_DIR / f"{key}.json"
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
