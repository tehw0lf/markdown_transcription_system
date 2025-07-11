#!/usr/bin/env python3
"""
Configuration system for the Universal Markdown Audio Transcription System
Supports JSON and YAML configuration files with validation and defaults.
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

class ConfigManager:
    """Manages configuration loading, validation, and defaults"""
    
    DEFAULT_CONFIG = {
        # Paths
        "vault_path": str(Path.home() / "Notes"),
        "audio_folder_name": "Audio",
        "transcripts_folder_name": "Audio-Transcripts",
        "temp_dir": "/tmp",
        
        # Templates
        "transcript_template_path": "templates/transcript-template.md",
        "link_template_path": "templates/link-template.md",
        
        # Whisper settings
        "whisper_model": "medium",
        "language": "auto",
        
        # System settings
        "log_file": "/var/log/markdown-transcription.log",
        "lock_file": "/var/lock/markdown-transcription.lock",
        "owner_user": None,
        "owner_group": None,
        "encoding": "utf-8",
        
        # File extensions
        "audio_extensions": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma"],
        "video_extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        
        # Link format customization
        "link_format_prefix": "📝 **Transcript:**",
        "link_format_style": "wikilink",  # wikilink, standard, custom
        
        # Processing options
        "auto_move_files": True,
        "create_timestamps": True,
        "skip_existing_transcripts": True,
        "recursive_search": True,
        
        # Logging
        "log_level": "INFO",
        "console_logging": True,
        "file_logging": True
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager"""
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.logger = logging.getLogger(__name__)
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    user_config = json.load(f)
                elif config_file.suffix.lower() in ['.yaml', '.yml']:
                    user_config = yaml.safe_load(f)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {config_file.suffix}")
            
            # Merge with defaults
            self.config.update(user_config)
            
            # Validate configuration
            self._validate_config()
            
            # Expand paths
            self._expand_paths()
            
            self.logger.info(f"Configuration loaded from {config_path}")
            return self.config
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ConfigurationError(f"Invalid configuration file format: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def _validate_config(self):
        """Validate configuration values"""
        # Validate paths - but only warn if they don't exist, don't fail
        vault_path = Path(self.config["vault_path"])
        if not vault_path.exists():
            # Only raise error if this is not a default path
            if str(vault_path) != str(Path.home() / "Notes"):
                import warnings
                warnings.warn(f"Vault path does not exist: {vault_path}")
        
        # Validate whisper model
        valid_models = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
        if self.config["whisper_model"] not in valid_models:
            raise ConfigurationError(f"Invalid whisper model: {self.config['whisper_model']}")
        
        # Validate link format style
        valid_styles = ["wikilink", "standard", "custom"]
        if self.config["link_format_style"] not in valid_styles:
            raise ConfigurationError(f"Invalid link format style: {self.config['link_format_style']}")
        
        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config["log_level"] not in valid_levels:
            raise ConfigurationError(f"Invalid log level: {self.config['log_level']}")
        
        # Validate extensions
        if not self.config["audio_extensions"] and not self.config["video_extensions"]:
            raise ConfigurationError("At least one audio or video extension must be specified")
    
    def _expand_paths(self):
        """Expand relative paths to absolute paths"""
        # Expand vault path
        self.config["vault_path"] = str(Path(self.config["vault_path"]).expanduser().resolve())
        
        # Expand template paths relative to script location
        script_dir = Path(__file__).parent.parent
        for template_key in ["transcript_template_path", "link_template_path"]:
            template_path = Path(self.config[template_key])
            if not template_path.is_absolute():
                self.config[template_key] = str(script_dir / template_path)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions"""
        return self.config["audio_extensions"] + self.config["video_extensions"]
    
    def get_vault_path(self) -> Path:
        """Get vault path as Path object"""
        return Path(self.config["vault_path"])
    
    def get_audio_folder(self) -> Path:
        """Get audio folder path"""
        return self.get_vault_path() / self.config["audio_folder_name"]
    
    def get_transcripts_folder(self) -> Path:
        """Get transcripts folder path"""
        return self.get_vault_path() / self.config["transcripts_folder_name"]
    
    def load_template(self, template_type: str) -> str:
        """Load template content"""
        template_key = f"{template_type}_template_path"
        template_path = Path(self.config[template_key])
        
        if not template_path.exists():
            raise ConfigurationError(f"Template file not found: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ConfigurationError(f"Error loading template {template_path}: {e}")
    
    def generate_link_format(self, audio_name: str) -> str:
        """Generate link format based on configuration"""
        link_style = self.config["link_format_style"]
        prefix = self.config["link_format_prefix"]
        
        if link_style == "wikilink":
            return f"{prefix} [[{audio_name}_transcript]]"
        elif link_style == "standard":
            return f"{prefix} [{audio_name}_transcript]({audio_name}_transcript.md)"
        else:  # custom
            # Load custom template
            try:
                template = self.load_template("link")
                return template.format(audio_name=audio_name)
            except:
                # Fallback to wikilink
                return f"{prefix} [[{audio_name}_transcript]]"
    
    def save_config(self, config_path: str):
        """Save current configuration to file"""
        config_file = Path(config_path)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                elif config_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {config_file.suffix}")
            
            self.logger.info(f"Configuration saved to {config_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Error saving configuration: {e}")
    
    def create_example_config(self, config_path: str, config_type: str = "obsidian"):
        """Create example configuration file"""
        example_configs = {
            "obsidian": {
                "vault_path": "./vault",  # Use relative path
                "audio_folder_name": "Audio",
                "transcripts_folder_name": "Audio-Transcripts",
                "link_format_style": "wikilink",
                "link_format_prefix": "📝 **Transcript:**"
            },
            "logseq": {
                "vault_path": "./vault",  # Use relative path
                "audio_folder_name": "assets",
                "transcripts_folder_name": "transcripts",
                "link_format_style": "wikilink",
                "link_format_prefix": "📝 **Transcript:**"
            },
            "foam": {
                "vault_path": "./vault",  # Use relative path
                "audio_folder_name": "attachments",
                "transcripts_folder_name": "transcripts",
                "link_format_style": "standard",
                "link_format_prefix": "📝 **Transcript:**"
            },
            "generic": {
                "vault_path": "./vault",  # Use relative path
                "audio_folder_name": "media",
                "transcripts_folder_name": "transcripts",
                "link_format_style": "standard",
                "link_format_prefix": "📝 **Transcript:**"
            }
        }
        
        if config_type not in example_configs:
            raise ConfigurationError(f"Unknown configuration type: {config_type}")
        
        config = self.DEFAULT_CONFIG.copy()
        config.update(example_configs[config_type])
        
        config_file = Path(config_path)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                if config_file.suffix.lower() == '.json':
                    json.dump(config, f, indent=2, ensure_ascii=False)
                elif config_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                else:
                    raise ConfigurationError(f"Unsupported configuration file format: {config_file.suffix}")
            
            self.logger.info(f"Example {config_type} configuration created at {config_path}")
            
        except Exception as e:
            raise ConfigurationError(f"Error creating example configuration: {e}")