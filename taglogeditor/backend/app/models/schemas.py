from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    root_path: str
    min_count: int = Field(default=5, ge=1)
    banned_rules: List[str] = Field(default_factory=list)
    case_insensitive: bool = False


class ScanResponse(BaseModel):
    files_found: List[str]
    total_files: int
    counts: Dict[str, Dict[str, int]]


class Selection(BaseModel):
    __root__: Dict[str, List[str]]

    def to_dict(self) -> Dict[str, List[str]]:
        return self.__root__


class PreviewRequest(BaseModel):
    root_path: str
    selected_to_remove: Dict[str, List[str]] = Field(default_factory=dict)
    banned_rules: List[str] = Field(default_factory=list)
    case_insensitive: bool = False
    sort_lines: bool = False


class FilePreview(BaseModel):
    file: str
    before: List[str]
    after: List[str]
    removed: int


class PreviewResponse(BaseModel):
    files_modified: int
    tags_removed: int
    previews: List[FilePreview]


class ApplyRequest(PreviewRequest):
    pass


class ApplyResponse(BaseModel):
    backup_path: str
    files_modified: int
    tags_removed: int


class BannedList(BaseModel):
    rules: List[str]
    case_insensitive: bool = False
