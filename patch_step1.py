import re
import os

filepath = '/root/ai-content-pro/static/js/app.js'
if not os.path.exists(filepath):
    print("app.js が見つかりません。")
    exit()

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 変更箇所1: ペルソナプロンプトの構築ロジック
pattern1 = r"let\s+personaText\s*=\s*settings\s*&&\s*settings\.persona\s*\?\s*'\\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\\n'\s*\+\s*settings\.persona\s*\+\s*'\\n'\s*:\s*'';"
repl1 = """let personaText = '';
      if (settings) {
          let pLines = [];
          if (settings.persona_base) pLines.push('基本性格: ' + settings.persona_base);
          if (settings.persona_first) pLines.push('一人称: ' + settings.persona_first);
          if (settings.persona) pLines.push('詳細設定: ' + settings.persona);
          if (pLines.length > 0) personaText = '\\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\\n' + pLines.join('\\n') + '\\n';
      }"""
content, c1 = re.subn(pattern1, repl1, content, count=1)

# 変更箇所2: マイペルソナのウィザードUI化
pattern2 = r"textarea\(\{\s*className:\s*'input-base[^']+',\s*placeholder:\s*'例:\s*私はプロのWebマーケターです[^']+',\s*value:\s*persona,\s*onChange:\s*e\s*=>\s*setPersona\(e\.target\.value\)\s*\}\)"
repl2 = """div({ className: 'p-4 bg-white/5 border border-white/10 rounded-xl mb-4' },
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, 'ベースの性格・トーン'),
                                select({ className: 'input-base !py-2 text-xs mb-3', value: uData.settings.persona_base || '', onChange: e => { const val=e.target.value; const ndb=AppDB.get(); ndb.users[user].settings.persona_base=val; AppDB.save(ndb); setDb(ndb); } },
                                    option({value:''}, '指定なし（標準）'), option({value:'プロフェッショナルで論理的'}, 'プロフェッショナルで論理的'), option({value:'優しく寄り添う共感型'}, '優しく寄り添う共感型'), option({value:'熱血で情熱的なリーダー'}, '熱血で情熱的なリーダー'), option({value:'ユーモア溢れる親友'}, 'ユーモア溢れる親友')
                                ),
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, '一人称'),
                                input({ className: 'input-base !py-2 text-xs mb-3', placeholder: '例: 私、僕、俺', value: uData.settings.persona_first || '', onChange: e => { const val=e.target.value; const ndb=AppDB.get(); ndb.users[user].settings.persona_first=val; AppDB.save(ndb); setDb(ndb); } }),
                                label({ className: 'block text-[10px] text-slate-400 mb-1' }, '自由記述（詳細な設定・口癖など）'),
                                textarea({ className: 'input-base min-h-[80px] text-xs', placeholder: '例: 語尾に「〜ですよね！」をよく使う。専門用語は避ける。', value: persona, onChange: e => setPersona(e.target.value) })
                            )"""
content, c2 = re.subn(pattern2, repl2, content, count=1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"パッチ1(ペルソナ構築ロジック): {'✅ 成功' if c1 > 0 else '⚠️ スキップ'}")
print(f"パッチ2(ウィザードUI): {'✅ 成功' if c2 > 0 else '⚠️ スキップ'}")
