from track_number_parser import TrackNumberParser


# pytest test_track_number_parser.py::TestEquivalenceClasses -v
class TestEquivalenceClasses:

    # C1 Input absent (None)
    def test_none_input_returns_empty_input_error(self):
        assert TrackNumberParser.validate_and_normalize(None, None) == (None, None, "empty input")

    # C2 Input gol ("")
    def test_empty_string_returns_empty_input_error(self):
        assert TrackNumberParser.validate_and_normalize("", None) == (None, None, "empty input")

    # C3 Input doar spatii
    def test_whitespace_only_returns_empty_input_error(self):
        assert TrackNumberParser.validate_and_normalize("   ", None) == (None, None, "empty input")

    # C4 Fara cifra in string
    def test_letters_only_returns_parse_error(self):
        assert TrackNumberParser.validate_and_normalize("abc", None) == (None, None, "parse error")

    # C5 Current este zero (format simplu)
    def test_current_zero_simple_format_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("0", None) == (None, None, "zero not allowed")

    # C6 Current este zero (format cu slash)
    def test_current_zero_slash_format_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("0/10", None) == (None, None, "zero not allowed")

    # C7 Total este zero
    def test_total_zero_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("3/0", None) == (None, None, "zero not allowed")

    # C8 Current depaseste total
    def test_current_exceeds_total_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("7/3", None) == (None, None, "current exceeds total")

    # C9 Total depaseste max_tracks
    def test_total_exceeds_max_tracks_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("3/15", 10) == (None, None, "total exceeds max")

    # C10 Current depaseste max_tracks
    def test_current_exceeds_max_tracks_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("8", 5) == (None, None, "current exceeds max")

    # C11 Format simplu valid
    def test_simple_format_returns_current_only(self):
        assert TrackNumberParser.validate_and_normalize("5", None) == (5, None, None)

    # C12 Format slash valid
    def test_slash_format_returns_current_and_total(self):
        assert TrackNumberParser.validate_and_normalize("3/10", None) == (3, 10, None)

    # C13 Litere si cifre amestecate
    def test_mixed_letters_and_digits_extracts_number(self):
        assert TrackNumberParser.validate_and_normalize("track3", None) == (3, None, None)

    # C14 Valid cu max_tracks respectat (cu total)
    def test_slash_format_within_max_tracks_is_valid(self):
        assert TrackNumberParser.validate_and_normalize("3/10", 10) == (3, 10, None)

    # C15 Valid cu max_tracks respectat (fara total)
    def test_simple_format_within_max_tracks_is_valid(self):
        assert TrackNumberParser.validate_and_normalize("5", 10) == (5, None, None)


# pytest test_track_number_parser.py::TestBoundaryValues -v
class TestBoundaryValues:

    # F1 Current sub limita minima (zero)
    def test_current_below_minimum_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("0", None) == (None, None, "zero not allowed")

    # F2 Current exact pe limita minima
    def test_current_at_minimum_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("1", None) == (1, None, None)

    # F3 Current peste limita minima
    def test_current_above_minimum_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("2", None) == (2, None, None)

    # F4 Total sub limita minima (zero)
    def test_total_below_minimum_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("3/0", None) == (None, None, "zero not allowed")

    # F5 Total exact pe limita minima
    def test_total_at_minimum_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("1/1", None) == (1, 1, None)

    # F6 Total peste limita minima
    def test_total_above_minimum_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("1/2", None) == (1, 2, None)

    # F7 Current sub total cu o unitate
    def test_current_one_below_total_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("4/5", None) == (4, 5, None)

    # F8 Current egal cu total
    def test_current_equal_to_total_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("5/5", None) == (5, 5, None)

    # F9 Current depaseste total cu o unitate
    def test_current_one_above_total_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("6/5", None) == (None, None, "current exceeds total")

    # F10 Total sub max_tracks cu o unitate
    def test_total_one_below_max_tracks_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("3/9", 10) == (3, 9, None)

    # F11 Total egal cu max_tracks
    def test_total_equal_to_max_tracks_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("3/10", 10) == (3, 10, None)

    # F12 Total depaseste max_tracks cu o unitate
    def test_total_one_above_max_tracks_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("3/11", 10) == (None, None, "total exceeds max")

    # F13 Current sub max_tracks cu o unitate (fara total)
    def test_current_one_below_max_tracks_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("9", 10) == (9, None, None)

    # F14 Current egal cu max_tracks
    def test_current_equal_to_max_tracks_returns_valid(self):
        assert TrackNumberParser.validate_and_normalize("10", 10) == (10, None, None)

    # F15 Current depaseste max_tracks cu o unitate
    def test_current_one_above_max_tracks_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("11", 10) == (None, None, "current exceeds max")


