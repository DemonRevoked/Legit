#!/usr/bin/env python3
import os
import time
import glob
import json
import shutil
import re
import logging

from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
LOG_DIR    = "/data/ttylogs"
RAW_ARCH   = "/data/raw"
JSON_OUT   = "/data/json/sessions.jsonl"
MONGO_URI  = os.getenv("MONGO_URI", "mongodb://mongo:27017/ttylogs")
SCAN_INT   = int(os.getenv("SCAN_INTERVAL", "10"))
WORKERS    = 4

# Regexes
ANSI_RE       = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]|\r')
DONE_MARKER   = re.compile(r"^Script done on", re.MULTILINE)
PROMPT_CMD_RE = re.compile(r"^[^\n]*#\s*(.+)$", re.MULTILINE)

# ──────────────────────────────────────────────────────────────────────────────
# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)7s] %(message)s"
)

# MongoDB client
tx_client = MongoClient(MONGO_URI)
coll      = tx_client.get_database().sessions

# Thread pool
pool = ThreadPoolExecutor(max_workers=WORKERS)

# ──────────────────────────────────────────────────────────────────────────────
def clean_text(b: bytes) -> str:
    """Decode and strip ANSI/control bytes."""
    text = b.decode("utf-8", "ignore")
    return ANSI_RE.sub("", text)


def extract_commands(full_text: str):
    """Find every command the user typed after a '# ' prompt."""
    return PROMPT_CMD_RE.findall(full_text)


def parse_and_persist(base: str):
    session_id = os.path.basename(base)
    meta_f = base + ".meta.json"
    ts_f   = base + ".typescript"
    tm_f   = ts_f + ".timing"

    try:
        # 1) Check all parts exist
        if not all(os.path.exists(f) for f in (meta_f, ts_f, tm_f)):
            logging.debug(f"[{session_id}] Waiting for all files to exist.")
            return

        # 2) Ensure recording finished
        ts_text = open(ts_f, "r", errors="ignore").read()
        if not DONE_MARKER.search(ts_text):
            logging.debug(f"[{session_id}] Session still recording, skipping.")
            return

        logging.info(f"[{session_id}] Processing completed session.")

        # 3) Archive raw files
        os.makedirs(RAW_ARCH, exist_ok=True)
        for src in (meta_f, ts_f, tm_f):
            dst = os.path.join(RAW_ARCH, os.path.basename(src))
            shutil.copy(src, dst)
        logging.info(f"[{session_id}] Archived raw files to {RAW_ARCH}.")

        # 4) Load metadata
        with open(meta_f) as mf:
            meta = json.load(mf)

        # 5) Read timing data and raw bytes
        timing = [line.split() for line in open(tm_f) if line.strip()]
        raw    = open(ts_f, "rb").read()

        # 6) Reconstruct events
        events, offset, toff = [], 0.0, 0.0
        for delay_str, size_str in timing:
            toff += float(delay_str)
            size = int(size_str)
            chunk_bytes = raw[int(offset):int(offset)+size]
            offset += size
            chunk = clean_text(chunk_bytes)
            events.append({"time_offset": toff, "data": chunk})

        # 7) Extract commands
        full_text = "".join(e["data"] for e in events)
        commands  = extract_commands(full_text)

        # 8) Assemble document
        doc = {**meta, "events": events, "commands": commands}

        # 9) Persist to MongoDB and capture inserted_id
        result = coll.insert_one(doc)
        _id = result.inserted_id
        logging.info(f"[{session_id}] Inserted into MongoDB with _id={_id}.")

        # 10) Convert _id to string for JSON serializability
        doc["_id"] = str(_id)

        # 11) Append to JSONL
        with open(JSON_OUT, "a") as jf:
            jf.write(json.dumps(doc) + "\n")
        logging.info(f"[{session_id}] Appended to JSONL at {JSON_OUT}.")

        # 12) Cleanup originals
        for f in (meta_f, ts_f, tm_f):
            try:
                os.remove(f)
            except FileNotFoundError:
                logging.warning(f"[{session_id}] File not found during cleanup: {f}")
        logging.info(f"[{session_id}] Removed original files from working dir.")

    except Exception as e:
        logging.error(f"[{session_id}] Error parsing session: {e}", exc_info=True)


def scan_and_submit():
    pattern = os.path.join(LOG_DIR, "*.typescript.timing")
    for tm in glob.glob(pattern):
        base = tm[:-len(".typescript.timing")]
        logging.debug(f"Found timing file: {tm}, scheduling parse.")
        pool.submit(parse_and_persist, base)

if __name__ == "__main__":
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(RAW_ARCH, exist_ok=True)
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)

    logging.info("Parser started, watching for new sessions.")
    while True:
        scan_and_submit()
        time.sleep(SCAN_INT)
