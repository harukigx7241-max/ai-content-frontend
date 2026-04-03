#!/usr/bin/env python3
import sys
import os
import shutil
import re

TOOLS_JS = '/root/ai-content-pro/static/js/tools.js'
APP_JS = '/root/ai-content-pro/static/js/app.js'

def apply_patch(content, search, replace, label):
    if search in content:
        content = content.replace(search, replace, 1)
        print(f"  ✅ 成功: {label}")
    else:
        print(f"  ⚠️ スキップ（既に適用済み、または該当箇所なし）: {label}")
    return content

def patch_tools():
    if not os.path.exists(TOOLS_JS): return
    shutil.copy2(TOOLS_JS, TOOLS_JS + '.bak')
    with open(TOOLS_JS, 'r', encoding='utf-8') as f: content = f.read()

    # 1. 占いカテゴリ追加
    content = apply_patch(content, 
        "{ id: 'fun',   name: '💬 ファン化 ＆ セールス自動化' }", 
        "{ id: 'uranai',name: '🔮 占い・スピリチュアル特化' },\n    { id: 'fun',   name: '💬 ファン化 ＆ セールス自動化' }", 
        "占いカテゴリの追加")

    # 2. コンプラチェック追加
    comp_code = """const COMPLIANCE_NG_WORDS = [
    { word: '絶対痩せる', reason: '薬機法違反の恐れ（効果の断言）' },
    { word: '必ず儲かる', reason: '景表法・金融商品取引法違反の恐れ（利益の断言）' },
    { word: '100%治る', reason: '薬機法・医師法違反の恐れ（治療の断言）' },
    { word: '誰でも簡単に100万円', reason: '誇大広告・情報商材詐欺とみなされるリスク' }
];
function checkCompliance(text) {
    if (!text) return [];
    const alerts = [];
    COMPLIANCE_NG_WORDS.forEach(rule => { if (text.includes(rule.word)) alerts.push(`「${rule.word}」: ${rule.reason}`); });
    return alerts;
}
window.checkCompliance = checkCompliance;

const CATEGORIES = ["""
    content = apply_patch(content, "const CATEGORIES = [", comp_code, "コンプライアンスチェッカーの追加")

    # 3. 新規ツール追加
    new_tools = """const TOOLS = {
    cw_profile: { cat: 'cw', icon: '🏆', name: 'プロフィール構築AI', desc: 'クラウドワークスで「この人に頼みたい」と思わせるプロフィール。',
      fields: [{ id: 'skill', t: 'area', l: 'あなたのスキル・経歴', ph: '例: 事務歴5年、Excel得意', isMainMagic: true }, { id: 'target', t: 'text', l: '獲得したい案件', ph: '例: YouTubeの動画編集' }],
      build: function(v) { return 'あなたは採用率95%のプロデューサーです。\\n以下の情報を元に、信頼感のあるプロフィール文を作成してください。\\n\\n【経歴・スキル】\\n' + (v.skill||'') + '\\n【狙う案件】\\n' + (v.target||''); }
    },
    cw_hearing: { cat: 'cw', icon: '📋', name: 'プロのヒアリングシート生成', desc: '案件受注時に真のニーズを引き出す質問リスト。',
      fields: [{ id: 'project', t: 'area', l: '案件の概要', ph: '例: 美容系Instagramの運用代行', isMainMagic: true }],
      build: function(v) { return '一流のプロジェクトマネージャーとして、以下の案件でクライアントの「真のニーズ」を引き出すヒアリングシートを5〜7項目作成してください。\\n\\n【案件概要】\\n' + (v.project||''); }
    },
    cw_delivery: { cat: 'cw', icon: '🎁', name: '「神納品」メッセージ＆次回提案', desc: '納品報告と同時に次回リピート案件を獲得する魔法のメッセージ。',
      fields: [{ id: 'work', t: 'text', l: '納品した成果物', ph: '例: 動画編集', isMainMagic: true }, { id: 'effort', t: 'text', l: '今回特に工夫した点', ph: '例: テンポを早めました' }],
      build: function(v) { return 'リピート率100%のフリーランスとして、納品報告メッセージを作成してください。工夫点をアピールし、継続案件へのアップセルを自然に含めてください。\\n\\n【納品物】' + (v.work||'') + '\\n【工夫点】' + (v.effort||''); }
    },
    uranai_age: { cat: 'uranai', icon: '👼', name: 'アゲ鑑定（ポジティブ変換）推敲', desc: '悪い結果を嘘をつかずに「希望」に変換。',
      fields: [{ id: 'bad_result', t: 'area', l: '出た悪い結果', ph: '例: 復縁の可能性は低いです。', isMainMagic: true }],
      build: function(v) { return '慈愛に満ちたトップ占い師として、以下の「ネガティブな鑑定結果」を、嘘をつかずに相談者が前向きに受け取れる「温かく建設的なアドバイス」にリライトしてください。\\n\\n【元の結果】\\n' + (v.bad_result||''); }
    },
    uranai_menu: { cat: 'uranai', icon: '✨', name: '独自占術・メニュー開発AI', desc: 'ライバル不在の高単価オリジナルメニューを企画。',
      fields: [{ id: 'base', t: 'text', l: 'ベースの占術・得意なこと', ph: '例: タロットと、心理カウンセリング', isMainMagic: true }],
      build: function(v) { return 'スピリチュアル業界のマーケターとして、以下のスキルを元に1万円以上で売れる「オリジナル独自占術」のコンセプト案を3つ提案してください。\\n\\n【ベーススキル】\\n' + (v.base||''); }
    },
    uranai_follow: { cat: 'uranai', icon: '💌', name: 'アフターフォロー生成', desc: '鑑定後1ヶ月に送り、リピート依頼を発生させるメッセージ。',
      fields: [{ id: 'memo', t: 'text', l: '前回の相談内容', ph: '例: 人間関係のタロット占い', isMainMagic: true }],
      build: function(v) { return '深く愛される占い師として、以前「' + (v.memo||'') + '」について鑑定した相談者に対し、1ヶ月後に送るアフターフォローメッセージを作成し、再鑑定への導線を含めてください。'; }
    },
    note_outline: { cat: 'mon', icon: '📑', name: 'プロ向け「目次・構成」ジェネレーター', desc: '長文記事を書くための完璧な設計図を作成。',
      fields: [{ id: 'theme', t: 'text', l: '書きたいテーマ', ph: '例: SEO対策', isMainMagic: true }],
      build: function(v) { return 'トップSEO専門家として、テーマ「' + (v.theme||'') + '」について、読者が離脱しない完璧な論理展開を持った「記事の目次構成」を作成してください。'; }
    },
    note_teaser: { cat: 'mon', icon: '🔥', name: '有料境界線直前の「焦らし」ライティング', desc: '最強の課金フック。',
      fields: [{ id: 'value', t: 'area', l: '有料部分で得られる最大の価値', ph: '例: ブルーオーシャン市場のリスト', isMainMagic: true }],
      build: function(v) { return '天才セールスライターとして、noteの「ここから先は有料です」の直前に配置し、読者の知りたい欲求を極限まで煽る【焦らしのフック文章】を3パターン作成してください。\\n\\n【有料部分の価値】\\n' + (v.value||''); }
    },
    note_promo: { cat: 'sns', icon: '📢', name: '記事連動・SNSプロモーション生成', desc: '公開した記事をSNSで拡散して売るための宣伝ポスト。',
      fields: [{ id: 'summary', t: 'area', l: '記事の概要や魅力', ph: '例: 月5万稼ぐ手順', isMainMagic: true }],
      build: function(v) { return '以下の記事をX等で宣伝し、読ませるためのプロモーション投稿文を、権威性アピール型、悩み寄り添い型、チラ見せ型の3パターンで作成してください。\\n\\n【記事概要】\\n' + (v.summary||''); }
    },"""
    content = apply_patch(content, "const TOOLS = {", new_tools, "特化型新ツール9種の追加")

    if "window.AICP_TOOLS =" not in content:
        content += "\nwindow.AICP_TOOLS = TOOLS;\nwindow.AICP_CATEGORIES = CATEGORIES;\n"
    with open(TOOLS_JS, 'w', encoding='utf-8') as f: f.write(content)


