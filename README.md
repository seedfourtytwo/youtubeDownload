# YouTube Channel Video Downloader

A Python script to download videos or shorts from YouTube channels in the highest quality available. The script uses `yt-dlp` for efficient downloading and supports various options for customization.

## Features

- Download all videos or shorts from a YouTube channel
- High-quality MP4 format downloads
- Progress tracking for each video
- Configurable retry mechanism
- Geo-restriction bypass
- Option to limit the number of downloads for testing
- Support for FFmpeg post-processing

## Prerequisites

1. Python 3.6 or higher
2. FFmpeg installed and in system PATH

### Installing FFmpeg

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract the archive to a folder (e.g., `C:\ffmpeg`)
3. Add the bin folder (e.g., `C:\ffmpeg\bin`) to your system PATH:
   - Open System Properties > Advanced > Environment Variables
   - Under System Variables, find and select "Path"
   - Click "Edit" and add the path to FFmpeg's bin folder
4. Restart your terminal/command prompt

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

#### macOS (using Homebrew)
```bash
brew install ffmpeg
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/seedfourtytwo/youtubeDownload.git
cd youtubeDownload
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python youtube_downloader.py [CHANNEL_URL]
```

Example:
```bash
python youtube_downloader.py https://www.youtube.com/@SomeChannel/shorts
```

### Command Line Options

- `--output`, `-o`: Output directory for downloaded videos (default: "downloads")
  ```bash
  python youtube_downloader.py [CHANNEL_URL] --output ./my_videos
  ```

- `--type`, `-t`: Content type to download: "shorts" or "videos" (default: "shorts")
  ```bash
  python youtube_downloader.py [CHANNEL_URL] --type videos
  ```

- `--retries`, `-r`: Number of retries for failed downloads (default: 3)
  ```bash
  python youtube_downloader.py [CHANNEL_URL] --retries 5
  ```

- `--no-geo-bypass`: Disable geo-restriction bypassing
  ```bash
  python youtube_downloader.py [CHANNEL_URL] --no-geo-bypass
  ```

- `--limit`, `-l`: Limit the number of videos to download (useful for testing)
  ```bash
  python youtube_downloader.py [CHANNEL_URL] --limit 5
  ```

### Example with Multiple Options

```bash
python youtube_downloader.py https://www.youtube.com/@SomeChannel/shorts \
  --output ./my_videos \
  --type shorts \
  --retries 5 \
  --limit 10
```

## Output Format

The script provides clear progress information:
1. Initial setup confirmation (FFmpeg check, options display)
2. Video count and scanning progress
3. Download progress for each video including:
   - Download percentage
   - Download speed
   - Time taken
   - Completion status

## Error Handling

The script includes robust error handling for common issues:
- FFmpeg not installed
- Network connectivity problems
- Geo-restricted content
- Invalid URLs
- Missing videos

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
