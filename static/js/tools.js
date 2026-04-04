// ================================================================
// AICP Pro v74.0.0 - Tools & Specialized Prompts (厳選37種・超特化版)
// カテゴリー: note生成, SNS集客, クラウドワークス, ココナラ副業(占い)
// ================================================================

var SNS_PERSONA_MAP = {
  '🌸 活発な女の子': '明るくテンション高め。感嘆符多め。ギャル語・略語・絵文字を自然に散りばめ、等身大で共感を生む文体。',
  '💅 おしゃれ大人女子': '丁寧だが親しみある文体。「〜かも」「〜だよね」「ていねいに生きる」感。上品で近寄りやすく、センスを感じさせる。',
  '👩‍💼 できるビジネス女性': '論理的でテンポよい。「結論から言うと」「ポイントは3つ」。端的だが温かみがあり高い信頼感を与える。',
  '😎 クールな男': '端的・断言系。「〜だけ。以上。」スタイル。数字と事実で語る。かっこよさと潔さ重視。',
  '🔥 熱血系兄貴': '熱量高め。「お前ら聞けよ」系。読者の背中を強く押す。感情移入させる。',
  '🤓 知識系博士': 'データ・数字・根拠を必ず添える。知的で信頼感があり教育的。',
  '🤖 AIネイティブ': 'AIを使いこなす人らしいテック感。モダンで前向き。先進的な視点で語る。',
  '✏️ カスタム': ''
};

var SNS_GENRE_MAP = {
  '💰 副業・マネー': { buzz: '「〇万円稼いだ方法」「手取りXX万から」', tips: '具体的な金額・期間・手順を数字で示す。再現性を強調。' },
  '💄 美容・コスメ': { buzz: '「使ってみた正直レビュー」「〇日後の肌が」', tips: 'ビフォーアフター・価格帯・成分情報を入れる。' },
  '🍽️ グルメ・料理': { buzz: '「作ってみた」「コスパ最強」「神コスパ」', tips: '五感で伝える描写。食感・香り・見た目を具体的に。' },
  '💪 筋トレ・ダイエット': { buzz: '「〇kg落ちた」「継続X日目」', tips: '数字と期間で結果を具体化。継続の秘訣を入れる。' },
  '💼 転職・キャリア': { buzz: '「年収X万アップした」「やめてよかった」', tips: 'リアルな体験談と感情の変化を描写。before/afterを明確に。' },
  '💕 恋愛・婚活': { buzz: '「実体験」「男性/女性心理」「正直に言うと」', tips: '心理学・行動経済学のエビデンスを1つ入れると説得力UP。' },
  '🤖 AI・テクノロジー': { buzz: '「これ知らないと置いてかれる」「AIで〇分が〇秒に」', tips: '具体的なツール名・操作手順・活用例を入れる。初心者向けに。' }
};

var GOAL_OPTS = ['🎯 ゴール指定なし（汎用）', '👥 フォロワー増加', '💌 LINE公式登録誘導', '📩 DM送信誘導', '🛒 商品・note購入誘導', '🔗 プロフィール誘導'];

function getPersonaInstruction(personaKey, customPersona) {
  if (customPersona && customPersona.trim()) return '\n\n【🎭 憑依ペルソナ】\n以下の人物像になりきって、その人格・文体・口調を完全に憑依させてください：\n「' + customPersona.trim() + '」\n';
  var desc = SNS_PERSONA_MAP[personaKey];
  if (!desc) return '';
  return '\n\n【🎭 憑依ペルソナ】\nキャラクター: ' + personaKey + '\n文体・口調: ' + desc + '\nこのキャラクターになりきって出力してください。\n';
}

function getGenreInstruction(genreKey) {
  var g = SNS_GENRE_MAP[genreKey];
  if (!g) return '';
  return '\n\n【🏷️ ジャンル特化最適化】\nジャンル: ' + genreKey + '\nバズりやすい表現: ' + g.buzz + '\n品質のコツ: ' + g.tips + '\n';
}

