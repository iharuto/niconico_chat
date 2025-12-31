# NicoNico-Style LAN Chat with Scrolling Display

A real-time LAN chat system with anonymous USER IDs, CSV logging, and niconico-style scrolling message display.

## Objective

This system is designed to **encourage anonymous questions during live meetings and presentations**, especially for questions that amateur or young students might hesitate to ask publicly.

**Use cases:**
- **"What is...?" questions** - Ask for definitions of technical terms without embarrassment
- **Clarification requests** - "Can you repeat that?" or "What did you mean by...?"
- **Basic questions** - Questions that might seem "too simple" to ask aloud
- **Real-time feedback** - Quick questions during lectures without interrupting the speaker

**Why it works:**
- **Anonymous USER IDs** (`USER_001`, `USER_002`) remove social pressure and fear of judgment
- **Scrolling display** makes questions visible to presenters without disrupting the flow
- **LAN-based** keeps questions within the meeting room (no public internet exposure)
- **Low barrier** - Just open a browser, enter room code, and ask

**Example scenario:**
During a biology presentation, a student types "What is mitochondria?" and it scrolls across the display. The presenter can address it without the student feeling embarrassed about asking a "basic" question.

## Features

- ✅ **Anonymous Chat** - Users get auto-assigned `USER_001`, `USER_002` IDs instead of showing nicknames
- ✅ **Scrolling Display** - Messages flow across screen in real-time (niconico/danmaku style)
- ✅ **CSV Logging** - All messages saved to timestamped CSV files
- ✅ **Room Codes** - Password-protected chat rooms
- ✅ **Capacity Limits** - Configurable max participants (default: 30)
- ✅ **Multi-Lane Display** - Up to 5 messages scroll simultaneously
- ✅ **No External Dependencies** - Display client uses only Python standard library
- ✅ **Single Command Startup** - Just run `./main.sh` to start everything

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

#### Install tmux (if not already installed)
```bash
# macOS
brew install tmux

# Ubuntu/Debian
sudo apt install tmux
```

That's it! No additional packages needed.

---

### 2. How to Run

#### Recommended: Single Command Startup

The easiest way to start the chat system is using the `main.sh` script:

```bash
cd /Users/haruto/niconico_chat
./main.sh
```

You should see:
```
[main] server started in tmux session: lan_chat
[main] ROOM_CODE=BIO2025  PORT=3000  MAX_CLIENTS=30

Access URL:
  http://192.168.1.100:3000

Press Ctrl+C to stop (this will also stop server/client).
```

**What it does:**
- Starts server and display client automatically in background (tmux)
- Auto-detects your WiFi IP address
- Shows access URL for easy sharing
- Ctrl+C stops everything cleanly

**Custom configuration:**
```bash
# Custom room code and settings
ROOM_CODE=PRIVATE2025 MAX_CLIENTS=10 PORT=8080 ./main.sh

# View server/client logs anytime
tmux attach -t lan_chat
# Press Ctrl+B then D to detach
```

---

#### Alternative: Manual Two-Terminal Startup

If you prefer to see live logs or don't have tmux:

**Terminal 1: Start the Chat Server**
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

**Terminal 2: Start the Display Client**
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

---

#### Join the Chat from Browser/Phone

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

### Using main.sh (Recommended)

The simplest way to configure the server:

```bash
# Basic usage with default settings
./main.sh

# Custom room code
ROOM_CODE=SECRET2025 ./main.sh

# Custom port
PORT=8080 ROOM_CODE=SECRET2025 ./main.sh

# All options
ROOM_CODE=SECRET2025 PORT=8080 MAX_CLIENTS=50 ./main.sh

# Example output:
# [main] server started in tmux session: lan_chat
# [main] ROOM_CODE=SECRET2025  PORT=8080  MAX_CLIENTS=50
#
# Access URL:
#   http://192.168.1.100:8080
#
# Press Ctrl+C to stop (this will also stop server/client).
```

### Manual Server Configuration

If using manual two-terminal startup:

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
├── main.sh                         # Single-command startup script
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

### Issue: "tmux: command not found"

**Cause**: tmux is not installed (required for `main.sh`)

**Solution**: Install tmux
```bash
# macOS
brew install tmux

# Ubuntu/Debian
sudo apt install tmux
```

**Alternative**: Use manual two-terminal startup instead.

### Issue: "Address already in use" or "Port already in use"

**Cause**: Server is already running from a previous session

**Solution using main.sh**:
```bash
# main.sh automatically kills old sessions, just run it again
./main.sh
```

**Manual solution**:
```bash
# Find and kill the process using the port
lsof -ti:3000 | xargs kill

# Or kill all node processes
pkill -f "node server.js"

# Check for orphaned tmux sessions
tmux ls
tmux kill-session -t lan_chat
```

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

### Viewing Live Logs

When using `main.sh`, server and client run in background. To view live logs:

```bash
# Attach to tmux session
tmux attach -t lan_chat

# Navigate between windows
Ctrl+B 0  # Server logs (window 0)
Ctrl+B 1  # Display client logs (window 1)

# Detach (leave running in background)
Ctrl+B D

# List all sessions
tmux ls

# Kill a specific session
tmux kill-session -t lan_chat
```

