"""
Unit tests for audio_utils module.

Test strategies implemented:
- Equivalence Partitioning (EC)
- Boundary Value Analysis (BVA)
- Decision/Condition/Statement Coverage
"""
import pytest
from audio_utils import (
    TrackNumberParser,
    AudioFileNameBuilder,
    FolderNameBuilder,
    LyricsFileFinder,
    AudioMetadata,
)


class TestFileNameSanitizer:
    """Tests for FileNameSanitizer class."""
    
    # ==================== WINDOWS TESTS ====================
    
    class TestWindowsSanitizer:
        """Test Windows-specific sanitization."""
        
        @pytest.fixture(autouse=True)
        def setup(self, windows_sanitizer):
            self.sanitizer = windows_sanitizer
        
        # EC1: Valid names (letters, numbers, spaces, basic punctuation)
        def test_valid_ascii_name(self):
            """EC1: Valid ASCII characters remain unchanged."""
            result = self.sanitizer.sanitize("Song Title 2024")
            assert result == "Song Title 2024"
        
        def test_valid_name_with_hyphen(self):
            """EC1: Hyphens are valid."""
            result = self.sanitizer.sanitize("Song-Title")
            assert result == "Song-Title"
        
        def test_valid_name_with_apostrophe(self):
            """EC1: Apostrophes are valid."""
            result = self.sanitizer.sanitize("Artist's Song")
            assert result == "Artist's Song"
        
        # EC2: Windows invalid characters (< > " : / \ | *)
        def test_colon_replaced_with_dash(self):
            """EC2: Colon becomes ' - '."""
            result = self.sanitizer.sanitize("Song: Title")
            assert ":" not in result
            assert " - " in result
        
        def test_angle_brackets_replaced(self):
            """EC2: < and > become underscores."""
            result = self.sanitizer.sanitize("<Song>")
            assert "<" not in result
            assert ">" not in result
            assert "_" in result
        
        def test_question_mark_removed(self):
            """EC2: Question mark is removed."""
            result = self.sanitizer.sanitize("Song?")
            assert "?" not in result
        
        def test_double_quote_replaced(self):
            """EC2: Double quote becomes underscore."""
            result = self.sanitizer.sanitize('Song "Title"')
            assert '"' not in result
            assert "_" in result
        
        def test_forward_slash_replaced(self):
            """EC2: Forward slash becomes underscore."""
            result = self.sanitizer.sanitize("Artist/Title")
            assert "/" not in result
            assert "_" in result
        
        def test_backslash_replaced(self):
            """EC2: Backslash becomes underscore."""
            result = self.sanitizer.sanitize("Artist\\Title")
            assert "\\" not in result
            assert "_" in result
        
        def test_pipe_replaced(self):
            """EC2: Pipe becomes underscore."""
            result = self.sanitizer.sanitize("Artist|Title")
            assert "|" not in result
        
        def test_asterisk_replaced(self):
            """EC2: Asterisk becomes underscore."""
            result = self.sanitizer.sanitize("Song*")
            assert "*" not in result
        
        # BVA: Trailing dots (Windows specific)
        def test_single_trailing_dot_removed(self):
            """BVA: Single trailing dot removed."""
            result = self.sanitizer.sanitize("Song.")
            assert result == "Song"
        
        def test_multiple_trailing_dots_removed(self):
            """BVA: Multiple trailing dots removed."""
            result = self.sanitizer.sanitize("Song...")
            assert result == "Song"
        
        def test_dots_in_middle_preserved(self):
            """BVA: Dots in middle are preserved."""
            result = self.sanitizer.sanitize("Mr. Song.")
            assert "Mr. Song" in result
        
        # BVA: Whitespace
        def test_leading_spaces_stripped(self):
            """BVA: Leading spaces removed."""
            result = self.sanitizer.sanitize("   Song")
            assert result == "Song"
        
        def test_trailing_spaces_stripped(self):
            """BVA: Trailing spaces removed."""
            result = self.sanitizer.sanitize("Song   ")
            assert result == "Song"
        
        # Edge: Empty and None
        def test_empty_string(self):
            """Edge: Empty string returns empty."""
            result = self.sanitizer.sanitize("")
            assert result == ""
        
        def test_none_input(self):
            """Edge: None input returns empty string."""
            result = self.sanitizer.sanitize(None)
            assert result == ""
        
        # Edge: Only whitespace
        def test_only_spaces(self):
            """Edge: String with only spaces."""
            result = self.sanitizer.sanitize("   ")
            assert result == ""
        
        # Edge: Multiple invalid characters
        def test_multiple_invalid_chars(self):
            """Edge: Multiple consecutive invalid characters."""
            result = self.sanitizer.sanitize("Song<>:|Title")
            assert all(c not in result for c in "<>:|")
    
    # ==================== UNIX TESTS ====================
    
    class TestUnixSanitizer:
        """Test Unix/Linux-specific sanitization."""
        
        @pytest.fixture(autouse=True)
        def setup(self, unix_sanitizer):
            self.sanitizer = unix_sanitizer
        
        def test_unix_preserves_colon(self):
            """Unix: Colon is allowed."""
            result = self.sanitizer.sanitize("Song: Title")
            assert ":" in result
        
        def test_unix_preserves_windows_chars(self):
            """Unix: Windows-invalid chars are allowed (except/)."""
            result = self.sanitizer.sanitize("<Song>")
            assert "<" in result and ">" in result
        
        def test_unix_forward_slash_replaced(self):
            """Unix: Forward slash is replaced (not allowed on Unix)."""
            result = self.sanitizer.sanitize("Artist/Title")
            assert "/" not in result
        
        def test_unix_null_bytes_removed(self):
            """Unix: Null bytes are removed."""
            input_str = "Song\x00Title"
            result = self.sanitizer.sanitize(input_str)
            assert "\x00" not in result
        
        def test_unix_preserves_trailing_dots(self):
            """Unix: Trailing dots are allowed."""
            result = self.sanitizer.sanitize("Song...")
            assert result == "Song..."


