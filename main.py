from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="副業AIプロンプトプロ", version="2.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ─────────────────────────────────────────
# Pydantic Models
# ─────────────────────────────────────────

class NoteArticleRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    age_range: str = Field(default="25〜35歳", max_length=50)
    situation: str = Field(..., min_length=1, max_length=300)
    concern: str = Field(..., min_length=1, max_length=300)
    tone: str = Field(default="です・ます調", max_length=50)
    free_chars: str = Field(default="2000字", max_length=20)
    paid_chars: str = Field(default="5000字", max_length=20)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class NoteTitlesRequest(BaseModel):
    genre: str = Field(..., min_length=1, max_length=100)
    keyword: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class NoteSalesCopyRequest(BaseModel):
    platform: str = Field(..., max_length=50)
    content: str = Field(..., min_length=1, max_length=300)
    target: str = Field(..., min_length=1, max_length=200)
    price: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class NoteGiftRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    gift_type: str = Field(..., max_length=50)
    volume: str = Field(default="標準版（A4 3枚相当）", max_length=50)
    buyer_situation: str = Field(..., min_length=1, max_length=300)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class CwProposalRequest(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=200)
    skills: str = Field(..., min_length=1, max_length=400)
    appeal: str = Field(..., min_length=1, max_length=300)
    desired_rate: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class CwProfileRequest(BaseModel):
    job_type: str = Field(..., max_length=50)
    experience_years: str = Field(..., max_length=20)
    specialty: str = Field(..., min_length=1, max_length=300)
    achievements: str = Field(..., min_length=1, max_length=400)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class CwPricingRequest(BaseModel):
    current_rate: str = Field(..., max_length=50)
    desired_rate: str = Field(..., max_length=50)
    evidence: str = Field(..., min_length=1, max_length=400)
    tone: str = Field(default="丁寧", max_length=20)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class FortuneReadingRequest(BaseModel):
    divination_type: str = Field(..., max_length=50)
    category: str = Field(..., max_length=50)
    direction: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class FortuneCoconalaRequest(BaseModel):
    divination_type: str = Field(..., max_length=50)
    specialty: str = Field(..., min_length=1, max_length=300)
    style: str = Field(..., max_length=50)
    price_range: str = Field(..., max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class FortuneProfileRequest(BaseModel):
    experience: str = Field(..., min_length=1, max_length=300)
    motivation: str = Field(..., min_length=1, max_length=300)
    strengths: str = Field(..., min_length=1, max_length=300)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class SnsTweetRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    genre: str = Field(..., max_length=50)
    style: str = Field(default="問いかけ", max_length=30)
    length: str = Field(default="140字", max_length=20)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class SnsThreadsRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    mood: str = Field(default="カジュアル", max_length=30)
    audience: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class SnsInstagramRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=300)
    genre: str = Field(..., max_length=50)
    goal: str = Field(default="エンゲージメント", max_length=50)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class SnsBioRequest(BaseModel):
    platform: str = Field(..., max_length=30)
    niche: str = Field(..., min_length=1, max_length=200)
    title: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)

class ProjectBundleRequest(BaseModel):
    theme: str = Field(..., min_length=1, max_length=200)
    target: str = Field(..., min_length=1, max_length=200)
    ai_mode: str = Field(default="ChatGPT", max_length=20)


# ─────────────────────────────────────────
# AI Mode Suffix
# ─────────────────────────────────────────

def ai_suffix(mode: str) -> str:
    if mode == "Gemini":
        return "\n\n※ Gemini向け補足: Googleの最新情報・トレンドデータを積極的にWeb検索で引用してください。最新性を最優先にしてください。"
    elif mode == "Claude":
        return "\n\n※ Claude向け補足: <output>タグ内に最終回答を整理して出力してください。構造化された読みやすいフォーマットで記述してください。"
    else:
        return "\n\n※ ChatGPT向け補足: マークダウン形式で見やすく出力してください。見出し・箇条書き・太字を積極的に活用してください。"

