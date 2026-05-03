import pytest
from track_number_parser import TrackNumberParser


class TestEquivalenceClasses:

    # input gol
    def test_none_input(self):
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_empty_string(self):
        assert TrackNumberParser.validate_and_normalize("") == (None, None, "empty input")

    def test_only_spaces(self):
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")

    # nici o cifra

    def test_no_digits(self):
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")

    # zero nu e valid

    def test_zero_simple(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_zero_current_slash(self):
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")

    def test_zero_total_slash(self):
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")

    # current depaseste total

    def test_current_exceeds_total(self):
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    # depasire max_tracks

    def test_total_exceeds_max(self):
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")

    def test_current_exceeds_max(self):
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")

    # cazuri valide

    def test_simple_valid(self):
        assert TrackNumberParser.validate_and_normalize("5") == (5, None, None)

    def test_slash_valid(self):
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)

    def test_mixed_letters_and_digits(self):
        assert TrackNumberParser.validate_and_normalize("track3") == (3, None, None)

    def test_valid_with_max_tracks_with_total(self):
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)

    def test_valid_with_max_tracks_no_total(self):
        assert TrackNumberParser.validate_and_normalize("5", max_tracks=10) == (5, None, None)


class TestBoundaryValues:
 
    # --- Frontiera zero/unu pentru current ---
 
    def test_current_below_minimum(self):
        # F1 - sub limita minima
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")
 
    def test_current_at_minimum(self):
        # F2 - exact pe limita minima
        assert TrackNumberParser.validate_and_normalize("1") == (1, None, None)
 
    def test_current_above_minimum(self):
        # F3 - peste limita minima
        assert TrackNumberParser.validate_and_normalize("2") == (2, None, None)
 
    # --- Frontiera zero/unu pentru total ---
 
    def test_total_below_minimum(self):
        # F4 - total zero
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")
 
    def test_total_at_minimum(self):
        # F5 - total exact 1
        assert TrackNumberParser.validate_and_normalize("1/1") == (1, 1, None)
 
    def test_total_above_minimum(self):
        # F6 - total peste 1
        assert TrackNumberParser.validate_and_normalize("1/2") == (1, 2, None)
 
    # --- Frontiera current vs total ---
 
    def test_current_below_total(self):
        # F7 - current cu o unitate sub total
        assert TrackNumberParser.validate_and_normalize("4/5") == (4, 5, None)
 
    def test_current_equal_total(self):
        # F8 - current exact egal cu total
        assert TrackNumberParser.validate_and_normalize("5/5") == (5, 5, None)
 
    def test_current_exceeds_total_by_one(self):
        # F9 - current depaseste total cu o unitate
        assert TrackNumberParser.validate_and_normalize("6/5") == (None, None, "current exceeds total")
 
    # --- Frontiera total vs max_tracks ---
 
    def test_total_below_max(self):
        # F10 - total cu o unitate sub max
        assert TrackNumberParser.validate_and_normalize("3/9", max_tracks=10) == (3, 9, None)
 
    def test_total_equal_max(self):
        # F11 - total exact egal cu max
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)
 
    def test_total_exceeds_max_by_one(self):
        # F12 - total depaseste max cu o unitate
        assert TrackNumberParser.validate_and_normalize("3/11", max_tracks=10) == (None, None, "total exceeds max")
 
    # --- Frontiera current vs max_tracks (fara total) ---
 
    def test_current_below_max_no_total(self):
        # F13 - current cu o unitate sub max
        assert TrackNumberParser.validate_and_normalize("9", max_tracks=10) == (9, None, None)
 
    def test_current_equal_max_no_total(self):
        # F14 - current exact egal cu max
        assert TrackNumberParser.validate_and_normalize("10", max_tracks=10) == (10, None, None)
 
    def test_current_exceeds_max_no_total_by_one(self):
        # F15 - current depaseste max cu o unitate
        assert TrackNumberParser.validate_and_normalize("11", max_tracks=10) == (None, None, "current exceeds max")


class TestStatementCoverage:
 
    def test_sc1_none_input(self):
        # 7 -> 8
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")
 
    def test_sc2_only_spaces(self):
        # 7 -> 10 -> 12 -> 13
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")
 
    def test_sc3_parse_error_slash(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 19 -> 21,22 -> 24
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")
 
    def test_sc4_zero_slash(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 19 -> 21,22 -> 26 -> 27
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")
 
    def test_sc5_parse_error_no_slash(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 29 -> 30 -> 31
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")
 
    def test_sc6_zero_no_slash(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 29 -> 30 -> 32 -> 33 -> 34
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")
 
    def test_sc7_current_exceeds_total(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 19 -> 21,22 -> 26 -> 36 -> 37
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")
 
    def test_sc8_total_exceeds_max(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 19 -> 21,22 -> 26 -> 36 -> 39 -> 40 -> 41
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")
 
    def test_sc9_current_exceeds_max(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 29 -> 30 -> 32 -> 33 -> 36 -> 39 -> 40 -> 42 -> 43
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")
 
    def test_sc10_valid(self):
        # 7 -> 10 -> 12 -> 15,16 -> 18 -> 19 -> 21,22 -> 26 -> 36 -> 39 -> 45
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)
 

 
class TestBranchCoverage:
 
    def test_bc1_d1_true(self):
        # D1=True: not track_num
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")
 
    def test_bc2_d1_false_d2_true(self):
        # D1=False, D2=True: not track_str
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")
 
    def test_bc3_d3_true_d4_true(self):
        # D3=True: "/" in track_str, D4=True: except
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")
 
    def test_bc4_d4_false_d5_true(self):
        # D4=False: try ok, D5=True: cur==0 or tot==0
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")
 
    def test_bc5_d3_false_d6_true(self):
        # D3=False: no slash, D6=True: not digits
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")
 
    def test_bc6_d6_false_d7_true(self):
        # D6=False: digits exist, D7=True: cur==0
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")
 
    def test_bc7_d5_false_d8_true(self):
        # D5=False: cur!=0 and tot!=0, D8=True: cur>tot
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")
 
    def test_bc8_d8_false_d9_true_d10_true(self):
        # D8=False, D9=True: max exists, D10=True: tot>max
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")
 
    def test_bc9_d10_false_d11_true(self):
        # D10=False, D11=True: tot==None and cur>max
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")
 
    def test_bc10_d9_false(self):
        # D9=False: max_tracks=None, cade direct la 45
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)
 
    def test_bc12_d9_true_d10_false_d11_false(self):
        # D9=True, D10=False, D11=False: tot exists, tot<=max -> valid
        # test nou fata de statement coverage
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)
 
class TestConditionCoverage:
 
    # C1: cur==0 — True acoperit de BC4, False acoperit de BC7
    # C2: tot==0 — False acoperit de BC4, True e NOU
    def test_cc1_c2_true(self):
        # C2=True: tot==0
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")
 
    # C3: tot is not None — True acoperit de BC7, False acoperit de BC9
    # C4: cur > tot — True acoperit de BC7, False acoperit de BC8
    # C5: tot is not None — True acoperit de BC8, False acoperit de BC9
    # C6: tot > max — True acoperit de BC8, False acoperit de BC11
    # C7: tot is None — True acoperit de BC9, False acoperit de BC8
    # C8: cur > max — True acoperit de BC9, False e NOU
    def test_cc2_c8_false(self):
        # C8=False: cur <= max, fara total
        assert TrackNumberParser.validate_and_normalize("3", max_tracks=10) == (3, None, None)
 