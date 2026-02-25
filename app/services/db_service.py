
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_datefromto_posts(db: Session, userid: str, start_date: date, end_date: date, limit: int = 200):
    """
    zst_post テーブルから最新の投稿を取得する
    """
    query = text("""
      SELECT 
        current_at ,
        title ,
        content ,
        tags ,
        state_detail
      FROM zstu_posts 
      WHERE user_id = :userid
      and current_at between  :start_date and :end_date 
      order by updated_at desc LIMIT :limit
    """)
    result = db.execute(query, {
        "userid": userid,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit
    })
    return [dict(row._mapping) for row in result]

def get_postids_posts(db: Session,userid: str,postids: List[int],  limit: int = 200):
    """
    zst_post テーブルから最新の投稿を取得する
    """
    if not postids:
        return []

    query = text("""
      SELECT 
        current_at ,
        title ,
        content ,
        tags ,
        state_detail
      FROM zstu_posts 
      WHERE user_id = :userid
      and id in :postids
      order by updated_at desc LIMIT :limit
    """)
    result = db.execute(query, {
        "userid": userid,
        "postids": tuple(postids),
        "limit": limit
    })
    return [dict(row._mapping) for row in result]