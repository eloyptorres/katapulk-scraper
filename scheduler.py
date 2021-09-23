import logging
import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler

import os
INTERVAL_MINUTES = int(os.environ.get('INTERVAL_MINUTES', 15))
del os

logging.basicConfig(level=logging.WARNING)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=INTERVAL_MINUTES)
def timed_job():
    subprocess.run(['scrapy', 'crawl', 'products'])
    subprocess.run(['python', './telegram-channel/channel_manager.py', 'products.json'])


sched.start()
