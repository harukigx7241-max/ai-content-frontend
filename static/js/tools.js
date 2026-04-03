// ================================================================
// AICP Pro v73.0.0 - Tools & Specialized Prompts
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

var GOAL_OPTS = ['🎯 ゴール指定なし（汎用）', '👥 フォロワー増加', '💌 LINE登録誘導', '📩 DM誘導', '🛒 商品・鑑定購入', '🔗 プロフィール誘導'];

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
    'フォロワー増加': '末尾に「フォローするとこういう情報が毎日届きます」という価値提示を必ず入れてください。',
    'LINE登録誘導': '「詳しくはプロフのLINEで」など、LINE登録への強力な動機づけを入れてください。',
    'DM誘導': '「気になった方はDMください」など、DM送信への心理的ハードルを下げる一文を添えてください。',
    '商品・鑑定購入': '希少性（先着○名等）や期限を入れ、購入への緊急性を極限まで高めてください。'
  };
  var key = Object.keys(inst).find(k => goalOpt.indexOf(k) >= 0);
  return key ? '\n\n【🎯 達成すべき訴求ゴール】\n' + inst[key] : '';
}

// ================================================================
// コンプライアンス・チェッカー機能
// ================================================================
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
    COMPLIANCE_NG_WORDS.forEach(rule => {
        if (text.includes(rule.word)) alerts.push(`「${rule.word}」: ${rule.reason}`);
    });
    return alerts;
}

// ================================================================
// ツール定義（全52種）
// ================================================================
const CATEGORIES = [
    { id: 'omega', name: '🔥 オメガ特級ツール' },
    { id: 'cw',    name: '💼 クラウドワークス・仕事完遂' },
    { id: 'uranai',name: '🔮 占い・スピリチュアル特化' },
    { id: 'mon',   name: '📝 note記事 ＆ 販売' },
    { id: 'sns',   name: '🚀 集客 ＆ SNSアナリティクス' },
    { id: 'fun',   name: '💬 ファン化 ＆ セールス自動化' }
];

