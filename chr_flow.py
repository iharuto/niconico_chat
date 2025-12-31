#!/usr/bin/env python3
"""
Stage 4: Multi-Lane Non-Looping Queue System
Purpose: Display multiple text messages without looping, maximum 5 simultaneous texts.

Features:
- Up to 5 texts displayed simultaneously on different rows
- No looping - texts scroll once from right to left and disappear
- Queue management - new texts appear automatically as lanes free up
- Transparent overlay with click-through
- Based on Stage 2 (transparent overlay)

Run: /usr/bin/python3 chr_flow_pyobjc_stage4.py
Exit: Press ESC
"""

import objc
from Foundation import NSObject, NSMakeRect, NSMakeSize
from AppKit import (
    NSApplication,
    NSWindow,
    NSTextField,
    NSColor,
    NSFont,
    NSTimer,
    NSFloatingWindowLevel,
    NSEvent,
    NSKeyDown,
    NSBorderlessWindowMask,
    NSBackingStoreBuffered,
    NSShadow,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
)
from PyObjCTools import AppHelper

# Configuration
NUM_LANES = 5  # Maximum simultaneous texts
LANE_HEIGHT = 80  # Vertical spacing between lanes (pixels)
LANE_START_Y = 150  # First lane Y position from top

SPEED = 6  # Pixels per frame
INTERVAL = 0.016  # ~60fps (16ms)
ALPHA = 1.0  # Window transparency (0.0-1.0)

# Calculate lane Y positions (from top of screen)
LANE_POSITIONS = [LANE_START_Y + (i * LANE_HEIGHT) for i in range(NUM_LANES)]


class TextMessage(NSObject):
    """Represents a single scrolling text message."""

    def initWithText_lane_screenWidth_yPosition_(self, text, lane_id, screen_width, y_pos):
        self = objc.super(TextMessage, self).init()
        if self is None:
            return None

        self.text = text
        self.lane_id = lane_id
        self.screen_width = screen_width
        self.x_position = float(screen_width)  # Start at right edge
        self.is_active = True

        # Create text field
        self.text_field = NSTextField.alloc().initWithFrame_(
            NSMakeRect(screen_width, y_pos, 2000, 60)
        )
        self.text_field.setStringValue_(text)
        self.text_field.setFont_(NSFont.boldSystemFontOfSize_(48))
        self.text_field.setTextColor_(NSColor.whiteColor())
        self.text_field.setBezeled_(False)
        self.text_field.setDrawsBackground_(False)
        self.text_field.setEditable_(False)
        self.text_field.setSelectable_(False)

        # Add shadow for readability
        shadow = NSShadow.alloc().init()
        shadow.setShadowOffset_(NSMakeSize(2, -2))
        shadow.setShadowBlurRadius_(4)
        shadow.setShadowColor_(NSColor.blackColor())
        self.text_field.setShadow_(shadow)

        # Calculate text width for off-screen detection
        attributed_string = self.text_field.attributedStringValue()
        self.text_width = attributed_string.size().width

        return self

    def updateWithSpeed_(self, speed):
        """Update X position, return False if off-screen (should be removed)."""
        self.x_position -= speed

        frame = self.text_field.frame()
        frame.origin.x = self.x_position
        self.text_field.setFrame_(frame)

        # Check if completely off-screen (no looping!)
        if self.x_position < -self.text_width:
            self.is_active = False
            return False
        return True


class LaneManager(NSObject):
    """Manages lane availability and assignment."""

    def init(self):
        self = objc.super(LaneManager, self).init()
        if self is None:
            return None

        self.num_lanes = NUM_LANES
        self.available_lanes = list(range(NUM_LANES))  # [0, 1, 2, 3, 4]
        return self

    def get_available_lane(self):
        """Get an available lane ID, or None if all lanes occupied."""
        if self.available_lanes:
            return self.available_lanes.pop(0)
        return None

    def releaseLane_(self, lane_id):
        """Mark a lane as available again."""
        if lane_id not in self.available_lanes:
            self.available_lanes.append(lane_id)
            self.available_lanes.sort()


