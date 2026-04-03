import re
import sys

# --- tools.js に新ツールを追加 ---
with open('static/js/tools.js', 'r', encoding='utf-8') as f:
    t_content = f.read()

new_omega_tools = """
    coconala_gig: { cat: 'omega', icon: '🛍️', name: 'ココナラ無双パッケージ', desc: 'ココナラで売れるサービスページと出品内容を丸ごと作成。',
      help: 'ココナラ（coconala）でサービスを出品するための、検索順位が上がりやすく成約しやすい「サービスタイトル・キャッチコピー・詳細説明文・購入にあたってのお願い」をパッケージとして生成します。',
      fields: [{ id: 'service', t: 'area', l: '提供したいサービスの内容・強み', ph: '例: タロット占い。恋愛相談が得意で、優しい言葉で背中を押します。', isMainMagic: true }],
      build: function(v) { return '# ココナラ出品パッケージ作成\\n以下のサービス内容をもとに、ココナラで売れる出品ページを作成してください。\\nサービス内容: ' + (v.service || '') + '\\n\\n以下の構成で出力してください：\\n1. 魅力的なサービスタイトル案（3つ）\\n2. サービス詳細説明文（coconala形式）\\n3. 購入にあたってのお願い（必要情報の案内）\\n4. よくある質問（3〜5つ）\\n5. サービス画像に入れるべきテキスト案'; }
    },
"""