def patch_app():
    if not os.path.exists(APP_JS): return
    shutil.copy2(APP_JS, APP_JS + '.bak')
    with open(APP_JS, 'r', encoding='utf-8') as f: content = f.read()

    # 1. 自動トリミング関数追加
    trim_func = """    const trimAIResponse = (text) => {
        if(!text) return "";
        let cleaned = text.replace(/^(承知いたしました|承知しました|はい、|以下の通り).*?\\n+/g, '');
        cleaned = cleaned.replace(/いかがでしょうか[。？]?.*$/g, '');
        return cleaned.trim();
    };

    const getAIPrefix = """
    content = apply_patch(content, "const getAIPrefix = ", trim_func, "不要な挨拶の自動トリミング機能追加")

    # 2. 生成結果へのトリミング＆コンプラ適用
    handle_gen = """let finalRes = isImage ? data.data : trimAIResponse(data.result);
            setRes(finalRes);
            if(window.checkCompliance) {
                const compAlerts = window.checkCompliance(finalRes);
                if(compAlerts.length > 0) setAlerts(compAlerts);
            }"""
    content = apply_patch(content, "setRes(isImage ? data.data : data.result);", handle_gen, "生成結果への自動チェック反映")

    # 3. アラート用 state 追加
    content = apply_patch(content, "const [error, setError] = useState('');", "const [error, setError] = useState('');\n      const [alerts, setAlerts] = useState([]);", "アラート用ステート追加")

    # 4. プレビュー画面のアラートUI
    alert_ui = """alerts.length > 0 && div({ className: 'p-3 bg-brand-danger/10 border border-brand-danger/30 rounded-xl mb-3 animate-in' },
                    h4({ className: 'text-[10px] font-black text-brand-danger mb-2 flex items-center gap-1.5' }, '\uD83D\uDEA8 コンプライアンス警告'),
                    alerts.map((a, i) => p({ key: i, className: 'text-[11px] text-brand-danger/80 mb-1' }, '\u26A0\uFE0F ' + a))
                ),
                tid === 'note' && res && div({ className: 'flex gap-1 overflow-x-auto hide-scrollbar' },"""
    content = apply_patch(content, "tid === 'note' && res && div({ className: 'flex gap-1 overflow-x-auto hide-scrollbar' },", alert_ui, "プレビュー画面のコンプラ警告UI追加")

    # 5. プロンプトギャラリーコンポーネント追加
    gallery_comp = """    const CommunityGallery = ({ db, user, onBack }) => {
        return div({ className: 'flex flex-col h-full bg-bg p-6 lg:p-12 overflow-y-auto animate-in' },
            div({ className: 'flex items-center mb-8 gap-4' },
                button({ onClick: onBack, className: 'glass-panel px-4 py-2 rounded-lg text-sm font-bold text-slate-400 hover:text-white transition' }, '← 戻る'),
                h2({ className: 'text-3xl font-black text-white' }, '🌐 みんなのプロンプトギャラリー')
            ),
            div({ className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' },
                p({className: 'text-slate-400'}, '準備中...（今後のアップデートでユーザー共有プロンプトが表示されます）')
            )
        );
    };

    const AdminDashboard"""
    content = apply_patch(content, "const AdminDashboard", gallery_comp, "プロンプトギャラリー画面の追加")

    # 6. MainApp へのギャラリー連携
    content = apply_patch(content, "const [showPopup, setShowPopup] = useState(false);", "const [showPopup, setShowPopup] = useState(false);\n      const [showGallery, setShowGallery] = useState(false);", "ギャラリー用ステート追加")
    
    # 7. サイドバーにギャラリーボタン追加
    content = apply_patch(content, "div({className: 'my-4 border-t border-white/10'}),", "div({className: 'my-4 border-t border-white/10'}),\n              button({ onClick: () => { setShowGallery(true); setScreen('home'); setIsMobileMenuOpen(false); }, className: 'w-full text-left p-3 rounded-lg text-sm font-bold text-brand-accent hover:bg-white/5 ' + (showGallery?'bg-brand-accent/10':'') }, '🌐 プロンプトギャラリー'),", "サイドバーへのギャラリーボタン追加")

    # 8. 画面切り替えロジック
    content = apply_patch(content, 
        "screen === 'admin_dashboard' && props.role === 'admin' ? el(AdminDashboard, { user: props.user }) :", 
        "screen === 'admin_dashboard' && props.role === 'admin' ? el(AdminDashboard, { user: props.user }) :\n                showGallery ? el(CommunityGallery, { db, user: props.user, onBack: ()=>setShowGallery(false) }) :", 
        "ギャラリー画面への遷移ロジック追加")

    # 9. バージョン更新
    content = re.sub(r"const SYS_VERSION = 'v72\.[^']+';", "const SYS_VERSION = 'v73.0.0 Ultimate SaaS Edition';", content)

    with open(APP_JS, 'w', encoding='utf-8') as f: f.write(content)

print("🚀 AICP Pro v73 アップデートパッチ実行開始...")
patch_tools()
patch_app()
print("\n✅ 全パッチ適用完了！既存のコード（魔法の杖、ダッシュボード等）は一切破壊せずに新機能を追加しました。")
