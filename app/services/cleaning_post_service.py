from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session
import json
import os
import time
import logging
import google.generativeai as genai
from sqlalchemy import text

from app.services.db_service import get_datefromto_posts, get_postids_posts
from app.services.prompt_tamplate_service import get_prompt_template_from_db
from app.services.tags_service import get_formatted_tags_json
from app.database_turso import get_db_turso


class TargetPeriod(BaseModel):
    start_date: date
    end_date: date

# 定数定義
CHUNK_SIZE = 5
WAIT_TIME_MS = 2000  # 2 seconds
MAX_RETRIES = 3

def call_gemini_api(db: Session, posts, user_id: str, prompt_template, tags_json):
    """
    Gemini APIを呼び出して投稿のクリーニングを行う。
    バッチログ、実行ログ、修正履歴をDBに保存する。
    """
    # API Key設定
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        logging.error("GOOGLE_GEMINI_API_KEY is not set.")
        return {"status": "error", "message": "API Key missing"}
    
    genai.configure(api_key=api_key)
    
    # モデル設定
    model_config = prompt_template.get("model_config", {})
    # Next.js (TypeScript) の実装に合わせ、モデル名を指定します。
    # `genai.GenerativeModel()` のようにモデル名を指定しないとエラーになります。
    model_name = "gemini-flash-latest"
    generation_config = {
        "temperature": model_config.get("temperature", 0.7),
        # APIからのレスポンスをJSON形式で受け取るように指定
        "response_mime_type": "application/json"
    }
    model = genai.GenerativeModel(model_name, generation_config=generation_config)
    
    total_posts = len(posts)
    total_chunks = (total_posts + CHUNK_SIZE - 1) // CHUNK_SIZE
    
    # Turso DB接続
    turso_gen = get_db_turso()
    print ("Connecting to Turso DB...")
    turso_db = next(turso_gen)
    print ("Connecting to Turso DB Finished.")

    # 1. バッチ作成 (DB)
    batch_id = _create_ai_batch(turso_db, user_id, total_chunks, total_posts)
    print ("Logging start")
    logging.info(f"Batch created: {batch_id}")
    print ("Logging End")
    
    all_results = []
    combined_raw_text = ""
    
    # 2. チャンク処理
    for i in range(0, total_posts, CHUNK_SIZE):
        chunk_index = (i // CHUNK_SIZE) + 1
        chunk_posts = posts[i : i + CHUNK_SIZE]
        
        # Wait
        if i > 0:
            time.sleep(WAIT_TIME_MS / 1000.0)
            
        # プロンプト作成
        prompt_text = build_prompt_text(db, chunk_posts, user_id, prompt_template, tags_json)
        
        # ログ用に入力JSONを再構築
        request_memo = [{
            "id": p.get("id"),
            "tags": p.get("tags"),
            "title": p.get("title"),
            "text": p.get("content")
        } for p in chunk_posts]
        request_json = json.dumps({"request_memo": request_memo}, ensure_ascii=False, indent=2)
        
        # API呼び出し (Retry)
        start_time = time.time()
        response_text = ""
        status = "failed"
        token_usage = {}
        
        for attempt in range(MAX_RETRIES):
            try:
                response = model.generate_content(prompt_text)
                # `response.text` は、ご提示のTypeScriptコードにおける `data.candidates[0].content.parts[0].text` と同じ内容を取得するための、
                # Pythonライブラリの便利なショートカットです。ライブラリがレスポンスのパースを代行してくれています。
                # より詳細な情報（他の候補など）にアクセスしたい場合は `response.candidates` を直接参照することも可能です。
                response_text = response.text
                if hasattr(response, "usage_metadata"):
                    token_usage = {
                        "prompt_token_count": response.usage_metadata.prompt_token_count,
                        "candidates_token_count": response.usage_metadata.candidates_token_count,
                        "total_token_count": response.usage_metadata.total_token_count
                    }
                status = "success"
                break
            except Exception as e:
                logging.warning(f"Gemini API attempt {attempt+1} failed: {e}")
                # 認証エラー(403)やAPIキー関連のエラーはリトライしても解決しないため即時中断してエラーを通知する
                if "403" in str(e) or "API key" in str(e):
                    raise e
                time.sleep(5)
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 3. 実行ログ作成
        print ("# 3. 実行ログ作成")
        execution_log_id = _create_execution_log(
            turso_db, batch_id, user_id, chunk_index, prompt_template.get("content", ""),
            request_json, response_text, model_name, duration_ms, status,
            tags_json, json.dumps(token_usage)
        )
        
        combined_raw_text += response_text + "\n"
        
        if status == "success":
            try:
                # JSONパース (Markdownブロック除去)
                print ("# JSONパース (Markdownブロック除去")
                clean_json = response_text.replace("```json", "").replace("```", "").strip()
                parsed_data = json.loads(clean_json)
                
                refinement_results = parsed_data.get("refinement_results", [])
                print(f"# refinement_results len: {len(refinement_results)}")
                
                # 4. 履歴保存
                print ("# 4. 履歴保存　ログ出力")
                _create_refinement_histories(
                    turso_db, batch_id, execution_log_id, chunk_posts, refinement_results
                )
                
                all_results.extend(refinement_results)
                
                # 進捗更新
                _update_batch_progress(turso_db, batch_id, chunk_index)
                
            except Exception as e:
                print(f"# Error in chunk processing: {e}")
                logging.error(f"Failed to parse response or save history: {e}")
        else:
            _fail_batch(turso_db, batch_id)
            raise Exception(f"Failed to process chunk {chunk_index}")

    # 5. 全完了
    print ("# 5. 全完了　ログ出力")

    _complete_batch(turso_db, batch_id)
    
    # Turso DB切断
    try:
        next(turso_gen)
    except StopIteration:
        pass
    
    return {
        "status": "COMPLETED",
        "batch_id": batch_id,
        "raw_text": combined_raw_text,
        "results": all_results
    }

def fetch_posts_from_db(db: Session, user_id: str, date_start: date, date_end: date, target_post_ids: List[int]):
    if target_post_ids:
        return get_postids_posts(db, user_id, target_post_ids)
    else:
        return get_datefromto_posts(db, user_id, date_start, date_end)

def build_prompt_text(db: Session, posts, user_id: str = None, prompt_template=None, tags_json=None):
    # ここでpostsの内容をもとにプロンプトテキストを構築するロジックを実装
    # is_force_reprocessがTrueの場合は、プロンプトに特定の指示を追加するなどの処理も可能

    # user_idが指定されていない場合、postsから取得を試みる
    if user_id is None and posts and "user_id" in posts[0]:
        user_id = posts[0]["user_id"]

    prompt = prompt_template["content"]

    # promptの内容をもとに、tags_jsonの内容をプロンプトテキストに組み込む処理を実装
    prompt = prompt.replace('{{tags}}', tags_json)
    # print(f"prompt_template: {prompt}")
    # promptの内容をもとに、postsの内容をプロンプトテキストに組み込む処理を実装
    memo_list = []
    for post in posts:
        memo_list.append({
            "id": post.get("id"),
            "title": post.get("title"),
            "text": post.get("content"),
            "tags": post.get("tags")
        })

    post_content = json.dumps({"request_memo": memo_list}, ensure_ascii=False, indent=2)

    prompt = prompt.replace('{{memo}}', post_content)
    
    # print(f"prompt: {prompt}")

    return prompt

def filter_posts_with_state_detail(posts, is_force_reprocess):
    # print("is_force_reprocess:", is_force_reprocess)
    if is_force_reprocess:
        return posts
    # print("posts before filtering:", posts)

    # state_detailが特定の値、または存在しない/NULLの場合に対象とする
    allowed_states = ["initial", "processed"]  # 例: これらの状態の投稿も処理対象にする
    # todo readme state_detailの値の定義と意味を明確にすること。例えば、"initial"は未処理、"processed"は一度処理済みだが再処理可能、"skipped"は処理対象外など。 

    filtered = [
        post for post in posts if not post.get("state_detail") or post.get("state_detail") in allowed_states
    ]
    return filtered

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


def get_posts_filter_by_targetcondition(posts,target_condition:str):
    if(target_condition == "all"):
        return posts
    return []

# --- DB Helper Functions ---

def _create_ai_batch(turso_db, user_id, total_chunks, total_posts):
    sql = """
        INSERT INTO ai_batches (user_id, total_chunks, total_memos, status, created_at)
        VALUES (:user_id, :total_chunks, :total_posts, 'processing', CURRENT_TIMESTAMP)
    """
    try:
        rs = turso_db.execute(sql, {"user_id": user_id, "total_chunks": total_chunks, "total_posts": total_posts})
        return rs.last_insert_rowid
    except KeyError as e:
        logging.error(
            "A KeyError occurred during a database operation. This may be due to an underlying "
            "database error (such as a missing 'ai_batches' table) that is not being "
            "surfaced correctly by the current version of the database client library. "
            "Please ensure your database schema is up to date and the table 'ai_batches' exists."
        )
        # Re-raising the original exception to not hide the stack trace
        raise e
    except Exception as e:
        logging.error(f"An unexpected error occurred in _create_ai_batch: {e}")
        raise e

def _create_execution_log(turso_db, batch_id, user_id, chunk_index, prompt_template, raw_input, raw_output, model, duration, status, tags_snapshot, token_usage):
    sql = """
        INSERT INTO ai_execution_logs (
            batch_id, user_id, chunk_index, prompt_template, raw_input_json, 
            raw_output_text, model_info, duration_ms, status, 
            used_tags_snapshot, token_usage, created_at
        ) VALUES (
            :batch_id, :user_id, :chunk_index, :prompt_template, :raw_input,
            :raw_output, :model, :duration, :status,
            :tags_snapshot, :token_usage, CURRENT_TIMESTAMP
        )
    """
    rs = turso_db.execute(sql, {
        "batch_id": batch_id, "user_id": user_id, "chunk_index": chunk_index,
        "prompt_template": prompt_template, "raw_input": raw_input,
        "raw_output": raw_output, "model": model, "duration": duration,
        "status": status, "tags_snapshot": tags_snapshot, "token_usage": token_usage
    })
    return rs.last_insert_rowid

def _create_refinement_histories(turso_db, batch_id, execution_log_id, chunk_posts, results):
    print(f"# _create_refinement_histories start. results count: {len(results)}")
    sql = """
        INSERT INTO ai_refinement_history (
            post_id, batch_id, execution_log_id, order_index,
            before_title, before_text, before_tags,
            after_title, after_text, after_tags,
            changes_summary, is_edited, applied, created_at
        ) VALUES (
            :post_id, :batch_id, :execution_log_id, :order_index,
            :before_title, :before_text, :before_tags,
            :after_title, :after_text, :after_tags,
            :changes_summary, :is_edited, :applied, CURRENT_TIMESTAMP
        )
    """
    for idx, res in enumerate(results):
        post_id = res.get("id")
        print(f"# Processing history item {idx}, post_id: {post_id}")
        original = next((p for p in chunk_posts if p["id"] == post_id), None)
        
        if original:
            print(f"# Original found. Inserting history for post_id: {post_id}")
            try:
                turso_db.execute(sql, {
                    "post_id": post_id,
                    "batch_id": batch_id,
                    "execution_log_id": execution_log_id,
                    "order_index": idx,
                    "before_title": original.get("title"),
                    "before_text": original.get("content"),
                    "before_tags": json.dumps(original.get("tags"), ensure_ascii=False),
                    "after_title": res.get("fixed_title"),
                    "after_text": res.get("fixed_text"),
                    "after_tags": json.dumps(res.get("fixed_tags"), ensure_ascii=False),
                    "changes_summary": json.dumps(res.get("changes"), ensure_ascii=False),
                    "is_edited": False,
                    "applied": False
                })
                print(f"# Insert success for post_id: {post_id}")
            except Exception as e:
                print(f"# Error inserting history for post_id {post_id}: {e}")
                raise e
        else:
            print(f"# Original post NOT found for post_id: {post_id}")

def _update_batch_progress(turso_db, batch_id, completed_chunks):
    sql = "UPDATE ai_batches SET completed_chunks = :c WHERE id = :id"
    turso_db.execute(sql, {"c": completed_chunks, "id": batch_id})

def _complete_batch(turso_db, batch_id):
    sql = "UPDATE ai_batches SET status = 'completed' WHERE id = :id"
    turso_db.execute(sql, {"id": batch_id})

def _fail_batch(turso_db, batch_id):
    sql = "UPDATE ai_batches SET status = 'failed' WHERE id = :id"
    turso_db.execute(sql, {"id": batch_id})
