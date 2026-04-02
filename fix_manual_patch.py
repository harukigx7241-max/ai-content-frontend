import re
import sys

filepath = '/root/ai-content-pro/static/js/app.js'
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print(f"❌ {filepath} が見つかりません。")
    sys.exit(1)

# マニュアルモーダル全体を正規表現で書き換える（動的リスト生成対応版）
new_manual_modal = r"""    const ManualModal = ({ onClose }) => {
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
                            return div({ key: c.id, className: 'space-y-3' },
                                h5({ className: 'font-black text-white text-base mb-3 border-b border-white/10 pb-2' }, c.name),
                                div({ className: 'grid grid-cols-1 md:grid-cols-2 gap-3' },
                                    catTools.map(tId => {
                                        const t = TOOLS[tId];
                                        return div({ key: tId, className: 'p-4 bg-white/5 rounded-xl border border-white/10 hover:border-brand/30 transition flex flex-col h-full group' },
                                            h6({ className: 'font-bold text-white text-sm mb-2 flex items-center gap-2' }, span({className: 'text-lg group-hover:scale-125 transition-transform'}, t.icon), t.name),
                                            p({ className: 'text-[11px] text-slate-300 font-bold mb-3 flex-1' }, t.desc),
                                            t.help && p({ className: 'text-[10px] text-slate-400 leading-relaxed bg-black/30 p-2 rounded-lg mt-auto border border-white/5' }, '💡 ', t.help)
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
    };"""

content = re.sub(
    r"const ManualModal = \(\{ onClose \}\) => \{.*?(?=const AdminDashboard = \(\{ user \}\) => \{)",
    new_manual_modal_code + "\n\n    ",
    content,
    flags=re.DOTALL
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("✅ app.js のマニュアルモーダルを超絶アップデートしました！")
