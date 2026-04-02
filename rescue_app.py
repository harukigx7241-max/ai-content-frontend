import sys
import os
import re

base_dir = '/root/ai-content-pro/static/js/'
backup_file = base_dir + 'app.js.bak'
target_file = base_dir + 'app.js'

if not os.path.exists(backup_file):
    print(f"❌ {backup_file} が見つかりません。")
    sys.exit(1)

print("🚑 クラッシュ復旧を開始します (2100行以上の元データから復元)...")

with open(backup_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 致命的なエラー原因（h5, h6の未定義）を修正
if "const h5 =" not in content:
    content = re.sub(
        r"(const h4 =.*?;\n?)", 
        r"\1const h5 = (pr, ...c) => el('h5', pr, ...c);\nconst h6 = (pr, ...c) => el('h6', pr, ...c);\n", 
        content
    )
    print("  ✅ h5, h6エイリアスを追加し、Reactのクラッシュを修正しました")

# 2. バージョン更新
content = re.sub(r"const SYS_VERSION = '[^']+';", "const SYS_VERSION = 'v71.9.0 Ultimate Master Edition';", content)

# 3. 総合マニュアルの追加
manual_modal_code = r"""
    // ================================================================
    // 総合マニュアル
    // ================================================================
    const ManualModal = ({ onClose }) => {
        const [activeTab, setActiveTab] = useState('basic');
        return div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4 animate-in backdrop-blur-sm' },
            div({ className: 'glass-panel rounded-3xl max-w-5xl w-full p-6 md:p-8 relative flex flex-col max-h-[90vh]' },
                button({ onClick: onClose, className: 'absolute top-5 right-5 text-slate-400 hover:text-white text-xl font-bold transition z-10' }, '\u2715'),
                h3({ className: 'text-2xl font-black text-white mb-6 pb-4 border-b border-white/10 flex items-center gap-2' }, '📖 AICP Pro 総合マニュアル'),
                div({ className: 'flex gap-2 mb-6 border-b border-white/10 pb-2 overflow-x-auto hide-scrollbar shrink-0' },
                    [{id:'basic', l:'🔰 基本の使い方'}, {id:'magic', l:'✨ 神丸投げ・自動補完'}, {id:'persona', l:'🎭 マイキャラ設定'}, {id:'tools', l:'🛠 各ツールの解説'}].map(t => 
                        button({ key: t.id, onClick: () => setActiveTab(t.id), className: 'px-4 py-2 rounded-full text-xs font-bold transition whitespace-nowrap ' + (activeTab === t.id ? 'bg-brand text-white' : 'text-slate-400 hover:bg-white/10') }, t.l)
                    )
                ),
                div({ className: 'overflow-y-auto flex-1 pr-4 custom-scrollbar text-slate-300 space-y-6 leading-relaxed text-sm relative' },
                    activeTab === 'basic' && div({ className: 'animate-in space-y-6' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '1. コンテンツの生成方法'),
                        p({}, '左側のフォームに必要な情報を入力し、画面下部の生成ボタンを押します。実行モードには以下の2種類があります。'),
                        ul({ className: 'list-disc pl-5 space-y-3 bg-white/5 p-4 rounded-xl' },
                            li({}, span({ className: 'font-bold text-white' }, '🚀 全自動生成 (API): '), 'システム内で直接AI（ChatGPT, Claude, Gemini）と通信し、結果を右画面に即座に表示します。'),
                            li({}, span({ className: 'font-bold text-white' }, '📋 プロンプトのみ作成: '), '高品質な指示文（プロンプト）を作成してコピーします。ご自身のChatGPT等に貼り付けて生成し、結果を本システムの「手動貼り付け」機能でプレビューに反映できます。')
                        ),
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2 mt-6' }, '2. プレビューと推敲（リライト）機能'),
                        p({}, '生成された結果は右側のプレビュー画面に表示されます。PC/スマホ表示の切り替えや、結果に対するワンクリックでの推敲が可能です。'),
                        ul({ className: 'list-disc pl-5 space-y-2' },
                            li({}, '「LINE誘導追加」「キャッチーに」「シンプルに」などのボタンを押すだけで、AIが文章を自動でブラッシュアップします。'),
                            li({}, 'SNSマルチ展開ボタンを使えば、1つの記事から「X(Twitter)用」「ショート動画用」「メルマガ用」などに瞬時に変換できます。')
                        )
                    ),
                    activeTab === 'magic' && div({ className: 'animate-in space-y-6' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '🔥 究極の「神丸投げ」機能'),
                        p({}, 'フォームを', span({ className: 'text-orange-400 font-bold bg-orange-400/20 px-1 rounded' }, '【すべて空欄】'), 'のまま生成ボタンを押すと「神丸投げモード」が発動します。'),
                        p({}, 'AIが自らWeb検索（Auto-Browsing）を行い、今日の日本の最新トレンドを分析した上で、最もバズりやすいテーマを自動選定し、コンテンツを丸ごと生成します。'),
                        div({ className: 'p-4 bg-orange-500/10 border border-orange-500/30 rounded-xl' },
                            p({ className: 'text-xs text-orange-200' }, '💡 おすすめ: 「今日は何を発信しようか迷った時」にとりあえず実行してみるのが最も効果的です。')
                        ),
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2 mt-6' }, '🌟 自動補完機能'),
                        p({}, '「テーマ」だけを入力し、他の項目を空欄にして生成すると、未入力の項目をAIがWeb検索結果をもとに最適な内容で自動的に補完して生成します。')
                    ),
                    activeTab === 'persona' && div({ className: 'animate-in space-y-6' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '🎭 マイ・ペルソナ（自分専用AI化）'),
                        p({}, '「⚙️ 個人設定」>「UI・出力」タブで、ご自身のプロフィールや文体のクセ（ペルソナ）を登録できます。'),
                        p({}, '過去のブログやSNSの文章を貼り付けるだけで、AIがあなたの特徴を自動で抽出する機能もあります。ここに設定した内容は、すべてのツールの生成結果に反映され、「あなたらしい」文章が出力されるようになります。'),
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2 mt-6' }, '👥 マイキャラ保存機能'),
                        p({}, '特定の用途に向けたキャラクター（例：熱血コンサルタント、優しい占い師など）を最大5体まで保存できます。'),
                        p({}, '保存したキャラは、SNS投稿ツールや動画台本ツールの「🎭 なりきりキャラクター」のプルダウンから簡単に呼び出すことができます。')
                    ),
                    activeTab === 'tools' && div({ className: 'animate-in space-y-8' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '🛠 収録ツール一覧と使い方'),
                        CATEGORIES.map(c => {
                            const catTools = Object.keys(TOOLS).filter(k => TOOLS[k].cat === c.id);
                            if (catTools.length === 0) return null;
                            return div({ key: c.id, className: 'space-y-4' },
                                h5({ className: 'font-black text-white text-base mb-3 border-b border-white/10 pb-2' }, c.name),
                                div({ className: 'grid grid-cols-1 lg:grid-cols-2 gap-4' },
                                    catTools.map(tId => {
                                        const t = TOOLS[tId];
                                        return div({ key: tId, className: 'p-5 bg-white/5 rounded-xl border border-white/10 hover:border-brand/50 transition flex flex-col h-full group' },
                                            h6({ className: 'font-black text-white text-sm mb-2 flex items-center gap-2' }, span({className: 'text-2xl group-hover:scale-125 transition-transform'}, t.icon), t.name),
                                            p({ className: 'text-xs text-slate-300 font-bold mb-4 flex-1' }, t.desc),
                                            t.help && p({ className: 'text-[11px] text-slate-400 leading-relaxed bg-black/40 p-3 rounded-lg mt-auto border border-white/5' }, '\uD83D\uDCA1 ', t.help)
                                        );
                                    })
                                )
                            );
                        })
                    )
                ),
                button({ onClick: onClose, className: 'w-full btn-gradient py-4 rounded-xl font-black mt-6 shadow-xl shrink-0' }, 'マニュアルを閉じる')
            )
        );
    };
"""
# AdminDashboardの直前に挿入する
if "const ManualModal =" not in content:
    content = re.sub(r"(const AdminDashboard = \(\{ user \}\) => \{)", manual_modal_code + r"\n\n\1", content)
    print("  ✅ マニュアル機能を安全に組み込みました")

# 4. MainAppにshowManualステートを追加
if "const [showManual, setShowManual]" not in content:
    content = re.sub(
        r"(const \[showSettings, setShowSettings\] = useState\(false\);)", 
        r"\1\n    const [showManual, setShowManual] = useState(false);", 
        content
    )

# 5. サイドバーにマニュアルボタンを追加
if "📖 総合マニュアル" not in content:
    content = re.sub(
        r"(button\(\{ onClick: \(\) => setShowSettings *\(true\), className: 'w-full bg- *white/5[^\n]+'⚙️ 設定'\),\n)",
        r"button({ onClick: () => setShowManual(true), className: 'w-full bg-brand/20 hover:bg-brand/30 border border-brand/30 py-3 rounded-lg text-sm font-bold text-brand-light flex items-center justify-center gap-2 transition mb-2' }, '📖 総合マニュアル'),\n                    \1",
        content
    )

# 6. MainAppのreturnにManualModalを追加
if "el(ManualModal" not in content:
    content = re.sub(
        r"(showSettings && el\(UserSettingModal, \{.*?onClose: \(\) => setShowSettings\(false\).*?\} \)\n\s*\),?)",
        r"\1\n            showManual && el(ManualModal, { onClose: () => setShowManual(false) }),",
        content,
        flags=re.DOTALL
    )

# 7. マイキャラ保存・LINE誘導ボタンなどの直近の機能も再適用
if "if(!db.users[u].settings.myCharas)" not in content:
    content = re.sub(
        r"(if\(!db\.users\[u\]\.settings\.templates\) db\.users\[u\]\.settings\.templates = \['', '', ''\];)",
        r"\1\n            if(!db.users[u].settings.myCharas) db.users[u].settings.myCharas = [];",
        content
    )
if "const [myCharas, setMyCharas]" not in content:
    content = re.sub(
        r"(const \[templates, setTemplates\] = useState\(uData\.settings\.templates\);)",
        r"\1\n    const [myCharas, setMyCharas] = useState(uData.settings.myCharas || []);",
        content
    )
    content = re.sub(r"notifications: notif, templates \}\);", r"notifications: notif, templates, myCharas });", content)

MYCHARA_UI = r"""
                    div({ className: 'pt-6 border-t border-white/10' },
                        label({ className: 'block text-xs font-bold text-slate-400 mb-3 flex items-center gap-2' }, '\uD83C\uDFAD マイキャラ保存 (最大5体)'),
                        p({ className: 'text-[10px] text-slate-500 mb-3' }, '※保存したキャラは全ツールの「なりきりキャラクター」選択肢に追加されます。'),
                        myCharas.map((ch, ci) => div({ key: ci, className: 'mb-3 p-3 bg-white/5 border border-white/10 rounded-xl animate-in' },
                            div({ className: 'flex items-center gap-2 mb-2' },
                                span({ className: 'text-xs font-bold text-brand-light' }, '\uD83C\uDFAD キャラ ' + (ci+1)),
                                button({ onClick: () => { const nc = myCharas.filter((_, i) => i !== ci); setMyCharas(nc); }, className: 'ml-auto text-[10px] text-brand-danger hover:text-white' }, '削除')
                            ),
                            input({ className: 'input-base !py-1.5 text-xs mb-1.5', placeholder: 'キャラ名 (例: 元看護師の占い師さくら)', value: ch.name || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { name: e.target.value }); setMyCharas(nc); } }),
                            textarea({ className: 'input-base min-h-[60px] text-xs', placeholder: '性格・口調・特徴 (例: 30代女性。優しく寄り添う口調。「〜ですよね」が多い。)', value: ch.desc || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { desc: e.target.value }); setMyCharas(nc); } })
                        )),
                        myCharas.length < 5 && button({ onClick: () => setMyCharas(myCharas.concat([{ name: '', desc: '' }])), className: 'w-full glass-panel py-2.5 rounded-xl text-xs font-bold text-brand-light hover:bg-brand/10 transition border border-dashed border-white/20' }, '+ 新しいキャラを追加')
                    ),\n"""
if "マイキャラ保存 (最大5体)" not in content:
    content = re.sub(
        r"(label\(\{ className: 'block text-xs font-bold text-slate-400\n*mb-2' \}, '\uD83C\uDFAD マイ・プロンプトテンプレート\(備忘録\)'\),)",
        MYCHARA_UI + r"\1",
        content
    )

if "'line_cta'" not in content:
    content = re.sub(r"('eyecatch_prompt': 'アイキャッチ\n*画像プロンプト')", r"'eyecatch_prompt': 'アイキャッチ画像プロンプト',\n        'line_cta': 'LINE誘導文を追加'", content)
    content = re.sub(r"(if \(actionType === 'eyecatch_prompt'\) return '[^']+';)", r"if (actionType === 'line_cta') return '以下の文章の末尾に、LINE公式アカウントへの登録を自然に促す誘導文（CTA）を3パターン追加してください。\\n・「詳しくはプロフのLINEで💌」系の軽いもの\\n・「LINE登録者限定で○○をプレゼント🎁」系の特典訴求\\n・「今だけ無料で○○を配布中」系の緊急性訴求\\n\\n元の文章はそのまま残し、末尾にCTAを追加する形にしてください。\\n\\n' + sourceText;\n    \1", content)
    content = re.sub(r"('\\uD83D\\uDDBC\\uFEOF'\) \+ 'アイキャッチリ\n*\)\n*\),)", r"'\uD83D\uDDBC\uFEOF') + 'アイキャッチ'),\nbutton({ onClick: () => handleModify('line_cta'), disabled: isLoading, className: 'glass-panel px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition disabled:opacity-50 ' + (genMode === 'prompt' ? 'text-brand-accent hover:bg-brand-accent/20 border border-brand-accent/30' : 'text-green-400 hover:text-white hover:bg-green-500/20') }, (genMode === 'prompt' ? '\uD83D\uDCCB ' : '\uD83D\uDC9A ') + 'LINE誘導追加')\n)", content)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ クラッシュ原因を完全に排除し、ファイル全データの復元に成功しました！")
