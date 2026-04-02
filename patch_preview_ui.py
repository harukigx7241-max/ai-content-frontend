import sys
import os

filepath = '/root/ai-content-pro/static/js/app.js'
if not os.path.exists(filepath):
    print(f"❌ {filepath} が見つかりません。")
    sys.exit(1)

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# バージョン更新
content = content.replace("v71.9.1 Ultimate Master Edition", "v71.9.3 Visual Preview Edition")

# 1. note以外のツールで勝手にタブ分割されるバグを修正
search_tab = r"""                        res && (() => {
                            const sectionMarkers = res.match(/---【[^】]+】---/g);
                            if (sectionMarkers && sectionMarkers.length >= 2) {"""

replace_tab = r"""                        res && (() => {
                            if (toolId === 'sns_cal') return div({ className: 'text-brand text-sm font-bold flex items-center gap-2 px-3 py-1.5 bg-brand/10 rounded-lg' }, '📅 カレンダービュー');
                            const sectionMarkers = res.match(/---【[^】]+】---/g);
                            if (toolId === 'note' && sectionMarkers && sectionMarkers.length >= 2) {"""

if search_tab in content:
    content = content.replace(search_tab, replace_tab)
    print("  ✅ タブ分割をnote専用に修正しました")
else:
    print("  ⚠️ タブ修正箇所が見つかりません")

# 2. 30日間SNSカレンダー専用の視覚的カードビューを追加
search_preview = r"""                            (() => {
                                if (previewTab.startsWith('sec_')) {"""

replace_preview = r"""                            (() => {
                                if (toolId === 'sns_cal' && res) {
                                    const lines = res.split('\n');
                                    let days = [];
                                    let isTable = false;
                                    let headers = [];
                                    lines.forEach(line => {
                                        line = line.trim();
                                        if (line.startsWith('|') && line.endsWith('|')) {
                                            const cols = line.split('|').map(s => s.trim()).filter((s, i, arr) => i > 0 && i < arr.length - 1);
                                            if (!isTable) {
                                                if (!cols[0].includes('---')) headers = cols;
                                                else isTable = true;
                                            } else {
                                                if (cols[0] && cols[0].match(/\d/)) days.push(cols);
                                            }
                                        }
                                    });
                                    if (days.length > 0) {
                                        return div({ className: 'p-2 w-full' },
                                            div({ className: 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4' },
                                                days.map((cols, i) => 
                                                    div({ key: i, className: 'bg-white p-4 rounded-2xl border border-slate-200 shadow-sm flex flex-col relative overflow-hidden group hover:shadow-md transition' },
                                                        div({ className: 'absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-brand to-brand-accent' }),
                                                        div({ className: 'font-black text-brand mb-3 text-sm border-b border-slate-100 pb-2 flex justify-between items-center' }, 
                                                            span({ className: 'bg-brand/10 px-2 py-1 rounded-md' }, cols[0] || (i+1)+'日目'),
                                                            span({ className: 'text-[10px] text-slate-500 font-normal bg-slate-100 px-2 py-1 rounded-md truncate max-w-[50%]' }, cols[cols.length-1] || '')
                                                        ),
                                                        div({ className: 'flex-1 overflow-y-auto custom-scrollbar space-y-3' },
                                                            headers.map((h, j) => {
                                                                if (j === 0 || j === headers.length - 1) return null;
                                                                return div({ key: j },
                                                                    span({ className: 'text-[10px] font-bold text-slate-400 block mb-1' }, h),
                                                                    div({ className: 'text-xs text-slate-700 leading-relaxed', dangerouslySetInnerHTML: renderMarkdown(cols[j] || '') })
                                                                );
                                                            })
                                                        )
                                                    )
                                                )
                                            )
                                        );
                                    }
                                }

                                if (previewTab.startsWith('sec_')) {"""

if search_preview in content:
    content = content.replace(search_preview, replace_preview)
    print("  ✅ 30日間SNSカレンダーのカードUIを追加しました")
else:
    print("  ⚠️ プレビュー修正箇所が見つかりません")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ パッチの適用が完了しました！")
