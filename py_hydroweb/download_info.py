# © CNES

from dataclasses import dataclass
from enum import Enum


@dataclass
class DownloadInfo:
    """Info about a download progression"""

    class Status(str, Enum):
        """All possible download statuses"""

        CREATED = "CREATED"
        BLOCKED = "BLOCKED"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        CANCELLED = "CANCELLED"
        EXPIRED_NOT_PURGED = "EXPIRED_NOT_PURGED"
        EXPIRED = "EXPIRED"
        DELETED = "DELETED"

    # Download identifier
    download_id: str
    # Download current status
    status: Status
    # Download current progress estimation (0..100)
    progress: int
    # Download message (failure or information to user)
    message: str

    def __init__(self, download_id: str, status: str, progress: int = None, message: str = None) -> None:
        self.download_id = download_id
        self.status = DownloadInfo.Status(status)
        self.progress = progress
        self.message = message
