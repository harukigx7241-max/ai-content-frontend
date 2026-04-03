import re

path = '/root/ai-content-pro/static/js/app.js'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# パッチ1: ペルソナ設定のウィザード対応
repl1 = """let personaText = '';
      if (settings) {
          let pLines = [];
          if (settings.persona_base) pLines.push('基本性格: ' + settings.persona_base);
          if (settings.persona_first) pLines.push('一人称: ' + settings.persona_first);
          if (settings.persona) pLines.push('詳細設定: ' + settings.persona);
          if (pLines.length > 0) personaText = '\\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\\n' + pLines.join('\\n') + '\\n';
      }"""
c, c1 = re.subn(r"let personaText = settings && settings\.persona \? [^:]+ : '';", repl1, c, count=1)

# パッチ2: UIをウィザード化
repl2 = """div({ className: 'p-4 bg-black/20 border border-white/10 rounded-xl mb-2' },
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, 'ベースの性格・トーン'),
                                select({ className: 'input-base !py-2 text-xs mb-3', value: uData.settings.persona_base || '', onChange: e => { const val=e.target.value; const ndb=AppDB.get(); ndb.users[user].settings.persona_base=val; AppDB.save(ndb); setDb(ndb); } },
                                    option({value:''}, '指定なし（標準）'), option({value:'プロフェッショナルで論理的'}, 'プロフェッショナルで論理的'), option({value:'優しく寄り添う共感型'}, '優しく寄り添う共感型'), option({value:'熱血で情熱的なリーダー'}, '熱血で情熱的なリーダー'), option({value:'ユーモア溢れる親友'}, 'ユーモア溢れる親友')
                                ),
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, '一人称'),
                                input({ className: 'input-base !py-2 text-xs mb-3', placeholder: '例: 私、僕、俺', value: uData.settings.persona_first || '', onChange: e => { const val=e.target.value; const ndb=AppDB.get(); ndb.users[user].settings.persona_first=val; AppDB.save(ndb); setDb(ndb); } }),
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, '自由記述（詳細な設定・口癖など）'),
                                textarea({ className: 'input-base min-h-[80px] text-xs', placeholder: '例: 語尾に「〜ですよね！」をよく使う。専門用語は避ける。', value: persona, onChange: e => setPersona(e.target.value) })
                            ),"""
c, c2 = re.subn(r"textarea\(\{ className: 'input-base min-h-\[100px\] text-xs', placeholder: '例: 私はプロのWebマーケターです[^']+', value: persona, onChange: e => setPersona\(e\.target\.value\) \}\),", repl2, c, count=1)

# パッチ3: 超特化プロンプト注入
repl3 = r"""\1
          let specialPersona = "";
          if (conf.cat === 'mon') specialPersona = "【超特化型ペルソナ】\\nあなたは累計10億円を売り上げた世界トップクラスのダイレクトレスポンスコピーライターであり、天才マーケターです。読者の「潜在的な痛み（Pain）」を深くえぐり、論理と感情の両面から購買意欲を限界まで高める文章を構築してください。出力は常に専門的かつ説得力に満ちたものにします。\\n\\n";
          else if (conf.cat === 'sns') specialPersona = "【超特化型ペルソナ】\\nあなたは各SNS（X, Instagram, TikTok等）のアルゴリズムを完全にハックし、累計100万フォロワーを熱狂させてきた天才SNSマーケターです。スクロールする指を強制的に止める強烈なフック、読者の共感と有益性、そして思わずシェアしたくなる心理的トリガーを駆使して作成してください。\\n\\n";
          else if (conf.cat === 'cw') specialPersona = "【超特化型ペルソナ】\\nあなたはクラウドソーシングで採用率99%、リピート率100%を誇るトップ1%のフリーランスプロデューサーです。クライアントの潜在的なニーズ（言外の要望）を先読みし、圧倒的な信頼感と「この人に頼めば間違いない」という安心感を与える文章を作成してください。\\n\\n";
          else if (conf.cat === 'fun') specialPersona = "【超特化型ペルソナ】\\nあなたは世界最高のカスタマーサクセス・プロフェッショナルであり、ファン化の達人です。相手の感情に深く寄り添い、どんなクレームも感動に変え、既存顧客を熱狂的なファン（リピーター）へと育成する、温かく誠実なコミュニケーションを構築してください。\\n\\n";
          else if (conf.cat === 'uranai') specialPersona = "【超特化型ペルソナ】\\nあなたは予約が数ヶ月取れない、慈愛と的確さを兼ね備えたカリスマ占い師です。相談者の心に深く寄り添い、ネガティブな結果であっても希望の光を見出せるような、温かくポジティブなアドバイスへと昇華させて伝えてください。\\n\\n";
          promptText = specialPersona + promptText;
"""
c, c3 = re.subn(r"(let\s+promptText\s*=\s*conf\.build\(vals\);\s*if\s*\(conf\.isImagePrompt\)\s*return\s+promptText;)", repl3, c, count=1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)

print(f"✅ パッチ適用完了: 1={c1}, 2={c2}, 3={c3}")