class TestTrackNumberParser:
    """Tests for TrackNumberParser class."""
    
    # ==================== PARSE TESTS ====================
    
    class TestParse:
        """Tests for parse() method."""
        
        def test_parse_normal_track_with_total(self):
            """Normal case: 'N/Total' format."""
            current, total = TrackNumberParser.parse("5/12")
            assert current == 5
            assert total == 12
        
        def test_parse_single_digit(self):
            """Single digit: '5'."""
            current, total = TrackNumberParser.parse("5")
            assert current == 5
            assert total is None
        
        def test_parse_double_digit(self):
            """Double digit: '12'."""
            current, total = TrackNumberParser.parse("12")
            assert current == 12
            assert total is None
        
        def test_parse_with_leading_zeros(self):
            """Leading zeros: '01/10'."""
            current, total = TrackNumberParser.parse("01/10")
            assert current == 1
            assert total == 10
        
        # BVA: Boundary cases
        def test_parse_track_zero(self):
            """BVA: Track 0."""
            current, total = TrackNumberParser.parse("0/1")
            assert current == 0
            assert total == 1
        
        def test_parse_track_exceeds_total(self):
            """BVA: Track number > total."""
            current, total = TrackNumberParser.parse("15/10")
            assert current == 15
            assert total == 10
        
        def test_parse_same_track_and_total(self):
            """BVA: Track = Total."""
            current, total = TrackNumberParser.parse("12/12")
            assert current == 12
            assert total == 12
        
        # Edge: Invalid inputs
        def test_parse_non_numeric(self):
            """Edge: Non-numeric input."""
            current, total = TrackNumberParser.parse("ABC")
            assert current is None
            assert total is None
        
        def test_parse_empty_string(self):
            """Edge: Empty string."""
            current, total = TrackNumberParser.parse("")
            assert current is None
            assert total is None
        
        def test_parse_none(self):
            """Edge: None input."""
            current, total = TrackNumberParser.parse(None)
            assert current is None
            assert total is None
        
        def test_parse_with_trash_prefix(self):
            """Edge: Track with prefix (e.g. 'Track 05')."""
            current, total = TrackNumberParser.parse("Track 05")
            assert current == 5
            assert total is None

        def test_parse_invalid_fraction_returns_none(self):
            """Edge: Invalid fraction input should return None tuple."""
            current, total = TrackNumberParser.parse("abc/def")
            assert current is None
            assert total is None
    
    # ==================== FORMAT TESTS ====================
    
    class TestFormat:
        """Tests for format_track() method."""
        
        def test_format_without_total(self):
            """Format without total: just number."""
            result = TrackNumberParser.format_track(5)
            assert result == "5"
        
        def test_format_with_total(self):
            """Format with total: 'current/total'."""
            result = TrackNumberParser.format_track(5, 12)
            assert result == "5/12"
        
        def test_format_track_one_of_one(self):
            """Format single track."""
            result = TrackNumberParser.format_track(1, 1)
            assert result == "1/1"
    
    # ==================== PAD TESTS ====================
    
    class TestPad:
        """Tests for pad_track() method."""
        
        def test_pad_single_digit(self):
            """Pad single digit."""
            result = TrackNumberParser.pad_track(5)
            assert result == "05"
        
        def test_pad_double_digit(self):
            """Pad double digit (unchanged)."""
            result = TrackNumberParser.pad_track(12)
            assert result == "12"
        
        def test_pad_zero(self):
            """Pad zero."""
            result = TrackNumberParser.pad_track(0)
            assert result == "00"
        
        def test_pad_99(self):
            """Pad 99."""
            result = TrackNumberParser.pad_track(99)
            assert result == "99"


