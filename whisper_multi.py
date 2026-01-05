"""
Ultra Whisper Transcriptor - Professional Audio Transcription Tool
A modern, efficient, and user-friendly audio transcription application
using OpenAI's Whisper API with multi-file processing support.

Features:
- Modern dark theme UI with CustomTkinter
- Multi-file batch processing with concurrent workers
- Support for 18+ audio formats
- Drag-and-drop file support (when tkinterdnd2 is available)
- Real-time progress tracking per file
- Configurable output directory and formats
- Persistent settings with API key storage
- Queue management with start/stop controls
"""

import os
import sys
import json
import threading
import re
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable, List
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    logger.info("OpenAI package loaded successfully")
except ImportError as e:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not installed. Run: pip install openai")

# Try to import TkinterDnD for drag-drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
    logger.info("TkinterDnD2 package loaded successfully")
except ImportError as e:
    DND_AVAILABLE = False
    logger.info("TkinterDnD2 not available. Drag-drop disabled. Install with: pip install tkinterdnd2")

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILE = Path.home() / ".whisper_transcriptor_config.json"

SUPPORTED_FORMATS = {
    # OpenAI Whisper officially supported
    ".mp3": "MP3 Audio",
    ".mp4": "MP4 Audio/Video",
    ".mpeg": "MPEG Audio",
    ".mpga": "MPGA Audio",
    ".m4a": "M4A Audio",
    ".wav": "WAV Audio",
    ".webm": "WebM Audio/Video",
    ".ogg": "OGG Audio",
    ".flac": "FLAC Audio",
    # Additional commonly used formats
    ".oga": "OGA Audio",
    ".opus": "Opus Audio",
    ".aac": "AAC Audio",
    ".wma": "WMA Audio",
    ".aiff": "AIFF Audio",
    ".aif": "AIF Audio",
    ".amr": "AMR Audio",
    ".3gp": "3GP Audio",
    ".3gpp": "3GPP Audio",
}

# Build file dialog filter string
FILETYPES = [
    ("All Audio Files", " ".join(f"*{ext}" for ext in SUPPORTED_FORMATS.keys())),
    ("MP3 Files", "*.mp3"),
    ("WAV Files", "*.wav"),
    ("M4A Files", "*.m4a"),
    ("FLAC Files", "*.flac"),
    ("OGG Files", "*.ogg *.oga"),
    ("All Files", "*.*"),
]

