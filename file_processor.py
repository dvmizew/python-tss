"""
File system operations for audio processing.
"""
import os
from typing import Optional, Tuple
from audio_utils import (
    AudioMetadata, 
    AudioFileNameBuilder, 
    FolderNameBuilder,
    LyricsFileFinder,
    SUPPORTED_EXTS
)
from metadata_utils import MetadataExtractor


class LyricsMetadataSynchronizer:
    """Synchronizes metadata with lyrics files."""
    
    @staticmethod
    def sync_lrc_file(lrc_path: str, artist: str, title: str) -> bool:
        """
        Update internal [ar:] and [ti:] tags in .lrc file.
        
        Args:
            lrc_path: Path to .lrc file
            artist: Artist name
            title: Song title
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(lrc_path) or not os.path.isfile(lrc_path):
            return False
        
        try:
            with open(lrc_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            new_lines = []
            ar_found = False
            ti_found = False
            
            for line in lines:
                line_stripped = line.strip()
                if line_stripped.lower().startswith("[ar:"):
                    new_lines.append(f"[ar:{artist}]\n")
                    ar_found = True
                elif line_stripped.lower().startswith("[ti:"):
                    new_lines.append(f"[ti:{title}]\n")
                    ti_found = True
                else:
                    new_lines.append(line)
            
            # Prepend missing tags
            header_additions = []
            if not ar_found:
                header_additions.append(f"[ar:{artist}]\n")
            if not ti_found:
                header_additions.append(f"[ti:{title}]\n")
            
            if header_additions:
                new_lines = header_additions + new_lines
            
            with open(lrc_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            return True
        except Exception:
            return False



class AudioFileRenamer:
    """Handles renaming of audio files and associated lyrics."""
    
    def __init__(self, 
                 dry_run: bool = False,
                 file_name_builder: Optional[AudioFileNameBuilder] = None,
                 lyrics_finder: Optional[LyricsFileFinder] = None):
        """
        Args:
            dry_run: If True, don't actually rename files
            file_name_builder: AudioFileNameBuilder instance
            lyrics_finder: LyricsFileFinder instance
        """
        self.dry_run = dry_run
        self.file_name_builder = file_name_builder or AudioFileNameBuilder()
        self.lyrics_finder = lyrics_finder or LyricsFileFinder()
    
    def rename_file(self, file_path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Rename audio file based on metadata.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (artist, album, title) for folder renaming, or (None, None, None)
        """
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in SUPPORTED_EXTS:
            return None, None, None
        
        # Extract metadata (should be provided by caller or extracted here)
        metadata = self._extract_metadata(file_path)
        if not metadata or not metadata.is_valid():
            return metadata.artist, metadata.album, None
        
        return self._perform_rename(file_path, metadata)
    
    def _extract_metadata(self, file_path: str) -> AudioMetadata:
        """Extract metadata from file."""
        try:
            from mutagen import File as MutagenFile
            audio = MutagenFile(file_path, easy=True)
            return MetadataExtractor.extract_from_mutagen(audio)
        except Exception:
            return AudioMetadata()
    
    def _perform_rename(self, file_path: str, metadata: AudioMetadata) -> Tuple[str, str, str]:
        """Perform the actual file rename."""
        folder = os.path.dirname(file_path)
        ext = os.path.splitext(file_path)[1]
        
        # Build new filename
        new_filename = self.file_name_builder.build_filename(
            metadata.title,
            metadata.track_number,
            ext
        )
        
        if not new_filename:
            return metadata.artist, metadata.album, None
        
        new_path = os.path.join(folder, new_filename)
        
        # Rename file if needed
        if os.path.abspath(file_path) != os.path.abspath(new_path):
            if os.path.exists(new_path):
                print(f"⚠️  Destination {new_filename} already exists, skipping file rename.")
            else:
                if self.dry_run:
                    print(f"[DRY-RUN] {os.path.basename(file_path)} → {new_filename}")
                else:
                    try:
                        os.rename(file_path, new_path)
                        print(f"✅ {os.path.basename(file_path)} → {new_filename}")
                    except Exception as e:
                        print(f"❌ Failed to rename {os.path.basename(file_path)}: {e}")
        
        # Handle lyrics files AFTER file rename
        self._handle_lyrics(file_path, new_path, metadata)
        
        return metadata.artist, metadata.album, metadata.title
    
    def _handle_lyrics(self, old_file_path: str, new_file_path: str, 
                       metadata: AudioMetadata) -> None:
        """Handle lyrics file renaming and synchronization."""
        folder = os.path.dirname(old_file_path)
        old_base = os.path.splitext(old_file_path)[0]
        new_base = os.path.splitext(new_file_path)[0]
        
        # Find existing lyrics file
        old_lrc_path, old_lrc_ext = self.lyrics_finder.find_lyrics_file(old_base, folder)
        
        # Fallback: search by pattern
        if not old_lrc_path:
            old_lrc_path, old_lrc_ext = self.lyrics_finder.find_lyrics_by_pattern(
                metadata.track_number,
                metadata.title,
                folder
            )
        
        new_lrc = new_base + ".lrc"
        
        # Sync metadata if LRC exists
        lrc_to_sync = (new_lrc if os.path.exists(new_lrc) 
                       else (old_lrc_path if old_lrc_path and os.path.exists(old_lrc_path) 
                             else None))
        
        if lrc_to_sync and lrc_to_sync.lower().endswith('.lrc'):
            if not self.dry_run:
                LyricsMetadataSynchronizer.sync_lrc_file(
                    lrc_to_sync,
                    metadata.artist or "Unknown",
                    metadata.title
                )
            else:
                print(f"   [DRY-RUN] 📝 Would sync metadata for {os.path.basename(lrc_to_sync)}")
        
        # Keep behavior aligned with original script: when the audio file is renamed,
        # move/delete corresponding lyric file; otherwise only sync-rename if needed.
        file_was_renamed = os.path.abspath(old_file_path) != os.path.abspath(new_file_path)

        if file_was_renamed:
            if old_lrc_path and os.path.exists(old_lrc_path) and os.path.abspath(old_lrc_path) != os.path.abspath(new_lrc):
                if os.path.exists(new_lrc):
                    if not self.dry_run:
                        os.remove(old_lrc_path)
                    print(f"   🗑️  Removed redundant {os.path.basename(old_lrc_path)}")
                else:
                    if self.dry_run:
                        print(f"   [DRY-RUN] 🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)}")
                    else:
                        try:
                            os.rename(old_lrc_path, new_lrc)
                            print(f"   🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)}")
                        except Exception as e:
                            print(f"⚠️ Failed to rename lyrics: {e}")
        else:
            if old_lrc_path and os.path.exists(old_lrc_path) and not os.path.exists(new_lrc) and os.path.abspath(old_lrc_path) != os.path.abspath(new_lrc):
                if self.dry_run:
                    print(f"   [DRY-RUN] 🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)} (Sync rename)")
                else:
                    try:
                        os.rename(old_lrc_path, new_lrc)
                        print(f"✅ 🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)} (Sync rename)")
                    except Exception as e:
                        print(f"⚠️ Failed to sync LRC rename {os.path.basename(old_lrc_path)}: {e}")


