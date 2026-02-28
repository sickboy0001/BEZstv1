from sqlalchemy.orm import Session
from sqlalchemy import text
import json

TAG_COUNT_LIMIT = 50

def get_tags_from_db(db: Session, userid: str):
    query = text("""
      SELECT 
          id,
          tag_name, 
          name, 
          COALESCE(aliases, '{}') as aliases, 
          description, 
          display_order, 
          is_active, 
          is_send_ai, 
          updated_at
      FROM zstu_tag_descriptions
      WHERE user_id = :userid
      ORDER BY display_order 
    """)
    result = db.execute(query, {"userid": userid})
    return [dict(row._mapping) for row in result]

def get_formatted_tags_json(db: Session, user_id: str):
    tags = get_tags_from_db(db, user_id)
    
    filtered_tags = [
        t for t in tags 
        if t.get("is_active") and t.get("is_send_ai")
    ]
    
    filtered_tags.sort(key=lambda x: (x.get("display_order") or 0))
    
    result_list = [
        {
            "name": t.get("name"),
            "tag_name": t.get("tag_name"),
            "aliases": t.get("aliases") or [],
            "description": t.get("description"),
        }
        for t in filtered_tags[:TAG_COUNT_LIMIT]
    ]
    
    return json.dumps(
        {"request_taglist": result_list},
        ensure_ascii=False,
        indent=2
    )