# Color Theme - Modern Dark
COLORS = {
    "bg_dark": "#1a1a2e",
    "bg_medium": "#16213e",
    "bg_light": "#0f3460",
    "accent": "#e94560",
    "accent_hover": "#ff6b6b",
    "success": "#00d26a",
    "warning": "#ffc107",
    "error": "#dc3545",
    "text": "#ffffff",
    "text_secondary": "#a0a0a0",
}

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Manages application configuration persistence."""

    DEFAULT_CONFIG = {
        "api_key": "",
        "output_dir": "",
        "create_subfolder": True,
        "max_workers": 3,
        "language": "auto",
        "output_format": "txt",
        "include_timestamps": False,
        "theme": "dark",
    }

    def __init__(self):
        self.config = self.load()

    def load(self) -> dict:
        """Load configuration from file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    logger.info("Configuration loaded successfully")
                    return {**self.DEFAULT_CONFIG, **loaded}
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load config: {e}")
        return self.DEFAULT_CONFIG.copy()

    def save(self):
        """Save configuration to file."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration saved successfully")
        except IOError as e:
            logger.error(f"Error saving config: {e}")
            messagebox.showerror("Save Error", f"Failed to save settings: {e}")

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value
        self.save()

# ============================================================================
# TRANSCRIPTION ENGINE
# ============================================================================

class TranscriptionEngine:
    """Handles the actual transcription logic using OpenAI's Whisper API."""

    # Maximum file size for Whisper API (25 MB)
    MAX_FILE_SIZE = 25 * 1024 * 1024

    def __init__(self, api_key: str):
        if not OPENAI_AVAILABLE:
            logger.error("OpenAI package not installed")
            raise ImportError("OpenAI package not installed")
        if not api_key or not api_key.strip():
            logger.error("Invalid API key provided")
            raise ValueError("API key is required")
        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    def transcribe(
        self,
        file_path: str,
        language: str = "auto",
        progress_callback: Optional[Callable] = None
    ) -> dict:
        """
        Transcribe a single audio file.

        Args:
            file_path: Path to the audio file
            language: Target language (or 'auto' for auto-detection)
            progress_callback: Optional callback for progress updates

        Returns:
            dict with 'success', 'text', 'duration', 'error' keys
        """
        result = {
            "success": False,
            "text": "",
            "duration": 0,
            "error": None,
            "file_path": file_path,
        }

        try:
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                error_msg = f"File too large ({file_size / 1024 / 1024:.1f} MB). Max: 25 MB"
                result["error"] = error_msg
                logger.warning(f"{error_msg}: {file_path}")
                return result

            logger.info(f"Starting transcription: {file_path}")
            if progress_callback:
                progress_callback("uploading", 0.3)

            with open(file_path, "rb") as audio_file:
                # Modern OpenAI API pattern
                kwargs = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "verbose_json",
                }

                if language and language != "auto":
                    kwargs["language"] = language

                if progress_callback:
                    progress_callback("transcribing", 0.5)

                response = self.client.audio.transcriptions.create(**kwargs)

            if progress_callback:
                progress_callback("complete", 1.0)

            result["success"] = True
            result["text"] = response.text
            result["duration"] = getattr(response, "duration", 0)
            result["language"] = getattr(response, "language", "unknown")
            logger.info(f"Transcription completed: {file_path}")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Transcription error for {file_path}: {error_msg}")
            # Provide more helpful error messages
            if "invalid_api_key" in error_msg.lower() or "401" in error_msg:
                result["error"] = "Invalid API key. Check settings."
            elif "rate_limit" in error_msg.lower() or "429" in error_msg:
                result["error"] = "Rate limited. Wait and retry."
            elif "insufficient_quota" in error_msg.lower():
                result["error"] = "Insufficient quota. Check OpenAI billing."
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                result["error"] = "Network error. Check connection."
            else:
                result["error"] = error_msg[:100]  # Truncate long errors

        return result

# ============================================================================
# FILE QUEUE ITEM
# ============================================================================

class FileQueueItem:
    """Represents a file in the processing queue."""

    STATUS_PENDING = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETE = "complete"
    STATUS_ERROR = "error"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        self.status = self.STATUS_PENDING
        self.progress = 0.0
        self.error_message = ""
        self.result_text = ""
        self.output_path = ""
        self.duration = 0

# ============================================================================
# PROCESSING MANAGER
# ============================================================================

