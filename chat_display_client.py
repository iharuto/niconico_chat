#!/usr/bin/env python3
"""
CSV Chat Display Client
Reads chat messages from CSV log files and displays using chr_flow.py
No external dependencies - uses only Python standard library
"""

import csv
import time
import threading
from queue import Queue
import os
import glob

# Import chr_flow components
from chr_flow import (
    create_window,
    ScrollController,
    setup_keyboard_handler,
    NUM_LANES,
    LANE_POSITIONS,
    INTERVAL,
    NSApplication,
    NSTimer,
    AppHelper
)

# Configuration
LOG_DIR = "chat_logs"
POLL_INTERVAL = 0.5  # Check for new messages every 0.5 seconds

# Thread-safe message queue (File watcher thread → AppKit main thread)
message_display_queue = Queue()


class CSVLogWatcher:
    """Watches CSV log file for new messages."""

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.current_file = None
        self.file_position = 0
        self.running = True

    def get_latest_log_file(self):
        """Find the most recent CSV log file."""
        pattern = os.path.join(self.log_dir, "*_log.csv")
        files = glob.glob(pattern)
        if not files:
            return None
        # Return the newest file by modification time
        return max(files, key=os.path.getmtime)

    def watch(self):
        """Watch log file and queue new messages."""
        print("[CSV Watcher] Starting file monitor...")

        while self.running:
            try:
                # Check if we need to switch to a newer log file
                latest_file = self.get_latest_log_file()

                if latest_file != self.current_file:
                    if latest_file:
                        print(f"[CSV Watcher] Watching: {latest_file}")
                        self.current_file = latest_file
                        self.file_position = 0

                        # Read existing messages (skip header)
                        with open(self.current_file, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            next(reader, None)  # Skip header
                            for row in reader:
                                pass  # Skip existing messages
                            self.file_position = f.tell()

                # Read new messages
                if self.current_file:
                    with open(self.current_file, 'r', encoding='utf-8') as f:
                        f.seek(self.file_position)
                        reader = csv.reader(f)

                        for row in reader:
                            if len(row) >= 4:
                                # CSV format: time,nickname,user_id,text
                                text = row[3]  # Extract text column
                                if text.strip():
                                    message_display_queue.put(text)
                                    print(f"[CSV Watcher] Queued: {text[:50]}...")

                        self.file_position = f.tell()

                time.sleep(POLL_INTERVAL)

            except Exception as e:
                print(f"[CSV Watcher] Error: {e}")
                time.sleep(POLL_INTERVAL)

    def start(self):
        """Start watching in background thread."""
        watch_thread = threading.Thread(target=self.watch, daemon=True)
        watch_thread.start()

    def stop(self):
        """Stop watching."""
        self.running = False


class DisplayController(ScrollController):
    """Extended ScrollController that pulls from CSV message queue."""

    def tick_(self, timer):
        """Override tick to check CSV queue before animating."""

        # Pull messages from CSV queue (non-blocking)
        while not message_display_queue.empty():
            try:
                message_text = message_display_queue.get_nowait()
                self.message_queue.append(message_text)
                print(f"[Display] Added to chr_flow queue: {message_text[:50]}...")
            except:
                break

        # Call parent tick (handles animation and spawning)
        super().tick_(timer)


def main():
    """Main application entry point."""
    import argparse

    # Command-line arguments
    parser = argparse.ArgumentParser(
        description="CSV Chat Display Client - Shows chat messages from CSV logs using chr_flow"
    )
    parser.add_argument(
        "--log-dir",
        default=LOG_DIR,
        help=f"Chat logs directory (default: {LOG_DIR})"
    )
    args = parser.parse_args()

    print("=== CSV Chat Display Client ===")
    print(f"Log Directory: {args.log_dir}")
    print(f"Display: chr_flow.py ({NUM_LANES} lanes)")
    print("Format: Message text only")
    print("\nPress ESC to exit\n")

    # Create CSV log watcher and start monitoring
    csv_watcher = CSVLogWatcher(args.log_dir)
    csv_watcher.start()

    # Create shared application instance
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(0)  # NSApplicationActivationPolicyRegular

    # Create window
    window, screen_width, screen_height = create_window()

    # Create display controller (extended version)
    controller = DisplayController.alloc().initWithWindow_screenWidth_screenHeight_(
        window, screen_width, screen_height
    )

    # Start animation timer
    NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
        INTERVAL,
        controller,
        "tick:",
        None,
        True
    )

    # Set up ESC key handler
    setup_keyboard_handler(app)

    # Show window and start event loop
    window.makeKeyAndOrderFront_(None)
    app.activateIgnoringOtherApps_(True)

    print("Starting chr_flow display...\n")

    # Start PyObjC event loop (blocks until ESC pressed)
    AppHelper.runEventLoop()

    # Cleanup
    csv_watcher.stop()


if __name__ == "__main__":
    main()
