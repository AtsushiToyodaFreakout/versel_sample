from flask import Flask, jsonify, request
import openai
import re
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    try:
        # URLパラメータからアーティスト名を取得
        artist = request.args.get('artist', 'スピッツ')

        # 環境変数からAPIキーを取得
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                "status": "error",
                "message": "OPENAI_API_KEY環境変数が設定されていません"
            }), 500

        client = openai.OpenAI(api_key=api_key)

        # ChatGPT APIに投げるプロンプト
        system_prompt = (
            "あなたはプロの音楽キュレーターです。"
            "ユーザーから送られてきたアーティスト名に基づき、"
            "そのアーティストとジャンルや音楽性が近い、"
            "他のアーティストを3組推薦してください。"
            "代表曲も教えてください。"
            "推薦理由も日本語で一言添えてください。"
            "以下の形式で回答してください:\n"
            "{\n"
            "  \"recommendations\": [\n"
            "    {\"artist\": \"アーティスト名1\", \"reason\": \"推薦理由1\", \"song\": \"代表曲\"},\n"
            "    {\"artist\": \"アーティスト名2\", \"reason\": \"推薦理由2\", \"song\": \"代表曲\"},\n"
            "    {\"artist\": \"アーティスト名3\", \"reason\": \"推薦理由3\", \"song\": \"代表曲\"}\n"
            "  ]\n"
            "}"
        )
        user_prompt = f"好きなアーティストは「{artist}」です。"

        # APIを呼び出す
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        raw_response = response.choices[0].message.content

        # 生の回答からJSON部分を抜き出す
        match = re.search(r'\{.*\}', raw_response, re.DOTALL)

        if match:
            json_text = match.group(0)
            try:
                # JSON文字列をPythonの辞書に変換
                data = json.loads(json_text)

                return jsonify({
                    "status": "success",
                    "artist": artist,
                    "recommendations": data.get('recommendations', [])
                })
            except json.JSONDecodeError:
                return jsonify({
                    "status": "error",
                    "message": "AIの回答をJSONとして解析できませんでした",
                    "raw_response": raw_response
                }), 500
        else:
            return jsonify({
                "status": "error",
                "message": "AIの回答からJSON部分を抽出できませんでした",
                "raw_response": raw_response
            }), 500

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Vercel Serverless Functions用のハンドラー
def handler(event, context):
    with app.test_request_context(
            path=event.get('path', '/'),
            method=event.get('httpMethod', 'GET'),
            query_string=event.get('queryStringParameters', {})
    ):
        response = app.full_dispatch_request()
        return {
            'statusCode': response.status_code,
            'body': response.get_data(as_text=True),
            'headers': dict(response.headers)
        }