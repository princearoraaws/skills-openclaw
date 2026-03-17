#!/usr/bin/env python3.10
"""
Snapshot Watcher with Auto-Cleanup
Watches for new snapshots AND automatically deletes old ones
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

SNAPSHOT_DIR = Path.home() / ".openclaw" / "workspace" / "camera" / "snapshots"
QUEUE_DIR = Path.home() / ".openclaw" / "workspace" / "camera" / "analysis_queue"
LOG_FILE = Path.home() / ".openclaw" / "workspace" / "camera" / "watcher.log"

# Config
MAX_AGE_HOURS = 1  # Delete snapshots older than this
CLEANUP_INTERVAL = 300  # Check for old files every 5 minutes (300 seconds)

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def cleanup_old_snapshots():
    """Delete snapshots older than MAX_AGE_HOURS"""
    cutoff_time = datetime.now() - timedelta(hours=MAX_AGE_HOURS)
    deleted_count = 0
    
    for image_file in SNAPSHOT_DIR.glob("*.jpg"):
        try:
            mtime = datetime.fromtimestamp(image_file.stat().st_mtime)
            if mtime < cutoff_time:
                image_file.unlink()
                deleted_count += 1
        except Exception as e:
            log(f"  Error deleting {image_file.name}: {e}")
    
    if deleted_count > 0:
        remaining = len(list(SNAPSHOT_DIR.glob("*.jpg")))
        log(f"🧹 Auto-cleanup: {deleted_count} old snapshot(s) deleted, {remaining} remaining")
    
    return deleted_count

def queue_for_analysis(image_path):
    """Queue image for analysis"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    queue_file = QUEUE_DIR / f"analyze_{timestamp}_{image_path.stem}.txt"
    
    with open(queue_file, "w") as f:
        f.write(str(image_path))
    
    log(f"   → Queued: {queue_file.name}")
    log(f"   → Person: Jade (home office, star necklace)")
    return queue_file

def watch_snapshots():
    """Watch for new snapshots with auto-cleanup"""
    log(f"👁️  Watching: {SNAPSHOT_DIR}")
    log(f"🧹 Auto-cleanup: Deletes snapshots older than {MAX_AGE_HOURS} hour(s)")
    log("Press Ctrl+C to stop\n")
    
    known_files = set(f.name for f in SNAPSHOT_DIR.glob("*.jpg"))
    log(f"Found {len(known_files)} existing snapshots")
    
    last_cleanup = time.time()
    
    try:
        while True:
            time.sleep(2)
            
            # Check for new snapshots
            current_files = set(f.name for f in SNAPSHOT_DIR.glob("*.jpg"))
            new_files = current_files - known_files
            
            for filename in sorted(new_files):
                image_path = SNAPSHOT_DIR / filename
                time.sleep(0.5)
                
                if image_path.exists() and image_path.stat().st_size > 1000:
                    log(f"📸 NEW: {filename}")
                    queue_for_analysis(image_path)
            
            known_files = current_files
            
            # Periodic cleanup
            if time.time() - last_cleanup > CLEANUP_INTERVAL:
                cleanup_old_snapshots()
                last_cleanup = time.time()
                # Refresh known files after cleanup
                known_files = set(f.name for f in SNAPSHOT_DIR.glob("*.jpg"))
            
    except KeyboardInterrupt:
        log("\n👋 Watcher stopped")

def main():
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    
    log("=" * 60)
    log("📷 Motion Watcher + Auto-Cleanup")
    log(f"Deletes snapshots older than {MAX_AGE_HOURS} hour(s)")
    log("=" * 60)
    
    watch_snapshots()
    return 0

if __name__ == "__main__":
    sys.exit(main())