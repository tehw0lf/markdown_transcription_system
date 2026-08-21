"""Tests for MarkdownTranscriptionSystem.

These import whisper (via the module under test), which pulls in torch and
costs a few seconds at collection time. No model is ever loaded: transcription
results are passed in as plain dicts, matching the shape whisper returns.
"""

import pytest
import yaml

from src.config import ConfigManager
from src.transcription_system import MarkdownTranscriptionSystem


@pytest.fixture
def system(tmp_path):
    """A system wired to an isolated vault, with logging kept off disk."""
    vault = tmp_path / "vault"
    (vault / "notes").mkdir(parents=True)

    template = tmp_path / "transcript-template.md"
    template.write_text(
        "# Transcription: {filename}\n\n"
        "**Date:** {date}\n"
        "**Location:** [[{audio_folder}/{filename}]]\n\n"
        "## Transcript\n\n{transcript_content}\n\n"
        "## Detailed Timestamps\n\n{timestamp_content}",
        encoding="utf-8",
    )
    link_template = tmp_path / "link-template.md"
    link_template.write_text("", encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "vault_path": str(vault),
                "audio_folder_name": "Audio",
                "transcripts_folder_name": "Audio-Transcripts",
                "temp_dir": str(tmp_path / "temp"),
                "transcript_template_path": str(template),
                "link_template_path": str(link_template),
                "whisper_model": "tiny",
                "log_file": str(tmp_path / "test.log"),
                "lock_file": str(tmp_path / "test.lock"),
                "file_logging": False,
                "console_logging": False,
            }
        ),
        encoding="utf-8",
    )
    return MarkdownTranscriptionSystem(ConfigManager(str(config_path)))


def whisper_result(*segments):
    """Build a whisper-shaped result from (start, text) pairs."""
    return {
        "segments": [
            {"start": start, "end": start + 2, "text": text} for start, text in segments
        ]
    }


class TestSetup:
    def test_creates_audio_and_transcript_folders(self, system):
        assert system.audio_folder.is_dir()
        assert system.transcripts_folder.is_dir()

    def test_loads_configured_template(self, system):
        assert "{transcript_content}" in system.transcript_template


class TestTranscriptCreation:
    def test_writes_transcript_file(self, system):
        audio = system.vault_path / "talk.mp3"
        audio.touch()
        assert system.create_markdown_transcript_from_result(
            whisper_result((0.0, "Hello there.")), audio
        )
        out = system.transcripts_folder / "talk_transcript.md"
        assert out.exists()
        assert "Hello there." in out.read_text(encoding="utf-8")

    def test_fills_template_placeholders(self, system):
        audio = system.vault_path / "talk.mp3"
        audio.touch()
        system.create_markdown_transcript_from_result(
            whisper_result((0.0, "Hello there.")), audio
        )
        content = (system.transcripts_folder / "talk_transcript.md").read_text(
            encoding="utf-8"
        )
        assert "# Transcription: talk.mp3" in content
        assert "[[Audio/talk.mp3]]" in content
        assert "{filename}" not in content

    def test_formats_timestamps(self, system):
        audio = system.vault_path / "talk.mp3"
        audio.touch()
        system.create_markdown_transcript_from_result(
            whisper_result((0.0, "Start."), (65.0, "Later."), (3661.0, "Much later.")),
            audio,
        )
        content = (system.transcripts_folder / "talk_transcript.md").read_text(
            encoding="utf-8"
        )
        assert "**[0:00]** Start." in content
        assert "**[1:05]** Later." in content
        assert "**[61:01]** Much later." in content

    def test_omits_timestamps_when_disabled(self, system):
        system.config.set("create_timestamps", False)
        audio = system.vault_path / "talk.mp3"
        audio.touch()
        system.create_markdown_transcript_from_result(
            whisper_result((0.0, "Hello.")), audio
        )
        content = (system.transcripts_folder / "talk_transcript.md").read_text(
            encoding="utf-8"
        )
        assert "**[0:00]**" not in content
        assert "Hello." in content

    def test_empty_segments_still_produce_a_file(self, system):
        audio = system.vault_path / "silence.mp3"
        audio.touch()
        assert system.create_markdown_transcript_from_result({"segments": []}, audio)
        assert (system.transcripts_folder / "silence_transcript.md").exists()

    def test_template_with_unknown_placeholder_does_not_lose_transcript(self, system):
        """A typo in a template must not discard a completed transcription."""
        system.transcript_template = "{transcript_content}\n{summary_typo}"
        audio = system.vault_path / "talk.mp3"
        audio.touch()
        assert system.create_markdown_transcript_from_result(
            whisper_result((0.0, "Important content.")), audio
        )
        content = (system.transcripts_folder / "talk_transcript.md").read_text(
            encoding="utf-8"
        )
        assert "Important content." in content
        assert "{summary_typo}" in content

    def test_template_with_literal_braces_does_not_lose_transcript(self, system):
        system.transcript_template = '```json\n{"model": "tiny"}\n```\n{transcript_content}'
        audio = system.vault_path / "talk.mp3"
        audio.touch()
        assert system.create_markdown_transcript_from_result(
            whisper_result((0.0, "Important content.")), audio
        )
        content = (system.transcripts_folder / "talk_transcript.md").read_text(
            encoding="utf-8"
        )
        assert '"model": "tiny"' in content
        assert "Important content." in content


