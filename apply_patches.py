#!/usr/bin/env python3
"""
AICP Pro v71.5.0 → v71.6.0 パッチスクリプト
===========================================
app.jsに以下の5機能を追加します：
  1. カスタムキャラ保存（マイキャラ5体）
  2. LINE誘導ワンクリック変換
  3. セクション自動判別タブ
  4. プロンプトモード3ステップUI
  5. ツールマニュアル（全ツール折りたたみヘルプ）

使い方:
  python3 apply_patches.py [app.jsのパス]
  
  例: python3 apply_patches.py /root/ai-content-pro/static/js/app.js
  
  バックアップは自動的に app.js.bak に保存されます。
"""

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
    # ファイルパス
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = '/root/ai-content-pro/static/js/app.js'
    
    if not os.path.exists(filepath):
        print(f"❌ ファイルが見つかりません: {filepath}")
        sys.exit(1)
    
    # バックアップ
    backup = filepath + '.bak'
    shutil.copy2(filepath, backup)
    print(f"📦 バックアップ作成: {backup}")
    
    # 読み込み
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    print(f"\n🔧 パッチ適用開始 (元ファイル: {len(content.splitlines())} 行)\n")

    # ================================================================
    # PATCH 1: バージョン更新
    # ================================================================
    print("【PATCH 1】バージョン更新 v71.5.0 → v71.6.0")
    content = apply_patch(content,
        "const SYS_VERSION = 'v71.5.0 Ultimate Auto-Browsing Edition';",
        "const SYS_VERSION = 'v71.6.0 Ultimate Auto-Browsing Edition';",
        "SYS_VERSION更新"
    )

    # ================================================================
    # PATCH 2: AppDB マイグレーション - myCharas追加
    # ================================================================
    print("\n【PATCH 2】AppDB myCharasマイグレーション追加")
    content = apply_patch(content,
        "if(!db.users[u].settings.templates) db.users[u].settings.templates = ['', '', ''];",
        """if(!db.users[u].settings.templates) db.users[u].settings.templates = ['', '', ''];
            if(!db.users[u].settings.myCharas) db.users[u].settings.myCharas = [];""",
        "myCharasデフォルト値追加"
    )

    # ================================================================
    # PATCH 3: UserSettingModal - myCharas state追加
    # ================================================================
    print("\n【PATCH 3】UserSettingModal myCharas state追加")
    content = apply_patch(content,
        "const [templates, setTemplates] = useState(uData.settings.templates);",
        """const [templates, setTemplates] = useState(uData.settings.templates);
        const [myCharas, setMyCharas] = useState(uData.settings.myCharas || []);""",
        "myCharas state宣言"
    )

    # ================================================================
    # PATCH 4: UserSettingModal save() - myCharas保存
    # ================================================================
    print("\n【PATCH 4】UserSettingModal save()にmyCharas追加")
    content = apply_patch(content,
        "ndb.users[user].settings = Object.assign({}, ndb.users[user].settings, { keys, aiModel, theme, tone, persona, knowledge, templateUrl, notifications: notif, templates });",
        "ndb.users[user].settings = Object.assign({}, ndb.users[user].settings, { keys, aiModel, theme, tone, persona, knowledge, templateUrl, notifications: notif, templates, myCharas });",
        "save()にmyCharas追加"
    )

    # ================================================================
    # PATCH 5: UserSettingModal UI tab - マイキャラ管理UI追加
    # ================================================================
    print("\n【PATCH 5】マイキャラ管理UI追加（UIタブ内）")
    
    MYCHARA_UI = r"""
                        div({ className: 'pt-6 border-t border-white/10' },
                            label({ className: 'block text-xs font-bold text-slate-400 mb-3 flex items-center gap-2' }, '\uD83C\uDFAD マイキャラ保存 (最大5体)'),
                            p({ className: 'text-[10px] text-slate-500 mb-3' }, '※保存したキャラは全ツールの「なりきりキャラクター」選択肢に追加されます。'),
                            myCharas.map((ch, ci) => div({ key: ci, className: 'mb-3 p-3 bg-white/5 border border-white/10 rounded-xl animate-in' },
                                div({ className: 'flex items-center gap-2 mb-2' },
                                    span({ className: 'text-xs font-bold text-brand-light' }, '\uD83C\uDFAD キャラ ' + (ci+1)),
                                    button({ onClick: () => { const nc = myCharas.filter((_, i) => i !== ci); setMyCharas(nc); }, className: 'ml-auto text-[10px] text-brand-danger hover:text-white' }, '削除')
                                ),
                                input({ className: 'input-base !py-1.5 text-xs mb-1.5', placeholder: 'キャラ名 (例: 元看護師の占い師さくら)', value: ch.name || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { name: e.target.value }); setMyCharas(nc); } }),
                                textarea({ className: 'input-base min-h-[60px] text-xs', placeholder: '性格・口調・特徴 (例: 30代女性。優しく寄り添う口調。「〜ですよね」が多い。)', value: ch.desc || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { desc: e.target.value }); setMyCharas(nc); } })
                            )),
                            myCharas.length < 5 && button({ onClick: () => setMyCharas(myCharas.concat([{ name: '', desc: '' }])), className: 'w-full glass-panel py-2.5 rounded-xl text-xs font-bold text-brand-light hover:bg-brand/10 transition border border-dashed border-white/20' }, '+ 新しいキャラを追加')
                        ),"""

    content = apply_patch(content,
        """div({ className: 'pt-6 border-t border-white/10' }, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83C\uDFAD マイ・プロンプトテンプレート (備忘録)'),""",
        MYCHARA_UI + """
                        div({ className: 'pt-6 border-t border-white/10' }, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83C\uDFAD マイ・プロンプトテンプレート (備忘録)'),""",
        "マイキャラ管理UIをUIタブに挿入"
    )

    # ================================================================
    # PATCH 6: ToolCore - LINE誘導ボタン追加 (modifyActionNames)
    # ================================================================
    print("\n【PATCH 6】LINE誘導ワンクリック変換ボタン追加")
    content = apply_patch(content,
        "'eyecatch_prompt': 'アイキャッチ画像プロンプト'",
        "'eyecatch_prompt': 'アイキャッチ画像プロンプト',\n          'line_cta': 'LINE誘導文を追加'",
        "modifyActionNamesにline_cta追加"
    )

    # ================================================================
    # PATCH 7: ToolCore - LINE誘導プロンプト追加 (buildModifyPrompt)
    # ================================================================
    print("\n【PATCH 7】LINE誘導プロンプト定義追加")
    content = apply_patch(content,
        "if (actionType === 'eyecatch_prompt') return '以下の文章の内容を象徴する、MidjourneyやDALL-E 3などの画像生成AI向けの「英語のプロンプト」を1つだけ作成してください。出力は英語のプロンプトテキストのみにしてください。\\n\\n' + sourceText;",
        """if (actionType === 'eyecatch_prompt') return '以下の文章の内容を象徴する、MidjourneyやDALL-E 3などの画像生成AI向けの「英語のプロンプト」を1つだけ作成してください。出力は英語のプロンプトテキストのみにしてください。\\n\\n' + sourceText;
          if (actionType === 'line_cta') return '以下の文章の末尾に、LINE公式アカウントへの登録を自然に促す誘導文（CTA）を3パターン追加してください。\\n・「詳しくはプロフのLINEで💌」系の軽いもの\\n・「LINE登録者限定で○○をプレゼント🎁」系の特典訴求\\n・「今だけ無料で○○を配布中」系の緊急性訴求\\n\\n元の文章はそのまま残し、末尾にCTAを追加する形にしてください。\\n\\n' + sourceText;""",
        "buildModifyPromptにline_cta追加"
    )

    # ================================================================
    # PATCH 8: ToolCore - 推敲パネルにLINEボタン追加
    # ================================================================
    print("\n【PATCH 8】推敲パネルにLINE誘導ボタン追加")
    content = apply_patch(content,
        """}, (genMode === 'prompt' ? '\uD83D\uDCCB ' : '\uD83D\uDDBC\uFE0F ') + 'アイキャッチ')
                        )
                    ),""",
        """}, (genMode === 'prompt' ? '\uD83D\uDCCB ' : '\uD83D\uDDBC\uFE0F ') + 'アイキャッチ'),
                            button({ onClick: () => handleModify('line_cta'), disabled: isLoading, className: 'glass-panel px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition disabled:opacity-50 ' + (genMode === 'prompt' ? 'text-brand-accent hover:bg-brand-accent/20 border border-brand-accent/30' : 'text-green-400 hover:text-white hover:bg-green-500/20') }, (genMode === 'prompt' ? '\uD83D\uDCCB ' : '\uD83D\uDC9A ') + 'LINE誘導追加')
                        )
                    ),""",
        "LINE誘導ボタンを推敲パネルに追加"
    )

    # ================================================================
    # PATCH 9: ToolCore - ツールマニュアル（折りたたみヘルプ）
    # ================================================================
    print("\n【PATCH 9】ツールマニュアル（折りたたみヘルプ）追加")

    TOOL_HELP = r"""
          // ツールヘルプ（折りたたみ）
          const [showHelp, setShowHelp] = useState(false);"""

    content = apply_patch(content,
        "const [brainstormIdeas, setBrainstormIdeas] = useState([]);",
        """const [brainstormIdeas, setBrainstormIdeas] = useState([]);""" + TOOL_HELP,
        "showHelp state追加"
    )

    # ツール名の横にヘルプボタン追加
    content = apply_patch(content,
        "h2({ className: 'text-xl font-black text-white' }, conf.name)",
        """h2({ className: 'text-xl font-black text-white' }, conf.name),
              conf.help && button({ onClick: () => setShowHelp(!showHelp), className: 'text-[10px] glass-panel px-2 py-1 rounded-lg text-slate-400 hover:text-white transition shrink-0' }, showHelp ? '✕ 閉じる' : '❓ 使い方')""",
        "ツール名横にヘルプボタン追加"
    )

    # ヘルプ内容表示エリア追加（トレンドパネルの前）
    HELP_DISPLAY = r"""
          // ツールマニュアル表示
          showHelp && conf.help && div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl animate-in' },
              div({ className: 'flex items-center gap-2 mb-2' },
                  span({ className: 'text-sm' }, '\u2753'),
                  span({ className: 'text-xs font-black text-brand-light' }, conf.name + ' の使い方')
              ),
              p({ className: 'text-xs text-slate-300 leading-relaxed' }, conf.help)
          ),
"""
    content = apply_patch(content,
        "          // トレンドパネル（折りたたみ式・日本語カードUI）",
        HELP_DISPLAY + "          // トレンドパネル（折りたたみ式・日本語カードUI）",
        "ヘルプ表示エリア追加"
    )

    # ================================================================
    # PATCH 10: ToolCore - セクション自動判別タブ
    # ================================================================
    print("\n【PATCH 10】セクション自動判別タブ追加")
    
    # note以外のツールでもセクション検出を有効化
    # 既存の `tid === 'note' && res` チェックの前に汎用セクション検出を追加
    SECTION_DETECT = r"""
                    // ── 汎用セクション自動判別タブ（note以外のツール）──
                    tid !== 'note' && res && (() => {
                        const sectionMarkers = res.match(/---【[^】]+】---/g);
                        if (sectionMarkers && sectionMarkers.length >= 2) {
                            const sectionNames = sectionMarkers.map(m => m.replace(/---【|】---/g, ''));
                            return div({ className: 'flex gap-1 overflow-x-auto hide-scrollbar' },
                                button({ onClick: () => setPreviewTab('all'), className: 'px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition ' + (previewTab === 'all' ? 'bg-brand text-white shadow-lg' : 'glass-panel text-slate-400 hover:text-white') }, '\uD83D\uDCCB 全体'),
                                sectionNames.map((name, i) => button({ key: i, onClick: () => setPreviewTab('sec_' + i), className: 'px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition ' + (previewTab === 'sec_' + i ? 'bg-brand text-white shadow-lg' : 'glass-panel text-slate-400 hover:text-white') }, name))
                            );
                        }
                        return null;
                    })(),
"""

    content = apply_patch(content,
        """                    // ── タブ（note記事は分割表示、その他はallのみ）──
                    tid === 'note' && res ?""",
        SECTION_DETECT + """                    // ── タブ（note記事は分割表示、その他はallのみ）──
                    tid === 'note' && res ?""",
        "汎用セクション自動判別タブ追加"
    )

    # セクション抽出表示ロジック追加（note以外）
    SECTION_RENDER = r"""
                                // 汎用セクション別表示
                                : (() => {
                                    if (previewTab.startsWith('sec_')) {
                                        const secIdx = parseInt(previewTab.replace('sec_', ''));
                                        const sections = res.split(/---【[^】]+】---/).filter(s => s.trim());
                                        const sectionContent = sections[secIdx] || res;
                                        return div({ id: 'preview-tab-content', className: 'bg-white p-5 md:p-8 rounded-2xl shadow-inner preview-content text-black ' + (previewMode === 'mobile' ? 'text-base leading-relaxed' : '') },
                                            div({ dangerouslySetInnerHTML: renderMarkdown(sectionContent.trim()) })
                                        );
                                    }
                                    return div({ id: 'preview-tab-content', className: 'bg-white p-5 md:p-8 rounded-2xl shadow-inner preview-content text-black ' + (previewMode === 'mobile' ? 'text-base leading-relaxed' : '') },
                                        div({ dangerouslySetInnerHTML: renderMarkdown(res) })
                                    );
                                })()"""

    content = apply_patch(content,
        """                : div({ id: 'preview-tab-content', className: 'bg-white p-5 md:p-8 rounded-2xl shadow-inner preview-content text-black ' + (previewMode === 'mobile' ? 'text-base leading-relaxed' : '') },
                                    div({ dangerouslySetInnerHTML: renderMarkdown(res) })
                                )""",
        SECTION_RENDER,
        "汎用セクション別表示レンダリング追加"
    )

    # ================================================================
    # PATCH 11: プロンプトモード3ステップUI
    # ================================================================
    print("\n【PATCH 11】プロンプトモード3ステップUI追加")

    THREESTEP_UI = r"""
          // プロンプトモード3ステップワークフロー
          genMode === 'prompt' && !conf.isImagePrompt && div({ className: 'mb-6 p-4 bg-gradient-to-r from-brand-accent/10 to-orange-500/5 border border-brand-accent/20 rounded-xl animate-in' },
              h4({ className: 'text-xs font-black text-brand-accent mb-3 flex items-center gap-2' }, '\uD83D\uDCCB プロンプトモード 3ステップ'),
              div({ className: 'flex gap-3' },
                  div({ className: 'flex-1 text-center p-2.5 rounded-lg ' + (res ? 'bg-brand-success/20 border border-brand-success/30' : 'bg-brand-accent/20 border border-brand-accent/30') },
                      div({ className: 'text-lg mb-1' }, '\u2776'),
                      p({ className: 'text-[10px] font-bold ' + (res ? 'text-brand-success' : 'text-brand-accent') }, res ? '\u2713 コピー済み' : 'プロンプトをコピー')
                  ),
                  div({ className: 'flex-1 text-center p-2.5 rounded-lg bg-white/5 border border-white/10' },
                      div({ className: 'text-lg mb-1' }, '\u2777'),
                      p({ className: 'text-[10px] font-bold text-slate-400' }, 'ChatGPT等に貼り付けて生成')
                  ),
                  div({ className: 'flex-1 text-center p-2.5 rounded-lg bg-white/5 border border-white/10' },
                      div({ className: 'text-lg mb-1' }, '\u2778'),
                      p({ className: 'text-[10px] font-bold text-slate-400' }, '結果を貼り付けてプレビュー')
                  )
              )
          ),
"""

    content = apply_patch(content,
        "          // フォーム入力エリア\n          div({ className: 'space-y-6 flex-1' },",
        THREESTEP_UI + "          // フォーム入力エリア\n          div({ className: 'space-y-6 flex-1' },",
        "3ステップワークフローUI追加"
    )

    # ================================================================
    # 結果の書き込み
    # ================================================================
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_lines = len(content.splitlines())
    print(f"\n{'='*50}")
    print(f"✅ パッチ適用完了！")
    print(f"   元ファイル: {len(open(backup).readlines())} 行")
    print(f"   更新後: {new_lines} 行")
    print(f"   バックアップ: {backup}")
    print(f"\n📌 次のステップ:")
    print(f"   1. index.htmlのバージョン番号を v=71.6.0 に更新")
    print(f"   2. git add . && git commit -m 'feat: 5機能追加 v71.6.0' && git push")
    print(f"   3. ブラウザでCmd+Shift+R（強制リロード）して確認")

if __name__ == '__main__':
    main()
