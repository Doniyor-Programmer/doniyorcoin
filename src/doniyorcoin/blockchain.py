"""Blockchain implementation for Doniyorcoin."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List

from .block import Block
from .transaction import Transaction


@dataclass
class Blockchain:
    """A minimal blockchain with proof-of-work."""

    difficulty: int = 3
    mining_reward: float = 50.0
    chain: List[Block] = field(default_factory=list)
    pending_transactions: List[Transaction] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.chain:
            self.chain.append(self._create_genesis_block())

    def _create_genesis_block(self) -> Block:
        return Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
        )

    @property
    def latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, transaction: Transaction) -> None:
        if not transaction.is_valid():
            raise ValueError("Cannot add invalid transaction to the chain")
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address: str) -> Block:
        reward_tx = Transaction(from_address=None, to_address=miner_address, amount=self.mining_reward)
        self.pending_transactions.append(reward_tx)

        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.latest_block.hash,
        )
        block.mine(self.difficulty)
        self.chain.append(block)
        self.pending_transactions.clear()
        return block

    def get_balance_of_address(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.from_address == address:
                    balance -= transaction.amount
                if transaction.to_address == address:
                    balance += transaction.amount
        for transaction in self.pending_transactions:
            if transaction.from_address == address:
                balance -= transaction.amount
        return balance

    def is_chain_valid(self) -> bool:
        if not self.chain:
            return False
        for index in range(1, len(self.chain)):
            current = self.chain[index]
            previous = self.chain[index - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
            for transaction in current.transactions:
                if not transaction.is_valid():
                    return False
        return True

    def to_dict(self) -> dict:
        return {
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward,
            "chain": [block.to_dict() for block in self.chain],
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Blockchain":
        chain = [Block.from_dict(block_data) for block_data in data.get("chain", [])]
        pending = [Transaction.from_dict(tx) for tx in data.get("pending_transactions", [])]
        blockchain = cls(
            difficulty=data.get("difficulty", 3),
            mining_reward=data.get("mining_reward", 50.0),
            chain=chain,
            pending_transactions=pending,
        )
        if not blockchain.chain:
            blockchain.chain.append(blockchain._create_genesis_block())
        return blockchain