function getGoalInstruction(goalOpt) {
  var inst = {
    'フォロワー増加': '末尾に「フォローするとこういう情報が毎日届きます」という読者への価値提示を必ず入れてください。',
    'LINE公式登録誘導': '「詳しくはプロフの公式LINEで」など、LINE登録への強力な動機づけ（限定特典の匂わせ等）を入れてください。',
    'DM送信誘導': '「気になった方はDMください」など、DM送信への心理的ハードルを下げる一文を添えてください。',
    '商品・note購入誘導': '希少性（先着○名等）や期限を入れ、今すぐ購入しなければならないという緊急性を極限まで高めてください。'
  };
  var key = Object.keys(inst).find(k => goalOpt.indexOf(k) >= 0);
  return key ? '\n\n【🎯 達成すべき訴求ゴール】\n' + inst[key] : '';
}

const COMPLIANCE_NG_WORDS = [
    { word: '絶対痩せる', reason: '薬機法違反の恐れ（効果の断言）' },
    { word: '必ず儲かる', reason: '景表法・金融商品取引法違反の恐れ（利益の断言）' },
    { word: '100%治る', reason: '薬機法・医師法違反の恐れ（治療の断言）' },
    { word: '誰でも簡単に100万円', reason: '誇大広告・情報商材詐欺とみなされるリスク' },
    { word: 'ガンが消える', reason: '薬機法違反の恐れ（重大な疾患の治療効果の断言）' }
];

function checkCompliance(text) {
    if (!text) return [];
    const alerts = [];
    COMPLIANCE_NG_WORDS.forEach(rule => { if (text.includes(rule.word)) alerts.push(`「${rule.word}」: ${rule.reason}`); });
    return alerts;
}

const CATEGORIES = [
    { id: 'mon',   name: '📝 note記事 ＆ コンテンツ販売' },
    { id: 'sns',   name: '🚀 SNS集客 ＆ ファン化自動化' },
    { id: 'cw',    name: '💼 クラウドワークス ＆ フリーランス' },
    { id: 'uranai',name: '🔮 ココナラ副業（占い・スピリチュアル）' }
];