class ProcessingManager:
    """Manages the file processing queue and workers."""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.queue: List[FileQueueItem] = []
        self.is_processing = False
        self.is_paused = False
        self.update_callback: Optional[Callable] = None
        self.completion_callback: Optional[Callable] = None
        self._stop_event = threading.Event()

    def add_files(self, file_paths: List[str]) -> int:
        """Add files to the queue. Returns number of files added."""
        added = 0
        for path in file_paths:
            # Normalize path
            path = os.path.normpath(path.strip())

            ext = Path(path).suffix.lower()
            if ext in SUPPORTED_FORMATS and os.path.isfile(path):
                # Check for duplicates
                if not any(item.file_path == path for item in self.queue):
                    self.queue.append(FileQueueItem(path))
                    added += 1
                    logger.debug(f"Added to queue: {path}")
                else:
                    logger.debug(f"Duplicate file skipped: {path}")
            else:
                logger.warning(f"Unsupported or invalid file: {path}")
        logger.info(f"Added {added} file(s) to queue")
        return added

    def remove_file(self, index: int):
        """Remove a file from the queue."""
        if 0 <= index < len(self.queue):
            item = self.queue[index]
            if item.status in (FileQueueItem.STATUS_PENDING, FileQueueItem.STATUS_ERROR):
                self.queue.pop(index)

    def clear_completed(self):
        """Remove all completed and error items from the queue."""
        self.queue = [
            item for item in self.queue
            if item.status not in (FileQueueItem.STATUS_COMPLETE, FileQueueItem.STATUS_ERROR, FileQueueItem.STATUS_CANCELLED)
        ]

    def clear_all(self):
        """Clear all pending items from the queue."""
        if not self.is_processing:
            self.queue.clear()

    def start_processing(self):
        """Start processing the queue."""
        if self.is_processing:
            logger.warning("Processing already in progress")
            return

        if not OPENAI_AVAILABLE:
            logger.error("OpenAI package not installed")
            raise ValueError("OpenAI package not installed. Run: pip install openai")

        api_key = self.config.get("api_key", "").strip()
        if not api_key:
            logger.error("API key not configured")
            raise ValueError("API key not configured. Click Settings to add your OpenAI API key.")

        pending = [item for item in self.queue if item.status == FileQueueItem.STATUS_PENDING]
        if not pending:
            logger.warning("No files to process")
            raise ValueError("No files to process")

        self.is_processing = True
        self.is_paused = False
        self._stop_event.clear()
        logger.info(f"Starting processing of {len(pending)} file(s)")

        thread = threading.Thread(target=self._process_queue, daemon=True)
        thread.start()

    def stop_processing(self):
        """Stop all processing."""
        self._stop_event.set()
        self.is_processing = False
        self.is_paused = False

        # Mark processing items as cancelled
        for item in self.queue:
            if item.status == FileQueueItem.STATUS_PROCESSING:
                item.status = FileQueueItem.STATUS_CANCELLED

    def _process_queue(self):
        """Internal method to process the queue."""
        api_key = self.config.get("api_key")

        try:
            engine = TranscriptionEngine(api_key)
        except Exception as e:
            logger.error(f"Failed to initialize transcription engine: {e}")
            self.is_processing = False
            if self.completion_callback:
                self.completion_callback()
            return

        max_workers = self.config.get("max_workers", 3)

        pending_items = [item for item in self.queue if item.status == FileQueueItem.STATUS_PENDING]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for item in pending_items:
                if self._stop_event.is_set():
                    break

                item.status = FileQueueItem.STATUS_PROCESSING
                self._notify_update()

                future = executor.submit(
                    self._process_single_file,
                    engine,
                    item
                )
                futures[future] = item

            for future in as_completed(futures):
                if self._stop_event.is_set():
                    break

                item = futures[future]
                try:
                    future.result()
                except Exception as e:
                    item.status = FileQueueItem.STATUS_ERROR
                    item.error_message = str(e)[:100]

                self._notify_update()

        self.is_processing = False
        stats = self.get_stats()
        logger.info(f"Processing completed. Stats: {stats}")
        if self.completion_callback:
            self.completion_callback()

    def _process_single_file(self, engine: TranscriptionEngine, item: FileQueueItem):
        """Process a single file."""
        if self._stop_event.is_set():
            item.status = FileQueueItem.STATUS_CANCELLED
            return

        def progress_cb(stage: str, progress: float):
            item.progress = progress
            self._notify_update()

        result = engine.transcribe(
            item.file_path,
            language=self.config.get("language", "auto"),
            progress_callback=progress_cb
        )

        if self._stop_event.is_set():
            item.status = FileQueueItem.STATUS_CANCELLED
            return

        if result["success"]:
            item.status = FileQueueItem.STATUS_COMPLETE
            item.result_text = result["text"]
            item.duration = result.get("duration", 0)

            # Save the transcription
            self._save_transcription(item, result["text"])
        else:
            item.status = FileQueueItem.STATUS_ERROR
            item.error_message = result["error"] or "Unknown error"

    def _save_transcription(self, item: FileQueueItem, text: str):
        """Save the transcription to a file."""
        output_dir = self.config.get("output_dir", "").strip()

        if not output_dir:
            # Default: create 'Transcripciones' folder next to the audio file
            parent_dir = os.path.dirname(os.path.dirname(item.file_path))
            if not parent_dir:
                parent_dir = os.path.dirname(item.file_path)
            output_dir = os.path.join(parent_dir, "Transcripciones")

        os.makedirs(output_dir, exist_ok=True)

        base_name = os.path.splitext(item.file_name)[0]
        output_format = self.config.get("output_format", "txt")
        output_path = os.path.join(output_dir, f"{base_name}_transcript.{output_format}")

        # Handle duplicates
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(output_dir, f"{base_name}_transcript_{counter}.{output_format}")
            counter += 1

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                if output_format == "json":
                    json.dump({
                        "source_file": item.file_path,
                        "transcription": text,
                        "timestamp": datetime.now().isoformat(),
                        "duration": item.duration,
                    }, f, ensure_ascii=False, indent=2)
                else:
                    f.write(text)

            item.output_path = output_path
            logger.info(f"Transcription saved: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save transcription: {e}")
            raise

    def _notify_update(self):
        """Notify the UI of an update."""
        if self.update_callback:
            self.update_callback()

    def get_stats(self) -> dict:
        """Get processing statistics."""
        total = len(self.queue)
        completed = sum(1 for item in self.queue if item.status == FileQueueItem.STATUS_COMPLETE)
        errors = sum(1 for item in self.queue if item.status == FileQueueItem.STATUS_ERROR)
        pending = sum(1 for item in self.queue if item.status == FileQueueItem.STATUS_PENDING)
        processing = sum(1 for item in self.queue if item.status == FileQueueItem.STATUS_PROCESSING)

        return {
            "total": total,
            "completed": completed,
            "errors": errors,
            "pending": pending,
            "processing": processing,
        }

