import logging
import re

import emoji
from telethon import TelegramClient, sync
from telethon.sessions import StringSession

from settings import API_HASH, API_ID, CHANNEL_ID, LOGGING_LEVEL, STORAGE_ID, TELEGRAM_SESSION

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=LOGGING_LEVEL)


class UpdateChannel:
    def __init__(self, products: dict):
        self.in_stock_emoji = emoji.emojize(':check_mark_button:')
        self.depleted_emoji = emoji.emojize(':cross_mark:')
        self.client = TelegramClient(StringSession(TELEGRAM_SESSION), API_ID, API_HASH)
        self.client.start()
        async def refresh_entities():
            await self.client.get_dialogs()
        self.client.loop.run_until_complete(refresh_entities())
        self.client.loop.run_until_complete(self.update_channel(products))

    async def get_last_stock(self):
        messages = await self.client.get_messages(STORAGE_ID)
        stock = set()
        if messages and messages[0].raw_text:
            text = messages[0].raw_text
            pattern = re.compile('(?P<description>.*) (?P<price>\$.*)')
            stock = {match.group(1, 2) for match in pattern.finditer(text)}
        return stock

    async def get_stock_changes(self, current_stock: set):
        last_stock = await self.get_last_stock()
        logging.info(f'Current stock size is {len(current_stock)}')
        logging.info(f'Last stock size is {len(last_stock)}')
        return (last_stock-current_stock, current_stock-last_stock) # (depleted_products, new_products)

    async def save_stock(self, stock):
        text = '\n'.join(' '.join(prod) for prod in sorted(stock))
        await self.client.send_message(STORAGE_ID, text)

    @staticmethod
    def log_stock(products, related_information:str):
        logging.info(f'Amount of {related_information}: {len(products)}')
        for description, price in products:
            logging.info(
                f'{related_information}: [{description}]:h={hash(description)} '
                f'[{price}]:h={hash(price)} tuple_hash={hash((description, price))}'
                )

    async def update_channel(self, products: dict):
        current_stock = {(prod['title'], prod['price']) for prod in products.values()}
        depleted_products, new_products = await self.get_stock_changes(current_stock)
        UpdateChannel.log_stock(depleted_products, 'depleted products')
        UpdateChannel.log_stock(new_products, 'new products')

        await self.save_stock(current_stock)

        if depleted_products: # notify about depleted products
            text = '\n'.join(' '.join((self.depleted_emoji, *prod)) for prod in depleted_products)
            await self.client.send_message(CHANNEL_ID, text)
        
        if new_products: # notify about new available products
            text = ''
            for pseudo_product in new_products:
                prod = products[''.join(pseudo_product)]
                text += f"{self.in_stock_emoji}[{prod['title']}]({prod['url']}) {prod['price']}\n"
            await self.client.send_message(CHANNEL_ID, text)


if __name__ == '__main__':
    import json
    import sys
    args = sys.argv[1:]
    del sys

    if len(args) == 1:
        with open(args[0], 'r') as f:
            products = json.load(f)
        UpdateChannel(products)
    else:
        logging.error(f'Expected 1 process argument. Found {len(args)}.')
