import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const artist = searchParams.get('artist') || 'スピッツ';

    // 環境変数からAPIキーを取得
    const apiKey = process.env.OPENAI_API_KEY;
    
    if (!apiKey) {
      return NextResponse.json({
        status: 'error',
        message: 'OPENAI_API_KEY環境変数が設定されていません'
      });
    }

    const systemPrompt = `あなたはプロの音楽キュレーターです。
ユーザーから送られてきたアーティスト名に基づき、
そのアーティストとジャンルや音楽性が近い、
他のアーティストを3組推薦してください。
代表曲も教｀えてください。
推薦理由も日本語で一言添えてください。
以下の形式で回答してください:
{
  "recommendations": [
    {"artist": "アーティスト名1", "reason": "推薦理由1", "song": "代表曲"},
    {"artist": "アーティスト名2", "reason": "推薦理由2", "song": "代表曲"},
    {"artist": "アーティスト名3", "reason": "推薦理由3", "song": "代表曲"}
  ]
}`;

    const userPrompt = `好きなアーティストは「${artist}」です。`;

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'gpt-3.5-turbo',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ]
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`);
    }

    const data = await response.json();
    const rawResponse = data.choices[0].message.content;

    const jsonMatch = rawResponse.match(/\{[\s\S]*\}/);

    if (jsonMatch) {
      try {
        const parsedData = JSON.parse(jsonMatch[0]);

        return NextResponse.json({
          status: 'success',
          artist: artist,
          recommendations: parsedData.recommendations || []
        });
      } catch (parseError) {
        return NextResponse.json({
          status: 'error',
          message: 'AIの回答をJSONとして解析できませんでした',
          raw_response: rawResponse
        });
      }
    } else {
      return NextResponse.json({
        status: 'error',
        message: 'AIの回答からJSON部分を見つけられませんでした',
        raw_response: rawResponse
      });
    }

  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({
      status: 'error',
      message: `エラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}`
    });
  }
}