# ============================================================================
# CUSTOM WIDGETS
# ============================================================================

class FileListItem(ctk.CTkFrame):
    """Custom widget for displaying a file in the queue."""

    STATUS_COLORS = {
        FileQueueItem.STATUS_PENDING: COLORS["text_secondary"],
        FileQueueItem.STATUS_PROCESSING: COLORS["accent"],
        FileQueueItem.STATUS_COMPLETE: COLORS["success"],
        FileQueueItem.STATUS_ERROR: COLORS["error"],
        FileQueueItem.STATUS_CANCELLED: COLORS["warning"],
    }

    STATUS_TEXT = {
        FileQueueItem.STATUS_PENDING: "Pending",
        FileQueueItem.STATUS_PROCESSING: "Processing...",
        FileQueueItem.STATUS_COMPLETE: "Complete",
        FileQueueItem.STATUS_ERROR: "Error",
        FileQueueItem.STATUS_CANCELLED: "Cancelled",
    }

    def __init__(self, master, item: FileQueueItem, on_remove: Callable, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_medium"], corner_radius=8, **kwargs)

        self.item = item
        self.on_remove = on_remove

        self.grid_columnconfigure(1, weight=1)

        # Status indicator
        self.status_dot = ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=16),
            width=30,
        )
        self.status_dot.grid(row=0, column=0, padx=(10, 5), pady=10)

        # File info container
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=10)
        info_frame.grid_columnconfigure(0, weight=1)

        # File name
        self.name_label = ctk.CTkLabel(
            info_frame,
            text=item.file_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        self.name_label.grid(row=0, column=0, sticky="w")

        # File details
        size_mb = item.file_size / (1024 * 1024)
        ext = Path(item.file_path).suffix.upper()
        self.details_label = ctk.CTkLabel(
            info_frame,
            text=f"{ext[1:]} • {size_mb:.2f} MB",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            anchor="w",
        )
        self.details_label.grid(row=1, column=0, sticky="w")

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text=self.STATUS_TEXT[item.status],
            font=ctk.CTkFont(size=11),
            width=100,
        )
        self.status_label.grid(row=0, column=2, padx=10, pady=10)

        # Remove button
        self.remove_btn = ctk.CTkButton(
            self,
            text="X",
            width=30,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=COLORS["error"],
            command=lambda: on_remove(item),
        )
        self.remove_btn.grid(row=0, column=3, padx=(0, 10), pady=10)

        self.update_status()

    def update_status(self):
        """Update the visual status of the item."""
        status = self.item.status
        color = self.STATUS_COLORS.get(status, COLORS["text_secondary"])

        self.status_dot.configure(text_color=color)

        # Show error message if available
        if status == FileQueueItem.STATUS_ERROR and self.item.error_message:
            status_text = f"Error: {self.item.error_message[:30]}..."
        else:
            status_text = self.STATUS_TEXT.get(status, "Unknown")

        self.status_label.configure(
            text=status_text,
            text_color=color
        )

        # Disable remove button while processing
        if status == FileQueueItem.STATUS_PROCESSING:
            self.remove_btn.configure(state="disabled")
        else:
            self.remove_btn.configure(state="normal")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Create the appropriate base class based on DnD availability
