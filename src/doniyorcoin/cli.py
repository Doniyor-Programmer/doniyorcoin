"""Command line interface for interacting with Doniyorcoin."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .blockchain import Blockchain
from .storage import DEFAULT_STATE_FILE, load_blockchain, save_blockchain
from .wallet import Wallet


def _load_blockchain(state_path: str) -> Blockchain:
    return load_blockchain(state_path)


def cmd_init(args: argparse.Namespace) -> None:
    blockchain = Blockchain(difficulty=args.difficulty, mining_reward=args.reward)
    save_blockchain(blockchain, args.state)
    print(f"Initialized new Doniyorcoin blockchain at {args.state}")


def cmd_create_wallet(args: argparse.Namespace) -> None:
    wallet = Wallet.create()
    if args.output:
        wallet.save(args.output)
        print(f"Wallet saved to {args.output}")
    else:
        print(json.dumps(Wallet.export(wallet), indent=2))


def cmd_balance(args: argparse.Namespace) -> None:
    blockchain = _load_blockchain(args.state)
    balance = blockchain.get_balance_of_address(args.address)
    print(f"Balance for {args.address}: {balance:.4f} DYC")


def cmd_transfer(args: argparse.Namespace) -> None:
    blockchain = _load_blockchain(args.state)
    wallet = Wallet.from_private_key(args.private_key)
    transaction = wallet.create_transaction(args.to, args.amount)
    blockchain.add_transaction(transaction)
    save_blockchain(blockchain, args.state)
    print("Transaction queued for mining.")


def cmd_mine(args: argparse.Namespace) -> None:
    blockchain = _load_blockchain(args.state)
    block = blockchain.mine_pending_transactions(args.miner)
    save_blockchain(blockchain, args.state)
    print(f"Mined block #{block.index} with hash {block.hash}")


def cmd_show_chain(args: argparse.Namespace) -> None:
    blockchain = _load_blockchain(args.state)
    data: Any = blockchain.to_dict()
    json.dump(data, sys.stdout, indent=2)
    print()


def cmd_validate(args: argparse.Namespace) -> None:
    blockchain = _load_blockchain(args.state)
    print("Chain valid" if blockchain.is_chain_valid() else "Chain invalid")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interact with the Doniyorcoin blockchain")
    parser.set_defaults(func=None)
    parser.add_argument(
        "--state",
        default=DEFAULT_STATE_FILE,
        help="Path to the blockchain state file (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(title="commands")

    init_parser = subparsers.add_parser("init", help="Initialize a blockchain state file")
    init_parser.add_argument("--difficulty", type=int, default=3, help="Proof-of-work difficulty")
    init_parser.add_argument("--reward", type=float, default=50.0, help="Mining reward")
    init_parser.set_defaults(func=cmd_init)

    wallet_parser = subparsers.add_parser("create-wallet", help="Generate a new wallet")
    wallet_parser.add_argument("--output", help="File path to save the wallet JSON")
    wallet_parser.set_defaults(func=cmd_create_wallet)

    balance_parser = subparsers.add_parser("balance", help="Show balance for an address")
    balance_parser.add_argument("address", help="Address to inspect")
    balance_parser.set_defaults(func=cmd_balance)

    transfer_parser = subparsers.add_parser("transfer", help="Create a new transaction")
    transfer_parser.add_argument("private_key", help="Sender private key")
    transfer_parser.add_argument("to", help="Recipient address")
    transfer_parser.add_argument("amount", type=float, help="Amount to transfer")
    transfer_parser.set_defaults(func=cmd_transfer)

    mine_parser = subparsers.add_parser("mine", help="Mine pending transactions")
    mine_parser.add_argument("miner", help="Miner address to receive the reward")
    mine_parser.set_defaults(func=cmd_mine)

    chain_parser = subparsers.add_parser("show-chain", help="Display the full blockchain")
    chain_parser.set_defaults(func=cmd_show_chain)

    validate_parser = subparsers.add_parser("validate", help="Validate the blockchain integrity")
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.func is None:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
