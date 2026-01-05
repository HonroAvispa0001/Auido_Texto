# Ultra Whisper Transcriptor 🎙️

A modern, efficient, and user-friendly audio transcription application using OpenAI's Whisper API with multi-file batch processing support.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-Whisper--1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎨 Modern User Interface
- **Dark Theme** - Professional CustomTkinter UI with modern aesthetics
- **Real-time Progress** - Live status updates for each file
- **Drag & Drop** - Simply drag audio files into the application
- **Queue Management** - Add, remove, and organize files with ease

### ⚡ High Performance
- **Multi-threaded Processing** - Process up to 5 files concurrently
- **Batch Operations** - Handle multiple files at once
- **Smart Queue** - Start, stop, and manage processing with controls
- **Progress Tracking** - See real-time status for each file

### 🎵 Extensive Format Support
Supports **18+ audio formats** including:
```
MP3, WAV, M4A, MP4, FLAC, OGG, OGA, OPUS, AAC,
WMA, AIFF, AIF, AMR, WEBM, MPEG, MPGA, 3GP, 3GPP
```

### ⚙️ Configurable Settings
- **API Key Management** - Secure storage of OpenAI API key
- **Language Selection** - Auto-detect or choose from 13+ languages
- **Output Options** - Save as TXT or JSON format
- **Custom Output Directory** - Choose where transcriptions are saved
- **Worker Configuration** - Adjust concurrent processing (1-5 workers)

## 📸 Screenshots

![Main Interface](https://via.placeholder.com/800x600?text=Main+Interface)

*Modern dark theme with file queue and real-time progress*

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HonroAvispa0001/Auido_Texto.git
   cd Auido_Texto
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python whisper_multi.py
   ```

4. **Configure your API key**
   - Click the "Settings" button
   - Enter your OpenAI API key
   - Click "Save Settings"

## 💡 Usage

### Adding Files

**Method 1: Drag & Drop**
- Drag audio files or folders directly into the application window

**Method 2: Add Files Button**
- Click "+ Add Files" button
- Select one or more audio files

**Method 3: Add Folder**
- Click "+ Add Folder" button
- Select a folder containing audio files
- All supported audio files will be added automatically

### Processing

1. Add your audio files to the queue
2. Click the **START** button
3. Watch real-time progress for each file
4. Transcriptions are automatically saved when complete

### Settings

Access settings by clicking the "Settings" button:

- **OpenAI API Key**: Your API key for Whisper transcription
- **Output Directory**: Custom location for transcriptions (optional)
- **Concurrent Workers**: Number of files to process simultaneously (1-5)
- **Language**: Auto-detect or specify language (en, es, fr, de, etc.)
- **Output Format**: Choose TXT or JSON format

## 📁 Output

Transcriptions are saved to the `Transcripciones` folder by default:

### TXT Format
```
audio_file_transcript.txt
```
Plain text transcription of the audio content.

### JSON Format
```json
{
  "source_file": "/path/to/audio.mp3",
  "transcription": "Transcribed text here...",
  "timestamp": "2025-01-05T16:30:00",
  "duration": 125.4
}
```

## 🛠️ Technical Details

### Architecture
- **UI Framework**: CustomTkinter (modern Tkinter wrapper)
- **API**: OpenAI Python SDK (latest)
- **Concurrency**: ThreadPoolExecutor for parallel processing
- **Config**: JSON-based persistent storage

### File Size Limit
- Maximum file size: **25 MB** (OpenAI Whisper API limit)
- Files larger than 25 MB will show an error

### Supported Languages
```
Auto-detect, English, Spanish, French, German, Italian,
Portuguese, Dutch, Japanese, Korean, Chinese, Russian, Arabic
```

## 📋 Requirements

See `requirements.txt` for full list:
- `openai>=1.0.0` - OpenAI API client
- `customtkinter>=5.2.0` - Modern UI framework
- `tkinterdnd2>=0.3.0` - Drag-and-drop support (optional)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the Whisper API
- CustomTkinter for the modern UI framework
- All contributors and users of this project

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ using OpenAI Whisper API**
