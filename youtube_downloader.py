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
            if 'total_bytes' in d and 'downloaded_bytes' in d:
                percent = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
                downloaded_mb = d['downloaded_bytes'] / (1024 * 1024)
                total_mb = d['total_bytes'] / (1024 * 1024)
                print(f"\rVideo {video_count['current'] + 1}: {percent}% ({downloaded_mb:.1f}MB/{total_mb:.1f}MB)", end='', flush=True)
                    
        elif d['status'] == 'finished':
            if video_id not in downloaded_videos:
                downloaded_videos.add(video_id)
                video_count['current'] += 1
                speed = d.get('speed', 0)
                elapsed = d.get('elapsed', 0)
                total_bytes = d.get('total_bytes', 0)
                if speed and elapsed:
                    speed_mb = speed / (1024 * 1024)  # Convert to MiB/s
                    size_mb = total_bytes / (1024 * 1024)  # Convert to MiB
                    print(f"\rVideo {video_count['current']}: Download completed - {speed_mb:.2f} MiB/s in {elapsed:.1f}s ({size_mb:.1f} MiB) ✓\033[K")
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

    def process_url(url):
        try:
            with YoutubeDL(scan_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and 'entries' in info:
                    return [e for e in info['entries'] if e]
        except Exception as e:
            print(f"\nError processing {url}: {str(e)}")
            return []
        return []

    try:
        entries = []
        if content_type == 'all':
            # Get regular videos
            print("\nScanning regular videos...")
            videos_url = f"{channel_url}/videos"
            video_entries = process_url(videos_url)
            
            # Get shorts
            print("Scanning shorts...")
            shorts_url = f"{channel_url}/shorts"
            shorts_entries = process_url(shorts_url)
            
            # Combine entries, removing duplicates based on video ID
            seen_ids = set()
            for entry in video_entries + shorts_entries:
                if entry and entry.get('id') not in seen_ids:
                    entries.append(entry)
                    seen_ids.add(entry.get('id'))
        else:
            # Add content type to URL if specified
            if content_type == 'shorts':
                channel_url = f"{channel_url}/shorts"
            elif content_type == 'videos':
                channel_url = f"{channel_url}/videos"
            entries = process_url(channel_url)

        if entries:
            total_videos = len(entries)
            if limit:
                total_videos = min(total_videos, limit)
                entries = entries[:limit]
            
            print(f"\nFound {total_videos} videos to process")
            video_count['total'] = total_videos
            
            # Add instructions for stopping the process
            print("\nPress Ctrl+C at any time to stop the download process.")
            print("Downloads completed so far will be saved.\n")
            
            # Now download the videos
            with YoutubeDL(ydl_opts) as ydl_download:
                try:
                    result = ydl_download.download([entry['url'] for entry in entries])
                    
                    if result == 0:
                        print("\nAll downloads completed!")
                    else:
                        print("\nSome downloads may have failed.")
                except KeyboardInterrupt:
                    print("\n\nDownload interrupted by user. Progress saved.")
                    print(f"Successfully downloaded {video_count['current']} out of {total_videos} videos.")
                    return
        else:
            print("\nNo videos found to download.")
                    
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
        if video_count['current'] > 0:
            print(f"Successfully downloaded {video_count['current']} videos before interruption.")
        return
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

def is_video_url(url):
    """Check if the URL is a single video URL rather than a channel."""
    return '/watch?' in url or '/shorts/' in url

def download_single_url(url, output_path, retries=3, geo_bypass=True):
    """Download a single video from its URL."""
    print(f"\nStarting download of video: {url}")
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4] / bv*[height<=1080]+ba/b[height<=1080]',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
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
        'socket_timeout': 30,
        'nocheckcertificate': True,
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print("Downloading video...")
            result = ydl.download([url])
            if result == 0:
                print("\nVideo downloaded successfully!")
                return True
            else:
                print("\nFailed to download video.")
                return False
    except Exception as e:
        print(f"\nError downloading video: {str(e)}")
        return False

def main():
    if not check_ffmpeg():
        print("\nPlease install FFmpeg before continuing.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Download YouTube videos from a channel or specific video URL.')
    parser.add_argument('url', help='YouTube channel URL or video URL')
    parser.add_argument('--output', '-o', default='downloads',
                      help='Output directory for downloaded videos')
    parser.add_argument('--type', '-t', choices=['shorts', 'videos', 'all'],
                      default='all', help='Content type to download (for channel URLs only)')
    parser.add_argument('--retries', '-r', type=int, default=3,
                      help='Number of retries for failed downloads')
    parser.add_argument('--no-geo-bypass', action='store_false', dest='geo_bypass',
                      help='Disable geo-restriction bypassing')
    parser.add_argument('--limit', '-l', type=int,
                      help='Limit the number of videos to download (for channel URLs only)')

    args = parser.parse_args()
    
    try:
        print(f"\nStarting download process...")
        create_output_dir(args.output)
        
        # Check if it's a single video URL or channel URL
        if is_video_url(args.url):
            print("Single video URL detected")
            success = download_single_url(args.url, args.output, args.retries, args.geo_bypass)
            if success:
                print("\nDownload completed successfully!")
            else:
                print("\nDownload failed.")
                sys.exit(1)
        else:
            print("Channel URL detected")
            print(f"Content type: {args.type}")
            print(f"Channel URL: {args.url}")
            print(f"Output directory: {args.output}")
            print(f"Retries: {args.retries}")
            print(f"Geo-bypass: {'enabled' if args.geo_bypass else 'disabled'}")
            if args.limit:
                print(f"Video limit: {args.limit}")
            
            download_videos(args.url, args.output, args.type, args.retries, args.geo_bypass, args.limit)
            print("\nChannel download process completed!")
            
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user. Exiting gracefully...")
        sys.exit(0)

if __name__ == "__main__":
    main() 