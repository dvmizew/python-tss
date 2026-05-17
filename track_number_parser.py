from typing import Optional, Tuple

class TrackNumberParser:

    @staticmethod
    def validate_and_normalize(track_num: Optional[str],max_tracks: Optional[int] = None) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        if not track_num:
            return None, None, "empty input"

        track_str = str(track_num).strip()

        if not track_str:
            return None, None, "empty input"
        
        current: Optional[int] = None
        total: Optional[int] = None

        if "/" in track_str:
            parts = track_str.split("/")
            try:
                current = int("".join(c for c in parts[0] if c.isdigit()))
                total = int("".join(c for c in parts[1] if c.isdigit()))
            except (ValueError, IndexError):
                return None, None, "parse error"

            if current == 0 or total == 0:
                return None, None, "zero not allowed"
        else:
            digits = "".join(c for c in track_str if c.isdigit())
            if not digits:
                return None, None, "parse error"
            current = int(digits)
            if current == 0:
                return None, None, "zero not allowed"
            
        if total is not None and current > total:
            return None, None, "current exceeds total"

        if max_tracks is not None:
            if total is not None and total > max_tracks:
                return None, None, "total exceeds max"
            elif total is None and current > max_tracks:
                return None, None, "current exceeds max"

        return current, total, None