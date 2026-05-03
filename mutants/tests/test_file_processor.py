"""Tests for file_processor module."""

import file_processor
from audio_utils import AudioMetadata
from file_processor import AudioFileRenamer, FolderRenamer, LyricsMetadataSynchronizer


class FakeAudio(dict):
    def __init__(self, tracknumber=None, tracktotal=None):
        super().__init__()
        self.saved = False
        if tracknumber is not None:
            self["tracknumber"] = tracknumber
        if tracktotal is not None:
            self["tracktotal"] = tracktotal

    def save(self):
        self.saved = True


def test_sync_lrc_file_updates_existing_tags(tmp_path):
    lrc_path = tmp_path / "track.lrc"
    lrc_path.write_text("[ar:Old Artist]\n[ti:Old Title]\n[00:10.00]Line\n", encoding="utf-8")

    result = LyricsMetadataSynchronizer.sync_lrc_file(str(lrc_path), "New Artist", "New Title")

    assert result is True
    content = lrc_path.read_text(encoding="utf-8")
    assert "[ar:New Artist]" in content
    assert "[ti:New Title]" in content
    assert "Old Artist" not in content
    assert "Old Title" not in content


def test_sync_lrc_file_prepends_missing_tags(tmp_path):
    lrc_path = tmp_path / "track.lrc"
    lrc_path.write_text("[00:10.00]Line\n", encoding="utf-8")

    result = LyricsMetadataSynchronizer.sync_lrc_file(str(lrc_path), "New Artist", "New Title")

    assert result is True
    content = lrc_path.read_text(encoding="utf-8")
    assert content.startswith("[ar:New Artist]\n[ti:New Title]\n")


def test_sync_lrc_file_invalid_path_returns_false():
    assert LyricsMetadataSynchronizer.sync_lrc_file("/does/not/exist.lrc", "A", "T") is False


def test_audio_file_renamer_renames_audio_and_lyrics(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    lrc_path = tmp_path / "song.lrc"
    lrc_path.write_text("[ar:Old]\n[ti:Old]\n[00:10.00]Line\n", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title="My Song", artist="Artist", album="Album", track_number="1"),
    )

    renamer = AudioFileRenamer()
    artist, album, title = renamer.rename_file(str(audio_path))

    new_audio_path = tmp_path / "01 - My Song.mp3"
    new_lrc_path = tmp_path / "01 - My Song.lrc"

    assert (artist, album, title) == ("Artist", "Album", "My Song")
    assert new_audio_path.exists()
    assert not audio_path.exists()
    assert new_lrc_path.exists()
    assert not lrc_path.exists()
    assert "[ar:Artist]" in new_lrc_path.read_text(encoding="utf-8")
    assert "[ti:My Song]" in new_lrc_path.read_text(encoding="utf-8")


def test_audio_file_renamer_dry_run_keeps_files(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title="My Song", artist="Artist", album="Album", track_number="1"),
    )

    renamer = AudioFileRenamer(dry_run=True)
    result = renamer.rename_file(str(audio_path))

    assert result == ("Artist", "Album", "My Song")
    assert audio_path.exists()
    assert not (tmp_path / "01 - My Song.mp3").exists()


def test_audio_file_renamer_returns_none_for_unsupported_extension(tmp_path):
    file_path = tmp_path / "note.txt"
    file_path.write_text("text", encoding="utf-8")

    renamer = AudioFileRenamer()

    assert renamer.rename_file(str(file_path)) == (None, None, None)


def test_audio_file_renamer_returns_metadata_without_title(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title=None, artist="Artist", album="Album", track_number="1"),
    )

    renamer = AudioFileRenamer()

    assert renamer.rename_file(str(audio_path)) == ("Artist", "Album", None)
    assert audio_path.exists()