# pytest test_track_number_parser.py::TestStatementCoverage -v
# python3 -m coverage run --source=track_number_parser -m pytest test_track_number_parser.py::TestStatementCoverage
# python3 -m coverage report -m
class TestStatementCoverage:

    # SC1 Nod 7, 8
    def test_none_input_covers_empty_return(self):
        assert TrackNumberParser.validate_and_normalize(None, None) == (None, None, "empty input")

    # SC2 Nod 7, 10, 12, 13
    def test_whitespace_input_covers_strip_and_empty_return(self):
        assert TrackNumberParser.validate_and_normalize("   ", None) == (None, None, "empty input")

    # SC3 Nod 7, 10, 12, 15-16, 18, 19, 21-22, 24
    def test_slash_only_covers_parse_exception_return(self):
        assert TrackNumberParser.validate_and_normalize("//", None) == (None, None, "parse error")

    # SC4 Nod 7, 10, 12, 15-16, 18, 19, 21-22, 26, 27
    def test_zero_current_slash_format_covers_zero_return(self):
        assert TrackNumberParser.validate_and_normalize("0/10", None) == (None, None, "zero not allowed")

    # SC5 Nod 7, 10, 12, 15-16, 18, 29, 30, 31
    def test_letters_only_covers_no_digits_return(self):
        assert TrackNumberParser.validate_and_normalize("abc", None) == (None, None, "parse error")

    # SC6 Nod 7, 10, 12, 15-16, 18, 29, 30, 32, 33, 34
    def test_zero_simple_format_covers_zero_return(self):
        assert TrackNumberParser.validate_and_normalize("0", None) == (None, None, "zero not allowed")

    # SC7 Nod 7, 10, 12, 15-16, 18, 19, 21-22, 26, 36, 37
    def test_current_exceeds_total_covers_exceeds_total_return(self):
        assert TrackNumberParser.validate_and_normalize("7/3", None) == (None, None, "current exceeds total")

    # SC8 Nod 7, 10, 12, 15-16, 18, 19, 21-22, 26, 36, 39, 40, 41
    def test_total_exceeds_max_covers_exceeds_max_return(self):
        assert TrackNumberParser.validate_and_normalize("3/15", 10) == (None, None, "total exceeds max")

    # SC9 Nod 7, 10, 12, 15-16, 18, 29, 30, 32, 33, 36, 39, 40, 42, 43
    def test_current_exceeds_max_covers_exceeds_max_return(self):
        assert TrackNumberParser.validate_and_normalize("8", 5) == (None, None, "current exceeds max")

    # SC10 Nod 7, 10, 12, 15-16, 18, 19, 21-22, 26, 36, 39, 45
    def test_valid_slash_format_covers_success_return(self):
        assert TrackNumberParser.validate_and_normalize("3/10", None) == (3, 10, None)

# pytest test_track_number_parser.py::TestBranchCoverage -v
class TestBranchCoverage:

    # D1 True: not track_num
    def test_none_input_decision_true_returns_empty_input(self):
        assert TrackNumberParser.validate_and_normalize(None, None) == (None, None, "empty input")

    # D1 False / D2 True: not track_str
    def test_whitespace_input_decision_true_returns_empty_input(self):
        assert TrackNumberParser.validate_and_normalize("   ", None) == (None, None, "empty input")

    # D2 False / D3 True / D4 True: "/" in track_str, exceptie aruncata
    def test_slash_only_decision_true_returns_parse_error(self):
        assert TrackNumberParser.validate_and_normalize("//", None) == (None, None, "parse error")

    # D4 False / D5 True: cur==0 or tot==0
    def test_zero_current_slash_format_decision_true_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("0/10", None) == (None, None, "zero not allowed")

    # D3 False / D6 True: not digits
    def test_letters_only_decision_true_returns_parse_error(self):
        assert TrackNumberParser.validate_and_normalize("abc", None) == (None, None, "parse error")

    # D6 False / D7 True: cur==0
    def test_zero_simple_format_decision_true_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("0", None) == (None, None, "zero not allowed")

    # D5 False / D8 True: cur > tot
    def test_current_exceeds_total_decision_true_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("7/3", None) == (None, None, "current exceeds total")

    # D8 False / D9 True / D10 True: max_tracks not None, tot > max
    def test_total_exceeds_max_tracks_decision_true_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("3/15", 10) == (None, None, "total exceeds max")

    # D7 False / D9 False / D11 True: cur > max, tot is None
    def test_current_exceeds_max_tracks_decision_true_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("8", 5) == (None, None, "current exceeds max")

    # D9 False: max_tracks is None
    def test_valid_slash_format_no_max_tracks_decision_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10", None) == (3, 10, None)

    # D10 False / D11 False: tot <= max, cur <= max
    def test_valid_slash_format_within_max_tracks_decisions_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10", 10) == (3, 10, None)


