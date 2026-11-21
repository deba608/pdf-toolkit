from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PdfPage:
    index: int
    width: float
    height: float
    rotation: int = 0
    thumbnail: Optional[bytes] = None


@dataclass
class PdfFile:
    path: Path
    name: str
    page_count: int
    pages: List[PdfPage] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    is_encrypted: bool = False
    password: Optional[str] = None

    @property
    def size_mb(self) -> float:
        return self.path.stat().st_size / (1024 * 1024)


@dataclass
class Job:
    id: str
    operation: str
    input_files: List[PdfFile]
    output_path: Optional[Path] = None
    params: dict = field(default_factory=dict)
    status: JobStatus = JobStatus.PENDING
    progress: int = 0
    error: Optional[str] = None
    result: Optional[PdfFile] = None