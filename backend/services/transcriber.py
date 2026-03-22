import asyncio
import os
from pathlib import Path

from loguru import logger
from openai import AsyncOpenAI

from backend.config import get_settings

WHISPER_SIZE_LIMIT = 24 * 1024 * 1024  # 24MB
CHUNK_DURATION_SEC = 600  # 10 minutes


async def transcribe_audio(audio_path: str) -> str:
    """
    Whisper APIで音声を文字起こしする。
    24MB超の場合は自動チャンク分割して結合する。

    Args:
        audio_path: 音声ファイルパス
    Returns:
        文字起こしテキスト
    """
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    file_size = os.path.getsize(audio_path)
    if file_size <= WHISPER_SIZE_LIMIT:
        return await _transcribe_single(client, audio_path)
    else:
        logger.info(f"File too large ({file_size/1024/1024:.1f}MB), chunking...")
        return await _transcribe_chunked(client, audio_path)


async def _transcribe_single(client: AsyncOpenAI, audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            language="ja",
        )
    return response.text


async def _transcribe_chunked(client: AsyncOpenAI, audio_path: str) -> str:
    output_dir = os.path.dirname(audio_path)
    stem = Path(audio_path).stem
    chunk_pattern = os.path.join(output_dir, f"{stem}_chunk_%03d.mp3")

    cmd = [
        "ffmpeg", "-i", audio_path,
        "-f", "segment",
        "-segment_time", str(CHUNK_DURATION_SEC),
        "-c", "copy",
        "-y",
        chunk_pattern
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    chunks = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.startswith(f"{stem}_chunk_") and f.endswith(".mp3")
    ])

    transcripts = []
    for chunk_path in chunks:
        text = await _transcribe_single(client, chunk_path)
        transcripts.append(text)
        os.remove(chunk_path)

    return "\n".join(transcripts)
