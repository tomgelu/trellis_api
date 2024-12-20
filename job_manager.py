from enum import Enum
import asyncio
from typing import Dict, Optional
import time

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job:
    def __init__(self):
        self.status = JobStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = time.time()

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Job] = {}

    def create_job(self, job_id: str) -> Job:
        job = Job()
        self.jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def update_job(self, job_id: str, status: JobStatus, result=None, error=None):
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = status
            job.result = result
            job.error = error 