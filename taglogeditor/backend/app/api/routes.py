from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from fastapi import APIRouter, HTTPException, Body

from ..models.schemas import (
    ApplyRequest,
    ApplyResponse,
    BannedList,
    PreviewRequest,
    PreviewResponse,
    ScanRequest,
    ScanResponse,
)
from ..services.file_service import apply_changes, preview_changes, scan_directory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest):
    root = Path(request.root_path)
    if not root.exists() or not root.is_dir():
        logger.error("Invalid root path: %s", root)
        raise HTTPException(status_code=400, detail="Invalid root path")
    data = scan_directory(root, request.min_count, request.banned_rules, request.case_insensitive)
    return ScanResponse(**data)


@router.post("/preview", response_model=PreviewResponse)
async def preview(request: PreviewRequest):
    root = Path(request.root_path)
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=400, detail="Invalid root path")
    data = preview_changes(
        root,
        request.selected_to_remove,
        request.banned_rules,
        request.case_insensitive,
        request.sort_lines,
    )
    return PreviewResponse(**data)


@router.post("/apply", response_model=ApplyResponse)
async def apply(request: ApplyRequest):
    root = Path(request.root_path)
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=400, detail="Invalid root path")
    data = apply_changes(
        root,
        request.selected_to_remove,
        request.banned_rules,
        request.case_insensitive,
        request.sort_lines,
    )
    return ApplyResponse(**data)


@router.post("/banned/export")
async def export_banned(banned: BannedList):
    content = "\n".join([rule for rule in banned.rules if rule.strip()])
    return {"content": content}


@router.post("/banned/import", response_model=BannedList)
async def import_banned(banned_text: str = Body(..., media_type="text/plain")):
    rules = [line for line in banned_text.splitlines() if line.strip()]
    return BannedList(rules=rules)
