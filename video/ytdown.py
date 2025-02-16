import yt_dlp

def download_full_video_with_captions(url, output_path='.'):
    ydl_opts = {
        # format max 720 min 480 for download speeds
        'format': 'bestvideo[height>=480][height<=720]+bestaudio[ext=m4a]/mp4',
        # Name video.mp4
        'outtmpl': f'{output_path}/video.%(ext)s',
        # Increase concurrent fragment downloads for speed
        'concurrent_fragment_downloads': 5,
        # Use FFmpeg to merge video and audio streams
        'merge_output_format': 'mp4',
        # Suppress terminal output
        'quiet': True,
        'no_warnings': True,
        # Use aria2c as the external downloader (optional)
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x', '16', '-k', '1M'],
        # Download subtitles if available:
        'writesubtitles': True,           # download official subtitles
        'writeautomaticsub': True,         # download auto-generated subtitles if no official subs available
        'subtitleslangs': ['en'],          # only download English subtitles; change as needed
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Download completed!")

if __name__ == '__main__':
    url = "https://youtu.be/O1hF25Cowv8?si=yxgLScGErbM_nUfr"
    download_full_video_with_captions(url)
