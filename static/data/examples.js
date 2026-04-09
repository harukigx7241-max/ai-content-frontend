'use strict';
/**
 * static/data/examples.js
 * テンプレートギャラリー用プレースホルダー。
 * TODO: Phase 2+ でテンプレートギャラリー UI 実装時に内容を充実させる。
 *
 * 構造:
 *   Examples[category][tool] = [ { label, data }, ... ]
 *   data: フォームの name 属性 → value のマッピング
 */

const Examples = {
  note: {
    article: [
      {
        label: 'AI副業入門',
        data: {
          theme: 'AIツールを使って副業で月5万円稼ぐ完全ロードマップ',
          age_range: '25〜35歳',
          situation: '会社員で副業を始めたいが何から手をつけるか分からない',
          concern: '時間がない・スキルがない・でも収入を増やしたい',
          tone: 'です・ます調',
          free_chars: '2000字',
          paid_chars: '5000字',
        },
      },
      {
        label: '月5万の副業術',
        data: {
          theme: '在宅ワークで月5万円を3ヶ月で実現した私の副業術',
          age_range: '30〜40歳',
          situation: '育児中で隙間時間しかない',
          concern: '育児と両立できる副業が見つからない',
          tone: 'です・ます調',
          free_chars: '1000字',
          paid_chars: '5000字',
        },
      },
      {
        label: 'ゼロからSNS運用',
        data: {
          theme: 'フォロワーゼロから始めるInstagram副業完全ガイド',
          age_range: '20代',
          situation: 'SNS経験ゼロの初心者',
          concern: '何を発信すればいいか分からない、フォロワーが増えない',
          tone: 'です・ます調',
          free_chars: '2000字',
          paid_chars: '5000字',
        },
      },
    ],
    titles: [
      {
        label: 'SNS運用入門',
        data: {
          genre: 'SNS運用・副業',
          keyword: 'Instagram 副業 初心者',
          target: '20代女性でInstagramを始めたい会社員',
        },
      },
      {
        label: 'AI副業',
        data: {
          genre: 'AI活用・副業',
          keyword: 'AI 副業 稼ぐ',
          target: '30代でAIを使った副業に興味がある会社員',
        },
      },
    ],
    salescopy: [
      {
        label: '副業ロードマップPDF',
        data: {
          platform: 'tips',
          content: '副業で月5万円稼ぐ完全ロードマップPDF（60ページ）',
          target: '副業初心者・会社員',
          price: '980円',
        },
      },
    ],
    gift: [
      {
        label: '30日間行動計画',
        data: {
          theme: 'AIツールを使った副業月5万円達成',
          gift_type: '行動計画書',
          volume: '標準版（A4 3枚相当）',
          buyer_situation: '副業初心者・平日の隙間時間のみ使える会社員',
        },
      },
    ],
  },

  cw: {
    proposal: [
      {
        label: 'Webライター提案',
        data: {
          job_title: 'SEOライター（副業・在宅）',
          skills: 'Webライター歴3年・SEO記事200本以上・美容・ライフスタイルジャンル得意',
          appeal: '納期厳守・リサーチ力・リライト無料対応',
          desired_rate: '1文字3円〜',
        },
      },
    ],
    profile: [
      {
        label: 'Webライタープロフィール',
        data: {
          job_type: 'Webライター',
          experience_years: '3年',
          specialty: 'SEO記事・副業・美容・ライフスタイル',
          achievements: 'SEO記事200本・月30本受注・上位表示実績あり',
        },
      },
    ],
    pricing: [
      {
        label: '単価アップ交渉',
        data: {
          current_rate: '1文字2円',
          desired_rate: '1文字3円',
          evidence: '半年で50本納品・リライト依頼なし・SEO上位実績3件',
          tone: '丁寧',
        },
      },
    ],
  },

  fortune: {
    reading: [
      {
        label: 'タロット恋愛鑑定',
        data: {
          divination_type: 'タロット',
          category: '恋愛・婚活',
          direction: 'ポジティブ・希望寄り',
        },
      },
    ],
    coconala: [
      {
        label: 'タロット恋愛鑑定ページ',
        data: {
          divination_type: 'タロット',
          specialty: '恋愛・復縁・片思い',
          style: '丁寧・寄り添い型',
          price_range: '500円〜',
        },
      },
    ],
    profile: [
      {
        label: '占い師プロフィール',
        data: {
          experience: 'タロット歴5年・西洋占星術3年',
          motivation: '自分が辛い時期に占いに救われた経験から',
          strengths: '共感力が高く、相談者の気持ちに寄り添った鑑定',
          target: '恋愛・仕事で悩んでいる20〜40代の女性',
        },
      },
    ],
  },

  sns: {
    twitter: [
      {
        label: '副業告知',
        data: {
          topic: '副業で月5万円を達成した体験談',
          genre: '副業・在宅ワーク',
          style: '体験談',
          length: '140字',
        },
      },
    ],
    threads: [
      {
        label: 'スピリチュアル投稿',
        data: {
          theme: '満月の日にやると運気が上がる3つのこと',
          mood: 'インスピレーション系',
          audience: 'スピリチュアル・占いに興味がある20〜30代女性',
        },
      },
    ],
    instagram: [
      {
        label: '副業アカウント投稿',
        data: {
          content: '在宅副業で月5万円達成したビフォーアフター画像',
          genre: '副業・ライフスタイル',
          goal: 'フォロワー増加',
        },
      },
    ],
    bio: [
      {
        label: '副業アカウントプロフ',
        data: {
          platform: 'X (Twitter)',
          niche: '在宅副業・AI活用',
          title: 'AI副業コンサルタント',
          target: '副業初心者・会社員',
        },
      },
    ],
  },
};

window.Examples = Examples;
