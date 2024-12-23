import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .blockchain import blockchain


class BlockchainConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("blockchain", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("blockchain", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if message['type'] == 'new_transaction':
            blockchain.add_transaction(message['sender'], message['recipient'], message['amount'])
        elif message['type'] == 'mine_block':
            blockchain.mine_pending_transactions(message['miner'])

        await self.channel_layer.group_send(
            "blockchain",
            {
                'type': 'blockchain_update',
                'message': {
                    'chain': [block.__dict__ for block in blockchain.chain],
                    'pending_transactions': blockchain.pending_transactions
                }
            }
        )

    async def blockchain_update(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))