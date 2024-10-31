import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from subprocess import run, CalledProcessError
from datetime import datetime
from pytz import timezone
import csv

# Set timezone to Asia/Manila for Philippine time
manila_timezone = timezone("Asia/Manila")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_fetch_data():
    current_time = datetime.now(manila_timezone)
    logging.info(f"Running data fetch at {current_time}")
    try:
        run(["python", "heat_index.py"], check=True)
    except CalledProcessError as e:
        logging.error(f"Failed to run heat_index.py: {e}")

# Read schedule times from CSV file
schedule_times = []
try:
    with open('schedule_times.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            schedule_times.append(row['time'])
except FileNotFoundError:
    logging.error("The file 'schedule_times.csv' was not found.")
    exit(1)

# Initialize scheduler with Manila timezone
scheduler = BlockingScheduler(timezone=manila_timezone)

for time in schedule_times:
    hour, minute = map(int, time.split(":"))
    scheduler.add_job(run_fetch_data, "cron", hour=hour, minute=minute)

logging.info("Scheduler started. It will run `heat_index.py` at specified times in Manila timezone.")
scheduler.start()