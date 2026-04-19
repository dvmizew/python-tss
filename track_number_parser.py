import os
import re
import sys
from dataclasses import dataclass
from typing import Optional, Tuple, List

class TrackNumberParser:
    """Parses and manipulates track numbers."""
    
    @staticmethod
    def parse(track_num: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse track number.
        
        Args:
            track_num: Track number (e.g., "5" or "5/12")
            
        Returns:
            Tuple of (track_num, total_tracks) or (None, None)
        """
        if not track_num:
            return None, None
        
        track_str = str(track_num).strip()
        
        if "/" in track_str:
            parts = track_str.split("/")
            try:
                current = int("".join(c for c in parts[0] if c.isdigit()))
                total = int("".join(c for c in parts[1] if c.isdigit()))
                return current, total
            except (ValueError, IndexError):
                return None, None
        else:
            try:
                current = int("".join(c for c in track_str if c.isdigit()))
                return current, None
            except ValueError:
                return None, None
    
    @staticmethod
    def format_track(current: int, total: Optional[int] = None) -> str:
        """
        Format track number.
        
        Args:
            current: Current track number
            total: Total tracks (optional)
            
        Returns:
            Formatted track string
        """
        if total is not None:
            return f"{current}/{total}"
        return str(current)
    
    @staticmethod
    def pad_track(track_num: int) -> str:
        """Pad track number with leading zero if needed."""
        return f"{track_num:02d}"