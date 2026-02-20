"""
Batch state manager for tracking scraping progress across batches.
Handles persistence and status management for batch operations.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class BatchStateManager:
    """Manages batch state and progress tracking"""
    
    STATE_FILE = "batch_state.json"
    
    def __init__(self):
        self.state_file_path = Path(self.STATE_FILE)
        self.ensure_state_file()
    
    def ensure_state_file(self):
        """Create state file if it doesn't exist"""
        if not self.state_file_path.exists():
            initial_state = {
                "last_completed_batch": 0,
                "total_batches": 0,
                "batch_size": 10,
                "current_batch": None,
                "status": "idle",
                "started_at": None,
                "batches": {}
            }
            self._write_state(initial_state)
            logger.info("Created new batch state file")
    
    def _read_state(self) -> Dict[str, Any]:
        """Read current state from file"""
        try:
            with open(self.state_file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading state file: {e}")
            return {}
    
    def _write_state(self, state: Dict[str, Any]):
        """Write state to file"""
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing state file: {e}")
    
    def start_batch_scraping(self, total_batches: int, batch_size: int = 10):
        """Initialize batch scraping"""
        state = self._read_state()
        state.update({
            "total_batches": total_batches,
            "batch_size": batch_size,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "last_completed_batch": 0,
            "current_batch": 1,
            "batches": {}
        })
        self._write_state(state)
        logger.info(f"Started batch scraping: {total_batches} batches of size {batch_size}")
    
    def update_batch_status(self, batch_num: int, status: str, results: Optional[Dict[str, Any]] = None):
        """Update status of a specific batch"""
        state = self._read_state()
        
        if "batches" not in state:
            state["batches"] = {}
        
        batch_key = str(batch_num)
        state["batches"][batch_key] = {
            "status": status,
            "completed_at": datetime.now().isoformat() if status == "completed" else None,
            "results": results
        }
        
        if status == "completed":
            state["last_completed_batch"] = batch_num
        
        state["current_batch"] = batch_num
        self._write_state(state)
        logger.info(f"Updated batch {batch_num} status to {status}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current batch scraping status"""
        state = self._read_state()
        
        if state.get("status") == "idle":
            return {
                "status": "idle",
                "message": "No batch scraping in progress"
            }
        
        total_batches = state.get("total_batches", 0)
        last_completed = state.get("last_completed_batch", 0)
        progress_percent = (last_completed / total_batches * 100) if total_batches > 0 else 0
        
        return {
            "status": state.get("status"),
            "current_batch": state.get("current_batch"),
            "total_batches": total_batches,
            "completed_batches": last_completed,
            "progress_percent": round(progress_percent, 2),
            "started_at": state.get("started_at"),
            "batch_size": state.get("batch_size"),
            "batches": state.get("batches", {})
        }
    
    def mark_complete(self):
        """Mark batch scraping as complete"""
        state = self._read_state()
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        self._write_state(state)
        logger.info("Batch scraping marked as complete")
    
    def reset_state(self):
        """Reset state for new batch run"""
        self.ensure_state_file()
        logger.info("Batch state reset")