# ─────────────────────────────────────────
# Tab 1: 有料コンテンツ Prompt Builders
# ─────────────────────────────────────────

def build_note_article_prompt(p) -> str:
    return f"""あなたはnote.comで累計1,000件超えの有料記事を販売し、月収50万円を達成したトッププロコンテンツクリエイターです。
編集者・ライター・マーケターの3役を兼ねた専門家として振る舞い、今すぐ販売できる品質の有料note記事を作成してください。
最新データや統計は必ずWeb検索で調べ、具体的な数字を引用してください。

【テーマ】
{p.theme}

【ターゲット読者】
・年齢層: {p.age_range}
・状況: {p.situation}
・悩み: {p.concern}

【記事構成と文字数指定】
以下の7セクション構成で記事を作成してください。
セクション1〜3が無料公開エリア（合計{p.free_chars}程度）、セクション4〜7が有料エリア（合計{p.paid_chars}程度）です。
無料エリアと有料エリアの境界には必ず以下の区切り線を入れてください:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ここから有料エリアです（続きを読むにはご購入ください）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【無料エリア】

1. 導入（600文字）
   ・「あなたもこんな悩みありませんか？」で書き始める
   ・3つの具体的な悩みを列挙する
   ・「でも大丈夫です」で読者に希望を示す

2. 問題の本質（800文字）
   ・なぜその悩みが生まれるのか（Web検索で最新データを引用すること）
   ・多くの人が気づいていない根本原因を明かす
   ・このまま放置するとどうなるかを具体的に示す

3. 解決策の全体像（600文字）
   ・この記事で得られる3つのことを明示する
   ・必要な時間と労力を正直に伝える
   ・期待できる具体的な結果を数字で示す

━━━━ ここから有料エリア ━━━━

4. 具体的な手順（2,000文字）
   ・ステップ1〜5で構成する
   ・各ステップに必ず具体例を入れる（Web検索で実例を調べること）
   ・「よくある失敗とその対処法」も各ステップに記載する

5. 実践例（800文字）
   ・リアルな数字を含む架空事例を作成する
   ・ビフォーアフターを明確に示す
   ・読者が「自分もできる」と感じる内容にする

6. よくある質問（600文字）
   ・Q&A形式で5つ
   ・読者の不安を先回りして解消する

7. 今すぐできること（400文字）
   ・3つのアクションプランを難易度順に並べる
   ・各アクションの所要時間も記載する
   ・読者の背中を押す締めくくりで終わる

【文章のルール】
・{p.tone}で統一する
・1文は50文字以内にする
・改行を多めにして読みやすくする
・専門用語は使わず、小学生でも分かる言葉を使う
・具体的な数字・事例を豊富に盛り込む
・Web検索で最新トレンド・統計データを調べ、現実的なデータを引用すること{ai_suffix(p.ai_mode)}""".strip()


def build_note_titles_prompt(p) -> str:
    return f"""あなたはnote.comで年間ベストセラーを複数持つカリスマnoteプロデューサーです。
コピーライティング・SEO・読者心理の3分野に精通した専門家として、
以下の条件で「思わずクリックしたくなる」有料noteのタイトルと見出し構成を作成してください。

【ジャンル】
{p.genre}

【メインキーワード】
{p.keyword}

【ターゲット読者】
{p.target}

【作成内容】

■ 売れるタイトル案（5パターン）
以下の5つの型でそれぞれ1案ずつ作成してください:
1. 数字型（例: 「〇〇を3ヶ月で達成した7つの方法」）
2. 問いかけ型（例: 「なぜあなたは〇〇できないのか？」）
3. 断言型（例: 「〇〇さえすれば誰でも月5万円稼げる」）
4. ビフォーアフター型（例: 「月収3万円だった私が〇〇で30万円になるまで」）
5. 秘密・暴露型（例: 「プロが教えない〇〇の真実」）

■ 記事構成の見出し案
上記タイトル案の中で最も売れそうなものを1つ選び、
その記事の全セクション見出し（H2・H3レベル）を作成してください。

■ SEOキーワード戦略
この記事で狙うべきキーワードを以下のカテゴリ別に提案してください:
・メインキーワード（1つ）
・サブキーワード（3〜5つ）
・LSIキーワード（3〜5つ）

Web検索で現在のトレンドキーワードを調べて最新情報を反映してください。{ai_suffix(p.ai_mode)}""".strip()