const TOOLS = {
    // --- 🔥 オメガ特級ツール ---
    secret_god: { cat: 'omega', icon: '🧿', name: '万能・神の眼', desc: 'あらゆる入力から最適なアウトプットを導き出します。',
      fields: [{ id: 'req', t: 'area', l: '神への要求', ph: '例: この商材を売るためのすべてを教えて', isMainMagic: true }],
      build: function(v) { return 'あなたは森羅万象を知る全知全能の神（トップコンサルタント）です。\n\n【神への要求】\n' + (v.req || ''); } 
    },
    sns_cal: { cat: 'omega', icon: '📅', name: '30日間SNSカレンダー（特化版）', desc: 'キャラ×ジャンル特化で1ヶ月分の投稿計画を自動生成',
      help: 'キャラクター×ジャンルで差別化された30日分のSNS投稿計画を自動生成します。各日の投稿内容・ハッシュタグ・最適投稿時間付き。',
      fields: [
        { id: 'theme',    t: 'text',   l: '発信テーマ', ph: '例: 投資・資産運用', isMainMagic: true },
        { id: 'persona',  t: 'select', l: '🎭 キャラクター', opts: Object.keys(SNS_PERSONA_MAP) },
        { id: 'genre',    t: 'select', l: '🏷 特化ジャンル', opts: Object.keys(SNS_GENRE_MAP) }
      ],
      build: function(v) {
        var persona = getPersonaInstruction(v.persona, '');
        var genre = getGenreInstruction(v.genre);
        return 'あなたは累計100万フォロワーを生み出した天才SNSマーケターです。\n' + persona + genre + '\n【指令】\nテーマ「' + (v.theme||'') + '」について、30日間分のSNS投稿カレンダーを作成してください。各日の「テーマ」「投稿のフック(1行目)」「内容の要点」「ハッシュタグ」を表形式（Markdown）で出力してください。';
      }
    },
    coconala_gig: { cat: 'omega', icon: '🛍️', name: 'ココナラ無双パッケージ', desc: 'ココナラで売れるサービスページと出品内容を丸ごと作成。',
      fields: [{ id: 'service', t: 'area', l: '提供したいサービスの内容・強み', ph: '例: タロット占い。恋愛相談が得意。', isMainMagic: true }],
      build: function(v) { return 'あなたはココナラで月商500万円を売り上げるトップ出品コンサルタントです。\n以下のサービス内容をもとに、検索上位を独占し、見た瞬間に購入される完璧な出品パッケージを作成してください。\n\n【サービス内容】\n' + (v.service || '') + '\n\n【必須出力項目】\n1. 魅力的なサービスタイトル案（3つ）\n2. サービス詳細説明文（coconala形式）\n3. 購入にあたってのお願い\n4. よくある質問（3〜5つ）\n5. サービス画像に入れるべきキャッチコピー'; }
    },

    // --- 💼 クラウドワークス・仕事完遂 ---
    cw_profile: { cat: 'cw', icon: '🏆', name: 'プロフィール＆ポートフォリオ構築AI', desc: 'クラウドワークスで「この人に頼みたい」と思わせるプロフィール。',
      fields: [{ id: 'skill', t: 'area', l: 'あなたのスキル・経歴', ph: '例: 事務歴5年、Excel得意、動画編集を最近始めた', isMainMagic: true }, { id: 'target', t: 'text', l: '獲得したい案件', ph: '例: YouTubeの動画編集' }],
      build: function(v) { return 'あなたはクラウドソーシングで採用率95%を誇るトップフリーランスのプロデューサーです。\n以下の情報を元に、クライアントが「どうしてもこの人に依頼したい」と感じる、圧倒的に信頼感のあるプロフィール文と自己PR文を作成してください。\n\n【経歴・スキル】\n' + (v.skill||'') + '\n【狙う案件】\n' + (v.target||''); }
    },
    cw_hearing: { cat: 'cw', icon: '📋', name: 'プロのヒアリングシート生成', desc: '案件受注時にクライアントの真のニーズを引き出す質問リスト。',
      fields: [{ id: 'project', t: 'area', l: '案件の概要', ph: '例: 美容系Instagramの運用代行', isMainMagic: true }],
      build: function(v) { return 'あなたは一流のプロジェクトマネージャーです。\n以下の案件を受注するにあたり、クライアントの「真のニーズ（潜在的な目的）」を引き出し、かつ「この人はプロだ」と信頼させるためのヒアリングシート（質問リスト）を5〜7項目作成してください。質問の意図も添えてください。\n\n【案件概要】\n' + (v.project||''); }
    },
    cw_delivery: { cat: 'cw', icon: '🎁', name: '「神納品」メッセージ＆次回提案', desc: '納品報告と同時に次回リピート案件を獲得する魔法のメッセージ。',
      fields: [{ id: 'work', t: 'text', l: '納品した成果物', ph: '例: 10分のYouTube動画編集', isMainMagic: true }, { id: 'effort', t: 'text', l: '今回特に工夫した点', ph: '例: 視聴維持率が上がるよう、最初の5秒のテンポを早めました' }],
      build: function(v) { return 'あなたはリピート率100%の超一流フリーランスです。\n以下の内容をもとに、クライアントに感動を与える「納品報告メッセージ」を作成してください。\nただの報告ではなく、工夫点をアピールし、さらに「次回はこんなこともできますがいかがですか？」という自然な継続案件へのアップセル（提案）を必ず含めてください。\n\n【納品物】' + (v.work||'') + '\n【工夫点】' + (v.effort||''); }
    },

    // --- 🔮 占い・スピリチュアル特化 ---
    uranai_kantei: { cat: 'uranai', icon: '🔮', name: '占い鑑定書ライター', desc: '有料販売に耐えるプロ品質の長文鑑定書を生成。',
      fields: [{ id: 'method', t: 'select', l: '占術', opts: ['タロット','西洋占星術','四柱推命','霊感・霊視'] }, { id: 'client', t: 'area', l: '相談者情報と悩み', ph: '例: 28歳女性。転職すべきか悩んでいる', isMainMagic: true }],
      build: function(v) { return 'あなたは予約が数ヶ月取れない、慈愛と的確さを兼ね備えたカリスマ占い師です。\n【占術】' + (v.method||'') + '\n【相談者】' + (v.client||'') + '\n\n上記の相談者に対し、有料（5000円相当）で提供するプロ品質の鑑定書を2000文字以上で作成してください。導入（寄り添い）→鑑定結果（詳細な解釈）→具体的アドバイス→希望を持てるまとめ、の構成にしてください。'; }
    },
    uranai_age: { cat: 'uranai', icon: '👼', name: 'アゲ鑑定（ポジティブ変換）推敲', desc: '悪い結果を嘘をつかずに「希望」に変換する魔法のツール。',
      fields: [{ id: 'bad_result', t: 'area', l: '出た悪い結果', ph: '例: 彼はあなたに冷めており、復縁の可能性は低いです。', isMainMagic: true }],
      build: function(v) { return 'あなたはクレーム率0%、リピート率100%を誇る慈愛に満ちたトップ占い師です。\n以下の「ネガティブな鑑定結果」を、絶対に嘘で上塗りすることなく、相談者が前向きに受け取れ、未来への希望の光を見出せる「温かく建設的なアドバイス（アゲ鑑定）」の文章にリライトしてください。\n\n【元のネガティブな結果】\n' + (v.bad_result||''); }
    },
    uranai_menu: { cat: 'uranai', icon: '✨', name: '独自占術・メニュー開発AI', desc: 'ライバル不在の高単価オリジナルメニューを企画。',
      fields: [{ id: 'base', t: 'text', l: 'ベースの占術・得意なこと', ph: '例: タロットと、心理カウンセリング', isMainMagic: true }],
      build: function(v) { return 'あなたはスピリチュアル業界の凄腕マーケターです。\n以下のベーススキルを元に、ココナラ等で1万円以上の高単価で売れる「ライバル不在のオリジナル独自占術（メニュー）」のコンセプト案を3つ提案してください。それぞれに魅力的な「メニュー名」と「どんな悩みを解決できるか」を含めてください。\n\n【ベーススキル】\n' + (v.base||''); }
    },
    uranai_follow: { cat: 'uranai', icon: '💌', name: 'アフターフォロー（リピート）生成', desc: '鑑定後1ヶ月に送り、自然にリピート依頼を発生させるメッセージ。',
      fields: [{ id: 'memo', t: 'text', l: '前回の相談内容', ph: '例: 職場の人間関係についてのタロット占い', isMainMagic: true }],
      build: function(v) { return 'あなたはクライアントから深く愛されている占い師です。\n以前「' + (v.memo||'') + '」について鑑定した相談者に対し、鑑定から1ヶ月後に送るアフターフォローメッセージを作成してください。「その後お加減いかがですか？」という心からの気遣いと、押し売りにならない自然な形での再鑑定（リピート）への導線を含めてください。'; }
    },

    // --- 📝 note記事 ＆ 販売 ---
    note: { cat: 'mon', icon: '📝', name: 'note記事 究極生成', desc: '売れるnote有料記事を全自動執筆。',
      fields: [{ id: 'theme', t: 'text', l: '記事テーマ', ph: '例: スマホ1台で月5万稼ぐ極意', isMainMagic: true }, { id: 'target', t: 'area', l: '読者の悩み', ph: '例: 副業したいが時間がない' }, { id: 'price', t: 'text', l: '販売金額', ph: '例: 1980円' }],
      build: function(v) { return 'あなたは累計1億円を売り上げたnote作家兼プロのダイレクトレスポンスコピーライターです。\n【テーマ】' + (v.theme||'') + '\n【読者の悩み】' + (v.target||'') + '\n【価格】' + (v.price||'') + '\n\n読者の「潜在的な痛み」を分析し、それを解決できる唯一の手段がこの記事であるという論理展開で執筆してください。必ず以下の区切り線を使って出力してください。\n\n---【タイトル案】---\n（クリックしたくなるタイトル5案）\n---【無料エリア】---\n（読者を強烈に惹きつけ、課金せずにはいられなくする導入）\n---【有料エリア】---\n（圧倒的に有益な解決策・ノウハウ本文）\n---【SEO・ハッシュタグ】---'; }
    },
    note_outline: { cat: 'mon', icon: '📑', name: 'プロ向け「目次・構成」ジェネレーター', desc: '長文記事を書くための完璧な設計図（アウトライン）を作成。',
      fields: [{ id: 'theme', t: 'text', l: '書きたいテーマ', ph: '例: 初心者向けSEO対策', isMainMagic: true }],
      build: function(v) { return 'あなたはGoogleの検索アルゴリズムを熟知したトップSEO専門家であり、ベストセラー編集者です。\nテーマ「' + (v.theme||'') + '」について、読者が最後まで離脱せずに読み進め、最終的に満足感（または商品購入）に至るための、完璧な論理展開を持った「記事の目次構成（H2, H3見出し）」を作成してください。各見出しの横に「そこで何を語るべきか」の簡単なメモも添えてください。'; }
    },
    note_teaser: { cat: 'mon', icon: '🔥', name: '有料境界線直前の「焦らし」ライティング', desc: 'ここから先は有料です、の直前に置く最強の課金フック。',
      fields: [{ id: 'value', t: 'area', l: '有料部分で得られる最大の価値', ph: '例: 誰も知らない競合不在のブルーオーシャン市場のリスト', isMainMagic: true }],
      build: function(v) { return 'あなたは天才的なセールスライターです。\nnoteやBrainの「ここから先は有料です」という境界線の直前に配置し、読者の「知りたい欲求」を極限まで煽り、課金率（CVR）を跳ね上げる【焦らしのフック文章】を3パターン作成してください。\n\n【有料部分の価値】\n' + (v.value||''); }
    },
    lp: { cat: 'mon', icon: '📄', name: '爆売れLP作成', desc: '高単価商品を一撃で成約させるセールスコピー。',
      fields: [{ id: 'prod', t: 'text', l: '商品名', ph: '例: AIコンサル', isMainMagic: true }, { id: 'bene', t: 'area', l: '最大のベネフィット', ph: '例: 自由な時間を手に入れる' }],
      build: function(v) { return 'あなたは世界トップクラスのダイレクトレスポンスコピーライターです。\n商品「' + (v.prod||'') + '」を販売するためのLPを作成してください。PASONAの法則を用い、ベネフィット「' + (v.bene||'') + '」を強調し、読者が今すぐ買わないと大損すると感じさせる圧倒的なセールスコピーを書いてください。'; }
    },

    // --- 🚀 集客 ＆ SNSアナリティクス ---
    sns: { cat: 'sns', icon: '📱', name: 'SNS無限集客ポスト', desc: 'キャラ×ジャンル特化でバズる集客投稿を生成。',
      fields: [{ id: 'platform', t: 'select', l: '投稿先SNS', opts: ['X(Twitter)', 'Instagram', 'Threads'] }, { id: 'goal', t: 'select', l: '🎯 訴求ゴール', opts: GOAL_OPTS }, { id: 'persona', t: 'select', l: '🎭 キャラクター', opts: Object.keys(SNS_PERSONA_MAP) }, { id: 'content', t: 'area', l: '伝えたい内容', ph: '例: 継続が大事', isMainMagic: true }],
      build: function(v) {
        var persona = getPersonaInstruction(v.persona, '');
        var goal = getGoalInstruction(v.goal);
        return 'あなたは「' + (v.platform||'X(Twitter)') + '」のアルゴリズムをハックし、累計100万フォロワーを熱狂させる天才コピーライターです。\n' + persona + goal + '\n【指令】\n内容「' + (v.content||'') + '」について、スクロールする指を強制的に止める「強烈なフック(1行目)」を持ち、読者の共感と有益性を提供する投稿文を3パターン作成してください。';
      }
    },
    note_promo: { cat: 'sns', icon: '📢', name: '記事連動・SNSプロモーション生成', desc: '公開したnoteや記事をSNSで拡散して売るための宣伝ポスト。',
      fields: [{ id: 'summary', t: 'area', l: '記事の概要や魅力', ph: '例: 知識ゼロから月5万稼ぐ手順を網羅したロードマップ', isMainMagic: true }],
      build: function(v) { return 'あなたはSNSマーケティングの天才です。\n以下の記事をX(Twitter)等のSNSで宣伝し、クリックして読ませるためのプロモーション投稿文を以下の3つの切り口で作成してください。\n1. 圧倒的な権威性と実績をアピールする型\n2. 読者の悩みに寄り添い解決策を提示する型\n3. 記事の一部をチラ見せして続きを気にならせる型\n\n【記事概要】\n' + (v.summary||''); }
    },

    // --- 💬 ファン化 ＆ セールス自動化 ---
    reply: { cat: 'fun', icon: '📨', name: 'LINE/DM 神返信', desc: '顧客からの質問やクレームに対する完璧な返信。',
      fields: [{ id: 'msg', t: 'area', l: '相手のメッセージ', ph: '例: 安くなりませんか？', isMainMagic: true }],
      build: function(v) { return 'あなたはカスタマーサクセスの世界的なプロフェッショナルです。\n以下の顧客メッセージに対し、相手の感情に深く寄り添い、決して怒らせることなく、最終的にブランドへの信頼（または成約）へとつなげる「神対応」の返信文を2パターン作成してください。\n\n【顧客のメッセージ】\n' + (v.msg||''); }
    },
    price_up: { cat: 'fun', icon: '📈', name: '値上げ告知ジェネレーター', desc: '既存顧客を逃がさず「今すぐ申込もう」と思わせる告知文。',
      fields: [{ id: 'service', t: 'text', l: 'サービス名', ph: '例: タロット鑑定', isMainMagic: true }, { id: 'current_price', t: 'text', l: '現在の価格', ph: '例: 3000円' }, { id: 'new_price', t: 'text', l: '値上げ後の価格', ph: '例: 5000円' }],
      build: function(v) { return 'あなたはファンマーケティングのプロです。\nサービス「' + (v.service||'') + '」を ' + (v.current_price||'') + ' から ' + (v.new_price||'') + ' に値上げする告知文を作成してください。\n既存顧客への深い感謝、正当な値上げ理由（価値の向上等）を伝えつつ、値上げ前の「駆け込み申し込み」を強烈に促す文章にしてください。'; }
    }
};

window.AICP_TOOLS = TOOLS;
window.AICP_CATEGORIES = CATEGORIES;
window.checkCompliance = checkCompliance;