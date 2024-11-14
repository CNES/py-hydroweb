# © CNES

from dataclasses import dataclass
from enum import Enum


@dataclass
class DownloadInfo:
    """Info about a download progression"""

    class Status(str, Enum):
        """All possible download statuses"""

        CREATED = "CREATED"
        RUNNING = "RUNNING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"
        CANCELED = "CANCELED"
        EXPIRED_NOT_PURGED = "EXPIRED_NOT_PURGED"
        EXPIRED = "EXPIRED"
        DELETED = "DELETED"

    # Download identifier
    download_id: str
    # Downloade current status
    status: Status
    # Download current progress estimation (0..100)
    progress: int

    def __init__(self, download_id: str, status: str, progress: int = None) -> None:
        self.download_id = download_id
        self.status = DownloadInfo.Status(status)
        self.progress = progress
