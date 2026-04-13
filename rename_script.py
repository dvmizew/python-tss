import os
import argparse
import re
import sys
from mutagen import File as MutagenFile

# --- 1. PLATFORM COMPATIBILITY ---
IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform == "linux"

SUPPORTED_EXTS = [".flac", ".mp3", ".m4a", ".ogg", ".wav"]

def sanitize_name(name):
    """Clean name for filesystem."""
    if not name:
        return ""
    
    # Windows-specific character replacement logic
    if IS_WINDOWS:
        name = str(name).replace(':', ' - ').replace('?', '')
        invalid_chars = '<>"/\\|*'
        for char in invalid_chars:
            name = name.replace(char, '_')
    else:
        # Linux is more lenient but we still want clean names
        name = str(name).replace('/', '_').replace('\x00', '')
        
    # Windows: trailing dots are problematic. Linux: they are allowed.
    if IS_WINDOWS:
        return name.strip().rstrip('.')
    return name.strip()

def sync_lrc_metadata(lrc_path, artist, title):
    """Update internal [ar:] and [ti:] tags in the .lrc file."""
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

        # If tags weren't found at all, we can prepend them
        header_additions = []
        if not ar_found: header_additions.append(f"[ar:{artist}]\n")
        if not ti_found: header_additions.append(f"[ti:{title}]\n")
        
        if header_additions:
            new_lines = header_additions + new_lines
            
        with open(lrc_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    except Exception:
        return False

def build_new_filename(track_num, title, ext):
    """Build standardized filename from tags: 'NN - Title.ext'."""
    if not title:
        return None

    clean_title = sanitize_name(title)
    
    # Extract track number part (e.g., "14" from "14/20")
    if track_num and "/" in track_num:
        track_num = track_num.split("/")[0]
    
    # Keep only digits
    if track_num and not track_num.isdigit():
        track_num = ''.join(ch for ch in track_num if ch.isdigit())
    
    # Format with leading zero if numeric
    if track_num and track_num.isdigit():
        track_num = f"{int(track_num):02d}"
        new_name = f"{track_num} - {clean_title}{ext}"
    else:
        new_name = f"{clean_title}{ext}"
    
    return new_name

def rename_album_folder(folder_path, artist, album, dry_run=False):
    """Rename the folder to 'Artist - Album' format."""
    parent_dir = os.path.dirname(folder_path)

    new_folder_name = sanitize_name(f"{artist} - {album}")
    if not new_folder_name:
        return folder_path

    new_folder_path = os.path.join(parent_dir, new_folder_name)
    
    if os.path.abspath(folder_path) == os.path.abspath(new_folder_path):
        return folder_path

    if os.path.exists(new_folder_path):
        print(f"⚠️  Folder destination {new_folder_name} already exists, skipping folder rename.")
        return folder_path

    if dry_run:
        print(f"[DRY-RUN] Folder: {os.path.basename(folder_path)} → {new_folder_name}")
    else:
        try:
            os.rename(folder_path, new_folder_path)
            print(f"📂  {os.path.basename(folder_path)} → {new_folder_name}")
            return new_folder_path
        except Exception as e:
            print(f"❌ Failed to rename folder {os.path.basename(folder_path)}: {e}")
    
    return folder_path

def normalize_track_numbers(root, audio_files, dry_run=False):
    """If an album starts at >1 and is continuous, shift everything so it starts at 01."""
    if not audio_files: return
    
    tracks_info = []
    for f in audio_files:
        path = os.path.join(root, f)
        try:
            audio = MutagenFile(path, easy=True)
            if audio:
                tn = audio.get("tracknumber", [None])[0]
                if tn:
                    # Parse "2/10" -> 2
                    try:
                        tn_clean = str(tn).split('/')[0]
                        tn_int = int("".join(filter(str.isdigit, tn_clean)))
                        tracks_info.append({
                            'path': path,
                            'audio': audio,
                            'old_tn': tn,
                            'tn_int': tn_int
                        })
                    except ValueError: pass
        except: pass

    if not tracks_info: return
    
    tracks_ints = [t['tn_int'] for t in tracks_info]
    min_track = min(tracks_ints)
    max_track = max(tracks_ints)
    num_tracks = len(tracks_info)
    
    # Logic: If it starts at N > 1 AND it's a continuous sequence (no gaps)
    # OR if it's a single track that isn't 1
    should_shift = False
    if min_track > 1:
        if num_tracks == 1:
            should_shift = True
        elif (max_track - min_track + 1) == num_tracks:
            should_shift = True

    if should_shift:
        shift = min_track - 1
        print(f"⚖️  Detecting off-by-{shift} numbering in {os.path.basename(root)}. Normalizing...")
        for t in tracks_info:
            new_tn_int = t['tn_int'] - shift
            # Preserving total if present: "2/10" -> "1/10"
            old_tn_str = str(t['old_tn'])
            if "/" in old_tn_str:
                parts = old_tn_str.split('/')
                total = parts[1]
                # If total is obviously wrong (smaller than new track number), update it or keep it
                try:
                    if int(total) < new_tn_int:
                        total = str(num_tracks) if num_tracks >= new_tn_int else str(new_tn_int)
                except: pass
                new_tn = f"{new_tn_int}/{total}"
            else:
                new_tn = str(new_tn_int)
                
            if dry_run:
                print(f"   [DRY-RUN] Tag Update: {os.path.basename(t['path'])} track {t['old_tn']} -> {new_tn}")
            else:
                try:
                    t['audio']["tracknumber"] = new_tn
                    # Also update tracktotal if it exists in easy tags
                    if "tracktotal" in t['audio']:
                        try:
                            if int(t['audio']["tracktotal"][0]) < new_tn_int:
                                t['audio']["tracktotal"] = str(num_tracks) if num_tracks >= new_tn_int else str(new_tn_int)
                        except: pass
                    t['audio'].save()
                    print(f"   🏷️  Updated Tag: {os.path.basename(t['path'])} track {t['old_tn']} -> {new_tn}")
                except Exception as e:
                    print(f"   ❌ Failed to update tags for {os.path.basename(t['path'])}: {e}")
    else:
        # Second pass: even if it starts at 1, check for track > total errors
        for t in tracks_info:
            old_tn_str = str(t['old_tn'])
            if "/" in old_tn_str:
                parts = old_tn_str.split('/')
                try:
                    curr_track = int("".join(filter(str.isdigit, parts[0])))
                    curr_total = int("".join(filter(str.isdigit, parts[1])))
                    if curr_track > curr_total:
                        new_total = str(num_tracks) if num_tracks >= curr_track else str(curr_track)
                        new_tn = f"{curr_track}/{new_total}"
                        if dry_run:
                            print(f"   [DRY-RUN] Tag Fix (Total): {os.path.basename(t['path'])} {old_tn_str} -> {new_tn}")
                        else:
                            t['audio']["tracknumber"] = new_tn
                            if "tracktotal" in t['audio']:
                                t['audio']["tracktotal"] = new_total
                            t['audio'].save()
                            print(f"   🏷️  Fixed Tag (Total): {os.path.basename(t['path'])} {old_tn_str} -> {new_tn}")
                except: pass

def process_file_rename_only(file_path, dry_run=False):
    """Rename audio file and associated .lrc. Returns (artist, title) for folder renaming."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTS:
        return None, None

    try:
        audio = MutagenFile(file_path, easy=True)
        if not audio:
            return None, None
    except Exception as e:
        print(f"⚠️ Error reading {file_path}: {e}")
        return None, None

    # Extract title, artist, album, track number
    title = audio.get("title", [None])[0]
    aa_list = audio.get("albumartist", audio.get("artist", []))
    artist = " & ".join([str(a) for a in aa_list if a]) if aa_list else "Unknown Artist"
    album = audio.get("album", [title])[0] if audio.get("album") else (title if title else "Unknown Album")
    track_num = audio.get("tracknumber", [None])[0]

    if not title:
        # print(f"⚠️ Missing title for {file_path}, skipping...")
        return artist, album, None

    new_name = build_new_filename(track_num, title, ext)
    folder = os.path.dirname(file_path)
    new_path = os.path.join(folder, new_name)

    # Lyrics extensions to check
    LRC_EXTS = [".lrc", ".txt"]
    
    def _get_existing_lrc(base_path):
        for e in LRC_EXTS:
            if os.path.exists(base_path + e): return base_path + e, e
        return None, None

    old_lrc_path, old_lrc_ext = _get_existing_lrc(os.path.splitext(file_path)[0])
    new_lrc_base = os.path.splitext(new_path)[0]
    new_lrc = new_lrc_base + ".lrc" # Always target .lrc for Symfonium

    # FALLBACK: Use Regex to find the lyric file if the standard path doesn't exist
    if not old_lrc_path and track_num:
        tn_clean = str(track_num).split('/')[0].strip()
        tn_digits = "".join(filter(str.isdigit, tn_clean))
        
        if tn_digits:
            tn_prefix = f"{int(tn_digits):02d}"
            tn_alt = str(int(tn_digits)) # Non-padded version (e.g. '1' instead of '01')
            
            # Normalize title for regex (remove special chars, replace spaces with .*)
            clean_title_reg = re.sub(r'[^a-zA-Z0-9]', ' ', str(title)).strip()
            title_parts = [re.escape(p) for p in clean_title_reg.split() if len(p) > 2]
            
            # Pattern 1: Track number + Title parts (high confidence)
            # Pattern 2: Just track number with separators (fallback)
            patterns = []
            for tn in [tn_prefix, tn_alt]:
                if title_parts:
                    patterns.append(re.compile(rf".*{tn}.*{'.*'.join(title_parts)}.*", re.I))
                patterns.append(re.compile(rf".*[\s\-_]{tn}[\s\-_].*", re.I))
                patterns.append(re.compile(rf"^{tn}[\s\-_].*", re.I))
                patterns.append(re.compile(rf"^{tn} .* ", re.I)) # Handle '1 Title.lrc'

            folder = os.path.dirname(file_path)
            for cand in os.listdir(folder):
                if any(cand.lower().endswith(e) for e in LRC_EXTS):
                    if cand == os.path.basename(new_lrc): continue
                    
                    for pat in patterns:
                        if pat.match(cand):
                            print(f"   🔍 Potential LRC match: {cand} (Pattern: {pat.pattern})")
                            old_lrc_path = os.path.join(folder, cand)
                            old_lrc_ext = os.path.splitext(cand)[1]
                            break
                    if old_lrc_path: break

    # Always sync metadata if LRC exists, regardless of rename
    lrc_to_sync = new_lrc if os.path.exists(new_lrc) else (old_lrc_path if old_lrc_path and os.path.exists(old_lrc_path) else None)
    if lrc_to_sync and lrc_to_sync.lower().endswith('.lrc'):
        if not dry_run:
            sync_lrc_metadata(lrc_to_sync, artist, title)
        else:
            print(f"   [DRY-RUN] 📝 Would sync metadata for {os.path.basename(lrc_to_sync)}")

    if os.path.abspath(file_path) != os.path.abspath(new_path):
        if os.path.exists(new_path):
            print(f"⚠️  Destination {new_name} already exists, skipping file rename.")
        else:
            if dry_run:
                print(f"[DRY-RUN] {os.path.basename(file_path)} → {new_name}")
                if old_lrc_path:
                    print(f"   [DRY-RUN] 🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)}")
            else:
                try:
                    os.rename(file_path, new_path)
                    print(f"✅ {os.path.basename(file_path)} → {new_name}")
                    
                    if old_lrc_path and os.path.exists(old_lrc_path) and os.path.abspath(old_lrc_path) != os.path.abspath(new_lrc):
                        if os.path.exists(new_lrc):
                            os.remove(old_lrc_path)
                            print(f"   🗑️  Removed redundant {os.path.basename(old_lrc_path)} (target already exists)")
                        else:
                            os.rename(old_lrc_path, new_lrc)
                            print(f"   🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)}")
                except Exception as e:
                    print(f"❌ Failed to rename {os.path.basename(file_path)}: {e}")
    else:
        # File name matches, but check if LRC needs renaming
        if old_lrc_path and os.path.exists(old_lrc_path) and not os.path.exists(new_lrc) and os.path.abspath(old_lrc_path) != os.path.abspath(new_lrc):
            if dry_run:
                print(f"[DRY-RUN] 🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)} (Sync rename)")
            else:
                try:
                    os.rename(old_lrc_path, new_lrc)
                    print(f"✅ 🔹 {os.path.basename(old_lrc_path)} → {os.path.basename(new_lrc)} (Sync rename)")
                except Exception as e:
                    print(f"⚠️ Failed to sync LRC rename {os.path.basename(old_lrc_path)}: {e}")
    
    return artist, album, title

def main():
    parser = argparse.ArgumentParser(description="Rename audio files and folders based on metadata.")
    parser.add_argument("directory", nargs="?", default=".", help="Music directory")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--normalize-tracks", action="store_true", help="Fix shifted track numbers (e.g. 2,3,4 -> 1,2,3)")
    args = parser.parse_args()

    print(f"🔍 Scanning {args.directory} for files to rename...")
    for root, dirs, files in os.walk(args.directory, topdown=True):
        # Skip hidden directories like .venv
        dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.', '..']]
            
        audio_files = [f for f in files if any(f.lower().endswith(ext) for ext in SUPPORTED_EXTS)]
        if not audio_files:
            continue

        folder_artist, folder_album, folder_title = None, None, None
        
        # Normalize numbering if requested
        if args.normalize_tracks:
            normalize_track_numbers(root, audio_files, dry_run=args.dry_run)
        
        # Process all files in this folder FIRST
        for f in audio_files:
            print(f"📄 Processing: {f}")
            art, alb, tit = process_file_rename_only(os.path.join(root, f), dry_run=args.dry_run)
            
            # Standardize artist string for folder naming
            if art:
                # If art is a list (from some tagging backends), join it.
                # If it's a string, split by common delimiters and rejoin with ' & '
                if isinstance(art, list):
                    parts = [str(p).strip() for p in art if p]
                else:
                    parts = [p.strip() for p in re.split(r'[;,/]', str(art)) if p.strip()]
                
                # Deduplicate while preserving order
                seen = set()
                art = " & ".join([p for p in parts if not (p.lower() in seen or seen.add(p.lower()))])
            
            if not folder_artist: folder_artist = art
            if not folder_album: folder_album = alb
            if not folder_title: folder_title = tit

        # Rename the folder based on metadata
        if folder_artist and folder_album:
            rename_album_folder(root, folder_artist, folder_album, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