class ScrollController(NSObject):
    """Controller for managing multiple non-looping text messages."""

    def initWithWindow_screenWidth_screenHeight_(self, window, screen_width, screen_height):
        self = objc.super(ScrollController, self).init()
        if self is None:
            return None

        self.window = window
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.speed = SPEED

        # Active text messages (currently scrolling)
        self.active_messages = []

        # Message queue (waiting to be displayed)
        self.message_queue = []

        # Lane manager
        self.lane_manager = LaneManager.alloc().init()

        return self

    def loadMessages_(self, messages):
        """Load a list of messages into the queue."""
        self.message_queue.extend(messages)
        print(f"Loaded {len(messages)} messages into queue")

    def tick_(self, timer):
        """Animation tick - update all active messages and manage queue."""

        # Update all active messages
        messages_to_remove = []
        for msg in self.active_messages:
            if not msg.updateWithSpeed_(self.speed):
                # Message is off-screen
                messages_to_remove.append(msg)

        # Remove off-screen messages
        for msg in messages_to_remove:
            msg.text_field.removeFromSuperview()
            self.active_messages.remove(msg)
            self.lane_manager.releaseLane_(msg.lane_id)
            print(f"Lane {msg.lane_id} freed: '{msg.text[:30]}...'")

        # Try to load next message from queue if lane available
        while self.message_queue and len(self.active_messages) < NUM_LANES:
            lane_id = self.lane_manager.get_available_lane()
            if lane_id is not None:
                text = self.message_queue.pop(0)
                self.spawnMessage_inLane_(text, lane_id)
            else:
                break

    def spawnMessage_inLane_(self, text, lane_id):
        """Spawn a new text message in the specified lane."""
        # Convert lane ID to Y position (from top to macOS bottom-origin)
        y_from_top = LANE_POSITIONS[lane_id]
        y_pos = self.screen_height - y_from_top - 60

        # Create message
        message = TextMessage.alloc().initWithText_lane_screenWidth_yPosition_(
            text, lane_id, self.screen_width, y_pos
        )

        # Add to window
        self.window.contentView().addSubview_(message.text_field)

        # Track active message
        self.active_messages.append(message)
        print(f"Lane {lane_id} spawned: '{text[:30]}...'")


def create_window():
    """Create and configure the transparent overlay window."""
    from AppKit import NSScreen
    screen = NSScreen.mainScreen()
    screen_frame = screen.frame()

    # Full screen width and height
    window_height = screen_frame.size.height
    x = 0
    y = 0

    # Create borderless window
    window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
        NSMakeRect(x, y, screen_frame.size.width, window_height),
        NSBorderlessWindowMask,
        NSBackingStoreBuffered,
        False
    )

    # Configure transparency
    window.setBackgroundColor_(NSColor.clearColor())
    window.setOpaque_(False)
    window.setAlphaValue_(ALPHA)
    window.setHasShadow_(False)

    # Set window level (above normal windows)
    window.setLevel_(NSFloatingWindowLevel + 1)

    # Enable click-through (ignore mouse events)
    window.setIgnoresMouseEvents_(True)

    # Appear on all Spaces and stay stationary
    window.setCollectionBehavior_(
        NSWindowCollectionBehaviorCanJoinAllSpaces |
        NSWindowCollectionBehaviorStationary
    )

    return window, screen_frame.size.width, screen_frame.size.height


def setup_keyboard_handler(app):
    """Set up ESC key handler for clean exit."""
    def keyboard_handler(event):
        if event.keyCode() == 53:  # ESC key
            print("\nESC pressed - exiting...")
            app.terminate_(None)
        return event

    NSEvent.addLocalMonitorForEventsMatchingMask_handler_(
        NSKeyDown,
        keyboard_handler
    )


def main():
    """Main application entry point."""
    # Create shared application instance
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(0)  # NSApplicationActivationPolicyRegular

    # Create window
    window, screen_width, screen_height = create_window()

    # Create scroll controller
    controller = ScrollController.alloc().initWithWindow_screenWidth_screenHeight_(
        window, screen_width, screen_height
    )

    # Define messages to display
    messages = [
        "First message  最初のメッセージ",
        "Second message  二番目のメッセージ",
        "Third message  三番目のメッセージ",
        "Fourth message  四番目のメッセージ",
        "Fifth message  五番目のメッセージ",
        "Sixth message (waits for lane)  六番目のメッセージ",
        "Seventh message  七番目のメッセージ",
        "Final message  最後のメッセージ",
    ]

    # Load messages into queue
    controller.loadMessages_(messages)

    # Start animation timer
    NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
        INTERVAL,
        controller,
        "tick:",
        None,
        True
    )

    # Set up keyboard handler
    setup_keyboard_handler(app)

    # Show window and start event loop
    window.makeKeyAndOrderFront_(None)
    app.activateIgnoringOtherApps_(True)

    print("\n=== Stage 4 running (MULTI-LANE NON-LOOPING) ===")
    print(f"- Maximum {NUM_LANES} texts displayed simultaneously")
    print(f"- {len(messages)} messages in queue")
    print(f"- Lane positions: {LANE_POSITIONS}")
    print("- Texts scroll once and disappear (NO LOOPING)")
    print("- Transparent overlay with click-through")
    print("- Press ESC to exit")
    print("\nStarting...\n")

    AppHelper.runEventLoop()


if __name__ == "__main__":
    main()
