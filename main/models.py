from django.db import models
import uuid
import hashlib
from django.utils.timezone import now

from main.utils import notify_new_block
from user.models import User


# Helper function to generate unique IDs
def generate_uuid():
    return uuid.uuid4().hex

# Blockchain Metadata Model
class BlockchainMetadata(models.Model):
    total_blocks = models.PositiveIntegerField(default=0)  # Total number of blocks in the chain
    total_transactions = models.PositiveIntegerField(default=0)  # Total number of transactions in the chain
    current_difficulty = models.PositiveIntegerField(default=0)  # Current mining difficulty
    last_block_hash = models.CharField(max_length=64, blank=True, null=True)  # Hash of the last block
    updated_at = models.DateTimeField(auto_now=True)  # When the metadata was last updated

    def __str__(self):
        return "Blockchain Metadata"

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if the block is newly created
        super().save(*args, **kwargs)
        if is_new:
            notify_new_block(self)


# Block Model
class Block(models.Model):
    block_hash = models.CharField(max_length=64, unique=True)  # Hash of the current block
    previous_block_hash = models.CharField(max_length=64)  # Hash of the previous block
    timestamp = models.DateTimeField(default=now)  # Timestamp of block creation
    difficulty = models.IntegerField()  # Mining difficulty at the time
    size = models.IntegerField()  # Size of the block in bytes
    transaction_count = models.IntegerField()  # Number of transactions in the block
    miner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mined_blocks')

    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Block {self.id}"

    def save(self, *args, **kwargs):
        if not self.block_hash:
            hash_input = f"{self.previous_block_hash}{self.timestamp}{self.difficulty}{self.size}{self.transaction_count}"
            self.block_hash = hashlib.sha256(hash_input.encode()).hexdigest()

        super().save(*args, **kwargs)
# Transaction Model
class Transaction(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='transactions')  # Block containing the transaction
    from_address = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions_sent')  # Sender's account
    to_address = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions_received')  # Recipient's account
    value = models.DecimalField(max_digits=30, decimal_places=18)  # Amount transferred
    data = models.TextField(null=True, blank=True)  # Optional data (e.g., for contract interactions)
    timestamp = models.DateTimeField(default=now)  # Transaction timestamp
    status = models.BooleanField()  # Whether the transaction was successful
    signature = models.TextField(null=True, blank=True)  # Digital signature for validation

    class Meta:
        indexes = [
            models.Index(fields=['from_address']),
            models.Index(fields=['to_address']),
            models.Index(fields=['block']),
        ]

    def __str__(self):
        return f"Transaction {self.transaction_id[:10]}..."

# Smart Contract Model
class SmartContract(models.Model):
    contract_address = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)  # Contract's account
    creator_address = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contracts')  # Creator's account
    creation_transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)  # Transaction that created the contract
    bytecode = models.TextField()  # Contract bytecode
    abi = models.JSONField(null=True, blank=True)  # Contract ABI for interaction

    def __str__(self):
        return f"Contract {self.contract_address.address[:10]}..."

# Event Model
class Event(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='events')  # Associated transaction
    contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='events')  # Smart contract emitting the event
    event_name = models.CharField(max_length=255)  # Name of the event
    event_data = models.JSONField()  # Event data in JSON format
    log_index = models.IntegerField()  # Log index for the event

    class Meta:
        indexes = [
            models.Index(fields=['contract']),
        ]

    def __str__(self):
        return f"{self.event_name} in {self.transaction.transaction_id[:10]}..."

# Token Transfer Model
class TokenTransfer(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='token_transfers')  # Related transaction
    token_contract = models.ForeignKey(SmartContract, on_delete=models.CASCADE, related_name='transfers')  # Token contract
    from_address = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_transfers_sent')  # Sender
    to_address = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_transfers_received')  # Recipient
    value = models.DecimalField(max_digits=78, decimal_places=0)  # Token transfer amount

    class Meta:
        indexes = [
            models.Index(fields=['token_contract']),
        ]

    def __str__(self):
        return f"Token Transfer: {self.value} from {self.from_address.address[:10]}... to {self.to_address.address[:10]}..."


# Blockchain State Model: Tracks current blockchain state
class BlockchainState(models.Model):
    current_block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True)  # Latest mined block
    total_supply = models.DecimalField(max_digits=30, decimal_places=18)  # Total supply of tokens
    current_difficulty = models.IntegerField()  # Current mining difficulty

    def __str__(self):
        return f"Blockchain State: Block {self.current_block.block_id} at Difficulty {self.current_difficulty}"

# Node Model: Represents each device or participant in the blockchain
class Node(models.Model):
    node_id = models.CharField(max_length=64, primary_key=True)  # Unique identifier for the node
    node_ip = models.GenericIPAddressField()  # Node's IP address
    node_port = models.IntegerField()  # Port number used by the node
    last_synced_block = models.ForeignKey('Block', null=True, on_delete=models.SET_NULL)  # Last synced block
    status = models.BooleanField(default=True)  # Active or inactive status
    is_miner = models.BooleanField(default=False)  # Whether this node is mining
    is_validator = models.BooleanField(default=False)  # Whether this node is validating transactions

    def __str__(self):
        return f"Node {self.node_id} ({'Active' if self.status else 'Inactive'})"


# Consensus Model: Handles validation and consensus state (PoW, PoS)
class Consensus(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)  # Associated node
    last_validated_block = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True)  # Last validated block by the node
    stake = models.DecimalField(max_digits=30, decimal_places=18, null=True, blank=True)  # Only for PoS nodes

    def __str__(self):
        return f"Consensus info for Node {self.node.node_id}"


# Token Model: Represents a token in the blockchain
class Token(models.Model):
    token_name = models.CharField(max_length=255)  # Token's name
    token_symbol = models.CharField(max_length=10)  # Token's symbol
    total_supply = models.DecimalField(max_digits=30, decimal_places=18)  # Total number of tokens
    creator = models.ForeignKey(User, on_delete=models.CASCADE)  # Creator of the token

    def __str__(self):
        return f"{self.token_name} ({self.token_symbol})"