def build_note_salescopy_prompt(p) -> str:
    return f"""あなたはデジタルコンテンツ販売で累計売上1,000万円超えを達成した、
ECとデジタルコンテンツ販売専門のトッププロコピーライターです。
購買心理・販売文・CTA設計のプロとして、以下の商品の販売ページ説明文を作成してください。

【プラットフォーム】
{p.platform}

【商品内容】
{p.content}

【ターゲット読者】
{p.target}

【価格】
{p.price}

【作成内容】

■ メインキャッチコピー（3案）
思わず読み進めたくなる、インパクトのあるキャッチコピーを3パターン作成してください。

■ 商品説明文（本文）
以下の構成で、{p.platform}の購入ページに貼り付けられる説明文を作成してください:

1. 読者の悩みへの共感（2〜3文）
2. この商品で得られる3つのベネフィット
3. 商品の詳細内容（何が含まれているか箇条書き）
4. こんな人に向けた商品です（3〜5項目）
5. 購入者の声（架空でOK・リアルな声2〜3件）
6. よくある質問（3問）
7. 購入を促すCTA（今すぐ購入したくなる文章）

■ サムネイル・画像に入れるコピー
購入ボタンを押させる短い一言コピー（20文字以内）を3案

価格{p.price}の価値を十分に感じさせる説明文にしてください。{ai_suffix(p.ai_mode)}""".strip()


def build_note_gift_prompt(p) -> str:
    return f"""あなたはデジタルコンテンツ販売と顧客満足度向上のスペシャリストです。
購入者が「買って良かった！」「想像以上だった！」と感じる特典設計のプロとして、
以下の条件で購入者向け特典をAIで生成するためのプロンプトを作成してください。

【記事テーマ】
{p.theme}

【特典の種類】
{p.gift_type}

【特典のボリューム】
{p.volume}

【購入者の状況】
{p.buyer_situation}

【作成してほしいもの】
上記の情報を元に、ChatGPT・Gemini・Claudeに渡すことで
「{p.gift_type}」を生成できる、高品質なプロンプトを作成してください。

そのプロンプトには以下を含めてください:
1. AIへの役割指定（どんな専門家として振る舞うか）
2. 特典の具体的な内容指定（{p.gift_type}の詳細な要件）
3. 購入者の状況に合わせたカスタマイズ指示
4. 出力フォーマットの指定（読みやすい構成・見た目）
5. ボリューム指定（{p.volume}相当）

また、生成した特典を購入者に渡す際の案内文テンプレートも一緒に作成してください。
（例: 「この度はご購入いただきありがとうございます。特典として〇〇をお送りします。」）{ai_suffix(p.ai_mode)}""".strip()


# ─────────────────────────────────────────
# Tab 2: クラウドワークス Prompt Builders
# ─────────────────────────────────────────

