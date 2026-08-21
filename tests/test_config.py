"""Tests for ConfigManager loading, validation, and link generation."""

import json

import pytest
import yaml

from src.config import ConfigManager, ConfigurationError


@pytest.fixture
def vault(tmp_path):
    v = tmp_path / "vault"
    v.mkdir()
    return v


def write_config(path, data, fmt="yaml"):
    path.write_text(
        json.dumps(data) if fmt == "json" else yaml.safe_dump(data),
        encoding="utf-8",
    )
    return str(path)


class TestLoading:
    def test_defaults_available_without_config_file(self):
        config = ConfigManager()
        assert config.get("whisper_model") == "medium"
        assert config.get("link_format_style") == "wikilink"

    @pytest.mark.parametrize("fmt,suffix", [("yaml", ".yaml"), ("json", ".json")])
    def test_loads_both_formats(self, tmp_path, vault, fmt, suffix):
        path = write_config(
            tmp_path / f"config{suffix}",
            {"vault_path": str(vault), "whisper_model": "tiny"},
            fmt,
        )
        config = ConfigManager(path)
        assert config.get("whisper_model") == "tiny"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ConfigurationError, match="not found"):
            ConfigManager(str(tmp_path / "nope.yaml"))

    def test_unsupported_suffix_raises(self, tmp_path):
        path = tmp_path / "config.txt"
        path.write_text("whatever", encoding="utf-8")
        with pytest.raises(ConfigurationError, match="Unsupported"):
            ConfigManager(str(path))

    def test_malformed_yaml_raises(self, tmp_path):
        path = tmp_path / "config.yaml"
        path.write_text("key: [unclosed", encoding="utf-8")
        with pytest.raises(ConfigurationError):
            ConfigManager(str(path))

    def test_user_values_merge_over_defaults(self, tmp_path, vault):
        path = write_config(
            tmp_path / "config.yaml", {"vault_path": str(vault), "language": "en"}
        )
        config = ConfigManager(path)
        assert config.get("language") == "en"
        # untouched default survives the merge
        assert config.get("encoding") == "utf-8"


class TestValidation:
    @pytest.mark.parametrize(
        "key,value,match",
        [
            ("whisper_model", "enormous", "whisper model"),
            ("link_format_style", "bogus", "link format style"),
            ("log_level", "LOUD", "log level"),
        ],
    )
    def test_invalid_values_raise(self, tmp_path, vault, key, value, match):
        path = write_config(
            tmp_path / "config.yaml", {"vault_path": str(vault), key: value}
        )
        with pytest.raises(ConfigurationError, match=match):
            ConfigManager(path)

    def test_requires_at_least_one_extension(self, tmp_path, vault):
        path = write_config(
            tmp_path / "config.yaml",
            {"vault_path": str(vault), "audio_extensions": [], "video_extensions": []},
        )
        with pytest.raises(ConfigurationError, match="extension"):
            ConfigManager(path)

    def test_nonexistent_vault_warns_but_does_not_raise(self, tmp_path):
        path = write_config(
            tmp_path / "config.yaml", {"vault_path": str(tmp_path / "absent")}
        )
        with pytest.warns(UserWarning, match="Vault path does not exist"):
            ConfigManager(path)


class TestPaths:
    def test_vault_path_is_absolute(self, tmp_path, vault):
        path = write_config(tmp_path / "config.yaml", {"vault_path": str(vault)})
        config = ConfigManager(path)
        assert config.get_vault_path().is_absolute()

    def test_folder_helpers_nest_under_vault(self, tmp_path, vault):
        path = write_config(
            tmp_path / "config.yaml",
            {
                "vault_path": str(vault),
                "audio_folder_name": "Audio",
                "transcripts_folder_name": "Transcripts",
            },
        )
        config = ConfigManager(path)
        assert config.get_audio_folder() == config.get_vault_path() / "Audio"
        assert config.get_transcripts_folder() == config.get_vault_path() / "Transcripts"

    def test_supported_extensions_combines_audio_and_video(self):
        config = ConfigManager()
        combined = config.get_supported_extensions()
        assert ".mp3" in combined and ".mp4" in combined


class TestLinkFormat:
    def _config(self, tmp_path, vault, **overrides):
        path = write_config(
            tmp_path / "config.yaml", {"vault_path": str(vault), **overrides}
        )
        return ConfigManager(path)

    def test_wikilink_style(self, tmp_path, vault):
        config = self._config(tmp_path, vault, link_format_style="wikilink")
        assert config.generate_link_format("talk") == "📝 **Transcript:** [[talk_transcript]]"

    def test_standard_style(self, tmp_path, vault):
        config = self._config(tmp_path, vault, link_format_style="standard")
        result = config.generate_link_format("talk")
        assert result == "📝 **Transcript:** [talk_transcript](talk_transcript.md)"

    def test_custom_style_uses_template(self, tmp_path, vault):
        template = tmp_path / "link.md"
        template.write_text("See [[{audio_name}_transcript]] for details", encoding="utf-8")
        config = self._config(
            tmp_path,
            vault,
            link_format_style="custom",
            link_template_path=str(template),
        )
        assert config.generate_link_format("talk") == "See [[talk_transcript]] for details"

    def test_custom_style_falls_back_when_template_missing(self, tmp_path, vault):
        config = self._config(
            tmp_path,
            vault,
            link_format_style="custom",
            link_template_path=str(tmp_path / "absent.md"),
        )
        assert config.generate_link_format("talk") == "📝 **Transcript:** [[talk_transcript]]"

    def test_custom_style_falls_back_when_template_empty(self, tmp_path, vault):
        """The shipped link-template.md is empty; that must not yield an empty link."""
        template = tmp_path / "link.md"
        template.write_text("   \n", encoding="utf-8")
        config = self._config(
            tmp_path,
            vault,
            link_format_style="custom",
            link_template_path=str(template),
        )
        assert config.generate_link_format("talk") == "📝 **Transcript:** [[talk_transcript]]"

    def test_custom_template_with_unknown_placeholder_does_not_raise(self, tmp_path, vault):
        template = tmp_path / "link.md"
        template.write_text("{audio_name} {typo_here}", encoding="utf-8")
        config = self._config(
            tmp_path,
            vault,
            link_format_style="custom",
            link_template_path=str(template),
        )
        assert config.generate_link_format("talk") == "talk {typo_here}"


class TestRoundTrip:
    @pytest.mark.parametrize("suffix", [".yaml", ".json"])
    def test_save_then_load_preserves_values(self, tmp_path, vault, suffix):
        config = ConfigManager()
        config.set("vault_path", str(vault))
        config.set("whisper_model", "tiny")
        out = tmp_path / f"saved{suffix}"
        config.save_config(str(out))

        reloaded = ConfigManager(str(out))
        assert reloaded.get("whisper_model") == "tiny"

    @pytest.mark.parametrize("kind", ["obsidian", "logseq", "foam", "generic"])
    def test_example_configs_are_valid(self, tmp_path, kind):
        out = tmp_path / f"{kind}.yaml"
        ConfigManager().create_example_config(str(out), kind)
        assert out.exists()
        data = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert data["link_format_style"] in ("wikilink", "standard", "custom")

    def test_unknown_example_type_raises(self, tmp_path):
        with pytest.raises(ConfigurationError, match="Unknown configuration type"):
            ConfigManager().create_example_config(str(tmp_path / "x.yaml"), "notepad")
