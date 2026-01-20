"""
State Manager
Handles incremental saving of data processing progress (Checkpointing).
"""
import json
import os
from typing import Any, Dict, Set

class StateManager:
    """
    Manages the state of data processing to allow fault tolerance.
    Saves progress to a JSON file after every N records or significant action.
    """
    
    def __init__(self, project_path: str, state_file: str = "enrichment_progress.json"):
        self.state_dir = os.path.join(project_path, "data", "state")
        self.state_path = os.path.join(self.state_dir, state_file)
        self.processed_ids: Set[str] = set()
        self.data: Dict[str, Any] = {}
        
        self._ensure_dir()
        self._load_state()
        
    def _ensure_dir(self):
        """Ensure state directory exists"""
        os.makedirs(self.state_dir, exist_ok=True)
        
    def _load_state(self):
        """Load state from disk if exists"""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                    self.processed_ids = set(self.data.keys())
                # print(f"Loaded state: {len(self.processed_ids)} items processed")
            except Exception as e:
                print(f"Warning: Failed to load state: {e}")
                self.data = {}
                self.processed_ids = set()
        else:
            self.data = {}
            self.processed_ids = set()

    def is_processed(self, record_id: str) -> bool:
        """Check if a record has already been processed"""
        return record_id in self.processed_ids
    
    def get_processed_data(self, record_id: str) -> Dict[str, Any]:
        """Get the processed data for a record"""
        return self.data.get(record_id, {})

    def mark_processed(self, record_id: str, result_data: Dict[str, Any]):
        """
        Mark a record as processed and save state immediately (or could buffer)
        """
        self.processed_ids.add(record_id)
        self.data[record_id] = result_data
        self._save_state()
        
    def _save_state(self):
        """Save current state to disk"""
        try:
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving state: {e}")

    def clear_state(self):
        """Clear the state file (reset)"""
        if os.path.exists(self.state_path):
            os.remove(self.state_path)
        self.data = {}
        self.processed_ids = set()