def test_audio_file_renamer_extract_metadata_exception_returns_empty(monkeypatch, tmp_path):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")

    monkeypatch.setattr(
        file_processor.MetadataExtractor,
        "extract_from_mutagen",
        lambda audio: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    renamer = AudioFileRenamer()

    assert renamer._extract_metadata(str(audio_path)) == AudioMetadata()


def test_audio_file_renamer_extract_metadata_success(monkeypatch, tmp_path):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")

    import mutagen

    monkeypatch.setattr(mutagen, "File", lambda path, easy=True: object())
    monkeypatch.setattr(
        file_processor.MetadataExtractor,
        "extract_from_mutagen",
        lambda audio: AudioMetadata(title="Song", artist="Artist", album="Album", track_number="1"),
    )

    renamer = AudioFileRenamer()

    assert renamer._extract_metadata(str(audio_path)) == AudioMetadata(
        title="Song", artist="Artist", album="Album", track_number="1"
    )


def test_audio_file_renamer_perform_rename_returns_none_when_builder_fails(monkeypatch, tmp_path):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")

    renamer = AudioFileRenamer()
    monkeypatch.setattr(renamer.file_name_builder, "build_filename", lambda title, track_number, extension: None)

    metadata = AudioMetadata(title="Song", artist="Artist", album="Album", track_number="1")

    assert renamer._perform_rename(str(audio_path), metadata) == ("Artist", "Album", None)


def test_audio_file_renamer_skips_when_destination_exists(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    existing_target = tmp_path / "01 - My Song.mp3"
    existing_target.write_text("existing", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title="My Song", artist="Artist", album="Album", track_number="1"),
    )

    renamer = AudioFileRenamer()
    result = renamer.rename_file(str(audio_path))

    assert result == ("Artist", "Album", "My Song")
    assert audio_path.exists()
    assert existing_target.exists()


def test_audio_file_renamer_handles_audio_rename_exception(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title="My Song", artist="Artist", album="Album", track_number="1"),
    )

    monkeypatch.setattr(file_processor.os, "rename", lambda src, dst: (_ for _ in ()).throw(OSError("rename failed")))

    renamer = AudioFileRenamer()

    assert renamer.rename_file(str(audio_path)) == ("Artist", "Album", "My Song")
    assert audio_path.exists()


def test_audio_file_renamer_dry_run_with_existing_lyrics(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    lrc_path = tmp_path / "song.lrc"
    lrc_path.write_text("[ti:Old]\n", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title="My Song", artist="Artist", album="Album", track_number="1"),
    )

    renamer = AudioFileRenamer(dry_run=True)
    result = renamer.rename_file(str(audio_path))

    assert result == ("Artist", "Album", "My Song")
    assert audio_path.exists()
    assert lrc_path.exists()


def test_audio_file_renamer_handles_sync_rename_without_audio_move(tmp_path):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    old_lrc = tmp_path / "alternate.lrc"
    old_lrc.write_text("[ti:Old]\n", encoding="utf-8")

    renamer = AudioFileRenamer()
    renamer.lyrics_finder.find_lyrics_file = lambda base_path, folder: (str(old_lrc), ".lrc")
    renamer.lyrics_finder.find_lyrics_by_pattern = lambda track_number, title, folder: (None, None)

    renamer._handle_lyrics(
        str(audio_path),
        str(audio_path),
        AudioMetadata(title="Song", artist="Artist", album="Album", track_number="1"),
    )

    assert not old_lrc.exists()
    assert (tmp_path / "song.lrc").exists()


def test_audio_file_renamer_handles_sync_rename_dry_run_without_audio_move(tmp_path):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    old_lrc = tmp_path / "alternate.lrc"
    old_lrc.write_text("[ti:Old]\n", encoding="utf-8")

    renamer = AudioFileRenamer(dry_run=True)
    renamer.lyrics_finder.find_lyrics_file = lambda base_path, folder: (str(old_lrc), ".lrc")
    renamer.lyrics_finder.find_lyrics_by_pattern = lambda track_number, title, folder: (None, None)

    renamer._handle_lyrics(
        str(audio_path),
        str(audio_path),
        AudioMetadata(title="Song", artist="Artist", album="Album", track_number="1"),
    )

    assert old_lrc.exists()
    assert not (tmp_path / "song.lrc").exists()


