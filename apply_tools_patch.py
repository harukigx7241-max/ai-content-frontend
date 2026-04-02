#!/usr/bin/env python3
import sys
import os
import shutil

def apply_patch(content, search, replace, label):
    if search in content:
        content = content.replace(search, replace, 1)
        print(f"  ✅ {label}")
        return content
    else:
        print(f"  ⚠️ パッチ適用失敗（該当箇所が見つかりません）: {label}")
        return content

def main():
    filepath = '/root/ai-content-pro/static/js/tools.js'
    if not os.path.exists(filepath):
        print(f"❌ ファイルが見つかりません: {filepath}")
        sys.exit(1)
    
    backup = filepath + '.bak'
    shutil.copy2(filepath, backup)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print("\n🔧 tools.js パッチ適用開始 (仕様書の中優先度機能実装)\n")

    # 1. 副業投稿カレンダー（特化版）の実装
    old_sns_cal = r"""  sns_cal: { cat: 'omega', icon: '📅', name: '30日間SNSカレンダー', desc: 'キャラ×ジャンル特化で1ヶ月分の投稿計画を自動生成',
    help: 'キャラクター×ジャンルで差別化された30日分のSNS投稿計画を自動生成します。各日の投稿内容・ハッシュタグ・最適投稿時間付き。',
    fields: [
      { id: 'theme',    t: 'text',   l: '発信テーマ', ph: '例: 投資・資産運用', isMainMagic: true },
      { id: 'persona',  t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
      { id: 'p_custom', t: 'text',   l: 'カスタムキャラ（「🔧 カスタム」選択時）', ph: '例: 30代元看護師の占い師' },
      { id: 'genre',    t: 'select', l: '🏷 特化ジャンル', opts: GENRE_OPTS }
    ],
    build: function(v) {
      var persona = getPersonaInstruction(v.persona, v.p_custom);
      var genre = getGenreInstruction(v.genre);
      return '# SNSカレンダー作成指示' + persona + genre + '\nテーマ「' + (v.theme||'') + '」について、30日間分のSNS投稿カレンダーを作成してください。各日の投稿内容・ハッシュタグ・最適な投稿時間を含めてください。';
    }
  },"""

    new_sns_cal = r"""  sns_cal: { cat: 'omega', icon: '📅', name: '30日間SNSカレンダー（特化版）', desc: '占い/副業/通常モード対応の1ヶ月分の投稿計画を自動生成',
    help: 'キャラクター×ジャンル×投稿モードで差別化された30日分のSNS投稿計画を自動生成します。訴求ゴールに基づいた投稿内容・ハッシュタグ・最適投稿時間付きのカレンダーを出力します。',
    fields: [
      { id: 'theme',    t: 'text',   l: '発信テーマ（通常モード時）', ph: '例: 投資・資産運用', isMainMagic: true },
      { id: 'mode',         t: 'select', l: '🔮 投稿モード', opts: ['通常投稿モード','🔮 占い・スピリチュアルモード','💼 副業全般モード'] },
      { id: 'uranai_type',  t: 'select', l: '🔮 占い系投稿タイプ（占いモード時）', opts: URANAI_POST_OPTS },
      { id: 'fukugyo_type', t: 'select', l: '💼 副業系投稿タイプ（副業モード時）', opts: FUKUGYO_POST_OPTS },
      { id: 'goal',         t: 'select', l: '🎯 訴求ゴール', opts: GOAL_OPTS },
      { id: 'persona',  t: 'select', l: '🎭 キャラクター', opts: PERSONA_OPTS },
      { id: 'p_custom', t: 'text',   l: 'カスタムキャラ（「🔧 カスタム」選択時）', ph: '例: 30代元看護師の占い師' },
      { id: 'genre',    t: 'select', l: '🏷 特化ジャンル', opts: GENRE_OPTS }
    ],
    build: function(v) {
      var persona = getPersonaInstruction(v.persona, v.p_custom);
      var genre = getGenreInstruction(v.genre);
      var goal = getGoalInstruction(v.goal);
      var mode = v.mode || '通常投稿モード';
      var modeInst = '';
      if (mode.indexOf('占い') >= 0) modeInst = getUranaiPostInstruction(v.uranai_type || '');
      else if (mode.indexOf('副業全般') >= 0) modeInst = getFukugyoPostInstruction(v.fukugyo_type || '');
      return '# 30日間SNSカレンダー作成指示' + persona + genre + goal + modeInst + '\n\nテーマ「' + (v.theme||'') + '」について、指定された投稿モード・訴求ゴールに特化した30日間分のSNS投稿カレンダーを作成してください。各日の投稿内容の要点・ハッシュタグ・最適な投稿時間を含め、表形式で出力してください。';
    }
  },"""
    content = apply_patch(content, old_sns_cal, new_sns_cal, "副業投稿カレンダー（特化版）の実装")

    # 2. ショート動画への訴求ゴール追加
    old_short_vid = r"""  short_vid: { cat: 'sns', icon: '🎬', name: 'ショート動画台本', desc: 'キャラ×ジャンルで視聴者の指を止める動画台本',
    help: 'TikTok・Reels・Shorts用のショート動画台本を生成。最初の1秒で惹きつけるフック付き。15秒〜90秒に対応。',
    fields: [
      { id: 'topic',    t: 'text',   l: '動画のテーマ', ph: '例: iPhoneの隠し機能', isMainMagic: true },
      { id: 'persona',  t: 'select', l: '🎭 なりきりキャラクター', opts: PERSONA_OPTS },
      { id: 'p_custom', t: 'text',   l: 'カスタムキャラ（「🔧 カスタム」選択時）', ph: '例: 30代元看護師の占い師' },
      { id: 'sns_genre',t: 'select', l: '🏷 特化ジャンル', opts: GENRE_OPTS },
      { id: 'platform', t: 'select', l: '対象プラットフォーム', opts: ['TikTok','Instagram Reels','YouTube Shorts'] },
      { id: 'duration', t: 'select', l: '動画の長さ', opts: ['15秒','30秒','60秒','90秒'] }
    ],
    build: function(v) {
      var persona = getPersonaInstruction(v.persona, v.p_custom);
      var genre = getGenreInstruction(v.sns_genre);
      return '# ショート動画台本作成' + persona + genre + '\nテーマ: 「'+(v.topic||'')+'」\nプラットフォーム: '+(v.platform||'TikTok')+'\n長さ: '+(v.duration||'60秒')+'\n\nフック→本編→CTA の構成で台本を作成してください。';
    }
  },"""
    new_short_vid = r"""  short_vid: { cat: 'sns', icon: '🎬', name: 'ショート動画台本', desc: 'キャラ×ジャンルで視聴者の指を止める動画台本',
    help: 'TikTok・Reels・Shorts用のショート動画台本を生成。最初の1秒で惹きつけるフック付き。15秒〜90秒に対応。',
    fields: [
      { id: 'topic',    t: 'text',   l: '動画のテーマ', ph: '例: iPhoneの隠し機能', isMainMagic: true },
      { id: 'goal',     t: 'select', l: '🎯 訴求ゴール', opts: GOAL_OPTS },
      { id: 'persona',  t: 'select', l: '🎭 なりきりキャラクター', opts: PERSONA_OPTS },
      { id: 'p_custom', t: 'text',   l: 'カスタムキャラ（「🔧 カスタム」選択時）', ph: '例: 30代元看護師の占い師' },
      { id: 'sns_genre',t: 'select', l: '🏷 特化ジャンル', opts: GENRE_OPTS },
      { id: 'platform', t: 'select', l: '対象プラットフォーム', opts: ['TikTok','Instagram Reels','YouTube Shorts'] },
      { id: 'duration', t: 'select', l: '動画の長さ', opts: ['15秒','30秒','60秒','90秒'] }
    ],
    build: function(v) {
      var persona = getPersonaInstruction(v.persona, v.p_custom);
      var genre = getGenreInstruction(v.sns_genre);
      var goal = getGoalInstruction(v.goal);
      return '# ショート動画台本作成' + persona + genre + goal + '\nテーマ: 「'+(v.topic||'')+'」\nプラットフォーム: '+(v.platform||'TikTok')+'\n長さ: '+(v.duration||'60秒')+'\n\nフック→本編→CTA の構成で台本を作成してください。';
    }
  },"""
    content = apply_patch(content, old_short_vid, new_short_vid, "ショート動画台本への訴求ゴール追加")

    # 3. YouTube対話シナリオへの訴求ゴール追加
    old_yt_script = r"""  yt_script: { cat: 'sns', icon: '▶', name: 'YouTube対話シナリオ', desc: 'キャラ×ジャンルで飽きない長尺動画シナリオ',
    help: 'YouTube長尺動画のシナリオを、飽きさせない対話形式で生成します。チャプター構成付き。',
    fields: [
      { id: 'topic',    t: 'text',   l: '動画のテーマ', ph: '例: NISAの始め方', isMainMagic: true },
      { id: 'persona',  t: 'select', l: '🎭 なりきりキャラクター（メインMC）', opts: PERSONA_OPTS },
      { id: 'p_custom', t: 'text',   l: 'カスタムキャラ（「🔧 カスタム」選択時）', ph: '例: 30代元看護師の占い師' },
      { id: 'sns_genre',t: 'select', l: '🏷 特化ジャンル', opts: GENRE_OPTS },
      { id: 'duration', t: 'select', l: '目標時間', opts: ['5～8分','10～15分','20～30分'] }
    ],
    build: function(v) {
      var persona = getPersonaInstruction(v.persona, v.p_custom);
      var genre = getGenreInstruction(v.sns_genre);
      return '# YouTube長尺動画シナリオ' + persona + genre + '\nテーマ: 「'+(v.topic||'')+'」\n目標時間: '+(v.duration||'10～15分')+'\n\nオープニング→本編（チャプター構成）→エンディング の台本を作成してください。';
    }
  },"""
    new_yt_script = r"""  yt_script: { cat: 'sns', icon: '▶', name: 'YouTube対話シナリオ', desc: 'キャラ×ジャンルで飽きない長尺動画シナリオ',
    help: 'YouTube長尺動画のシナリオを、飽きさせない対話形式で生成します。チャプター構成付き。',
    fields: [
      { id: 'topic',    t: 'text',   l: '動画のテーマ', ph: '例: NISAの始め方', isMainMagic: true },
      { id: 'goal',     t: 'select', l: '🎯 訴求ゴール', opts: GOAL_OPTS },
      { id: 'persona',  t: 'select', l: '🎭 なりきりキャラクター（メインMC）', opts: PERSONA_OPTS },
      { id: 'p_custom', t: 'text',   l: 'カスタムキャラ（「🔧 カスタム」選択時）', ph: '例: 30代元看護師の占い師' },
      { id: 'sns_genre',t: 'select', l: '🏷 特化ジャンル', opts: GENRE_OPTS },
      { id: 'duration', t: 'select', l: '目標時間', opts: ['5～8分','10～15分','20～30分'] }
    ],
    build: function(v) {
      var persona = getPersonaInstruction(v.persona, v.p_custom);
      var genre = getGenreInstruction(v.sns_genre);
      var goal = getGoalInstruction(v.goal);
      return '# YouTube長尺動画シナリオ' + persona + genre + goal + '\nテーマ: 「'+(v.topic||'')+'」\n目標時間: '+(v.duration||'10～15分')+'\n\nオープニング→本編（チャプター構成）→エンディング の台本を作成してください。';
    }
  },"""
    content = apply_patch(content, old_yt_script, new_yt_script, "YouTubeシナリオへの訴求ゴール追加")

    # 4. マニュアル漏れの修正 (reply)
    old_reply = r"""  reply: { cat: 'fun', icon: '💬', name: 'LINE/DM 神返信', desc: '顧客からの質問やクレームに対する最適な返信',
    fields: [{ id: 'msg', t: 'area', l: '相手からのメッセージ', ph: '例: 高くて買えません。安くなりませんか？', isMainMagic: true }],
    build: function(v) { return '# 神返信作成\n以下のメッセージに対して、相手の感情に寄り添い、信頼関係を構築しながら成約に近づけるプロフェッショナルな返信を3パターン作成してください。\n\n' + (v.msg||''); }
  },"""
    new_reply = r"""  reply: { cat: 'fun', icon: '💬', name: 'LINE/DM 神返信', desc: '顧客からの質問やクレームに対する最適な返信',
    help: '顧客からのLINEやDMへの返信を自動生成します。クレーム対応から価格交渉まで、信頼を損なわないプロフェッショナルな返信を3パターン提案します。',
    fields: [{ id: 'msg', t: 'area', l: '相手からのメッセージ', ph: '例: 高くて買えません。安くなりませんか？', isMainMagic: true }],
    build: function(v) { return '# 神返信作成\n以下のメッセージに対して、相手の感情に寄り添い、信頼関係を構築しながら成約に近づけるプロフェッショナルな返信を3パターン作成してください。\n\n' + (v.msg||''); }
  },"""
    content = apply_patch(content, old_reply, new_reply, "LINE神返信ツールへのマニュアル追加")

    # 5. review_replyの重複helpの修正
    old_review_reply = r"""  review_reply: { cat: 'fun', icon: '⭐', name: '口コミ・レビュー返信文ジェネレーター', desc: 'ポジティブ～ネガティブまで完璧に返信',
    help: '「高い」「迷っている」等の顧客メッセージに対して、信頼関係を構築しながら成約に近づけるプロ返信を3パターン生成。',
    help: '高評価〜低評価まで、レビューの種類に応じた最適な返信文を3パターン生成。ココナラ・Google・SNS対応。',"""
    new_review_reply = r"""  review_reply: { cat: 'fun', icon: '⭐', name: '口コミ・レビュー返信文ジェネレーター', desc: 'ポジティブ～ネガティブまで完璧に返信',
    help: '高評価〜低評価まで、レビューの種類に応じた最適な返信文を3パターン生成。ココナラ・Google・SNS等のプラットフォームに対応。',"""
    content = apply_patch(content, old_review_reply, new_review_reply, "レビュー返信ツールの重複マニュアル修正")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n✅ tools.js パッチ適用完了！")

if __name__ == '__main__':
    main()
