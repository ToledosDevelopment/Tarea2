import json
from pathlib import Path

class JSONHelper:
    def __init__(self, json_path):
        """Initialize with a JSON file path"""
        self.json_path = Path(json_path)
        self.current = {}
        
        try:
            # Load existing JSON or create new file if it doesn't exist
            if self.json_path.exists():
                with open(self.json_path, 'r') as f:
                    self.current = json.load(f)
            else:
                self.current = {}
                self.save_to_file()
        except json.JSONDecodeError:
            # If file exists but has invalid JSON, create new empty JSON
            self.current = {}
            self.save_to_file()
    
    def save_to_file(self):
        """Save current JSON to file"""
        with open(self.json_path, 'w') as f:
            json.dump(self.current, f, indent=2)
    
    def get_value(self, path):
        """Get a value using dot notation path"""
        current = self.current
        keys = path.split('.')
        
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return None
            current = current[key]
        
        return current
    
    def set_value(self, path, value):
        """Set a value using dot notation path"""
        keys = path.split('.')
        current = self.current
        
        # Create nested dictionaries if they don't exist
        for key in keys[:-1]:
            current.setdefault(key, {})
            current = current[key]
        
        current[keys[-1]] = value
        self.save_to_file()