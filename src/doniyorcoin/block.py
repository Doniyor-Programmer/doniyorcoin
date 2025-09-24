"""Block representation for Doniyorcoin."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import List

from .transaction import Transaction


@dataclass
class Block:
    """A single block in the Doniyorcoin blockchain."""

    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate the block hash."""
        block_contents = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        block_string = json.dumps(block_contents, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine(self, difficulty: int) -> None:
        """Perform a simple proof-of-work."""
        prefix = "0" * difficulty
        while not self.hash.startswith(prefix):
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> dict:
        """Serialize the block to a dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        """Deserialize a block from a dictionary."""
        transactions = [Transaction.from_dict(tx) for tx in data["transactions"]]
        block = cls(
            index=data["index"],
            timestamp=data["timestamp"],
            transactions=transactions,
            previous_hash=data["previous_hash"],
            nonce=data.get("nonce", 0),
        )
        block.hash = data.get("hash", block.calculate_hash())
        return block
