"""Tests for batch_processor module."""

import runpy
import sys
from pathlib import Path
import batch_processor
from batch_processor import AlbumBatchProcessor


class FakeAudio(dict):
    def __init__(self, tracknumber=None, title=None, artist=None, album=None, tracktotal=None):
        super().__init__()
        self.saved = False
        if tracknumber is not None:
            self["tracknumber"] = tracknumber
        if title is not None:
            self["title"] = [title]
        if artist is not None:
            self["artist"] = [artist]
        if album is not None:
            self["album"] = [album]
        if tracktotal is not None:
            self["tracktotal"] = [tracktotal]

    def save(self):
        self.saved = True


def test_find_audio_files_filters_supported_extensions(tmp_path):
    (tmp_path / "a.mp3").write_text("x", encoding="utf-8")
    (tmp_path / "b.flac").write_text("x", encoding="utf-8")
    (tmp_path / "c.txt").write_text("x", encoding="utf-8")

    processor = AlbumBatchProcessor()

    assert sorted(processor._find_audio_files(str(tmp_path))) == ["a.mp3", "b.flac"]


def test_find_audio_files_missing_folder_returns_empty(tmp_path):
    processor = AlbumBatchProcessor()

    assert processor._find_audio_files(str(tmp_path / "missing")) == []


def test_collect_track_info_parses_valid_tracks(tmp_path, monkeypatch):
    audio1 = FakeAudio(tracknumber=["2/10"], title="Song A", artist="Artist", album="Album")
    audio2 = FakeAudio(tracknumber=["ABC"], title="Song B", artist="Artist", album="Album")
    audio_map = {"a.mp3": audio1, "b.mp3": audio2}

    (tmp_path / "a.mp3").write_text("x", encoding="utf-8")
    (tmp_path / "b.mp3").write_text("x", encoding="utf-8")

    monkeypatch.setattr(batch_processor, "MutagenFile", lambda path, easy=True: audio_map[Path(path).name])

    processor = AlbumBatchProcessor()
    track_info = processor._collect_track_info(str(tmp_path), ["a.mp3", "b.mp3"])

    assert len(track_info) == 1
    assert track_info[0]["current"] == 2
    assert track_info[0]["total"] == 10
    assert track_info[0]["original_str"] == "2/10"


def test_collect_track_info_skips_missing_audio_and_errors(tmp_path, monkeypatch):
    (tmp_path / "none.mp3").write_text("x", encoding="utf-8")
    (tmp_path / "missing.mp3").write_text("x", encoding="utf-8")
    (tmp_path / "error.mp3").write_text("x", encoding="utf-8")

    def fake_mutagen(path, easy=True):
        name = Path(path).name
        if name == "none.mp3":
            return None
        if name == "missing.mp3":
            return FakeAudio(title="Song", artist="Artist", album="Album")
        raise RuntimeError("boom")

    monkeypatch.setattr(batch_processor, "MutagenFile", fake_mutagen)

    processor = AlbumBatchProcessor()
    track_info = processor._collect_track_info(str(tmp_path), ["none.mp3", "missing.mp3", "error.mp3"])

    assert track_info == []


def test_normalize_all_tracks_shifts_continuous_album(monkeypatch):
    processor = AlbumBatchProcessor()
    track_info = [
        {
            "path": "a.mp3",
            "audio": FakeAudio(tracknumber=["2/10"], tracktotal=["10"]),
            "filename": "a.mp3",
            "current": 2,
            "total": 10,
            "original_str": "2/10",
        },
        {
            "path": "b.mp3",
            "audio": FakeAudio(tracknumber=["3/10"], tracktotal=["10"]),
            "filename": "b.mp3",
            "current": 3,
            "total": 10,
            "original_str": "3/10",
        },
        {
            "path": "c.mp3",
            "audio": FakeAudio(tracknumber=["4/10"], tracktotal=["10"]),
            "filename": "c.mp3",
            "current": 4,
            "total": 10,
            "original_str": "4/10",
        },
    ]

    monkeypatch.setattr(processor, "_collect_track_info", lambda folder_path, audio_files: track_info)

    processor._normalize_all_tracks("Album", ["a.mp3", "b.mp3", "c.mp3"])

    assert track_info[0]["audio"]["tracknumber"] == "1/10"
    assert track_info[1]["audio"]["tracknumber"] == "2/10"
    assert track_info[2]["audio"]["tracknumber"] == "3/10"
    assert all(item["audio"].saved for item in track_info)


def test_apply_track_shift_handles_tracks_without_total():
    processor = AlbumBatchProcessor(dry_run=True)
    track_info = [
        {
            "path": "a.mp3",
            "audio": FakeAudio(tracknumber=["5"]),
            "filename": "a.mp3",
            "current": 5,
            "total": None,
            "original_str": "5",
        }
    ]

    processor._apply_track_shift(track_info, 4)


def test_process_folder_with_normalize_tracks_calls_normalizer(tmp_path, monkeypatch):
    (tmp_path / "a.mp3").write_text("x", encoding="utf-8")

    processor = AlbumBatchProcessor()
    called = []

    monkeypatch.setattr(processor, "_normalize_all_tracks", lambda folder_path, audio_files: called.append((folder_path, tuple(audio_files))))
    monkeypatch.setattr(processor.file_renamer, "rename_file", lambda path: ("Artist", "Album", "Song"))
    monkeypatch.setattr(processor.folder_renamer, "rename_folder", lambda folder_path, artist, album: folder_path)

    processor.process_folder(str(tmp_path), normalize_tracks=True)

    assert called == [(str(tmp_path), ("a.mp3",))]