class FolderRenamer:
    """Handles renaming of album folders."""
    
    def __init__(self, dry_run: bool = False, 
                 folder_builder: Optional[FolderNameBuilder] = None):
        """
        Args:
            dry_run: If True, don't actually rename folders
            folder_builder: FolderNameBuilder instance
        """
        self.dry_run = dry_run
        self.folder_builder = folder_builder or FolderNameBuilder()
    
    def rename_folder(self, folder_path: str, artist: str, album: str) -> str:
        """
        Rename folder to 'Artist - Album' format.
        
        Args:
            folder_path: Current folder path
            artist: Artist name
            album: Album name
            
        Returns:
            New folder path (or original if not renamed)
        """
        parent_dir = os.path.dirname(folder_path)
        
        new_folder_name = self.folder_builder.build_folder_name(artist, album)
        if not new_folder_name:
            return folder_path
        
        new_folder_path = os.path.join(parent_dir, new_folder_name)
        
        # Check if already has correct name
        if os.path.abspath(folder_path) == os.path.abspath(new_folder_path):
            return folder_path
        
        # Check if destination already exists
        if os.path.exists(new_folder_path):
            print(f"⚠️  Folder destination {new_folder_name} already exists, skipping.")
            return folder_path
        
        if self.dry_run:
            print(f"[DRY-RUN] Folder: {os.path.basename(folder_path)} → {new_folder_name}")
        else:
            try:
                os.rename(folder_path, new_folder_path)
                print(f"📂  {os.path.basename(folder_path)} → {new_folder_name}")
                return new_folder_path
            except Exception as e:
                print(f"❌ Failed to rename folder {os.path.basename(folder_path)}: {e}")
        
        return folder_path