def test_audio_file_renamer_handles_sync_rename_exception_without_audio_move(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    old_lrc = tmp_path / "alternate.lrc"
    old_lrc.write_text("[ti:Old]\n", encoding="utf-8")

    renamer = AudioFileRenamer()
    renamer.lyrics_finder.find_lyrics_file = lambda base_path, folder: (str(old_lrc), ".lrc")
    renamer.lyrics_finder.find_lyrics_by_pattern = lambda track_number, title, folder: (None, None)

    real_rename = file_processor.os.rename

    def rename_side_effect(src, dst):
        if src.endswith(".lrc"):
            raise OSError("lyrics rename failed")
        return real_rename(src, dst)

    monkeypatch.setattr(file_processor.os, "rename", rename_side_effect)

    renamer._handle_lyrics(
        str(audio_path),
        str(audio_path),
        AudioMetadata(title="Song", artist="Artist", album="Album", track_number="1"),
    )

    assert old_lrc.exists()
    assert not (tmp_path / "song.lrc").exists()


def test_sync_lrc_file_returns_false_on_io_error(tmp_path, monkeypatch):
    lrc_path = tmp_path / "track.lrc"
    lrc_path.write_text("[ti:Old]\n", encoding="utf-8")

    def boom(*args, **kwargs):
        raise OSError("boom")

    import builtins

    monkeypatch.setattr(builtins, "open", boom)

    assert LyricsMetadataSynchronizer.sync_lrc_file(str(lrc_path), "New Artist", "New Title") is False


def test_audio_file_renamer_removes_redundant_lyrics_when_target_exists(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    old_lrc = tmp_path / "song.lrc"
    old_lrc.write_text("[ti:Old]\n", encoding="utf-8")
    new_lrc = tmp_path / "01 - My Song.lrc"
    new_lrc.write_text("[ti:Existing]\n", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title="My Song", artist="Artist", album="Album", track_number="1"),
    )

    renamer = AudioFileRenamer()
    result = renamer.rename_file(str(audio_path))

    assert result == ("Artist", "Album", "My Song")
    assert (tmp_path / "01 - My Song.mp3").exists()
    assert not old_lrc.exists()
    assert new_lrc.exists()


def test_audio_file_renamer_handles_lyrics_rename_exception(tmp_path, monkeypatch):
    audio_path = tmp_path / "song.mp3"
    audio_path.write_text("audio", encoding="utf-8")
    old_lrc = tmp_path / "song.lrc"
    old_lrc.write_text("[ti:Old]\n", encoding="utf-8")

    monkeypatch.setattr(
        AudioFileRenamer,
        "_extract_metadata",
        lambda self, path: AudioMetadata(title="My Song", artist="Artist", album="Album", track_number="1"),
    )

    real_rename = file_processor.os.rename

    def rename_side_effect(src, dst):
        if src.endswith(".lrc"):
            raise OSError("lyrics rename failed")
        return real_rename(src, dst)

    monkeypatch.setattr(file_processor.os, "rename", rename_side_effect)

    renamer = AudioFileRenamer()

    assert renamer.rename_file(str(audio_path)) == ("Artist", "Album", "My Song")
    assert (tmp_path / "01 - My Song.mp3").exists()
    assert old_lrc.exists()


def test_folder_renamer_renames_folder(tmp_path):
    folder = tmp_path / "old_album"
    folder.mkdir()

    renamer = FolderRenamer()
    new_path = renamer.rename_folder(str(folder), "Artist", "Album")

    assert new_path == str(tmp_path / "Artist - Album")
    assert (tmp_path / "Artist - Album").exists()
    assert not folder.exists()


def test_folder_renamer_returns_same_path_for_existing_destination(tmp_path):
    folder = tmp_path / "old_album"
    folder.mkdir()
    existing = tmp_path / "Artist - Album"
    existing.mkdir()

    renamer = FolderRenamer()

    assert renamer.rename_folder(str(folder), "Artist", "Album") == str(folder)
    assert folder.exists()


def test_folder_renamer_returns_original_when_already_named_correctly(tmp_path):
    folder = tmp_path / "Artist - Album"
    folder.mkdir()

    renamer = FolderRenamer()

    assert renamer.rename_folder(str(folder), "Artist", "Album") == str(folder)


def test_folder_renamer_returns_original_when_name_missing(tmp_path):
    folder = tmp_path / "old_album"
    folder.mkdir()

    renamer = FolderRenamer()

    assert renamer.rename_folder(str(folder), "", "Album") == str(folder)
    assert folder.exists()


def test_folder_renamer_handles_rename_exception(tmp_path, monkeypatch):
    folder = tmp_path / "old_album"
    folder.mkdir()

    def boom(src, dst):
        raise OSError("folder rename failed")

    monkeypatch.setattr(file_processor.os, "rename", boom)

    renamer = FolderRenamer()

    assert renamer.rename_folder(str(folder), "Artist", "Album") == str(folder)
    assert folder.exists()


def test_folder_renamer_dry_run_leaves_folder(tmp_path):
    folder = tmp_path / "old_album"
    folder.mkdir()

    renamer = FolderRenamer(dry_run=True)

    assert renamer.rename_folder(str(folder), "Artist", "Album") == str(folder)
    assert folder.exists()