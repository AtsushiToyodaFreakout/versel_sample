from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import openai
import re
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # URLパラメータを解析
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # アーティスト名を取得（デフォルトは「スピッツ」）
            artist = query_params.get('artist', ['スピッツ'])[0]
            
            # 環境変数からAPIキーを取得
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "error",
                    "message": "OPENAI_API_KEY環境変数が設定されていません"
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
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
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    response_data = {
                        "status": "success",
                        "artist": artist,
                        "recommendations": data.get('recommendations', [])
                    }
                    self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
                    
                except json.JSONDecodeError:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    error_response = {
                        "status": "error",
                        "message": "AIの回答をJSONとして解析できませんでした",
                        "raw_response": raw_response
                    }
                    self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = {
                    "status": "error", 
                    "message": "AIの回答からJSON部分を見つけられませんでした",
                    "raw_response": raw_response
                }
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {
                "status": "error",
                "message": f"エラーが発生しました: {str(e)}"
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))