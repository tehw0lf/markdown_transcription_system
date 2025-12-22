#!/usr/bin/env python3
"""
Universal Markdown Audio Transcription System
Provides local, private, and free audio transcription for any markdown-based note-taking system.
"""

import os
import json
import re
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple
import fcntl
import shutil

from .config import ConfigManager, ConfigurationError

class MarkdownTranscriptionSystem:
    """Universal markdown transcription system that works with any markdown-based note-taking app"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.vault_path = self.config.get_vault_path()
        self.audio_folder = self.config.get_audio_folder()
        self.transcripts_folder = self.config.get_transcripts_folder()
        self.supported_extensions = self.config.get_supported_extensions()
        self.encoding = self.config.get("encoding")
        
        # Set up logging
        self.setup_logging()
        
        # Create directories
        self.setup_directories()
        
        # Load templates
        self.load_templates()
    
    def setup_logging(self):
        """Set up logging configuration"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        
        # Configure logging handlers
        handlers = []
        
        if self.config.get("file_logging", True):
            log_file = Path(self.config.get("log_file"))
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_file))
        
        if self.config.get("console_logging", True):
            handlers.append(logging.StreamHandler())
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            self.audio_folder,
            self.transcripts_folder,
            Path(self.config.get("lock_file")).parent,
            Path(self.config.get("temp_dir"))
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_templates(self):
        """Load template content from files"""
        try:
            self.transcript_template = self.config.load_template("transcript")
            self.link_template = self.config.load_template("link")
        except ConfigurationError as e:
            self.logger.warning(f"Template loading error: {e}")
            # Fall back to basic templates
            self.transcript_template = """# Transcription: {filename}

**File:** `{filename}`  
**Date:** {date}  
**Original Location:** `{audio_folder}/{filename}`

## Transcript

{transcript_content}

## Detailed Timestamps

{timestamp_content}"""
            self.link_template = "📝 **Transcript:** [[{audio_name}_transcript]]"
    
    def acquire_lock(self) -> bool:
        """Acquire file lock to prevent multiple instances"""
        try:
            self.lock_file = open(self.config.get("lock_file"), 'w')
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except (IOError, OSError):
            self.logger.warning("Another instance is already running")
            return False
    
    def release_lock(self):
        """Release the file lock"""
        if hasattr(self, 'lock_file'):
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close()
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        try:
            subprocess.run(["whisper", "--help"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error("Whisper is not installed! Install with: sudo apt install python-openai-whisper OR pip install --global openai-whisper")
            return False
    
    def find_media_files(self) -> List[Path]:
        """Find all media files that need transcription"""
        media_files = []
        
        if self.config.get("recursive_search", True):
            # Search recursively through all subdirectories
            search_pattern = "**/*"
        else:
            # Search only in vault root
            search_pattern = "*"
        
        for file_path in self.vault_path.glob(search_pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                # Skip files already in the audio folder
                if file_path.parent == self.audio_folder:
                    continue
                
                # Check if transcript already exists
                transcript_file = self.transcripts_folder / f"{file_path.stem}_transcript.md"
                if not transcript_file.exists() or not self.config.get("skip_existing_transcripts", True):
                    media_files.append(file_path)
                else:
                    self.logger.info(f"Skipping {file_path.name} - transcript already exists")
        
        return media_files
    
    def transcribe_file(self, file_path: Path) -> bool:
        """Transcribe a single media file using Whisper"""
        self.logger.info(f"Transcribing: {file_path.name}")
        
        temp_dir = Path(self.config.get("temp_dir"))
        
        try:
            # Prepare Whisper command
            cmd = [
                "whisper",
                str(file_path),
                "--model", self.config.get("whisper_model"),
                "--output_format", "json",
                "--output_dir", str(temp_dir)
            ]
            
            # Add language parameter if not auto
            if self.config.get("language") != "auto":
                cmd.extend(["--language", self.config.get("language")])
            
            # Run Whisper
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"Whisper failed for {file_path.name}: {result.stderr}")
                return False
            
            # Process the JSON output
            json_file = temp_dir / f"{file_path.stem}.json"
            if json_file.exists():
                success = self.create_markdown_transcript(json_file, file_path)
                
                # Clean up temp files
                for temp_file in temp_dir.glob(f"{file_path.stem}.*"):
                    temp_file.unlink()
                
                if success:
                    # Move media file to audio folder if configured
                    if self.config.get("auto_move_files", True):
                        destination = self.audio_folder / file_path.name
                        shutil.move(str(file_path), str(destination))
                        self.logger.info(f"✓ Moved {file_path.name} to {self.config.get('audio_folder_name')} folder")
                        
                        # Fix ownership if specified
                        self.fix_ownership(destination)
                    
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error transcribing {file_path.name}: {e}")
            return False
    
    def create_markdown_transcript(self, json_file: Path, original_file: Path) -> bool:
        """Create a markdown transcript from Whisper JSON output using templates"""
        try:
            with open(json_file, 'r', encoding=self.encoding) as f:
                data = json.load(f)
            
            transcript_file = self.transcripts_folder / f"{original_file.stem}_transcript.md"
            
            # Prepare transcript content
            transcript_content = ""
            timestamp_content = ""
            
            for segment in data.get('segments', []):
                transcript_content += f"{segment.get('text', '').strip()}\n"
                
                if self.config.get("create_timestamps", True):
                    start_time = segment.get('start', 0)
                    minutes = int(start_time // 60)
                    seconds = int(start_time % 60)
                    timestamp = f"**[{minutes}:{seconds:02d}]**"
                    text = segment.get('text', '').strip()
                    timestamp_content += f"{timestamp} {text}\n"
            
            # Use template to create final content
            content = self.transcript_template.format(
                filename=original_file.name,
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                audio_folder=self.config.get("audio_folder_name"),
                transcript_content=transcript_content.strip(),
                timestamp_content=timestamp_content.strip()
            )
            
            with open(transcript_file, 'w', encoding=self.encoding) as f:
                f.write(content)
            
            # Fix ownership if specified
            self.fix_ownership(transcript_file)
            
            self.logger.info(f"✓ Transcript saved: {transcript_file.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating transcript for {original_file.name}: {e}")
            return False
    
    def fix_ownership(self, file_path: Path):
        """Fix file ownership using configured user/group"""
        owner_user = self.config.get("owner_user")
        owner_group = self.config.get("owner_group")
        
        if owner_user and owner_group:
            try:
                shutil.chown(str(file_path), user=owner_user, group=owner_group)
            except Exception as e:
                self.logger.warning(f"Could not fix ownership for {file_path}: {e}")
    
    def generate_audio_embed_patterns(self, audio_name: str) -> List[str]:
        """Generate regex patterns for finding audio embeds based on supported extensions"""
        patterns = []
        
        for ext in self.supported_extensions:
            ext_clean = ext.lstrip('.')
            # Direct embed pattern
            patterns.append(rf'!\[\[{re.escape(audio_name)}{re.escape(ext)}\]\]')
            # Folder-prefixed embed pattern (both cases)
            patterns.append(rf'!\[\[{self.config.get("audio_folder_name").lower()}/{re.escape(audio_name)}{re.escape(ext)}\]\]')
            patterns.append(rf'!\[\[{self.config.get("audio_folder_name")}/{re.escape(audio_name)}{re.escape(ext)}\]\]')
            
            # Standard markdown image syntax
            patterns.append(rf'!\[.*?\]\({re.escape(audio_name)}{re.escape(ext)}\)')
            patterns.append(rf'!\[.*?\]\({self.config.get("audio_folder_name")}/{re.escape(audio_name)}{re.escape(ext)}\)')
        
        return patterns
    
    def find_notes_with_audio(self, audio_name: str) -> List[Path]:
        """Find all notes that contain references to a specific audio file"""
        notes_with_audio = []
        patterns = self.generate_audio_embed_patterns(audio_name)
        
        # Search through all markdown files in vault
        for note_file in self.vault_path.rglob("*.md"):
            # Skip transcript files
            if note_file.parent.name == self.config.get("transcripts_folder_name"):
                continue
            
            try:
                content = note_file.read_text(encoding=self.encoding)
                
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        notes_with_audio.append(note_file)
                        break
                        
            except Exception as e:
                self.logger.warning(f"Error reading {note_file}: {e}")
        
        return notes_with_audio
    
    def generate_transcript_link_replacements(self, audio_name: str) -> List[Tuple[str, str]]:
        """Generate pattern-replacement pairs for adding transcript links"""
        replacements = []
        
        # Use configured link format
        transcript_link = self.config.generate_link_format(audio_name)
        
        # Generate replacements for each supported extension
        for ext in self.supported_extensions:
            ext_clean = ext.lstrip('.')
            
            # Direct embed patterns
            pattern = rf'(!\[\[{re.escape(audio_name)}{re.escape(ext)}\]\])'
            replacement = f'\\1\n\n{transcript_link}'
            replacements.append((pattern, replacement))
            
            # Folder-prefixed patterns
            for folder_variant in [self.config.get("audio_folder_name").lower(), self.config.get("audio_folder_name")]:
                pattern = rf'(!\[\[{folder_variant}/{re.escape(audio_name)}{re.escape(ext)}\]\])'
                replacement = f'\\1\n\n{transcript_link}'
                replacements.append((pattern, replacement))
            
            # Standard markdown patterns
            pattern = rf'(!\[.*?\]\({re.escape(audio_name)}{re.escape(ext)}\))'
            replacement = f'\\1\n\n{transcript_link}'
            replacements.append((pattern, replacement))
        
        return replacements
    
    def add_transcript_link_to_note(self, note_path: Path, audio_name: str) -> bool:
        """Add transcript link to a note if not already present"""
        try:
            content = note_path.read_text(encoding=self.encoding)
            
            # Check if transcript link already exists
            transcript_link_check = f"{audio_name}_transcript"
            if transcript_link_check in content:
                self.logger.info(f"Transcript link already exists in {note_path.name}")
                return False
            
            # Get pattern-replacement pairs
            patterns_replacements = self.generate_transcript_link_replacements(audio_name)
            
            # Try to find and replace audio embed with transcript link
            updated = False
            for pattern, replacement in patterns_replacements:
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    updated = True
                    break
            
            if updated:
                note_path.write_text(content, encoding=self.encoding)
                self.logger.info(f"✓ Added transcript link to {note_path.name}")
                return True
            else:
                self.logger.warning(f"Could not find audio embed pattern in {note_path.name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating {note_path.name}: {e}")
            return False
    
    def link_transcripts_to_notes(self):
        """Link all existing transcripts to their corresponding notes"""
        self.logger.info("Linking transcripts to notes...")
        
        # Find all transcript files
        transcript_files = list(self.transcripts_folder.glob("*_transcript.md"))
        
        for transcript_file in transcript_files:
            # Extract audio name from transcript filename
            audio_name = transcript_file.stem.replace("_transcript", "")
            
            # Find all notes that contain this audio
            notes_with_audio = self.find_notes_with_audio(audio_name)
            
            for note in notes_with_audio:
                self.add_transcript_link_to_note(note, audio_name)
    
    def run(self):
        """Main execution function"""
        self.logger.info("Starting Universal Markdown Audio Transcription System")
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Audio folder: {self.audio_folder}")
        self.logger.info(f"Transcripts folder: {self.transcripts_folder}")
        
        # Acquire lock
        if not self.acquire_lock():
            return
        
        try:
            # Check dependencies
            if not self.check_dependencies():
                return
            
            # Check if vault exists
            if not self.vault_path.exists():
                self.logger.error(f"Vault path does not exist: {self.vault_path}")
                return
            
            # Find media files to transcribe
            media_files = self.find_media_files()
            
            if not media_files:
                self.logger.info("No new files to transcribe")
            else:
                self.logger.info(f"Found {len(media_files)} files to transcribe")
                
                # Transcribe each file
                successful_transcriptions = 0
                for media_file in media_files:
                    if self.transcribe_file(media_file):
                        successful_transcriptions += 1
                
                self.logger.info(f"Successfully transcribed {successful_transcriptions}/{len(media_files)} files")
            
            # Link transcripts to notes (both new and existing)
            self.link_transcripts_to_notes()
            
            # Fix ownership of directories
            self.fix_ownership(self.audio_folder)
            self.fix_ownership(self.transcripts_folder)
            
            self.logger.info("Transcription and linking completed successfully")
            
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.release_lock()

def main():
    """Main entry point with configuration support"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Markdown Audio Transcription System")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--create-config", help="Create example configuration file")
    parser.add_argument("--config-type", choices=["obsidian", "logseq", "foam", "generic"], 
                       default="generic", help="Type of configuration to create")
    
    args = parser.parse_args()
    
    if args.create_config:
        # Create example configuration
        config_manager = ConfigManager()
        config_manager.create_example_config(args.create_config, args.config_type)
        print(f"Example configuration created at: {args.create_config}")
        return
    
    try:
        # Initialize configuration
        config_manager = ConfigManager(args.config)
        
        # Create and run transcription system
        system = MarkdownTranscriptionSystem(config_manager)
        system.run()
        
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()