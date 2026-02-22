from sqlalchemy.orm import Session
from sqlalchemy import text

def get_recent_posts(db: Session, limit: int = 10):
    """
    zst_post テーブルから最新の投稿を取得する
    """
    query = text("SELECT * FROM zst_post order by update_at desc LIMIT :limit")
    result = db.execute(query, {"limit": limit})
    return [dict(row._mapping) for row in result]