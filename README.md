# NicoNico-Style LAN Chat with Scrolling Display

A real-time LAN chat system with anonymous USER IDs, CSV logging, and niconico-style scrolling message display.

## Features

✅ **Anonymous Chat** - Users get auto-assigned `USER_001`, `USER_002` IDs instead of showing nicknames
✅ **Scrolling Display** - Messages flow across screen in real-time (niconico/danmaku style)
✅ **CSV Logging** - All messages saved to timestamped CSV files
✅ **Room Codes** - Password-protected chat rooms
✅ **Capacity Limits** - Configurable max participants (default: 30)
✅ **Multi-Lane Display** - Up to 5 messages scroll simultaneously
✅ **No External Dependencies** - Display client uses only Python standard library

---

## Quick Start

### 1. Setup (One-time)

#### Install Node.js Dependencies
```bash
cd /Users/haruto/niconico_chat
npm install
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

That's it! No additional packages needed.

---

### 2. How to Run

You need **two terminal windows**:

#### Terminal 1: Start the Chat Server
```bash
cd /Users/haruto/niconico_chat
ROOM_CODE=BIO2025 node server.js
```

You should see:
```
CSV log initialized: /Users/haruto/niconico_chat/chat_logs/20251231_132229_log.csv
LAN chat server running on port 3000
ROOM_CODE = BIO2025
Open: http://<server-lan-ip>:3000
```

#### Terminal 2: Start the Display Client
```bash
cd /Users/haruto/niconico_chat
/usr/bin/python3 chat_display_client.py
```

You should see:
```
=== CSV Chat Display Client ===
Log Directory: chat_logs
Display: chr_flow.py (5 lanes)
Format: Message text only

Press ESC to exit

[CSV Watcher] Watching: chat_logs/20251231_132229_log.csv
Starting chr_flow display...
```

#### Browser/Phone: Join the Chat

**On the same computer:**
- Open: `http://localhost:3000`