def build_cw_proposal_prompt(p) -> str:
    return f"""あなたはクラウドワークスで月40件以上の案件を受注し、
クライアントから98%以上の高評価を獲得し続けているトップフリーランサーです。
採用担当者の心理を熟知した提案文の専門家として、
以下の情報を元に採用率を最大化する提案文を作成してください。

【案件タイトル】
{p.job_title}

【自分のスキル・経歴】
{p.skills}

【アピールポイント】
{p.appeal}

【希望単価】
{p.desired_rate}

【提案文の構成】

■ 提案文（完成版）
以下の構成で、コピペしてすぐ使える提案文を作成してください:

1. 書き出し（クライアントへの配慮と興味を示す一文）
2. 自己紹介（スキルと実績を30秒で伝える）
3. この案件に応募した理由（なぜこの仕事に興味があるか）
4. 提供できる価値（具体的に何ができるか・何を解決できるか）
5. 作業の進め方（コミュニケーション方法・納期への対応）
6. 単価について（{p.desired_rate}の根拠・交渉余地）
7. クロージング（次のアクションへの誘導）

■ 件名候補（3案）
メッセージの件名として使える短いフレーズを3案

■ 差別化ポイント
他の応募者と差をつける一言アピールを3案

Web検索でクラウドワークスの採用されやすい提案文のトレンドを調べ、
最新の傾向を反映してください。{ai_suffix(p.ai_mode)}""".strip()


def build_cw_profile_prompt(p) -> str:
    return f"""あなたはクラウドワークスで3,000件以上の採用実績を持つ
フリーランス採用コンサルタントです。
クライアントが「この人に頼みたい」と感じるプロフィール設計の専門家として、
以下の情報を元に魅力的なプロフィール文を作成してください。

【職種】
{p.job_type}

【経験年数】
{p.experience_years}

【得意分野・専門】
{p.specialty}

【実績・経験】
{p.achievements}

【作成内容】

■ プロフィールメイン文（300〜400字）
クライアントが一目で「この人に頼もう」と思う、
説得力のあるプロフィール文を作成してください。
・強みを冒頭で明確に
・具体的な数字・実績を入れる
・クライアントへの提供価値にフォーカス
・信頼感・安心感が伝わる表現を使う

■ スキルタグ・キーワード（10個）
プロフィールに設定すべきスキルタグを10個提案してください。

■ ポートフォリオ説明文テンプレート（3パターン）
実績を掲載する際の説明文テンプレートを3種類

■ 自己PR動画スクリプト（任意参考・30秒版）
もし自己紹介動画を撮る場合のスクリプト案{ai_suffix(p.ai_mode)}""".strip()


def build_cw_pricing_prompt(p) -> str:
    return f"""あなたはフリーランス交渉術の専門家で、
クラウドワークスでの単価アップ交渉を200件以上サポートしてきたコンサルタントです。
クライアントとの関係を壊さず、自然に単価を上げる交渉文の達人として、
以下の情報を元に単価交渉メッセージを作成してください。

【現在の単価】
{p.current_rate}

【希望単価】
{p.desired_rate}

【根拠・実績】
{p.evidence}

【トーン】
{p.tone}

【作成内容】

■ 単価交渉メッセージ（完成版）
以下の構成で、自然で説得力のある交渉メッセージを作成してください:
1. 感謝の言葉（これまでの関係への感謝）
2. 交渉の切り出し方（唐突にならない自然な導入）
3. 単価アップの根拠説明（{p.evidence}を活用）
4. 新単価の提案（{p.desired_rate}）
5. クライアントへのメリット提示（単価アップ後に提供できる追加価値）
6. 柔軟性の示し方（話し合いの余地を残す表現）
7. クロージング（次のステップへの誘導）

■ 交渉が難航した場合の返答例（2パターン）
・クライアントが渋った場合の切り返し
・「少し考えます」と言われた場合のフォロー文

■ 新規クライアント向け初回提示価格の根拠文
{p.desired_rate}を初回から提示する際の説明文テンプレート{ai_suffix(p.ai_mode)}""".strip()



# ─────────────────────────────────────────
# Tab 3: 占い副業 Prompt Builders
# ─────────────────────────────────────────

