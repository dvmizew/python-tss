"""
Utility classes for audio file processing and metadata management.
"""
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional, Tuple, List
from track_number_parser import TrackNumberParser

IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform == "linux"

SUPPORTED_EXTS = [".flac", ".mp3", ".m4a", ".ogg", ".wav"]
LRC_EXTS = [".lrc", ".txt"]


@dataclass
class AudioMetadata:
    """Container for audio metadata."""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    track_number: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if metadata has minimum required fields."""
        return bool(self.title)


class FileNameSanitizer:
    """Cleans filenames for filesystem compatibility."""
    
    def __init__(self, is_windows: bool = IS_WINDOWS):
        """
        Args:
            is_windows: Whether to apply Windows-specific sanitization
        """
        self.is_windows = is_windows
    
    def sanitize(self, name: str) -> str:
        """
        Clean name for filesystem.
        
        Args:
            name: Original name
            
        Returns:
            Sanitized name
        """
        if not name:
            return ""
        
        name = str(name)
        
        if self.is_windows:
            return self._sanitize_windows(name)
        else:
            return self._sanitize_unix(name)
    
    def _sanitize_windows(self, name: str) -> str:
        """Apply Windows-specific sanitization."""
        # Replace problematic characters
        name = name.replace(':', ' - ').replace('?', '')
        
        invalid_chars = '<>"/\\|*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # trailing dots are problematic
        return name.strip().rstrip('.')
    
    def _sanitize_unix(self, name: str) -> str:
        """Apply Unix-specific sanitization."""
        # Unix is more lenient
        name = name.replace('/', '_').replace('\x00', '')
        return name.strip()


# class TrackNumberParser:
#     """Parses and manipulates track numbers."""
    
#     @staticmethod
#     def parse(track_num: Optional[str]) -> Tuple[Optional[int], Optional[int]]:
#         """
#         Parse track number.
        
#         Args:
#             track_num: Track number (e.g., "5" or "5/12")
            
#         Returns:
#             Tuple of (track_num, total_tracks) or (None, None)
#         """
#         if not track_num:
#             return None, None
        
#         track_str = str(track_num).strip()
        
#         if "/" in track_str:
#             parts = track_str.split("/")
#             try:
#                 current = int("".join(c for c in parts[0] if c.isdigit()))
#                 total = int("".join(c for c in parts[1] if c.isdigit()))
#                 return current, total
#             except (ValueError, IndexError):
#                 return None, None
#         else:
#             try:
#                 current = int("".join(c for c in track_str if c.isdigit()))
#                 return current, None
#             except ValueError:
#                 return None, None
    
#     @staticmethod
#     def format_track(current: int, total: Optional[int] = None) -> str:
#         """
#         Format track number.
        
#         Args:
#             current: Current track number
#             total: Total tracks (optional)
            
#         Returns:
#             Formatted track string
#         """
#         if total is not None:
#             return f"{current}/{total}"
#         return str(current)
    
#     @staticmethod
#     def pad_track(track_num: int) -> str:
#         """Pad track number with leading zero if needed."""
#         return f"{track_num:02d}"


class AudioFileNameBuilder:
    """Builds standardized audio filenames from metadata."""
    
    def __init__(self, sanitizer: Optional[FileNameSanitizer] = None):
        """
        Args:
            sanitizer: FileNameSanitizer instance (creates default if None)
        """
        self.sanitizer = sanitizer or FileNameSanitizer()
    
    def build_filename(self, 
                       title: str, 
                       track_number: Optional[str] = None,
                       extension: str = ".mp3") -> Optional[str]:
        """
        Build standardized filename: 'NN - Title.ext' or 'Title.ext'
        
        Args:
            title: Song title
            track_number: Track number (e.g., "5" or "5/12")
            extension: File extension
            
        Returns:
            Formatted filename or None if title is invalid
        """
        if not title:
            return None
        
        if not extension.startswith('.'):
            extension = '.' + extension
        
        clean_title = self.sanitizer.sanitize(title)
        if not clean_title:
            return None
        
        # Parse track number
        current_track, _ = TrackNumberParser.parse(track_number)
        
        if current_track:
            padded_track = TrackNumberParser.pad_track(current_track)
            return f"{padded_track} - {clean_title}{extension}"
        else:
            return f"{clean_title}{extension}"


