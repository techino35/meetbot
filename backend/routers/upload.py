import os
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from loguru import logger

from backend.config import get_settings
from backend.models import Job, JobStatus, UploadResponse
from backend.routers.jobs import job_store
from backend.services.audio_extractor import extract_audio
from backend.services.transcriber import transcribe_audio
from backend.services.structurer import structure_transcript
from backend.services.docs_writer import write_to_google_docs

router = APIRouter()

ALLOWED_EXTENSIONS = {
    ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac",
    ".mp4", ".mov", ".mkv", ".avi", ".webm"
}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    settings = get_settings()

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.1f}MB (max {settings.max_file_size_mb}MB)"
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    job = Job(filename=file.filename)
    job_store[job.job_id] = job

    file_path = upload_dir / f"{job.job_id}{ext}"
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"Job {job.job_id} created for file: {file.filename}")
    background_tasks.add_task(_process_job, job.job_id, str(file_path))

    return UploadResponse(job_id=job.job_id, message="Upload successful. Processing started.")


async def _process_job(job_id: str, file_path: str):
    job = job_store.get(job_id)
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    audio_path = None
    try:
        from datetime import datetime

        # Step 1: Extract audio
        job.status = JobStatus.transcribing
        job.updated_at = datetime.utcnow()
        logger.info(f"[{job_id}] Extracting audio")
        audio_path = await extract_audio(file_path, os.path.dirname(file_path))

        # Step 2: Transcribe
        logger.info(f"[{job_id}] Transcribing audio")
        transcript = await transcribe_audio(audio_path)
        job.transcript = transcript
        job.updated_at = datetime.utcnow()

        # Step 3: Structure
        job.status = JobStatus.structuring
        job.updated_at = datetime.utcnow()
        logger.info(f"[{job_id}] Structuring transcript")
        structure = await structure_transcript(transcript)
        job.structure = structure
        job.updated_at = datetime.utcnow()

        # Step 4: Write to Google Docs
        job.status = JobStatus.writing
        job.updated_at = datetime.utcnow()
        logger.info(f"[{job_id}] Writing to Google Docs")
        doc_url = await write_to_google_docs(job.filename, transcript, structure)
        job.doc_url = doc_url

        job.status = JobStatus.done
        job.updated_at = datetime.utcnow()
        logger.info(f"[{job_id}] Done: {doc_url}")

    except Exception as e:
        logger.exception(f"[{job_id}] Failed: {e}")
        job.status = JobStatus.failed
        job.error = str(e)
        from datetime import datetime
        job.updated_at = datetime.utcnow()
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if audio_path and audio_path != file_path and os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass
