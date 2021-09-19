import logging
import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(level=logging.WARNING)

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=15)
def timed_job():
    subprocess.run(['scrapy', 'crawl', 'products'])
    subprocess.run(['python', './telegram-channel/channel_manager.py', 'products.json'])


sched.start()
