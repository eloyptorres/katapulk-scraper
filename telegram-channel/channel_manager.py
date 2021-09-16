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

    async def is_product_in_stock(self, product):
        messages = await self.client.get_messages(settings.channel_id, search=product['title'])
        if messages:
            message = messages[0]
            return self.in_stock_emoji in message.raw_text
        return False
            
    async def update_channel(self, products: dict):
        for product in products.values():
            if await self.is_product_in_stock(product):
                continue
            else:
                text = f"{self.in_stock_emoji}[{product['title']}]({product['url']})\n{product['description']}\n{product['price']}"
                await self.client.send_message(settings.channel_id, text)


if __name__ == '__main__':
    import sys, json
    args = sys.argv[1:]

    if len(args) == 1:
        with open(args[0], 'r') as f:
            products = json.load(f)
        UpdateChannel(products)
    else:
        print(f'Expected 1 argument. Found {len(args)}.')
