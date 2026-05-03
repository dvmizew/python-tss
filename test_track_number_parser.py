import pytest
from track_number_parser import TrackNumberParser


class TestEquivalenceClasses:

    def test_c1_none_input(self):
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_c2_empty_string(self):
        assert TrackNumberParser.validate_and_normalize("") == (None, None, "empty input")

    def test_c3_only_spaces(self):
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")

    def test_c4_no_digits(self):
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")

    def test_c5_zero_simple(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_c6_zero_current_slash(self):
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")

    def test_c7_zero_total_slash(self):
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")

    def test_c8_current_exceeds_total(self):
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    def test_c9_total_exceeds_max(self):
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")

    def test_c10_current_exceeds_max(self):
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")

    def test_c11_simple_valid(self):
        assert TrackNumberParser.validate_and_normalize("5") == (5, None, None)

    def test_c12_slash_valid(self):
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)

    def test_c13_mixed_letters_digits(self):
        assert TrackNumberParser.validate_and_normalize("track3") == (3, None, None)

    def test_c14_valid_with_max_with_total(self):
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)

    def test_c15_valid_with_max_no_total(self):
        assert TrackNumberParser.validate_and_normalize("5", max_tracks=10) == (5, None, None)


class TestBoundaryValues:

    def test_f1_current_below_minimum(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_f2_current_at_minimum(self):
        assert TrackNumberParser.validate_and_normalize("1") == (1, None, None)

    def test_f3_current_above_minimum(self):
        assert TrackNumberParser.validate_and_normalize("2") == (2, None, None)

    def test_f4_total_below_minimum(self):
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")

    def test_f5_total_at_minimum(self):
        assert TrackNumberParser.validate_and_normalize("1/1") == (1, 1, None)

    def test_f6_total_above_minimum(self):
        assert TrackNumberParser.validate_and_normalize("1/2") == (1, 2, None)

    def test_f7_current_below_total(self):
        assert TrackNumberParser.validate_and_normalize("4/5") == (4, 5, None)

    def test_f8_current_equal_total(self):
        assert TrackNumberParser.validate_and_normalize("5/5") == (5, 5, None)

    def test_f9_current_exceeds_total_by_one(self):
        assert TrackNumberParser.validate_and_normalize("6/5") == (None, None, "current exceeds total")

    def test_f10_total_below_max(self):
        assert TrackNumberParser.validate_and_normalize("3/9", max_tracks=10) == (3, 9, None)

    def test_f11_total_equal_max(self):
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)

    def test_f12_total_exceeds_max_by_one(self):
        assert TrackNumberParser.validate_and_normalize("3/11", max_tracks=10) == (None, None, "total exceeds max")

    def test_f13_current_below_max_no_total(self):
        assert TrackNumberParser.validate_and_normalize("9", max_tracks=10) == (9, None, None)

    def test_f14_current_equal_max_no_total(self):
        assert TrackNumberParser.validate_and_normalize("10", max_tracks=10) == (10, None, None)

    def test_f15_current_exceeds_max_no_total_by_one(self):
        assert TrackNumberParser.validate_and_normalize("11", max_tracks=10) == (None, None, "current exceeds max")


class TestStatementCoverage:

    def test_sc1(self):
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_sc2(self):
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")

    def test_sc3(self):
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")

    def test_sc4(self):
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")

    def test_sc5(self):
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")

    def test_sc6(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_sc7(self):
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    def test_sc8(self):
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")

    def test_sc9(self):
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")

    def test_sc10(self):
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)


class TestBranchCoverage:

    def test_bc1_d1_true(self):
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_bc2_d1_false_d2_true(self):
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")

    def test_bc3_d3_true_d4_true(self):
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")

    def test_bc4_d4_false_d5_true(self):
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")

    def test_bc5_d3_false_d6_true(self):
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")

    def test_bc6_d6_false_d7_true(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_bc7_d5_false_d8_true(self):
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    def test_bc8_d8_false_d9_true_d10_true(self):
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")

    def test_bc9_d10_false_d11_true(self):
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")

    def test_bc10_d9_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)

    def test_bc11_d9_true_d10_false_d11_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)


class TestConditionCoverage:

    def test_bc1_d1_true(self):
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_bc2_d1_false_d2_true(self):
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")

    def test_bc3_d3_true_d4_true(self):
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")

    def test_bc4_d4_false_d5_true(self):
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")

    def test_bc5_d3_false_d6_true(self):
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")

    def test_bc6_d6_false_d7_true(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_bc7_d5_false_d8_true(self):
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    def test_bc8_d8_false_d9_true_d10_true(self):
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")

    def test_bc9_d10_false_d11_true(self):
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")

    def test_bc10_d9_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)

    def test_bc11_d9_true_d10_false_d11_false(self):
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)

    def test_cc1_c2_true(self):
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")

    def test_cc2_c8_false(self):
        assert TrackNumberParser.validate_and_normalize("3", max_tracks=10) == (3, None, None)


class TestIndependentCircuits:

    def test_ci_a(self):
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_ci_b(self):
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")

    def test_ci_c(self):
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")

    def test_ci_d(self):
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")

    def test_ci_e(self):
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")

    def test_ci_f(self):
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_ci_g(self):
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    # h) nefezabil

    def test_ci_i(self):
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)

    def test_ci_j(self):
        assert TrackNumberParser.validate_and_normalize("5") == (5, None, None)

    def test_ci_k(self):
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")

    def test_ci_l(self):
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")

    def test_ci_m(self):
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)

    def test_ci_n(self):
        assert TrackNumberParser.validate_and_normalize("3", max_tracks=10) == (3, None, None)