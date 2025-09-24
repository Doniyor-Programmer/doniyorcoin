"""Transactions for Doniyorcoin."""

from __future__ import annotations

import hmac
import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Transaction:
    """A simple transaction between two addresses."""

    from_address: Optional[str]
    to_address: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    public_key: Optional[str] = None
    signature: Optional[str] = None

    def payload(self) -> str:
        """Return the transaction payload used for signing."""
        return f"{self.from_address}->{self.to_address}:{self.amount}:{self.timestamp}"

    def sign(self, private_key: str) -> None:
        """Sign the transaction using a private key.

        The signing approach used here is intentionally simple and not secure for
        real-world usage. It is suitable only for educational demonstrations.
        """

        private_bytes = bytes.fromhex(private_key)
        self.public_key = hashlib.sha256(private_bytes).hexdigest()
        expected_address = hashlib.sha256(self.public_key.encode()).hexdigest()
        if self.from_address is None:
            self.from_address = expected_address
        elif self.from_address != expected_address:
            raise ValueError("Private key does not match the from_address")

        message = self.payload().encode()
        key = bytes.fromhex(self.public_key)
        self.signature = hmac.new(key, message, hashlib.sha256).hexdigest()

    def is_valid(self) -> bool:
        """Check if the transaction is valid."""
        if self.from_address == self.to_address:
            return False
        if self.amount <= 0:
            return False
        if self.from_address is None:
            # Reward transaction
            return True
        if not self.signature or not self.public_key:
            return False
        expected_address = hashlib.sha256(self.public_key.encode()).hexdigest()
        if expected_address != self.from_address:
            return False
        message = self.payload().encode()
        expected_signature = hmac.new(bytes.fromhex(self.public_key), message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_signature, self.signature)

    def to_dict(self) -> dict:
        """Serialize the transaction to a dictionary."""
        return {
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "public_key": self.public_key,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Deserialize a transaction from a dictionary."""
        return cls(
            from_address=data.get("from_address"),
            to_address=data["to_address"],
            amount=data["amount"],
            timestamp=data.get("timestamp", time.time()),
            public_key=data.get("public_key"),
            signature=data.get("signature"),
        )
