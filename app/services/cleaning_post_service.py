from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session

from app.services.db_service import get_datefromto_posts, get_postids_posts


class TargetPeriod(BaseModel):
    start_date: date
    end_date: date




  # target_condition
  #   all すべて 
  #   none 通常なので、　unprocessed requeue
  # loglevel
  #   normal 経緯のみ
  #   detail 詳細
  #   none ログなし
  # disp 
  #   none 全工程完遂
  #   targets 工程4まで（対象抽出の確認）
  #   airesult 工程7まで（AI回答の確認）
  #   results 工程9まで（DB反映直前までの確認）
class CleaningPostRequest(BaseModel):
    user_id: str
    target_period: TargetPeriod
    post_ids: Optional[List[int]] = None
    target_condition: str = "none"
    loglevel: str = "normal"
    disp: str = "none"

async def cleaning_post(
    db: Session,
    payload: CleaningPostRequest
):
  print(f"cleaning_post called")
  print(f"cleaning_post payload: {payload}")
  # 対象のポストの取得
  posts = []
  if(payload.post_ids):
    posts = get_postids_posts(db, str(payload.user_id), payload.post_ids)
  else:
    posts = get_datefromto_posts(db, str(payload.user_id), payload.target_period.start_date, payload.target_period.end_date)
  
  print(posts)
  posts = get_posts_filter_by_targetcondition(posts,payload.target_condition)



  return posts
  # 対象の条件の確認
  # ログ詳細の確認
  # 停止ポイントに従う


def get_posts_filter_by_targetcondition(posts,target_condition:str):
    if(target_condition == "all"):
        return posts
    return []


def get_prompt(db:Session,userid: str,posts):
    """
    プロンプトの入手（現状は定数からの入手を想定）
    最終的にはデータベースからの入手になる
    """
    return ""

def get_prompt_template(db: Session):
    """
    プロンプトテンプレート
    
    の入手（現状は定数からの入手を想定）
    最終的にはデータベースからの入手になる
    """
    return ""


def get_user_tags(db: Session, userid: str):
    """
    ユーザーのタグの入手（現状は定数からの入手を想定）
    最終的にはデータベースからの入手になる
    """
    return ""