new_fun_tools = """
    price_up: { cat: 'fun', icon: '📈', name: '値上げ告知投稿ジェネレーター', desc: '既存顧客を逃がさず「今すぐ申込もう」と思わせる告知文。',
      help: 'サービスの値上げを告知する際、駆け込み申込を促しつつ既存顧客の信頼を失わない投稿文を生成します。',
      fields: [
        { id: 'service', t: 'text', l: 'サービス名', ph: '例: タロット鑑定', isMainMagic: true },
        { id: 'current_price', t: 'text', l: '現在の価格', ph: '例: 3000円' },
        { id: 'date', t: 'text', l: '値上げ実施日', ph: '例: 4月15日から' },
        { id: 'new_price', t: 'text', l: '値上げ後の価格', ph: '例: 5000円' },
        { id: 'reason', t: 'text', l: '値上げの理由 (任意)', ph: '例: サービス内容の充実のため' }
      ],
      build: function(v) {
        return '# 値上げ告知文作成\\nサービス: ' + (v.service || '') + '\\n現在: ' + (v.current_price || '') + ' → 新価格: ' + (v.new_price || '') + '\\n実施日: ' + (v.date || '') + '\\n理由: ' + (v.reason || '') + '\\n\\n値上げの正当な理由を説明し、既存顧客への感謝を伝えつつ、値上げ前の駆け込み申し込みを促すSNS告知文を2パターン作成してください。';
      }
    },
    uranai_kantei: { cat: 'fun', icon: '🔮', name: '占い鑑定書ライター', desc: 'coconala/note販売向けのプロ品質鑑定書を生成。',
      help: '占術・相談者情報を入力するだけで、有料販売に耐えるプロ品質の鑑定書を自動生成します。',
      fields: [
        { id: 'method', t: 'select', l: '占術', opts: ['タロット','西洋占星術','四柱推命','数秘術','手相','霊感・霊視','オラクルカード'] },
        { id: 'client', t: 'area', l: '相談者情報', ph: '例: 28歳女性、仕事の転機について悩み中', isMainMagic: true },
        { id: 'question', t: 'text', l: '相談内容', ph: '例: 転職すべきか今の会社に残るべきか' }
      ],
      build: function(v) {
        return '# 占い鑑定書作成指示\\n占術:'+(v.method || 'タロット') + '\\n相談者:'+(v.client || '') + '\\n相談内容:'+(v.question || '') + '\\n\\nプロの占い師として、有料販売できる品質の鑑定書を作成してください。\\n\\n【構成】\\n1. 導入(相談者への寄り添い)\\n2. 鑑定結果(占術に基づく詳細な解釈)\\n3. 具体的アドバイス(行動指針・開運アクション)\\n4. まとめ(希望を持てる締めくくり)\\n\\n2000文字以上で丁寧に、温かみのある文体で書いてください。';
      }
    },
    uranai_aisho: { cat: 'fun', icon: '💕', name: '相性鑑定書ライター', desc: '2人の相性を深掘りする鑑定書 (恋愛系No.1ジャンル)。',
      help: '恋愛・相性鑑定はcoconalaで最も売れるジャンルです。2人の情報から本格的な相性鑑定書を生成します。',
      fields: [
        { id: 'method', t: 'select', l: '占術', opts: ['タロット','西洋占星術','四柱推命','数秘術','相性占い総合'] },
        { id: 'person1', t: 'text', l: '相談者(本人)', ph: '例: 1995年3月15日生まれ 女性' },
        { id: 'person2', t: 'text', l: 'お相手', ph: '例: 1992年8月22日生まれ 男性', isMainMagic: true },
        { id: 'concern', t: 'text', l: '気になること', ph: '例: 復縁の可能性' }
      ],
      build: function(v) {
        return '# 相性鑑定書作成\\n占術:'+(v.method || '相性占い総合') + '\\n本人:'+(v.person1 || '') + '\\nお相手:'+(v.person2 || '') + '\\n気になること:'+(v.concern || '') + '\\n\\n2人の相性を多角的に鑑定する鑑定書を作成してください。\\n\\n【構成】\\n1. 総合相性(星5段階評価付き)\\n2. 恋愛面の相性\\n3. コミュニケーションの相性\\n4. 価値観・将来性の相性\\n5. 注意すべきポイント\\n6. 2人へのアドバイス\\n\\n温かく希望が持てる文体で、2000文字以上で書いてください。';
      }
    },
    uranai_calendar: { cat: 'fun', icon: '📅', name: '運勢カレンダー鑑定', desc: '月次・年間運勢鑑定書(高単価販売に最適)。',
      help: '月別または年間の運勢を網羅した鑑定書を生成します。coconalaで3000円〜の高単価で販売可能です。',
      fields: [
        { id: 'method', t: 'select', l: '占術', opts: ['西洋占星術','四柱推命','数秘術','九星気学'] },
        { id: 'period', t: 'select', l: '期間', opts: ['今月の運勢','3ヶ月間の運勢','年間運勢(12ヶ月)'] },
        { id: 'client', t: 'text', l: '相談者情報', ph: '例: 1990年6月10日生まれ 女性', isMainMagic: true }
      ],
      build: function(v) {
        return '# 運勢カレンダー鑑定\\n占術:'+(v.method || '西洋占星術') + '\\n期間:'+(v.period || '今月の運勢') + '\\n相談者:'+(v.client || '') + '\\n\\n指定期間の運勢を月ごとに詳細に鑑定してください。\\n\\n【各月の項目】\\n- 総合運(5段階★表記)\\n- 恋愛運\\n- 仕事運\\n- 金運\\n- 健康運\\n- ラッキーカラー・ラッキーアイテム\\n- 月のテーマ(一言メッセージ)\\n\\n読みやすい表形式で、各月の詳細解説も添えてください。';
      }
    },
    coconala_listing: { cat: 'fun', icon: '📝', name: 'coconala出品文ジェネレーター', desc: 'coconala検索で上位表示されるサービス説明文を自動生成。',
      help: 'coconalaのアルゴリズムに最適化されたサービスタイトル・説明文・購入特典を生成します。',
      fields: [
        { id: 'service', t: 'text', l: 'サービス内容', ph: '例: タロットで恋愛相談に乗ります。', isMainMagic: true },
        { id: 'price', t: 'text', l: '販売価格', ph: '例: 3000円' },
        { id: 'strength', t: 'area', l: 'あなたの強み・実績', ph: '例: 鑑定歴5年、リピーター率80%、鑑定件数500件超' }
      ],
      build: function(v) {
        return '# coconala出品文作成\\nサービス:'+(v.service || '') + '\\n価格:'+(v.price || '') + '\\n強み:'+(v.strength || '') + '\\n\\ncoconalaで検索上位に表示され、購入されやすいサービスページを作成してください。\\n\\n【出力項目】\\n1. サービスタイトル案(3つ・キーワード含む・25文字以内)\\n2. サービス説明文(1000文字程度・coconala形式)\\n3. 「購入にあたってのお願い」(必要情報の案内)\\n4. よくある質問(3〜5つ)\\n5. サービス画像に入れるべきテキスト案';
      }
    },
    profile_writer: { cat: 'fun', icon: '👤', name: 'プロフィール文ジェネレーター', desc: 'SNS/coconala/noteで集客力が上がるプロフィール文。',
      help: 'フォローしたくなる・依頼したくなるプロフィール文を、プラットフォーム別に最適化して生成します。',
      fields: [
        { id: 'platform', t: 'select', l: '対象プラットフォーム', opts: ['X(Twitter)', 'Instagram', 'coconala', 'note','Threads', 'TikTok','YouTube'] },
        { id: 'job', t: 'text', l: '肩書き・職業', ph: '例: 元看護師の占い師', isMainMagic: true },
        { id: 'achievement', t: 'text', l: '実績・数字', ph: '例: 鑑定件数500件超、リピート率80%' }
      ],
      build: function(v) {
        return '# プロフィール文作成\\nプラットフォーム: ' + (v.platform || 'X') + '\\n肩書き: ' + (v.job || '') + '\\n実績: ' + (v.achievement || '') + '\\n\\n対象プラットフォームの文字数や文化に最適化した魅力的なプロフィール文を作成してください。箇条書きや絵文字を適度に使い、実績を強調してください。';
      }
    },
"""

if "coconala_gig:" not in t_content:
    t_content = t_content.replace("secret_god: {", new_omega_tools + "secret_god: {")
