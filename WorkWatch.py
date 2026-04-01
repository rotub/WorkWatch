"""
WIP Clipper — Automatic dev clip saver for TikTok WIP posts
============================================================
Monitors your active window for Unity, Blender, and Substance Painter.
When you've been working in one of those apps, it tells OBS to save
a replay buffer clip every 15 minutes.

Requirements:
    pip install obsws-python pywin32 plyer

OBS Setup:
    1. Open OBS Studio
    2. Go to Tools → WebSocket Server Settings → Enable
    3. Note your port (default 4455) and password
    4. Go to Settings → Output → Replay Buffer → Enable
    5. Set "Maximum Replay Time" to 30 seconds
    6. Start Replay Buffer (in the main OBS window or via hotkey)

Usage:
    python wip_clipper.py
"""

import time
import sys
import os
import logging
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG — tweak these to your liking
# ---------------------------------------------------------------------------
OBS_HOST = "localhost"
OBS_PORT = 4455
OBS_PASSWORD = ""  # Leave empty if you didn't set one in OBS

# Window title keywords (case-insensitive) — if ANY of these appear
# in the active window title, we consider it a "working" window.
TARGET_APPS = [
    "unity",
    "blender",
    "substance painter",
    "substance 3d painter",
]

# How often to save a clip (in seconds)
SAVE_INTERVAL = 15 * 60  # 15 minutes

# Minimum continuous work time before first clip is saved (seconds).
# Prevents saving a clip if you just alt-tabbed through briefly.
MIN_ACTIVE_TIME = 60  # 1 minute

# How often the script checks your active window (seconds)
POLL_INTERVAL = 5

# Where to save clips — set this in OBS under:
#   Settings → Output → Replay Buffer → Recording Path
# The script just tells OBS to save; OBS decides where the file goes.

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("wip_clipper")

# ---------------------------------------------------------------------------
# PLATFORM-SPECIFIC: get the active window title
# ---------------------------------------------------------------------------
def get_active_window_title() -> str:
    """Return the title of the currently focused window."""
    if sys.platform == "win32":
        import win32gui
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)
    elif sys.platform == "darwin":
        # macOS fallback (requires pyobjc)
        try:
            from AppKit import NSWorkspace
            app = NSWorkspace.sharedWorkspace().activeApplication()
            return app.get("NSApplicationName", "")
        except ImportError:
            return ""
    else:
        # Linux fallback
        try:
            import subprocess
            out = subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                stderr=subprocess.DEVNULL,
            )
            return out.decode().strip()
        except Exception:
            return ""


def is_target_app(title: str) -> bool:
    """Check if the window title matches one of our target apps."""
    title_lower = title.lower()
    return any(app in title_lower for app in TARGET_APPS)


def matched_app(title: str) -> str:
    """Return which target app matched, for logging."""
    title_lower = title.lower()
    for app in TARGET_APPS:
        if app in title_lower:
            return app.title()
    return ""


# ---------------------------------------------------------------------------
# OBS CONNECTION
# ---------------------------------------------------------------------------
def connect_obs():
    """Connect to OBS WebSocket and return the client."""
    try:
        import obsws_python as obs
    except ImportError:
        log.error("obsws-python not installed. Run: pip install obsws-python")
        sys.exit(1)

    try:
        client = obs.ReqClient(
            host=OBS_HOST,
            port=OBS_PORT,
            password=OBS_PASSWORD if OBS_PASSWORD else None,
        )
        log.info("Connected to OBS WebSocket on %s:%s", OBS_HOST, OBS_PORT)
        return client
    except Exception as e:
        log.error("Could not connect to OBS: %s", e)
        log.error("Make sure OBS is running and WebSocket Server is enabled.")
        sys.exit(1)


def save_replay(client) -> bool:
    """Tell OBS to save the replay buffer. Returns True on success."""
    try:
        client.save_replay_buffer()
        return True
    except Exception as e:
        log.warning("Failed to save replay buffer: %s", e)
        log.warning("Is Replay Buffer running in OBS?")
        return False


# ---------------------------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------------------------
def notify(clip_number: int, app_name: str):
    """Show a Windows toast notification when a clip is saved."""
    try:
        from plyer import notification
        notification.notify(
            title="WIP Clipper 🎬",
            message=f"Clip #{clip_number} saved from {app_name}",
            app_name="WIP Clipper",
            timeout=5,  # disappears after 5 seconds
        )
    except Exception as e:
        log.debug("Notification failed (non-critical): %s", e)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------
def main():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║       WIP Clipper — Running 🎬       ║")
    print("  ╠══════════════════════════════════════╣")
    print("  ║  Watching: Unity, Blender,           ║")
    print("  ║           Substance Painter          ║")
    print("  ║  Clip length:  30 sec (set in OBS)   ║")
    print("  ║  Save every:   15 min of work        ║")
    print("  ║  Press Ctrl+C to stop                ║")
    print("  ╚══════════════════════════════════════╝")
    print()

    client = connect_obs()

    # State tracking
    active_start = None          # When current work session began
    last_save_time = None        # When we last saved a clip
    total_clips_saved = 0
    current_app = ""

    try:
        while True:
            title = get_active_window_title()
            now = time.time()

            if is_target_app(title):
                app_name = matched_app(title)

                # Just started working?
                if active_start is None:
                    active_start = now
                    current_app = app_name
                    log.info("🟢 Detected %s — tracking work session", app_name)
                elif app_name != current_app:
                    current_app = app_name
                    log.info("🔄 Switched to %s", app_name)

                # How long have we been working?
                active_duration = now - active_start

                # Have we been working long enough?
                if active_duration >= MIN_ACTIVE_TIME:
                    # Time to save a clip?
                    should_save = False

                    if last_save_time is None:
                        # First clip of this session
                        should_save = True
                    elif (now - last_save_time) >= SAVE_INTERVAL:
                        # Interval elapsed
                        should_save = True

                    if should_save:
                        if save_replay(client):
                            last_save_time = now
                            total_clips_saved += 1
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            log.info(
                                "💾 Clip #%d saved! (%s in %s)",
                                total_clips_saved,
                                timestamp,
                                current_app,
                            )
                            notify(total_clips_saved, current_app)
            else:
                # Not in a target app
                if active_start is not None:
                    duration = now - active_start
                    mins = int(duration // 60)
                    log.info(
                        "🔴 Left %s (session was %d min). Pausing tracker.",
                        current_app,
                        mins,
                    )
                    active_start = None
                    current_app = ""
                    # Keep last_save_time so we don't double-save
                    # when switching back quickly

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print()
        log.info("Stopped. Saved %d clips this session.", total_clips_saved)


if __name__ == "__main__":
    main()