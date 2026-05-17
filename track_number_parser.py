import argparse
from typing import Optional, Tuple

class TrackNumberParser:

    @staticmethod
    def validate_and_normalize(
        track_num: Optional[str], 
        max_tracks: Optional[int] = None, 
        allow_zero: bool = False  # CERINȚA: Parametrul 3
    ) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        
        if not track_num:
            return None, None, "empty input"

        track_str = str(track_num).strip()

        if not track_str:
            return None, None, "empty input"
        
        if "/" in track_str:
            parts = track_str.split("/")
            try:
                cur_str = ""
                for c in parts[0]:
                    if c.isdigit():
                        cur_str += c
                        
                tot_str = ""
                for c in parts[1]:
                    if c.isdigit():
                        tot_str += c

                current = int(cur_str)
                total = int(tot_str)
            except (ValueError, IndexError):
                return None, None, "parse error"

            if 0 in (current, total) and allow_zero is False:
                return None, None, "zero not allowed"
        else:
            digits = ""
            for c in track_str:
                if c.isdigit():
                    digits += c
                    
            if not digits:
                return None, None, "parse error"
            
            current = int(digits)
            total = None
            
            if current == 0 and allow_zero is False:
                return None, None, "zero not allowed"
            
        if total is not None and current > total:
            return None, None, "current exceeds total"

        if max_tracks is not None:
            if total is not None and total > max_tracks:
                return None, None, "total exceeds max"
            elif total is None and current > max_tracks:
                return None, None, "current exceeds max"

        return current, total, None
    
    @staticmethod
    def pad_track(track_number: Optional[int]) -> str:
        """Adăugată pentru compatibilitate cu audio_utils.py"""
        if not isinstance(track_number, int):
            return ""
        return f"{track_number:02d}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="run the class"
    )
    parser.add_argument("track_num", nargs="?", help="Track number to parse")
    parser.add_argument("max_tracks", nargs="?", type=int, help="Optional maximum track count")
    args = parser.parse_args()

    if args.track_num is None:
        samples = [
            ("3", None),
            ("3/10", None),
            ("track3/album10", None),
            ("0", None),
        ]
        for track_num, max_tracks in samples:
            result = TrackNumberParser.validate_and_normalize(track_num, max_tracks)
            print(f"input={track_num!r}, max_tracks={max_tracks!r} -> {result}")
        return

    result = TrackNumberParser.validate_and_normalize(args.track_num, args.max_tracks)
    print(result)


if __name__ == "__main__":
    main()