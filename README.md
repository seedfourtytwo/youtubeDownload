# YouTube Video Downloader

A Python script to download videos from YouTube. It supports downloading either all videos from a channel or a single video by URL. The script uses `yt-dlp` for efficient downloading and supports various options for customization.

## Features

- Download all videos and/or shorts from a YouTube channel
- Download single videos by URL (including regular videos and shorts)
- High-quality MP4 format downloads
- Progress tracking for each video
- Configurable retry mechanism
- Geo-restriction bypass
- Option to limit the number of downloads for testing (channel downloads only)
- Support for FFmpeg post-processing
- Smart duplicate detection when downloading both videos and shorts

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

The script supports two main modes of operation:

### 1. Download a Single Video

To download a single video, simply provide its URL:
```bash
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID
# or for shorts
python youtube_downloader.py https://www.youtube.com/shorts/VIDEO_ID
```

### 2. Download from a Channel

To download videos from a channel:
```bash
python youtube_downloader.py https://www.youtube.com/@ChannelName
```

To see all available options and their descriptions:
```bash
python youtube_downloader.py --help
# or
python youtube_downloader.py -h
```

### Command Line Options

- `url`: YouTube video URL or channel URL (required)
  ```bash
  # For single video
  python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID
  # For channel
  python youtube_downloader.py https://www.youtube.com/@ChannelName
  ```

- `--output`, `-o`: Output directory for downloaded videos (default: "downloads")
  ```bash
  python youtube_downloader.py [URL] --output ./my_videos
  ```

- `--type`, `-t`: Content type to download from channel: "shorts", "videos", or "all" (default: "all")
  ```bash
  # Download both regular videos and shorts from channel (default)
  python youtube_downloader.py [CHANNEL_URL]
  
  # Download only shorts from channel
  python youtube_downloader.py [CHANNEL_URL] --type shorts
  
  # Download only regular videos from channel
  python youtube_downloader.py [CHANNEL_URL] --type videos
  ```

- `--retries`, `-r`: Number of retries for failed downloads (default: 3)
  ```bash
  python youtube_downloader.py [URL] --retries 5
  ```

- `--no-geo-bypass`: Disable geo-restriction bypassing
  ```bash
  python youtube_downloader.py [URL] --no-geo-bypass
  ```

- `--limit`, `-l`: Limit the number of videos to download from a channel (useful for testing)
  ```bash
  python youtube_downloader.py [CHANNEL_URL] --limit 5
  ```

### Examples

1. Download a single video:
```bash
python youtube_downloader.py https://www.youtube.com/watch?v=VIDEO_ID \
  --output ./my_videos \
  --retries 5
```

2. Download from a channel with multiple options:
```bash
python youtube_downloader.py https://www.youtube.com/@SomeChannel \
  --output ./my_videos \
  --type all \
  --retries 5 \
  --limit 10
```

## Output Format

The script provides clear progress information:
1. Initial setup confirmation (FFmpeg check, options display)
2. When downloading all content types:
   - Scans for regular videos first
   - Then scans for shorts
   - Combines results and removes any duplicates
   - Shows total unique videos found
3. Download progress for each video including:
   - Download percentage
   - Current size / Total size in MB
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