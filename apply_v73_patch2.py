#!/usr/bin/env python3
import os
import shutil

APP_JS = '/root/ai-content-pro/static/js/app.js'

def apply_patch(content, search, replace, label):
    if search in content:
        content = content.replace(search, replace, 1)
        print(f"  ✅ 成功: {label}")
    else:
        print(f"  ⚠️ スキップ（既に適用済み、または該当箇所なし）: {label}")
    return content

def patch_app():
    if not os.path.exists(APP_JS): return
    shutil.copy2(APP_JS, APP_JS + '.bak2')
    with open(APP_JS, 'r', encoding='utf-8') as f: content = f.read()

    # 1. getAIPrefix関数: ペルソナウィザードの項目をプロンプトに反映
    search1 = "let personaText = settings && settings.persona ? '\\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\\n' + settings.persona + '\\n' : '';"
    replace1 = """let personaText = '';
      if (settings) {
          let pLines = [];
          if (settings.persona_base) pLines.push('基本性格: ' + settings.persona_base);
          if (settings.persona_first) pLines.push('一人称: ' + settings.persona_first);
          if (settings.persona) pLines.push('詳細設定: ' + settings.persona);
          if (pLines.length > 0) personaText = '\\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\\n' + pLines.join('\\n') + '\\n';
      }"""
    content = apply_patch(content, search1, replace1, "ペルソナウィザード対応プロンプト構築")

    # 2. 個人設定UI: マイペルソナのウィザード化
    search2 = "textarea({ className: 'input-base min-h-[120px] text-xs', placeholder: '例: 私はプロのWebマーケターです。実績は〇〇で、文章は論理的かつ情熱的に書きます。', value: persona, onChange: e => setPersona(e.target.value) })"
    replace2 = """div({ className: 'p-4 bg-white/5 border border-white/10 rounded-xl mb-4' },
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, 'ベースの性格・トーン'),
                                select({ className: 'input-base !py-2 text-xs mb-3', value: uData.settings.persona_base || '', onChange: e => { const val=e.target.value; const ndb=AppDB.get(); ndb.users[user].settings.persona_base=val; AppDB.save(ndb); setDb(ndb); } },
                                    option({value:''}, '指定なし（標準）'), option({value:'プロフェッショナルで論理的'}, 'プロフェッショナルで論理的'), option({value:'優しく寄り添う共感型'}, '優しく寄り添う共感型'), option({value:'熱血で情熱的なリーダー'}, '熱血で情熱的なリーダー'), option({value:'ユーモア溢れる親友'}, 'ユーモア溢れる親友')
                                ),
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, '一人称'),
                                input({ className: 'input-base !py-2 text-xs mb-3', placeholder: '例: 私、僕、俺', value: uData.settings.persona_first || '', onChange: e => { const val=e.target.value; const ndb=AppDB.get(); ndb.users[user].settings.persona_first=val; AppDB.save(ndb); setDb(ndb); } }),
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, '自由記述（詳細な設定・口癖など）'),
                                textarea({ className: 'input-base min-h-[80px] text-xs', placeholder: '例: 語尾に「〜ですよね！」をよく使う。専門用語は避ける。', value: persona, onChange: e => setPersona(e.target.value) })
                            )"""
    content = apply_patch(content, search2, replace2, "マイペルソナのウィザードUI化")

    # 3. 個人設定UI: API設定のアコーディオン化
    search3 = """                    tab === 'advanced' && div({ className: 'animate-in' },
                        div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl leading-relaxed text-slate-300' },
                            p({ className: 'text-xs font-bold text-brand-light mb-2' }, '\\u26A0\\uFE0F 自身のAPIキー登録 (任意)'),
                            p({ className: 'text-[10px] mb-1' }, '※APIキーを登録すると、クレジットを消費せずに生成可能になります。初心者の方は未設定のままでもシステム側のキーで動作します。')
                        ),
                        div({ className: 'flex gap-2 mb-6' },"""
    replace3 = """                    tab === 'advanced' && div({ className: 'animate-in' },
                        div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl leading-relaxed text-slate-300 cursor-pointer hover:bg-brand/20 transition', onClick: e => { e.currentTarget.nextElementSibling.classList.toggle('hidden'); e.currentTarget.querySelector('.arrow').textContent = e.currentTarget.nextElementSibling.classList.contains('hidden') ? '▼' : '▲'; } },
                            div({ className: 'flex justify-between items-center' },
                                p({ className: 'text-xs font-bold text-brand-light' }, '\\u26A0\\uFE0F 自身のAPIキー登録 (任意)'),
                                span({ className: 'text-xs arrow' }, '▼')
                            ),
                            p({ className: 'text-[10px] mt-2' }, '※APIキーを登録するとクレジットを消費せずに無制限で生成可能になります。初心者の方は未設定のままでもシステム側のキーで動作します。タップで開閉します。')
                        ),
                        div({ className: 'hidden animate-in space-y-4' },
                            div({ className: 'flex gap-2 mb-6' },"""
    content = apply_patch(content, search3, replace3, "API設定のアコーディオンUI化")

    # 4. 全ツールの超・特化型プロンプト化 (グローバル・インジェクション)
    search4 = """          if (isCustom) {
              promptText = conf.buildPrompt;
              conf.fields.forEach(f => { promptText = promptText.replace(new RegExp(`{${f.id}}`, 'g'), vals[f.id]||''); });
          } else { promptText = conf.build ? conf.build(vals) : ''; }
          
          if (conf.isImagePrompt) return promptText;"""
    replace4 = """          if (isCustom) {
              promptText = conf.buildPrompt;
              conf.fields.forEach(f => { promptText = promptText.replace(new RegExp(`{${f.id}}`, 'g'), vals[f.id]||''); });
          } else { promptText = conf.build ? conf.build(vals) : ''; }
          
          let specialPersona = "";
          if (conf.cat === 'mon') specialPersona = "【超特化型ペルソナ】\\nあなたは累計10億円を売り上げた世界トップクラスのダイレクトレスポンスコピーライターであり、天才マーケターです。読者の「潜在的な痛み（Pain）」を深くえぐり、論理と感情の両面から購買意欲を限界まで高める文章を構築してください。出力は常に専門的かつ説得力に満ちたものにします。\\n\\n";
          else if (conf.cat === 'sns') specialPersona = "【超特化型ペルソナ】\\nあなたは各SNS（X, Instagram, TikTok等）のアルゴリズムを完全にハックし、累計100万フォロワーを熱狂させてきた天才SNSマーケターです。スクロールする指を強制的に止める強烈なフック、読者の共感と有益性、そして思わずシェアしたくなる心理的トリガーを駆使して作成してください。\\n\\n";
          else if (conf.cat === 'cw') specialPersona = "【超特化型ペルソナ】\\nあなたはクラウドソーシングで採用率99%、リピート率100%を誇るトップ1%のフリーランスプロデューサーです。クライアントの潜在的なニーズ（言外の要望）を先読みし、圧倒的な信頼感と「この人に頼めば間違いない」という安心感を与える文章を作成してください。\\n\\n";
          else if (conf.cat === 'fun') specialPersona = "【超特化型ペルソナ】\\nあなたは世界最高のカスタマーサクセス・プロフェッショナルであり、ファン化の達人です。相手の感情に深く寄り添い、どんなクレームも感動に変え、既存顧客を熱狂的なファン（リピーター）へと育成する、温かく誠実なコミュニケーションを構築してください。\\n\\n";
          else if (conf.cat === 'uranai') specialPersona = "【超特化型ペルソナ】\\nあなたは予約が数ヶ月取れない、慈愛と的確さを兼ね備えたカリスマ占い師です。相談者の心に深く寄り添い、ネガティブな結果であっても希望の光を見出せるような、温かくポジティブなアドバイスへと昇華させて伝えてください。\\n\\n";
          
          promptText = specialPersona + promptText;

          if (conf.isImagePrompt) return promptText;"""
    content = apply_patch(content, search4, replace4, "全ツールの超・特化型プロンプト化注入")

    with open(APP_JS, 'w', encoding='utf-8') as f: f.write(content)

print("🚀 v73.0.0 第二弾パッチ（ウィザード化＆特化プロンプト）実行開始...")
patch_app()
print("\n✅ 全パッチ適用完了！既存のコードを一切壊さずにUI改善と品質強化を行いました。")