### Multiple Display Screens

Run multiple display clients for different screens:

```bash
# Using main.sh (starts one display)
./main.sh

# In another terminal, start additional display client
/usr/bin/python3 chat_display_client.py

# Or start manually on each screen
/usr/bin/python3 chat_display_client.py  # Screen 1
/usr/bin/python3 chat_display_client.py  # Screen 2
```

Both will show the same messages (synchronized via CSV).

### Running in Background

`main.sh` already runs server and client in background using tmux. If you need to run it detached from terminal:

```bash
# Start and immediately detach
./main.sh &

# Or use nohup to keep it running after logout
nohup ./main.sh > main.log 2>&1 &

# Check logs
tail -f main.log

# Stop
pkill -f "main.sh"
# Or attach and Ctrl+C:
fg  # Bring to foreground, then Ctrl+C
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

## Security & Privacy Considerations

### What Can the Host See?

**Important: Anonymity is only between participants, NOT from the host.**

The person running the server (host) has access to:

1. **Real nicknames** - Stored in CSV logs (`chat_logs/*.csv`)
   - Format: `time,nickname,user_id,text`
   - Host can see which USER_### corresponds to which nickname

2. **All messages** - Both in real-time and permanently in logs

3. **User IP addresses** - Visible in server logs and WebSocket connections

4. **Complete conversation history** - CSV files are never deleted automatically

**Example CSV entry:**
```csv
"13:23:08","Alice","USER_001","What is mitochondria?"
```
The host can see that "Alice" asked this question, even though other participants only see "USER_001".

### Trust Model

**This system requires trust in the host.** Only use it when:
- ✅ The host is trustworthy (e.g., your teacher, meeting organizer)
- ✅ You're comfortable with the host knowing your real nickname
- ✅ The host commits to keeping CSV logs confidential
- ✅ You're in a LAN environment you trust

**Do NOT use if:**
- ❌ You don't trust the host to keep identities confidential
- ❌ You need true anonymity (consider other platforms)
- ❌ The network is untrusted or public

### Network Security

**Transmission:**
- Messages sent in **plaintext** over LAN (no encryption)
- Room code transmitted **unencrypted**
- Anyone on the same LAN network with packet sniffing tools can read messages

**LAN-only design:**
- Intended for **local network use only** (classrooms, meeting rooms)
- **Do NOT expose to the internet** without:
  - HTTPS/WSS encryption (requires SSL certificates)
  - Proper authentication system
  - Rate limiting and DDoS protection
  - Security auditing

### Privacy Best Practices

**For hosts:**
1. **Keep CSV logs confidential** - Don't share them publicly
2. **Delete logs after use** - Run `rm chat_logs/*.csv` when done
3. **Inform participants** - Let them know you can see real nicknames
4. **Secure your computer** - CSV logs contain private information

**For participants:**
1. **Trust the host** - They will see your real nickname
2. **Use appropriate nicknames** - Avoid using full real names if concerned
3. **Use trusted networks only** - Avoid public WiFi
4. **Know that anonymity is limited** - Host has full access to your identity

### Recommended Use Cases

**✅ Appropriate:**
- Classroom lectures with trusted teacher as host
- Company meetings with IT department as host
- Conference presentations with organizer as host
- Study groups among friends

**❌ Not appropriate:**
- Public internet deployment
- Untrusted hosts
- High-security environments
- Anonymous whistleblowing (use proper anonymous platforms instead)

### What the Host Cannot Do

- **Cannot modify past messages** - CSV is append-only during session
- **Cannot see messages before server starts** - No history from previous sessions unless CSV files are kept
- **Cannot identify users who only observe** - Must send a message to be logged

### Additional Security Notes

- Server has no built-in rate limiting (assumes LAN trust)
- No authentication beyond room code (simple shared password)
- CSV files stored unencrypted on host's disk
- No automatic log rotation or deletion
- Display client is read-only (cannot send messages)

**Bottom line:** This is a **privacy-lite** system designed for trusted LAN environments like classrooms. It provides anonymity between participants but requires complete trust in the host.

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

**Start everything (recommended):**
```bash
./main.sh
# Custom config: ROOM_CODE=BIO2025 MAX_CLIENTS=10 PORT=8080 ./main.sh
```

**Stop everything:**
- Press **Ctrl+C** (stops both server and display)

**View logs:**
```bash
tmux attach -t lan_chat
# Press Ctrl+B then 0 for server logs
# Press Ctrl+B then 1 for client logs
# Press Ctrl+B then D to detach
```

**Manual startup (alternative):**
```bash
# Terminal 1: Start server
ROOM_CODE=BIO2025 node server.js

# Terminal 2: Start display
/usr/bin/python3 chat_display_client.py
```

**Join chat:**
- Open: `http://localhost:3000` (local) or the URL shown by `main.sh` (LAN)
- Enter nickname and room code
- Send messages!

**Exit display (manual mode only):**
- Press **ESC** key

That's all you need to know! 🎉
