
import json
import os

from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    APIStatusError,
)

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_llm(**kwargs):
    global api_call_count

    if api_call_count >= MAX_API_CALLS:
        print("API呼び出し回数の上限に達しました。")
        raise SystemExit(1)

    api_call_count += 1

    try:
        return client.responses.create(**kwargs)

    except APITimeoutError:
        print("エラー：APIの応答がタイムアウトしました。")

    except APIConnectionError:
        print("エラー：APIに接続できません。")

    except RateLimitError:
        print("エラー：APIの利用制限に達しました。")

    except APIStatusError as e:
        print(f"APIエラー：HTTP {e.status_code}")

    raise SystemExit(1)


total_input_tokens = 0
total_output_tokens = 0
MAX_API_CALLS = 3
api_call_count = 0
web_search_count = 0

# Python側で実際に動く関数


def get_available_time():
    print("[Python] get_available_time() を実行")

    while True:
        user_input = input("活動に使える時間（分）：").strip()

        # 未入力なら時間は不明として扱う
        if user_input == "":
            return {"available_minutes": None}

        # 整数への変換を試みる
        try:
            minutes = int(user_input)
        except ValueError:
            print("数字で入力してください。")
            continue

        # 入力値が適切か確認する
        if not 1 <= minutes <= 1440:
            print("1〜1440分の範囲で入力してください。")
            continue

        return {"available_minutes": minutes}




# LLMに公開するツールの定義
tools = [
    {"type": "web_search"},
    {
        "type": "function",
        "name": "get_available_time",
        "description": "ユーザーが活動に使える時間を取得する",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


interest = input("興味のあることを入力してください：")


instructions = (
    "あなたはユーザーの好奇心を具体的な行動につなげるAIです。"
    "今日または明日から挑戦できる活動を、異なる方向性で3つ提案してください。"
    "必要に応じてWeb検索を行い、最新情報を確認してください。"
    "外出先の地域指定がなければ東京・千葉周辺を対象にしてください。"
    "利用可能時間が分かる場合は、移動・準備も含めた所要時間を考慮してください。"
    "実在するイベントや施設については、開催日時、料金、対象者、"
    "予約の必要性を可能な範囲で公式情報から確認してください。"
    "確認できなかった情報は推測で埋めず、未確認と明示してください。"
    "各提案には、活動名、内容、目安時間、費用、最初の一歩、"
    "参考URLを可能な範囲で含めてください。"
    "単なる検索方法の紹介ではなく、実際に行動できる提案を優先してください。"
    "条件を満たす候補が3つ見つからない場合は、その理由を説明し、"
    "無理に候補を作らないでください。"
)


MAX_WEB_TOOL_CALLS = 2
# 最初のAPI呼び出し
response = call_llm(
    model="gpt-6-luna",
    instructions=instructions,
    input=interest,
    tools=tools,
    tool_choice="auto",
    max_tool_calls=MAX_WEB_TOOL_CALLS,
)

# Python側で管理する実行ループ
MAX_STEPS = 3


# 最初のAPI呼び出し分を記録


if response.usage:
    total_input_tokens += response.usage.input_tokens
    total_output_tokens += response.usage.output_tokens

web_search_count += sum(
    item.type == "web_search_call"
    for item in response.output
)

for step in range(MAX_STEPS):
    print(f"\n=== 実行ステップ {step + 1} ===")
    

    # 今回のAPI応答に含まれるツール実行を確認
    for item in response.output:
        if item.type == "web_search_call":
            print("[Web検索] ステータス:", item.status)
            print("[Web検索] アクション:", item.action)

        elif item.type == "function_call":
            print("[Function Calling] 要求:", item.name)


    function_calls = [
        item for item in response.output
        if item.type == "function_call"
    ]

    # 関数呼び出しがなければ終了
    if not function_calls:
        print("\n=== 提案された活動 ===")
        print(response.output_text)
        break

    # LLMから要求された関数を実行
    results = []

    for call in function_calls:
        print("[LLM] 関数呼び出し要求:", call.name)

        if call.name == "get_available_time":
            result = get_available_time()
        else:
            raise ValueError(f"未対応の関数: {call.name}")

        results.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result),
        })

    # 関数の実行結果をLLMに返す
    response = call_llm(
        model="gpt-6-luna",
        instructions=instructions,
        previous_response_id=response.id,
        input=results,
        tools=tools,
        tool_choice="auto",
        max_tool_calls=MAX_WEB_TOOL_CALLS,
    )
    
    if response.usage:
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

    web_search_count += sum(
        item.type == "web_search_call"
        for item in response.output
    )

else:
    print("実行回数の上限に達しました。")

print("\n=== API利用状況 ===")
print("API呼び出し回数:", api_call_count)
print("Web検索ツール呼び出し回数:", web_search_count)
print("入力トークン:", total_input_tokens)
print("出力トークン:", total_output_tokens)