- [🚀 プロジェクト概要](#-プロジェクト概要)
- [🛠 技術スタックと選定理由](#-技術スタックと選定理由)
- [📋 基本仕様](#-基本仕様)
  - [1. 開発・実行環境](#1-開発実行環境)
  - [2. フロントエンド](#2-フロントエンド)
  - [3. バックエンド \& データ層](#3-バックエンド--データ層)
  - [4. インフラ](#4-インフラ)
- [📂 ディレクトリ構成](#-ディレクトリ構成)
- [🚢 デプロイフロー](#-デプロイフロー)
- [`zstu_posts`](#zstu_posts)
  - [zstu\_posts:state\_details](#zstu_postsstate_details)
- [ログ周り](#ログ周り)
  - [A. API\_Logs（共通アクセスログ）](#a-api_logs共通アクセスログ)
  - [B. Task\_Progress\_Logs（目的別・処理進捗ログ）](#b-task_progress_logs目的別処理進捗ログ)
  - [💡 設計のポイント](#-設計のポイント)
  - [DDL](#ddl)
  - [この構成で実現できること](#この構成で実現できること)
    - [③ サービス層での利用：`app/services/item_service.py`](#-サービス層での利用appservicesitem_servicepy)
    - [④ ルーター層での利用：`app/routers/item_router.py`](#-ルーター層での利用approutersitem_routerpy)
  - [3. なぜこの構成が良いのか？](#3-なぜこの構成が良いのか)
- [ポストの分析状況](#ポストの分析状況)
  - [1. API Input（引数）](#1-api-input引数)
  - [output)](#output)
  - [2. Process（処理フローとログ・状態制御）](#2-process処理フローとログ状態制御)
  - [3. 設計の重要ポイント](#3-設計の重要ポイント)
    - [⚠️ `disp` 指定時の競合回避（安全策）](#️-disp-指定時の競合回避安全策)
    - [📊 ログの活用（※1）](#-ログの活用1)
    - [🔄 状態遷移の確定](#-状態遷移の確定)
  - [A. 個別ポスト精査テーブル (`zstu_post_refinements`)](#a-個別ポスト精査テーブル-zstu_post_refinements)
      - [3. 実装上のアドバイス：ステータス管理のコツ](#3-実装上のアドバイスステータス管理のコツ)
      - [`disp` (検証モード) の扱い](#disp-検証モード-の扱い)
      - [4. ログレベル (`loglevel`) の落とし所](#4-ログレベル-loglevel-の落とし所)
- [🚀 AI週間評価API 設計案](#-ai週間評価api-設計案)
  - [1. Input (引数)](#1-input-引数)
  - [2. Process (ロジックフロー)](#2-process-ロジックフロー)
  - [3. Output (レスポンス)](#3-output-レスポンス)
- [週次評価結果を保存するテーブル（案）](#週次評価結果を保存するテーブル案)
- [サマリをAIに問い合わせる動き](#サマリをaiに問い合わせる動き)
- [todo](#todo)
- [History](#history)


## 🚀 プロジェクト概要

**BackEndZeroSecondThink** は、Python/FastAPI と htmx を組み合わせ、SPAのような操作感を最小限の JavaScript で実現するモダンな Web アプリケーションです。Cloud Run によるオートスケーリングと、Turso による高速なエッジ・ロギングを組み合わせ、高可用かつ低遅延なシステムを目指しています。

---

## 🛠 技術スタックと選定理由

| 技術要素 | 役割・選定理由 |
| --- | --- |
| **Python / FastAPI** | サーバーサイドの主軸。非同期処理と型安全性を両立し、DIを活用した保守性の高い設計を実践。 |
| **htmx** | フロントエンドのUX向上。サーバーサイドから部分的なHTMLを返すことで、複雑なJSフレームワークなしに動的なUIを実現。 |
| **DaisyUI (Tailwind)** | UIコンポーネント。一貫したデザインと迅速なスタイリングを可能にするため採用。 |
| **Cloud Run (Docker)** | インフラ基盤。Renderから移行し、リクエストに応じた柔軟なスケーリングとデプロイの高速化を実現。 |
| **Supabase** | 認証基盤（Auth）およびメインの構造化データ（PostgreSQL）の管理。 |
| **Turso (libSQL)** | **エッジ・ロギング。** CSVLoggerを拡張し、APIアクセスログや処理進捗を低遅延でクラウド上に蓄積。 |

---

## 📋 基本仕様

### 1. 開発・実行環境

* **エディタ**: Visual Studio Code (VS Code)
* **ランタイム**: Python 3.12+ / Docker
* **ローカル環境**: `venv` による仮想環境管理
* **パッケージ管理**: pip (`requirements.txt`)

### 2. フロントエンド

* **テンプレートエンジン**: Jinja2 (サーバーサイド・レンダリング)
* **非同期通信**: htmx (HTMLの部分置換、ローディング制御)
* **デザイン**: DaisyUI / Tailwind CSS

### 3. バックエンド & データ層

* **Webフレームワーク**: FastAPI (Async対応)
* **バリデーション**: Pydantic v2
* **メインDB/認証**: Supabase 
* **ログ基盤**: Turso (HTTPベースのSQLite) ＋ ローカルCSVのハイブリッド構成

### 4. インフラ

* **デプロイ**: Google Cloud Build -> Cloud Run
* **環境変数管理**: `.env` による環境分離 (Local / Production)

---



---

## 📂 ディレクトリ構成

```
localProject/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── app/
    ├── main.py
    ├── models/          # 【Model】DBテーブル定義 (SQLAlchemy等)
    ├── schemas/         #  入出力バリデーション (Pydantic)
    ├── services/        # 【Business Logic】ここに計算やDB処理を書く
    │   └── item_service.py
    ├── lib/             #  Lib 共通部分
    │   └── utils.py     #  共通関数
    ├── routers/         # 【Controller】ルーティングとViewの制御
    │   └── item_router.py
    ├── templates/       # 【View】HTML (Jinja2)
    │   ├── base.html
    │   └── items/
    │       └── list.html
    └── static/          # 静的ファイル
        ├── css/
        └── js/
```

---

## 🚢 デプロイフロー

CloudRunを利用したCI/CDが自動化されています。

1. **GitHubへPush**: `main` ブランチへコードをプッシュ。
2. **ビルド**: Renderがリポジトリの `Dockerfile` を検知し、Dockerイメージをビルド。
3. **自動デプロイ**: ビルド成功後、Web Serviceとして自動デプロイ。
4. **環境変数管理**: Render Dashboardおよびローカルの `.env` で秘匿情報を管理。

---

Dockerでの起動方法
ターミナルを開く VS Code で Ctrl + J（または Ctrl + @）を押してターミナルを開きます。

Dockerイメージのビルド 以下のコマンドを実行して、現在のディレクトリ（.）の Dockerfile からイメージを作成します。

```bash
docker build -t testloginrendar .
```

-t testloginrendar: イメージに名前（タグ）を付けます。
コンテナの起動 ビルドが成功したら、以下のコマンドで起動します。

```bash
docker run --rm -p 8000:10000 --env-file .env --name my-test-container testloginrendar
```

--rm: 停止時にコンテナを自動削除します（検証用に便利）。
-p 8000:10000: ホストのポート 8000 をコンテナの 10000 に転送します。
--env-file .env: .env ファイルがある場合、環境変数を読み込みます（docker-compose では自動ですが、docker run では指定が必要です）。 .env については xxxURL="xxxx" はNG　xxxURL=xxxx　はOK　ダブルコーテーションは省くこと。 
検証 ブラウザで http://localhost:8000 にアクセスして動作を確認します。 停止するにはターミナルで Ctrl + C を押します。



## `zstu_posts` 


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
| **state_details** | 状態の詳細 | **`jsonb`** | - |  | AI連携の詳細 |

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



## ログ周り

### A. API_Logs（共通アクセスログ）

すべてのリクエストの「外枠」を記録します。パフォーマンス監視やエラーの早期発見に特化したテーブルです。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | BigInt | ログの一意識別子 |
| `trace_id` | UUID | 一連のリクエストを追跡する共通ID（フロントから渡すか、入口で生成） |
| `method` | String | HTTPメソッド (GET, POST, etc.) |
| `endpoint` | String | アクセスされたURLパス |
| `request_header` | JSONB | 認証情報やユーザーエージェントなど |
| `request_body` | JSONB | クライアントから送られてきたデータ |
| `response_status` | Int | HTTPステータスコード (200, 404, 500 etc.) |
| `response_body` | JSONB | 返したレスポンス内容 |
| `duration_ms` | Int | 処理にかかった時間（ミリ秒） |
| `ip_address` | String | 接続元IPアドレス |
| `user_id` | Int | 操作したユーザーのID（ログイン時のみ） |
| `created_at` | Timestamp | リクエスト受信日時 |

---

### B. Task_Progress_Logs（目的別・処理進捗ログ）

特定の重い処理や、複数のステップに分かれるタスクの「中身」を記録します。`API_Logs` と `trace_id` で紐付ける運用を想定しています。

| カラム名 | 型 | 説明 |
| --- | --- | --- |
| `id` | BigInt | 進捗ログの一意識別子 |
| `trace_id` | UUID | `API_Logs` と紐付けるための追跡ID |
| `task_name` | String | 処理の名前（例: "Image_Optimization", "Bulk_Import"） |
| `step_name` | String | 現在のステップ名（例: "Validation", "AI_Generation", "DB_Commit"） |
| `status` | String | ステップの状態 (START, IN_PROGRESS, SUCCESS, FAILED) |
| `input_data` | JSONB | そのステップに渡された引数やデータ |
| `output_data` | JSONB | そのステップの結果や返り値 |
| `error_message` | Text | 失敗時のエラー内容 |
| `stack_trace` | Text | エラー発生時のスタックトレース |
| `execution_order` | Int | 処理内の実行順序 |
| `created_at` | Timestamp | ステップ開始/記録日時 |

---

### 💡 設計のポイント

1. **Trace ID による紐付け**:
`API_Logs` で「500エラー」を見つけた際、同じ `trace_id` で `Task_Progress_Logs` を検索すれば、どのステップでコケたのかが即座に判明します。
2. **型に JSONB を採用**:
リクエスト内容やタスクごとの個別データは構造が変わりやすいため、`JSONB` 型にしておくことで、スキーマ変更なしで柔軟にログを拡張できます。
3. **BigInt の利用**:
ログテーブルはレコード数が膨大になりやすいため、IDには `Int` よりも範囲の広い `BigInt` を推奨します。

次は、これらのテーブルを使って「エラー調査」や「分析」を行うためのSQLクエリの例を作成しましょうか？あるいは、特定の言語（PythonやNode.jsなど）での実装イメージが必要でしょうか。


### DDL
Turso(SQLite)向け

```sql
-- APIアクセスログ本体
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- SQLiteではBigInt相当として機能
    trace_id TEXT NOT NULL,               -- UUIDを格納
    method TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    request_header TEXT,                  -- JSONB相当 (TEXTで格納しアプリ側/関数で制御)
    request_body TEXT,                    -- JSONB相当
    response_status INTEGER,
    response_body TEXT,                   -- JSONB相当
    duration_ms INTEGER,
    ip_address TEXT,
    user_id INTEGER,
    created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
);

-- パフォーマンス最適化のためのインデックス
CREATE INDEX idx_api_logs_trace_id ON api_logs(trace_id);
CREATE INDEX idx_api_logs_created_at ON api_logs(created_at);
CREATE INDEX idx_api_logs_status ON api_logs(response_status);

-- 処理の詳細ステップログ
CREATE TABLE task_progress_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,               -- api_logs.trace_id と紐付け
    task_name TEXT NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT NOT NULL,                 -- START, SUCCESS, FAILED 等
    input_data TEXT,                      -- JSONB相当
    output_data TEXT,                     -- JSONB相当
    error_message TEXT,
    stack_trace TEXT,
    execution_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'))
);

-- パフォーマンス最適化のためのインデックス
CREATE INDEX idx_task_progress_trace_id ON task_progress_logs(trace_id);
CREATE INDEX idx_task_progress_created_at ON task_progress_logs(created_at);


```


承知いたしました。提示した「API_Logs」と「Task_Progress_Logs」のテーブルデザインを、そのままPythonの辞書形式（dict）として扱い、CSVとTursoの両方に書き込む拡張版`CSVLogger`の実装を作成します。

これを使うことで、**「ローカルのCSV」と「クラウドのTurso」に全く同じ構造のログが自動的に蓄積**されるようになります。


### この構成で実現できること

1. **データ構造の一致**: CSVのカラム名とTursoのテーブルカラム名が完全に一致するため、後からCSVをSQLで分析したり、逆にTursoからCSVへ書き戻すのも容易です。
2. **型変換の自動化**: `request_header` や `input_data` など、Pythonの辞書をそのまま渡せば、`json.dumps` を経てDBにはテキストとして、CSVには文字列として正しく保存されます。
3. **耐障害性**: もしネット接続が不安定でTursoへのHTTPリクエストが失敗しても、ローカルの `logs/api_logs.csv` には必ずデータが残ります。

この実装をベースに、さらに「特定のユーザーIDで絞り込みたい」や「エラー時だけ詳細なスタックトレースを含める」といった調整も簡単に行えます。実際のプロジェクトに組み込んでみてはいかがでしょうか？



プロジェクトの規模と保守性を考えると、**「`app/lib/` にクラス本体を置き、`app/main.py` でインスタンス化して DI（Dependency Injection）で各所に配る」**構成が最もクリーンで FastAPI らしい設計です。

具体的にどこに何を置くべきか、ディレクトリ構造に合わせて整理しました。

---


#### ③ サービス層での利用：`app/services/item_service.py`

ビジネスロジックの中で「進捗」を記録する場合です。

```python
from fastapi import BackgroundTasks
from app.lib.logger import EnhancedCSVLogger

class ItemService:
    def __init__(self, logger: EnhancedCSVLogger):
        self.logger = logger

    async def do_complex_job(self, trace_id: str, background_tasks: BackgroundTasks):
        # 処理進捗を記録
        self.logger.log(background_tasks, "task_progress_logs", {
            "trace_id": trace_id,
            "task_name": "Item_Update",
            "step_name": "DB_Update_Start",
            "status": "SUCCESS"
        })
        # ...実際の処理...

```

#### ④ ルーター層での利用：`app/routers/item_router.py`

ここで `get_logger` を注入します。

```python
from fastapi import APIRouter, Depends, BackgroundTasks
from app.main import get_logger
from app.lib.logger import EnhancedCSVLogger

router = APIRouter()

@router.post("/items")
async def create_item(
    background_tasks: BackgroundTasks,
    logger: EnhancedCSVLogger = Depends(get_logger) # ここでDI
):
    trace_id = "..." 
    # APIアクセスログを記録
    logger.log(background_tasks, "api_logs", { ... })
    return {"status": "ok"}

```

---


### 3. なぜこの構成が良いのか？

1. **テストがしやすい**:
テスト時に Turso へ接続したくない場合、`get_logger` をオーバーライドして「何もしないロガー」や「CSVだけのロガー」に簡単に差し替えられます。
2. **設定の一元管理**:
`main.py`（または `config.py`）で Turso の接続情報を管理するため、環境変数 (`.env`) との連携がスムーズです。
3. **疎結合**:
`item_service.py` 自体は「どうやってログを保存するか」を知る必要がなく、「渡されたロガーの `.log()` を呼ぶ」だけで済みます。


## ポストの分析状況

ポストは定期的に、AIでの整形を予定しています。
１時間に一回生成AIへの要求されていないものがあれば、
それを要求対象にする動きを想定しています。
そのためには各ポストの状況が必要で、そのための設定については以下のとおりとする。


|日本語の状態|推奨する英語定数 (Status)|説明・補足|
|:----|:----|:----|
|なし|unprocessed|まだ何もしていない初期状態。|
|再要求|pending_requeue|ユーザーが「やり直し」を求めた状態。次回のバッチ対象。|
|要求中|processing|AIにリクエストを投げた直後、または実行中。|
|受領済み|refined|AIの回答が届き、ユーザーの確認を待っている状態。|
|登録済み（更新あり）|completed_with_edit|AIの結果を元にユーザーが修正して確定させた。|
|登録済み|completed|AIの結果をそのまま確定させた。|


「なし」「再要求」の場合は、１時間ごとのタスクで生成AIへの要求実施
「要求中」「受領済み」「 登録済み（更新あり）」「登録済み」の物は、一度AIに問い合わせ済なので、対象外とする。

```json
  {
  "ai_request": {
    "status": "processing",
    "updated_at": "2026-02-24T18:00:00Z",
    "retry_count": 0,
    "last_error": null,
    "refined_content": "..." 
    }
　}
```

### 1. API Input（引数）

| カテゴリ | 引数名 | 型 | デフォルト値 | 説明 |
| --- | --- | --- | --- | --- |
| **必須** | `user_id` | UUID | - | 実行ユーザーの識別子 |
| **必須** | `target_period` | Object | - | 開始日〜終了日の指定 |
| **オプション** | `post_ids` | List[ID] | `null` | 特定のポストのみを狙い撃ちで精査する場合に指定 |
| **オプション** | `target_condition` | String | `none` | `none`: 未処理(`unprocessed`, `requeue`)のみ<br>`all`: 全データ(`refined`, `completed`込)を強制再精査 |
| **オプション** | `loglevel` | String | `normal` | `detail`: プロンプト・AI回答をフル保存<br>`normal`: ヘッダ・経緯のみ<br>`none`: ログ保存なし |
| **オプション** | `disp` | String | `none` | `none`: 全工程完遂<br>`targets`: 工程4まで（対象抽出の確認）<br>
`results`: 工程9まで（DB反映直前までの確認） |


### output)
 結果のUUID

### 2. Process（処理フローとログ・状態制御）

`disp` の値によって、**状態更新（processing）をスキップ**し、安全に検証できるロジックを組み込んでいます。

| ステップ | 処理内容 | `API_Logs` (※1) | `Detail` 状態更新 | 備考 |
| --- | --- | --- | --- | --- |
| **1** | Postの検索・抽出 | 検索ヒット件数 | - | `target_condition` に基づく |
| **2** | テンプレート入手 | - | - | プロンプトの雛形取得 |
| **3** | タグ情報入手 | - | - | タグメンテナンス情報 |
| **4** | プロンプト作成 | 作成済みプロンプト | - | **`disp=targets` の場合ここで終了** |
| **5** | **実行予約** | 予約成功件数 | **`processing`** | **`disp` が `none` 以外ならスキップ** |
| **6** | GoogleAIStudio依頼 | リクエスト送信時刻 | - | Gemini API呼び出し |
| **7** | 結果の受領 | AI回答データ(Raw) | - | **`disp=airesult` の場合ここで終了** |
| **8** | 結果のデータ整形 | 整形後データ | - | DB登録用フォーマットへの変換 |
| **9** | **結果のDB登録** | 登録成功件数 | **`refined`** | **`disp=results` の場合ここで終了** |
| **10** | UUID返却 | 最終ステータス | - | `trace_id` をフロントに返却 |


|プロセス|内容|詳細|
|:----|:----|:----|
|1-3|準備|検索条件に合致する件数を API_Logs に記録。|
|4|プロンプト作成|disp=targets の場合ここで終了。 ログにプロンプト案を保存。|
|5|状態更新|status: processing へ一括更新。他プロセスからの割り込みを防止。|
|6-7|AI通信|通信エラー時のリトライ回数、AIのレスポンス時間を計測。|
|8|結果登録|Detail 列に AI結果を一時保存。disp=airesult ならここで停止。|
|9|確定更新|status: refined へ更新。一連の trace_id を付与。|
|10|完了|最終的な成功/失敗数を返し、処理終了。|


### 3. 設計の重要ポイント

#### ⚠️ `disp` 指定時の競合回避（安全策）

アドバイス通り、`disp` が `none`（本番実行）以外のときは、ステップ5の **`processing` 更新をスキップ** します。これにより、「1時間ごとのバッチ」が動いても、検証中のデータが「実行中」としてロックされることがなく、安全にテストできます。

#### 📊 ログの活用（※1）

`loglevel=detail` の場合、ステップ4のプロンプトとステップ7のAI回答を `API_Logs` に残します。これにより、「AIが変な回答をした」ときに、どのプロンプトが悪かったのか後から完全に再現・調査可能になります。

#### 🔄 状態遷移の確定

ステップ9で `refined` になったタイミングで、ユーザー画面（フロントエンド）に「精査完了」のバッジが表示されるようになります。



### A. 個別ポスト精査テーブル (`zstu_post_refinements`)

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


- `ai_request` -> 不要、一括処理時の識別からたどれるので
- `ai_response` -> 不要、一括処理時の識別からたどれるので


```
CREATE TABLE public.zstu_post_refinements (
  id serial NOT NULL,
  post_id integer NOT NULL,
  user_id uuid NOT NULL,
  status character varying NOT NULL DEFAULT 'unprocessed',
  
  -- 1. 要求時（Input）
  request_title text,
  request_content text,
  request_tags jsonb DEFAULT '[]'::jsonb,
  
  -- 2. AIからの返答（AI Output）
  ai_refined_title text,
  ai_refined_content text,
  ai_refined_tags jsonb DEFAULT '[]'::jsonb,
  ai_changes jsonb DEFAULT '[]'::jsonb, -- 変更点の指摘など
  
  -- 3. ユーザーによる調整・確定
  is_fixed boolean NOT NULL DEFAULT false, -- 登録済みフラグ
  fixed_title text,
  fixed_content text,
  fixed_tags jsonb DEFAULT '[]'::jsonb,
  
  trace_id uuid, -- 一括処理時のログテーブル等との紐付け用
  created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT zstu_post_refinements_pkey PRIMARY KEY (id),
  CONSTRAINT fk_zstu_post_refinements_post_id FOREIGN KEY (post_id) 
    REFERENCES public.zstu_posts (id) ON DELETE CASCADE
) TABLESPACE pg_default;

-- インデックス：一つのポストに複数溜まるため、post_idでの検索を高速化
CREATE INDEX idx_refinements_post_id ON public.zstu_post_refinements (post_id);
CREATE INDEX idx_refinements_status ON public.zstu_post_refinements (status);
CREATE INDEX idx_refinements_user_id ON public.zstu_post_refinements (user_id);
```

##### 3. 実装上のアドバイス：ステータス管理のコツ

ご提示いただいたステータス遷移を、別テーブルで管理する際のイメージです。

1. **一括実行（バッチ）**: `status` が `unprocessed` または `pending_requeue` のレコードを SELECT。
2. **ロック**: 取得したレコードを即座に `processing` へ UPDATE（`disp=none` の場合）。
3. **完了**: AIからの応答を `refined_content` に入れ、`status` を `refined` に更新。
4. **ユーザー確認**: ユーザーが画面で「確定」を押したら `completed` または `completed_with_edit` へ。

##### `disp` (検証モード) の扱い

別テーブルにすることで、`disp` が `targets` や `results` のときは **「レコードを作成するが、`zstu_posts` 本体には何の影響も与えない」** という状態が作れるため、本番データへの悪影響を完全に遮断できます。

---

##### 4. ログレベル (`loglevel`) の落とし所

`API_Logs` という別テーブルを想定されているようですが、**「成功した時の詳細ログ」は上記精査テーブルの `ai_request / ai_response` に入れ、「システムエラー（通信失敗など）」は `API_Logs` に入れる**という使い分けが、調査時にあちこちのテーブルを見なくて済むので楽ですよ。




---

## 🚀 AI週間評価API 設計案

このAPIは、1週間分のパブリックなポストと過去2週間のサマリーを読み込み、ユーザーの思考のクセや成長を言語化します。

### 1. Input (引数)

評価の「基準日」を指定することで、過去の任意の週を再評価できるようにします。

| 引数 | 初期値 | 説明 |
| --- | --- | --- |
| **`user_id`** | (必須) | ユーザー識別子。 |
| **`target_date`** | 本日 | 評価対象週の基準日（この日を含む週を評価）。 |
| **`include_past_weeks`** | 2 | 過去何週間分の評価結果をコンテキストに含めるか。 |
| **`options.force_refresh`** | `false` | `true`の場合、既に評価済みでも再計算する。 |
| **`options.focus_theme`** | `none` | 特定のタグやテーマに絞って重点的に評価したい場合に指定。 |
| **`loglevel`** / **`disp`** | `normal` / `none` | 整形APIと同様のデバッグ・保存オプション。 |

---

### 2. Process (ロジックフロー)

週次評価では、**「データの凝縮」**がポイントになります。

1. **対象データの抽出**:
* 指定週の `ZstuPost` のうち、`is_public=true` かつ `status=refined` のものを全取得。

2. **過去コンテキストの取得**:
* 前週・前々週の「週次評価テーブル（後述）」から、AIが作成したサマリーを取得。

3. **タグ統計の算出**:
* 今週多く使われたタグ、出現頻度の変化を数値化。

4. **プロンプト組み立て**:
* 「今週のポスト群」「過去のサマリー」「統計データ」をGeminiに渡し、「変化」と「アドバイス」を求める。

5. **Google AI Studio へのリクエスト**:
* 思考の深まり、習慣の継続、新しい視点の獲得などを分析。

6. **結果の登録**:
* 「週次評価テーブル」に新規保存。

7. **メール通知 (Resend)**:
* 評価結果のダイジェストをユーザーに送信し、アプリへの再訪を促す。



---

### 3. Output (レスポンス)

整形APIと同様、バックグラウンド実行を想定して `trace_id` を即座に返します。

```json
{
  "trace_id": "uuid-eval-12345",
  "status": "accepted",
  "target_week": "2026-W08",
  "message": "週次評価プロセスを開始しました。完了後メールでお知らせします。"
}

```

---

## 週次評価結果を保存するテーブル（案）

AIが生成した評価は、後から振り返れるように専用のテーブル（例：`WeeklyEvaluations`）に保存することを推奨します。

| カラム名 | 説明 |
| --- | --- |
| **`id`** | id |
| **`user_id`** | ユーザーID |
| **`year_week`** | 2026-08 形式の週番号 |
| **`summary`** | AIによる全体サマリー（短文） |
| **`detail_report`** | AIによる詳細分析（Markdown形式） |
| **`top_tags`** | 今週の主要タグ（JSON） |
| **`growth_point`** | AIが見つけた「先週からの変化・成長」 |
| **`post_ids`** | 評価対象となったポストのIDリスト（JSON） |


---

## サマリをAIに問い合わせる動き
Step1 トリガーでプッシュ
STep2 年ｘｘ週ごとのデータみて、状況確認
Step3 未処理なら、処理対象
Step4 処理中ならパス
Step5 処理開始
Step6 Post入手(公開分のみ)
Step7 ＡＩ問い合わせ
Step8 結果登録

## todo 
- [ ] Api経由での呼び出しのテスト
  - [ ] EnhancedCSVLoggerでのログの登録、実践的なもの（※１）
    - task_nameなど入力できるようにして作ってみる、インターバルも含む
- [ ] 「※１」で登録した情報が見えること確認
- [ ] タイマー処理で、定期的にPosts取得する動きの実装
- [ ] タイマー処理を手動で、Postsできる動きの追加
- [ ] スタート画面、ダッシュボードの整理(/Dashboard) メニューの追加　ログ一覧画面、タイマーを手動で実行する画面、ログを登録する画面
- [ ] メール: Resend の統合（精査結果の送信）
- [ ] 低：UI調整: htmx を使ったダッシュボードの動的化

- [ ] Promtをテーブルからの入手
- [ ] 過去分デプロイ済み分で登録
- [ ] タイポの実装
  - [ ] 処理のモックアップ作成
  - [ ] 引数に応じたフロー作成
  - [ ] 開始のStatuに変更
  - [ ] ログ記載の件
  - [ ] 結果登録の件
  - [ ] メール送信
- [ ] サマリの実装
  - [ ] 専用テーブルの見直し、Stateいるんでないかな・・・重複回避必要かと
  - [ ] UI作成
  - [ ] 引数選定
  - [ ] 処理のモックアップ作成
  - [ ] 引数に応じたフロー作成
  - [ ] 開始のStatuに変更
  - [ ] ログ記載の件
  - [ ] 結果登録の件
  - [ ] メール送信
- [ ] 他システムサマリ処理の検討
  - [ ] 昨日分拾って、登録するかどうかを翌日の１時に作成
  - [ ] 翌日URLみて、登録するかを選ぶ
  - [ ] どちらにしてもメール機能必要
- [ ] メール送信機能整理　Resend候補かと・・・
  - [ ] お名前.comの状況確認


## History 
- 2026/03/01
  - GeminiAI調整
  - resend テスト
- 2026/02/25
  - ホスト [CloudRun]([https://](https://bezstv1-420574500377.asia-northeast1.run.app/dashboard))
  - UI回り、APITest用のUi画面作成、Htmxの利用など開始
- 2026/02/23
  - デプロイ完了



---


