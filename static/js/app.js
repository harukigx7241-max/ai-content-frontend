// ... existing code ...
              button({ 
                  onClick: () => handleMagic('all'), 
                  disabled: isMagicLoading,
                  className: 'w-full bg-gradient-to-r from-brand-accent to-red-500 text-white text-xs font-bold py-2 rounded-lg shadow-lg hover:brightness-110 transition disabled:opacity-50 mb-2' 
              }, isMagicLoading ? '魔法詠唱中...' : '💫 コンテキスト連鎖マジック (全項目を一撃で埋める)'),
              
              // 🌟 新機能：AIおまかせ無限テンプレート生成ボタンを追加
              button({ 
                  onClick: async () => {
                      if (role !== 'admin' && uData.credits <= 0) { setError('クレジットが不足しています。'); return; }
                      setIsMagicLoading(true); setError('');
                      try {
                          const promptText = tid === 'note' ? 
                              `noteで現在バズっている、または売れやすい最新のWebトレンド（副業、AI、恋愛、メンタル、投資など）を1つランダムに選び、そのテーマで記事を書くための設定をJSONで出力してください。\nフォーマット:\n{\n "genre": "（ジャンル名。例:副業・ビジネス）",\n "age": "（ターゲット年代。例:20代）",\n "theme": "（魅力的な記事テーマ）",\n "target": "（読者の具体的な悩み）",\n "free_len": "1500",\n "paid_len": "4000",\n "price": "1980"\n}` 
                              : 
                              `このツール「${conf.name}」において、現在SNSやWebでトレンドになっているバズりやすいテーマをランダムに1つ考え、以下の入力項目を埋めるためのJSONを出力してください。\n項目:\n${conf.fields.map(f => `"${f.id}": "(${f.l}の具体的な内容)"`).join(',\n')}`;
                          
                          let currentProvider = magicAI;
                          let ai_model = currentProvider === 'openai' ? 'chatgpt_free' : currentProvider === 'anthropic' ? 'claude_free' : 'gemini_free';
                          const res = await fetch('/api/auto_generate', {
                              method: 'POST', headers: {'Content-Type': 'application/json'},
                              body: JSON.stringify({ prompt: promptText + '\n\n必ずJSONデータのみ（\`\`\`jsonなどの装飾なし）を出力してください。', user_api_key: userKeys[currentProvider], ai_model: ai_model })
                          });
                          const data = await res.json();
                          if(data.status === 'success') {
                              let jsonStr = data.result.match(/\{[\s\S]*\}/);
                              if(jsonStr) {
                                  const parsed = JSON.parse(jsonStr[0]);
                                  const newVals = {...vals, ...parsed};
                                  setVals(newVals);
                                  if (role !== 'admin') {  
                                      const ndb = AppDB.get(); ndb.users[user].projects[uData.curProj].data[tid] = newVals; AppDB.save(ndb);  
                                  }
                                  showToast(`🎲 AIおまかせ生成完了！ランダムなトレンドテーマをセットしました！`);
                              } else {
                                  setError("JSONの解析に失敗しました。もう一度お試しください。");
                              }
                          } else {
                              setError(data.message);
                          }
                      } catch(e) { setError('AIおまかせ生成に失敗しました。APIキーの設定などを確認してください。'); }
                      setIsMagicLoading(false);
                  }, 
                  disabled: isMagicLoading,
                  className: 'w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold py-2 rounded-lg shadow-lg hover:brightness-110 transition disabled:opacity-50 mb-2' 
              }, '🎲 AIおまかせ無限テンプレート生成 (ランダムトレンドで埋める)'),

              showAdvancedMagic && div({ className: 'space-y-3 mt-3 pt-3 border-t border-white/10 animate-in' },
// ... existing code ...
