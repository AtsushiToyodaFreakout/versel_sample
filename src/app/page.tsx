'use client';

import { useState } from 'react';

export default function Home() {
  const [message, setMessage] = useState("アーティスト名を入力して検索ボタンを押してください");
  const [artistInput, setArtistInput] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const searchArtist = async () => {
    if (!artistInput.trim()) {
      setMessage("アーティスト名を入力してください");
      return;
    }

    try {
      setIsLoading(true);
      console.log("APIを呼び出し中...");
      setMessage("ChatGPT APIを呼び出し中...");
      setRecommendations([]);
      
      const res = await fetch(`/api?artist=${encodeURIComponent(artistInput)}`);
      const data = await res.json();
      
      if (data.status === 'success') {
        setMessage(`「${data.artist}」に似たアーティストを見つけました！`);
        setRecommendations(data.recommendations);
      } else {
        setMessage(`エラー: ${data.message}`);
        setRecommendations([]);
      }
    } catch (error) {
      console.error("エラー:", error);
      setMessage("エラーが発生しました");
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <h1>おすすめアーティスト検索</h1>
        
        <div style={{ margin: '30px 0' }}>
          <input
            type="text"
            placeholder="アーティスト名(例: スピッツ, 米津玄師)"
            value={artistInput}
            onChange={(e) => setArtistInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isLoading && searchArtist()}
            style={{
              padding: '12px 20px',
              fontSize: '16px',
              width: '400px',
              maxWidth: '80%',
              border: '2px solid #ddd',
              borderRadius: '8px',
              marginRight: '10px'
            }}
            disabled={isLoading}
          />
          <button
            onClick={searchArtist}
            disabled={isLoading}
            style={{
              padding: '12px 24px',
              fontSize: '16px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              backgroundColor: isLoading ? '#ccc' : '#0070f3',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              marginTop: '10px'
            }}
          >
            {isLoading ? '検索中' : '🔍 検索'}
          </button>
        </div>
        
        <p style={{ fontSize: '18px', margin: '20px 0', color: '#666' }}>
          {message}
        </p>
        
        {recommendations.length > 0 && (
          <div style={{ marginTop: '30px', textAlign: 'left', maxWidth: '600px', margin: '30px auto' }}>
            <h2>おすすめアーティスト:</h2>
            {recommendations.map((rec: any, index: number) => (
              <div key={index} style={{ 
                border: '1px solid #ddd', 
                padding: '15px', 
                margin: '10px 0', 
                borderRadius: '8px',
                backgroundColor: '#f9f9f9'
              }}>
                <h3 style={{ margin: '0 0 10px 0', color: '#0070f3' }}>{rec.artist}</h3>
                <p style={{ margin: '5px 0', color: '#0070f3'}}><strong>代表曲:</strong> {rec.song}</p>
                <p style={{ margin: '5px 0', color: '#0070f3'}}><strong>推薦理由:</strong> {rec.reason}</p>
              </div>
            ))}
          </div>
        )}
      </div>
  );
}