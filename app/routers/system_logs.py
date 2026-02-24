from fastapi import APIRouter, Query, HTTPException, Depends
from datetime import date
from typing import List, Dict, Any
import logging

from libsql_client import Client
# Turso用のDBセッション取得関数をインポート
# ※ファイルの場所に合わせて import パスを調整してください
from app.database_turso import get_db_turso # 直接インポート

# ルーターの設定
router = APIRouter(
    prefix="/system-logs",
    tags=["System Logs"]
)

@router.get("/turso-db-test")
def test_turso_db_connection(db: Client = Depends(get_db_turso)):
    """
    Turso DBに接続し、テーブル一覧を取得して接続を確認します。
    このエンドポイントにアクセスして、'api_logs'と'task_progress_logs'テーブルが存在するか確認してください。
    """
    try:
        # SQLiteでテーブル一覧を取得するクエリ
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        result = db.execute(query)
        tables = [row[0] for row in result]
        
        return {
            "status": "success",
            "message": "Turso DBへの接続に成功しました。",
            "tables": tables
        }
    except Exception as e:
        # エラーが発生した場合は、詳細を返す
        raise HTTPException(status_code=500, detail=f"Turso DBへの接続中にエラーが発生しました: {str(e)}")
    
@router.get("/traces")
async def get_system_traces(
    start_date: date,
    end_date: date,
    limit: int = 100,
    db = Depends(get_db_turso) # 通常はFastAPIが注入
):
    # --- 内部呼び出しの対応 ---
    is_internal = False
    if db is None:
        # get_db_turso() はジェネレータなので next() で client を取得
        db_gen = get_db_turso()
        db = next(db_gen)
        is_internal = True

    try:
        query = """
        SELECT 
            api.created_at AS api_created_at, 
            api.method, 
            api.endpoint, 
            api.request_header,
            api.request_body,
            api.ip_address,
            task.created_at AS task_created_at,
            task.execution_order,
            task.task_name,
            task.step_name, 
            task.status, 
            task.input_data
        FROM api_logs api
        INNER JOIN task_progress_logs task ON api.trace_id = task.trace_id
        WHERE api.created_at BETWEEN :start AND :end
        ORDER BY api.created_at DESC, task.created_at DESC
        LIMIT :limit;
        """
        
        params = {
            "start": f"{start_date} 00:00:00",
            "end": f"{end_date} 23:59:59",
            "limit": limit
        }

        # libsql_client (sync) の実行
        result = db.execute(query, params)
        
        # 辞書形式に変換
        rows = [dict(zip(result.columns, row)) for row in result]
        
        return {
            "status": "success",
            "data": rows
        }

    except Exception as e:
        logging.error(f"Log retrieval error: {e}")
        raise HTTPException(status_code=500, detail="ログの取得に失敗しました")
    
    finally:
        # 内部で作成した場合のみ、確実にクローズする
        if is_internal:
            db.close()