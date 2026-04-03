var SNS_PERSONA_MAP = {
  '🌸 活発な女の子': '明るくテンション高め。感嘆符多め。「やってみた！」「マジで神〜」「最高すぎ」など。ギャル語・略語・絵文字を自然に散りばめ、等身大で共感を生む文体。',
  '💅 おしゃれ大人女子': '丁寧だが親しみある文体。「〜かも」「〜だよね」「ていねいに生きる」感。上品で近寄りやすく、センスを感じさせる。',
  '🧘 ナチュラル系女子': 'ゆったりした文体。ひらがな多め。「のんびり」「ほっこり」「じんわり」系の言葉。自然体で癒し系。急かさない温かさがある。',
  '👩‍💼 できるビジネス女性': '論理的でテンポよい。「結論から言うと」「ポイントは3つ」。端的だが温かみがあり高い信頼感を与える。',
  '😎 クールな男': '端的・断言系。「〜だけ。以上。」スタイル。数字と事実で語る。余計な感情表現を排除。かっこよさと潔さ重視。',
  '🔥 熱血系兄貴': '熱量高め。「お前ら聞けよ」系。読者の背中を強く押す。「絶対できる」「諦めるな」「俺も同じだった」。感情移入させる。',
  '🤓 知識系博士': 'データ・数字・根拠を必ず添える。「研究によると」「統計では」。知的で信頼感があり教育的。マニアックな深掘りが得意。',
  '😄 親しみ系おじさん': '「〜だよね笑」「正直に言うと」経験談多め。失敗談も交えながら共感を生む。人間味あふれる温かい文体。',
  '🤖 AIネイティブ': 'AIを使いこなす人らしいテック感。「効率化」「自動化」「最適解」。モダンで前向き。先進的な視点で語る。',
  '🎮 オタク気質': '深掘り・マニアック。「わかる人だけわかって」感。熱量と専門知識が自然に滲み出る。コアファンを作る文体。',
  '🌍 帰国子女': '日本語に外来語が自然に混ざる。グローバルな視点。「海外では〜」「日本特有の〜」。国際感覚と新鮮な切り口。',
  '✏️ カスタム': ''
};

var SNS_GENRE_MAP = {
  '💰 副業・マネー': { buzz: '「〇万円稼いだ方法」「手取りXX万から」「副業で月収アップ」', caution: '「簡単に稼げる」「誰でも」は景表法に注意', tips: '具体的な金額・期間・手順を数字で示す。再現性を強調。' },
  '💄 美容・コスメ': { buzz: '「使ってみた正直レビュー」「〇日後の肌が」「プチプラ最強」', caution: '「効果が出ます」「治ります」は薬機法に注意', tips: 'ビフォーアフター・価格帯・成分情報を入れる。' },
  '🍽️ グルメ・料理': { buzz: '「作ってみた」「コスパ最強」「リピ確定」「神コスパ」', caution: '', tips: '五感で伝える描写。食感・香り・見た目を具体的に。' },
  '💪 筋トレ・ダイエット': { buzz: '「〇kg落ちた」「継続X日目」「before/after」「習慣化した方法」', caution: '「痩せます」「必ず効果が出る」は薬機法に注意', tips: '数字と期間で結果を具体化。継続の秘訣を入れる。' },
  '📚 学び・スキルアップ': { buzz: '「知らないと損」「〇分でわかる」「まとめた」「保存版」', caution: '', tips: 'リスト形式で情報を整理。保存・シェアされる構成に。' },
  '💼 転職・キャリア': { buzz: '「年収X万アップした」「やめてよかった」「転職で人生変わった」', caution: '', tips: 'リアルな体験談と感情の変化を描写。before/afterを明確に。' },
  '💕 恋愛・婚活': { buzz: '「実体験」「リアルな話」「男性/女性心理」「正直に言うと」', caution: '', tips: '心理学・行動経済学のエビデンスを1つ入れると説得力UP。' },
  '🤱 育児・ファミリー': { buzz: '「〇歳育児」「神アイテム発見」「試してよかった」「育児の真実」', caution: '', tips: '共感フレーズ多め。同じ立場のパパ・ママに刺さる言葉を。' },
  '🌿 ライフスタイル': { buzz: '「暮らしの工夫」「ルーティン公開」「朝活」「シンプルに生きる」', caution: '', tips: '写真映えする描写と生活改善の具体策をセットで。' },
  '🎮 エンタメ・趣味': { buzz: '「やばすぎた」「沼った」「語らせてください」「本気でハマった」', caution: '', tips: '熱量と具体的なおすすめポイントで読者を沼に引き込む。' },
  '🤖 AI・テクノロジー': { buzz: '「これ知らないと置いてかれる」「AIで〇〇分が〇秒に」「衝撃だった」', caution: '', tips: '具体的なツール名・操作手順・活用例を入れる。初心者向けに噛み砕く。' },
  '💹 投資・資産形成': { buzz: '「〇年で〇倍になった」「新NISA活用法」「資産形成の真実」', caution: '「必ず儲かる」は金融商品取引法に注意', tips: '数字と長期視点で信頼感を出す。リスクにも触れる。' }
};