# pytest test_track_number_parser.py::TestConditionCoverage -v
class TestConditionCoverage:

    # CC1 
    def test_none_input_condition_true_returns_empty_input(self):
        assert TrackNumberParser.validate_and_normalize(None, None) == (None, None, "empty input")

    # CC2 
    def test_whitespace_input_condition_true_returns_empty_input(self):
        assert TrackNumberParser.validate_and_normalize("   ", None) == (None, None, "empty input")

    # CC3 
    def test_slash_only_condition_true_returns_parse_error(self):
        assert TrackNumberParser.validate_and_normalize("//", None) == (None, None, "parse error")

    # CC4 
    def test_letters_only_condition_true_returns_parse_error(self):
        assert TrackNumberParser.validate_and_normalize("abc", None) == (None, None, "parse error")

    # CC5 
    def test_zero_current_slash_format_condition_true_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("0/10", None) == (None, None, "zero not allowed")

    # CC6 
    def test_current_exceeds_total_condition_true_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("7/3", None) == (None, None, "current exceeds total")

    # CC7 
    def test_total_zero_condition_true_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("3/0", None) == (None, None, "zero not allowed")

    # CC8 
    def test_zero_simple_format_condition_true_returns_zero_error(self):
        assert TrackNumberParser.validate_and_normalize("0", None) == (None, None, "zero not allowed")

    # CC9 
    def test_current_exceeds_max_no_total_condition_true_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("8", 5) == (None, None, "current exceeds max")

    # CC10 
    def test_total_exceeds_max_tracks_condition_true_returns_error(self):
        assert TrackNumberParser.validate_and_normalize("3/15", 10) == (None, None, "total exceeds max")

    # CC11 
    def test_valid_slash_format_no_max_tracks_condition_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10", None) == (3, 10, None)

    # CC12 
    def test_valid_slash_format_within_max_tracks_condition_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10", 10) == (3, 10, None)

    # CC13 
    def test_valid_simple_format_within_max_tracks_condition_false(self):
        assert TrackNumberParser.validate_and_normalize("3", 10) == (3, None, None)

