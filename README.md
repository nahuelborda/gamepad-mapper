# USB Gamepad Mapper for Mac

A Python script that automatically detects USB gamepad connections and maps button presses to keyboard shortcuts. Perfect for creating custom shortcuts with your gamepad!

## Features

- **Automatic Detection**: Automatically starts when a gamepad is plugged in
- **Auto-Restart**: Restarts when the gamepad is unplugged and plugged back in
- **Configurable Mappings**: Easy JSON configuration for button-to-key mappings
- **Support for Common Controllers**: Works with Xbox, PlayStation, Nintendo, and generic USB gamepads
- **D-pad Support**: Maps directional pad to arrow keys
- **Trigger Support**: Maps left and right triggers to modifier keys

## Supported Buttons

- **A, B, X, Y buttons**: Main action buttons
- **START/SELECT buttons**: Menu and select buttons
- **D-pad**: Up, Down, Left, Right arrows
- **Left/Right Triggers**: Analog triggers
- **Left/Right Sticks**: Analog stick buttons (if available)

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Make the launcher executable**:
   ```bash
   chmod +x gamepad_launcher.sh
   ```

## Usage

### Option 1: Auto-Launcher (Recommended)

Run the auto-launcher script that monitors for gamepad connections:

```bash
./gamepad_launcher.sh
```

This will:
- Monitor for USB gamepad connections
- Automatically start the mapper when a gamepad is detected
- Stop the mapper when the gamepad is disconnected
- Restart when the gamepad is reconnected

### Option 2: Manual Start

Run the Python script directly:

```bash
python3 gamepad_mapper.py
```

## Configuration

Edit `gamepad_config.json` to customize your button mappings:

```json
{
  "button_mappings": {
    "A": "space",
    "B": "escape",
    "X": "return",
    "Y": "tab",
    "START": "f11",
    "SELECT": "f12",
    "LEFT_TRIGGER": "ctrl",
    "RIGHT_TRIGGER": "shift",
    "DPAD_UP": "up",
    "DPAD_DOWN": "down",
    "DPAD_LEFT": "left",
    "DPAD_RIGHT": "right"
  },
  "trigger_threshold": 0.5,
  "polling_rate": 60,
  "auto_restart": true
}
```

### Available Keys

You can map buttons to any of these keys:
- **Function keys**: `f1`, `f2`, `f3`, ..., `f12`
- **Arrow keys**: `up`, `down`, `left`, `right`
- **Modifier keys**: `ctrl`, `shift`, `alt`, `cmd`
- **Special keys**: `space`, `return`, `escape`, `tab`, `backspace`
- **Navigation keys**: `home`, `end`, `page_up`, `page_down`
- **Any character**: `a`, `b`, `c`, `1`, `2`, `3`, etc.

### Configuration Options

- **trigger_threshold**: Sensitivity for analog triggers (0.0 to 1.0)
- **polling_rate**: How often to check for input (Hz)
- **auto_restart**: Whether to restart when gamepad is reconnected

## Troubleshooting

### Gamepad Not Detected

1. Check if your gamepad is recognized by macOS:
   ```bash
   system_profiler SPUSBDataType | grep -i "gamepad\|controller"
   ```

2. Try the alternative detection method:
   ```bash
   ioreg -p IOUSB -l | grep -i "gamepad\|controller"
   ```

### Button Mappings Not Working

1. Check the log file for errors:
   ```bash
   tail -f gamepad_mapper.log
   ```

2. Your gamepad might use different button IDs. Try pressing buttons and check the console output to see which button IDs are being detected.

3. Edit the `get_button_name()` method in `gamepad_mapper.py` to match your specific controller.

### Permission Issues

On macOS, you may need to grant accessibility permissions:

1. Go to System Preferences > Security & Privacy > Privacy > Accessibility
2. Add Terminal (or your terminal app) to the list
3. Check the box to allow control

## Running at Startup

To run the launcher automatically when you log in:

1. Open System Preferences > Users & Groups
2. Select your user account
3. Click "Login Items"
4. Click the "+" button and add the `gamepad_launcher.sh` script

## Files

- `gamepad_mapper.py`: Main Python script
- `gamepad_config.json`: Button mapping configuration
- `gamepad_launcher.sh`: Auto-launcher script
- `requirements.txt`: Python dependencies
- `gamepad_mapper.log`: Log file (created automatically)

## License

This project is open source. Feel free to modify and distribute as needed. 