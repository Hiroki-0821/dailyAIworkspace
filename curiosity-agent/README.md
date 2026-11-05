
# Curiosity Agent

日常の興味や好奇心を、実際の行動につなげるAIエージェント。

## 概要

ユーザーが興味を入力すると、AIが必要に応じてWeb検索を行い、今日または明日から試せる活動を提案します。

## 主な機能

- 自由な日本語による興味の入力
- LLMによるWeb検索の判断と実行
- Function CallingによるPython関数の利用
- 利用可能時間を考慮した活動提案
- ツール実行ログの表示
- API利用量の記録
- 基本的なエラー処理と実行回数の制限

## 使用技術

- Python 3.12
- OpenAI Responses API
- Web Search
- Function Calling
- python-dotenv

## セットアップ

1. Python 3.12で仮想環境を作成
2. requirements.txtからライブラリをインストール
3. .envにOPENAI_API_KEYを設定
4. python main.pyで実行

※ OpenAI APIの利用料金が別途発生します。

## 今後の改善案

- 活動履歴の保存
- ユーザーの興味・好みの記憶
- 提案の評価機能
- 複数LLMによる役割分担
- Webアプリ化
