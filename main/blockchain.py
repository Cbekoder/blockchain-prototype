import time
import hashlib
import json
import random
from .encryption import custom_encrypt, custom_decrypt

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return custom_encrypt(hashlib.sha256(block_string.encode()).hexdigest())

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2
        self.pending_transactions = []
        self.mining_reward = 10
        self.validators = {}
        self.lightning_channels = {}

    def create_genesis_block(self):
        return Block(0, [], int(time.time()), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, recipient, amount):
        self.pending_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })

    def mine_pending_transactions(self, miner_address):
        block = Block(len(self.chain), self.pending_transactions, int(time.time()), self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        self.chain.append(block)
        self.pending_transactions = [
            {"sender": "network", "recipient": miner_address, "amount": self.mining_reward}
        ]

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction['sender'] == address:
                    balance -= transaction['amount']
                if transaction['recipient'] == address:
                    balance += transaction['amount']
        return balance

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def add_validator(self, address, stake):
        self.validators[address] = stake

    def remove_validator(self, address):
        if address in self.validators:
            del self.validators[address]

    def choose_validator(self):
        total_stake = sum(self.validators.values())
        target = random.uniform(0, total_stake)
        current_stake = 0
        for validator, stake in self.validators.items():
            current_stake += stake
            if current_stake >= target:
                return validator
        return None

    def open_lightning_channel(self, party1, party2, amount):
        channel_id = f"{party1}-{party2}"
        self.lightning_channels[channel_id] = {party1: amount, party2: amount}

    def lightning_transaction(self, sender, recipient, amount):
        channel_id = f"{sender}-{recipient}"
        if channel_id in self.lightning_channels:
            if self.lightning_channels[channel_id][sender] >= amount:
                self.lightning_channels[channel_id][sender] -= amount
                self.lightning_channels[channel_id][recipient] += amount
                return True
        return False

blockchain = Blockchain()