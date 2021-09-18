import logging
import subprocess

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.WARNING)

sched = AsyncIOScheduler()

@sched.scheduled_job('interval', minutes=15)
def timed_job():
    subprocess.run(['scrapy', 'crawl', 'products'])
    subprocess.run(['python', './telegram-channel/channel_manager.py', 'products.json'])


sched.start()