const TOOLS = {
    // =========================================================================
    // 1. 📝 note記事 ＆ コンテンツ販売 (全4種)
    // =========================================================================
    note: { cat: 'mon', icon: '📝', name: 'note記事 究極生成', desc: '読者の悩みをえぐり、無料/有料を分けた完璧な記事を執筆。',
      fields: [ { id: 'theme', t: 'text', l: '記事のメインテーマ', ph: '例: スマホ1台で月5万稼ぐ極意', isMainMagic: true }, { id: 'target', t: 'area', l: 'ターゲットの悩み・現状', ph: '例: 副業したいが時間がない、スキルもない' }, { id: 'benefit', t: 'text', l: '読者が得られる究極の未来', ph: '例: 1日30分で月5万の安定収入' }, { id: 'price', t: 'text', l: '販売金額', ph: '例: 1980円' } ],
      build: function(v) { return `テーマ「${v.theme||''}」悩み「${v.target||''}」究極の未来「${v.benefit||''}」価格「${v.price||''}」でnote有料記事を作成してください。\n1. タイトル案5つ\n2. 無料エリア（PASTORフォーマットで痛みに共感し解決策を提示）\n3. 有料エリア（具体的で再現性の高いノウハウ）\n4. SEOハッシュタグ\nの構成で出力してください。`; } },
    
    note_outline: { cat: 'mon', icon: '📑', name: 'プロ向け「目次・構成」ジェネレーター', desc: '離脱させない長文記事の完璧な設計図を作成。',
      fields: [{ id: 'theme', t: 'text', l: '書きたいテーマ', ph: '例: SEO対策', isMainMagic: true }, { id: 'target', t: 'text', l: 'ターゲット読者', ph: '例: ブログ初心者' }],
      build: function(v) { return `テーマ「${v.theme||''}」（ターゲット: ${v.target||''}）について、読者が最後まで離脱せずに読み進める完璧な論理展開を持った「記事の目次構成（H2, H3）」を作成し、各見出しに語るべき核心的な内容のメモを添えてください。`; } },
    
    note_teaser: { cat: 'mon', icon: '🔥', name: '焦らしライティング', desc: '「ここから先は有料」の直前に置く最強の課金フック。',
      fields: [{ id: 'value', t: 'area', l: '有料部分で手に入る価値', ph: '例: ブルーオーシャン市場のリスト', isMainMagic: true }, { id: 'price', t: 'text', l: '価格', ph: '例: 980円' }],
      build: function(v) { return `noteの「ここから先は有料（${v.price||''}）」の直前に配置し、読者の知りたい欲求を極限まで煽り課金率を跳ね上げる【焦らしのフック文章】を、感情訴求型・論理説得型・恐怖回避型で3パターン作成してください。\n価値: ${v.value||''}`; } },
    
    lp: { cat: 'mon', icon: '📄', name: '爆売れセールスレター(LP)作成', desc: '高単価商品を一撃で成約させる最強LPコピー。',
      fields: [{ id: 'prod', t: 'text', l: '商品・サービス名', ph: '例: AIライティング講座', isMainMagic: true }, { id: 'target', t: 'text', l: 'ターゲット', ph: '例: 記事作成に疲れたブロガー' }, { id: 'bene', t: 'area', l: '最大のベネフィット', ph: '例: 執筆時間が1/10になる' }, { id: 'offer', t: 'area', l: '特典/オファー', ph: '例: 全額返金保証' }],
      build: function(v) { return `PASONAの法則を極限まで研ぎ澄ませたLP原稿を作成してください。商品「${v.prod||''}」ターゲット「${v.target||''}」ベネフィット「${v.bene||''}」オファー「${v.offer||''}」。今すぐ買わないと大損する緊急性を提示してください。`; } },
    
    // =========================================================================
    // 2. 🚀 SNS集客 ＆ ファン化自動化 (全12種)
    // =========================================================================
    sns_cal: { cat: 'sns', icon: '📅', name: '30日間SNSカレンダー', desc: 'キャラ×ジャンルで1ヶ月分の投稿計画を自動生成。',
      fields: [{ id: 'theme', t: 'text', l: '発信テーマ', ph: '例: 投資・資産運用', isMainMagic: true }, { id: 'persona', t: 'select', l: '🎭 キャラクター', opts: Object.keys(SNS_PERSONA_MAP) }, { id: 'genre', t: 'select', l: '🏷 特化ジャンル', opts: Object.keys(SNS_GENRE_MAP) }, { id: 'frequency', t: 'select', l: '投稿頻度', opts: ['毎日1投稿', '毎日2投稿'] }],
      build: function(v) { return `テーマ「${v.theme||''}」、頻度「${v.frequency||'毎日1投稿'}」で、30日間分のSNS投稿カレンダーを作成してください。表形式で【日付】【フック(1行目)】【内容の要点】【狙う感情】【ハッシュタグ】を出力してください。` + getPersonaInstruction(v.persona) + getGenreInstruction(v.genre); } },
    
    sns: { cat: 'sns', icon: '📱', name: 'SNS無限集客ポスト', desc: 'スクロールを止めるバズ集客投稿を生成。',
      fields: [{ id: 'platform', t: 'select', l: '投稿先', opts: ['X(Twitter)','Instagram','Threads'] }, { id: 'goal', t: 'select', l: '🎯 訴求ゴール', opts: GOAL_OPTS }, { id: 'persona', t: 'select', l: '🎭 キャラクター', opts: Object.keys(SNS_PERSONA_MAP) }, { id: 'content', t: 'area', l: '伝えたい内容', ph: '例: 継続が大事', isMainMagic: true }, { id: 'emotion', t: 'text', l: '読者に抱かせたい感情', ph: '例: 焦りからの行動喚起' }],
      build: function(v) { return `SNS「${v.platform||'X'}」向けに、内容「${v.content||''}」を魅力的に伝える投稿文を3パターン作成してください。読者に「${v.emotion||'強い関心'}」という感情を抱かせる心理トリガーを組み込んでください。` + getPersonaInstruction(v.persona) + getGoalInstruction(v.goal); } },
    
    acc_design: { cat: 'sns', icon: '🏗️', name: 'バズるアカウントコンセプト設計', desc: '競合と差別化したSNSコンセプトを完全設計。',
      fields: [{ id: 'genre', t: 'text', l: '発信ジャンル', ph: '例: ダイエット', isMainMagic: true }, { id: 'target', t: 'text', l: 'ターゲット層', ph: '例: 産後太りに悩むママ' }],
      build: function(v) { return `ジャンル「${v.genre||''}」（ターゲット: ${v.target||''}）において、競合と差別化し熱狂的なファンを生み出すSNSアカウントのコンセプト設計（アカウント名案、プロフ案、発信軸）を行ってください。`; } },

    sns_analyze: { cat: 'sns', icon: '📈', name: 'SNSインサイト視覚アナリティクス', desc: '画像を解析し、課題解決の戦略をコンサル。',
      fields: [{ id: 'image', t: 'image', l: 'インサイト画像' }, { id: 'goal', t: 'text', l: '目標', ph: '例: フォロワー1万人', isMainMagic: true }, { id: 'issue', t: 'text', l: '現在の課題', ph: '例: プロフアクセス率が低い' }],
      build: function(v) { return `提供されたSNSインサイト画像データと、現在の課題「${v.issue||''}」を分析し、目標「${v.goal||''}」を達成するための根本的な改善点と具体的なアクションプランを3つ提示してください。`; } },
    
    sns_buzz_check: { cat: 'sns', icon: '💯', name: 'バズ診断＆自動改善AI', desc: '投稿文のバズ予測スコアを診断して自動改善。',
      fields: [{ id: 'post', t: 'area', l: '作成した投稿文', ph: '例: 今日も一日頑張ろう', isMainMagic: true }, { id: 'target', t: 'text', l: 'ターゲット層', ph: '例: 20代のフリーランス' }],
      build: function(v) { return `ターゲット「${v.target||''}」に向けて書かれた以下の投稿文の「バズる確率」を100点満点で採点し、より反応率が高まるようにフックや表現を劇的に改善したリライト案を提示してください。\n\n${v.post||''}`; } },

    image: { cat: 'sns', icon: '🎨', name: '画像生成AIプロンプト', desc: 'Midjourney等向けの高品質な英語プロンプト。',
      fields: [{ id: 'desc', t: 'area', l: '描きたい情景', ph: '例: サイバーパンクな東京', isMainMagic: true }],
      build: function(v) { return `Midjourney等の画像生成AIで最高品質の画像を出力するための「英語のプロンプト」を作成してください。被写体、照明、スタイルを含め、出力は英語テキストのみにしてください。情景: ${v.desc||''}`; } },

    eye_catch: { cat: 'sns', icon: '🖼️', name: 'アイキャッチ構成デザイン', desc: '目を引くサムネイル画像用のプロンプト生成。',
      fields: [{ id: 'title', t: 'text', l: '記事/動画のタイトル', ph: '例: やってはいけないNG行動', isMainMagic: true }],
      build: function(v) { return `タイトル「${v.title||''}」のクリック率を極限まで高めるサムネイル画像の構成案（背景、文字の配置、色）と、画像生成AI用のプロンプトを作成してください。`; } },

    sns_comment: { cat: 'sns', icon: '💬', name: 'コメント返信AI', desc: 'キャラを保ったまま褒め・質問・批判に完璧返信。',
      fields: [{ id: 'comment', t: 'text', l: 'もらったコメント', ph: '例: 全然参考になりません', isMainMagic: true }, { id: 'persona', t: 'select', l: '🎭 キャラクター', opts: Object.keys(SNS_PERSONA_MAP) }],
      build: function(v) { return `以下のコメントに対する完璧な返信案を2パターン作成してください。批判的な内容でも神対応でファン化させてください。\n\nコメント: ${v.comment||''}` + getPersonaInstruction(v.persona); } },

    sns_remix: { cat: 'sns', icon: '♻️', name: '投稿リミックス', desc: '1つの投稿を別キャラ・別媒体に自動変換。',
      fields: [{ id: 'post', t: 'area', l: '元の投稿文', ph: '例: ブログ更新しました', isMainMagic: true }],
      build: function(v) { return `以下の投稿文の「コアな主張」を抽出し、全く異なる3つの切り口（ストーリー型、ノウハウ型、箇条書き型）で書き直してください。\n\n${v.post||''}`; } },

    sns_giveaway: { cat: 'sns', icon: '🎁', name: 'プレゼント企画テンプレ', desc: 'フォロワー爆増プレゼント企画の投稿文を生成。',
      fields: [{ id: 'item', t: 'text', l: 'プレゼント内容', ph: '例: Amazonギフト券', isMainMagic: true }, { id: 'cond', t: 'text', l: '参加条件', ph: '例: フォロー＆RT' }],
      build: function(v) { return `プレゼント内容「${v.item||''}」、条件「${v.cond||''}」で、SNSで爆発的に拡散されるプレゼント企画の投稿文を作成してください。煽り文句と期限を含めてください。`; } },

    profile_writer: { cat: 'sns', icon: '👤', name: 'SNSプロフィール文ジェネレーター', desc: '集客力が上がるプロフィール文を作成。',
      fields: [{ id: 'job', t: 'text', l: '職業・肩書き', ph: '例: AIコンサルタント', isMainMagic: true }, { id: 'achieve', t: 'text', l: '実績', ph: '例: 支援企業50社' }],
      build: function(v) { return `肩書き「${v.job||''}」、実績「${v.achieve||''}」をもとに、読者がフォローしたくなる魅力的なプロフィール文を作成してください。`; } },

    freebie: { cat: 'sns', icon: '📥', name: '無料プレゼント量産アイデア', desc: 'LINE登録を促すリードマグネット作成。',
      fields: [{ id: 'target', t: 'text', l: 'ターゲット顧客', ph: '例: ダイエット中の主婦', isMainMagic: true }],
      build: function(v) { return `ターゲット「${v.target||''}」が喉から手が出るほど欲しがる、公式LINE登録特典（無料プレゼント）のアイデアを3つ提案し、その目次案も作成してください。`; } },

    // =========================================================================
    // 3. 💼 クラウドワークス ＆ フリーランス (全12種)
    // =========================================================================
    cw_prop: { cat: 'cw', icon: '✉️', name: '採用率99% 案件獲得提案文', desc: 'クラウドソーシングで採用される最強の提案文。',
      fields: [{ id: 'job', t: 'area', l: '案件内容', ph: '例: YouTube動画編集', isMainMagic: true }, { id: 'skill', t: 'text', l: '自分の強み', ph: '例: 納期厳守、即レス' }, { id: 'portfolio', t: 'text', l: '実績', ph: '例: 美容系動画を10本作成' }],
      build: function(v) { return `案件「${v.job||''}」に対し、強み「${v.skill||''}」実績「${v.portfolio||''}」を自然にアピールし、クライアントが即決する提案文を作成してください。`; } },
    
    cw_profile: { cat: 'cw', icon: '🏆', name: 'プラチナランク プロフィール構築', desc: '「この人に頼みたい」と思わせるプロフィール文。',
      fields: [{ id: 'skill', t: 'area', l: 'スキル・経歴', ph: '例: 事務歴5年、Excel得意', isMainMagic: true }, { id: 'target', t: 'text', l: '獲得したい案件', ph: '例: YouTubeの動画編集' }],
      build: function(v) { return `以下の情報から圧倒的な信頼感のあるプロフィール文を作成してください。「経歴: ${v.skill||''}」「狙う案件: ${v.target||''}」。プロとしてのスタンスを明確にしてください。`; } },
    
    cw_hearing: { cat: 'cw', icon: '📋', name: 'プロのヒアリングシート生成', desc: 'クライアントの真のニーズを引き出す質問リスト。',
      fields: [{ id: 'project', t: 'area', l: '案件の概要', ph: '例: 美容系Instagramの運用', isMainMagic: true }, { id: 'client_level', t: 'select', l: 'クライアントの知識', opts: ['IT知識なし', '一般的な担当者', '専門知識あり'] }],
      build: function(v) { return `以下の案件でクライアントの「真のニーズ」を引き出すヒアリングシートを作成してください。相手は「${v.client_level||''}」です。質問の意図も添えてください。\n\n${v.project||''}`; } },
    
    cw_delivery: { cat: 'cw', icon: '🎁', name: '「神納品」メッセージ＆アップセル', desc: '納品報告と同時に次回リピート案件を獲得する。',
      fields: [{ id: 'work', t: 'text', l: '納品した成果物', ph: '例: 動画編集', isMainMagic: true }, { id: 'effort', t: 'text', l: '工夫した点', ph: '例: テンポを早めた' }, { id: 'next_step', t: 'text', l: '次回提案', ph: '例: サムネイル作成' }],
      build: function(v) { return `クライアントに感動を与える納品報告を作成してください。納品物「${v.work||''}」、工夫点「${v.effort||''}」を伝え、次回案件「${v.next_step||''}」への自然なアップセルを行ってください。`; } },
      
    high_ticket: { cat: 'cw', icon: '💰', name: '高単価案件ハンター', desc: '低単価から抜け出すためのスキル掛け合わせ提案。',
      fields: [{ id: 'skill', t: 'text', l: '現在のスキル', ph: '例: ただの動画編集', isMainMagic: true }, { id: 'current_price', t: 'text', l: '現在の単価感', ph: '例: 1本3000円' }],
      build: function(v) { return `現在のスキル「${v.skill||''}」（単価: ${v.current_price||''}）から単価を3倍以上にするための「スキルの掛け合わせ提案」と、狙うべき高単価市場を提案してください。`; } },
    
    nego: { cat: 'cw', icon: '🤝', name: '報酬・単価交渉AI', desc: '角を立てずに単価アップを交渉するメッセージ。',
      fields: [{ id: 'reason', t: 'text', l: '単価アップの理由', ph: '例: 作業範囲が増えたため', isMainMagic: true }, { id: 'desired_price', t: 'text', l: '希望する新単価', ph: '例: 1本5000円' }],
      build: function(v) { return `クライアントとの良好な関係を保ちつつ、プロとして正当な評価を得るための「単価アップ交渉メッセージ」を作成してください。理由「${v.reason||''}」、希望単価「${v.desired_price||''}」。`; } },

    seo: { cat: 'cw', icon: '🎯', name: 'SEO特化ブログ記事作成', desc: '検索上位を狙うためのSEO最適化記事を作成。',
      fields: [{ id: 'kw', t: 'text', l: '狙うキーワード', ph: '例: 仮想通貨 初心者', isMainMagic: true }, { id: 'target', t: 'text', l: '想定読者', ph: '例: 投資を始めたい20代' }],
      build: function(v) { return `キーワード「${v.kw||''}」（想定読者: ${v.target||''}）で検索1位を取るための、SEOに特化したブログ記事の構成（H2, H3）と、検索意図を満たす高品質な本文を作成してください。