
from libsql_client import Client, ResultSet

def get_ailogposts_id_from_db(turso_db: Client,id: int,  limit: int = 200):
    """
    zst_post テーブルから最新の投稿を取得する
    """
    if not id:
        return []

    query = """
      SELECT 
          refi.id,
          refi.post_id,
          refi.batch_id,
          refi.order_index,
          refi.before_title,
          refi.before_text,
          refi.before_tags,
          refi.after_title,
          refi.after_text,
          refi.after_tags,
          refi.changes_summary,
          refi.fixed_title,
          refi.fixed_text,
          refi.fixed_tags
        FROM ai_batches batches
        inner join ai_refinement_history refi
        on refi.batch_id = batches.id
      where batches.id = :id
      order by refi.created_at desc
      LIMIT :limit
    """
    result: ResultSet = turso_db.execute(query, {
        "id": id,
        "limit": limit
    })

    print("get_ailogposts_id_from_db result:", result,id)
    
    # ResultSetは一度しかイテレートできないため、先にリストに変換して中身を確認します。
    rows = list(result)
    print(f"Found {len(rows)} rows for batch_id {id}")

    # 結果が0件の場合は、ここで空のリストを返します
    if not rows:
        return []

    # カラム名と行データを組み合わせて辞書のリストを作成します
    return [dict(zip(result.columns, row)) for row in rows]

def get_ailogexecutions_id_from_db(turso_db: Client,id: int,  limit: int = 200):
    """
    """
    if not id:
        return []

    query = """
      select 
        id , 
        raw_input_json ,
        raw_output_text,
        model_info,
        api_version , 
        duration_ms ,
        status, 
        used_tags_snapshot,
        error_payload,
        token_usage,
        created_at
        
        
      from ai_execution_logs 
      where id = :id LIMIT :limit;
    """
    result: ResultSet = turso_db.execute(query, {
        "id": id,
        "limit": limit
    })

    # print("get_ailogexecutions_id_from_db result:", result,id)
    
    # ResultSetは一度しかイテレートできないため、先にリストに変換して中身を確認します。
    rows = list(result)
    # print(f"Found {len(rows)} rows for batch_id {id}")

    # 結果が0件の場合は、ここで空のリストを返します
    if not rows:
        return []

    # カラム名と行データを組み合わせて辞書のリストを作成します
    return [dict(zip(result.columns, row)) for row in rows]

def get_ailoghdlist_userid_from_db(turso_db: Client,userid: str,  limit: int = 200):
    """
    zst_post テーブルから最新の投稿を取得する
    """
    if not id:
        return []

    query = """
      SELECT 
        id,
        created_at,
        total_chunks,
        completed_chunks,
        total_memos ,
        status   
        FROM ai_batches
      where user_id = :user_id
      --   and ai_batches.id = 41
      order by created_at desc
      LIMIT :limit
    """
    result: ResultSet = turso_db.execute(query, {
        "user_id": userid,
        "limit": limit
    })

    
    # ResultSetは一度しかイテレートできないため、先にリストに変換して中身を確認します。
    rows = list(result)
    print(f"Found {len(rows)} rows for user_id {userid}")

    # 結果が0件の場合は、ここで空のリストを返します
    if not rows:
        return []

    # カラム名と行データを組み合わせて辞書のリストを作成します
    return [dict(zip(result.columns, row)) for row in rows]

def get_ailogexecution_detail_id_from_db(turso_db: Client, id: int):
    """
    """
    if not id:
        return None

    query = """
      select 
        id , 
        raw_input_json ,
        raw_output_text,
        model_info,
        api_version , 
        duration_ms ,
        status, 
        used_tags_snapshot,
        error_payload,
        token_usage,
        created_at
      from ai_execution_logs 
      where id = :id
      and limit 1;
    """
    result: ResultSet = turso_db.execute(query, {
        "id": id
    })

    
    # ResultSetは一度しかイテレートできないため、先にリストに変換して中身を確認します。
    rows = list(result)
    print(f"Found {len(rows)} rows for execution_id {id}")

    # 結果が0件の場合は、ここで空のリストを返します
    if not rows:
        return None

    # カラム名と行データを組み合わせて辞書のリストを作成します
    return [dict(zip(result.columns, row)) for row in rows]
