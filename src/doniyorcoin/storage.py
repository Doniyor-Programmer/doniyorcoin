"""Persistence helpers for Doniyorcoin."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from .blockchain import Blockchain


DEFAULT_STATE_FILE = "doniyorcoin_state.json"


def load_blockchain(path: Optional[str] = None) -> Blockchain:
    """Load a blockchain from disk."""
    state_path = Path(path or DEFAULT_STATE_FILE)
    if not state_path.exists():
        return Blockchain()
    with state_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return Blockchain.from_dict(data)


def save_blockchain(blockchain: Blockchain, path: Optional[str] = None) -> None:
    """Persist a blockchain to disk."""
    state_path = Path(path or DEFAULT_STATE_FILE)
    os.makedirs(state_path.parent, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as f:
        json.dump(blockchain.to_dict(), f, indent=2)
