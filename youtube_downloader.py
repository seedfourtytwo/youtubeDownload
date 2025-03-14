#!/usr/bin/env python3
import os
import argparse
import subprocess
import sys
from yt_dlp import YoutubeDL
from time import sleep
import threading
import itertools
import time

def check_ffmpeg():
    """Check if FFmpeg is installed and in system PATH."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"FFmpeg is installed: {version_line}")
            return True
        else:
            print("FFmpeg is installed but returned an error.")
            return False
    except FileNotFoundError:
        print("FFmpeg is not installed or not in system PATH.")
        print("\nTo install FFmpeg:")
        if sys.platform == 'win32':
            print("1. Download FFmpeg from https://ffmpeg.org/download.html")
            print("2. Extract the archive to a folder (e.g., C:\\ffmpeg)")
            print("3. Add the bin folder (e.g., C:\\ffmpeg\\bin) to your system PATH")
            print("4. Restart your terminal/command prompt")
        else:
            print("1. On Ubuntu/Debian: sudo apt-get install ffmpeg")
            print("   On macOS with Homebrew: brew install ffmpeg")
        return False
    except Exception as e:
        print(f"Error checking FFmpeg: {str(e)}")
        return False

def create_output_dir(directory):
    """Create output directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_short(info, debug=False):
    """Check if video is a short."""
    url = info.get('webpage_url', '')
    title = info.get('title', '').lower()
    original_url = info.get('original_url', '').lower()
    playlist_url = info.get('playlist_url', '').lower()
    
    # Check if video is from shorts section or has shorts indicators
    checks = {
        'url_check': any(pattern in str(url).lower() for pattern in ['/shorts/', 'shorts%2F']),
        'original_url_check': '/shorts/' in original_url,
        'playlist_check': '/shorts' in str(playlist_url),
        'title_check': any(tag in title for tag in ['#shorts', '#short', '#fyp', '#foryou', '#foryoupage'])
    }
    
    if debug:
        print("\nDebug - Short detection:")
        print(f"URL: {url}")
        print(f"Original URL: {original_url}")
        print(f"Playlist URL: {playlist_url}")
        print(f"Title: {title}")
        print(f"Checks: {checks}")
    
    # If the video comes from a shorts playlist, consider it a short
    # Otherwise, fall back to other indicators
    is_short_video = checks['playlist_check'] or checks['url_check'] or checks['original_url_check'] or checks['title_check']
    
    if debug:
        print(f"Final decision - Is short: {is_short_video}")
    
    return is_short_video

def loading_animation(stop_event, message="Discovering videos"):
    """Display an animated loading message."""
    dots = itertools.cycle(['', '.', '..', '...'])
    while not stop_event.is_set():
        sys.stdout.write(f'\r{message}{next(dots)}')
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write('\r' + ' ' * (len(message) + 3) + '\r')
    sys.stdout.flush()

def download_videos(channel_url, output_path, content_type='shorts', retries=3, geo_bypass=True, limit=None):
    """Download videos from a YouTube channel."""
    create_output_dir(output_path)
    
    # Track downloaded videos to avoid duplicates
    downloaded_videos = set()
    video_count = {'current': 0, 'total': 0}
    
    def progress_hook(d):
        video_id = d.get('info_dict', {}).get('id', '')
        
        if not video_id or video_id in downloaded_videos:
            return
            
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
                print(f"\rVideo {video_count['current']}: {percent}%", end='', flush=True)
                    
        elif d['status'] == 'finished':
            if video_id not in downloaded_videos:
                downloaded_videos.add(video_id)
                video_count['current'] += 1
                speed = d.get('speed', 0)
                elapsed = d.get('elapsed', 0)
                if speed and elapsed:
                    speed_mb = speed / (1024 * 1024)  # Convert to MiB/s
                    print(f"\rVideo {video_count['current']}: Download completed - {speed_mb:.2f} MiB/s in {elapsed:.1f}s ✓\033[K")
                else:
                    print(f"\rVideo {video_count['current']}: Download completed ✓\033[K")
    
    # Configure yt-dlp options for scanning
    scan_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'playlistend': limit if limit else None,
    }
    
    # Configure yt-dlp options for download
    ydl_opts = {
        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b',  # Prefer MP4 format
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'retries': retries,
        'fragment_retries': retries,
        'skip_unavailable_fragments': True,
        'geo_bypass': geo_bypass,
        'geo_bypass_country': 'US',
        'extractor_retries': retries,
        'file_access_retries': retries,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        },
        'socket_timeout': 30,
        'nocheckcertificate': True,
        'playlistend': limit if limit else None,
        'extractor_args': {
            'youtube': {
                'formats': 'missing_pot',
            }
        },
        'progress_hooks': [progress_hook],
        'consoletitle': True,
        'ignoreerrors': True,
    }

    # Add content type to URL if specified
    if content_type == 'shorts':
        channel_url = f"{channel_url}/shorts"
    elif content_type == 'videos':
        channel_url = f"{channel_url}/videos"

    print("Getting video count and details...")
    
    # Get video information
    try:
        with YoutubeDL(scan_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            if info and 'entries' in info:
                # Filter out None entries and get valid videos
                entries = [e for e in info['entries'] if e]
                total_videos = len(entries)
                if limit:
                    total_videos = min(total_videos, limit)
                    entries = entries[:limit]
                
                print(f"Found {total_videos} videos to process")
                video_count['total'] = total_videos
                
                # Now download the videos
                with YoutubeDL(ydl_opts) as ydl_download:
                    result = ydl_download.download([entry['url'] for entry in entries])
                
                if result == 0:
                    print("\nAll downloads completed!")
                else:
                    print("\nSome downloads may have failed.")
                    
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

def main():
    if not check_ffmpeg():
        print("\nPlease install FFmpeg before continuing.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Download YouTube videos or shorts from a channel.')
    parser.add_argument('channel_url', help='YouTube channel URL')
    parser.add_argument('--output', '-o', default='downloads',
                      help='Output directory for downloaded videos')
    parser.add_argument('--type', '-t', choices=['shorts', 'videos'],
                      default='shorts', help='Content type to download (shorts or videos)')
    parser.add_argument('--retries', '-r', type=int, default=3,
                      help='Number of retries for failed downloads')
    parser.add_argument('--no-geo-bypass', action='store_false', dest='geo_bypass',
                      help='Disable geo-restriction bypassing')
    parser.add_argument('--limit', '-l', type=int,
                      help='Limit the number of videos to download (for testing)')

    args = parser.parse_args()
    
    print(f"\nStarting download process...")
    print(f"Content type: {args.type}")
    print(f"Channel URL: {args.channel_url}")
    print(f"Output directory: {args.output}")
    print(f"Retries: {args.retries}")
    print(f"Geo-bypass: {'enabled' if args.geo_bypass else 'disabled'}")
    if args.limit:
        print(f"Video limit: {args.limit}")
    
    download_videos(args.channel_url, args.output, args.type, args.retries, args.geo_bypass, args.limit)
    print("\nDownload process completed!")

if __name__ == "__main__":
    main() 