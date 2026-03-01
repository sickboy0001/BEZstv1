# 不要　**[以下](../../../README.MD)に統合済み**

# APITypo
## 目的

条件に従って、登録されたPostを読み取り、それをGoogleAIStudioに投げて、
その結果を参照できるようにする。
登録も可能にする。
Post自体の更新は、別途メールで案内したページで確認するようにする


## 手順
### step 1 ログインする（既存機能）
### Step 2: UI/API 条件指定 (Input Parameters)

UIから渡される、またはAPI引数として定義する変数名です。

| 項目 | 変数名 (Python形式) | 型 | デフォルト / 備考 |
| --- | --- | --- | --- |
| **A: ユーザーID** | `user_id` | `uuid` | ログインセッションから取得 |
| **B-1: 期間指定** | `date_start`, `date_end` | `date` | 対象期間（22日〜28日など） |
| **B-2: ポスト個別指定** | `target_post_ids` | `list[int]` | 空リストなら全件対象/ポスト検索時はRead:zstu_posts |
| **B-3: 再問い合わせ** | `is_force_reprocess` | `bool` | `True`なら`refined`済みも対象 |
| **C: 実行モード** | `action_mode` | `str` | `mode_script` , `mode_ai` , `mode_result` |
| **D: ログ詳細度** | `log_level_type` | `str` | `normal`, `detail`, `none` |
| **E: バッチログ登録** | `is_enable_batch_log` | `bool` | `ai_batches` への登録有無 |
| **F: ポスト毎結果登録** | `is_enable_post_refinement` | `bool` | `zstu_post_refinements` への登録 |

**バリデーション・連動ロジック:**

* mode_script スクリプトの作成まで
* mode_ai　aiの問い合わせまで
* mode_result 結果の登録まで
* `if not is_enable_batch_log:` → `is_enable_post_refinement = False`

- Z:「開始」ボタン
  - 参照情報として、対象のプロンプトを確認できること

**バリデーション・連動ロジック:**

* `if is_dry_run_only:` → `log_level_type = 'none'`, `is_enable_batch_log = False`, `is_enable_post_refinement = False`
* `if not is_enable_batch_log:` → `is_enable_post_refinement = False`


### Step 3: 対象ポスト取得 (Fetch Posts)

1. **検索実行**: `date_start` 〜 `date_end` の範囲で `zstu_posts` を検索。
2. **フィルタリング**:
* `target_post_ids` が指定されていれば、そのIDで絞り込み。
* `is_force_reprocess == False` の場合、`state_detail -> ai_refinement -> status` が `unprocessed` または `pending_requeue` のもののみを抽出。
* 変数 `target_posts` (List[Dict]) に格納。

### Step 4: プロンプト構築 (Build Prompt)

1. **マスタ取得**: `prompt_versions` から `is_active=True` のテンプレートを取得。
2. **タグ情報取得**: `zstu_tag_descriptions` から `is_send_ai=True` のタグを取得し、コンテキスト用文字列 `tag_context` を作成。
3. **プロンプト生成**: テンプレート内の変数（`{{posts}}`, `{{tags}}` 等）を `target_posts` と `tag_context` で置換。
* 変数名: `final_prompt_text`

1. **早期リターン**: `is_dry_run_only == True` の場合、ここで `final_prompt_text` をレスポンスとして終了。


### Step 5 : AI問い合わせ (Execution & Logging)

1. **バッチ開始記録**: `is_enable_batch_log == True` なら `ai_batches` にレコード作成。
* 戻り値: `current_batch_id`


2. **AIリクエスト**: Google AI Studioへ `final_prompt_text` を送信。
3. **実行ログ記録**: `ai_execution_logs` に `prompt_template`, `raw_input_json`, `model_info` 等を保存。
4. **個別結果保存**: `is_enable_post_refinement == True` なら、AIの返答をパースし、各ポストに対して `zstu_post_refinements` に `INSERT`。


### Step 6: AI結果受領 (Execution & Logging)

- 「Step5」の結果受領記録 (Execution & Logging)

