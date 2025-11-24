#!/usr/bin/env python3
import os
import time
import logging
from datetime import datetime, timedelta

from pymongo import MongoClient

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
LOG_FILE = os.getenv("NTP_LOG_FILE", "/data/peerstats")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/ttylogs")
SCAN_INT = int(os.getenv("SCAN_INTERVAL", "10"))

# ──────────────────────────────────────────────────────────────────────────────
# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)7s] %(message)s"
)

# ──────────────────────────────────────────────────────────────────────────────
# MongoDB client
try:
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    ntp_coll = db.ntp_requests
    attackers_coll = db.attackers
    logging.info(f"Successfully connected to MongoDB, using database '{db.name}'.")
except Exception as e:
    logging.error(f"Could not connect to MongoDB: {e}")
    exit(1)

def follow(thefile):
    """Generator function that yields new lines in a file."""
    thefile.seek(0, 2)  # Go to the end of the file
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(1) # Sleep when idle
            continue
        yield line

def parse_and_store_line(line):
    """Parses a single line from ntpd's peerstats log and stores it in MongoDB."""
    try:
        parts = line.strip().split()
        if len(parts) < 4: return

        ip_address = parts[2]
        status_hex = parts[3]

        # Filter out traffic from our own upstream servers and local clock.
        # Upstream servers are marked with a 'CONFIG' flag (LSB=1 in the status word).
        # Local clock IPs start with '127.'.
        if ip_address.startswith("127."):
            return
        
        status_int = int(status_hex, 16)
        if (status_int & 0x1): # Check for CONFIG flag
            return

        # The peerstats log only contains the time of day, not the full date.
        # We'll combine it with the current UTC date. This is reliable as
        # the parser processes logs in near real-time.
        current_date = datetime.utcnow().date()
        seconds_of_day_str = parts[1]
        seconds = int(float(seconds_of_day_str))
        time_obj = (datetime.min + timedelta(seconds=seconds)).time()
        dt_obj = datetime.combine(current_date, time_obj)

        doc = {"timestamp": dt_obj, "source_ip": ip_address, "raw_log": line.strip()}

        # Insert the specific event
        ntp_coll.update_one({"timestamp": dt_obj, "source_ip": ip_address}, {"$set": doc}, upsert=True)
        logging.info(f"Logged NTP request from {ip_address}")

        # Update the centralized attacker record
        attackers_coll.update_one(
            {"source_ip": ip_address},
            {
                "$set": {"last_seen": dt_obj},
                "$setOnInsert": {"first_seen": dt_obj},
                "$addToSet": {"services_targeted": "ntp"}
            },
            upsert=True
        )
    except (ValueError, IndexError):
        # This can happen for malformed lines (e.g., status isn't valid hex).
        # We can safely ignore these lines as they are not client requests we want to log.
        return
    except Exception as e:
        logging.error(f"Error processing line '{line.strip()}': {e}", exc_info=True)

if __name__ == "__main__":
    logging.info(f"NTP log parser started. Watching {LOG_FILE}")
    while not os.path.exists(LOG_FILE):
        logging.info(f"Log file {LOG_FILE} not found. Waiting {SCAN_INT} seconds...")
        time.sleep(SCAN_INT)

    with open(LOG_FILE, "r") as logfile:
        for line in logfile: parse_and_store_line(line)
        for line in follow(logfile): parse_and_store_line(line)