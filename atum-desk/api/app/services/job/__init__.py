"""
ATUM DESK Job Services
"""
from app.services.job.queue import JobQueueService, get_job_queue_service

__all__ = ["JobQueueService", "get_job_queue_service"]
