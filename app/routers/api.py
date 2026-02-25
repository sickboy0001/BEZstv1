from fastapi import APIRouter, Depends, HTTPException
import logging
from sqlalchemy.orm import Session
from app.services.cleaning_post_service import (
    cleaning_post, CleaningPostRequest
)
from app.database import get_db


router = APIRouter(
    prefix="/api",
    tags=["api"]
)


@router.post("/cleaning-post")
async def cleaning_post_api(
    payload: CleaningPostRequest,
    db: Session = Depends(get_db)
):
    # print(f"cleaning_post_api payload: {payload}")
    try:
        result = await cleaning_post(db,payload )
        # TODO: ここに実際のクリーニング処理を実装
        # 現在はリクエスト内容をそのまま返却
        return {
            "status": "success",
            "message": "cleaning_post_api accepted",
            "data": payload,
            "result": result
        }
    except Exception as e:
        logging.error(f"cleaning_post_api error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")