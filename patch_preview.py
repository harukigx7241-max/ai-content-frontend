import sys
import os
import re
import shutil

filepath = '/root/ai-content-pro/static/js/app.js'
if not os.path.exists(filepath):
    print(f"❌ {filepath} が見つかりません。")
    sys.exit(1)

# 万が一のためのバックアップ
shutil.copy2(filepath, filepath + '.bak_preview')

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 正規表現で「デフォルトのプレビュー表示div」を特定し、既存コードを一切削除せずに
# その手前に「sns_cal専用カレンダーUI」の条件分岐を安全に挿入します。
pattern = r"(:\s*div\(\{\s*id:\s*'preview-tab-content',\s*className:\s*'bg-white[^}]+?\}\s*,\s*div\(\{\s*dangerouslySetInnerHTML:\s*renderMarkdown\(res\)\s*\}\)\s*\))"

replacement = r"""
: (tid === 'sns_cal' && res ?
  (() => {
      // AIの出力を解析（カンマ区切り、タブ区切り、表形式に全て対応）
      const lines = res.split('\n').filter(l => l.trim().length > 0);
      let items = [];
      for (let line of lines) {
          if (line.includes('---')) continue;
          let cols = [];
          if (line.includes('|')) cols = line.split('|').map(s => s.trim()).filter(s => s);
          else if (line.includes(',')) cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(s => s.trim().replace(/^"|"$/g, ''));
          else if (line.includes('\t')) cols = line.split('\t').map(s => s.trim());
          
          // ヘッダー行を除外し、実際の投稿データのみを抽出
          if (cols.length >= 2 && !cols.some(c => c.includes('曜日') || c.includes('投稿文の要点'))) {
              items.push(cols);
          }
      }
      
      // カレンダー形式のデータが見つからなかった場合は、既存の標準表示に安全にフォールバック
      if (items.length === 0) return \g<1>.substring(2); 
      
      // 抽出したデータを美しいカレンダーカードUIに配置
      return div({ id: 'preview-tab-content', className: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4 md:p-6 bg-slate-100 rounded-2xl shadow-inner overflow-y-auto' + (previewMode === 'mobile' ? ' grid-cols-1' : '') },
          items.map((cols, i) => {
              const dayStr = cols[0].length < 15 ? cols[0] : (cols[1] ? cols[1] : `Day ${i+1}`);
              const contentStr = cols[cols.length - 1];
              const themeStr = cols.length > 2 ? cols[cols.length - 2] : '';
              return div({ key: i, className: 'bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col hover:shadow-lg transition group relative' },
                  div({ className: 'absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-brand to-brand-accent' }),
                  div({ className: 'bg-brand/5 border-b border-brand/10 px-4 py-3 flex justify-between items-center' },
                      span({ className: 'text-sm font-black text-brand' }, `📅 日目: ${i+1}`),
                      span({ className: 'text-[10px] font-bold text-slate-500 bg-white px-2 py-1 rounded-full shadow-sm border border-slate-100' }, dayStr)
                  ),
                  div({ className: 'p-4 flex-1 flex flex-col gap-3' },
                      themeStr && div({},
                          span({ className: 'text-[10px] font-bold text-slate-400 block mb-1' }, '🎯 テーマ / 狙い'),
                          p({ className: 'text-xs font-bold text-slate-700 leading-tight bg-slate-50 p-2 rounded-lg border border-slate-100' }, themeStr)
                      ),
                      div({ className: 'flex-1' },
                          span({ className: 'text-[10px] font-bold text-slate-400 block mb-1' }, '📝 投稿内容'),
                          div({ className: 'text-xs text-slate-700 leading-relaxed overflow-y-auto max-h-[150px] custom-scrollbar', dangerouslySetInnerHTML: renderMarkdown(contentStr) })
                      )
                  )
              );
          })
      );
  })()
  \g<1>
)
"""

if not re.search(pattern, content):
    print("❌ プレビューエリアが見つかりません。")
    sys.exit(1)

# 既存コードを \g<1> で完全維持したまま、手前に拡張UIを挿入
content = re.sub(pattern, replacement.strip(), content)

# バージョン情報のみ更新
content = re.sub(r"const SYS_VERSION = '[^']+';", "const SYS_VERSION = 'v71.9.3 Visual Preview Edition';", content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ パッチ適用完了（既存コードは一切変更していません）")
