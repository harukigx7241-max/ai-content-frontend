import sys
import os
import re
import shutil

filepath = '/root/ai-content-pro/static/js/app.js'
if not os.path.exists(filepath):
    print(f"❌ {filepath} が見つかりません。")
    sys.exit(1)

# 万が一のためのバックアップ
shutil.copy2(filepath, filepath + '.bak_preview3')

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# -------------------------------------------------------------
# 【標的1】プレビューのヘッダー部分（既存コードを維持して前に挿入）
# -------------------------------------------------------------
header_pattern = r"(tid !== 'note' && res && \(\(\) => \{)"
if re.search(header_pattern, content):
    content = re.sub(
        header_pattern, 
        r"tid === 'sns_cal' && res ? div({ className: 'text-brand text-sm font-bold flex items-center gap-2 px-3 py-1.5 bg-brand/10 rounded-lg' }, '📅 カレンダービュー') : tid !== 'sns_cal' && \1", 
        content
    )
    print("  ✅ ヘッダー部分のパッチ適用成功")

# -------------------------------------------------------------
# 【標的2】プレビューのコンテンツ部分（既存のnote用タブの前に挿入）
# -------------------------------------------------------------
content_pattern = r"(tid === 'note'\s*\?\s*\(\(\) => \{)"
if re.search(content_pattern, content):
    calendar_ui = r"""tid === 'sns_cal' ? (() => {
                                        const lines = res.split('\n').filter(l => l.trim().length > 0);
                                        let items = [];
                                        for (let line of lines) {
                                            if (line.includes('---')) continue;
                                            let cols = [];
                                            if (line.includes('|')) cols = line.split('|').map(s => s.trim()).filter(s => s);
                                            else if (line.includes(',')) cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(s => s.trim().replace(/^"|"$/g, ''));
                                            else if (line.includes('\t')) cols = line.split('\t').map(s => s.trim());
                                            if (cols.length >= 2 && !cols.some(c => c.includes('曜日') || c.includes('投稿文の要点'))) items.push(cols);
                                        }
                                        if (items.length === 0) return div({ className: 'preview-content text-black' }, div({ dangerouslySetInnerHTML: renderMarkdown(res) })); 
                                        return div({ id: 'preview-tab-content', className: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-4 md:p-6 bg-slate-100 rounded-2xl shadow-inner overflow-y-auto custom-scrollbar' + (previewMode === 'mobile' ? ' grid-cols-1' : '') },
                                            items.map((cols, i) => {
                                                const dayStr = cols[0].length < 15 ? cols[0] : (cols[1] ? cols[1] : `Day ${i+1}`);
                                                const contentStr = cols[cols.length - 1];
                                                const themeStr = cols.length > 2 ? cols[cols.length - 2] : '';
                                                return div({ key: i, className: 'bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col hover:shadow-lg transition overflow-hidden relative' },
                                                    div({ className: 'absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-brand to-brand-accent' }),
                                                    div({ className: 'bg-brand/5 border-b border-brand/10 px-4 py-2 flex justify-between items-center' },
                                                        span({ className: 'text-sm font-black text-brand' }, `📅 ${i+1}日目`),
                                                        span({ className: 'text-[10px] font-bold text-slate-500 bg-white px-2 py-1 rounded-full shadow-sm' }, dayStr)
                                                    ),
                                                    div({ className: 'p-4 flex-1 flex flex-col gap-3' },
                                                        themeStr && div({}, span({ className: 'text-[10px] font-bold text-slate-400 block' }, '🎯 テーマ'), p({ className: 'text-xs font-bold text-slate-700' }, themeStr)),
                                                        div({ className: 'flex-1' }, span({ className: 'text-[10px] font-bold text-slate-400 block' }, '📝 投稿内容'), div({ className: 'text-xs text-slate-700 leading-relaxed overflow-y-auto max-h-[150px] custom-scrollbar', dangerouslySetInnerHTML: renderMarkdown(contentStr) }))
                                                    )
                                                );
                                            })
                                        );
                                    })() :
                                    \1"""
    content = re.sub(content_pattern, calendar_ui, content)
    print("  ✅ プレビュー表示部分のパッチ適用成功")

# バージョン情報のみ更新
content = re.sub(r"const SYS_VERSION = '[^']+';", "const SYS_VERSION = 'v72.0.2 Visual Preview Edition';", content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ パッチ適用完了（既存のロジックは一切削除・変更していません）")
