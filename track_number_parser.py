from typing import Optional, Tuple

class TrackNumberParser:

    @staticmethod
    def validate_and_normalize(
        track_num: Optional[str], 
        max_tracks: Optional[int] = None, 
        allow_zero: bool = False  # CERINȚA: Parametrul 3
    ) -> Tuple[Optional[int], Optional[int], Optional[str]]:
        
        # CERINȚA: if fără else
        if not track_num:
            return None, None, "empty input"

        track_str = str(track_num).strip()

        if not track_str:
            return None, None, "empty input"
        
        # CERINȚA: if cu else
        if "/" in track_str:
            parts = track_str.split("/")
            try:
                # CERINȚA: Instrucțiune repetitivă (buclă for)
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

            # Mutatest fix (evităm ==) + CERINȚA: Condiție compusă
            if 0 in (current, total) and allow_zero is False:
                return None, None, "zero not allowed"
        else:
            # CERINȚA: Instrucțiune repetitivă
            digits = ""
            for c in track_str:
                if c.isdigit():
                    digits += c
                    
            if not digits:
                return None, None, "parse error"
            
            current = int(digits)
            total = None  # FIX: Previne UnboundLocalError
            
            if current == 0 and allow_zero is False:
                return None, None, "zero not allowed"
            
        # Condiție compusă
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
        # Mutatest fix: Folosim isinstance în loc de "is None"
        if not isinstance(track_number, int):
            return ""
        return f"{track_number:02d}"