class TestAudioFileNameBuilder:
    """Tests for AudioFileNameBuilder class."""
    
    def test_build_with_track_and_extension(self, file_name_builder):
        """Build standard 'NN - Title.ext' format."""
        result = file_name_builder.build_filename(
            title="My Song",
            track_number="5",
            extension=".mp3"
        )
        assert result == "05 - My Song.mp3"
    
    def test_build_without_track(self, file_name_builder):
        """Build without track number."""
        result = file_name_builder.build_filename(
            title="My Song",
            extension=".mp3"
        )
        assert result == "My Song.mp3"
    
    def test_build_with_track_fraction(self, file_name_builder):
        """Build with 'N/Total' format."""
        result = file_name_builder.build_filename(
            title="My Song",
            track_number="5/12",
            extension=".mp3"
        )
        assert result == "05 - My Song.mp3"
    
    def test_build_with_invalid_title(self, file_name_builder):
        """Build with None/empty title."""
        result = file_name_builder.build_filename(
            title=None,
            extension=".mp3"
        )
        assert result is None

    def test_build_returns_none_when_sanitized_title_is_empty(self, windows_sanitizer):
        """Build returns None if sanitization removes the whole title."""
        builder = AudioFileNameBuilder(windows_sanitizer)
        result = builder.build_filename(
            title="???",
            track_number="1",
            extension=".mp3"
        )
        assert result is None

    def test_find_lyrics_by_pattern_returns_match(self, temp_audio_dir):
        """Pattern search should find a matching lyrics file."""
        lyrics_path = f"{temp_audio_dir}/01 My Song.lrc"
        with open(lyrics_path, "w", encoding="utf-8") as handle:
            handle.write("[ti:My Song]\n")

        result = LyricsFileFinder.find_lyrics_by_pattern("1/10", "My Song", temp_audio_dir)

        assert result == (lyrics_path, ".lrc")

    def test_find_lyrics_by_pattern_returns_none_on_oserror(self, monkeypatch, temp_audio_dir):
        """Pattern search should handle listdir errors gracefully."""
        monkeypatch.setattr("audio_utils.os.listdir", lambda folder: (_ for _ in ()).throw(OSError("boom")))

        result = LyricsFileFinder.find_lyrics_by_pattern("1/10", "My Song", temp_audio_dir)

        assert result == (None, None)

    def test_find_lyrics_by_pattern_returns_none_for_invalid_input(self, temp_audio_dir):
        """Invalid track or missing folder should return None tuple."""
        assert LyricsFileFinder.find_lyrics_by_pattern(None, "My Song", temp_audio_dir) == (None, None)
        assert LyricsFileFinder.find_lyrics_by_pattern("abc", "My Song", temp_audio_dir) == (None, None)
        assert LyricsFileFinder.find_lyrics_by_pattern("1/10", "My Song", f"{temp_audio_dir}/missing") == (None, None)
    
    def test_build_extension_without_dot(self, file_name_builder):
        """Build extension without leading dot."""
        result = file_name_builder.build_filename(
            title="Song",
            extension="mp3"
        )
        assert result == "Song.mp3"


