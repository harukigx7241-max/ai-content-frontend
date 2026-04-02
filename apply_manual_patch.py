#!/usr/bin/env python3
import sys
import os
import shutil
import re

def apply_patch(content, search, replace, label):
    if search in content:
        content = content.replace(search, replace, 1)
        print(f"  ✅ {label}")
        return content
    else:
        print(f"  ⚠️ パッチ適用失敗（該当箇所が見つかりません）: {label}")
        return content

def main():
    filepath = '/root/ai-content-pro/static/js/app.js'
    if not os.path.exists(filepath):
        print(f"❌ ファイルが見つかりません: {filepath}")
        sys.exit(1)
    
    backup = filepath + '.bak_manual'
    shutil.copy2(filepath, backup)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print("\n🔧 app.js パッチ適用開始 (総合マニュアル機能の追加)\n")

    # PATCH 1: ManualModalコンポーネントの追加
    search_admin = "    const AdminDashboard = ({ user }) => {"
    
    manual_modal_code = r"""    // ================================================================
    // 総合マニュアル (初心者向け)
    // ================================================================
    const ManualModal = ({ onClose }) => {
        const [activeTab, setActiveTab] = useState('basic');
        return div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4 animate-in' },
            div({ className: 'glass-panel rounded-3xl max-w-4xl w-full p-6 md:p-8 relative flex flex-col max-h-[90vh]' },
                button({ onClick: onClose, className: 'absolute top-5 right-5 text-slate-400 hover:text-white text-xl font-bold transition' }, '\u2715'),
                h3({ className: 'text-2xl font-black text-white mb-6 pb-4 border-b border-white/10 flex items-center gap-2' }, '📖 AICP Pro 総合マニュアル'),
                div({ className: 'flex gap-2 mb-6 border-b border-white/10 pb-2 overflow-x-auto hide-scrollbar' },
                    [{id:'basic', l:'🔰 基本の使い方'}, {id:'magic', l:'✨ 神丸投げ・自動補完'}, {id:'persona', l:'🎭 マイキャラ設定'}, {id:'tools', l:'🛠 各ツールの解説'}].map(t => 
                        button({ key: t.id, onClick: () => setActiveTab(t.id), className: 'px-4 py-2 rounded-full text-xs font-bold transition whitespace-nowrap ' + (activeTab === t.id ? 'bg-brand text-white' : 'text-slate-400 hover:bg-white/10') }, t.l)
                    )
                ),
                div({ className: 'overflow-y-auto flex-1 pr-4 hide-scrollbar text-slate-300 space-y-6 leading-relaxed text-sm' },
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
                    activeTab === 'tools' && div({ className: 'animate-in space-y-6' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '🛠 カテゴリ別 ツール解説'),
                        div({ className: 'grid grid-cols-1 md:grid-cols-2 gap-4' },
                            div({ className: 'p-4 bg-white/5 rounded-xl border border-white/10 hover:border-brand-light/50 transition' }, 
                                h5({ className: 'font-black text-white mb-2 flex items-center gap-2' }, '🔥 オメガ特級ツール'), 
                                p({ className: 'text-xs text-slate-400 leading-relaxed' }, 'ローンチ設計、VSL台本、30日間SNSカレンダーなど、大規模なマーケティング施策を一撃で構築する最強のツール群です。')),
                            div({ className: 'p-4 bg-white/5 rounded-xl border border-white/10 hover:border-brand-light/50 transition' }, 
                                h5({ className: 'font-black text-white mb-2 flex items-center gap-2' }, '📝 コンテンツ作成 ＆ 販売'), 
                                p({ className: 'text-xs text-slate-400 leading-relaxed' }, '売れるnote有料記事の全自動執筆、高単価商品のLP作成、バックエンド商品の企画など、直接的な収益化に直結します。')),
                            div({ className: 'p-4 bg-white/5 rounded-xl border border-white/10 hover:border-brand-light/50 transition' }, 
                                h5({ className: 'font-black text-white mb-2 flex items-center gap-2' }, '💼 クラウドワークス・仕事完遂'), 
                                p({ className: 'text-xs text-slate-400 leading-relaxed' }, '案件の獲得率を上げる提案文作成や、角を立てない単価交渉メッセージなど、フリーランスの営業・納品活動をサポートします。')),
                            div({ className: 'p-4 bg-white/5 rounded-xl border border-white/10 hover:border-brand-light/50 transition' }, 
                                h5({ className: 'font-black text-white mb-2 flex items-center gap-2' }, '🚀 集客 ＆ SNSアナリティクス'), 
                                p({ className: 'text-xs text-slate-400 leading-relaxed' }, 'X(Twitter)やInstagram等のバズるアカウント設計、ショート動画台本、SNSアナリティクスの画像解析による改善提案を行います。')),
                            div({ className: 'p-4 bg-white/5 rounded-xl border border-white/10 hover:border-brand-light/50 transition' }, 
                                h5({ className: 'font-black text-white mb-2 flex items-center gap-2' }, '💬 ファン化 ＆ セールス自動化'), 
                                p({ className: 'text-xs text-slate-400 leading-relaxed' }, 'LINE登録を促す無料プレゼント企画、ステップ配信シナリオ、顧客からのクレームに対する神返信などを作成します。'))
                        )
                    )
                ),
                button({ onClick: onClose, className: 'w-full btn-gradient py-4 rounded-xl font-black mt-6 shadow-xl' }, 'マニュアルを閉じる')
            )
        );
    };

    const AdminDashboard = ({ user }) => {"""

    content = apply_patch(content, search_admin, manual_modal_code, "ManualModalコンポーネントの追加")

    # PATCH 2: MainApp のステートに showManual を追加
    search_mainapp_state = "const [showSettings, setShowSettings] = useState(false);"
    replace_mainapp_state = "const [showSettings, setShowSettings] = useState(false);\n      const [showManual, setShowManual] = useState(false);"
    content = apply_patch(content, search_mainapp_state, replace_mainapp_state, "MainAppのstateにshowManual追加")

    # PATCH 3: Sidebar にマニュアルボタンを追加
    search_sidebar_btn = r"button({ onClick: () => setShowSettings(true), className: 'w-full bg-white/5 hover:bg-white/10 p-3 rounded-lg text-sm font-bold text-slate-300 flex items-center gap-3 transition' }, '\u2699\uFE0F 個人設定'),"
    replace_sidebar_btn = r"button({ onClick: () => setShowManual(true), className: 'w-full bg-brand/10 hover:bg-brand/20 p-3 rounded-lg text-sm font-bold text-brand-light flex items-center gap-3 transition border border-brand/30' }, '📖 総合マニュアル')," + "\n              " + search_sidebar_btn
    content = apply_patch(content, search_sidebar_btn, replace_sidebar_btn, "Sidebarにマニュアルボタン追加")

    # PATCH 4: MainApp の戻り値に ManualModal を追加
    search_mainapp_return = "el(Sidebar), showSettings && el(UserSettingModal, { user: props.user, onClose: () => setShowSettings(false) }),"
    replace_mainapp_return = "el(Sidebar), showSettings && el(UserSettingModal, { user: props.user, onClose: () => setShowSettings(false) }),\n        showManual && el(ManualModal, { onClose: () => setShowManual(false) }),"
    content = apply_patch(content, search_mainapp_return, replace_mainapp_return, "MainAppの戻り値にManualModal追加")

    # PATCH 5: バージョン表記の更新
    content = re.sub(r"const SYS_VERSION = '[^']+';", "const SYS_VERSION = 'v71.7.0 Ultimate Master Edition';", content)
    print("  ✅ SYS_VERSION更新(v71.7.0)")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ app.js 総合マニュアル追加パッチ適用完了！")

if __name__ == '__main__':
    main()