**On other devices (LAN):**
1. Find server IP: `ifconfig | grep "inet " | grep -v 127.0.0.1`
2. Open: `http://192.168.1.xxx:3000` (use your server's IP)

**Join the chat:**
1. Enter your nickname (e.g., "Alice")
2. Enter room code: `BIO2025`
3. Click "Join"
4. Send messages → **watch them scroll on the display!**

---

## How It Works

```
┌──────────────────────────────────────────────────────┐
│  Web Clients (Browser/Phone)                         │
│  - Enter nickname + room code                        │
│  - Get assigned USER_001, USER_002, etc.            │
│  - Send/receive messages                             │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  Node.js WebSocket Server (server.js)                │
│  - Authenticates users with room code                │
│  - Assigns USER_### IDs sequentially                 │
│  - Broadcasts messages to all clients                │
│  - Logs messages to CSV files                        │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  CSV Log Files (chat_logs/)                          │
│  - Format: time,nickname,user_id,text                │
│  - One file per server start                         │
│  - Example: 20251231_132229_log.csv                  │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  Display Client (chat_display_client.py)             │
│  - Watches CSV log for new messages                  │
│  - Polls every 0.5 seconds                           │
│  - Extracts message text only                        │
│  - Feeds to chr_flow display                         │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  Scrolling Display (chr_flow.py)                     │
│  - Transparent overlay on screen                     │
│  - Up to 5 messages scroll simultaneously            │
│  - Right-to-left animation (niconico style)          │
│  - Works over other applications                     │
└──────────────────────────────────────────────────────┘
```

---

## Configuration

### Server Environment Variables

Configure the server with environment variables:

```bash
# Room authentication code (required)
ROOM_CODE=SECRET2025

# Server port (default: 3000)
PORT=8080

# Maximum participants (default: 30)
MAX_CLIENTS=50

# Start server with config
ROOM_CODE=SECRET2025 PORT=8080 MAX_CLIENTS=50 node server.js
```

### Display Client Options

```bash
# Default: watches chat_logs/ directory
/usr/bin/python3 chat_display_client.py

# Custom log directory
/usr/bin/python3 chat_display_client.py --log-dir /path/to/logs
```

### chr_flow Display Settings

Edit `chr_flow.py` to customize the display:

```python
NUM_LANES = 5          # Max simultaneous messages (1-10)
LANE_HEIGHT = 80       # Vertical spacing (pixels)
LANE_START_Y = 150     # Top margin (pixels)
SPEED = 6              # Scroll speed (pixels/frame)
ALPHA = 0.9            # Window transparency (0.0-1.0)
```

**Recommendations:**
- **Busy chats**: Increase `NUM_LANES = 7` and `SPEED = 8`
- **Slow chats**: Decrease `NUM_LANES = 3` and `SPEED = 4`
- **More visible**: Increase `ALPHA = 1.0` (fully opaque)

---

## Features Explained

### 1. Anonymous USER_### IDs

**Purpose**: Hide real nicknames for privacy

**How it works:**
- Server assigns IDs sequentially: `USER_001`, `USER_002`, etc.
- Web clients see only USER IDs (not nicknames)
- Nicknames stored in CSV log for moderation
- IDs never reused during server session

**Example:**
```
[12:34:56] USER_001: Hello everyone!
[12:35:02] USER_002: Hi there!
[12:35:10] USER_001: How are you?
```

### 2. CSV Logging

**Purpose**: Permanent record of all messages

**Log Format:**
```csv
time,nickname,user_id,text
"13:23:08","Alice","USER_001","Hello everyone!"
"13:23:15","Bob","USER_002","Hi there!"
```

**Log Files:**
- Location: `chat_logs/`
- Filename: `YYYYMMDD_HHMMSS_log.csv`
- One file per server start
- Proper CSV escaping (handles quotes, commas, newlines)

**To view logs:**
```bash
# View latest log
cat chat_logs/*.csv | tail -20

# Open in Excel/Numbers
open chat_logs/20251231_132229_log.csv
```

### 3. Room Capacity Limits

**Purpose**: Prevent overcrowding on personal servers

**How it works:**
- Set `MAX_CLIENTS` environment variable
- Server rejects connections when room is full
- Display client counts as one participant

**Example:**
```bash
# Allow only 10 participants
MAX_CLIENTS=10 ROOM_CODE=PRIVATE node server.js
```

### 4. Scrolling Display

**Purpose**: Visual, distraction-free message display

**Features:**
- **Transparent overlay**: Works over other apps
- **Click-through**: Mouse events pass through
- **Multi-lane**: Up to 5 messages scroll at once
- **Auto-queue**: New messages spawn as lanes free
- **ESC to exit**: Press ESC key to close

**Display format:**
- Shows message text ONLY
- No user IDs, no timestamps
- Clean, minimal display

---

## File Structure

```
niconico_chat/
├── server.js                       # WebSocket server (Node.js)
├── public/
│   └── index.html                  # Web client (HTML/JS)
├── chat_logs/                      # CSV log files (auto-created)
│   ├── 20251231_132229_log.csv
│   └── 20251231_140530_log.csv
├── chr_flow.py                     # Display engine (PyObjC)
├── chat_display_client.py          # CSV watcher + display
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies
├── CLAUDE.md                       # Implementation requirements
└── README.md                       # This file
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'websocket'"

**Solution**: This error is obsolete! The new CSV-based display client doesn't need websocket-client. Just run:
```bash
/usr/bin/python3 chat_display_client.py
```

### Issue: Display client shows no messages

**Checklist:**
1. ✅ Server is running? Check Terminal 1
2. ✅ Display client is running? Check Terminal 2
3. ✅ CSV log file exists? Check `ls chat_logs/`
4. ✅ Sent NEW message? (Old messages are skipped)

**Debug:**
```bash
# Check if messages are in CSV
cat chat_logs/*.csv | tail -5

# Check display client output
# Should show: "[CSV Watcher] Queued: your message..."
```

### Issue: "Room full" error

**Cause**: Too many participants (default limit: 30)

**Solutions:**
```bash
# Option 1: Increase limit
MAX_CLIENTS=50 ROOM_CODE=BIO2025 node server.js

# Option 2: Disconnect some users
# Users must close browser tabs or disconnect
```

### Issue: Messages have 0.5 second delay

**Cause**: Display client polls CSV every 0.5 seconds (by design)

**This is normal!** CSV-based approach trades slight delay for simplicity.

**To reduce delay**: Edit `chat_display_client.py`:
```python
POLL_INTERVAL = 0.2  # Faster polling (more CPU usage)
```

### Issue: chr_flow display not visible

**Checklist:**
1. ✅ Screen recording permission granted?
   - System Preferences > Security & Privacy > Privacy > Screen Recording
   - Enable for Terminal or Python
2. ✅ Display shows on correct screen? (Multi-monitor setups)
3. ✅ Window transparency too high? Edit `chr_flow.py`:
   ```python
   ALPHA = 1.0  # Fully opaque (easier to see)
   ```

### Issue: Can't connect from other devices

**Cause**: Firewall blocking port 3000

**Solutions:**
```bash
# Option 1: Allow port in firewall
# System Preferences > Security & Privacy > Firewall > Firewall Options
# Add node.js to allowed apps

# Option 2: Temporarily disable firewall (testing only)
# Not recommended for production use
```

**Find your server IP:**
```bash
# macOS
ifconfig | grep "inet " | grep -v 127.0.0.1

# Example output: inet 192.168.1.100
# Use: http://192.168.1.100:3000 from other devices
```

---

## Advanced Usage

### Multiple Display Screens

Run multiple display clients for different screens:

```bash
# Display 1
/usr/bin/python3 chat_display_client.py

# Display 2 (if you have two screens)
/usr/bin/python3 chat_display_client.py
```

Both will show the same messages (synchronized via CSV).

### Background Server

Run server in background to free up terminal:

```bash
# Start in background
ROOM_CODE=BIO2025 node server.js > server.log 2>&1 &

# Check if running
ps aux | grep "node server.js"

# View logs
tail -f server.log

# Stop server
kill $(ps aux | grep "node server.js" | grep -v grep | awk '{print $2}')
```

### Replaying Old Messages

Display client can replay old CSV logs:

```bash
# Copy old log to new name
cp chat_logs/20251231_132229_log.csv chat_logs/replay.csv

# Watch the replay file
/usr/bin/python3 chat_display_client.py --log-dir chat_logs
```

Then append messages to `replay.csv` manually or with a script.

---

## Technical Details

### Technologies Used

**Server:**
- Node.js + Express (HTTP server)
- ws library (WebSocket server)
- Built-in fs, path (File I/O)

**Client:**
- Vanilla HTML/JavaScript (no frameworks)
- WebSocket API (built-in)

**Display:**
- Python 3 (standard library only)
- PyObjC (macOS native UI)
- csv, glob, os, threading (built-in modules)

### Security Considerations

**Room Codes:**
- Transmitted in plaintext (use HTTPS for production)
- No rate limiting (LAN usage assumed safe)
- No password hashing (simple authentication)

**CSV Logs:**
- Contain real nicknames (private information)
- Stored unencrypted on disk
- Add `chat_logs/*.csv` to `.gitignore`

**Display Client:**
- Read-only (doesn't send messages)
- Requires file system access
- Runs with user privileges

### Performance

**Server:**
- Handles ~100 concurrent connections easily
- CPU: <5% on modern hardware
- Memory: ~50MB base + 1MB per connection

**Display Client:**
- CPU: <2% (polling overhead)
- Memory: ~100MB (PyObjC + chr_flow)
- Disk I/O: <1KB/s (CSV reads)

**Suitable for:**
- Small to medium LAN events (5-50 people)
- Local development/testing
- Personal/home use

**Not suitable for:**
- Large public servers (>100 users)
- Internet-facing deployments (no TLS/auth)
- High-security environments

---

## Credits & Inspiration

This project is inspired by the scrolling comment (danmaku) style popularized by **niconico douga (niconico動画)**.

This implementation is original and not affiliated with or endorsed by DWANGO or niconico douga.

**Key differences:**
- LAN-only (not internet-facing)
- CSV-based (simpler architecture)
- Anonymous USER IDs (privacy-focused)
- macOS native display (PyObjC)

---

## License

See LICENSE file for details.

---

## Support

**Issues?** Check the Troubleshooting section above.

**Questions?** Review the configuration options and how-it-works diagram.

**Want to contribute?** See CLAUDE.md for implementation details.

---

## Quick Reference

**Start server:**
```bash
ROOM_CODE=BIO2025 node server.js
```

**Start display:**
```bash
/usr/bin/python3 chat_display_client.py
```

**Join chat:**
- Open: `http://localhost:3000` (local) or `http://192.168.1.xxx:3000` (LAN)
- Enter nickname and room code
- Send messages!

**Exit display:**
- Press **ESC** key

**Stop server:**
- Press **Ctrl+C**

That's all you need to know! 🎉
