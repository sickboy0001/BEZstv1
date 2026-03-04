
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import text,func
from datetime import date,datetime, timezone

def get_datefromto_posts(db: Session, userid: str, start_date: date, end_date: date, limit: int = 200):
    """
    zst_post テーブルから最新の投稿を取得する
    """
    query = text("""
      SELECT 
        id,
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
        id,
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

def _update_post_ai_status(db: Session, posts: list, status: str):
    """
    内部共通関数: 指定されたステータスでstate_detailを一括更新する
    """
    # 呼び出し元がオブジェクトか辞書かに応じてIDを抽出
    # posts[0]が辞書なら p["id"]、オブジェクトなら p.id を使う
    if not posts:
        print("_update_post_ai_status:No posts to update.")
        return
    
    is_dict = isinstance(posts[0], dict)
    postids = [p["id"] if is_dict else p.id for p in posts]
    # print("_update_post_ai_status:is_dict=", is_dict, "postids=", postids)

    # 現在時刻を ISO8601 形式で生成
    current_iso_time = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # 汎用的な更新クエリ
    query = text("""

        UPDATE zstu_posts
        SET 
            state_detail = COALESCE(state_detail, '{}'::jsonb) || jsonb_build_object(
                'ai_request', 
                (COALESCE(state_detail->'ai_request', '{}'::jsonb) || jsonb_build_object(
                    'status', :status_json,
                    'updated_at', :iso_time
                ))
            ),
            updated_at = CURRENT_TIMESTAMP
        WHERE id IN :postids
    """)

    try:
        db.execute(query, {
            # 前： f'"{status}"'  -> 変更後： status
            "status_json": status,
            # 前： f'"{current_iso_time}"' -> 変更後： current_iso_time
            "iso_time": current_iso_time,
            "postids": tuple(postids)
        })
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Update Error [{status}]: {e}")
        raise e

# --- 公開用関数 ---

def update_posts_state_detail_processing(db: Session, posts):
    """AI処理中状態に更新"""
    _update_post_ai_status(db, posts, "processing")

def update_posts_state_detail_refined(db: Session, posts):
    """AI回答受領状態に更新"""
    _update_post_ai_status(db, posts, "refined")

def update_posts_state_detail_completed(db: Session, posts):
    """完了状態に更新"""
    _update_post_ai_status(db, posts, "completed")