def build_fortune_reading_prompt(p) -> str:
    return f"""あなたは{p.divination_type}を専門とし、ココナラで鑑定数2,000件超え・
星5評価率99%を誇るカリスマ占い師です。
鑑定文の執筆と相談者の心理サポートのプロとして、
以下の条件でプロ品質の鑑定書テンプレートを作成してください。

【占術の種類】
{p.divination_type}

【相談内容カテゴリ】
{p.category}

【鑑定結果の方向性】
{p.direction}

【作成内容】

■ 鑑定書テンプレート（完成版）
占い師が名前・詳細を記入すれば即座に納品できる鑑定書テンプレートを作成してください。

構成:
1. ご挨拶・感謝の言葉（温かく丁寧に）
2. {p.divination_type}による全体的な鑑定（現状・エネルギー・流れ）
3. {p.category}についての詳細鑑定（具体的なメッセージ）
4. 時期・タイミングについて（いつ頃どうなるか）
5. アドバイス・行動指針（相談者が今すぐできること3〜5つ）
6. ラッキーアイテム・カラー・数字（{p.divination_type}に沿った形で）
7. 締めくくりのメッセージ（相談者を励ます温かい言葉）

【文体のルール】
・温かく寄り添う文体で
・断定しすぎず、可能性を示す表現を使う
・希望が持てる前向きな内容にする
・[相談者名]などのプレースホルダーを適切に配置する{ai_suffix(p.ai_mode)}""".strip()


def build_fortune_coconala_prompt(p) -> str:
    return f"""あなたはスピリチュアルビジネスの販売戦略家であり、
ココナラで年間トップセラーを達成した{p.divination_type}師でもあります。
購買意欲を最大化するサービスページ設計の専門家として、
以下の条件でコカナラの商品ページを作成してください。

【占術の種類】
{p.divination_type}

【得意な相談内容】
{p.specialty}

【鑑定スタイル】
{p.style}

【価格帯】
{p.price_range}

【作成内容】

■ サービスタイトル（5案）
クリックされやすいタイトルを以下のパターンで5案:
1. 結果・効果を強調するタイトル
2. 安心・信頼を強調するタイトル
3. 特徴・強みを強調するタイトル
4. スピード・手軽さを強調するタイトル
5. 占術名を前面に出したタイトル

■ サービス説明文（完成版）
ococからコピペして使えるサービス説明文を作成してください:
1. キャッチコピー（20文字以内）
2. このサービスで得られること（3つ）
3. こんな方へのサービスです（5〜7項目）
4. 鑑定の流れ（ステップ形式で分かりやすく）
5. 鑑定に含まれる内容（箇条書き）
6. 購入者の声（架空2〜3件・リアルな表現で）
7. よくある質問（3問）
8. 購入前にご確認ください（注意事項）

■ {p.price_range}の価格設定根拠
この価格の正当性を購入者に伝える一文{ai_suffix(p.ai_mode)}""".strip()


def build_fortune_profile_prompt(p) -> str:
    return f"""あなたはスピリチュアル業界のブランディング専門家であり、
ここナラ・SNSで人気占い師を多数輩出してきたプロデューサーです。
「この占い師さんに見てもらいたい！」と思わせるプロフィール設計のプロとして、
以下の情報を元に魅力的な占い師プロフィールを作成してください。

【占術歴・経験】
{p.experience}

【占いを始めたきっかけ】
{p.motivation}

【強み・特徴】
{p.strengths}

【ターゲット顧客層】
{p.target}

【作成内容】

■ 占い師プロフィール文（300〜400字）
以下の要素を自然な流れで盛り込んでください:
・占いへの情熱・きっかけ（共感を呼ぶストーリー）
・経験・実績（信頼感の醸成）
・強みと他の占い師との違い
・どんな相談を得意とするか
・相談者への温かいメッセージ

■ ショートプロフィール（Twitter/Threads用・100字以内）

■ Instagram用自己紹介（改行・箇条書き活用）

■ ブランドコンセプト一文（キャッチフレーズ）
占い師としてのブランドを象徴する一文（30字以内）{ai_suffix(p.ai_mode)}""".strip()



# ─────────────────────────────────────────
# Tab 4: SNS特化 Prompt Builders
# ─────────────────────────────────────────

