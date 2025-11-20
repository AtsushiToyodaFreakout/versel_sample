This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app) with Flask API backend.

## プロジェクト概要

このプロジェクトは、Next.js (React) のフロントエンドと Flask (Python) のバックエンドを組み合わせたアプリケーションです。
OpenAI の ChatGPT API を使用して、好きなアーティストに似た音楽アーティストを推薦する機能を提供します。

## Getting Started

### 必要な環境変数

Vercel にデプロイする前に、以下の環境変数を設定する必要があります：

- `OPENAI_API_KEY`: OpenAI API キー

Vercel ダッシュボードの Settings > Environment Variables から設定してください。

### ローカル開発

First, install dependencies:

```bash
npm install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## プロジェクト構成

- `/src/app/` - Next.js のフロントエンドコード
  - `page.tsx` - メインページ UI
  - `layout.tsx` - アプリケーションレイアウト
- `/api/` - Flask バックエンド API
  - `index.py` - Flask アプリケーション (ChatGPT API を呼び出す)
  - `requirements.txt` - Python 依存関係
- `vercel.json` - Vercel デプロイ設定

## API エンドポイント

### GET /api/index

アーティストに似た音楽アーティストを推薦します。

**パラメータ:**
- `artist` (string, optional): 検索するアーティスト名 (デフォルト: "スピッツ")

**レスポンス例:**
```json
{
  "status": "success",
  "artist": "スピッツ",
  "recommendations": [
    {
      "artist": "推薦アーティスト名1",
      "reason": "推薦理由1",
      "song": "代表曲1"
    },
    ...
  ]
}
```

## Vercel へのデプロイ

### 重要な設定ファイル

1. **vercel.json** - Vercel の設定ファイル
   - `builds`: Python コードのビルド設定
   - `routes`: API ルーティング設定

2. **api/requirements.txt** - Python 依存関係
   - flask
   - openai

### デプロイ手順

1. Vercel にプロジェクトをインポート
2. Environment Variables に `OPENAI_API_KEY` を設定
3. デプロイ実行

Vercel は自動的に：
- Next.js アプリケーションをビルド
- Flask API を Python serverless function として構成
- `/api/*` へのリクエストを Flask アプリにルーティング

## 修正内容 (この PR で実施)

### 問題点
Flask バックエンドが Vercel で動作せず、Next.js からのリクエストが 404 エラーで返っていました。

### 解決策
1. **api/index.py** - 不要な `handler()` 関数を削除
   - 以前は `test_request_context()` を使用した誤った実装がありました
   - Vercel は Flask アプリを直接 WSGI アプリケーションとして処理します

2. **vercel.json** - 設定を修正
   - `functions` + `rewrites` から `builds` + `routes` に変更
   - `@vercel/python` ビルダーを明示的に指定
   - API ルーティングを適切に設定

3. **src/app/page.tsx** - TypeScript の型定義を改善
   - `Recommendation` インターフェースを追加
   - `any` 型を排除して型安全性を向上

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python) - Vercel Python serverless functions documentation.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
