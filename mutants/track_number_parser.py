from typing import Optional, Tuple
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore

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
    
    @staticmethod
    def pad_track(track_number: Optional[int]) -> str:
        """Adăugată pentru compatibilitate cu audio_utils.py"""
        if track_number is None:
            return ""
        return f"{track_number:02d}"