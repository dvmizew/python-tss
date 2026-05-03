from track_number_parser import TrackNumberParser


class TestValidateAndNormalizeEmptyInput:
    """Teste pentru cazuri de input gol/invalid."""

    def test_none_input(self):
        """None -> (None, None, 'empty input')."""
        assert TrackNumberParser.validate_and_normalize(None) == (None, None, "empty input")

    def test_empty_string(self):
        """'' -> (None, None, 'empty input')."""
        assert TrackNumberParser.validate_and_normalize("") == (None, None, "empty input")

    def test_only_spaces(self):
        """'   ' -> (None, None, 'empty input')."""
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


class TestValidateAndNormalizeEdgeCases:
    """Teste pentru edge case-uri si cazuri extreme."""

    def test_multiple_slashes_keeps_first(self):
        """'3/4/5' -> (3, 4, None) - doar primul slash conteaza."""
        assert TrackNumberParser.validate_and_normalize("3/4/5") == (3, 4, None)

    def test_very_large_numbers(self):
        """'999999/1000000' -> (999999, 1000000, None)."""
        assert TrackNumberParser.validate_and_normalize("999999/1000000") == (999999, 1000000, None)

    def test_single_very_large_number(self):
        """'999999' -> (999999, None, None)."""
        assert TrackNumberParser.validate_and_normalize("999999") == (999999, None, None)

    def test_complex_text_extraction(self):
        """'3 track / 10 albums' -> (3, 10, None)."""
        assert TrackNumberParser.validate_and_normalize("3 track / 10 albums") == (3, 10, None)

    def test_only_digits_surrounded_by_chars(self):
        """'T3D/A10B' -> (3, 10, None)."""
        assert TrackNumberParser.validate_and_normalize("T3D/A10B") == (3, 10, None)

    def test_dash_instead_of_slash_extracts_all_digits(self):
        """'3-10' -> (310, None, None) - fara slash, extrage toate."""
        assert TrackNumberParser.validate_and_normalize("3-10") == (310, None, None)

    def test_no_slash_with_mixed_separators_extracts_all(self):
        """'3:10' -> (310, None, None) - fara slash."""
        assert TrackNumberParser.validate_and_normalize("3:10") == (310, None, None)

    def test_consecutive_spaces_in_middle_without_slash(self):
        """'3    10' -> (310, None, None) - fara slash."""
        assert TrackNumberParser.validate_and_normalize("3    10") == (310, None, None)

    def test_spaces_around_slash_are_handled(self):
        """'3    /    10' -> (3, 10, None) - cu slash."""
        assert TrackNumberParser.validate_and_normalize("3    /    10") == (3, 10, None)


class TestValidateAndNormalizeMaxTracksExtreme:
    """Teste extreme pentru max_tracks validation."""

    def test_max_tracks_one_minimum(self):
        """'1' cu max_tracks=1 -> (1, None, None) minimum."""
        assert TrackNumberParser.validate_and_normalize("1", max_tracks=1) == (1, None, None)

    def test_max_tracks_one_exceeded(self):
        """'2' cu max_tracks=1 -> (None, None, 'current exceeds max')."""
        assert TrackNumberParser.validate_and_normalize("2", max_tracks=1) == (None, None, "current exceeds max")

    def test_max_tracks_very_large(self):
        """'500/999' cu max_tracks=999 -> (500, 999, None)."""
        assert TrackNumberParser.validate_and_normalize("500/999", max_tracks=999) == (500, 999, None)

    def test_max_tracks_very_large_exceeded_by_one(self):
        """'500/1000' cu max_tracks=999 -> (None, None, 'total exceeds max')."""
        assert TrackNumberParser.validate_and_normalize("500/1000", max_tracks=999) == (None, None, "total exceeds max")

    def test_max_tracks_boundary_current_just_below(self):
        """'9' cu max_tracks=10 -> (9, None, None)."""
        assert TrackNumberParser.validate_and_normalize("9", max_tracks=10) == (9, None, None)

    def test_max_tracks_boundary_current_just_above(self):
        """'11' cu max_tracks=10 -> (None, None, 'current exceeds max')."""
        assert TrackNumberParser.validate_and_normalize("11", max_tracks=10) == (None, None, "current exceeds max")

    def test_max_tracks_boundary_total_just_below(self):
        """'5/9' cu max_tracks=10 -> (5, 9, None)."""
        assert TrackNumberParser.validate_and_normalize("5/9", max_tracks=10) == (5, 9, None)

    def test_max_tracks_boundary_total_just_above(self):
        """'5/11' cu max_tracks=10 -> (None, None, 'total exceeds max')."""
        assert TrackNumberParser.validate_and_normalize("5/11", max_tracks=10) == (None, None, "total exceeds max")


class TestValidateAndNormalizeExtremeInputs:
    """Teste pentru inputuri extreme si edge case-uri de caractere."""

    def test_special_chars_around_digits_with_slash(self):
        """'#3!@/&10%' -> (3, 10, None) cu slash."""
        assert TrackNumberParser.validate_and_normalize("#3!@/&10%") == (3, 10, None)

    def test_special_chars_around_digits_no_slash(self):
        """'#3!@&10%' -> (310, None, None) fara slash."""
        assert TrackNumberParser.validate_and_normalize("#3!@&10%") == (310, None, None)

    def test_dots_between_digits_with_slash(self):
        """'1.2.3/4.5.6' -> (123, 456, None)."""
        assert TrackNumberParser.validate_and_normalize("1.2.3/4.5.6") == (123, 456, None)

    def test_dots_between_digits_no_slash(self):
        """'1.2.3' -> (123, None, None) fara slash."""
        assert TrackNumberParser.validate_and_normalize("1.2.3") == (123, None, None)

    def test_leading_trailing_zeros_with_slash(self):
        """'00123/00456' -> (123, 456, None)."""
        assert TrackNumberParser.validate_and_normalize("00123/00456") == (123, 456, None)

    def test_leading_trailing_zeros_no_slash(self):
        """'00123' -> (123, None, None) fara slash."""
        assert TrackNumberParser.validate_and_normalize("00123") == (123, None, None)

    def test_minimum_valid_current(self):
        """'1' -> (1, None, None) minimum."""
        assert TrackNumberParser.validate_and_normalize("1") == (1, None, None)

    def test_maximum_common_current_single_digit(self):
        """'9' -> (9, None, None) maximum single digit."""
        assert TrackNumberParser.validate_and_normalize("9") == (9, None, None)

    def test_minimum_valid_pair(self):
        """'1/1' -> (1, 1, None) minimum pair."""
        assert TrackNumberParser.validate_and_normalize("1/1") == (1, 1, None)

    def test_transition_from_single_to_double_digit(self):
        """'9/10' -> (9, 10, None) tranzitie digit."""
        assert TrackNumberParser.validate_and_normalize("9/10") == (9, 10, None)