if "price_up:" not in t_content:
    t_content = t_content.replace("reply: {", new_fun_tools + "reply: {")

with open('static/js/tools.js', 'w', encoding='utf-8') as f:
    f.write(t_content)


# --- app.js に利用規約(AuthBox)を追加 ---
with open('static/js/app.js', 'r', encoding='utf-8') as f:
    a_content = f.read()

new_authbox = r"""    const AuthBox = ({ onLogin }) => {
        const [isRegister, setIsRegister] = useState(false);
        const [id, setId] = useState('');
        const [pass, setPass] = useState('');
        const [err, setErr] = useState('');
        const [regAgreed, setRegAgreed] = useState(false);
        const [showTerms, setShowTerms] = useState(false);
        
        const handle = () => {
            const db = AppDB.get();
            if(db.users[id]) {
                if(id === 'admin' && pass === db.config.adminP) onLogin(id);
                else if(id !== 'admin' && pass === 'password') onLogin(id);
                else setErr('パスワードが違います');
            } else setErr('ユーザーが存在しません');
        };

        const register = () => {
            setErr('登録申請を受け付けました（現在はデモ用です）');
        };

        return div({className: 'flex h-screen items-center justify-center relative overflow-hidden bg-[#020617]'},
            div({className: 'glass-panel p-8 md:p-12 rounded-3xl w-full max-w-md relative z-10 animate-in border border-white/10 shadow-2xl'},
                div({className: 'text-center mb-8'}, h2({className: 'text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-brand-light to-brand-accent mb-2'}, 'AICP Pro')),
                err && ErrorAlert({msg: err}),
                div({className: 'space-y-4'},
                    input({className: 'input-base py-4 px-5 text-base rounded-2xl bg-black/40', placeholder: 'ユーザーID', value: id, onChange: e=>setId(e.target.value)}),
                    input({className: 'input-base py-4 px-5 text-base rounded-2xl bg-black/40', type: 'password', placeholder: 'パスワード', value: pass, onKeyDown: e => e.key === 'Enter' && (!isRegister ? handle() : register()), onChange: e=>setPass(e.target.value)}),
                    
                    isRegister && div ({ className: 'flex items-center gap-3 p-3 mt-4 bg-black/30 rounded-xl border border-white/5' },
                        div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition shrink-0 cursor-not-allowed opacity-80' },
                            div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (regAgreed ? 'bg-brand left-5': 'bg-gray-400') })
                        ),
                        button({ onClick: () => setShowTerms (true), className: 'text-xs text-brand hover:text-brand-light font-bold leading-relaxed text-left underline underline-offset-4'}, '利用規約およびプライバシーポリシーを確認し、同意する')
                    ),

                    !isRegister ? button({className: 'btn-gradient w-full py-4 rounded-2xl font-black text-lg shadow-xl mt-4', onClick: handle}, 'ログイン')
                                : button({onClick: register, disabled: !regAgreed, className: 'w-full btn-gradient py-4 rounded-xl text-lg mt-4 shadow-lg shadow-brand/20 disabled:opacity-50 disabled:cursor-not-allowed'}, '登録申請する'),
                    
                    button({className: 'w-full text-slate-400 text-sm mt-4 hover:text-white', onClick: () => setIsRegister(!isRegister)}, isRegister ? '既存アカウントでログイン' : '新規アカウント登録申請')
                )
            ),
            showTerms && div({className: 'fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4'},
                div({className: 'glass-panel p-8 rounded-2xl max-w-lg w-full'},
                    h3({className: 'text-xl font-bold text-white mb-4'}, '利用規約 / プライバシーポリシー'),
                    div({className: 'h-64 overflow-y-auto text-sm text-slate-300 mb-6 bg-black/30 p-4 rounded-lg'}, 'ここに利用規約とプライバシーポリシーが記載されます。内容を確認し、同意する場合は下の「同意する」ボタンを押してください。'),
                    div({className: 'flex justify-end gap-4'},
                        button({className: 'px-4 py-2 rounded-lg text-slate-400 hover:bg-white/10', onClick: () => setShowTerms(false)}, '閉じる'),
                        button({className: 'px-4 py-2 rounded-lg btn-gradient', onClick: () => { setRegAgreed(true); setShowTerms(false); }}, '同意する')
                    )
                )
            )
        );
    };"""

a_content = re.sub(r"const AuthBox = \(\{ onLogin \}\) => \{.*?// ================================================================\n\s*// App \(Root Component\)", new_authbox + "\n\n    // ================================================================\n    // App (Root Component)", a_content, flags=re.DOTALL)
a_content = re.sub(r"const SYS_VERSION = '[^']+';", "const SYS_VERSION = 'v72.0.6 Ultimate Edition';", a_content)

with open('static/js/app.js', 'w', encoding='utf-8') as f:
    f.write(a_content)

print("✅ 新ツールと利用規約UIの追加に成功しました。")
