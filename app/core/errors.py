from __future__ import annotations

from typing import Any, Dict, Optional


def err(code: str, message: str, *, details: Optional[Any] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        payload["details"] = details
    return payload
