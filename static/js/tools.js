// ================================================================
// SNS なりきりキャラ定義
// ================================================================
var SNS_PERSONA_MAP = {
  '🌸 活発な女の子':     '明るくテンション高め。感嘆符多め。「やってみた！」「マジで神〜」「最高すぎ」など。ギャル語・略語・絵文字を自然に散りばめ、等身大で共感を生む文体。',
  '💅 おしゃれ大人女子': '丁寧だが親しみある文体。「〜かも」「〜だよね」「ていねいに生きる」感。上品で近寄りやすく、センスを感じさせる。',
  '🧘 ナチュラル系女子': 'ゆったりした文体。ひらがな多め。「のんびり」「ほっこり」「じんわり」系の言葉。自然体で癒し系。急かさない温かさがある。',
  '👩‍💼 できるビジネス女性': '論理的でテンポよい。「結論から言うと」「ポイントは3つ」。端的だが温かみがあり高い信頼感を与える。',
  '😎 クールな男':       '端的・断言系。「〜だけ。以上。」スタイル。数字と事実で語る。余計な感情表現を排除。かっこよさと潔さ重視。',
  '🔥 熱血系兄貴':       '熱量高め。「お前ら聞けよ」系。読者の背中を強く押す。「絶対できる」「諦めるな」「俺も同じだった」。感情移入させる。',
  '🤓 知識系博士':       'データ・数字・根拠を必ず添える。「研究によると」「統計では」。知的で信頼感があり教育的。マニアックな深掘りが得意。',
  '😄 親しみ系おじさん': '「〜だよね笑」「正直に言うと」経験談多め。失敗談も交えながら共感を生む。人間味あふれる温かい文体。',
  '🤖 AIネイティブ':     'AIを使いこなす人らしいテック感。「効率化」「自動化」「最適解」。モダンで前向き。先進的な視点で語る。',
  '🎮 オタク気質':       '深掘り・マニアック。「わかる人だけわかって」感。熱量と専門知識が自然に滲み出る。コアファンを作る文体。',
  '🌍 帰国子女':         '日本語に外来語が自然に混ざる。グローバルな視点。「海外では〜」「日本特有の〜」。国際感覚と新鮮な切り口。',
  '✏️ カスタム':         ''
};

var SNS_GENRE_MAP = {
  '💰 副業・マネー':       { buzz: '「〇万円稼いだ方法」「手取りXX万から」「副業で月収アップ」', caution: '「簡単に稼げる」「誰でも」は景表法に注意', tips: '具体的な金額・期間・手順を数字で示す。再現性を強調。' },
  '💄 美容・コスメ':       { buzz: '「使ってみた正直レビュー」「〇日後の肌が」「プチプラ最強」', caution: '「効果が出ます」「治ります」は薬機法に注意', tips: 'ビフォーアフター・価格帯・成分情報を入れる。' },
  '🍽️ グルメ・料理':      { buzz: '「作ってみた」「コスパ最強」「リピ確定」「神コスパ」', caution: '', tips: '五感で伝える描写。食感・香り・見た目を具体的に。' },
  '💪 筋トレ・ダイエット': { buzz: '「〇kg落ちた」「継続X日目」「before/after」「習慣化した方法」', caution: '「痩せます」「必ず効果が出る」は薬機法に注意', tips: '数字と期間で結果を具体化。継続の秘訣を入れる。' },
  '📚 学び・スキルアップ': { buzz: '「知らないと損」「〇分でわかる」「まとめた」「保存版」', caution: '', tips: 'リスト形式で情報を整理。保存・シェアされる構成に。' },
  '💼 転職・キャリア':     { buzz: '「年収X万アップした」「やめてよかった」「転職で人生変わった」', caution: '', tips: 'リアルな体験談と感情の変化を描写。before/afterを明確に。' },
  '💕 恋愛・婚活':         { buzz: '「実体験」「リアルな話」「男性/女性心理」「正直に言うと」', caution: '', tips: '心理学・行動経済学のエビデンスを1つ入れると説得力UP。' },
  '🤱 育児・ファミリー':   { buzz: '「〇歳育児」「神アイテム発見」「試してよかった」「育児の真実」', caution: '', tips: '共感フレーズ多め。同じ立場のパパ・ママに刺さる言葉を。' },
  '🌿 ライフスタイル':     { buzz: '「暮らしの工夫」「ルーティン公開」「朝活」「シンプルに生きる」', caution: '', tips: '写真映えする描写と生活改善の具体策をセットで。' },
  '🎮 エンタメ・趣味':     { buzz: '「やばすぎた」「沼った」「語らせてください」「本気でハマった」', caution: '', tips: '熱量と具体的なおすすめポイントで読者を沼に引き込む。' },
  '🤖 AI・テクノロジー':   { buzz: '「これ知らないと置いてかれる」「AIで〇〇分が〇秒に」「衝撃だった」', caution: '', tips: '具体的なツール名・操作手順・活用例を入れる。初心者向けに噛み砕く。' },
  '💹 投資・資産形成':     { buzz: '「〇年で〇倍になった」「新NISA活用法」「資産形成の真実」', caution: '「必ず儲かる」は金融商品取引法に注意', tips: '数字と長期視点で信頼感を出す。リスクにも触れる。' }
};

