"""
Audio file batch processor with metadata management.
"""
import os
import argparse
from typing import List, Optional
from mutagen import File as MutagenFile

from audio_utils import (
    SUPPORTED_EXTS,
    FolderNameBuilder,
    TrackNumberParser,
)
from metadata_utils import MetadataExtractor, TrackNumberNormalizer
from file_processor import AudioFileRenamer, FolderRenamer


class AlbumBatchProcessor:
    """Processes all audio files in an album folder."""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.file_renamer = AudioFileRenamer(dry_run=dry_run)
        self.folder_renamer = FolderRenamer(dry_run=dry_run)
    
    def process_folder(self, folder_path: str, 
                      normalize_tracks: bool = False) -> Optional[str]:
        """
        Process all audio files in a folder.
        
        Args:
            folder_path: Path to folder containing audio files
            normalize_tracks: Whether to normalize track numbers
            
        Returns:
            New folder path after processing (if renamed)
        """
        audio_files = self._find_audio_files(folder_path)
        if not audio_files:
            return folder_path
        
        # Normalize track numbers if requested
        if normalize_tracks:
            self._normalize_all_tracks(folder_path, audio_files)
        
        # Process each file
        folder_artist, folder_album, folder_title = None, None, None
        
        for audio_file in audio_files:
            file_path = os.path.join(folder_path, audio_file)
            print(f"📄 Processing: {audio_file}")
            
            art, alb, tit = self.file_renamer.rename_file(file_path)
            
            # Standardize artist format
            if art:
                art = FolderNameBuilder.standardize_artist(art)
            
            if not folder_artist:
                folder_artist = art
            if not folder_album:
                folder_album = alb
            if not folder_title:
                folder_title = tit
        
        # Rename the folder based on metadata
        if folder_artist and folder_album:
            folder_path = self.folder_renamer.rename_folder(
                folder_path, 
                folder_artist, 
                folder_album
            )
        
        return folder_path
    
    def _find_audio_files(self, folder_path: str) -> List[str]:
        """Find all audio files in folder."""
        try:
            return [
                f for f in os.listdir(folder_path)
                if any(f.lower().endswith(ext) for ext in SUPPORTED_EXTS)
            ]
        except OSError:
            return []
    
    def _normalize_all_tracks(self, folder_path: str, audio_files: List[str]) -> None:
        """Normalize track numbers in all files."""
        track_info = self._collect_track_info(folder_path, audio_files)
        if not track_info:
            return
        
        should_normalize, shift = TrackNumberNormalizer.should_normalize(
            [t['current'] for t in track_info]
        )
        
        if should_normalize and shift:
            print(f"⚖️  Detecting off-by-{shift} numbering in {os.path.basename(folder_path)}. Normalizing...")
            self._apply_track_shift(track_info, shift)
        else:
            # Second pass: check for track > total errors even if no shift needed
            self._fix_track_total_errors(track_info)
    
    def _collect_track_info(self, folder_path: str, audio_files: List[str]) -> List[dict]:
        """Collect track information from audio files."""
        track_info = []
        
        for audio_file in audio_files:
            file_path = os.path.join(folder_path, audio_file)
            try:
                audio = MutagenFile(file_path, easy=True)
                if not audio:
                    continue
                
                metadata = MetadataExtractor.extract_from_mutagen(audio)
                if not metadata.track_number:
                    continue
                
                current, total, _ = TrackNumberParser.validate_and_normalize(metadata.track_number)
                if current:
                    track_info.append({
                        'path': file_path,
                        'audio': audio,
                        'filename': audio_file,
                        'current': current,
                        'total': total,
                        'original_str': str(metadata.track_number)
                    })
            except Exception:
                pass
        
        return track_info
    
    def _apply_track_shift(self, track_info: List[dict], shift: int) -> None:
        """Apply track number shift to all files."""
        for info in track_info:
            try:
                new_current, new_total = TrackNumberNormalizer.apply_shift(
                    info['current'],
                    info['total'],
                    shift
                )
                
                # Format new track number
                if new_total:
                    new_track_str = f"{new_current}/{new_total}"
                else:
                    new_track_str = str(new_current)
                
                if self.dry_run:
                    print(f"   [DRY-RUN] {info['filename']} track "
                          f"{info['original_str']} -> {new_track_str}")
                else:
                    info['audio']["tracknumber"] = new_track_str
                    if "tracktotal" in info['audio'] and new_total:
                        info['audio']["tracktotal"] = str(new_total)
                    info['audio'].save()
                    print(f"   🏷️  {info['filename']} track "
                          f"{info['original_str']} -> {new_track_str}")
            except Exception as e:
                print(f"   ❌ Failed to update {info['filename']}: {e}")
    
    def _fix_track_total_errors(self, track_info: List[dict]) -> None:
        """Fix track > total errors (second pass, even if no shift needed)."""
        num_tracks = len(track_info)
        
        for info in track_info:
            try:
                current = info['current']
                total = info['total']
                
                # Only fix if track > total
                if total and current > total:
                    new_total = num_tracks if num_tracks >= current else current
                    new_track_str = f"{current}/{new_total}"
                    
                    if self.dry_run:
                        print(f"   [DRY-RUN] {info['filename']} track "
                              f"{info['original_str']} -> {new_track_str} (Fix Total)")
                    else:
                        info['audio']["tracknumber"] = new_track_str
                        if "tracktotal" in info['audio']:
                            info['audio']["tracktotal"] = str(new_total)
                        info['audio'].save()
                        print(f"   🏷️  {info['filename']} track "
                              f"{info['original_str']} -> {new_track_str} (Fixed Total)")
            except Exception as e:
                print(f"   ❌ Failed to fix track total for {info['filename']}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Rename audio files and folders based on metadata."
    )
    parser.add_argument("directory", nargs="?", default=".", 
                       help="Music directory")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show changes without applying")
    parser.add_argument("--normalize-tracks", action="store_true", 
                       help="Fix shifted track numbers (e.g. 2,3,4 -> 1,2,3)")
    args = parser.parse_args()
    
    print(f"🔍 Scanning {args.directory} for files to rename...")
    
    processor = AlbumBatchProcessor(dry_run=args.dry_run)
    
    for root, dirs, files in os.walk(args.directory, topdown=True):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.', '..']]
        
        processor.process_folder(root, normalize_tracks=args.normalize_tracks)


if __name__ == "__main__":
    main()
