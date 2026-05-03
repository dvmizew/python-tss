"""Tests for metadata_utils module."""
from audio_utils import AudioMetadata
from metadata_utils import MetadataExtractor, TrackNumberNormalizer


class MockAudio(dict):
    def __init__(self, data=None, should_raise=False):
        super().__init__(data or {})
        self.should_raise = should_raise

    def get(self, key, default=None):
        if self.should_raise:
            raise RuntimeError("boom")
        return super().get(key, default)


def test_extract_from_mutagen_prefers_albumartist():
    audio = MockAudio(
        {
            "title": ["Song"],
            "albumartist": ["Artist One", "Artist Two"],
            "artist": ["Fallback Artist"],
            "album": ["Album"],
            "tracknumber": ["5/12"],
        }
    )

    metadata = MetadataExtractor.extract_from_mutagen(audio)

    assert metadata.title == "Song"
    assert metadata.artist == "Artist One & Artist Two"
    assert metadata.album == "Album"
    assert metadata.track_number == "5/12"


def test_extract_from_mutagen_falls_back_to_artist_and_title_album():
    audio = MockAudio(
        {
            "title": ["Song"],
            "artist": ["Solo Artist"],
            "tracknumber": ["2"],
        }
    )

    metadata = MetadataExtractor.extract_from_mutagen(audio)

    assert metadata.artist == "Solo Artist"
    assert metadata.album == "Song"
    assert metadata.track_number == "2"


def test_extract_from_mutagen_handles_empty_audio():
    metadata = MetadataExtractor.extract_from_mutagen(None)

    assert metadata == AudioMetadata()


def test_extract_from_mutagen_handles_exception():
    metadata = MetadataExtractor.extract_from_mutagen(
        MockAudio({"title": ["Song"], "artist": ["Artist"]}, should_raise=True)
    )

    assert metadata == AudioMetadata()


def test_should_normalize_continuous_shift():
    should_normalize, shift = TrackNumberNormalizer.should_normalize([2, 3, 4])

    assert should_normalize is True
    assert shift == 1


def test_should_normalize_single_track_shift():
    should_normalize, shift = TrackNumberNormalizer.should_normalize([5])

    assert should_normalize is True
    assert shift == 4


def test_should_normalize_no_shift_for_valid_sequence():
    should_normalize, shift = TrackNumberNormalizer.should_normalize([1, 2, 3])

    assert should_normalize is False
    assert shift is None


def test_should_normalize_no_shift_for_gap_sequence():
    should_normalize, shift = TrackNumberNormalizer.should_normalize([1, 3])

    assert should_normalize is False
    assert shift is None


def test_should_normalize_empty_list():
    should_normalize, shift = TrackNumberNormalizer.should_normalize([])

    assert should_normalize is False
    assert shift is None


def test_apply_shift_updates_current_and_total():
    new_current, new_total = TrackNumberNormalizer.apply_shift(5, 10, 4)

    assert new_current == 1
    assert new_total == 10


def test_apply_shift_updates_total_when_needed():
    new_current, new_total = TrackNumberNormalizer.apply_shift(7, 5, 0)

    assert new_current == 7
    assert new_total == 7


def test_apply_shift_without_total():
    new_current, new_total = TrackNumberNormalizer.apply_shift(3, None, 2)

    assert new_current == 1
    assert new_total is None