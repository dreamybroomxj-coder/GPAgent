# GPAgent

An automated lecture note-taking tool. It scrapes course replay videos from HKUST-GZ's TRMS platform, converts them to audio, transcribes them with Whisper, and then uses an LLM to automatically generate summaries, key points, self-test questions, and exam/assignment intelligence — all output to Markdown files.

> [中文版 (Chinese Version)](../README.MD)

## Setup

### 1. System Requirements

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) (used for audio/video conversion and silence detection; must be added to PATH)

### 2. Installation

```bash
git clone https://github.com/dreamybroomxj-coder/GPAgent
cd GPAgent
```

Create a conda virtual environment:

```bash
conda create -n gpagent python=3.10
conda activate gpagent
pip install -r requirements.txt
# Install Playwright browser (Chromium)
playwright install chromium
```

### 3. Configuration

Rename `example_api.json` and `example_config.json` in the `config/` directory to `api.json` and `config.json`, then fill in:

- Your LLM API endpoint and key
- Your university email username and password (without the `@connect.hkust-gz.edu.cn` part, used for auto-login)

### 4. Running

Run the manual mode to test the full pipeline:

```bash
python manual.py
```

Follow the prompts to enter the TRMS playback page URL, course name, etc. The program will run through: scraping → audio conversion → transcription → AI note generation.

Automatic watch mode is still under development...

## File Structure

```
GPAgent/
├── config/                     # Configuration files
│   ├── example_config.json     # Account/course config template
│   ├── example_api.json        # API config template
│   ├── config.json             # Actual account config (gitignored)
│   ├── api.json                # Actual API config (gitignored)
│   └── state.json              # Browser login state (gitignored)
├── src/
│   ├── config.py               # Config loading helpers
│   ├── get/
│   │   ├── get.py              # Playwright-based MP4 link scraper & downloader
│   │   └── getschedule.py      # Course schedule reader
│   ├── stt/
│   │   ├── stt.py              # Speech-to-text main pipeline (chunk → transcribe → merge)
│   │   └── mp32srt.py          # Single-segment MP3 → SRT transcription
│   ├── ai/
│   │   ├── askai.py            # LLM API wrapper (ask / ask_json / ask_reason)
│   │   └── skills.py           # AI note generation (abstract / takeaways / self-test / intel / illustrations)
│   └── utils/
│       ├── mp42mp3.py          # MP4 → MP3 audio extraction (ffmpeg)
│       ├── srt2txt.py          # SRT subtitles → plain text (timestamp removal)
│       └── clean.py            # Cache cleaner (deletes files in data/ by mode)
├── data/                       # Runtime data directory (gitignored)
│   └── <course_name>/          # Organized by course: mp4 / mp3 / srt / txt / chunk/
├── export/                     # AI-generated note output (gitignored)
├── manual.py                   # Manual mode entry point — interactive full pipeline
├── ideas.MD                    # Feature planning & ideas
└── README.MD
```

## TODO

- [ ] Use prompts to have the AI generate a list of domain-specific vocabulary for the course content, to serve as a hint for speech recognition

- [ ] Automatic watch mode: read the course homepage schedule and automatically start scraping and processing right after each class ends

- [ ] Multimedia awareness: AI determines which parts of the transcript most need illustrations, locates the corresponding timestamps, captures frames from the original video, and inserts them into the notes
