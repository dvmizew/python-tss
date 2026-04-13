"""
Pytest configuration and shared fixtures for audio processing tests.
"""
import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_audio_dir():
    """Create temporary directory for audio file tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def windows_sanitizer():
    """FileNameSanitizer configured for Windows."""
    from audio_utils import FileNameSanitizer
    return FileNameSanitizer(is_windows=True)


@pytest.fixture
def unix_sanitizer():
    """FileNameSanitizer configured for Unix/Linux."""
    from audio_utils import FileNameSanitizer
    return FileNameSanitizer(is_windows=False)


@pytest.fixture
def file_name_builder():
    """AudioFileNameBuilder instance."""
    from audio_utils import AudioFileNameBuilder
    return AudioFileNameBuilder()


@pytest.fixture
def folder_name_builder():
    """FolderNameBuilder instance."""
    from audio_utils import FolderNameBuilder
    return FolderNameBuilder()


@pytest.fixture
def track_number_parser():
    """TrackNumberParser class."""
    from audio_utils import TrackNumberParser
    return TrackNumberParser()


@pytest.fixture
def lyrics_finder():
    """LyricsFileFinder class."""
    from audio_utils import LyricsFileFinder
    return LyricsFileFinder()


@pytest.fixture
def track_normalizer():
    """TrackNumberNormalizer class."""
    from metadata_utils import TrackNumberNormalizer
    return TrackNumberNormalizer()


@pytest.fixture
def sample_metadata():
    """Sample AudioMetadata for tests."""
    from audio_utils import AudioMetadata
    return AudioMetadata(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        track_number="5/12"
    )


@pytest.fixture
def sample_lrc_content():
    """Sample .lrc file content."""
    return """[ti:Old Title]
[ar:Old Artist]
[al:Test Album]
[00:10.00]First line
[00:20.00]Second line
"""


@pytest.fixture
def lrc_file_with_content(temp_audio_dir, sample_lrc_content):
    """Create a test .lrc file."""
    lrc_path = os.path.join(temp_audio_dir, "test.lrc")
    with open(lrc_path, "w", encoding="utf-8") as f:
        f.write(sample_lrc_content)
    return lrc_path


@pytest.fixture
def mock_mutagen_audio():
    """Mock Mutagen audio object."""
    class MockAudio(dict):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.saved = False
        
        def get(self, key, default=None):
            return super().get(key, default)
        
        def save(self):
            self.saved = True
    
    audio = MockAudio()
    audio["title"] = ["Test Song"]
    audio["artist"] = ["Test Artist"]
    audio["album"] = ["Test Album"]
    audio["tracknumber"] = ["5/12"]
    
    return audio


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
