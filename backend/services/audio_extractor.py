import asyncio
import os
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}


async def extract_audio(input_path: str, output_dir: str) -> str:
    """
    動画ファイルから音声を抽出する。音声ファイルはそのまま返す。

    Args:
        input_path: 入力ファイルパス
        output_dir: 出力ディレクトリ
    Returns:
        音声ファイルパス
    """
    ext = Path(input_path).suffix.lower()
    if ext in AUDIO_EXTENSIONS:
        return input_path

    output_path = os.path.join(output_dir, Path(input_path).stem + "_audio.mp3")

    cmd = [
        "ffmpeg", "-i", input_path,
        "-vn",
        "-acodec", "libmp3lame",
        "-q:a", "2",
        "-y",
        output_path
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=600)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError("ffmpeg timeout (600s)")

    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {stderr.decode()[:500]}")

    return output_path