def build_sns_tweet_prompt(p) -> str:
    return f"""あなたはフォロワー15万人を誇り、エンゲージメント率が業界平均の5倍を記録する
X（旧Twitter）のトップインフルエンサー兼SNSマーケターです。
バズる投稿の法則を熟知したコピーライターとして、
以下の条件で高エンゲージメントな投稿文を作成してください。

【トピック】
{p.topic}

【ジャンル】
{p.genre}

【投稿スタイル】
{p.style}

【文字数目安】
{p.length}

【作成内容】

■ 投稿文（3パターン）
同じトピックを3つの異なるアプローチで作成してください:

パターン1: 「{p.style}」スタイル（正統派）
パターン2: 感情を揺さぶる・共感型
パターン3: 数字・事実・驚きを活用した型

各パターンに以下を含めてください:
・本文（{p.length}以内）
・ハッシュタグ（3〜5個、#{p.genre}関連）
・投稿に付ける画像・動画の案（あれば）

■ スレッド展開案
上記3パターンの中で最もバズりそうなものを1つ選び、
5ツイートのスレッドに展開した案も作成してください。

■ 投稿タイミング
このジャンルで最もエンゲージメントが高い曜日・時間帯の推奨

Web検索で{p.genre}ジャンルの最新トレンドハッシュタグを調べてください。{ai_suffix(p.ai_mode)}""".strip()


def build_sns_threads_prompt(p) -> str:
    return f"""あなたはThreadsリリース初期からフォロワー8万人を達成した
Threads専門のSNSコンサルタントです。
Threadsの独特なアルゴリズムと文化を熟知したコンテンツ戦略家として、
以下の条件でThreads投稿文を作成してください。

【テーマ】
{p.theme}

【雰囲気・トーン】
{p.mood}

【フォロワー層・ターゲット】
{p.audience}

【作成内容】

■ Threads投稿文（3パターン）

パターン1: 単発投稿（500字以内・インパクト重視）
パターン2: 連続投稿シリーズ（5投稿・ストーリー形式）
パターン3: 問いかけ・コメント誘導型投稿

各パターンのポイント:
・Threadsらしいカジュアルで親しみやすい文体
・改行を活かしたテンポのよいリズム
・コメントが増えるような問いかけや余白を作る
・インスタとの差別化（より深い内容・本音を出す）

■ リプライ・コメント返信テンプレ（5パターン）
フォロワーとの関係構築に使えるコメント返信例

■ このテーマの連続投稿カレンダー（1週間分）
月曜〜日曜の投稿テーマ・内容の簡単な計画{ai_suffix(p.ai_mode)}""".strip()


def build_sns_instagram_prompt(p) -> str:
    return f"""あなたはInstagramで複数のアカウントを10万フォロワー超えに育て上げた
Instagramマーケティングの第一人者です。
アルゴリズム・ハッシュタグ戦略・エンゲージメント最大化のプロとして、
以下の条件でInstagram投稿キャプションとハッシュタグセットを作成してください。

【投稿内容】
{p.content}

【アカウントジャンル】
{p.genre}

【投稿の目的】
{p.goal}

【作成内容】

■ キャプション（3パターン）

パターン1: 短め（150字以内）・インパクト重視
パターン2: 中程度（300字）・ストーリー型
パターン3: 長め（500字）・価値提供型・保存されやすい内容

各キャプションの構成:
・書き出し（1行目が命・思わず「もっと読む」を押す）
・本文（改行多め・読みやすく）
・CTA（保存・コメント・フォローを促す）
・絵文字の活用（親しみやすさUP）

■ ハッシュタグセット（30個）
以下のカテゴリ別に整理して提案してください:
・ビッグワード（100万件以上）: 5個
・ミドルワード（10万〜100万件）: 10個
・スモールワード（1万〜10万件）: 10個
・ニッチワード（1万件以下）: 5個

■ Instagramリール・ストーリーズへの展開案
この投稿コンテンツをリール・ストーリーズに活用する方法

Web検索で{p.genre}ジャンルの最新人気ハッシュタグを調べてください。{ai_suffix(p.ai_mode)}""".strip()


