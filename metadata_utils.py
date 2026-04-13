"""
Metadata extraction and track normalization utilities.
"""
from typing import Optional, Tuple
from audio_utils import AudioMetadata


class MetadataExtractor:
    """Extracts metadata from audio files using mutagen."""
    
    @staticmethod
    def extract_from_mutagen(audio) -> AudioMetadata:
        """
        Extract metadata from mutagen audio object.
        
        Args:
            audio: Mutagen Audio object
            
        Returns:
            AudioMetadata instance
        """
        if not audio:
            return AudioMetadata()
        
        try:
            title = audio.get("title", [None])[0]
            
            # Try albumartist first, fall back to artist
            aa_list = audio.get("albumartist", audio.get("artist", []))
            artist_parts = [str(a) for a in aa_list if a] if aa_list else []
            artist = " & ".join(artist_parts) if artist_parts else "Unknown Artist"
            
            album = audio.get("album", [None])[0] or title or "Unknown Album"
            track_number = audio.get("tracknumber", [None])[0]
            
            return AudioMetadata(
                title=title,
                artist=artist,
                album=album,
                track_number=track_number
            )
        except Exception:
            return AudioMetadata()


class TrackNumberNormalizer:
    """Normalizes track numbering across an album."""
    
    @staticmethod
    def should_normalize(track_numbers: list) -> Tuple[bool, Optional[int]]:
        """
        Determine if normalization is needed and calculate shift.
        
        Args:
            track_numbers: List of track numbers (integers)
            
        Returns:
            Tuple of (should_normalize, shift_amount)
        """
        if not track_numbers:
            return False, None
        
        sorted_tracks = sorted(track_numbers)
        min_track = sorted_tracks[0]
        max_track = sorted_tracks[-1]
        num_tracks = len(track_numbers)
        
        # Check if it's a continuous sequence
        is_continuous = (max_track - min_track + 1) == num_tracks
        
        # Should normalize if starts > 1 and continuous, or is single track != 1
        if min_track > 1:
            if num_tracks == 1 or is_continuous:
                return True, min_track - 1
        
        return False, None
    
    @staticmethod
    def apply_shift(current: int, total: Optional[int] = None, shift: int = 0) -> Tuple[int, Optional[int]]:
        """
        Apply shift to track number.
        
        Args:
            current: Current track number
            total: Total tracks
            shift: Amount to shift
            
        Returns:
            Tuple of (new_current, new_total)
        """
        new_current = current - shift
        new_total = total
        
        # Update total if track exceeds it
        if total and new_current > total:
            new_total = new_current
        
        return new_current, new_total