if DND_AVAILABLE:
    class BaseApp(ctk.CTk, TkinterDnD.DnDWrapper):
        """Base application with drag-and-drop support."""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Initialize TkinterDnD properly
            try:
                self.TkdndVersion = TkinterDnD._require(self)
                logger.info(f"TkinterDnD initialized: {self.TkdndVersion}")
            except Exception as e:
                logger.error(f"Failed to initialize TkinterDnD: {e}")
else:
    class BaseApp(ctk.CTk):
        """Base application without drag-and-drop."""
        pass


class WhisperTranscriptor(BaseApp):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Initialize configuration
        self.config = ConfigManager()
        self.processing_manager = ProcessingManager(self.config)
        self.processing_manager.update_callback = self._on_queue_update
        self.processing_manager.completion_callback = self._on_processing_complete

        # Window setup
        self.title("Ultra Whisper Transcriptor")
        self.geometry("900x700")
        self.minsize(700, 500)

        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=COLORS["bg_dark"])

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._create_header()
        self._create_toolbar()
        self._create_file_list()
        self._create_footer()
        self._create_settings_panel()

        # Setup drag and drop if available
        if DND_AVAILABLE:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind('<<Drop>>', self._on_drop)
                logger.info("Drag-and-drop enabled")
            except Exception as e:
                logger.error(f"Drag-drop setup failed: {e}")
                messagebox.showwarning(
                    "Drag-Drop Warning",
                    "Drag-and-drop initialization failed. You can still use 'Add Files' button."
                )

        # File list widgets cache
        self.file_widgets: List[FileListItem] = []

        # Check if API key is set
        if not self.config.get("api_key"):
            self.after(500, self._show_api_key_prompt)

    def _create_header(self):
        """Create the header section."""
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # Logo/Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        ctk.CTkLabel(
            title_frame,
            text="ULTRA WHISPER",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text=" TRANSCRIPTOR",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        # Settings button
        self.settings_btn = ctk.CTkButton(
            header,
            text="Settings",
            width=100,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["accent"],
            command=self._toggle_settings,
        )
        self.settings_btn.grid(row=0, column=2, padx=20, pady=15, sticky="e")

    def _create_toolbar(self):
        """Create the toolbar section."""
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        toolbar.grid_columnconfigure(2, weight=1)

        # Add files button
        self.add_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Files",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._add_files,
        )
        self.add_btn.grid(row=0, column=0, padx=(0, 10))

        # Add folder button
        self.add_folder_btn = ctk.CTkButton(
            toolbar,
            text="+ Add Folder",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_light"],
            hover_color=COLORS["accent"],
            command=self._add_folder,
        )
        self.add_folder_btn.grid(row=0, column=1, padx=(0, 10))

        # Clear buttons
        clear_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        clear_frame.grid(row=0, column=3, sticky="e")

        ctk.CTkButton(
            clear_frame,
            text="Clear Completed",
            width=120,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["text_secondary"],
            hover_color=COLORS["bg_light"],
            command=self._clear_completed,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            clear_frame,
            text="Clear All",
            width=80,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            border_width=1,
            border_color=COLORS["error"],
            text_color=COLORS["error"],
            hover_color=COLORS["bg_light"],
            command=self._clear_all,
        ).pack(side="left")

    def _create_file_list(self):
        """Create the file list section."""
        list_container = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=10)
        list_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        # Scrollable frame for file list
        self.file_list_frame = ctk.CTkScrollableFrame(
            list_container,
            fg_color="transparent",
        )
        self.file_list_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.file_list_frame.grid_columnconfigure(0, weight=1)

        # Drop zone placeholder
        self.drop_zone = ctk.CTkFrame(
            self.file_list_frame,
            fg_color=COLORS["bg_dark"],
            corner_radius=10,
            height=200,
        )
        self.drop_zone.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.drop_zone.grid_columnconfigure(0, weight=1)

        # Drop zone text
        drop_text = "Drag & Drop Audio Files Here" if DND_AVAILABLE else "Click 'Add Files' to Select Audio"
        ctk.CTkLabel(
            self.drop_zone,
            text=drop_text,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_secondary"],
        ).grid(row=0, column=0, pady=(50, 10))

        ctk.CTkLabel(
            self.drop_zone,
            text="or click 'Add Files' / 'Add Folder' button above",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        ).grid(row=1, column=0, pady=(0, 10))

        # Supported formats info
        formats_text = "Supported: " + ", ".join(ext.upper()[1:] for ext in list(SUPPORTED_FORMATS.keys())[:8]) + "..."
        ctk.CTkLabel(
            self.drop_zone,
            text=formats_text,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
        ).grid(row=2, column=0, pady=(0, 50))

    def _create_footer(self):
        """Create the footer section with controls."""
        footer = ctk.CTkFrame(self, fg_color=COLORS["bg_medium"], corner_radius=0)
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_columnconfigure(1, weight=1)

        # Stats section
        stats_frame = ctk.CTkFrame(footer, fg_color="transparent")
        stats_frame.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Ready | 0 files in queue",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"],
        )
        self.stats_label.pack(side="left")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            footer,
            width=200,
            height=8,
            progress_color=COLORS["accent"],
        )
        self.progress_bar.grid(row=0, column=1, padx=20, pady=15)
        self.progress_bar.set(0)

        # Control buttons
        control_frame = ctk.CTkFrame(footer, fg_color="transparent")
        control_frame.grid(row=0, column=2, padx=20, pady=15, sticky="e")

        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="Stop",
            width=80,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["error"],
            hover_color="#ff4444",
            state="disabled",
            command=self._stop_processing,
        )
        self.stop_btn.pack(side="left", padx=(0, 10))

        self.start_btn = ctk.CTkButton(
            control_frame,
            text="START",
            width=160,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["success"],
            hover_color="#00ff7f",
            command=self._start_processing,
        )
        self.start_btn.pack(side="left")

    def _create_settings_panel(self):
        """Create the settings panel (hidden by default)."""
        self.settings_panel = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_medium"],
            corner_radius=10,
            width=350,
        )
        self.settings_visible = False

        # Settings content
        ctk.CTkLabel(
            self.settings_panel,
            text="Settings",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 15), padx=20, anchor="w")

        # API Key
        ctk.CTkLabel(
            self.settings_panel,
            text="OpenAI API Key:",
            font=ctk.CTkFont(size=13),
        ).pack(pady=(10, 5), padx=20, anchor="w")

        self.api_key_entry = ctk.CTkEntry(
            self.settings_panel,
            width=310,
            height=35,
            placeholder_text="sk-...",
            show="*",
        )
        self.api_key_entry.pack(padx=20)
        self.api_key_entry.insert(0, self.config.get("api_key", ""))

        # Show/Hide API key toggle
        self.show_key_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            self.settings_panel,
            text="Show API Key",
            variable=self.show_key_var,
            font=ctk.CTkFont(size=12),
            command=self._toggle_api_key_visibility,
        ).pack(pady=(5, 15), padx=20, anchor="w")

        # Output directory
        ctk.CTkLabel(
            self.settings_panel,
            text="Output Directory (optional):",
            font=ctk.CTkFont(size=13),
        ).pack(pady=(10, 5), padx=20, anchor="w")

        output_frame = ctk.CTkFrame(self.settings_panel, fg_color="transparent")
        output_frame.pack(padx=20, fill="x")

        self.output_dir_entry = ctk.CTkEntry(
            output_frame,
            width=250,
            height=35,
            placeholder_text="Default: Transcripciones folder",
        )
        self.output_dir_entry.pack(side="left")
        self.output_dir_entry.insert(0, self.config.get("output_dir", ""))

        ctk.CTkButton(
            output_frame,
            text="...",
            width=50,
            height=35,
            command=self._browse_output_dir,
        ).pack(side="left", padx=(10, 0))

        # Max workers
        ctk.CTkLabel(
            self.settings_panel,
            text="Concurrent Workers:",
            font=ctk.CTkFont(size=13),
        ).pack(pady=(15, 5), padx=20, anchor="w")

        self.workers_slider = ctk.CTkSlider(
            self.settings_panel,
            from_=1,
            to=5,
            number_of_steps=4,
            width=310,
        )
        self.workers_slider.pack(padx=20)
        self.workers_slider.set(self.config.get("max_workers", 3))

        self.workers_label = ctk.CTkLabel(
            self.settings_panel,
            text=f"{int(self.workers_slider.get())} workers",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        )
        self.workers_label.pack(pady=(5, 15), padx=20, anchor="w")
        self.workers_slider.configure(command=self._on_workers_change)

        # Language selection
        ctk.CTkLabel(
            self.settings_panel,
            text="Language:",
            font=ctk.CTkFont(size=13),
        ).pack(pady=(10, 5), padx=20, anchor="w")

        self.language_var = ctk.StringVar(value=self.config.get("language", "auto"))
        self.language_menu = ctk.CTkOptionMenu(
            self.settings_panel,
            width=310,
            height=35,
            values=["auto", "en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh", "ru", "ar"],
            variable=self.language_var,
        )
        self.language_menu.pack(padx=20)

        # Output format
        ctk.CTkLabel(
            self.settings_panel,
            text="Output Format:",
            font=ctk.CTkFont(size=13),
        ).pack(pady=(15, 5), padx=20, anchor="w")

        self.format_var = ctk.StringVar(value=self.config.get("output_format", "txt"))
        format_frame = ctk.CTkFrame(self.settings_panel, fg_color="transparent")
        format_frame.pack(padx=20, anchor="w")

        for fmt in ["txt", "json"]:
            ctk.CTkRadioButton(
                format_frame,
                text=fmt.upper(),
                variable=self.format_var,
                value=fmt,
            ).pack(side="left", padx=(0, 20))

        # Save button
        ctk.CTkButton(
            self.settings_panel,
            text="Save Settings",
            width=310,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._save_settings,
        ).pack(pady=30, padx=20)

    def _toggle_settings(self):
        """Toggle settings panel visibility."""
        if self.settings_visible:
            self.settings_panel.place_forget()
            self.settings_visible = False
        else:
            self.settings_panel.place(relx=1.0, x=-370, y=70)
            self.settings_visible = True

    def _toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.show_key_var.get():
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="*")

    def _on_workers_change(self, value):
        """Handle workers slider change."""
        self.workers_label.configure(text=f"{int(value)} workers")

    def _browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_entry.delete(0, "end")
            self.output_dir_entry.insert(0, directory)

    def _save_settings(self):
        """Save settings to config."""
        api_key = self.api_key_entry.get().strip()
        
        # Basic API key validation
        if api_key and not api_key.startswith("sk-"):
            messagebox.showwarning(
                "Invalid API Key",
                "OpenAI API keys typically start with 'sk-'. Please verify your key."
            )
            return
        
        self.config.set("api_key", api_key)
        self.config.set("output_dir", self.output_dir_entry.get().strip())
        self.config.set("max_workers", int(self.workers_slider.get()))
        self.config.set("language", self.language_var.get())
        self.config.set("output_format", self.format_var.get())

        logger.info("Settings saved")
        self._toggle_settings()
        self._show_notification("Settings saved successfully!")

    def _show_api_key_prompt(self):
        """Show prompt to enter API key."""
        messagebox.showinfo(
            "Welcome!",
            "Welcome to Ultra Whisper Transcriptor!\n\n"
            "Please configure your OpenAI API key in the Settings panel to start transcribing.\n\n"
            "Get your API key at: https://platform.openai.com/api-keys"
        )
        self._toggle_settings()

    def _add_files(self):
        """Open file dialog to add files."""
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=FILETYPES,
        )
        if files:
            self._add_to_queue(list(files))

    def _add_folder(self):
        """Open folder dialog to add all audio files from a folder."""
        folder = filedialog.askdirectory(title="Select Folder with Audio Files")
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for filename in filenames:
                    ext = Path(filename).suffix.lower()
                    if ext in SUPPORTED_FORMATS:
                        files.append(os.path.join(root, filename))

            if files:
                self._add_to_queue(files)
            else:
                messagebox.showwarning("No Files", "No supported audio files found in the selected folder.")

    def _on_drop(self, event):
        """Handle drag and drop."""
        data = event.data

        # Parse dropped files - Windows paths with spaces are enclosed in braces
        if "{" in data:
            files = re.findall(r'\{([^}]+)\}|(\S+)', data)
            files = [f[0] or f[1] for f in files if f[0] or f[1]]
        else:
            files = data.split()

        # Filter to supported files and expand directories
        valid_files = []
        for f in files:
            f = f.strip().strip('"').strip("'")
            if os.path.isdir(f):
                for root, _, filenames in os.walk(f):
                    for filename in filenames:
                        ext = Path(filename).suffix.lower()
                        if ext in SUPPORTED_FORMATS:
                            valid_files.append(os.path.join(root, filename))
            elif os.path.isfile(f):
                ext = Path(f).suffix.lower()
                if ext in SUPPORTED_FORMATS:
                    valid_files.append(f)

        if valid_files:
            self._add_to_queue(valid_files)

    def _add_to_queue(self, files: List[str]):
        """Add files to the processing queue."""
        added = self.processing_manager.add_files(files)
        self._refresh_file_list()
        self._update_stats()

        if added > 0:
            self._show_notification(f"Added {added} file(s) to queue")

    def _remove_file(self, item: FileQueueItem):
        """Remove a file from the queue."""
        try:
            index = self.processing_manager.queue.index(item)
            self.processing_manager.remove_file(index)
            self._refresh_file_list()
            self._update_stats()
        except ValueError:
            pass

    def _clear_completed(self):
        """Clear completed files from queue."""
        self.processing_manager.clear_completed()
        self._refresh_file_list()
        self._update_stats()

    def _clear_all(self):
        """Clear all files from queue."""
        if self.processing_manager.is_processing:
            messagebox.showwarning("Processing", "Cannot clear queue while processing. Stop first.")
            return

        self.processing_manager.clear_all()
        self._refresh_file_list()
        self._update_stats()

    def _refresh_file_list(self):
        """Refresh the file list display."""
        # Clear existing widgets
        for widget in self.file_widgets:
            widget.destroy()
        self.file_widgets.clear()

        queue = self.processing_manager.queue

        if not queue:
            self.drop_zone.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        else:
            self.drop_zone.grid_forget()

            for i, item in enumerate(queue):
                widget = FileListItem(
                    self.file_list_frame,
                    item,
                    on_remove=self._remove_file,
                )
                widget.grid(row=i, column=0, sticky="ew", padx=5, pady=3)
                self.file_widgets.append(widget)

    def _update_stats(self):
        """Update the stats display."""
        stats = self.processing_manager.get_stats()

        if self.processing_manager.is_processing:
            status = "Processing"
            if stats["processing"] > 0:
                status = f"Processing {stats['processing']} file(s)"
        else:
            status = "Ready"

        self.stats_label.configure(
            text=f"{status} | {stats['completed']}/{stats['total']} completed"
            + (f" | {stats['errors']} errors" if stats['errors'] > 0 else "")
        )

        # Update progress bar
        if stats["total"] > 0:
            progress = stats["completed"] / stats["total"]
            self.progress_bar.set(progress)
        else:
            self.progress_bar.set(0)

    def _start_processing(self):
        """Start processing the queue."""
        try:
            self.processing_manager.start_processing()
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.add_btn.configure(state="disabled")
            self.add_folder_btn.configure(state="disabled")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _stop_processing(self):
        """Stop processing."""
        self.processing_manager.stop_processing()
        self._on_processing_complete()

    def _on_queue_update(self):
        """Handle queue update from processing thread."""
        self.after(0, self._refresh_ui)

    def _refresh_ui(self):
        """Refresh UI elements (called on main thread)."""
        for widget in self.file_widgets:
            widget.update_status()
        self._update_stats()

    def _on_processing_complete(self):
        """Handle processing completion."""
        self.after(0, self._processing_complete_ui)

    def _processing_complete_ui(self):
        """Update UI after processing complete."""
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.add_btn.configure(state="normal")
        self.add_folder_btn.configure(state="normal")
        self._refresh_ui()

        stats = self.processing_manager.get_stats()
        if stats["completed"] > 0:
            self._show_notification(f"Completed! {stats['completed']} file(s) transcribed.")

    def _show_notification(self, message: str):
        """Show a temporary notification."""
        original_text = self.stats_label.cget("text")
        original_color = COLORS["text_secondary"]
        self.stats_label.configure(text=message, text_color=COLORS["success"])
        self.after(3000, lambda: self.stats_label.configure(
            text=original_text,
            text_color=original_color
        ))

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    # Check for required packages
    missing = []

    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    if not OPENAI_AVAILABLE:
        missing.append("openai")

    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        sys.exit(1)

    app = WhisperTranscriptor()
    app.mainloop()

if __name__ == "__main__":
    main()
