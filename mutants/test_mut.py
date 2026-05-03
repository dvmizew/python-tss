import pytest
from track_number_parser import TrackNumberParser

class TestCoreBehavior:

    def test_empty_inputs(self):
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")
        assert TrackNumberParser.validate_and_normalize("") == (None, None, "empty input")
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")

    def test_invalid_parse(self):
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")

    def test_zero_not_allowed(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")

    def test_basic_valid_cases(self):
        assert TrackNumberParser.validate_and_normalize("5") == (5, None, None)
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)
        assert TrackNumberParser.validate_and_normalize("track3") == (3, None, None)


class TestMutationKilling:

    # operator flip killer (>, <, >=, <=)
    def test_current_cannot_exceed_total(self):
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    def test_total_vs_max_boundary(self):
        assert TrackNumberParser.validate_and_normalize("3/11", max_tracks=10) == (None, None, "total exceeds max")

    def test_current_vs_max_boundary(self):
        assert TrackNumberParser.validate_and_normalize("11", max_tracks=10) == (None, None, "current exceeds max")

class TestDifferentialBehavior:

    def test_different_inputs_must_not_be_equal(self):
        r1 = TrackNumberParser.validate_and_normalize("3/10")
        r2 = TrackNumberParser.validate_and_normalize("3/9")
        assert r1 != r2

    def test_boundary_flip_detection(self):
        low = TrackNumberParser.validate_and_normalize("9", max_tracks=10)
        high = TrackNumberParser.validate_and_normalize("11", max_tracks=10)
        assert low != high


class TestInvariants:

    def test_valid_result_structure(self):
        cur, tot, err = TrackNumberParser.validate_and_normalize("3/10")
        assert err is None
        assert isinstance(cur, int)
        assert cur > 0

    def test_error_consistency(self):
        _, _, err = TrackNumberParser.validate_and_normalize("0")
        assert err is not None


class TestEdgeCases:

    def test_max_tracks_effect(self):
        assert TrackNumberParser.validate_and_normalize("10", max_tracks=10) == (10, None, None)
        assert TrackNumberParser.validate_and_normalize("11", max_tracks=10)[2] == "current exceeds max"