class TestFolderNameBuilder:
    """Tests for FolderNameBuilder class."""
    
    def test_build_normal_folder_name(self, folder_name_builder):
        """Build 'Artist - Album' format."""
        result = folder_name_builder.build_folder_name(
            artist="The Beatles",
            album="Abbey Road"
        )
        assert result == "The Beatles - Abbey Road"
    
    def test_build_with_invalid_chars(self, folder_name_builder, windows_sanitizer):
        """Build with invalid characters (sanitized on Windows)."""
        # On Unix, < and > are allowed, so use Windows sanitizer explicitly
        win_builder = FolderNameBuilder(windows_sanitizer)
        result = win_builder.build_folder_name(
            artist="Art<ist",
            album="Alb>um"
        )
        assert "<" not in result
        assert ">" not in result
    
    def test_build_with_empty_artist(self, folder_name_builder):
        """Build with empty artist."""
        result = folder_name_builder.build_folder_name(
            artist="",
            album="Album"
        )
        assert result is None
    
    def test_standardize_single_artist(self):
        """Standardize single artist (unchanged)."""
        result = FolderNameBuilder.standardize_artist("The Beatles")
        assert result == "The Beatles"
    
    def test_standardize_multiple_artists_semicolon(self):
        """Standardize artists separated by semicolon."""
        result = FolderNameBuilder.standardize_artist("Artist1; Artist2; Artist3")
        assert result == "Artist1 & Artist2 & Artist3"
    
    def test_standardize_multiple_artists_comma(self):
        """Standardize artists separated by comma."""
        result = FolderNameBuilder.standardize_artist("Artist1, Artist2")
        assert result == "Artist1 & Artist2"
    
    def test_standardize_multiple_artists_list(self):
        """Standardize artists from list."""
        result = FolderNameBuilder.standardize_artist(["Artist1", "Artist2"])
        assert result == "Artist1 & Artist2"
    
    def test_standardize_duplicate_artists(self):
        """Standardize removes duplicate artists."""
        result = FolderNameBuilder.standardize_artist("Artist; Artist; Other")
        assert result.count("Artist") == 1


class TestAudioMetadata:
    """Tests for AudioMetadata dataclass."""
    
    def test_metadata_is_valid_with_title(self, sample_metadata):
        """Metadata is valid if it has title."""
        assert sample_metadata.is_valid() is True
    
    def test_metadata_invalid_without_title(self):
        """Metadata is invalid without title."""
        metadata = AudioMetadata(artist="Artist", album="Album")
        assert metadata.is_valid() is False
    
    def test_metadata_creation(self, sample_metadata):
        """Create metadata instance."""
        assert sample_metadata.title == "Test Song"
        assert sample_metadata.artist == "Test Artist"
        assert sample_metadata.track_number == "5/12"


# Integration-like tests combining multiple components
class TestIntegration:
    """Integration tests combining multiple classes."""
    
    def test_track_to_filename_pipeline(self, file_name_builder):
        """Full pipeline: track number -> filename."""
        # Parse track
        current, total = TrackNumberParser.parse("5/12")
        
        # Build filename
        result = file_name_builder.build_filename(
            title="My Song",
            track_number="5/12",
            extension=".mp3"
        )
        
        assert result == "05 - My Song.mp3"
        assert current == 5
        assert total == 12
    
    def test_sanitize_and_build_pipeline(self, windows_sanitizer):
        """Full pipeline: sanitize + build (Windows-specific chars)."""
        # Use Windows sanitizer to test Windows-specific behavior
        builder = AudioFileNameBuilder(windows_sanitizer)
        result = builder.build_filename(
            title="Song: Title?",  # Invalid chars on Windows
            track_number="3",
            extension=".mp3"
        )
        
        # These chars should be removed on Windows
        assert "?" not in result
        # Colon becomes " - " on Windows
        assert ":" not in result
        assert "03 - Song" in result
