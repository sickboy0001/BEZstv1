from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import date, datetime, timedelta
import logging
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID

from libsql_client import Client
from app.database_turso import get_db_turso
from app.dependencies import templates,get_current_user
from app.routers.system_logs import get_system_traces


router = APIRouter(
    prefix="/api",
    tags=["api"]
)

class TargetPeriod(BaseModel):
    start_date: date
    end_date: date

class CleaningPostRequest(BaseModel):
    user_id: UUID
    target_period: TargetPeriod
    post_ids: Optional[List[int]] = None
    target_condition: str = "none"
    loglevel: str = "normal"
    disp: str = "none"



@router.post("/cleaning-post")
async def cleaning_post_api(
    payload: CleaningPostRequest
):
    print(f"cleaning_post_api payload: {payload}")
    try:
        # TODO: ここに実際のクリーニング処理を実装
        # 現在はリクエスト内容をそのまま返却
        return {
            "status": "success",
            "message": "cleaning_post_api accepted",
            "data": payload
        }
    except Exception as e:
        logging.error(f"cleaning_post_api error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")