# pytest test_track_number_parser.py::TestIndependentCircuits -v
class TestIndependentCircuits:

    # Circuit a: 7, 8
    def test_none_input_covers_circuit_a(self):
        assert TrackNumberParser.validate_and_normalize(None, None) == (None, None, "empty input")

    # Circuit b: 7, 10, 12, 13
    def test_whitespace_input_covers_circuit_b(self):
        assert TrackNumberParser.validate_and_normalize("   ", None) == (None, None, "empty input")

    # Circuit c: 7, 10, 12, 15-16, 18, 19, 21-22, 24
    def test_slash_only_covers_circuit_c(self):
        assert TrackNumberParser.validate_and_normalize("//", None) == (None, None, "parse error")

    # Circuit d: 7, 10, 12, 15-16, 18, 19, 21-22, 26, 27
    def test_zero_current_slash_format_covers_circuit_d(self):
        assert TrackNumberParser.validate_and_normalize("0/10", None) == (None, None, "zero not allowed")

    # Circuit e: 7, 10, 12, 15-16, 18, 29, 30, 31
    def test_letters_only_covers_circuit_e(self):
        assert TrackNumberParser.validate_and_normalize("abc", None) == (None, None, "parse error")

    # Circuit f: 7, 10, 12, 15-16, 18, 29, 30, 32, 33, 34
    def test_zero_simple_format_covers_circuit_f(self):
        assert TrackNumberParser.validate_and_normalize("0", None) == (None, None, "zero not allowed")

    # Circuit g: 7, 10, 12, 15-16, 18, 19, 21-22, 26, 36, 37
    def test_current_exceeds_total_covers_circuit_g(self):
        assert TrackNumberParser.validate_and_normalize("7/3", None) == (None, None, "current exceeds total")

    # Circuit i: 7, 10, 12, 15-16, 18, 19, 21-22, 26, 36, 39, 45
    def test_valid_slash_no_max_covers_circuit_i(self):
        assert TrackNumberParser.validate_and_normalize("3/10", None) == (3, 10, None)

    # Circuit j: 7, 10, 12, 15-16, 18, 29, 30, 32, 33, 36, 39, 45 — TEST NOU
    def test_valid_simple_no_max_covers_circuit_j(self):
        assert TrackNumberParser.validate_and_normalize("5", None) == (5, None, None)

    # Circuit k: 7, 10, 12, 15-16, 18, 19, 21-22, 26, 36, 39, 40, 41
    def test_total_exceeds_max_covers_circuit_k(self):
        assert TrackNumberParser.validate_and_normalize("3/15", 10) == (None, None, "total exceeds max")

    # Circuit l: 7, 10, 12, 15-16, 18, 29, 30, 32, 33, 36, 39, 40, 42, 43
    def test_current_exceeds_max_no_total_covers_circuit_l(self):
        assert TrackNumberParser.validate_and_normalize("8", 5) == (None, None, "current exceeds max")

    # Circuit m: 7, 10, 12, 15-16, 18, 19, 21-22, 26, 36, 39, 40, 42, 45
    def test_valid_slash_within_max_covers_circuit_m(self):
        assert TrackNumberParser.validate_and_normalize("3/10", 10) == (3, 10, None)

    # Circuit n: 7, 10, 12, 15-16, 18, 29, 30, 32, 33, 36, 39, 40, 42, 45
    def test_valid_simple_within_max_covers_circuit_n(self):
        assert TrackNumberParser.validate_and_normalize("3", 10) == (3, None, None)



class TestPadTrackAndStaticMethods:
    """Teste finale pentru pad_track, @staticmethod și parametrii default (Sniper Tests)."""

    def test_pad_track_invalid_type(self):
        """Verifică ramura când track_number nu este int."""
        assert TrackNumberParser.pad_track(None) == ""
        assert TrackNumberParser.pad_track("5") == ""

    def test_pad_track_number(self):
        """Verifică formatarea corectă a stringului (padding cu 0)."""
        assert TrackNumberParser.pad_track(5) == "05"
        assert TrackNumberParser.pad_track(12) == "12"

    def test_staticmethod_validate_on_instance(self):
        """Verifică dacă funcția poate fi apelată corect de pe o instanță."""
        parser = TrackNumberParser()
        assert parser.validate_and_normalize("5") == (5, None, None)

    def test_staticmethod_pad_track_on_instance(self):
        """Verifică dacă funcția pad_track poate fi apelată de pe o instanță."""
        parser = TrackNumberParser()
        assert parser.pad_track(5) == "05"

    def test_default_max_tracks_is_strictly_none(self):
        """Verifică valoarea default pentru parametrul max_tracks."""
        # Dacă max_tracks ar deveni True/1, track-ul 100 ar pica.
        assert TrackNumberParser.validate_and_normalize("100") == (100, None, None)

    def test_default_allow_zero_is_strictly_false(self):
        """Verifică valoarea default pentru parametrul allow_zero."""
        # Dacă allow_zero ar deveni True, "0" ar fi acceptat.
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_slash_format_with_letters_in_total_kills_mutant(self):
        """Ucide mutantul care strică isdigit() pe parts[1]."""
        # Dacă isdigit() e forțat pe True, "album10" nu va fi curățat, 
        # va arunca ValueError și va returna "parse error". 
        # Noi verificăm că știe să curețe literele și să dea (3, 10, None).
        assert TrackNumberParser.validate_and_normalize("track3/album10") == (3, 10, None)