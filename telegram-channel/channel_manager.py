import re

import emoji
from telethon import TelegramClient, sync
from telethon.sessions import StringSession

import settings


class UpdateChannel:
    def __init__(self, products: dict):
        self.in_stock_emoji = emoji.emojize(':check_mark_button:')
        self.depleted_emoji = emoji.emojize(':cross_mark:')
        self.client = TelegramClient(StringSession(settings.session), settings.api_id, settings.api_hash)
        self.client.start()
        async def refresh_entities():
            await self.client.get_dialogs()
        self.client.loop.run_until_complete(refresh_entities())
        self.client.loop.run_until_complete(self.update_channel(products))

    async def get_last_stock(self):
        messages = await self.client.get_messages(settings.storage_id)
        stock = set()
        if messages and messages[0].raw_text:
            text = messages[0].raw_text
            pattern = re.compile('(?P<description>.*) (?P<price>$.*)')
            stock = {match.group(1, 2) for match in pattern.finditer(text)}
        return stock
    
    async def get_stock_changes(self, current_stock: set):
        last_stock = await self.get_last_stock()
        return (last_stock-current_stock, current_stock-last_stock) # (depleted_products, new_products)

    async def save_stock(self, stock):
        text = '\n'.join(' '.join(prod) for prod in sorted(stock))
        await self.client.send_message(settings.storage_id, text)

    async def update_channel(self, products: dict):
        current_stock = {(prod['title'], prod['price']) for prod in products.values()}
        depleted_products, new_products = await self.get_stock_changes(current_stock)
        await self.save_stock(current_stock)

        if depleted_products: # notify about depleted products
            text = '\n'.join(' '.join(self.depleted_emoji, prod) for prod in depleted_products)
            await self.client.send_message(settings.channel_id, text)
        
        for pseudo_product in new_products: # notify about new available products
            prod = products[''.join(pseudo_product)]
            text = f"{self.in_stock_emoji}[{prod['title']}]({prod['url']})\n{prod['description']}\n{prod['price']}"
            await self.client.send_message(settings.channel_id, text)


if __name__ == '__main__':
    import json
    import sys
    args = sys.argv[1:]

    if len(args) == 1:
        with open(args[0], 'r') as f:
            products = json.load(f)
        UpdateChannel(products)
    else:
        print(f'Expected 1 argument. Found {len(args)}.')
