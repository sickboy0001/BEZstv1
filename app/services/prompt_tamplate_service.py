from sqlalchemy.orm import Session
from sqlalchemy import text
import json

# デフォルト値の定義
default_typo_prompt = "以下の投稿をクリーニングしてください。"
default_week_summary_prompt = "以下の内容を週次で要約してください。"

def get_prompt_template_from_db(db: Session, slug: str):
    """
    slugに対応するアクティブなプロンプトを取得する。
    DBにない場合はデフォルト値を返す。
    """
    query = text("""
        SELECT 
          pv.version,
          pv.content,
          pv.model_config
        FROM prompt_templates pt
        JOIN prompt_versions pv ON pt.id = pv.template_id
        WHERE pt.slug = :slug 
          AND pv.is_active = true
        LIMIT 1
    """)
    # print(f"Executing query to fetch prompt template with slug: {slug}")
    try:
        result = db.execute(query, {"slug": slug})
        row = result.mappings().first()
        
        if row:
            data = dict(row)
            # model_configがJSON文字列の場合は辞書に変換
            if isinstance(data.get("model_config"), str):
                try:
                    data["model_config"] = json.loads(data["model_config"])
                except:
                    pass
            return data
    except Exception as e:
        print(f"Error fetching prompt template: {e}")

    # DBにない場合は定数からデフォルト値を取得
    fallback_content = ""
    if slug == "typo_prompt":
        fallback_content = default_typo_prompt
    elif slug == "week_summary_prompt":
        fallback_content = default_week_summary_prompt

    if fallback_content:
        return {
            "version": 0,
            "content": fallback_content,
            "model_config": {"model": "gemini-1.5-flash", "temperature": 0.7},
        }

    return None