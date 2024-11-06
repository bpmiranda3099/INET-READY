import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from subprocess import run, CalledProcessError
from datetime import datetime
from pytz import timezone
import csv
import os
import threading
from functools import lru_cache

# Set timezone to Asia/Manila for Philippine time
manila_timezone = timezone("Asia/Manila")

# Determine the path to the script directory and log file
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_dir, 'schedule_log.txt')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

@lru_cache(maxsize=32)
def run_fetch_data():
    current_time = datetime.now(manila_timezone)
    logging.info(f"Running data fetch at {current_time}")
    try:
        run(["python", os.path.join(script_dir, "heat_index.py")], check=True)
    except CalledProcessError as e:
        logging.error(f"Failed to run heat_index.py: {e}")

# Determine the path to the CSV file
csv_file_path = os.path.join(script_dir, 'schedule_times.csv')

# Read schedule times from CSV file in batches
schedule_times = []
batch_size = 100  # Adjust the batch size as needed

try:
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        batch = []
        for row in reader:
            if 'Time' in row:
                batch.append(row['Time'])
                if len(batch) >= batch_size:
                    schedule_times.extend(batch)
                    batch = []
            else:
                logging.error("The 'Time' column is missing in the CSV file.")
                exit(1)
        if batch:
            schedule_times.extend(batch)
except FileNotFoundError:
    logging.error("The file 'schedule_times.csv' was not found.")
    exit(1)

# Initialize scheduler with Manila timezone
scheduler = BlockingScheduler(timezone=manila_timezone)

for time in schedule_times:
    hour, minute = map(int, time.split(":"))
    scheduler.add_job(run_fetch_data, "cron", hour=hour, minute=minute)

def start_scheduler():
    logging.info("Scheduler started. It will run `heat_index.py` at specified times in Manila timezone.")
    scheduler.start()

if __name__ == "__main__":
    start_scheduler()