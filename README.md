# Doniyorcoin

Doniyorcoin is a toy cryptocurrency inspired by the high level ideas of
Bitcoin. It implements a very small proof-of-work blockchain with mining
rewards, wallet generation and a command line interface for experimenting
locally. The implementation is **not** meant for production use, but it is a
good starting point for learning about how blockchains operate.

## Features

- Simple blockchain with proof-of-work mining
- Wallet generation with deterministic address derivation
- Ability to create and queue transactions
- Mining rewards credited to miners when blocks are produced
- JSON persistence so you can stop and resume the chain state

## Quick start

```bash
# Create and enter a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate

# Install Doniyorcoin in editable mode
pip install -e .

# Initialize the blockchain state
python -m doniyorcoin init --state state.json --difficulty 3 --reward 50

# Create two wallets
python -m doniyorcoin create-wallet --output alice.json
python -m doniyorcoin create-wallet --output bob.json

# Check balances (both start at 0)
python -m doniyorcoin --state state.json balance $(jq -r '.address' alice.json)
python -m doniyorcoin --state state.json balance $(jq -r '.address' bob.json)
```

Create a transaction from Alice to Bob (replace the command substitution if you
are on a shell without `jq`):

```bash
ALICE_KEY=$(jq -r '.private_key' alice.json)
BOB_ADDRESS=$(jq -r '.address' bob.json)
python -m doniyorcoin --state state.json transfer "$ALICE_KEY" "$BOB_ADDRESS" 5
```

Mine the pending transactions and collect the reward:

```bash
MINER_ADDRESS=$(jq -r '.address' alice.json)
python -m doniyorcoin --state state.json mine "$MINER_ADDRESS"
```

Inspect the blockchain and verify its integrity:

```bash
python -m doniyorcoin --state state.json show-chain
python -m doniyorcoin --state state.json validate
```

## Security notice

The cryptography used by Doniyorcoin is intentionally simplified to keep the
project approachable. Keys and signatures are **not** secure, and the
implementation should only ever be used for experimentation and learning.

## License

This project is released into the public domain. Have fun exploring!