def build_sns_bio_prompt(p) -> str:
    return f"""あなたはSNSブランディングとプロフィール最適化の専門家で、
{p.platform}で1,000件以上のアカウントプロフィール改善を支援してきたコンサルタントです。
「フォローしたい！」と思わせるプロフィール設計のプロとして、
以下の情報を元に最適化されたプロフィール文を作成してください。

【プラットフォーム】
{p.platform}

【発信ジャンル・ニッチ】
{p.niche}

【肩書き・強み】
{p.title}

【ターゲットフォロワー】
{p.target}

【作成内容】

■ プロフィール文（3パターン）
{p.platform}の文字数制限に合わせたプロフィールを3パターン作成してください:

パターン1: 実績・権威性重視型
パターン2: 親しみやすさ・共感型
パターン3: ベネフィット・価値提供型

各パターンに含める要素:
・キャッチーな肩書き（「〇〇専門家」「〇〇を△△に変える人」等）
・何者か（バックグラウンド・実績）
・フォローするとどんなことが学べるか
・CTA（DMください・リンクから等）

■ アイコン画像・ヘッダー画像の方向性アドバイス

■ ハイライト名の提案（Instagram用・6個）

■ ピン留め投稿のテーマ提案（3つ）
初めて見た人が「フォローしよう」と思う固定投稿のテーマ{ai_suffix(p.ai_mode)}""".strip()



# ─────────────────────────────────────────
# Project Bundle Prompt Builder
# ─────────────────────────────────────────

def build_project_bundle(theme: str, target: str, ai_mode: str) -> dict:
    suffix = ai_suffix(ai_mode)

    article = f"""あなたはnote.comで累計1,000件超えの有料記事を販売し、月収50万円を達成したトッププロコンテンツクリエイターです。

【テーマ】{theme}
【ターゲット】{target}

以下の7セクション構成で有料note記事を作成してください。
セクション1〜3が無料公開エリア、セクション4〜7が有料エリアです。
無料/有料の境界に「━━━━ ここから有料エリア ━━━━」を必ず入れてください。

1. 導入（600字）: 「あなたもこんな悩みありませんか？」から始め、3つの悩みを列挙
2. 問題の本質（800字）: 悩みの根本原因・Web検索で最新データを引用
3. 解決策の全体像（600字）: 得られること3つ・期待できる結果

━━━━ ここから有料エリア ━━━━

4. 具体的な手順（2000字）: ステップ1〜5・よくある失敗も記載
5. 実践例（800字）: リアルな数字付き架空事例・ビフォーアフター
6. よくある質問（600字）: Q&A形式5問
7. 今すぐできること（400字）: アクションプラン3つ（難易度順）

文体: です・ます調・1文50字以内・改行多め・専門用語なし{suffix}"""

    titles = f"""あなたはnote.comで年間ベストセラーを複数持つカリスマnoteプロデューサーです。

【テーマ】{theme}
【ターゲット】{target}

以下を作成してください:
1. 売れるタイトル案 5パターン（数字型・問いかけ型・断言型・ビフォーアフター型・秘密型）
2. 最も売れそうなタイトルの記事見出し構成（H2・H3）
3. SEOキーワード（メイン1・サブ3〜5・LSI3〜5）{suffix}"""

    gift = f"""あなたはデジタルコンテンツ販売の顧客満足度向上スペシャリストです。

【テーマ】{theme}
【購入者】{target}

「{theme}」の有料note購入者向けの特典として、以下を作成してください:
1. 30日間行動計画書（AIで生成できるプロンプト付き）
2. 実践チェックリスト（AIで生成できるプロンプト付き）
3. 購入者への特典案内メール文テンプレート{suffix}"""

    twitter = f"""あなたはフォロワー15万人のX（旧Twitter）トップインフルエンサーです。

【テーマ】{theme}
【ターゲット】{target}

「{theme}」の有料noteを告知・宣伝するためのX投稿文を3パターン作成してください:
1. 興味を引く問いかけ型（140字以内）
2. 「こんな人に読んでほしい」型（140字以内）
3. 実績・数字を使った信頼型（140字以内）
各パターンにハッシュタグ3〜5個も追加してください。{suffix}"""

    instagram = f"""あなたはInstagramマーケティングの第一人者です。

【テーマ】{theme}
【ターゲット】{target}

「{theme}」の有料noteを告知するInstagramキャプションを2パターン作成してください:
1. リール・フィード投稿用（300字）
2. ストーリーズ用（短め・CTA重視）
各パターンに30個のハッシュタグセット（ビッグ5・ミドル10・スモール10・ニッチ5）も含めてください。{suffix}"""

    return {
        "note_article": article.strip(),
        "note_titles": titles.strip(),
        "note_gift": gift.strip(),
        "sns_twitter": twitter.strip(),
        "sns_instagram": instagram.strip(),
    }