class TestMediaDiscovery:
    def test_finds_audio_in_vault(self, system):
        (system.vault_path / "a.mp3").touch()
        (system.vault_path / "notes" / "b.wav").touch()
        found = {p.name for p in system.find_media_files()}
        assert found == {"a.mp3", "b.wav"}

    def test_ignores_non_media_files(self, system):
        (system.vault_path / "note.md").touch()
        (system.vault_path / "image.png").touch()
        assert system.find_media_files() == []

    def test_skips_files_already_in_audio_folder(self, system):
        (system.audio_folder / "done.mp3").touch()
        assert system.find_media_files() == []

    def test_skips_when_transcript_exists(self, system):
        (system.vault_path / "a.mp3").touch()
        (system.transcripts_folder / "a_transcript.md").write_text("x", encoding="utf-8")
        assert system.find_media_files() == []

    def test_reprocesses_when_skip_disabled(self, system):
        system.config.set("skip_existing_transcripts", False)
        (system.vault_path / "a.mp3").touch()
        (system.transcripts_folder / "a_transcript.md").write_text("x", encoding="utf-8")
        assert [p.name for p in system.find_media_files()] == ["a.mp3"]

    def test_non_recursive_search_ignores_subfolders(self, system):
        system.config.set("recursive_search", False)
        (system.vault_path / "root.mp3").touch()
        (system.vault_path / "notes" / "nested.mp3").touch()
        assert [p.name for p in system.find_media_files()] == ["root.mp3"]


class TestNoteLinking:
    def _note(self, system, body):
        note = system.vault_path / "notes" / "note.md"
        note.write_text(body, encoding="utf-8")
        return note

    @pytest.mark.parametrize(
        "embed",
        [
            "![[talk.mp3]]",
            "![[Audio/talk.mp3]]",
            "![[audio/talk.mp3]]",
            "![audio](talk.mp3)",
        ],
    )
    def test_finds_notes_for_each_embed_style(self, system, embed):
        self._note(system, f"# Note\n\n{embed}\n")
        assert [p.name for p in system.find_notes_with_audio("talk")] == ["note.md"]

    def test_ignores_notes_without_the_audio(self, system):
        self._note(system, "# Note\n\nNo audio here.\n")
        assert system.find_notes_with_audio("talk") == []

    def test_adds_link_after_embed(self, system):
        note = self._note(system, "# Note\n\n![[talk.mp3]]\n\nAfter.\n")
        assert system.add_transcript_link_to_note(note, "talk")
        content = note.read_text(encoding="utf-8")
        assert "[[talk_transcript]]" in content
        assert content.index("![[talk.mp3]]") < content.index("[[talk_transcript]]")

    def test_does_not_duplicate_existing_link(self, system):
        note = self._note(
            system, "# Note\n\n![[talk.mp3]]\n\n📝 **Transcript:** [[talk_transcript]]\n"
        )
        assert system.add_transcript_link_to_note(note, "talk") is False
        assert note.read_text(encoding="utf-8").count("talk_transcript") == 1

    def test_returns_false_when_no_embed_present(self, system):
        note = self._note(system, "# Note\n\nNothing to link.\n")
        assert system.add_transcript_link_to_note(note, "talk") is False


class TestLocking:
    def test_acquire_and_release(self, system):
        assert system.acquire_lock()
        system.release_lock()

    def test_second_holder_is_refused(self, system, tmp_path):
        assert system.acquire_lock()
        try:
            other = MarkdownTranscriptionSystem(system.config)
            assert other.acquire_lock() is False
        finally:
            system.release_lock()

    def test_failed_acquire_does_not_leak_a_descriptor(self, system):
        """run() never calls release_lock() when acquire_lock() returns False."""
        assert system.acquire_lock()
        try:
            other = MarkdownTranscriptionSystem(system.config)
            for _ in range(50):
                assert other.acquire_lock() is False
            # Nothing was published, so there is no handle left dangling.
            assert getattr(other, "lock_file", None) is None
        finally:
            system.release_lock()

    def test_release_is_idempotent(self, system):
        assert system.acquire_lock()
        system.release_lock()
        system.release_lock()  # must not raise on an already-closed handle

    def test_release_without_acquire_is_safe(self, system):
        system.release_lock()

    def test_lock_can_be_reacquired_after_release(self, system):
        assert system.acquire_lock()
        system.release_lock()
        assert system.acquire_lock()
        system.release_lock()

    def test_reports_failure_when_lock_file_cannot_be_opened(self, system, tmp_path):
        unwritable = tmp_path / "no-such-dir" / "test.lock"
        system.config.set("lock_file", str(unwritable))
        assert system.acquire_lock() is False


class TestDependencyCheck:
    """Whisper is imported lazily so this check can actually run.

    With a module-level ``import whisper`` the process died on import and the
    user got a raw traceback instead of the actionable message below.
    """

    def test_module_imports_without_whisper_installed(self):
        import importlib

        assert importlib.util.find_spec("src.transcription_system") is not None

    def test_reports_true_when_whisper_is_available(self, system):
        assert system.check_dependencies() is True

    def test_reports_false_when_whisper_is_missing(self, system, monkeypatch):
        import importlib

        def missing(name, *args, **kwargs):
            if name == "whisper":
                raise ImportError("No module named 'whisper'")
            return importlib.import_module(name, *args, **kwargs)

        monkeypatch.setattr(
            "src.transcription_system.importlib.import_module", missing
        )
        assert system.check_dependencies() is False

    def test_no_module_level_whisper_import(self):
        """Guard the lazy import: re-adding it would break check_dependencies."""
        from pathlib import Path

        import src.transcription_system as module

        source = Path(module.__file__).read_text(encoding="utf-8")
        header = source.split("class MarkdownTranscriptionSystem")[0]
        assert "\nimport whisper" not in header
        assert "\nfrom whisper" not in header
