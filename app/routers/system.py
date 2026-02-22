from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db

router = APIRouter()

@router.get("/db-test")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        # zst_post テーブルから最新10件を取得するクエリ
        query = text("SELECT * FROM zst_post order by update_at desc LIMIT 10")
        result = db.execute(query)
        
        posts = [dict(row._mapping) for row in result]
        
        return {
            "status": "success",
            "message": "zst_postの取得に成功しました",
            "data": posts
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"エラーが発生しました: {str(e)}"
        }