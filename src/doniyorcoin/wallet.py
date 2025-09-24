"""Wallet utilities for Doniyorcoin."""

from __future__ import annotations

import json
import os
import secrets
from dataclasses import dataclass
from typing import Dict

import hashlib

from .transaction import Transaction


@dataclass
class Wallet:
    """A Doniyorcoin wallet consisting of a private key and derived address."""

    private_key: str
    public_key: str
    address: str

    @classmethod
    def create(cls) -> "Wallet":
        private_key = secrets.token_hex(32)
        private_bytes = bytes.fromhex(private_key)
        public_key = hashlib.sha256(private_bytes).hexdigest()
        address = hashlib.sha256(public_key.encode()).hexdigest()
        return cls(private_key=private_key, public_key=public_key, address=address)

    @classmethod
    def from_private_key(cls, private_key: str) -> "Wallet":
        private_bytes = bytes.fromhex(private_key)
        public_key = hashlib.sha256(private_bytes).hexdigest()
        address = hashlib.sha256(public_key.encode()).hexdigest()
        return cls(private_key=private_key, public_key=public_key, address=address)

    @staticmethod
    def load(path: str) -> "Wallet":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Wallet(**data)

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "private_key": self.private_key,
                    "public_key": self.public_key,
                    "address": self.address,
                },
                f,
                indent=2,
            )

    def create_transaction(self, to_address: str, amount: float) -> Transaction:
        transaction = Transaction(from_address=self.address, to_address=to_address, amount=amount)
        transaction.public_key = self.public_key
        transaction.sign(self.private_key)
        return transaction

    @staticmethod
    def export(wallet: "Wallet") -> Dict[str, str]:
        return {
            "private_key": wallet.private_key,
            "public_key": wallet.public_key,
            "address": wallet.address,
        }
