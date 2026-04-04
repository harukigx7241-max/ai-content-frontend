'use strict';
// ============================================================
//  tools.js – 全35ツール定義 & プロンプトロジック
// ============================================================

// ── カテゴリ定義 ────────────────────────────────────────────
const CATEGORIES = [
  { id: 'note',     name: 'note記事 & コンテンツ販売',        emoji: '📝', count: 8  },
  { id: 'sns',      name: 'SNS集客 & ファン化自動化',          emoji: '🚀', count: 10 },
  { id: 'crowd',    name: 'クラウドワークス & フリーランス',   emoji: '💼', count: 8  },
  { id: 'coconala', name: 'ココナラ副業（占い・スピリチュアル）', emoji: '🔮', count: 9  },
];

// ── コンプライアンスNGワード ────────────────────────────────
const COMPLIANCE_NG_WORDS = [
  '絶対に痩せる','必ず痩せる','確実に痩せる','絶対痩せ','痩せる効果を保証',
  '必ず儲かる','絶対に儲かる','確実に稼げる','絶対儲かる','確実に稼げます',
  '100%効果がある','効果を保証','成果を保証します','絶対に成功',
  '失敗しない','誰でも必ず','楽して稼げる','楽に稼ぐ','誰でも稼げる',
  '副作用なし','完全に治る','病気が治る','治療効果',
  '100%成功','必ずバズる','絶対バズ',
];

// ── 天才ペルソナ（カテゴリ別） ──────────────────────────────
const GENIUS_PERSONAS = {
  note:     'あなたは累計10億円の売上を誇る日本最高峰のnoteクリエイター兼トップコピーライターです。読者の深層心理を完璧に理解し、無料公開エリアで強烈な価値を提供しながら有料購入へ自然に誘導する、conversion率90%超の記事を書きます。',
  sns:      'あなたは複数のSNSで100万フォロワーを持つ日本最高峰のSNSマーケターです。アルゴリズムを熟知し、1投稿でフォロワーを数百人獲得するバズコンテンツを量産する天才です。',
  crowd:    'あなたはクラウドワークスで月収200万円を稼ぐ日本最高峰のフリーランサーです。クライアントの心理を完璧に読み、採用率99%の提案文と最高の成果物で次々と高単価案件を獲得し続けています。',
  coconala: 'あなたはココナラで年間5000件以上の鑑定をこなし、リピート率98%を誇る日本最高峰の占い・スピリチュアル専門家です。クライアントの心に深く響き、人生を変える鑑定書と出品ページを作成します。',
};

// ── inputフィールドのtype定義 ────────────────────────────────
// type: 'text' | 'textarea' | 'select' | 'number'

// ── プロンプトビルダーユーティリティ ────────────────────────
function v(vals, key, fallback='（AIが最適な内容を自動設定）') {
  const val = vals[key];
  return (val && val.toString().trim()) ? val.toString().trim() : fallback;
}