function getPersonaInstruction(personaKey, customPersona) {
  if (customPersona && customPersona.trim()) {
    return '\n\n【🎭 なりきりキャラクター指示】\n以下の人物像になりきって、その人格・文体・口調を完全に憑依させてください：\n「' + customPersona.trim() + '」\nこのキャラクターらしい言葉遣い・テンション・表現を徹底してください。\n';
  }
  var desc = SNS_PERSONA_MAP[personaKey];
  if (!desc || !desc.trim()) return '';
  return '\n\n【🎭 なりきりキャラクター指示】\nキャラクター: ' + personaKey + '\n文体・口調: ' + desc + '\nこのキャラクターになりきって、そのキャラらしい言葉遣い・テンション・絵文字の使い方で出力してください。\n';
}

function getGenreInstruction(genreKey) {
  var g = SNS_GENRE_MAP[genreKey];
  if (!g) return '';
  return '\n\n【🏷️ ジャンル特化指示】\nジャンル: ' + genreKey + '\nバズりやすい表現: ' + g.buzz + '\n' + (g.caution ? '法律・規約注意: ' + g.caution + '\n' : '') + '品質のコツ: ' + g.tips + '\nこのジャンルの読者が「保存したい」「シェアしたい」と思う投稿にしてください。\n';
}

var PERSONA_OPTS = Object.keys(SNS_PERSONA_MAP);
var GENRE_OPTS = Object.keys(SNS_GENRE_MAP);

// ================================================================
// カテゴリ定義
// ================================================================
const CATEGORIES = [
    { id: 'omega', name: '🔥 オメガ特級ツール' },
    { id: 'mon',   name: '📝 コンテンツ作成 ＆ 販売' },
    { id: 'cw',    name: '💼 クラウドワークス・仕事完遂' },
    { id: 'sns',   name: '🚀 集客 ＆ SNSアナリティクス' },
    { id: 'fun',   name: '💬 ファン化 ＆ セールス自動化' },
    { id: 'prompt_only', name: '✨ 無限プロンプト集 (API不要)' }
];

