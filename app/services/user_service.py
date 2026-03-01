import os
from sqlalchemy import text
from sqlalchemy.orm import Session

async def get_user_mail(db: Session, user_id: str) -> str:
    
    # ユーザーテーブルからメールアドレスを取得するロジックを実装
    # 例: user = db.query(User).filter(User.id == user_id).first()
    #     return user.email if user else None

    authuser_email = await get_user_mail_from_authuser(db, user_id)
    return authuser_email


async def get_user_mail_from_authuser(db: Session, user_id: str) -> str:

    query = text("""
      select email 
      from auth.users 
      where id = :user_id;
    """)
    result = db.execute(query, {"user_id": user_id})
    rows = [dict(row._mapping) for row in result]
    return rows[0]["email"] if rows else None