def test_normalize_all_tracks_no_track_info_returns_early(monkeypatch):
    processor = AlbumBatchProcessor()
    called = []

    monkeypatch.setattr(processor, "_collect_track_info", lambda folder_path, audio_files: [])
    monkeypatch.setattr(processor, "_apply_track_shift", lambda track_info, shift: called.append("shift"))
    monkeypatch.setattr(processor, "_fix_track_total_errors", lambda track_info: called.append("fix"))

    processor._normalize_all_tracks("Album", ["a.mp3"])

    assert called == []


def test_normalize_all_tracks_fixes_track_total_errors(monkeypatch):
    processor = AlbumBatchProcessor()
    track_info = [
        {
            "path": "a.mp3",
            "audio": FakeAudio(tracknumber=["1/1"], tracktotal=["1"]),
            "filename": "a.mp3",
            "current": 1,
            "total": 1,
            "original_str": "1/1",
        },
        {
            "path": "b.mp3",
            "audio": FakeAudio(tracknumber=["3/2"], tracktotal=["2"]),
            "filename": "b.mp3",
            "current": 3,
            "total": 2,
            "original_str": "3/2",
        },
    ]

    monkeypatch.setattr(processor, "_collect_track_info", lambda folder_path, audio_files: track_info)

    processor._normalize_all_tracks("Album", ["a.mp3", "b.mp3"])

    assert track_info[1]["audio"]["tracknumber"] == "3/3"
    assert track_info[1]["audio"]["tracktotal"] == "3"
    assert track_info[1]["audio"].saved is True


def test_apply_track_shift_handles_save_error():
    processor = AlbumBatchProcessor()

    class BrokenAudio(FakeAudio):
        def save(self):
            raise RuntimeError("save failed")

    track_info = [
        {
            "path": "a.mp3",
            "audio": BrokenAudio(tracknumber=["2/10"], tracktotal=["10"]),
            "filename": "a.mp3",
            "current": 2,
            "total": 10,
            "original_str": "2/10",
        }
    ]

    processor._apply_track_shift(track_info, 1)

    assert track_info[0]["audio"]["tracknumber"] == "1/10"


def test_process_folder_calls_file_and_folder_renamers(tmp_path, monkeypatch):
    (tmp_path / "a.mp3").write_text("x", encoding="utf-8")
    (tmp_path / "b.flac").write_text("x", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("x", encoding="utf-8")

    processor = AlbumBatchProcessor(dry_run=True)
    file_calls = []
    folder_calls = []

    def fake_rename_file(path):
        file_calls.append(Path(path).name)
        return ("Artist One; Artist Two", "Album", Path(path).stem)

    def fake_rename_folder(folder_path, artist, album):
        folder_calls.append((Path(folder_path).name, artist, album))
        return str(Path(folder_path).with_name("Artist One - Album"))

    monkeypatch.setattr(processor.file_renamer, "rename_file", fake_rename_file)
    monkeypatch.setattr(processor.folder_renamer, "rename_folder", fake_rename_folder)

    result = processor.process_folder(str(tmp_path))

    assert sorted(file_calls) == ["a.mp3", "b.flac"]
    assert folder_calls == [(tmp_path.name, "Artist One & Artist Two", "Album")]
    assert result == str(tmp_path.with_name("Artist One - Album"))


def test_fix_track_total_errors_dry_run(monkeypatch):
    processor = AlbumBatchProcessor(dry_run=True)
    track_info = [
        {
            "path": "a.mp3",
            "audio": FakeAudio(tracknumber=["3/2"], tracktotal=["2"]),
            "filename": "a.mp3",
            "current": 3,
            "total": 2,
            "original_str": "3/2",
        }
    ]

    processor._fix_track_total_errors(track_info)


def test_fix_track_total_errors_handles_save_error():
    processor = AlbumBatchProcessor()

    class BrokenAudio(FakeAudio):
        def save(self):
            raise RuntimeError("save failed")

    track_info = [
        {
            "path": "a.mp3",
            "audio": BrokenAudio(tracknumber=["3/2"], tracktotal=["2"]),
            "filename": "a.mp3",
            "current": 3,
            "total": 2,
            "original_str": "3/2",
        }
    ]

    processor._fix_track_total_errors(track_info)


def test_process_folder_without_audio_files_returns_original_path(tmp_path):
    processor = AlbumBatchProcessor()

    assert processor.process_folder(str(tmp_path)) == str(tmp_path)


def test_main_delegates_to_processor(monkeypatch, tmp_path):
    calls = []

    def fake_walk(directory, topdown=True):
        yield str(tmp_path), [], ["song.mp3"]

    def fake_process_folder(self, folder_path, normalize_tracks=False):
        calls.append((folder_path, normalize_tracks))
        return folder_path

    monkeypatch.setattr(batch_processor.os, "walk", fake_walk)
    monkeypatch.setattr(AlbumBatchProcessor, "process_folder", fake_process_folder)
    monkeypatch.setattr(sys, "argv", ["batch_processor.py", str(tmp_path), "--normalize-tracks"])

    batch_processor.main()

    assert calls == [(str(tmp_path), True)]


def test_rename_script_wrapper_invokes_batch_main(monkeypatch):
    import batch_processor as batch_module

    calls = []

    monkeypatch.setattr(batch_module, "main", lambda: calls.append("called"))
    runpy.run_module("rename_script", run_name="__main__")

    assert calls == ["called"]