// ============================================================
//  TOOLS 定義
// ============================================================
const TOOLS = [

  // ── 1. note記事 究極生成 ─────────────────────────────────
  {
    id: 'note_ultimate', category: 'note', emoji: '✍️',
    name: 'note記事 究極生成',
    description: '読者の悩みをえぐり、無料/有料を分けた完璧なnote記事を執筆',
    inputs: [
      { id: 'theme',     label: 'テーマ・ジャンル',         type: 'text',     placeholder: '例: SNSで月10万円を稼ぐ方法' },
      { id: 'target',    label: 'ターゲット読者',            type: 'text',     placeholder: '例: 副業初心者の20〜30代会社員' },
      { id: 'price',     label: '有料部分の価格（円）',      type: 'text',     placeholder: '例: 500' },
      { id: 'keywords',  label: 'キーワード（カンマ区切り）',type: 'text',     placeholder: '例: SNS, 副業, 在宅ワーク' },
      { id: 'unique',    label: '独自の経験・強み',          type: 'textarea', placeholder: '例: 会社員しながら半年でフォロワー1万人を達成した経験' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `以下の条件で高品質なnote記事を生成してください。

テーマ: ${v(vals,'theme')}
ターゲット: ${v(vals,'target')}
有料価格: ${v(vals,'price','500')}円
キーワード: ${v(vals,'keywords')}
独自経験: ${v(vals,'unique')}

【出力形式】以下の区切り文字で明確に分けてください:
---【タイトル】---
（思わずクリックしたくなる強烈なタイトル案を3つ）

---【無料エリア】---
（導入・共感・問題提起・価値提供の予告。1200字以上）

---【有料エリア】---
（具体的手法・実践ステップ・事例。2000字以上）` },
      ];
    },
  },

  // ── 2. プロ向け目次・構成ジェネレーター ─────────────────
  {
    id: 'note_structure', category: 'note', emoji: '📋',
    name: 'プロ向け「目次・構成」ジェネレーター',
    description: '離脱させない長文記事の完璧な設計図を作成',
    inputs: [
      { id: 'theme',    label: '記事テーマ',      type: 'text',   placeholder: '例: フリーランスとして月50万円稼ぐ方法' },
      { id: 'level',    label: '読者レベル',       type: 'select', options: ['初心者向け','中級者向け','上級者向け'] },
      { id: 'length',   label: '目標文字数',       type: 'text',   placeholder: '例: 5000字' },
      { id: 'goal',     label: '記事を読んだ後の読者の変化', type: 'textarea', placeholder: '例: 明日から行動できる具体的なステップが分かる' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `以下の条件で完璧な記事構成・目次を作成してください。

テーマ: ${v(vals,'theme')}
読者レベル: ${v(vals,'level','初心者向け')}
目標文字数: ${v(vals,'length','5000字')}
読後の変化: ${v(vals,'goal')}

【出力】
・タイトル案（3つ）
・リード文の方向性
・章立て構成（H2・H3含む詳細な目次）
・各セクションで伝える核心ポイント
・読者を有料へ誘導するフックの配置案` },
      ];
    },
  },

  // ── 3. 焦らしライティング ────────────────────────────────
  {
    id: 'note_tease', category: 'note', emoji: '🔒',
    name: '焦らしライティング',
    description: '「ここから先は有料」の直前に置く最強の課金フック',
    inputs: [
      { id: 'content',  label: '有料コンテンツの内容',     type: 'textarea', placeholder: '例: 月収100万円達成のための具体的な5ステップ' },
      { id: 'target',   label: 'ターゲット読者の悩み',     type: 'textarea', placeholder: '例: 副業を始めたいけど何から手をつければいいか分からない' },
      { id: 'price',    label: '価格',                     type: 'text',     placeholder: '例: 980円' },
      { id: 'benefit',  label: '購入後に得られる最大の恩恵', type: 'text',   placeholder: '例: 最短1ヶ月で初収益を達成できる' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `有料コンテンツ購入率を最大化する「焦らしライティング」を生成してください。

有料コンテンツの内容: ${v(vals,'content')}
読者の悩み: ${v(vals,'target')}
価格: ${v(vals,'price','980円')}
購入後の最大恩恵: ${v(vals,'benefit')}

【要件】
・読者が「これを知らないと損だ」と感じるよう焦らす
・有料部分のネタバレをせずに価値を最大限に予感させる
・購入への心理的ハードルを最小化するセリフ
・300〜500字で、有料エリア直前に置くテキストとして完成させる` },
      ];
    },
  },

  // ── 4. 爆売れセールスレター(LP)作成 ─────────────────────
  {
    id: 'note_lp', category: 'note', emoji: '🎯',
    name: '爆売れセールスレター(LP)作成',
    description: '高単価商品を一撃で成約させる最強LPコピー',
    inputs: [
      { id: 'product',  label: '商品・サービス名',   type: 'text',     placeholder: '例: SNSマネタイズ完全マスター講座' },
      { id: 'price',    label: '価格',               type: 'text',     placeholder: '例: 29,800円' },
      { id: 'target',   label: 'ターゲット',          type: 'textarea', placeholder: '例: SNSを始めたばかりで収益化できていない30代会社員' },
      { id: 'benefits', label: '主要ベネフィット',    type: 'textarea', placeholder: '例: 90日でフォロワー1万人達成、月収10万円の仕組みを構築' },
      { id: 'proof',    label: '実績・社会的証明',    type: 'textarea', placeholder: '例: 受講生200名以上、平均90日で初収益達成' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `以下の商品の爆売れセールスレター（ランディングページのコピー）を作成してください。

商品名: ${v(vals,'product')}
価格: ${v(vals,'price')}
ターゲット: ${v(vals,'target')}
ベネフィット: ${v(vals,'benefits')}
実績・証拠: ${v(vals,'proof')}

【AIDA構造で出力】
---【タイトル & キャッチコピー】---
（注意を瞬時に掴む強烈なヘッドライン）

---【問題提起 & 共感】---
（読者の痛みを言語化し、「そうそう！」と頷かせる）

---【解決策の提示】---
（商品がどう問題を解決するか具体的に）

---【ベネフィット & 社会的証明】---
（得られる変化と信頼性の証拠）

---【クロージング & CTA】---
（購入への強い動機と明確な行動促進）` },
      ];
    },
  },

  // ── 5. 悪魔のキャッチコピー量産AI ──────────────────────
  {
    id: 'note_catchcopy', category: 'note', emoji: '😈',
    name: '悪魔のキャッチコピー量産AI',
    description: 'クリック率を跳ね上げる魅力的なコピーを大量生成',
    inputs: [
      { id: 'product',  label: '商品・サービス・記事',  type: 'text',   placeholder: '例: 占いサービス、noteの有料記事' },
      { id: 'target',   label: 'ターゲット',            type: 'text',   placeholder: '例: 婚活に悩む30代女性' },
      { id: 'usp',      label: 'USP・独自の強み',       type: 'text',   placeholder: '例: 的中率98%、3000件以上の鑑定実績' },
      { id: 'count',    label: '生成数',                type: 'select', options: ['5個','10個','20個'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `以下の条件でクリック率を最大化するキャッチコピーを${v(vals,'count','10個')}生成してください。

対象: ${v(vals,'product')}
ターゲット: ${v(vals,'target')}
USP: ${v(vals,'usp')}

【要件】
・好奇心・恐怖・共感・承認欲求など多様な心理トリガーを使う
・数字・記号・体験談風など様々なパターンで
・各コピーに【使用トリガー】も付記する
・表現が過剰にならないよう景表法に配慮` },
      ];
    },
  },

  // ── 6. 高単価バックエンド企画 ──────────────────────────
  {
    id: 'note_backend', category: 'note', emoji: '💰',
    name: '高単価バックエンド企画',
    description: '利益を最大化するバックエンド商品を企画',
    inputs: [
      { id: 'frontend', label: 'フロント商品（低単価）',    type: 'text',   placeholder: '例: 500円のnote記事' },
      { id: 'target',   label: 'ターゲット顧客',            type: 'text',   placeholder: '例: SNS副業を始めたい主婦' },
      { id: 'niche',    label: '専門分野・得意なこと',      type: 'text',   placeholder: '例: Instagramコンサル、ライティング' },
      { id: 'price_range', label: '希望バックエンド価格帯', type: 'text',  placeholder: '例: 5万〜30万円' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `以下の条件で利益を最大化する高単価バックエンド商品を企画してください。

フロント商品: ${v(vals,'frontend')}
ターゲット: ${v(vals,'target')}
専門分野: ${v(vals,'niche')}
希望価格帯: ${v(vals,'price_range')}

【出力内容】
・バックエンド商品の企画案（3パターン）
・各商品の価格設定と根拠
・フロント→バックエンドへの自然な導線設計
・高単価でも売れる価値の見せ方
・初月から実現できる販売ロードマップ` },
      ];
    },
  },

  // ── 7. 心理的クロージング生成 ─────────────────────────
  {
    id: 'note_closing', category: 'note', emoji: '🎪',
    name: '心理的クロージング生成',
    description: '最後の迷いを断ち切る強力なクロージング文章',
    inputs: [
      { id: 'product',  label: '商品・サービス',    type: 'text',     placeholder: '例: 月収10万円達成プログラム' },
      { id: 'objection',label: '客の主な迷いポイント', type: 'textarea', placeholder: '例: 本当に効果あるの？私でもできる？高いかも' },
      { id: 'price',    label: '価格',              type: 'text',     placeholder: '例: 98,000円' },
      { id: 'bonus',    label: '購入特典',          type: 'text',     placeholder: '例: 限定30名、個別相談60分無料' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `以下の商品の購入をためらっている見込み客の背中を押す、最強のクロージング文章を生成してください。

商品: ${v(vals,'product')}
客の迷い: ${v(vals,'objection')}
価格: ${v(vals,'price')}
購入特典: ${v(vals,'bonus')}

【出力】
・よくある反論への具体的な切り返し（3〜5個）
・緊急性・希少性を作るクロージング文
・購入後のビジョンを描かせる文章
・最終CTAコピー（3パターン）` },
      ];
    },
  },

  // ── 8. 競合リサーチ＆差別化戦略 ─────────────────────────
  {
    id: 'note_compete', category: 'note', emoji: '🔍',
    name: '競合リサーチ＆差別化戦略',
    description: '競合を丸裸にし、自社が勝つ独自の切り口を提案',
    inputs: [
      { id: 'niche',    label: 'あなたのジャンル',             type: 'text',     placeholder: '例: Instagram副業コンサルタント' },
      { id: 'strength', label: 'あなたの強み・得意なこと',    type: 'textarea', placeholder: '例: 元ダサいアカウントを6ヶ月でフォロワー5万人にした実績' },
      { id: 'competitor', label: '競合の特徴（知ってる範囲で）', type: 'textarea', placeholder: '例: 高額コンサル多め、テクニック系が多い、初心者向けが少ない' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.note },
        { role: 'user', content: `以下の情報を元に競合分析と差別化戦略を提案してください。

ジャンル: ${v(vals,'niche')}
あなたの強み: ${v(vals,'strength')}
競合の特徴: ${v(vals,'competitor')}

【出力】
・市場の現状分析とブルーオーシャン領域
・あなたが活かせる差別化ポイント（5個）
・独自ポジショニングの提案（3案）
・競合に勝つための具体的コンテンツ戦略
・最初の90日間ロードマップ` },
      ];
    },
  },

  // ── 9. 30日間SNSカレンダー ────────────────────────────
  {
    id: 'sns_calendar', category: 'sns', emoji: '📅',
    name: '30日間SNSカレンダー',
    description: 'キャラ×ジャンルで1ヶ月分の投稿計画を自動生成',
    inputs: [
      { id: 'character', label: 'アカウントのキャラ・ジャンル', type: 'text',   placeholder: '例: 占い師・スピリチュアルアカウント' },
      { id: 'target',    label: 'ターゲットフォロワー',          type: 'text',   placeholder: '例: 婚活中の20〜30代女性' },
      { id: 'theme',     label: '今月のテーマ',                  type: 'text',   placeholder: '例: 引き寄せ・金運・復縁' },
      { id: 'platform',  label: 'プラットフォーム',              type: 'select', options: ['X（Twitter）','Instagram','TikTok','Facebook','複数プラットフォーム'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下の条件で30日間の投稿カレンダーを作成してください。

キャラ・ジャンル: ${v(vals,'character')}
ターゲット: ${v(vals,'target')}
今月のテーマ: ${v(vals,'theme')}
プラットフォーム: ${v(vals,'platform','X（Twitter）')}

【出力形式】
Day 1〜30まで、各日に:
・投稿タイプ（教育/共感/エンタメ/宣伝/CTA）
・投稿テーマ・タイトル
・狙うエンゲージメント
を一覧表形式で出力してください。月全体の戦略的な流れも説明してください。` },
      ];
    },
  },

  // ── 10. SNS無限集客ポスト ────────────────────────────
  {
    id: 'sns_post', category: 'sns', emoji: '✨',
    name: 'SNS無限集客ポスト',
    description: 'スクロールを止めるバズ集客投稿を量産',
    inputs: [
      { id: 'niche',    label: 'ジャンル',          type: 'text',   placeholder: '例: 占い、副業、ダイエット' },
      { id: 'target',   label: 'ターゲット',         type: 'text',   placeholder: '例: 婚活に悩む30代女性' },
      { id: 'platform', label: 'プラットフォーム',   type: 'select', options: ['X（Twitter）','Instagram','TikTok','Facebook'] },
      { id: 'count',    label: '生成本数',           type: 'select', options: ['5本','10本','20本'] },
      { id: 'goal',     label: '投稿の目的',         type: 'select', options: ['フォロワー獲得','note誘導','ライン誘導','集客全般'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下の条件で${v(vals,'count','10本')}の集客投稿を生成してください。

ジャンル: ${v(vals,'niche')}
ターゲット: ${v(vals,'target')}
プラットフォーム: ${v(vals,'platform','X（Twitter）')}
目的: ${v(vals,'goal','フォロワー獲得')}

【要件】
・各投稿は${v(vals,'platform','X（Twitter）')}の文字数制限を考慮
・スクロールが止まる書き出し
・ターゲットの深い悩みに刺さる内容
・自然にフォロー・いいね・保存を促す設計
・各投稿に使用した「集客フック名」を付記` },
      ];
    },
  },

  // ── 11. 記事連動・SNSプロモーション生成 ─────────────────
  {
    id: 'sns_promo', category: 'sns', emoji: '📢',
    name: '記事連動・SNSプロモーション生成',
    description: '記事をSNSで拡散し、クリックさせるポスト',
    inputs: [
      { id: 'title',    label: '記事タイトル',       type: 'text',     placeholder: '例: 【保存版】副業で月10万円を達成した5つのステップ' },
      { id: 'points',   label: '記事の要点',          type: 'textarea', placeholder: '例: ・具体的な手順を公開\n・初心者でも再現可能\n・実際の収益スクショあり' },
      { id: 'platform', label: 'プラットフォーム',    type: 'select',   options: ['X（Twitter）','Instagram','TikTok','Facebook','全プラットフォーム'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下の記事をSNSで最大拡散させるためのプロモーション投稿を生成してください。

記事タイトル: ${v(vals,'title')}
要点: ${v(vals,'points')}
プラットフォーム: ${v(vals,'platform','X（Twitter）')}

【出力】
・投稿用テキスト（3パターン）：即クリック誘導型/共感型/疑問型
・ハッシュタグ戦略
・最適な投稿タイミングの提案
・スレッド・連投形式の展開案` },
      ];
    },
  },

  // ── 12. バズるアカウントコンセプト設計 ──────────────────
  {
    id: 'sns_concept', category: 'sns', emoji: '💡',
    name: 'バズるアカウントコンセプト設計',
    description: '競合と差別化したSNSコンセプトを完全設計',
    inputs: [
      { id: 'niche',    label: 'ジャンル・専門分野',       type: 'text',     placeholder: '例: 恋愛、占い、ビジネス' },
      { id: 'profile',  label: 'あなたの特徴・経歴・強み', type: 'textarea', placeholder: '例: 元引きこもりで占いで人生が変わった。現在ココナラ評価5.0' },
      { id: 'audience', label: 'ターゲットオーディエンス', type: 'text',     placeholder: '例: 恋愛に悩む20〜30代女性' },
      { id: 'platform', label: 'メインプラットフォーム',   type: 'select',   options: ['X（Twitter）','Instagram','TikTok','YouTube'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下の情報を元にバズり続けるSNSアカウントコンセプトを完全設計してください。

ジャンル: ${v(vals,'niche')}
プロフィール・強み: ${v(vals,'profile')}
ターゲット: ${v(vals,'audience')}
プラットフォーム: ${v(vals,'platform','X（Twitter）')}

【出力】
・唯一無二のアカウントコンセプト（3案）
・プロフィール文（完成版）
・固定ツイート/ピン投稿の設計
・投稿の世界観・トーン設定
・0→1000フォロワー達成の具体的ロードマップ` },
      ];
    },
  },

  // ── 13. SNSインサイト視覚アナリティクス ─────────────────
  {
    id: 'sns_analytics', category: 'sns', emoji: '📊',
    name: 'SNSインサイト視覚アナリティクス',
    description: '投稿データを分析し、課題解決の戦略をコンサル',
    inputs: [
      { id: 'data',     label: 'アナリティクスデータ・投稿実績', type: 'textarea', placeholder: '例: 先月の投稿:30件、いいね平均:15、リポスト:3、フォロワー増加:+50' },
      { id: 'goal',     label: '達成したい目標',                  type: 'text',     placeholder: '例: 3ヶ月でフォロワー1万人、noteへの誘導率10%' },
      { id: 'platform', label: 'プラットフォーム',                type: 'select',   options: ['X（Twitter）','Instagram','TikTok','YouTube','Facebook'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下のSNSデータを分析し、目標達成のための具体的な改善戦略をコンサルしてください。

データ: ${v(vals,'data')}
目標: ${v(vals,'goal')}
プラットフォーム: ${v(vals,'platform','X（Twitter）')}

【出力】
・現状の課題点の分析（具体的に3〜5点）
・KPI達成のための改善施策（優先度付き）
・コンテンツミックスの最適化提案
・今すぐ実施すべきアクションプラン（1週間分）
・目標達成シミュレーション` },
      ];
    },
  },

  // ── 14. バズ診断＆自動改善AI ─────────────────────────
  {
    id: 'sns_buzz_fix', category: 'sns', emoji: '🔧',
    name: 'バズ診断＆自動改善AI',
    description: '投稿文のバズ予測スコアを診断して自動改善',
    inputs: [
      { id: 'post',     label: '改善したい投稿文',     type: 'textarea', placeholder: '投稿文をそのまま貼り付けてください' },
      { id: 'platform', label: 'プラットフォーム',     type: 'select',   options: ['X（Twitter）','Instagram','TikTok','Facebook'] },
      { id: 'goal',     label: '投稿の目的',           type: 'select',   options: ['フォロワー増加','いいね・保存増加','リンククリック誘導','認知拡大'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下の投稿を診断し、バズる文章に改善してください。

【元の投稿】
${v(vals,'post','（投稿文を入力してください）')}

プラットフォーム: ${v(vals,'platform','X（Twitter）')}
目的: ${v(vals,'goal','フォロワー増加')}

【出力形式】
■ バズスコア: 〇〇/100
■ 診断コメント: （具体的な改善点）
■ 改善版（パターンA）: （スクロールが止まる書き出し型）
■ 改善版（パターンB）: （共感誘発型）
■ 改善版（パターンC）: （好奇心刺激型）
■ 改善のポイント解説: ` },
      ];
    },
  },

  // ── 15. 画像生成AIプロンプト ─────────────────────────
  {
    id: 'sns_image_prompt', category: 'sns', emoji: '🎨',
    name: '画像生成AIプロンプト',
    description: 'Midjourney等向けの高品質な英語プロンプトを生成',
    inputs: [
      { id: 'concept',  label: '生成したい画像の概要',  type: 'textarea', placeholder: '例: 神秘的な占い師が月明かりの下でタロットカードを読んでいる様子' },
      { id: 'style',    label: 'スタイル',              type: 'select',   options: ['フォトリアル','イラスト（アニメ風）','水彩画','デジタルアート','3DCG','ロゴデザイン'] },
      { id: 'tool',     label: '使用ツール',            type: 'select',   options: ['Midjourney','DALL-E 3','Stable Diffusion','Adobe Firefly'] },
      { id: 'mood',     label: '雰囲気・ムード',        type: 'text',     placeholder: '例: 神秘的、幻想的、深海ブルー' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: 'あなたはAI画像生成の専門家です。プロ品質の画像を生成するための最適なプロンプトを作成してください。' },
        { role: 'user', content: `以下の条件で${v(vals,'tool','Midjourney')}用の高品質な画像生成プロンプトを作成してください。

概要: ${v(vals,'concept')}
スタイル: ${v(vals,'style','フォトリアル')}
ムード: ${v(vals,'mood')}

【出力】
・英語プロンプト（メイン）
・日本語解説
・${v(vals,'tool','Midjourney')}専用パラメータ
・バリエーション案（3パターン）` },
      ];
    },
  },

  // ── 16. アイキャッチ構成デザイン ─────────────────────
  {
    id: 'sns_thumbnail', category: 'sns', emoji: '🖼️',
    name: 'アイキャッチ構成デザイン',
    description: '目を引くサムネイル画像用のプロンプト生成',
    inputs: [
      { id: 'title',   label: 'コンテンツタイトル',   type: 'text', placeholder: '例: 副業で月10万円を達成した方法' },
      { id: 'genre',   label: 'コンテンツジャンル',   type: 'text', placeholder: '例: SNS副業、占い' },
      { id: 'target',  label: 'ターゲット',            type: 'text', placeholder: '例: 副業初心者' },
      { id: 'color',   label: '希望カラーイメージ',   type: 'text', placeholder: '例: パープル系、ゴールド' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下の条件でSNS・note用のアイキャッチ画像のデザイン案と画像生成プロンプトを作成してください。

タイトル: ${v(vals,'title')}
ジャンル: ${v(vals,'genre')}
ターゲット: ${v(vals,'target')}
カラーイメージ: ${v(vals,'color','パープル・ゴールド')}

【出力】
・デザインコンセプト（3案）
・各案の構成要素（背景・テキスト配置・アイコン）
・Midjourney用画像生成プロンプト（英語）
・Canvaで再現するためのポイント` },
      ];
    },
  },

  // ── 17. コメント返信AI ────────────────────────────────
  {
    id: 'sns_reply', category: 'sns', emoji: '💬',
    name: 'コメント返信AI',
    description: 'キャラを保ったまま褒め・質問・批判に完璧返信',
    inputs: [
      { id: 'post',      label: '元の投稿内容',          type: 'textarea', placeholder: '例: 占いで人生が変わった体験談の投稿' },
      { id: 'comment',   label: '受け取ったコメント',    type: 'textarea', placeholder: 'コメントをそのまま貼り付けてください' },
      { id: 'type',      label: 'コメントの種類',        type: 'select',   options: ['褒め・感謝','質問・相談','批判・クレーム','スパム的なもの','複合（複数種類）'] },
      { id: 'character', label: 'アカウントのキャラ・口調', type: 'text',  placeholder: '例: 優しい占い師、関西弁、フレンドリー' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下のコメントに対してアカウントキャラを保った最適な返信を生成してください。

元投稿: ${v(vals,'post')}
コメント: ${v(vals,'comment','（コメントを入力してください）')}
種類: ${v(vals,'type','複合（複数種類）')}
キャラ・口調: ${v(vals,'character')}

【要件】
・アカウントのブランディングを崩さない
・コメントした人をファン化する方向性
・返信後に会話が続くような終わり方
・返信案を3パターン提案` },
      ];
    },
  },

  // ── 18. 投稿リミックス ───────────────────────────────
  {
    id: 'sns_remix', category: 'sns', emoji: '🔄',
    name: '投稿リミックス',
    description: '1つの投稿を別キャラ・別媒体に自動変換',
    inputs: [
      { id: 'original',  label: '元の投稿文',              type: 'textarea', placeholder: '元の投稿を貼り付けてください' },
      { id: 'target_platform', label: '変換先プラットフォーム', type: 'select', options: ['X→Instagram','X→TikTokスクリプト','Instagram→X','note記事→SNS投稿', 'SNS投稿→note記事', 'X→LINE配信文'] },
      { id: 'new_character', label: '変換先のキャラ・トーン', type: 'text', placeholder: '例: より丁寧なビジネストーン、より砕けたカジュアル' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.sns },
        { role: 'user', content: `以下の投稿を指定の媒体・キャラに最適化してリミックスしてください。

【元の投稿】
${v(vals,'original','（投稿を入力してください）')}

変換: ${v(vals,'target_platform','X→Instagram')}
新キャラ・トーン: ${v(vals,'new_character','元のトーンを最適化')}

【出力】
・変換後の投稿文（完成版）
・変換のポイント解説
・追加すべきハッシュタグ・タグ` },
      ];
    },
  },

  // ── 19. 採用率99%案件獲得提案文 ──────────────────────
  {
    id: 'crowd_proposal', category: 'crowd', emoji: '🏆',
    name: '採用率99% 案件獲得提案文',
    description: 'クラウドソーシングで採用される最強の提案文',
    inputs: [
      { id: 'job',      label: '案件の概要',      type: 'textarea', placeholder: '案件の説明文をそのまま貼り付けてください' },
      { id: 'skills',   label: 'あなたのスキル',  type: 'text',     placeholder: '例: WordPress構築、LP制作、SEO対策' },
      { id: 'experience',label: '実績・経験',      type: 'textarea', placeholder: '例: LP制作50件以上、CVR平均5%達成' },
      { id: 'price',    label: '希望報酬',        type: 'text',     placeholder: '例: 5万円〜' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.crowd },
        { role: 'user', content: `以下の案件に採用される可能性を最大化する提案文を生成してください。

【案件内容】
${v(vals,'job','（案件詳細を入力してください）')}

スキル: ${v(vals,'skills')}
実績: ${v(vals,'experience')}
希望報酬: ${v(vals,'price')}

【出力】
・提案文本文（完成版）
・クライアントの不安を先回りして解消する文章
・採用後の具体的な進め方イメージ
・NGにしている内容と理由` },
      ];
    },
  },

  // ── 20. プラチナランク プロフィール構築 ──────────────
  {
    id: 'crowd_profile', category: 'crowd', emoji: '💎',
    name: 'プラチナランク プロフィール構築',
    description: '「この人に頼みたい」と思わせるプロフィール文',
    inputs: [
      { id: 'skills',   label: '得意なスキル',         type: 'text',     placeholder: '例: Webデザイン、コピーライティング、SNS運用' },
      { id: 'experience',label: '実績・経歴',           type: 'textarea', placeholder: '例: 某大手企業でマーケ担当5年、副業で月50万達成' },
      { id: 'target_price', label: '目標案件単価',     type: 'text',     placeholder: '例: 1案件10万円〜' },
      { id: 'platform', label: 'プラットフォーム',      type: 'select',   options: ['クラウドワークス','ランサーズ','ココナラ','MENTAなど教えるサービス','複数プラットフォーム'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.crowd },
        { role: 'user', content: `以下の情報を元に${v(vals,'platform','クラウドワークス')}で高単価案件が集まるプロフィールを作成してください。

スキル: ${v(vals,'skills')}
実績・経歴: ${v(vals,'experience')}
目標単価: ${v(vals,'target_price')}

【出力】
・プロフィール文（完成版、300〜500字）
・実績の見せ方・数値化のポイント
・サービスの説明文（3パターン）
・クライアントが安心できる具体的な表現` },
      ];
    },
  },

  // ── 21. プロのヒアリングシート生成 ──────────────────
  {
    id: 'crowd_hearing', category: 'crowd', emoji: '📝',
    name: 'プロのヒアリングシート生成',
    description: 'クライアントの真のニーズを引き出す質問リスト',
    inputs: [
      { id: 'service',  label: '対応するサービス・案件ジャンル', type: 'text', placeholder: '例: LP制作、記事ライティング、SNS運用代行' },
      { id: 'client',   label: 'クライアントの業種・規模',       type: 'text', placeholder: '例: 中小企業、個人事業主、EC事業者' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.crowd },
        { role: 'user', content: `以下のサービスに最適なヒアリングシートを作成してください。

サービス: ${v(vals,'service')}
クライアント: ${v(vals,'client')}

【出力】
・必須ヒアリング項目（10〜15問）
・優先度分類（必須/推奨/任意）
・各質問の意図・なぜ必要かの解説
・回答例付き（クライアントが答えやすい形式）
・ヒアリング時の注意点・NGな聞き方` },
      ];
    },
  },

  // ── 22. 「神納品」メッセージ＆アップセル ────────────
  {
    id: 'crowd_delivery', category: 'crowd', emoji: '🎁',
    name: '「神納品」メッセージ＆アップセル',
    description: '納品報告と同時に次回リピート案件を獲得する',
    inputs: [
      { id: 'delivered', label: '納品したもの',              type: 'text',     placeholder: '例: LP制作（5ページ、スマホ対応）' },
      { id: 'project',   label: '案件の内容',                type: 'text',     placeholder: '例: 美容サロンのホームページ制作' },
      { id: 'upsell',    label: '次回提案したいサービス',    type: 'text',     placeholder: '例: SEO対策、SNS運用代行、月次更新サポート' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.crowd },
        { role: 'user', content: `以下の案件の納品メッセージと次回案件獲得のためのアップセルメッセージを生成してください。

納品物: ${v(vals,'delivered')}
案件内容: ${v(vals,'project')}
次回提案: ${v(vals,'upsell')}

【出力】
・納品メッセージ（感謝・報告・確認依頼）
・クライアントに「また頼みたい」と思わせる一言
・自然なアップセル提案文（押し付けにならない）
・評価・レビュー依頼の文章（さりげなく）` },
      ];
    },
  },

  // ── 23. 高単価案件ハンター ────────────────────────────
  {
    id: 'crowd_upgrade', category: 'crowd', emoji: '🚀',
    name: '高単価案件ハンター',
    description: '低単価から抜け出すためのスキル掛け合わせ提案',
    inputs: [
      { id: 'skills',    label: '現在持っているスキル',  type: 'text', placeholder: '例: ライティング、WordPress、Canva' },
      { id: 'current_price', label: '現在の平均単価',   type: 'text', placeholder: '例: 1記事2000円' },
      { id: 'target_price',  label: '目標単価',          type: 'text', placeholder: '例: 1案件10万円' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.crowd },
        { role: 'user', content: `以下の情報を元に高単価案件を獲得するための戦略を提案してください。

現在のスキル: ${v(vals,'skills')}
現在の単価: ${v(vals,'current_price')}
目標単価: ${v(vals,'target_price')}

【出力】
・スキルの掛け合わせによる高単価ポジション（5案）
・各ポジションの市場相場と需要
・高単価を実現するためのポートフォリオ戦略
・3ヶ月で単価2倍を達成するロードマップ
・最初に取るべき具体的アクション（今週中にできること）` },
      ];
    },
  },

  // ── 24. 報酬・単価交渉AI ──────────────────────────────
  {
    id: 'crowd_negotiate', category: 'crowd', emoji: '🤝',
    name: '報酬・単価交渉AI',
    description: '角を立てずに単価アップを交渉するメッセージ',
    inputs: [
      { id: 'current',  label: '現在の単価',       type: 'text',     placeholder: '例: 1記事3000円' },
      { id: 'target',   label: '希望単価',          type: 'text',     placeholder: '例: 1記事8000円' },
      { id: 'reason',   label: '交渉の根拠・実績', type: 'textarea', placeholder: '例: 3ヶ月間継続で品質向上、SEO記事で検索上位実績あり' },
      { id: 'relation', label: 'クライアントとの関係', type: 'select', options: ['初めての取引','3ヶ月以上の継続','1年以上の長期取引'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.crowd },
        { role: 'user', content: `以下の条件で角を立てずに単価アップを交渉するメッセージを生成してください。

現在の単価: ${v(vals,'current')}
希望単価: ${v(vals,'target')}
根拠: ${v(vals,'reason')}
関係性: ${v(vals,'relation','3ヶ月以上の継続')}

【出力】
・交渉メッセージ（完成版、丁寧かつ説得力あり）
・断られた場合の切り返し文（2パターン）
・交渉成功率を上げるタイミングの提案
・交渉を有利にする事前準備リスト` },
      ];
    },
  },

  // ── 25. SEO特化ブログ記事作成 ────────────────────────
  {
    id: 'crowd_seo', category: 'crowd', emoji: '🔎',
    name: 'SEO特化ブログ記事作成',
    description: '検索上位を狙うためのSEO最適化記事を作成',
    inputs: [
      { id: 'main_kw',  label: 'メインキーワード',    type: 'text', placeholder: '例: 副業 在宅 おすすめ' },
      { id: 'sub_kw',   label: 'サブキーワード',      type: 'text', placeholder: '例: 初心者 稼ぎ方 始め方' },
      { id: 'purpose',  label: '記事の目的・ゴール',  type: 'text', placeholder: '例: アフィリエイト商品のCV獲得' },
      { id: 'target',   label: '読者ターゲット',      type: 'text', placeholder: '例: 会社員で副業を探している30代男性' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: 'あなたはSEOとコンテンツマーケティングの第一人者です。検索意図を完璧に満たし、Googleに評価される最高品質のSEO記事を書いてください。' },
        { role: 'user', content: `以下の条件でSEO特化の記事を作成してください。

メインKW: ${v(vals,'main_kw')}
サブKW: ${v(vals,'sub_kw')}
目的: ${v(vals,'purpose')}
ターゲット: ${v(vals,'target')}

【出力形式】
---【SEOタイトル & メタディスクリプション】---
（クリック率最大化のタイトル案3つ＋メタディスクリプション）

---【記事本文】---
（H2・H3を使った構造化、内部リンク案、FAQセクション含む、3000字以上）` },
      ];
    },
  },

  // ── 26. ブルーオーシャンSEOキーワード選定 ──────────
  {
    id: 'crowd_keyword', category: 'crowd', emoji: '🌊',
    name: 'ブルーオーシャンSEOキーワード選定',
    description: '検索ボリュームがあり競合の少ないキーワードを提案',
    inputs: [
      { id: 'theme',    label: 'ジャンル・テーマ',              type: 'text',   placeholder: '例: 副業、占い、ダイエット' },
      { id: 'target',   label: 'ターゲット読者',                type: 'text',   placeholder: '例: 40代主婦' },
      { id: 'domain',   label: '現在のドメインパワー',          type: 'select', options: ['弱い（新規ドメイン）','普通（DA10〜30）','強い（DA30以上）'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: 'あなたはSEOキーワード戦略の専門家です。' },
        { role: 'user', content: `以下の条件でブルーオーシャンのSEOキーワードを提案してください。

ジャンル: ${v(vals,'theme')}
ターゲット: ${v(vals,'target')}
ドメインパワー: ${v(vals,'domain','弱い（新規ドメイン）')}

【出力】
・ロングテールキーワード候補（20個）
・各KWの推定検索ボリューム・競合度・難易度
・優先度ランキング（取り組む順番）
・各KWで書くべき記事の方向性
・6ヶ月でアクセス10倍を実現するKW戦略` },
      ];
    },
  },

  // ── 27. ココナラ無双出品パッケージ ──────────────────
  {
    id: 'coconala_package', category: 'coconala', emoji: '🏆',
    name: 'ココナラ無双出品パッケージ',
    description: 'ココナラで圧倒的に売れるサービスページを丸ごと作成',
    inputs: [
      { id: 'service',  label: '占い・サービスの種類',    type: 'text',     placeholder: '例: タロット占い、四柱推命、オラクルカード' },
      { id: 'price',    label: '価格',                   type: 'text',     placeholder: '例: 3,000円〜5,000円' },
      { id: 'feature',  label: 'あなたの特徴・強み',     type: 'textarea', placeholder: '例: 10年以上の鑑定歴、復縁実績300件以上、共感力の高さ' },
      { id: 'target',   label: 'ターゲット',             type: 'text',     placeholder: '例: 恋愛・婚活に悩む20〜40代女性' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の情報を元にココナラで爆売れするサービスページを丸ごと作成してください。

サービス種類: ${v(vals,'service')}
価格: ${v(vals,'price')}
特徴・強み: ${v(vals,'feature')}
ターゲット: ${v(vals,'target')}

【出力】
---【サービスタイトル】---
（検索上位×クリック率最大化）

---【サービス説明文（メイン）】---
（読者の悩みへの共感→解決→あなたを選ぶ理由の流れ、800字以上）

---【購入前FAQと回答】---
（よくある5つの不安を解消）

---【購入者へのメッセージ】---
（温かみがあり信頼を生む締めの言葉）` },
      ];
    },
  },

  // ── 28. coconala出品文（簡易版） ─────────────────────
  {
    id: 'coconala_simple', category: 'coconala', emoji: '✏️',
    name: 'coconala出品文（簡易版）',
    description: '検索上位表示されるサービス説明文を素早く生成',
    inputs: [
      { id: 'service',  label: 'サービス種類',    type: 'text', placeholder: '例: タロット占い' },
      { id: 'price',    label: '価格',            type: 'text', placeholder: '例: 2,000円' },
      { id: 'feature',  label: '特徴・ウリ',      type: 'text', placeholder: '例: 当日対応可、復縁専門' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の情報でシンプルで売れるcocoanala出品文を作成してください。

サービス: ${v(vals,'service')}
価格: ${v(vals,'price')}
特徴: ${v(vals,'feature')}

・タイトル（SEO対策済み）
・説明文（300〜400字）
・ハッシュタグ候補5個` },
      ];
    },
  },

  // ── 29. プロ品質 占い鑑定書ライター ─────────────────
  {
    id: 'coconala_reading', category: 'coconala', emoji: '🔮',
    name: 'プロ品質 占い鑑定書ライター',
    description: '有料販売に耐えるプロ品質の長文鑑定書を生成',
    inputs: [
      { id: 'type',     label: '占いの種類',        type: 'text',     placeholder: '例: タロット、西洋占星術、四柱推命' },
      { id: 'info',     label: '鑑定対象者の情報',  type: 'textarea', placeholder: '例: 女性・32歳・ニックネーム: さくらさん・牡羊座' },
      { id: 'theme',    label: '鑑定テーマ',        type: 'select',   options: ['恋愛・復縁','婚活・結婚運','仕事・転職運','金運・副業運','総合運','対人関係・友人'] },
      { id: 'result',   label: '出たカード・占い結果（任意）', type: 'textarea', placeholder: '例: 太陽・月・世界のカードが出た' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の情報を元に有料販売に耐えるプロ品質の鑑定書を作成してください。

占いの種類: ${v(vals,'type')}
対象者情報: ${v(vals,'info')}
テーマ: ${v(vals,'theme','恋愛・復縁')}
占い結果: ${v(vals,'result','（AIが最適に設定）')}

【出力形式】
---【鑑定書】---
・冒頭の挨拶と鑑定への感謝
・現状分析（深掘り）
・テーマ別の詳細鑑定（具体的なアドバイスを含む）
・今後の展望と時期
・クライアントへのメッセージ（温かみのある締め）
合計1500字以上で出力してください。` },
      ];
    },
  },

  // ── 30. 深層・相性鑑定書ライター ─────────────────────
  {
    id: 'coconala_compatibility', category: 'coconala', emoji: '💑',
    name: '深層・相性鑑定書ライター',
    description: '2人の相性を深掘りする鑑定書（恋愛系No.1ジャンル）',
    inputs: [
      { id: 'person_a', label: 'Aさんの情報',     type: 'textarea', placeholder: '例: 女性・29歳・AB型・天秤座' },
      { id: 'person_b', label: 'Bさんの情報',     type: 'textarea', placeholder: '例: 男性・33歳・O型・牡牛座' },
      { id: 'theme',    label: '鑑定テーマ',      type: 'select',   options: ['恋愛の相性・発展可能性','復縁の可能性','結婚の可能性','片思い成就の可能性','職場の人間関係'] },
      { id: 'situation',label: '現在の状況',      type: 'textarea', placeholder: '例: 3ヶ月前に別れて、彼から連絡がない状態' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の2人の情報を元に深層相性鑑定書を作成してください。

Aさん: ${v(vals,'person_a')}
Bさん: ${v(vals,'person_b')}
テーマ: ${v(vals,'theme','恋愛の相性・発展可能性')}
現状: ${v(vals,'situation')}

【出力】
・2人の基本的な相性分析
・エネルギー的な引き合い・反発のポイント
・関係改善・進展のための具体的アドバイス
・今後3〜6ヶ月の展望
・クライアントへの温かいメッセージ
1200字以上で出力してください。` },
      ];
    },
  },

  // ── 31. 運勢カレンダー鑑定書 ─────────────────────────
  {
    id: 'coconala_calendar', category: 'coconala', emoji: '🗓️',
    name: '運勢カレンダー鑑定書',
    description: '月次・年間運勢鑑定書（高単価販売に最適）',
    inputs: [
      { id: 'info',     label: '対象者の情報',      type: 'textarea', placeholder: '例: 女性・35歳・山羊座・壬子年生まれ' },
      { id: 'period',   label: '期間',              type: 'select',   options: ['今月の運勢（月次）','今年の年間運勢','来年の運勢'] },
      { id: 'theme',    label: '重点テーマ',         type: 'select',   options: ['総合運','恋愛・結婚運','仕事・キャリア運','金運・財運','健康運','対人運'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の情報を元に${v(vals,'period','今月の運勢（月次）')}の鑑定書を作成してください。

対象者: ${v(vals,'info')}
重点テーマ: ${v(vals,'theme','総合運')}

【出力】
・概観・総括
・月別（または週別）の運気の流れ
・ラッキーな時期とその活かし方
・注意すべき時期と乗り越え方
・開運アドバイス（行動・場所・アイテム）
・締めのメッセージ
1500字以上で出力してください。` },
      ];
    },
  },

  // ── 32. アゲ鑑定（ポジティブ変換）推敲 ─────────────
  {
    id: 'coconala_positive', category: 'coconala', emoji: '⬆️',
    name: 'アゲ鑑定（ポジティブ変換）推敲',
    description: '悪い結果を嘘をつかずに「希望」に変換するリライト',
    inputs: [
      { id: 'original', label: '元の鑑定文', type: 'textarea', placeholder: '悪い結果を含む鑑定文を貼り付けてください' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の鑑定文を「嘘をつかずに希望に変換する」アゲ鑑定にリライトしてください。

【元の鑑定文】
${v(vals,'original','（鑑定文を入力してください）')}

【要件】
・ネガティブな内容を完全に消すのではなく、成長の機会・学びとして再解釈する
・クライアントが「読んで良かった」と思える温かみを加える
・具体的な行動アドバイスを添えて希望を持たせる
・原文の意図・情報は維持しつつポジティブな表現に変換
・リライト版を完成形で出力` },
      ];
    },
  },

  // ── 33. ライバル不在 独自占術メニュー開発 ──────────
  {
    id: 'coconala_menu', category: 'coconala', emoji: '⭐',
    name: 'ライバル不在 独自占術メニュー開発',
    description: 'ライバル不在の高単価オリジナル占術メニューを企画',
    inputs: [
      { id: 'specialty', label: '得意な占術',           type: 'text',     placeholder: '例: タロット、西洋占星術、数秘術' },
      { id: 'target',    label: 'ターゲット客層',        type: 'text',     placeholder: '例: 復縁を望む20〜40代女性' },
      { id: 'unique',    label: '差別化したい点',        type: 'textarea', placeholder: '例: スピリチュアルと心理学を組み合わせた独自鑑定' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の情報を元にライバル不在の高単価オリジナル占術メニューを開発してください。

得意な占術: ${v(vals,'specialty')}
ターゲット: ${v(vals,'target')}
差別化ポイント: ${v(vals,'unique')}

【出力】
・独自占術コンセプト（3案）
・各メニューの名称・価格・内容
・「なぜこのメニューが他にないのか」の説明
・高単価化のためのパッケージ設計
・集客のためのキャッチコピー案` },
      ];
    },
  },

  // ── 34. リピート率100% アフターフォロー ─────────────
  {
    id: 'coconala_followup', category: 'coconala', emoji: '💌',
    name: 'リピート率100% アフターフォロー',
    description: '鑑定後に送り、自然にリピート依頼を発生させるメッセージ',
    inputs: [
      { id: 'reading',  label: '鑑定した内容・テーマ',      type: 'textarea', placeholder: '例: 復縁について鑑定、前向きなアドバイスをした' },
      { id: 'situation',label: 'クライアントの状況・悩み',  type: 'text',     placeholder: '例: 別れた彼氏との復縁を望んでいる' },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の鑑定後にリピートを自然に促すアフターフォローメッセージを作成してください。

鑑定内容: ${v(vals,'reading')}
クライアントの状況: ${v(vals,'situation')}

【出力】
・鑑定直後のお礼・振り返りメッセージ
・1週間後のフォローアップメッセージ
・1ヶ月後のリマインドメッセージ
・各メッセージに自然なリピート誘導を含める
（押し付けにならず、クライアントが「また頼みたい」と感じる文章）` },
      ];
    },
  },

  // ── 35. 「毎日のお告げ」30日分生成 ──────────────────
  {
    id: 'coconala_oracle', category: 'coconala', emoji: '🌟',
    name: '「毎日のお告げ」30日分生成',
    description: 'SNS配信用「毎日のお告げ」30日分自動生成ツール',
    inputs: [
      { id: 'theme',    label: 'テーマ・ジャンル',  type: 'text',   placeholder: '例: 引き寄せ、宇宙からのメッセージ、天使のお告げ' },
      { id: 'target',   label: '対象者',            type: 'text',   placeholder: '例: スピリチュアルに興味がある女性' },
      { id: 'tone',     label: 'トーン・スタイル',  type: 'select', options: ['神聖・厳か','温かみ・優しい','ポジティブ・力強い','謎めいた・神秘的','詩的・幻想的'] },
    ],
    buildMessages(vals) {
      return [
        { role: 'system', content: GENIUS_PERSONAS.coconala },
        { role: 'user', content: `以下の条件でSNS配信用「毎日のお告げ」を30日分生成してください。

テーマ: ${v(vals,'theme')}
対象者: ${v(vals,'target')}
トーン: ${v(vals,'tone','温かみ・優しい')}

【出力形式】
Day 1〜30まで、各日1つ:
・タイトル（キャッチー）
・お告げ本文（100〜150字）
・ハッシュタグ（3〜5個）

全て独自性があり、毎日読み続けたくなる内容にしてください。` },
      ];
    },
  },

];

// ── エクスポート ─────────────────────────────────────────
// (グローバル変数としてアクセス可能)
