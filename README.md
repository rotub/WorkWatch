# WorkWatch 🎬

**Auto-capture WIP clips while you work.** WorkWatch is a lightweight Python script that monitors your active window and tells OBS Studio to save short replay clips whenever you're working in Unity, Blender, or Substance Painter. No manual recording — clips just pile up in a folder, ready for sharing on social media.

Built by an indie game dev who kept forgetting to hit record.

---

## How It Works

1. **OBS Studio** runs in the background with its Replay Buffer holding the last 30 seconds of your screen in memory
2. **WorkWatch** polls your active window every 5 seconds
3. When it detects a target app (Unity, Blender, Substance Painter), it starts tracking your session
4. After 1 minute of continuous focus, it saves the first clip — then every 15 minutes after that
5. You get a Windows toast notification each time a clip is saved

Alt-tab away and the session pauses. Come back and the tracking resumes. Completely hands-off.

---

## Quick Start

### 1. Requirements

- Windows 10/11
- Python 3.10+
- [OBS Studio 28+](https://obsproject.com/) (free)

### 2. Install dependencies

```bash
pip install obsws-python pywin32 plyer
```

### 3. Configure OBS

- **Tools → WebSocket Server Settings** → Enable (default port 4455)
- **Settings → Output → Replay Buffer** → Enable, set to **30 seconds**
- **Settings → Output → Recording** → Set format to **MP4**, choose a recording folder
- Add a **Source** (Display Capture or Window Capture)
- Click **Start Replay Buffer**

### 4. Run

```bash
python WorkWatch.py
```

Leave the terminal open in the background. `Ctrl+C` to stop.

---

## Auto-Start on Boot

### OBS

1. Find OBS in the **Start Menu** → right-click → **Open file location**
2. Copy the shortcut
3. `Win + R` → type `shell:startup` → Enter
4. Paste the shortcut, then right-click it → **Properties**
5. Add to the **Target** field after the closing quote:

```
--startreplaybuffer --minimize-to-tray
```

Full target should look something like:

```
"C:\Program Files\obs-studio\bin\64bit\obs64.exe" --startreplaybuffer --minimize-to-tray
```

### WorkWatch

1. `Win + R` → type `shell:startup` → Enter
2. Create a shortcut in that folder with this target:

```
C:\Windows\System32\cmd.exe /k timeout /t 15 /nobreak && "C:\path\to\python.exe" "C:\path\to\WorkWatch.py"
```

The 15-second delay gives OBS time to start first. Use the full path to your Python executable to avoid issues with multiple Python installs (`where python` to find it).

---

## Configuration

Edit the variables at the top of `WorkWatch.py`:

| Setting | Default | Description |
|---|---|---|
| `TARGET_APPS` | `unity`, `blender`, `substance painter` | Window title keywords that trigger recording (case-insensitive) |
| `SAVE_INTERVAL` | `15 * 60` (15 min) | Seconds between clip saves |
| `MIN_ACTIVE_TIME` | `60` (1 min) | Seconds of focus required before first save |
| `POLL_INTERVAL` | `5` | How often the script checks your active window (seconds) |
| `OBS_HOST` | `localhost` | OBS WebSocket host |
| `OBS_PORT` | `4455` | OBS WebSocket port |
| `OBS_PASSWORD` | `""` | OBS WebSocket password (leave empty if not set) |

---

## Troubleshooting

**"obsws-python not installed"** — You likely have multiple Python installs. Use `python -m pip install obsws-python` and make sure your startup shortcut uses the full path to the correct `python.exe`. Run `where python` to check.

**"Could not connect to OBS"** — Make sure OBS is running and WebSocket Server is enabled under Tools → WebSocket Server Settings. Check the port matches.

**"Failed to save replay buffer"** — The Replay Buffer needs to be actively running in OBS (not just enabled in settings). Click **Start Replay Buffer** in the OBS main window, or enable auto-start under Settings → General → Automatically start replay buffer.

**No clips appearing** — Check your OBS recording path under Settings → Output → Recording → Recording Path. That's where clips are saved.

---

## Contributing

Contributions welcome! Some ideas:

- **More app support** — Godot, Aseprite, Photoshop, Krita, etc.
- **System tray icon** — Run as a tray app instead of a terminal window
- **Date-sorted folders** — Automatically organise clips into daily subfolders
- **macOS / Linux support** — Active window detection for other platforms
- **Auto-upload** — Push clips directly to TikTok or YouTube
- **Smarter triggers** — Save clips on scene changes, play mode toggles, file saves, etc.

### Adding a new target app

The simplest contribution — just add the app's window title keyword to the `TARGET_APPS` list:

```python
TARGET_APPS = [
    "unity",
    "blender",
    "substance painter",
    "substance 3d painter",
    "godot",        # add new apps here
    "aseprite",
]
```

The keyword is matched case-insensitively against the active window title.

---

## License

MIT — do whatever you want with it.

---

Made by [Rotub Games](https://rotub.games)