# ─────────────────────────────────────────
# Routes
# ─────────────────────────────────────────

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@app.get("/health")
def health():
    return {"status": "ok"}

# Tab 1: 有料コンテンツ
@app.post("/api/note/article")
def note_article(p: NoteArticleRequest):
    return JSONResponse({"prompt": build_note_article_prompt(p)})

@app.post("/api/note/titles")
def note_titles(p: NoteTitlesRequest):
    return JSONResponse({"prompt": build_note_titles_prompt(p)})

@app.post("/api/note/salescopy")
def note_salescopy(p: NoteSalesCopyRequest):
    return JSONResponse({"prompt": build_note_salescopy_prompt(p)})

@app.post("/api/note/gift")
def note_gift(p: NoteGiftRequest):
    return JSONResponse({"prompt": build_note_gift_prompt(p)})

# Tab 2: クラウドワークス
@app.post("/api/cw/proposal")
def cw_proposal(p: CwProposalRequest):
    return JSONResponse({"prompt": build_cw_proposal_prompt(p)})

@app.post("/api/cw/profile")
def cw_profile(p: CwProfileRequest):
    return JSONResponse({"prompt": build_cw_profile_prompt(p)})

@app.post("/api/cw/pricing")
def cw_pricing(p: CwPricingRequest):
    return JSONResponse({"prompt": build_cw_pricing_prompt(p)})

# Tab 3: 占い副業
@app.post("/api/fortune/reading")
def fortune_reading(p: FortuneReadingRequest):
    return JSONResponse({"prompt": build_fortune_reading_prompt(p)})

@app.post("/api/fortune/coconala")
def fortune_coconala(p: FortuneCoconalaRequest):
    return JSONResponse({"prompt": build_fortune_coconala_prompt(p)})

@app.post("/api/fortune/profile")
def fortune_profile(p: FortuneProfileRequest):
    return JSONResponse({"prompt": build_fortune_profile_prompt(p)})

# Tab 4: SNS特化
@app.post("/api/sns/twitter")
def sns_twitter(p: SnsTweetRequest):
    return JSONResponse({"prompt": build_sns_tweet_prompt(p)})

@app.post("/api/sns/threads")
def sns_threads(p: SnsThreadsRequest):
    return JSONResponse({"prompt": build_sns_threads_prompt(p)})

@app.post("/api/sns/instagram")
def sns_instagram(p: SnsInstagramRequest):
    return JSONResponse({"prompt": build_sns_instagram_prompt(p)})

@app.post("/api/sns/bio")
def sns_bio(p: SnsBioRequest):
    return JSONResponse({"prompt": build_sns_bio_prompt(p)})

# Project Bundle
@app.post("/api/project/bundle")
def project_bundle(p: ProjectBundleRequest):
    prompts = build_project_bundle(p.theme, p.target, p.ai_mode)
    return JSONResponse(prompts)

