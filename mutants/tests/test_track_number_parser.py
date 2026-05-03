from track_number_parser import TrackNumberParser


class TestValidateAndNormalizeEmptyInput:
    """Teste pentru cazuri de input gol/invalid."""

    def test_none_input(self):
        """None trebuie sa returneze (None, None, 'empty input')."""
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_empty_string(self):
        """String gol trebuie sa returneze (None, None, 'empty input')."""
        assert TrackNumberParser.validate_and_normalize("") == (None, None, "empty input")

    def test_only_spaces(self):
        """String cu doar spații trebuie sa returneze (None, None, 'empty input')."""
        assert TrackNumberParser.validate_and_normalize("   ") == (None, None, "empty input")


class TestValidateAndNormalizeParseErrors:
    """Teste pentru erori de parsare."""

    def test_no_digits(self):
        """String fara cifre: 'abc' -> parse error."""
        assert TrackNumberParser.validate_and_normalize("abc") == (None, None, "parse error")

    def test_slash_only(self):
        """Doar slash: '/' -> parse error."""
        assert TrackNumberParser.validate_and_normalize("/") == (None, None, "parse error")

    def test_slash_missing_current(self):
        """/10 fara current -> parse error."""
        assert TrackNumberParser.validate_and_normalize("/10") == (None, None, "parse error")

    def test_slash_missing_total(self):
        """3/ fara total -> parse error."""
        assert TrackNumberParser.validate_and_normalize("3/") == (None, None, "parse error")

    def test_double_slash(self):
        """// fara cifre -> parse error."""
        assert TrackNumberParser.validate_and_normalize("//") == (None, None, "parse error")


class TestValidateAndNormalizeZeroNotAllowed:
    """Teste pentru validare zero (nu e permis)."""

    def test_zero_simple(self):
        """0 singur -> zero not allowed."""
        assert TrackNumberParser.validate_and_normalize("0") == (None, None, "zero not allowed")

    def test_zero_current_with_slash(self):
        """0/10 cu zero la current -> zero not allowed."""
        assert TrackNumberParser.validate_and_normalize("0/10") == (None, None, "zero not allowed")

    def test_zero_total_with_slash(self):
        """3/0 cu zero la total -> zero not allowed."""
        assert TrackNumberParser.validate_and_normalize("3/0") == (None, None, "zero not allowed")

    def test_zero_both(self):
        """0/0 cu zero pe ambele -> zero not allowed."""
        assert TrackNumberParser.validate_and_normalize("0/0") == (None, None, "zero not allowed")


class TestValidateAndNormalizeCurrentExceedsTotal:
    """Teste pentru validare logica: current > total."""

    def test_current_exceeds_total_simple(self):
        """7/3 cu current > total -> current exceeds total."""
        assert TrackNumberParser.validate_and_normalize("7/3") == (None, None, "current exceeds total")

    def test_current_exceeds_total_large(self):
        """100/50 -> current exceeds total."""
        assert TrackNumberParser.validate_and_normalize("100/50") == (None, None, "current exceeds total")

    def test_current_exceeds_by_one(self):
        """6/5 exceeded cu unu -> current exceeds total."""
        assert TrackNumberParser.validate_and_normalize("6/5") == (None, None, "current exceeds total")


class TestValidateAndNormalizeMaxTracksValidation:
    """Teste pentru validare max_tracks."""

    def test_total_exceeds_max(self):
        """3/15 cu max_tracks=10 -> total exceeds max."""
        assert TrackNumberParser.validate_and_normalize("3/15", max_tracks=10) == (None, None, "total exceeds max")

    def test_total_equals_max(self):
        """3/10 cu max_tracks=10 -> valid, no error."""
        assert TrackNumberParser.validate_and_normalize("3/10", max_tracks=10) == (3, 10, None)

    def test_total_below_max(self):
        """3/9 cu max_tracks=10 -> valid."""
        assert TrackNumberParser.validate_and_normalize("3/9", max_tracks=10) == (3, 9, None)

    def test_current_exceeds_max_no_total(self):
        """8 cu max_tracks=5 (fara total) -> current exceeds max."""
        assert TrackNumberParser.validate_and_normalize("8", max_tracks=5) == (None, None, "current exceeds max")

    def test_current_equals_max_no_total(self):
        """5 cu max_tracks=5 (fara total) -> valid."""
        assert TrackNumberParser.validate_and_normalize("5", max_tracks=5) == (5, None, None)

    def test_current_below_max_no_total(self):
        """4 cu max_tracks=5 (fara total) -> valid."""
        assert TrackNumberParser.validate_and_normalize("4", max_tracks=5) == (4, None, None)


class TestValidateAndNormalizeSuccessSimple:
    """Teste pentru cazuri valide fara slash."""

    def test_single_digit_valid(self):
        """'5' -> (5, None, None)."""
        assert TrackNumberParser.validate_and_normalize("5") == (5, None, None)

    def test_double_digit_valid(self):
        """'12' -> (12, None, None)."""
        assert TrackNumberParser.validate_and_normalize("12") == (12, None, None)

    def test_with_leading_zeros(self):
        """'03' -> (3, None, None), zerourile de start sunt eliminate."""
        assert TrackNumberParser.validate_and_normalize("03") == (3, None, None)

    def test_with_spaces(self):
        """'  5  ' -> (5, None, None), spații eliminate."""
        assert TrackNumberParser.validate_and_normalize("  5  ") == (5, None, None)

    def test_mixed_chars_and_digits(self):
        """'track3' -> (3, None, None), doar cifrele conteaza."""
        assert TrackNumberParser.validate_and_normalize("track3") == (3, None, None)

    def test_prefix_suffix(self):
        """'T03B' -> (3, None, None)."""
        assert TrackNumberParser.validate_and_normalize("T03B") == (3, None, None)


class TestValidateAndNormalizeSuccessSlash:
    """Teste pentru cazuri valide cu slash."""

    def test_slash_basic(self):
        """'3/10' -> (3, 10, None)."""
        assert TrackNumberParser.validate_and_normalize("3/10") == (3, 10, None)

    def test_slash_single_digits(self):
        """'1/1' -> (1, 1, None)."""
        assert TrackNumberParser.validate_and_normalize("1/1") == (1, 1, None)

    def test_slash_with_spaces(self):
        """'  3  /  10  ' -> (3, 10, None)."""
        assert TrackNumberParser.validate_and_normalize("  3  /  10  ") == (3, 10, None)

    def test_slash_leading_zeros_both(self):
        """'03/10' -> (3, 10, None)."""
        assert TrackNumberParser.validate_and_normalize("03/10") == (3, 10, None)

    def test_slash_current_with_text(self):
        """'track3/album10' -> (3, 10, None)."""
        assert TrackNumberParser.validate_and_normalize("track3/album10") == (3, 10, None)

    def test_slash_current_equals_total(self):
        """'5/5' -> (5, 5, None), valid caz special."""
        assert TrackNumberParser.validate_and_normalize("5/5") == (5, 5, None)

    def test_slash_large_numbers(self):
        """'999/1000' -> (999, 1000, None)."""
        assert TrackNumberParser.validate_and_normalize("999/1000") == (999, 1000, None)

    def test_slash_leading_zeros_total(self):
        """'5/09' -> (5, 9, None)."""
        assert TrackNumberParser.validate_and_normalize("5/09") == (5, 9, None)

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