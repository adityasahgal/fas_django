from django.conf import settings
import os, subprocess

OUTPUT_DIR = os.path.join(settings.BASE_DIR, "media", "streams")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_PATH = r"C:\Users\Office Point\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe"


def start_hls_stream(camera_url, output_name):
    output_path = os.path.join(OUTPUT_DIR, f"{output_name}.m3u8")
    command = [
        FFMPEG_PATH,
        "-rtsp_transport", "tcp",
        "-i", camera_url,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-tune", "zerolatency",
        "-f", "hls",
        "-hls_time", "1",
        "-hls_list_size", "5",
        "-hls_flags", "delete_segments",
        output_path
    ]
    print("Running ffmpeg →", " ".join(command))
    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
