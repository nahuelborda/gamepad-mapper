#!/usr/bin/env python3
"""
USB Gamepad Mapper for Mac
Detects gamepad input and maps buttons to keyboard shortcuts
"""

import json
import time
import threading
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import pygame
from pynput import keyboard
from pynput.keyboard import Key, Controller

class GamepadMapper:
    def __init__(self, config_file: str = "gamepad_config.json"):
        self.config_file = Path(config_file)
        self.keyboard_controller = Controller()
        self.running = False
        self.gamepad = None
        self.config = self.load_config()
        
        # Initialize pygame for gamepad support
        pygame.init()
        pygame.joystick.init()
        
    def load_config(self) -> Dict[str, Any]:
        """Load button mapping configuration from JSON file"""
        if not self.config_file.exists():
            # Create default configuration
            default_config = {
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
                "auto_restart": True
            }
            self.save_config(default_config)
            return default_config
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Error loading config from {self.config_file}")
            return {}
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save button mapping configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def detect_gamepad(self) -> Optional[int]:
        """Detect and return the first available gamepad"""
        pygame.joystick.quit()
        pygame.joystick.init()
        
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                name = joystick.get_name().lower()
                
                # Common gamepad identifiers
                if any(keyword in name for keyword in ['gamepad', 'controller', 'xbox', 'playstation', 'nintendo']):
                    print(f"Found gamepad: {joystick.get_name()}")
                    return i
        
        return None
    
    def get_key_from_string(self, key_string: str):
        """Convert string representation to pynput Key or character"""
        key_mapping = {
            'space': ' ',
            'return': Key.enter,
            'escape': Key.esc,
            'tab': Key.tab,
            'f11': Key.f11,
            'f12': Key.f12,
            'ctrl': Key.ctrl,
            'shift': Key.shift,
            'alt': Key.alt,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'insert': Key.insert,
            'delete': Key.delete,
            'backspace': Key.backspace
        }
        
        return key_mapping.get(key_string, key_string)
    
    def press_key(self, key_string: str) -> None:
        """Press a key based on the string representation"""
        key = self.get_key_from_string(key_string)
        try:
            self.keyboard_controller.press(key)
            time.sleep(0.05)  # Brief press
            self.keyboard_controller.release(key)
        except Exception as e:
            print(f"Error pressing key {key_string}: {e}")
    
    def handle_button_press(self, button_name: str) -> None:
        """Handle button press events"""
        if button_name in self.config.get("button_mappings", {}):
            key_mapping = self.config["button_mappings"][button_name]
            print(f"Button {button_name} pressed -> {key_mapping}")
            self.press_key(key_mapping)
    
    def run_gamepad_loop(self) -> None:
        """Main gamepad input loop"""
        if not self.gamepad:
            return
        
        joystick = pygame.joystick.Joystick(self.gamepad)
        joystick.init()
        
        print(f"Gamepad connected: {joystick.get_name()}")
        print("Button mappings:")
        for button, key in self.config.get("button_mappings", {}).items():
            print(f"  {button} -> {key}")
        print("Press Ctrl+C to exit")
        
        # Track button states to avoid repeated presses
        button_states = {}
        trigger_states = {"left": False, "right": False}
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    button_name = self.get_button_name(event.button)
                    if button_name and button_name not in button_states:
                        button_states[button_name] = True
                        self.handle_button_press(button_name)
                
                elif event.type == pygame.JOYBUTTONUP:
                    button_name = self.get_button_name(event.button)
                    if button_name:
                        button_states[button_name] = False
                
                elif event.type == pygame.JOYAXISMOTION:
                    # Handle triggers (usually axes 2 and 3)
                    if event.axis in [2, 3]:  # Common trigger axes
                        trigger_name = "left" if event.axis == 2 else "right"
                        threshold = self.config.get("trigger_threshold", 0.5)
                        
                        if abs(event.value) > threshold:
                            if not trigger_states[trigger_name]:
                                trigger_states[trigger_name] = True
                                self.handle_button_press(f"{trigger_name.upper()}_TRIGGER")
                        else:
                            trigger_states[trigger_name] = False
                    
                    # Handle D-pad (if mapped to axes)
                    elif event.axis in [0, 1]:  # X and Y axes
                        threshold = 0.5
                        if abs(event.value) > threshold:
                            if event.axis == 0:  # X axis
                                if event.value > threshold:
                                    self.handle_button_press("DPAD_RIGHT")
                                elif event.value < -threshold:
                                    self.handle_button_press("DPAD_LEFT")
                            elif event.axis == 1:  # Y axis
                                if event.value > threshold:
                                    self.handle_button_press("DPAD_DOWN")
                                elif event.value < -threshold:
                                    self.handle_button_press("DPAD_UP")
            
            time.sleep(1.0 / self.config.get("polling_rate", 60))
    
    def get_button_name(self, button_id: int) -> Optional[str]:
        """Map button ID to button name"""
        # Common button mappings (may vary by controller)
        button_mapping = {
            0: "A",
            1: "B", 
            2: "X",
            3: "Y",
            4: "LEFT_TRIGGER",
            5: "RIGHT_TRIGGER",
            6: "SELECT",
            7: "START",
            8: "LEFT_STICK",
            9: "RIGHT_STICK"
        }
        return button_mapping.get(button_id)
    
    def start(self) -> None:
        """Start the gamepad mapper"""
        self.running = True
        
        while self.running:
            # Try to detect gamepad
            gamepad_id = self.detect_gamepad()
            
            if gamepad_id is not None:
                self.gamepad = gamepad_id
                self.run_gamepad_loop()
            else:
                print("No gamepad detected. Waiting for connection...")
                time.sleep(2)
                
                if not self.config.get("auto_restart", True):
                    break
    
    def stop(self) -> None:
        """Stop the gamepad mapper"""
        self.running = False
        pygame.quit()

def main():
    """Main entry point"""
    print("USB Gamepad Mapper for Mac")
    print("==========================")
    
    mapper = GamepadMapper()
    
    try:
        mapper.start()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        mapper.stop()

if __name__ == "__main__":
    main() 