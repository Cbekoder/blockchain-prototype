from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

def notify_new_block(block):
    channel_layer = get_channel_layer()
    block_data = {
        "block_id": block.block_id,
        "block_hash": block.block_hash,
        "previous_block_hash": block.previous_block_hash,
        "timestamp": block.timestamp.isoformat(),
        "transaction_count": block.transaction_count,
    }
    async_to_sync(channel_layer.group_send)(
        "blockchain",  # WebSocket group name
        {"type": "send_block", "block": block_data}
    )
