# APIType
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
| **C: スクリプト作成のみ** | `is_dry_run_only` | `bool` | `True`ならAIに投げずPromptを返す |
| **D: ログ詳細度** | `log_level_type` | `str` | `normal`, `detail`, `none` |
| **E: バッチログ登録** | `is_enable_batch_log` | `bool` | `ai_batches` への登録有無 |
| **F: ポスト毎結果登録** | `is_enable_post_refinement` | `bool` | `zstu_post_refinements` への登録 |

**バリデーション・連動ロジック:**

* `if is_dry_run_only:` → `log_level_type = 'none'`, `is_enable_batch_log = False`, `is_enable_post_refinement = False`
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


## 関連するテーブル`zstu_tag_descriptions`

- prompt作成時に、ローカルのTag情報として作成する。

| カラム名 | 型 | 制約 | 説明 |
| --- | --- | --- | --- |
| `id` | UUID | PK | タグの一意識別子 |
| `user_id` | UUID / Int | FK | どのユーザーのタグかを識別 |
| `tag_name` | String(50) | Not Null | AIへの指示に使う短い識別子 (例: `zstv2`) |
| `name` | String(100) | Not Null | 画面表示用の正式名称 (例: `zerosecthinkv2`) |
| `aliases` | JSONB |  | 同義語リスト（重複回避用）(例：["パイソン", "Py", "python3"]) |
| `description` | Text | - | タグの意味やAIへの補足説明  |
| **`display_order`** | Int | Default: 0 | 画面上での表示順（昇順・降順でソート用） |
| **`is_active`** | Boolean | Default: true | 有効/無効フラグ。削除せずに非表示にしたい場合に使用 |
| **`is_send_ai`** | Boolean | Default: true | **AIへの送信対象にするか。** (※) |
| **`created_at`** | Timestamp | Not Null | レコード作成日時 |
| **`updated_at`** | Timestamp | Not Null | レコード更新日時 |

---

### 各項目の検討理由と詳細

#### 1. `is_active` (論理削除・有効化)

* **必要性：** 非常に高いです。
* **理由：** 過去のメモに関連付けられているタグを物理削除してしまうと、過去ログの整合性が崩れる可能性があります。「今は使わないけれどデータとして残しておきたい」場合に、`false` にすることで管理画面や選択肢から除外できます。

#### 2. `is_send_ai` (AI送信フラグ) ※「is_sendai」の解釈

* **必要性：** 高いです。
* **理由：** おそらく `is_send_ai`（AIに送るかどうか）の意図かと推察します。タグが増えてくると、全てのタグをプロンプト（`{tags}`）に含めるとトークン数（コスト）を消費しすぎたり、AIが混乱したりします。「このタグはAIに文脈を理解させるために必須」というものにチェックを入れて制御できると便利です。

#### 3. `display_order` (表示順)

* **必要性：** 高いです。
* **理由：** 作成順（`created_at`）だけでなく、よく使うタグを上に固定（ピン留め）したり、ユーザーが任意に並び替えたりできると、タグ管理画面の使い勝手が劇的に向上します。

#### 4. `created_at` / `updated_at` (タイムスタンプ)

* **必要性：** 必須レベルです。
* **理由：** データのデバッグ時や、「最近作ったタグから表示する」といった並び替え、またAIの処理履歴との突合に必ず必要になります。


## 関連するテーブル`ai_Batches`




「1週間分のメモを修正する」という、ユーザーの1回の操作（リクエスト）を管理する親テーブルです。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | Int | バッチ全体の一意識別子 |
| `user_id` | UUID | 実行ユーザー |
| `total_chunks` | Int | 全体の分割数（例：4チャンク） |
| `completed_chunks` | Int | 完了した数（進捗管理用） |
| `total_memos` | Int | 処理対象の総メモ件数（例：70件） |
| `status` | String | `processing`, `completed`, `partial_success`, `failed` |
| `created_at` | Timestamp | 開始日時 |

SQLiteを想定なので、UUID、JSONB -> TEXT型、Boolean -> Integer(0,1)

## 関連するテーブル`ai_Execution_Logs`


| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | Int | ログの一意識別子 |
| `user_id` | UUID | 実行したユーザー |
|`batch_id` |int|`ai_Batches` へのリレーション|
|`chunk_index` |int|「4チャンク中、何番目のリクエストか」を記録します。|
| `prompt_template` | Text | 使用した `typo_content` のスナップショット |
| `raw_input_json` | JSONB | AIに送った実際のJSONデータ |
| `raw_output_text` | Text | AIから返ってきた生のレスポンス |
| `model_info` | String | 使用モデル (Gemini 1.5 Flash等) |
| **`api_version`** | String | `v1` や `v1beta` など。API側の仕様変更の追跡用 |
| **`duration_ms`** | Int | 実行にかかった時間（ミリ秒）。パフォーマンス監視用 |
| `status` | String | `success`, `failed`, `retry` など |
| `used_tags_snapshot` | JSONB | 当時送ったタグ定義（名前・説明）の記録 |
| `error_payload` | JSONB |  APIがエラーを返した際、その詳細をそのまま保存します |
| `token_usage` | JSONB | Geminiから返ってくる `prompt_token_count` と `candidates_token_count` を保存。 |
| `created_at` | Timestamp | 実行日時 |


---

### 1. `api_version` の重要性

Google AI Studio (Gemini API) は、`v1beta` でのみ先行実装される機能（構造化出力の厳密な定義など）が多いです。
「以前は動いていたのに急にJSONパースに失敗するようになった」という時、**「APIのバージョンが原因か、モデルの更新が原因か」**を切り分ける重要な手がかりになります。

### 2. `duration_ms` (実行時間) の重要性

提示いただいたコードでは `CHUNK_SIZE` ごとに分割送信し、さらに `WAIT_TIME_MS` (10秒) の待機を入れています。
* ログを見ることで「実際にAIの推論に何秒かかったのか」と「待機時間を含めた全体のUXとしてどうなのか」を数値化できます。
* あまりに時間がかかるチャンクがある場合、プロンプトが長すぎる、あるいはタグの `description` が多すぎるといったボトルネックを発見できます。



## A. 個別ポスト精査テーブル (`zstu_post_refinements`)

1つの投稿に対するAIの整形・精査結果を管理します。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` |Integer | プライマリキーメール用のトークンは別に管理します |
| `post_id` | Integer | `zstu_posts.id` (FK) |
| `user_id` | UUID | ユーザーID |
| `status` | String | ご提示の `unprocessed` 〜 `completed` |
| `request_title` | Text | 要求時のコンテンツ |
| `request_content` | Text | 要求時のコンテンツ |
| `request_tags` | jsonb | 要求時のコンテンツ |
| `ai_refined_title` | Text | AIからの返答内容 |
| `ai_refined_content` | Text | AIからの返答内容 |
| `ai_refined_tags` | jsonb | AIからの返答内容 |
| `ai_changes` | jsonb | AIからの変更点の指摘 |
| `is_fixed` | boolean | AIからの返答から調整して、登録したかどうか |
| `fixed_title` | Text | 最終的に登録された内容 |
| `fixed_content` | Text | 最終的に登録された内容 |
| `fixed_tags` | jsonb | 最終的に登録された内容 |
| `trace_id` | UUID | 一括処理時のバッチ識別子 |
| `created_at` | Timestamp | 実行日時 |
| `updated_at` | Timestamp | 更新日時 |


---

is_edited,applied,状態の意味
false,true,AIの提案をそのまま採用した。
true,true,AIの提案を人間が手直しして採用した。
false,false,AIが提案したが、採用を見送った（破棄）。
true,false,（レアケース）手直しはしたが、結局採用しなかった。


## 関連するテーブル`prompt_templates`

- 複数のシステムから利用される情報（VercelNextJSやFastAPI）なので、テーブルに情報として持つ


プロンプトの「枠組み（名前や用途）」を定義します。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | `integer` | 主キー (PK) |
| `slug` | `text` | プロンプト識別子（例: `typo_propmt`）※一意制約 |
| `name` | `text` | 管理用の表示名（例: カスタマーサポート返信） |
| `description` | `text` | このプロンプトの用途説明 |
| `created_at` | `timestamptz` | 作成日時 |


## 関連するテーブル`prompt_versions`


プロンプトの「中身（バージョン）」を保持します。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | `integer` | 主キー (PK) |
| `template_id` | `integer` | `prompt_templates.id` への外部キー |
| `version` | `integer` | バージョン番号 (1, 2, 3...) |
| `content` | `text` | **プロンプト本文**（変数は `{{memo}}` `{{tags}}` 等で保持） |
| `comment` | `text` | コメント |
| `model_config` | `jsonb` | モデル設定（`model: "gpt-4o"`, `temperature: 0.7` など） |
| `is_active` | `boolean` | **現在使用中のバージョンか**（Trueは1つのみ） |
| `created_by` | `uuid` | 作成者のユーザーID（Supabase Authと連携） |
| `created_at` | `timestamptz` | 作成日時 |

---

API_Logs（共通アクセスログ）Task_Progress_Logs（目的別・処理進捗ログ）への登録は別途検討