1. **実行ログ記録**: `ai_execution_logs` に `prompt_template`, `raw_input_json`, `model_info` 等を保存。
2. **個別結果保存**: `is_enable_post_refinement == True` なら、AIの返答をパースし、各ポストに対して `zstu_post_refinements` に `INSERT`。
* 同時に `zstu_posts.state_detail` の `status` を `refined` に `UPDATE`。


### step 7 結果の送信
- 「F」がONの場合は、その結果をメールで送信（ひとまずはログで）
  - insert:api_logs
  - insert:task_progress_logs
### Step 8 結果の確認
- 「Step 7」を承認するなどの微調整して登録
  - 「F」がOFF対象のPostなし。
  - update:zstu_posts.ai_refinement


---

### 補足：Python実装時のヒント

ご提示の「詳細なログを残すかどうか（条件D）」については、以下のように実装するとスッキリします。

```python
# 条件Dのハンドリング例
if log_level_type == "detail":
    log_payload = {
        "input": raw_input_json,
        "output": raw_output_text,
        "tokens": token_usage
    }
elif log_level_type == "normal":
    log_payload = {"tokens": token_usage} # 入出力は残さない
else:
    log_payload = {}

```



## 関連するテーブル `zstu_posts` 



| カラム物理名 | 論理名 | データ型 | 必須 | デフォルト / 制約 | 備考 |
| --- | --- | --- | --- | --- | --- |
| **id** | 投稿ID | `serial` | ◯ | PRIMARY KEY | 自動採番 |
| **user_id** | ユーザーID | **`uuid`** | ◯ |  | 投稿者の識別子 (auth.users.id) |
| **current_at** | 基準日時 | `timestamp` | - | `CURRENT_TIMESTAMP` | 投稿の対象日・時刻 |
| **title** | タイトル | `text` | ◯ |  |  |
| **content** | 本文 | `text` | ◯ |  |  |
| **tags** | タグリスト | **`text[]`** | ◯ | **`'{}'`** | タグの配列。検索用GINインデックス推奨 |
| **source_type** | 連携元種別 | `varchar` | - |  | `observation`, `hadbit` 等 |
| **source_key** | 連携元キー | **`text`** | - | **UNIQUE (type, key)** | 連携元のID (Int/UUID等を保持) |
| **source_detail** | 連携元詳細 | **`jsonb`** | - |  | 連携元特有の情報 (距離、単位、銘柄等) |
| **second** | 所要秒数 | `integer` | ◯ | `0` | 執筆や実施にかかった秒数 |
| **public_flg** | 公開フラグ | `boolean` | ◯ | `true` | 全体公開設定 |
| **public_content_flg** | 内容公開フラグ | `boolean` | ◯ | `true` | コンテンツ部分の公開設定 |
| **delete_flg** | 削除フラグ | `boolean` | ◯ | `false` | 論理削除フラグ |
| **write_start_at** | 執筆開始日時 | `timestamp` | - | `CURRENT_TIMESTAMP` |  |
| **write_end_at** | 執筆終了日時 | `timestamp` | - | `CURRENT_TIMESTAMP` |  |
| **created_at** | 作成日時 | `timestamp` | ◯ | `CURRENT_TIMESTAMP` | レコード作成日 |
| **updated_at** | 更新日時 | `timestamp` | ◯ | `CURRENT_TIMESTAMP` | レコード更新日 |
| **state_detail** | 状態の詳細 | **`jsonb`** | - |  | AI連携の詳細 |

### zstu_posts:state_details

AIへの要求などの最終的な状態

|日本語の状態|推奨する英語定数 (Status)|説明・補足|
|:----|:----|:----|
|なし|unprocessed|まだ何もしていない初期状態。|
|再要求|pending_requeue|ユーザーが「やり直し」を求めた状態。次回のバッチ対象。|
|要求中|processing|AIにリクエストを投げた直後、または実行中。|
|受領済み|refined|AIの回答が届き、ユーザーの確認を待っている状態。|
|登録済み（更新あり）|completed_with_edit|AIの結果を元にユーザーが修正して確定させた。|
|登録済み|completed|AIの結果をそのまま確定させた。|

```
{
  "ai_refinement": {
    "status": "refined",
    "is_fixed": false,
    "last_refinement_id": 1234,
    "updated_at": "2026-02-26T14:00:00Z"
  }
}
```
---