const TOOLS = {
    // --- 🔥 オメガ特級ツール ---
    secret_god: { cat: 'omega', icon: '🧿', name: '【神限定】万能・神の眼', desc: 'あらゆる入力から最適なアウトプットを導き出します。', reqLevel: 50,
      fields: [{ id: 'req', t: 'area', l: '神の要求', ph: '例: この商材を売るためのすべてを教えて' }],
      build: (v) => '# 神の要求\n以下の要求に対して、考えうる最高のクオリティで包括的な回答を生成してください。\n要求: ' + v.req },
    funnel: { cat: 'omega', icon: '🌪️', name: '全自動ファネル構築', desc: '集客から販売までの最強の導線を設計します。',
      fields: [{ id: 'prod', t: 'text', l: '販売商品', ph: '例: AI副業マスター講座', isMainMagic: true }, { id: 'target', t: 'text', l: 'ターゲット層', ph: '例: 副業初心者' }],
      build: (v) => '# ファネル構築指示\n商品「' + v.prod + '」を「' + v.target + '」に販売するための、集客・教育・販売の全自動ファネル導線を設計してください。' },
    vsl: { cat: 'omega', icon: '🎬', name: 'VSL台本', desc: '動画セールスレター用の心を動かす台本を生成。',
      fields: [{ id: 'prod', t: 'text', l: '販売商品', ph: '例: ダイエットプログラム', isMainMagic: true }],
      build: (v) => '# VSL台本作成指示\n商品「' + v.prod + '」を販売するための動画セールスレター(VSL)の台本を作成してください。冒頭のフックからオファーまで含めてください。' },
    sns_cal: { cat: 'omega', icon: '📅', name: '30日間SNSカレンダー', desc: 'キャラ×ジャンル特化で1ヶ月分のSNS発信内容を自動構築。',
      fields: [
        { id: 'theme',    t: 'text',   l: '発信テーマ', ph: '例: 投資・資産運用', isMainMagic: true },
        { id: 'persona',  t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
        { id: 'p_custom', t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'genre',    t: 'select', l: '🏷️ 特化ジャンル', opts: GENRE_OPTS }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, v.p_custom);
        var genre = getGenreInstruction(v.genre);
        return '# SNSカレンダー作成指示' + persona + genre + '\nテーマ「' + (v.theme||'') + '」についてのSNS投稿内容を、30日間のカレンダー形式（表）で作成してください。\n上記のキャラクターとジャンル特化の指示を全投稿に反映してください。各投稿に曜日・テーマ・投稿文の要点を記載してください。';
      }
    },
    ai_meeting: { cat: 'omega', icon: '🧠', name: 'AIエージェント会議', desc: '複数のAIペルソナによる多角的なアイデア出し。',
      fields: [{ id: 'topic', t: 'area', l: '議論テーマ', ph: '例: 新しいSaaSのマーケティング戦略' }],
      build: (v) => '# AIエージェント会議指示\nテーマ「' + v.topic + '」について、CEO、マーケター、エンジニアの3つの視点から議論し、多角的なアイデアと結論を出してください。' },
    affiliate: { cat: 'omega', icon: '🤝', name: 'アフィリエイトセンター', desc: 'アフィリエイター向けの紹介文や特典設計。',
      fields: [{ id: 'prod', t: 'text', l: '商品詳細', ph: '例: 英語学習アプリ', isMainMagic: true }],
      build: (v) => '# アフィリエイト設計指示\n商品「' + v.prod + '」をアフィリエイターに紹介してもらうための、紹介用テンプレートと特典アイデアを提案してください。' },
    launch: { cat: 'omega', icon: '🚀', name: 'プロダクトローンチ生成', desc: '売上を最大化するローンチシナリオを設計。',
      fields: [{ id: 'prod', t: 'text', l: '商品名', ph: '例: 動画編集スクール' }],
      build: (v) => '# ローンチシナリオ作成\n商品「' + v.prod + '」を爆発的に売るための、プレローンチから販売開始までのプロダクトローンチシナリオを設計してください。' },
    slide_gen: { cat: 'omega', icon: '📊', name: 'ウェビナースライド構成', desc: '成約率を高めるウェビナーの構成とスライド用画像プロンプトを作成。', isImagePrompt: true,
      fields: [{ id: 'topic', t: 'text', l: 'ウェビナーのテーマ', ph: '例: AIを使った業務効率化' }],
      build: (v) => v.topic },
    rule: { cat: 'omega', icon: '⚖️', name: 'コンテンツ盗用防止＆規約', desc: 'デジタルコンテンツの利用規約や警告文を作成。',
      fields: [{ id: 'prod', t: 'text', l: 'コンテンツ名', ph: '例: 稼ぐためのプロンプト集' }],
      build: (v) => '# 規約作成指示\nコンテンツ「' + v.prod + '」の無断転載・盗用を防止するための厳格な利用規約と、冒頭に記載する警告文を作成してください。' },

    // ================================================================
    // 📝 note記事 究極生成
    // ================================================================
    note: { cat: 'mon', icon: '📝', name: 'note記事 究極生成', desc: '売れるnote有料記事を、最高品質のプロ構成で全自動執筆。',
      fields: [
        { id: 'genre',      t: 'select', l: 'noteのジャンル', opts: ['副業・ビジネス', '恋愛・婚活', '美容・ダイエット', '投資・マネー', '自己啓発・メンタル', 'テクノロジー・AI', 'エンタメ・趣味', 'スキル・資格', '子育て・家族', '健康・医療'] },
        { id: 'age',        t: 'select', l: 'ターゲット年代', opts: ['10代', '20代', '25〜35歳', '30代', '35〜45歳', '40代', '50代', '60代以上'] },
        { id: 'theme',      t: 'text',   l: '記事テーマ（メインキーワード）', ph: '例: スマホ1台で月5万稼ぐ極意', isMainMagic: true },
        { id: 'target',     t: 'area',   l: '読者の具体的な悩み・状況', ph: '例: 副業したいがスキルがない30代会社員。毎月赤字で将来が不安。' },
        { id: 'result',     t: 'text',   l: '読者が得られる具体的な結果・数字', ph: '例: 3ヶ月で月3万円の副収入、作業時間1日30分' },
        { id: 'steps',      t: 'text',   l: '解決策のステップ数', ph: '例: 5ステップ（空欄でAIが自動設定）' },
        { id: 'price',      t: 'text',   l: '販売金額（必須）', ph: '例: 1980円' },
        { id: 'free_len',   t: 'text',   l: '無料エリア文字数 (±200字)', ph: '例: 2000（空欄で自動）' },
        { id: 'paid_len',   t: 'text',   l: '有料エリア文字数 (±200字)', ph: '例: 4000（空欄で自動）' },
        { id: 'guarantee',  t: 'check',  l: '返金保証をアピール' }
      ],
      build: (v) => {
        var genre=v.genre||'', age=v.age||'', theme=v.theme||'', target=v.target||'';
        var result=v.result||'具体的な成果（AIが最適な数字を設定）';
        var steps=v.steps||'5', price=v.price||'未定';
        var free_len=v.free_len||'2000', paid_len=v.paid_len||'4500';
        var guarantee=v.guarantee?'・冒頭で返金保証があることを強調し、読者の不安を取り除いてください。\n':'';
        return '# ✅ note有料記事 プロ品質執筆指示（Stella Note式 完全版）\n\n## 基本設定\n- ジャンル: '+genre+'\n- ターゲット: '+age+'\n- テーマ: '+theme+'\n- 読者の悩み・状況: '+target+'\n- 読者が得られる結果: '+result+'\n- 販売金額: '+price+'\n\n## 文章ルール\n- です・ます調 / 1文50字以内 / 改行多め / 専門用語なし / 具体的な数字を多用\n\n## ⚠️ 出力フォーマット厳守\n---【タイトル案】---\nクリック率が最大化されるタイトル案を5つ（数字必須・30字前後）\n\n---【無料エリア】---\n約'+free_len+'文字。## 見出し / **太字** / > 引用 / [ここに図解挿入] を使用。\n導入（600字）→問題の本質（800字）→解決策の全体像（600字）→有料誘導の構成で。\n\n---【有料エリア】---\n約'+paid_len+'文字。\n'+guarantee+'ステップ1〜'+steps+'（各ステップに実例・失敗注意点）→実践事例→Q&A（5つ）→今すぐできること（3アクション）\n\n---【SEO・ハッシュタグ】---\nハッシュタグ5つ＋140字の記事説明文';
      }
    },

    // --- 📝 コンテンツ作成 ＆ 販売 ---
    lp: { cat: 'mon', icon: '📄', name: '爆売れLP作成', desc: '高単価商品を一撃で成約させるセールスコピー。',
      fields: [
        { id: 'prod', t: 'text', l: '商品名・価格', ph: '例: AIコンサル (10万円)', isMainMagic: true },
        { id: 'bene', t: 'area', l: '最強のベネフィット', ph: '例: 会社に依存せず自由な収入と時間を手に入れる' }
      ],
      build: (v) => '# LP作成指示\n商品「'+v.prod+'」を販売するためのLPを作成してください。\nベネフィット「'+v.bene+'」を強調し、読者の痛みに共感し、この商品こそが唯一の解決策であると確信させる構成にしてください。' },
    backend: { cat: 'mon', icon: '💎', name: '高単価バックエンド企画', desc: '利益を最大化するバックエンド商品を企画。',
      fields: [{ id: 'front', t: 'text', l: 'フロント商品', ph: '例: 無料のPDFレポート', isMainMagic: true }],
      build: (v) => '# バックエンド企画\nフロント商品「'+v.front+'」を購入した顧客に対して、LTVを最大化するための高単価バックエンド商品（30万〜100万円）のコンセプトと内容を企画してください。' },
    closing: { cat: 'mon', icon: '🎯', name: '心理的クロージング', desc: '最後の迷いを断切る強力なクロージング文章。',
      fields: [{ id: 'objection', t: 'area', l: '顧客の反論・不安', ph: '例: お金がない、時間がない' }],
      build: (v) => '# クロージング指示\n顧客の抱える不安「'+v.objection+'」を解消し、今すぐ購入しなければならない理由を提示する、強力なクロージングコピーを作成してください。' },
    research: { cat: 'mon', icon: '🔍', name: '競合リサーチ解剖', desc: '競合の強みと弱みを丸裸にする分析プロンプト。',
      fields: [{ id: 'competitor', t: 'text', l: '競合の名前や特徴', ph: '例: 業界最大手のA社' }],
      build: (v) => '# 競合分析指示\n競合「'+v.competitor+'」について、4P分析・SWOT分析を行い、我々が勝つための隙（弱み）と戦略を提案してください。' },
    site_analyze: { cat: 'mon', icon: '🌐', name: '競合サイト完全解剖', desc: 'URLから（想定）サイト構造と改善点を導き出す。',
      fields: [{ id: 'url', t: 'text', l: 'ターゲットURL/サイト名', ph: '例: https://example.com' }],
      build: (v) => '# サイト分析\n対象「'+v.url+'」のWebサイト構成を想定し、UI/UX、SEO、コンバージョンの観点から改善点と、自社サイトに活かせる要素を列挙してください。' },

    // --- 💼 クラウドワークス・仕事完遂 ---
    cw_prop: { cat: 'cw', icon: '✍️', name: 'CW案件獲得 提案文', desc: 'クラウドソーシングで採用される最強の提案文。',
      fields: [{ id: 'job', t: 'area', l: '案件の内容', ph: '例: YouTubeの動画編集 1本5000円', isMainMagic: true }],
      build: (v) => '# 提案文作成\n以下の案件に対して、クライアントの信頼を勝ち取り、確実に発注される魅力的な提案文を作成してください。\n案件: '+v.job },
    seo: { cat: 'cw', icon: '📈', name: 'SEO特化ライティング', desc: '検索上位を狙うためのSEO最適化記事を作成。',
      fields: [{ id: 'kw', t: 'text', l: '対策キーワード', ph: '例: AI ツール おすすめ' }],
      build: (v) => '# SEO記事作成\nキーワード「'+v.kw+'」で検索上位を獲得するための、網羅的で読者の検索意図を満たすSEO記事（構成案と本文）を作成してください。' },
    high_ticket: { cat: 'cw', icon: '🦅', name: '高単価案件ハンター', desc: '低単価から抜け出すためのスキル掛け合わせ提案。',
      fields: [{ id: 'skill', t: 'text', l: 'あなたのスキル', ph: '例: ライティング、簡単な画像作成' }],
      build: (v) => '# 高単価提案\nスキル「'+v.skill+'」を活かして、単価を3倍〜5倍に引き上げるための付加価値の付け方と、クライアントへの具体的な提案フレーズを作成してください。' },
    nego: { cat: 'cw', icon: '💬', name: '報酬・単価交渉AI', desc: '角を立てずに単価アップを交渉するメッセージ。',
      fields: [{ id: 'reason', t: 'area', l: '単価交渉の理由', ph: '例: 継続して半年経過、作業範囲が広がった' }],
      build: (v) => '# 交渉メッセージ作成\n理由「'+v.reason+'」をもとに、既存クライアントに対して不快感を与えずに単価アップを承諾させる丁寧な交渉メッセージを作成してください。' },
    trans: { cat: 'cw', icon: '🌍', name: '多言語翻訳・納品', desc: 'ニュアンスを保ったプロレベルの翻訳。',
      fields: [{ id: 'text', t: 'area', l: '翻訳するテキスト', ph: '例: このツールは世界を変える' }, { id: 'lang', t: 'select', l: '翻訳先言語', opts: ['英語', '中国語', '韓国語'] }],
      build: (v) => '# 翻訳指示\n以下のテキストを、ネイティブが自然に感じるプロフェッショナルな'+v.lang+'に翻訳してください。\n\n'+v.text },

    // ================================================================
    // 🚀 集客 ＆ SNSアナリティクス
    // ================================================================
    sns_analyze: { cat: 'sns', icon: '👁️', name: 'SNS視覚アナリティクス', desc: 'グラフ画像を解析し、目標達成のための戦略をコンサル。',
      fields: [
        { id: 'goal',  t: 'area',  l: '現在の状況と1ヶ月後の目標', ph: '例: 現在フォロワー500人。1ヶ月後に1000人にしたい。' },
        { id: 'image', t: 'image', l: 'SNSアナリティクスのスクショ (必須)' }
      ],
      build: (v) => '# SNS分析コンサルティング依頼\n目標・現状：「'+v.goal+'」\n添付したスクリーンショット（SNSのアナリティクスデータやグラフ）を視覚的に詳細に解析し、現状の課題と、目標達成に向けた来週の具体的なアクションプラン（投稿カレンダー含む）を提案してください。'
    },

    acc_design: { cat: 'sns', icon: '🏗️', name: 'バズるアカウント設計', desc: 'キャラ×ジャンルで差別化したSNSコンセプトを完全設計。',
      fields: [
        { id: 'genre',     t: 'text',   l: '発信ジャンル', ph: '例: 美容・ダイエット', isMainMagic: true },
        { id: 'persona',   t: 'select', l: '🎭 なりきりキャラクター', opts: PERSONA_OPTS },
        { id: 'p_custom',  t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'sns_genre', t: 'select', l: '🏷️ 特化ジャンル', opts: GENRE_OPTS },
        { id: 'platform',  t: 'select', l: '対象SNS', opts: ['X(Twitter)', 'Instagram', 'Threads', 'TikTok', 'YouTube'] }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, v.p_custom);
        var genre = getGenreInstruction(v.sns_genre);
        return '# キャラ×ジャンル特化アカウント設計' + persona + genre +
          '\n対象SNS: '+(v.platform||'X(Twitter)')+'\n発信ジャンル: '+(v.genre||'')+
          '\n\n以下の全項目を設計してください：\n1. アカウント名（キャラクターが滲み出るもの）\n2. 肩書き・プロフィール文（200字以内、フォローしたくなる）\n3. 固定ツイート/ピン投稿のテンプレート\n4. 発信の軸3本（テーマ・角度・頻度）\n5. このキャラ×ジャンルが刺さるターゲット像\n6. 競合との差別化ポイント\n7. 最初の7投稿のテーマ案';
      }
    },

    sns: { cat: 'sns', icon: '📱', name: 'SNS無限集客ポスト', desc: 'キャラ×ジャンルで人格のある投稿文を3パターン生成。',
      fields: [
        { id: 'platform',  t: 'select', l: '📱 媒体', opts: ['X(Twitter)', 'Threads', 'Instagram'] },
        { id: 'persona',   t: 'select', l: '🎭 なりきりキャラクター', opts: PERSONA_OPTS },
        { id: 'p_custom',  t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'sns_genre', t: 'select', l: '🏷️ 特化ジャンル', opts: GENRE_OPTS },
        { id: 'content',   t: 'area',   l: '伝えたい内容・テーマ', ph: '例: 継続が大事。完璧を目指さない。', isMainMagic: true }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, v.p_custom);
        var genre = getGenreInstruction(v.sns_genre);
        var platform = v.platform || 'X(Twitter)';
        var platformTips = platform === 'X(Twitter)' ? '\n【X最適化】140字目安。改行多め。最初の1行でスクロールを止めるフック必須。' :
                           platform === 'Instagram' ? '\n【Instagram最適化】キャプション長めOK。保存・シェアされる有益情報を意識。ハッシュタグ案も末尾に。' :
                           '\n【Threads最適化】会話的・自然体。共感や議論を呼ぶ問いかけを末尾に。';
        return '# '+platform+' 投稿作成指示' + persona + genre + platformTips +
          '\n\n伝えたい内容: 「'+(v.content||'')+'」\n\n投稿文を3パターン作成してください。\nパターンA: フック重視（最初の1行で引き込む）\nパターンB: 共感重視（読者の悩みに寄り添う）\nパターンC: 情報価値重視（保存・シェアされる有益な内容）\n\n品質チェック（出力前に自己確認）:\n□ キャラクターの文体・口調が一貫しているか\n□ ジャンルのバズりパターンを活用しているか\n□ 最初の1行がフックになっているか\n□ スマホで読んで気持ちいい改行か';
      }
    },

    short_vid: { cat: 'sns', icon: '🎞️', name: 'ショート動画台本', desc: 'キャラ×ジャンルで視聴者の指が止まる台本を生成。',
      fields: [
        { id: 'topic',     t: 'text',   l: '動画のテーマ', ph: '例: iPhoneの隠し機能', isMainMagic: true },
        { id: 'persona',   t: 'select', l: '🎭 なりきりキャラクター', opts: PERSONA_OPTS },
        { id: 'p_custom',  t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'sns_genre', t: 'select', l: '🏷️ 特化ジャンル', opts: GENRE_OPTS },
        { id: 'platform',  t: 'select', l: '対象プラットフォーム', opts: ['TikTok', 'Instagram Reels', 'YouTube Shorts'] },
        { id: 'duration',  t: 'select', l: '動画の長さ', opts: ['15秒', '30秒', '60秒', '90秒'] }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, v.p_custom);
        var genre = getGenreInstruction(v.sns_genre);
        return '# ショート動画台本作成' + persona + genre +
          '\nテーマ: 「'+(v.topic||'')+'」\nプラットフォーム: '+(v.platform||'TikTok')+'\n目標尺: '+(v.duration||'60秒')+
          '\n\n以下の形式で台本を作成してください：\n\n【フック（0〜3秒）】\n視聴者の指を止め「続きが見たい」と思わせる最初のセリフと画面の動き\n\n【本編（4秒〜終盤）】\nテンポよく情報を届けるセリフと画面演出（テロップ案も含める）\n\n【CTA・締め（最後3秒）】\nフォロー・いいね・コメントを促す自然な締め\n\n【概要欄・ハッシュタグ】\nSEOを意識したキャプションとハッシュタグ案\n\nキャラクターの口調でセリフを書いてください。テンポとリズムを重視してください。';
      }
    },

    yt_script: { cat: 'sns', icon: '▶️', name: 'YouTube対話シナリオ', desc: 'キャラ×ジャンルで飽きさせない長尺台本を生成。',
      fields: [
        { id: 'topic',     t: 'text',   l: '動画のテーマ', ph: '例: NISAの始め方', isMainMagic: true },
        { id: 'persona',   t: 'select', l: '🎭 なりきりキャラクター（メインMC）', opts: PERSONA_OPTS },
        { id: 'p_custom',  t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'sns_genre', t: 'select', l: '🏷️ 特化ジャンル', opts: GENRE_OPTS },
        { id: 'duration',  t: 'select', l: '目標時間', opts: ['5〜8分', '10〜15分', '20〜30分'] }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, v.p_custom);
        var genre = getGenreInstruction(v.sns_genre);
        return '# YouTube長尺動画シナリオ' + persona + genre +
          '\nテーマ: 「'+(v.topic||'')+'」\n目標時間: '+(v.duration||'10〜15分')+
          '\n\nメインMCのキャラクターと初心者役（視聴者代表）の対話形式で台本を作成してください。\n\n① オープニング（30秒）: サムネと一致する掴みのセリフ\n② 自己紹介・信頼構築（1分）\n③ メインコンテンツ（時間の70%）: Q&A対話形式で\n④ まとめ・行動促進（2分）: 視聴者が今日できる1アクション\n⑤ エンディング（30秒）: チャンネル登録・次回予告\n\n各セクションにセリフと画面演出（テロップ・Bロール案）を記載してください。';
      }
    },

    image: { cat: 'sns', icon: '🎨', name: '画像生成AIプロンプト', desc: 'Midjourney等向けの英語の「呪文」を作成。', isImagePrompt: true,
      fields: [{ id: 'desc', t: 'text', l: '描きたい内容', ph: '例: サイバーパンクな未来の東京' }],
      build: (v) => v.desc
    },
    eye_catch: { cat: 'sns', icon: '🖼️', name: 'アイキャッチ構成デザイン', desc: '目を引くサムネイル画像用のプロンプト生成。', isImagePrompt: true,
      fields: [{ id: 'title', t: 'text', l: 'コンテンツのタイトル', ph: '例: AIで月10万稼ぐ方法' }],
      build: (v) => 'A YouTube thumbnail image for a video titled "'+v.title+'", high impact, bold typography style, eye-catching, vibrant colors' },

    // ================================================================
    // 🆕 SNS新機能ツール
    // ================================================================
    sns_buzz_check: { cat: 'sns', icon: '📊', name: 'バズ診断＆改善AI', desc: '投稿文のバズ予測スコアを診断して自動改善。',
      fields: [
        { id: 'post',      t: 'area',   l: '診断したい投稿文', ph: '診断・改善したいSNS投稿をここに入れてください', isMainMagic: true },
        { id: 'platform',  t: 'select', l: '投稿先SNS', opts: ['X(Twitter)', 'Instagram', 'Threads', 'TikTok'] },
        { id: 'persona',   t: 'select', l: '🎭 目標キャラクター', opts: PERSONA_OPTS },
        { id: 'sns_genre', t: 'select', l: '🏷️ ジャンル', opts: GENRE_OPTS }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, '');
        var genre = getGenreInstruction(v.sns_genre);
        return '# バズ診断＆改善AI' + persona + genre +
          '\n\n【診断対象投稿】\n'+(v.post||'')+'\n対象SNS: '+(v.platform||'X(Twitter)')+
          '\n\n以下の形式で診断・改善を行ってください：\n\n## 📊 バズスコア診断（100点満点）\n- フック（最初の1行）: 〇点/20点 → 評価コメント\n- 読みやすさ・改行: 〇点/20点 → 評価コメント\n- 情報価値・有益性: 〇点/20点 → 評価コメント\n- 共感・感情訴求: 〇点/20点 → 評価コメント\n- CTA・行動促進: 〇点/20点 → 評価コメント\n- **総合バズスコア: 〇点/100点**\n\n## 🔍 問題点の特定（具体的に）\n\n## ✨ 改善版（キャラクター・ジャンル反映）\n完全に書き直した改善版を出力してください。\n\n## 💡 さらに伸ばすためのアドバイス（3つ）';
      }
    },

    sns_comment: { cat: 'sns', icon: '💬', name: 'コメント返信AI', desc: 'キャラを保ったまま褒め・質問・批判に完璧返信。',
      fields: [
        { id: 'comment',      t: 'area',   l: '届いたコメント', ph: '例: 「本当に効果ありましたか？信じていいですか？」', isMainMagic: true },
        { id: 'context',      t: 'text',   l: '元の投稿内容（任意）', ph: '例: 副業で月5万稼いだ方法を投稿した' },
        { id: 'persona',      t: 'select', l: '🎭 あなたのキャラクター', opts: PERSONA_OPTS },
        { id: 'p_custom',     t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'comment_type', t: 'select', l: 'コメントの種類', opts: ['質問・疑問', '批判・クレーム', '褒め・感謝', '煽り・荒らし', '購入相談'] }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, v.p_custom);
        var typeGuide = { '質問・疑問':'疑問を解消しながら信頼感を高め興味を持ってもらう返信', '批判・クレーム':'感情的にならず相手の気持ちに寄り添い冷静に対応する返信', '褒め・感謝':'キャラクターらしく自然に感謝を表現し関係を深める返信', '煽り・荒らし':'スルーか軽くかわしてフォロワーに好印象を与える返信', '購入相談':'押し付けにならず自然にクロージングにつながる返信' };
        var guide = typeGuide[v.comment_type] || typeGuide['質問・疑問'];
        return '# コメント返信AI' + persona +
          '\n\n【元の投稿】'+(v.context?v.context:'（未入力）')+'\n【届いたコメント】\n「'+(v.comment||'')+'」\n【コメント種類】'+(v.comment_type||'質問・疑問')+
          '\n\n目標: '+guide+'\n\nキャラクターの文体・口調を完全に保ちながら、返信を2パターン作成してください：\n\nパターンA（短め・テンポよく）:\n\nパターンB（丁寧・詳しく）:\n\nどちらのパターンが効果的か、理由も1行で添えてください。';
      }
    },

    sns_remix: { cat: 'sns', icon: '🔄', name: '投稿リミックス', desc: '1つの投稿を別キャラ・別媒体に自動変換。',
      fields: [
        { id: 'original',     t: 'area',   l: 'リミックス元の投稿', ph: '変換したい元の投稿文を貼り付けてください', isMainMagic: true },
        { id: 'from_persona', t: 'select', l: '元のキャラクター', opts: PERSONA_OPTS },
        { id: 'to_persona',   t: 'select', l: '🎭 変換後のキャラクター', opts: PERSONA_OPTS },
        { id: 'p_custom',     t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'from_platform',t: 'select', l: '元の媒体', opts: ['X(Twitter)', 'Instagram', 'Threads', 'その他'] },
        { id: 'to_platform',  t: 'select', l: '変換先の媒体', opts: ['X(Twitter)', 'Instagram', 'Threads', 'TikTok台本', 'LINE配信', 'メルマガ', 'ブログ記事'] }
      ],
      build: (v) => {
        var toPersona = getPersonaInstruction(v.to_persona, v.p_custom);
        var platformMap = { 'X(Twitter)':'140字目安。改行多め。最初の1行フック必須。', 'Instagram':'キャプション長めOK。保存・シェアされる構成。ハッシュタグ案も。', 'Threads':'会話的・短め。共感や議論を呼ぶ問いかけ末尾に。', 'TikTok台本':'セリフ形式で。フック3秒→本編→CTAの構成。', 'LINE配信':'絵文字多め・親しみやすく。URLクリックを促す構成。', 'メルマガ':'ヘッダー・本文・PS付きの形式。読者との1対1感。', 'ブログ記事':'SEO意識。見出し(##)・太字・箇条書きで読みやすく。2000字程度。' };
        var toPlatformTips = platformMap[v.to_platform] || '';
        return '# 投稿リミックス' + toPersona +
          '\n\n【元の投稿（'+(v.from_platform||'X')+'・'+(v.from_persona||'元キャラ')+'）】\n'+(v.original||'')+
          '\n\n【変換先】'+(v.to_platform||'Instagram')+'形式\n'+(toPlatformTips?'最適化ポイント: '+toPlatformTips:'')+
          '\n\n元投稿の「内容・伝えたいメッセージ・核心」を完全に保ちながら、変換後のキャラクター・媒体に最適化したバージョンを2パターン作成してください。\n単なる言い換えではなく、そのキャラクターがそのSNSで本当に投稿しそうなリアルな文体にしてください。';
      }
    },

    sns_giveaway: { cat: 'sns', icon: '🎁', name: 'プレゼント企画テンプレ', desc: 'フォロワー爆増プレゼント企画の投稿文を自動生成。',
      fields: [
        { id: 'prize',     t: 'text',   l: 'プレゼント内容', ph: '例: 副業で月5万稼ぐ完全ロードマップPDF', isMainMagic: true },
        { id: 'count',     t: 'select', l: '当選人数', opts: ['1名様', '3名様', '5名様', '10名様'] },
        { id: 'deadline',  t: 'text',   l: '締め切り', ph: '例: 3月31日 23:59' },
        { id: 'persona',   t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
        { id: 'p_custom',  t: 'text',   l: 'カスタムキャラ（「✏️ カスタム」選択時）', ph: '例: 30代元OL、サバサバしているが面倒見が良い' },
        { id: 'platform',  t: 'select', l: '投稿先SNS', opts: ['X(Twitter)', 'Instagram', 'Threads'] },
        { id: 'condition', t: 'select', l: '応募条件', opts: ['フォロー＋いいね', 'フォロー＋リポスト', 'フォロー＋コメント', 'フォロー＋リポスト＋コメント'] }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, v.p_custom);
        return '# プレゼント企画テンプレート生成' + persona +
          '\n\nプレゼント内容: 「'+(v.prize||'')+'」\n当選人数: '+(v.count||'3名様')+'\n締め切り: '+(v.deadline||'近日中')+'\n応募条件: '+(v.condition||'フォロー＋いいね')+'\n投稿先: '+(v.platform||'X(Twitter)')+
          '\n\n以下を生成してください：\n\n## 📣 メイン投稿文（キャラクター反映）\nプレゼントの魅力・希少性・締め切りの緊急性を盛り込み、シェアしたくなる文体で。\n\n## 📌 固定投稿用の詳細版\n応募方法・注意事項・当選発表方法を含む完全版。\n\n## 💬 当選者へのDM文\n温かみがありキャラクターらしい当選連絡メッセージ。\n\n## 📢 結果発表用の投稿文\n落選者にも感謝を伝え、次回企画への期待を高める投稿。';
      }
    },

    // --- 💬 ファン化 ＆ セールス自動化 ---
    freebie: { cat: 'fun', icon: '🎁', name: '無料プレゼント量産', desc: 'LINE登録を促す魅力的なリードマグネット作成。',
      fields: [{ id: 'target', t: 'text', l: 'ターゲット層', ph: '例: ブログ初心者', isMainMagic: true }],
      build: (v) => '# リードマグネット企画\n「'+v.target+'」が思わずLINE登録したくなるような、喉から手が出るほど欲しい無料プレゼント（PDFや動画講座）のアイデアを3つ提案し、そのうち1つの目次構成を作成してください。' },
    line: { cat: 'fun', icon: '💌', name: 'LINE教育ステップ', desc: '5日間でファン化して販売する自動導線。',
      fields: [
        { id: 'prod',  t: 'text', l: '販売商品', ph: '例: 動画編集教材' },
        { id: 'story', t: 'area', l: 'どん底からの成功ストーリー', ph: '例: 手取り15万から独立して月商100万' }
      ],
      build: (v) => '# LINE教育ステップ作成指示\n商品「'+v.prod+'」を販売するために、公式LINE登録者を5日間教育しファン化するシナリオを作成してください。\nユーザーのストーリー「'+v.story+'」を織り込み、信頼構築からオファーまで繋げてください。'
    },
    funnel_diag: { cat: 'fun', icon: '🩺', name: 'ファネル診断コンサル', desc: '現状の導線のボトルネックを特定し改善提案。',
      fields: [{ id: 'current', t: 'area', l: '現状の導線と悩み', ph: '例: Twitter集客→LINE登録はされるが、商品が売れない' }],
      build: (v) => '# ファネル診断\n現状の導線「'+v.current+'」におけるボトルネック（離脱ポイント）を分析し、成約率を改善するための具体的な打ち手と新しい導線設計を提案してください。' },
    reply: { cat: 'fun', icon: '📨', name: 'LINE/DM 神返信', desc: '顧客からの質問やクレームに対する完璧な返信。',
      fields: [{ id: 'msg', t: 'area', l: '相手からのメッセージ', ph: '例: 高くて買えません。安くなりませんか？' }],
      build: (v) => '# 神返信作成\n以下のメッセージに対して、相手の感情に寄り添い、信頼関係を築きつつ、適切な対応をする返信文を2パターン作成してください。\nメッセージ: '+v.msg },
    interview: { cat: 'fun', icon: '🎤', name: 'AIインタビュー', desc: 'あなたの頭の中にあるアイデアをAIが引き出す。',
      fields: [{ id: 'topic', t: 'text', l: '壁打ちしたいテーマ', ph: '例: 新しいオンラインサロンの構想' }],
      build: (v) => '# AIインタビュー\nテーマ「'+v.topic+'」について、私に3つほど鋭い質問を投げかけてください。私の考えを深掘りし、言語化するのを手伝ってください。' },
    journey: { cat: 'fun', icon: '🗺️', name: 'カスタマージャーニー', desc: '顧客が認知から購入・熱狂に至る心理マップ。',
      fields: [{ id: 'prod', t: 'text', l: '商品名', ph: '例: 高級パーソナルジム' }],
      build: (v) => '# カスタマージャーニーマップ作成\n商品「'+v.prod+'」のターゲット顧客が、認知→興味→比較・検討→購入→リピート・口コミに至るまでの各フェーズにおける「思考」「感情」「行動」を表形式で整理してください。' },
    webdev: { cat: 'fun', icon: '💻', name: 'Webアプリ開発支援', desc: 'アイデアからプロトタイプのコードを生成。',
      fields: [{ id: 'idea', t: 'area', l: '作りたいツール案', ph: '例: 食材からレシピを提案するAIアプリ' }],
      build: (v) => '# Webアプリ開発指示\nアイデア「'+v.idea+'」を実現するための、要件定義と1枚のHTML（JavaScript, CSS含む）で動くプロトタイプコードの構造を設計してください。'
    },

    // --- ✨ 無限プロンプト集 (API不要) ---
    stella_blog_prompt: { cat: 'prompt_only', icon: '🌟', name: 'Stella Note式 ブログ構成', desc: '【Stella Note 監修】高品質なブログ構成案を作成するためのプロンプトです。',
      fields: [{ id: 'kw', t: 'text', l: '狙いたいキーワード', ph: '例: AI ツール おすすめ' }],
      build: (v) => '【Stella Note オリジナルプロンプト】\n以下のキーワードで検索上位を狙うブログ記事の構成案（H2, H3見出し）を作成してください。\nキーワード: '+v.kw+'\n\n※検索意図を満たし、読者の悩みを解決する構成にしてください。'
    },
    stella_sns_prompt: { cat: 'prompt_only', icon: '💫', name: 'Stella Note式 SNS投稿', desc: '【Stella Note 監修】キャラ×ジャンル特化でバズるSNS投稿を生成。',
      fields: [
        { id: 'topic',     t: 'area',   l: '伝えたいテーマ', ph: '例: 継続の大切さ' },
        { id: 'persona',   t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
        { id: 'sns_genre', t: 'select', l: '🏷️ ジャンル', opts: GENRE_OPTS }
      ],
      build: (v) => {
        var persona = getPersonaInstruction(v.persona, '');
        var genre = getGenreInstruction(v.sns_genre);
        return '【Stella Note オリジナルプロンプト】' + persona + genre +
          '\n以下のテーマについて、X（Twitter）で共感を呼び、インプレッションが伸びる投稿文を作成してください。\nテーマ: '+(v.topic||'')+
          '\n\n※冒頭に強力なフック（惹きつけ）を入れ、読みやすい改行を心がけてください。';
      }
    }
};