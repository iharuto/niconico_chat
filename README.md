# Ubersicht_niconico

## Inspiration

This project is inspired by the scrolling comment (danmaku) style popularized by niconico douga (niconico動画), but this implementation is original and not affiliated with or endorsed by DWANGO or niconico douga.

## Overview

This project creates a macOS screen overlay with right-to-left scrolling text (niconico-style) that works even during Keynote/PowerPoint fullscreen presentations.

**Three implementations are available:**
- **PyObjC** (Recommended): Native macOS solution with proper window level control
- **Tkinter**: Original implementation (text rendering issues on some systems)

## PyObjC Implementation (Recommended)

The PyObjC implementation uses native macOS APIs to create transparent overlay windows that work reliably with fullscreen presentations.

### Setup

1. **Install PyObjC dependencies:**
```bash
/usr/bin/python3 -m pip install --user pyobjc-core==11.1 pyobjc-framework-Cocoa==11.1
```

Or use the requirements file:
```bash
/usr/bin/python3 -m pip install --user -r requirements.txt
```

### Usage

**Stage 1: Baseline (Visible Window)**
- Standard window with title bar
- Validates text scrolling works
- Good for debugging

```bash
/usr/bin/python3 chr_flow_pyobjc_stage1.py
```

**Stage 2: Transparent Overlay (Primary)**
- Borderless transparent overlay
- Click-through enabled
- Works on all Spaces
- Best for normal desktop use

```bash
/usr/bin/python3 chr_flow_pyobjc_stage2.py
```

**Stage 3: Presentation Mode (Fullscreen)**
- Maximum window level (NSScreenSaverWindowLevel)
- Works during Keynote/PowerPoint fullscreen
- Fullscreen auxiliary behavior

```bash
/usr/bin/python3 chr_flow_pyobjc_stage3.py
```

To test Stage 3:
1. Run the script
2. Open Keynote or PowerPoint
3. Enter fullscreen presentation mode
4. Text should scroll over the presentation

**Exit:** Press ESC to quit (or Cmd+Q)

### Configuration

Edit the script files to customize:
- `TEXT`: The scrolling text content
- `SPEED`: Pixels per frame (default: 6)
- `Y_POSITION`: Distance from top of screen (default: 200)
- `ALPHA`: Window transparency 0.0-1.0 (default: 0.9)

Stage 3 supports multi-lane mode by uncommenting `MULTI_LANE` configuration.

### Technical Details

**Window Levels:**
- Stage 1: `NSFloatingWindowLevel` (3) - above normal windows
- Stage 2: `NSFloatingWindowLevel + 1` (4) - above floating palettes
- Stage 3: `NSScreenSaverWindowLevel` (1000) - above fullscreen apps

**Why PyObjC vs Tkinter:**
- Tkinter's `-topmost` uses `NSNormalWindowLevel` (0-3), which cannot penetrate macOS fullscreen app layers
- PyObjC provides direct access to `NSScreenSaverWindowLevel` (1000), which explicitly sits above fullscreen applications
- PyObjC enables proper window collection behaviors for fullscreen auxiliary mode

### Troubleshooting

**"Screen Recording" permission prompt (macOS 10.14+):**
- Go to System Preferences > Security & Privacy > Privacy > Screen Recording
- Enable permission for Terminal or your Python executable

**Text not visible:**
- Try Stage 1 first to validate basic functionality
- Check that PyObjC is installed correctly: `/usr/bin/python3 -c "import objc; print(objc.__version__)"`

**Performance issues on high-resolution displays:**
- Reduce `SPEED` value
- Increase `INTERVAL` value (e.g., 0.033 for 30fps)

## Tkinter Implementation (Original)

Original implementation using Tkinter. May have text rendering issues on some macOS systems.

**Original borderless version:**
```bash
/usr/bin/python3 chr_flow.py
```

**Debug version with visible window:**
```bash
/usr/bin/python3 chr_flow_test.py
```

**Known Issues:**
- Text may not render properly with transparency enabled
- Cannot penetrate fullscreen presentation layers
- Background color may not display correctly on some systems