function getPersonaInstruction(personaKey, customPersona) {
  if (customPersona && customPersona.trim()) return '\n\n【🎭 なりきりキャラクター指示】\n以下の人物像になりきって、その人格・文体・口調を完全に憑依させてください：\n「' + customPersona.trim() + '」\nこのキャラクターらしい言葉遣い・テンション・表現を徹底してください。\n';
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

var X_CHAR_LIMIT_OPTS = ['🆓 無料版（140文字以内）', '✅ Premium（280文字以内）', '✅ Premium+（500文字以内）', '✅ Premium+（1,000文字以内）', '✅ Premium+（2,000文字以内）', '✅ Premium+（制限なし・長文スレッド）'];
function getCharLimitInstruction(limitOpt, platform) {
  if (platform !== 'X(Twitter)') return '';
  if (!limitOpt) return '\n\n【文字数】X(Twitter)投稿のため140文字以内を目安にしてください。';
  if (limitOpt.indexOf('制限なし') >= 0) return '\n\n【文字数】制限なし。長文・スレッド形式で書いてください。';
  var m = limitOpt.match(/（(\d[\d,]+)文字以内）/);
  if (!m) return '\n\n【文字数】X(Twitter)投稿のため140文字以内を目安にしてください。';
  return '\n\n【⚠️ 文字数ルール 絶対厳守】\n各パターンの本文を必ず' + m[1].replace(',', '') + '文字以内に収めること。\n出力後に自分で文字数をカウントし、超過していれば削って修正してから出力すること。';
}

var GOAL_OPTS = ['🎯 ゴール指定なし（汎用）', '👥 フォロワー増加', '💌 LINE登録誘導', '📩 DM誘導', '🛒 商品・鑑定購入', '🎁 無料体験・申込み', '🔗 プロフィール誘導'];
function getGoalInstruction(goalOpt) {
  var instructions = {
    'フォロワー増加': '末尾に「フォローするとこういう情報が毎日届きます」という価値提示を入れてください。',
    'LINE登録誘導': '「詳しくはプロフのLINEで▶️」など、LINE登録への動機づけを自然に入れてください。',
    'DM誘導': '「気になった方はDMください」など、DM送信への心理的ハードルを下げる一文を添えてください。',
    '商品・鑑定購入': '希少性（先着○名等）や期限を入れ、購入への緊急性を演出してください。',
    '無料体験・申込み': '「今だけ無料でお試しできます」など、低リスクで試せる訴求を入れてください。',
    'プロフィール誘導': '「詳しくはプロフィールに↑」など、プロフィールへの誘導を入れてください。'
  };
  var key = Object.keys(instructions).find(k => goalOpt.indexOf(k) >= 0) || '';
  return key ? '\n\n【訴求ゴール】\n' + instructions[key] : '';
}

var URANAI_POST_OPTS = ['---【占い系】---', '🔮 今日の運勢', '🃏 カード診断', '💌 無料鑑定案内'];
function getUranaiPostInstruction(postType) { return postType.indexOf('---') >= 0 ? '' : '\n\n【投稿タイプ】' + postType + 'の内容で構成してください。'; }
var FUKUGYO_POST_OPTS = ['---【副業系】---', '✍️ 月収実績報告', '📝 ノウハウ公開', '💡 失敗談'];
function getFukugyoPostInstruction(postType) { return postType.indexOf('---') >= 0 ? '' : '\n\n【投稿タイプ】' + postType + 'の内容で構成してください。'; }

const CATEGORIES = [
    { id: 'omega', name: '🔥 オメガ特級ツール' },
    { id: 'mon',   name: '📝 コンテンツ作成 ＆ 販売' },
    { id: 'cw',    name: '💼 クラウドワークス・仕事完遂' },
    { id: 'sns',   name: '🚀 集客 ＆ SNSアナリティクス' },
    { id: 'fun',   name: '💬 ファン化 ＆ セールス自動化' }
];

const TOOLS = {
    // --- 🔥 オメガ特級ツール ---
    secret_god: { cat: 'omega', icon: '🧿', name: '万能・神の眼', desc: 'あらゆる入力から最適なアウトプットを導き出します。',
      fields: [{ id: 'req', t: 'area', l: '神の要求', ph: '例: この商材を売るためのすべてを教えて' }],
      build: function(v) { return '# 神の要求\n要求: ' + (v.req || ''); } },
    sns_cal: { cat: 'omega', icon: '📅', name: '30日間SNSカレンダー', desc: 'キャラ×ジャンル特化で1ヶ月分のSNS発信内容を自動構築。',
      fields: [
        { id: 'theme',    t: 'text',   l: '発信テーマ', ph: '例: 投資・資産運用', isMainMagic: true },
        { id: 'persona',  t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
        { id: 'genre',    t: 'select', l: '🏷️ 特化ジャンル', opts: GENRE_OPTS }
      ],
      build: function(v) {
        var persona = getPersonaInstruction(v.persona, '');
        var genre = getGenreInstruction(v.genre);
        return '# SNSカレンダー作成指示' + persona + genre + '\nテーマ「' + (v.theme || '') + '」についてのSNS投稿内容を、30日間のカレンダー形式（表：| 日目 | テーマ | 投稿文の要点 |）で作成してください。';
      }
    },
    coconala_gig: { cat: 'omega', icon: '🛍️', name: 'ココナラ無双パッケージ', desc: 'ココナラで売れるサービスページと出品内容を丸ごと作成。',
      help: 'ココナラ（coconala）でサービスを出品するための、検索順位が上がりやすく成約しやすい「サービスタイトル・キャッチコピー・詳細説明文・購入にあたってのお願い」をパッケージとして生成します。',
      fields: [{ id: 'service', t: 'area', l: '提供したいサービスの内容・強み', ph: '例: タロット占い。恋愛相談が得意で、優しい言葉で背中を押します。', isMainMagic: true }],
      build: function(v) { return '# ココナラ出品パッケージ作成\n以下のサービス内容をもとに、ココナラで売れる出品ページを作成してください。\nサービス内容: ' + (v.service || '') + '\n\n以下の構成で出力してください：\n1. 魅力的なサービスタイトル案（3つ）\n2. サービス詳細説明文（coconala形式）\n3. 購入にあたってのお願い（必要情報の案内）\n4. よくある質問（3〜5つ）\n5. サービス画像に入れるべきテキスト案'; }
    },
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
        return '# 値上げ告知文作成\nサービス: ' + (v.service || '') + '\n現在: ' + (v.current_price || '') + ' → 新価格: ' + (v.new_price || '') + '\n実施日: ' + (v.date || '') + '\n理由: ' + (v.reason || '') + '\n\n値上げの正当な理由を説明し、既存顧客への感謝を伝えつつ、値上げ前の駆け込み申し込みを促すSNS告知文を2パターン作成してください。';
      }
    },

    // --- コンテンツ作成 ＆ 販売 ---
    note: { cat: 'mon', icon: '📝', name: 'note記事 究極生成', desc: '売れるnote有料記事を全自動執筆。',
      fields: [
        { id: 'theme',  t: 'text', l: '記事テーマ', ph: '例: スマホ1台で月5万稼ぐ極意', isMainMagic: true },
        { id: 'target', t: 'area', l: '読者の悩み', ph: '例: 副業したいがスキルがない' },
        { id: 'price',  t: 'text', l: '販売金額', ph: '例: 1980円' }
      ],
      build: function(v) { return '# note有料記事 執筆指示\nテーマ: ' + (v.theme||'') + '\n悩み: ' + (v.target||'') + '\n販売金額: ' + (v.price||'') + '\n\n---【タイトル案】---\n5つ\n---【無料エリア】---\n導入\n---【有料エリア】---\n解決策'; }
    },
    lp: { cat: 'mon', icon: '📄', name: '爆売れLP作成', desc: '高単価商品を一撃で成約させるセールスコピー。',
      fields: [{ id: 'prod', t: 'text', l: '商品名・価格', ph: '例: AIコンサル (10万円)', isMainMagic: true }, { id: 'bene', t: 'area', l: '最強のベネフィット', ph: '例: 会社に依存せず自由な収入を手に入れる' }],
      build: function(v) { return '# LP作成指示\n商品「' + (v.prod || '') + '」を販売するためのLPを作成してください。\nベネフィット「' + (v.bene || '') + '」を強調してください。'; } },

    // --- クラウドワークス・仕事完遂 ---
    cw_prop: { cat: 'cw', icon: '✍️', name: 'CW案件獲得 提案文', desc: 'クラウドソーシングで採用される最強の提案文。',
      fields: [{ id: 'job', t: 'area', l: '案件の内容', ph: '例: YouTube動画編集 5000円', isMainMagic: true }],
      build: function(v) { return '# 提案文作成\n案件「' + (v.job || '') + '」に対する魅力的な提案文を作成してください。'; } },
    trans: { cat: 'cw', icon: '🌍', name: '多言語翻訳・納品', desc: 'ニュアンスを保ったプロレベルの翻訳。',
      fields: [{ id: 'text', t: 'area', l: 'テキスト', ph: '例: 翻訳したい文章' }, { id: 'lang', t: 'select', l: '言語', opts: ['英語', '中国語', '韓国語'] }],
      build: function(v) { return '# 翻訳指示\n以下のテキストを' + (v.lang || '英語') + 'に翻訳してください。\n\n' + (v.text || ''); } },

    // --- 集客 ＆ SNSアナリティクス ---
    sns: { cat: 'sns', icon: '📱', name: 'SNS無限集客ポスト', desc: 'キャラ×ジャンル特化でバズる集客投稿を生成。',
      fields: [
        { id: 'platform', t: 'select', l: '投稿先SNS', opts: ['X(Twitter)', 'Instagram', 'Threads'] },
        { id: 'goal',     t: 'select', l: '🎯 訴求ゴール', opts: GOAL_OPTS },
        { id: 'persona',  t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
        { id: 'sns_genre',t: 'select', l: '🏷️ 特化ジャンル', opts: GENRE_OPTS },
        { id: 'content',  t: 'area',   l: '伝えたい内容', ph: '例: 継続が大事', isMainMagic: true }
      ],
      build: function(v) {
        var persona = getPersonaInstruction(v.persona, '');
        var genre = getGenreInstruction(v.sns_genre);
        var goal = getGoalInstruction(v.goal);
        return '# ' + (v.platform || 'X(Twitter)') + ' 投稿作成指示' + persona + genre + goal + '\n\n内容: 「' + (v.content||'') + '」\n\n投稿文を3パターン作成してください。';
      }
    },
    short_vid: { cat: 'sns', icon: '🎬', name: 'ショート動画台本', desc: '視聴者の指が止まる台本を生成。',
      fields: [
        { id: 'topic',    t: 'text',   l: '動画のテーマ', ph: '例: iPhoneの隠し機能', isMainMagic: true },
        { id: 'goal',     t: 'select', l: '🎯 訴求ゴール', opts: GOAL_OPTS },
        { id: 'persona',  t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
        { id: 'sns_genre',t: 'select', l: '🏷 特化ジャンル', opts: GENRE_OPTS },
        { id: 'platform', t: 'select', l: '対象', opts: ['TikTok','Instagram Reels','YouTube Shorts'] }
      ],
      build: function(v) {
        var persona = getPersonaInstruction(v.persona, '');
        var genre = getGenreInstruction(v.sns_genre);
        var goal = getGoalInstruction(v.goal);
        return '# ショート動画台本作成' + persona + genre + goal + '\nテーマ: 「'+(v.topic||'')+'」\n\nフック→本編→CTA の構成で作成してください。';
      }
    },
    
    // --- ファン化 ＆ セールス自動化 ---
    reply: { cat: 'fun', icon: '📨', name: 'LINE/DM 神返信', desc: '顧客からの質問やクレームに対する完璧な返信。',
      fields: [{ id: 'msg', t: 'area', l: '相手のメッセージ', ph: '例: 安くなりませんか？', isMainMagic: true }],
      build: function(v) { return '# 神返信作成\nメッセージ「' + (v.msg || '') + '」に対して、相手に寄り添う返信を2パターン作成してください。'; } },
    freebie: { cat: 'fun', icon: '🎁', name: '無料プレゼント量産', desc: 'LINE登録を促すリードマグネット作成。',
      fields: [{ id: 'target', t: 'text', l: 'ターゲット層', ph: '例: ブログ初心者', isMainMagic: true }],
      build: function(v) { return '# リードマグネット企画\n「' + (v.target || '') + '」がLINE登録したくなる無料プレゼントのアイデアを3つ提案してください。'; } }
};