class FolderNameBuilder:
    """Builds standardized folder names."""
    
    def __init__(self, sanitizer: Optional[FileNameSanitizer] = None):
        """
        Args:
            sanitizer: FileNameSanitizer instance (creates default if None)
        """
        self.sanitizer = sanitizer or FileNameSanitizer()
    
    def build_folder_name(self, artist: str, album: str) -> Optional[str]:
        """
        Build folder name: 'Artist - Album'
        
        Args:
            artist: Artist name
            album: Album name
        
        Returns:
            Formatted folder name or None if invalid
        """
        if not artist or not album:
            return None
        
        name = f"{artist} - {album}"
        return self.sanitizer.sanitize(name) or None
    
    @staticmethod
    def standardize_artist(artist: str) -> str:
        """
        Standardize artist string format.
        Handles multiple artists separated by various delimiters.
        
        Args:
            artist: Artist string (may contain multiple artists)
            
        Returns:
            Standardized artist string with ' & ' separator
        """
        if isinstance(artist, list):
            parts = [str(p).strip() for p in artist if p]
        else:
            parts = [p.strip() for p in re.split(r'[;,/]', str(artist)) if p.strip()]
        
        # Deduplicate while preserving order
        seen = set()
        return " & ".join([
            p for p in parts 
            if not (p.lower() in seen or seen.add(p.lower()))
        ])


class LyricsFileFinder:
    """Finds lyrics files by pattern matching."""
    
    @staticmethod
    def find_lyrics_file(base_path: str, folder: str) -> Optional[Tuple[str, str]]:
        """
        Find lyrics file matching base_path.
        
        Args:
            base_path: Base filename without extension (used for exact match)
            folder: Folder to search in
            
        Returns:
            Tuple of (path, extension) or None
        """
        for ext in LRC_EXTS:
            full_path = base_path + ext
            if os.path.exists(full_path):
                return full_path, ext
        
        return None, None
    
    @staticmethod
    def find_lyrics_by_pattern(track_number: Optional[str],
                               title: str,
                               folder: str) -> Optional[Tuple[str, str]]:
        """
        Find lyrics file by regex pattern matching.
        
        Args:
            track_number: Track number
            title: Song title
            folder: Folder to search in
            
        Returns:
            Tuple of (path, extension) or None
        """
        if not track_number or not os.path.isdir(folder):
            return None, None
        
        current_track, _ = TrackNumberParser.parse(track_number)
        if not current_track:
            return None, None
        
        patterns = LyricsFileFinder._build_patterns(current_track, title)
        
        try:
            for candidate in os.listdir(folder):
                if any(candidate.lower().endswith(e) for e in LRC_EXTS):
                    for pattern in patterns:
                        if pattern.match(candidate):
                            full_path = os.path.join(folder, candidate)
                            ext = os.path.splitext(candidate)[1]
                            return full_path, ext
        except OSError:
            pass
        
        return None, None
    
    @staticmethod
    def _build_patterns(track_num: int, title: str) -> List[re.Pattern]:
        """Build regex patterns for lyrics file matching."""
        patterns = []
        tn_padded = f"{track_num:02d}"
        tn_str = str(track_num)
        
        # Normalize title for regex
        clean_title = re.sub(r'[^a-zA-Z0-9]', ' ', str(title)).strip()
        title_parts = [re.escape(p) for p in clean_title.split() if len(p) > 2]
        
        # Build patterns with both padded and non-padded track numbers
        for tn in [tn_padded, tn_str]:
            if title_parts:
                patterns.append(
                    re.compile(rf".*{tn}.*{'.*'.join(title_parts)}.*", re.I)
                )
            patterns.append(re.compile(rf".*[\s\-_]{tn}[\s\-_].*", re.I))
            patterns.append(re.compile(rf"^{tn}[\s\-_].*", re.I))
            patterns.append(re.compile(rf"^{tn} .* ", re.I))
        
        return patterns
