
# PFXDRSBase

Python + FastAPI + htmx + Docker + Render + Supabase を組み合わせた、開発効率とモダンなユーザー体験を両立させるためのフルスタック・テンプレートです。

## 🚀 プロジェクト概要

PFXDRS Templateは、ReactやVueなどの重厚なSPAフレームワークを使わずに、HTMLベースで動的なUIを実現する\*\*「ハイパーメディア駆動」\*\*な開発スタイルを提案します。
クリーンなディレクトリ構成とコンテナ化により、迅速な開発からデプロイまでをスムーズに行える構成になっています。

---

## 🛠 技術スタックと選定理由

|技術要素|役割・選定理由|
|-|-|
|**Python / FastAPI**|サーバーサイドの主軸。Router/Service層を分けたクリーンな構成の学習と実践。|
|**htmx**|フロントエンドのUX向上。HTMLベースで動的な非同期通信を実現し、複雑さを軽減。|
|**DaisyUI (Tailwind CSS)**|UIコンポーネントライブラリ。直接CSSを書く手間を省き、一貫したデザインを迅速に構築。|
|**Docker**|環境のポータビリティ確保。Render以外のホスト環境への移行も容易にするため。|
|**Render**|サーバーサイドおよびDockerとの親和性が高く、Vercel以外の有力な選択肢として採用。|
|**Supabase**|データベース(PostgreSQL)および認証基盤(Auth)として利用。|

---

## 📋 基本仕様

### 1\. 開発・実行環境

* **エディタ**: Visual Studio Code (VS Code)
* **開発支援**: Gemini Code Assist
* **ランタイム**: Python 3.11+ / Docker
* **パッケージ管理**: pip (`requirements.txt`)

### 2\. フロントエンド

* **テンプレートエンジン**: Jinja2 (サーバーサイドレンダリング)
* **非同期通信**: htmx (Partial HTMLの差し替え)
* **スタイリング**: DaisyUI (Tailwind CSSベースのコンポーネント)

### 3\. バックエンド \& BaaS

* **Webフレームワーク**: FastAPI
* **バリデーション**: Pydantic
* **DB/Auth**: Supabase (PostgreSQL / Supabase Auth)
* **SDK**: `supabase-py`

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

Renderを利用したCI/CDが自動化されています。

1. **GitHubへPush**: `main` ブランチへコードをプッシュ。
2. **ビルド**: Renderがリポジトリの `Dockerfile` を検知し、Dockerイメージをビルド。
3. **自動デプロイ**: ビルド成功後、Web Serviceとして自動デプロイ。
4. **環境変数管理**: Render Dashboardおよびローカルの `.env` で秘匿情報を管理。

---