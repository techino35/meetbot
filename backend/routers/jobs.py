from fastapi import APIRouter, HTTPException

from backend.models import Job, JobStatusResponse

router = APIRouter()

job_store: dict[str, Job] = {}


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        doc_url=job.doc_url,
        error=job.error,
        structure=job.structure,
    )


@router.get("/jobs", response_model=list[JobStatusResponse])
def list_jobs():
    return [
        JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            doc_url=job.doc_url,
            error=job.error,
            structure=job.structure,
        )
        for job in sorted(job_store.values(), key=lambda j: j.created_at, reverse=True)
    ]
