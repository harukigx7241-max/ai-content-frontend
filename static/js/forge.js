/* ═══════════════════════════════════════════════════════════════════════
   forge.js — Phase 7 テンプレ鍛冶場
   ForgeVault · ForgeMixer · ForgePath · ForgeCompare
   ═══════════════════════════════════════════════════════════════════════ */

/* ── Helpers ─────────────────────────────────────────────────────────── */
function escHtml(s) {
  return String(s || '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function showForgeToast(msg, duration = 2400) {
  const el = document.getElementById('forgeToast');
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), duration);
}

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('is-open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('is-open');
}

/* close on overlay click or data-close button */
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('forge-modal-overlay')) {
    e.target.classList.remove('is-open');
  }
  const btn = e.target.closest('[data-close]');
  if (btn) closeModal(btn.dataset.close);
});

/* close on Escape */
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.forge-modal-overlay.is-open')
      .forEach(el => el.classList.remove('is-open'));
  }
});

/* ══════════════════════════════════════════════════════════════════════
   ForgeVault — localStorage 保管庫
   ══════════════════════════════════════════════════════════════════════ */
const ForgeVault = (() => {
  const KEY = 'pg_forge_vault_v1';
  const MAX = 30;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; }
    catch { return []; }
  }

  function save(items) {
    localStorage.setItem(KEY, JSON.stringify(items));
  }

  function add(title, content) {
    const items = load();
    const item = {
      id: Date.now(),
      title: title.slice(0, 60),
      content,
      savedAt: new Date().toLocaleDateString('ja-JP'),
    };
    items.unshift(item);
    if (items.length > MAX) items.length = MAX;
    save(items);
    updateBadge();
    // ログイン済みの場合はサーバーにも保存 (fire & forget)
    if (window._pguildLoggedIn) {
      fetch('/api/vault', {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: item.title, content: item.content, source: 'forge' }),
      }).catch(() => {});
    }
    return item;
  }

  function remove(id) {
    save(load().filter(i => i.id !== id));
    updateBadge();
  }

  function clear() {
    save([]);
    updateBadge();
  }

  function updateBadge() {
    const badge = document.getElementById('forgeVaultBadge');
    if (badge) badge.textContent = load().length;
  }

  function renderList() {
    const items = load();
    const list = document.getElementById('vaultList');
    const empty = document.getElementById('vaultEmpty');
    const count = document.getElementById('vaultCount');
    if (!list) return;

    if (count) count.textContent = `${items.length} / ${MAX} 件`;

    if (items.length === 0) {
      list.innerHTML = '';
      list.style.display = 'none';
      if (empty) empty.style.display = '';
      return;
    }
    if (empty) empty.style.display = 'none';
    list.style.display = '';

    list.innerHTML = items.map(item => `
      <div class="forge-vault-item" data-id="${item.id}">
        <div class="forge-vault-item-top">
          <div class="forge-vault-item-title">${escHtml(item.title)}</div>
          <div class="forge-vault-item-actions">
            <button class="forge-vault-action vault-copy-btn" data-id="${item.id}">📋 コピー</button>
            <button class="forge-vault-action delete vault-delete-btn" data-id="${item.id}">🗑️</button>
          </div>
        </div>
        <div class="forge-vault-item-preview">${escHtml(item.content)}</div>
        <div class="forge-vault-item-meta">💾 ${escHtml(item.savedAt)}</div>
      </div>
    `).join('');

    list.querySelectorAll('.vault-copy-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = Number(btn.dataset.id);
        const item = load().find(i => i.id === id);
        if (!item) return;
        navigator.clipboard.writeText(item.content).then(() => showForgeToast('📋 コピーしました'));
      });
    });

    list.querySelectorAll('.vault-delete-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        remove(Number(btn.dataset.id));
        renderList();
        showForgeToast('🗑️ 削除しました');
      });
    });
  }

  /* inject 💾 save buttons next to copy buttons in existing tool outputs */
  function injectSaveBtns() {
    document.querySelectorAll('.copy-btn:not([data-forge-injected])').forEach(copyBtn => {
      copyBtn.dataset.forgeInjected = '1';
      const saveBtn = document.createElement('button');
      saveBtn.className = 'forge-save-btn';
      saveBtn.innerHTML = '💾 保存';
      saveBtn.title = '保管庫へ保存';
      saveBtn.addEventListener('click', () => {
        const outputEl = copyBtn.closest('.result-area, .output-area, .prompt-output')
          || copyBtn.parentElement;
        const textEl = outputEl ? outputEl.querySelector('pre, textarea, .prompt-text, p') : null;
        const content = textEl ? textEl.textContent.trim() : '';
        if (!content) { showForgeToast('⚠️ 保存するテキストが見つかりません'); return; }
        const title = content.split('\n')[0].slice(0, 60) || 'プロンプト';
        add(title, content);
        showForgeToast('💾 保管庫に保存しました');
      });
      copyBtn.parentElement.insertBefore(saveBtn, copyBtn.nextSibling);
    });
  }

  function init() {
    updateBadge();

    document.getElementById('forgeVaultBtn')?.addEventListener('click', () => {
      renderList();
      openModal('forgeVaultModal');
    });

    document.getElementById('vaultClearBtn')?.addEventListener('click', () => {
      if (!confirm('保管庫を全削除しますか？')) return;
      clear();
      renderList();
      showForgeToast('🗑️ 全削除しました');
    });

    /* inject buttons after DOMContentLoaded and after dynamic renders */
    setTimeout(injectSaveBtns, 800);
    document.addEventListener('forge:inject-save', injectSaveBtns);
  }

  return { init, add, load, updateBadge, injectSaveBtns };
})();

/* ══════════════════════════════════════════════════════════════════════
   ForgeMixer — チップ選択でプロンプト下書き組み立て
   ══════════════════════════════════════════════════════════════════════ */
const ForgeMixer = (() => {
  /* Parts text library (API fallback: built-in strings) */
  const PARTS = {
    hook: {
      question: '【書き出し：問いかけ型】\n「あなたは〇〇に悩んでいませんか？」\n読者の心に刺さる問いで始め、共感を引き出してください。',
      story:    '【書き出し：ストーリー型】\n「かつて私も同じ状況でした…」\n具体的なエピソードで始め、読者を物語に引き込んでください。',
      data:     '【書き出し：データ型】\n「実は〇〇人中〇〇人が経験している事実があります」\n信頼性の高い数字・統計で始めてください。',
      shock:    '【書き出し：衝撃型】\n「これを知らないと損をし続けます」\n予想を裏切る事実や逆説で始め、読み続けさせてください。',
    },
    intro: {
      pas:    '【構成：PAS フレームワーク】\n① Problem（問題）: 読者が抱える課題を具体的に描写\n② Agitation（扇動）: 解決しないとどうなるかを掘り下げ\n③ Solution（解決）: あなたのコンテンツ/提案が解決策であると示す',
      aida:   '【構成：AIDA フレームワーク】\n① Attention（注目）: 強力な見出し・冒頭で注目を集める\n② Interest（興味）: 読者が求める情報・メリットを示す\n③ Desire（欲求）: 感情に訴え、強く欲しいと思わせる\n④ Action（行動）: 具体的な行動を促す CTA',
      star:   '【構成：STAR フレームワーク】\n① Situation（状況）: 背景・文脈を設定\n② Task（課題）: 解決すべき問題を明確化\n③ Action（行動）: 具体的な解決策・手順を示す\n④ Result（結果）: 期待できる成果・変化を提示',
      bridge: '【構成：ビフォーアフター型】\nBefore: 現状の辛い状態を共感をもって描写する\nAfter: コンテンツを使った後の理想の状態を鮮明に描く\nBridge: その変化を実現する橋渡しとして本コンテンツを位置づける',
    },
    cta: {
      action: '【CTA：行動促進】\n「まず今日、たった1つだけ試してみてください」\n具体的で小さな行動を提示し、心理的障壁を下げてください。',
      follow: '【CTA：フォロー誘導】\n「続きの情報は〇〇でお届けします。フォローして見逃さないでください」\n次回への期待感と継続的価値を伝えてください。',
      buy:    '【CTA：購入誘導】\n「今だけ〇〇特典付き。ご購入はこちらから」\n限定性・希少性を示し、今すぐ行動する理由を作ってください。',
      share:  '【CTA：シェア促進】\n「役に立ったら周りの〇〇で悩む人に教えてあげてください」\n読者が自分ごととして広めたくなる言葉で締めてください。',
    },
    tone: {
      warm:   'トーン：温かみ・共感重視。読者に寄り添い、「あなたのことをわかっています」と伝わる文体で。',
      expert: 'トーン：専門家・権威。実績・データ・経験に基づいた自信ある口調で、信頼と説得力を演出。',
      casual: 'トーン：カジュアル・親近感。堅苦しくなく、友人に話しかけるような軽やかな文体で。',
      urgent: 'トーン：緊急性・限定感。「今しかない」「見逃したら損」という感覚を自然に醸成する文体で。',
    },
    platform: {
      note:      'メディア：note。有料記事を意識し、無料部分で引き込み、有料エリアで本質を届ける構成にする。',
      x:         'メディア：X (Twitter)。140字の制約を意識し、バズりやすい凝縮表現で。スレッド形式も可。',
      instagram: 'メディア：Instagram。視覚的なイメージと感情に訴えるキャプション。ハッシュタグ提案も含める。',
      cw:        'メディア：クラウドワークス。クライアントが発注したくなる提案文・プロフィールとして最適化。',
      blog:      'メディア：ブログ記事。SEO を意識し、検索意図に沿った構成と見出しで書く。',
    },
    reader: {
      beginner:     'ターゲット：完全初心者。専門用語を避け、「なぜそうなのか」を丁寧に説明。成功体験への最短ルートを示す。',
      intermediate: 'ターゲット：中級者・伸び悩み。「なぜ結果が出ないか」の核心をついた深い洞察と次のステップを提示。',
      busy:         'ターゲット：忙しい会社員。時短・効率・スキマ時間活用を強調。すぐ実践できる具体策を優先。',
      sidehustle:   'ターゲット：副業を始めたい人。最初の1円を稼ぐまでのリアルなロードマップと心理的安心感を提供。',
    },
    goal: {
      sell:    '目的：販売・収益化。読者が「買いたい」「有料でも価値がある」と感じる価値提案に集中する。',
      attract: '目的：集客・認知拡大。シェアされやすく、初見の人でも価値が伝わる間口の広いコンテンツにする。',
      educate: '目的：教育・価値提供。読者が「学べた・成長できた」と感じる知識・スキル・視点を提供する。',
      trust:   '目的：信頼構築。実績・事例・背景を開示し「この人に任せたい・応援したい」という関係を築く。',
    },
  };

  function getSelected(groupId) {
    const el = document.querySelector(`#${groupId} .forge-chip.selected`);
    return el ? el.dataset.val : null;
  }

  function buildPrompt(selections, keyword) {
    const { hook, intro, cta, tone, platform, reader, goal } = selections;
    const kw = keyword ? `\nキーワード：「${keyword}」を中心に展開してください。` : '';
    const lines = [
      '【あなたへの依頼】',
      '以下の設計に従い、副業支援コンテンツのプロンプト下書きを作成してください。',
      kw,
      '',
      hook   ? PARTS.hook[hook]     : '',
      '',
      intro  ? PARTS.intro[intro]   : '',
      '',
      cta    ? PARTS.cta[cta]       : '',
      '',
      '【スタイル指定】',
      tone     ? PARTS.tone[tone]       : '',
      platform ? PARTS.platform[platform] : '',
      '',
      '【読者設定】',
      reader ? PARTS.reader[reader] : '',
      '',
      '【コンテンツ目的】',
      goal   ? PARTS.goal[goal]     : '',
      '',
      '上記の設計に沿って、今すぐ ChatGPT / Gemini / Claude に貼り付けて使えるプロンプトを作成してください。',
    ];
    return lines.filter(l => l !== undefined).join('\n').replace(/\n{3,}/g, '\n\n').trim();
  }

  function init() {
    /* chip toggle — single-select per group */
    document.querySelectorAll('.forge-chip[data-group]').forEach(chip => {
      chip.addEventListener('click', () => {
        const group = chip.dataset.group;
        document.querySelectorAll(`.forge-chip[data-group="${group}"]`)
          .forEach(c => c.classList.remove('selected'));
        chip.classList.add('selected');
      });
    });

    document.getElementById('forgeMixerBtn')?.addEventListener('click', () => openModal('forgeMixerModal'));

    document.getElementById('mixerBuildBtn')?.addEventListener('click', () => {
      const selections = {
        hook:     getSelected('mixerHookGroup'),
        intro:    getSelected('mixerIntroGroup'),
        cta:      getSelected('mixerCtaGroup'),
        tone:     getSelected('mixerToneGroup'),
        platform: getSelected('mixerPlatformGroup'),
        reader:   getSelected('mixerReaderGroup'),
        goal:     getSelected('mixerGoalGroup'),
      };
      const keyword = document.getElementById('mixerKeyword')?.value.trim() || '';
      const prompt = buildPrompt(selections, keyword);

      const preview = document.getElementById('mixerPreview');
      if (preview) {
        preview.textContent = prompt;
        preview.classList.remove('placeholder');
      }
      document.getElementById('mixerCopyBtn').style.display = '';
      document.getElementById('mixerSaveBtn').style.display = '';
    });

    document.getElementById('mixerCopyBtn')?.addEventListener('click', () => {
      const text = document.getElementById('mixerPreview')?.textContent || '';
      navigator.clipboard.writeText(text).then(() => showForgeToast('📋 コピーしました'));
    });

    document.getElementById('mixerSaveBtn')?.addEventListener('click', () => {
      const text = document.getElementById('mixerPreview')?.textContent || '';
      if (!text) return;
      const title = text.split('\n').find(l => l.trim()) || 'Mixer 下書き';
      ForgeVault.add(title.slice(0, 60), text);
      ForgeVault.updateBadge();
      showForgeToast('💾 保管庫に保存しました');
    });
  }

  return { init };
})();

/* ══════════════════════════════════════════════════════════════════════
   ForgePath — 4問ウィザードでテンプレおすすめ
   ══════════════════════════════════════════════════════════════════════ */
const ForgePath = (() => {
  const QUESTIONS = [
    {
      text: '① どのプラットフォームで使いますか？',
      key: 'platform',
      options: [
        { val: 'note',      emoji: '📝', label: 'note (有料記事・コンテンツ販売)' },
        { val: 'sns',       emoji: '📱', label: 'SNS (X・Instagram・Threads)' },
        { val: 'cw',        emoji: '💼', label: 'クラウドワークス (案件獲得)' },
        { val: 'fortune',   emoji: '🔮', label: '占い副業 (ココナラ・鑑定書)' },
        { val: 'blog',      emoji: '✍️', label: 'ブログ・サイト' },
      ],
    },
    {
      text: '② コンテンツの主な目的は？',
      key: 'goal',
      options: [
        { val: 'sell',    emoji: '💰', label: '販売・収益化' },
        { val: 'attract', emoji: '🧲', label: '集客・認知拡大' },
        { val: 'educate', emoji: '📚', label: '教育・価値提供' },
        { val: 'trust',   emoji: '🤝', label: '信頼構築・ブランディング' },
      ],
    },
    {
      text: '③ ターゲット読者のレベルは？',
      key: 'difficulty',
      options: [
        { val: 'beginner',     emoji: '🌱', label: '初心者・ゼロスタート' },
        { val: 'intermediate', emoji: '📈', label: '中級者・伸び悩み' },
        { val: 'advanced',     emoji: '🚀', label: '上級者・プロ向け' },
      ],
    },
    {
      text: '④ 無料で使えるテンプレートを優先しますか？',
      key: 'freeFirst',
      options: [
        { val: 'yes', emoji: '✅', label: '無料テンプレートを優先する' },
        { val: 'no',  emoji: '💎', label: '全テンプレートから選ぶ' },
      ],
    },
  ];

  let step = 0;
  const answers = {};
  let allTemplates = [];

  async function fetchAll() {
    if (allTemplates.length) return allTemplates;
    try {
      const r = await fetch('/api/templates');
      const d = await r.json();
      allTemplates = d.templates || [];
    } catch { allTemplates = []; }
    return allTemplates;
  }

  function scoreTemplate(t, ans) {
    let score = 0;
    const platform = ans.platform || '';
    const goal = ans.goal || '';
    const difficulty = ans.difficulty || '';
    const freeFirst = ans.freeFirst === 'yes';

    /* category → platform match */
    const catMap = { note: 'note', tips: 'note', brain: 'note', blog: 'blog', sales: 'note',
                     email: 'note', common: 'note', prompt_forge: 'note',
                     cw: 'cw', fortune: 'fortune', sns: 'sns' };
    if (catMap[t.category] === platform) score += 4;

    /* platform tags match */
    const platformTags = t.platform || [];
    if (platformTags.some(p => p === platform)) score += 3;

    /* goal tags */
    const tagGoalMap = {
      sell: ['sales', 'monetize', 'cta', 'paid', 'funnel'],
      attract: ['sns', 'viral', 'hook', 'title', 'seo'],
      educate: ['knowledge', 'template', 'guide', 'tutorial'],
      trust: ['profile', 'story', 'testimonial', 'brand'],
    };
    const goalTags = tagGoalMap[goal] || [];
    const tTags = t.tags || [];
    score += tTags.filter(tag => goalTags.some(g => tag.includes(g))).length;

    /* difficulty match */
    if (t.difficulty === difficulty) score += 2;

    /* free bonus */
    if (freeFirst && t.free_available) score += 2;

    return score;
  }

  function renderStep() {
    const q = QUESTIONS[step];
    document.getElementById('pathQuestion').textContent = q.text;

    const optionsEl = document.getElementById('pathOptions');
    optionsEl.innerHTML = q.options.map(o => `
      <button class="forge-path-option${answers[q.key] === o.val ? ' selected' : ''}" data-val="${escHtml(o.val)}">
        <span class="forge-path-option-emoji">${o.emoji}</span>
        ${escHtml(o.label)}
      </button>
    `).join('');

    optionsEl.querySelectorAll('.forge-path-option').forEach(btn => {
      btn.addEventListener('click', () => {
        answers[q.key] = btn.dataset.val;
        optionsEl.querySelectorAll('.forge-path-option').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        /* advance automatically */
        setTimeout(() => {
          step++;
          updateProgress();
          if (step >= QUESTIONS.length) showResults();
          else renderStep();
        }, 300);
      });
    });

    updateProgress();
  }

  function updateProgress() {
    document.querySelectorAll('.forge-path-step-dot').forEach((dot, i) => {
      dot.classList.remove('active', 'done');
      if (i < step) dot.classList.add('done');
      else if (i === step) dot.classList.add('active');
    });
  }

  async function showResults() {
    document.getElementById('pathQuestionArea').style.display = 'none';
    document.getElementById('pathResultsArea').style.display = '';

    const templates = await fetchAll();
    const scored = templates
      .map(t => ({ ...t, _score: scoreTemplate(t, answers) }))
      .filter(t => t._score > 0)
      .sort((a, b) => b._score - a._score)
      .slice(0, 5);

    const resultsEl = document.getElementById('pathResults');
    if (!scored.length) {
      resultsEl.innerHTML = '<div style="color:rgba(255,255,255,0.4);font-size:0.85rem;">条件に合うテンプレートが見つかりませんでした。</div>';
      return;
    }

    resultsEl.innerHTML = scored.map((t, i) => `
      <div class="forge-path-result-card" data-id="${escHtml(t.id)}">
        <div class="forge-path-result-rank">${i + 1}</div>
        <div class="forge-path-result-info">
          <div class="forge-path-result-title">${escHtml(t.title)}</div>
          <div class="forge-path-result-meta">${escHtml(t.category || '')} · ${escHtml(t.difficulty || '')}</div>
        </div>
        <div class="forge-path-result-score">+${t._score}pt</div>
      </div>
    `).join('');

    resultsEl.querySelectorAll('.forge-path-result-card').forEach(card => {
      card.addEventListener('click', async () => {
        const id = card.dataset.id;
        /* delegate to TemplateLibrary if available */
        if (window.TemplateLibrary && typeof window.TemplateLibrary.applyById === 'function') {
          await window.TemplateLibrary.applyById(id);
        }
        closeModal('forgePathModal');
        showForgeToast('✅ テンプレートを適用しました');
      });
    });
  }

  function reset() {
    step = 0;
    Object.keys(answers).forEach(k => delete answers[k]);
    document.getElementById('pathQuestionArea').style.display = '';
    document.getElementById('pathResultsArea').style.display = 'none';
    renderStep();
  }

  function init() {
    document.getElementById('forgePathBtn')?.addEventListener('click', () => {
      reset();
      openModal('forgePathModal');
    });
    document.getElementById('pathRetryBtn')?.addEventListener('click', reset);
  }

  return { init };
})();

/* ══════════════════════════════════════════════════════════════════════
   ForgeCompare — タイトル・CTA・導入文 A/B 比較
   ══════════════════════════════════════════════════════════════════════ */
const ForgeCompare = (() => {
  const POWER_WORDS = [
    '方法', '秘密', '誰も', '完全', '初心者', '月収', '稼ぎ', '無料', '限定', '最速',
    '驚き', 'ゼロから', '達成', '暴露', '真実', '禁断', '最強', '徹底', '厳選', '革命',
    '激変', '爆速', '保存版', '完全版', '究極', '失敗しない', '必見', '決定版',
  ];

  const CTA_PATTERNS = {
    action: { label: '行動促進型', keywords: ['今すぐ', 'さっそく', 'まず', '試して', 'やってみて', '始めて'] },
    follow: { label: 'フォロー誘導型', keywords: ['フォロー', 'チェック', '見逃さない', '通知', '登録'] },
    buy:    { label: '購入誘導型', keywords: ['購入', '申込', '注文', '限定', 'お得', '今だけ'] },
    share:  { label: 'シェア促進型', keywords: ['シェア', 'リツイート', '拡散', '教えて', '広め'] },
    curiosity: { label: '好奇心型', keywords: ['実は', '意外', 'じつは', '知らない', '秘密'] },
  };

  const INTRO_PATTERNS = {
    question:  { label: '問いかけ型', re: /[？?]/ },
    data:      { label: 'データ型', re: /\d+[%％人件万億]/ },
    story:     { label: 'ストーリー型', re: /かつて|以前|昔|あの日|そのとき|私も/ },
    empathy:   { label: '共感型', re: /悩んで|困って|辛い|しんど|疲れ|迷って/ },
    statement: { label: '断言型', re: /です。|ます。|だ。|である。/ },
  };

  function scorePowerWords(text) {
    const found = POWER_WORDS.filter(w => text.includes(w));
    const score = Math.min(100, found.length * 14 + (text.length > 10 ? 10 : 0));
    return { score, found };
  }

  function detectCtaType(text) {
    for (const [key, def] of Object.entries(CTA_PATTERNS)) {
      if (def.keywords.some(k => text.includes(k))) return def.label;
    }
    return '汎用型';
  }

  function detectIntroType(text) {
    for (const [key, def] of Object.entries(INTRO_PATTERNS)) {
      if (def.re.test(text)) return def.label;
    }
    return '説明型';
  }

  function scoreClass(s) {
    if (s >= 60) return 'high';
    if (s >= 30) return 'mid';
    return 'low';
  }

  function renderTitleResult(el, text, label) {
    const { score, found } = scorePowerWords(text);
    const cls = scoreClass(score);
    const tags = found.length
      ? found.map(w => `<span class="forge-compare-word-tag">${escHtml(w)}</span>`).join('')
      : '<span style="color:rgba(255,255,255,0.3);font-size:0.75rem">パワーワードなし</span>';
    el.innerHTML = `
      <h4>${escHtml(label)}</h4>
      <div class="forge-compare-score ${cls}">${score}<small style="font-size:0.55em;font-weight:400">pt</small></div>
      <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);margin-bottom:8px">パワーワードスコア</div>
      <div class="forge-compare-found-words">${tags}</div>
      <div style="font-size:0.76rem;color:rgba(255,255,255,0.35);margin-top:10px">${escHtml(text)}</div>
    `;
  }

  function renderCtaResult(el, text, label) {
    const type = detectCtaType(text);
    const { score, found } = scorePowerWords(text);
    const cls = scoreClass(score);
    el.innerHTML = `
      <h4>${escHtml(label)}</h4>
      <div class="forge-compare-score ${cls}">${score}<small style="font-size:0.55em;font-weight:400">pt</small></div>
      <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);margin-bottom:8px">スコア</div>
      <div style="font-size:0.8rem;color:#c4b5fd;font-weight:700;margin-bottom:8px">🏷️ ${escHtml(type)}</div>
      <div class="forge-compare-text-result">${escHtml(text)}</div>
    `;
  }

  function renderIntroResult(el, text, label) {
    const type = detectIntroType(text);
    const charCount = text.replace(/\s/g, '').length;
    const { score } = scorePowerWords(text);
    const cls = scoreClass(score);
    el.innerHTML = `
      <h4>${escHtml(label)}</h4>
      <div class="forge-compare-score ${cls}">${score}<small style="font-size:0.55em;font-weight:400">pt</small></div>
      <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);margin-bottom:8px">スコア</div>
      <div style="font-size:0.8rem;color:#c4b5fd;font-weight:700;margin-bottom:6px">🏷️ ${escHtml(type)}</div>
      <div style="font-size:0.75rem;color:rgba(255,255,255,0.35);margin-bottom:8px">文字数: ${charCount}字</div>
      <div class="forge-compare-text-result">${escHtml(text.slice(0, 120))}${text.length > 120 ? '…' : ''}</div>
    `;
  }

  function init() {
    document.getElementById('forgeCompareBtn')?.addEventListener('click', () => openModal('forgeCompareModal'));

    /* compare tabs */
    document.querySelectorAll('.forge-compare-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.forge-compare-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.forge-compare-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.panel)?.classList.add('active');
      });
    });

    /* title compare */
    document.getElementById('compareTitleBtn')?.addEventListener('click', () => {
      const a = document.getElementById('titleA')?.value.trim();
      const b = document.getElementById('titleB')?.value.trim();
      if (!a || !b) { showForgeToast('⚠️ A と B を両方入力してください'); return; }
      const grid = document.getElementById('titleResults');
      renderTitleResult(document.getElementById('titleResultA'), a, 'タイトル A');
      renderTitleResult(document.getElementById('titleResultB'), b, 'タイトル B');
      grid.style.display = '';
    });

    /* CTA compare */
    document.getElementById('compareCtaBtn')?.addEventListener('click', () => {
      const a = document.getElementById('ctaA')?.value.trim();
      const b = document.getElementById('ctaB')?.value.trim();
      if (!a || !b) { showForgeToast('⚠️ A と B を両方入力してください'); return; }
      const grid = document.getElementById('ctaResults');
      renderCtaResult(document.getElementById('ctaResultA'), a, 'CTA A');
      renderCtaResult(document.getElementById('ctaResultB'), b, 'CTA B');
      grid.style.display = '';
    });

    /* Intro compare */
    document.getElementById('compareIntroBtn')?.addEventListener('click', () => {
      const a = document.getElementById('introA')?.value.trim();
      const b = document.getElementById('introB')?.value.trim();
      if (!a || !b) { showForgeToast('⚠️ A と B を両方入力してください'); return; }
      const grid = document.getElementById('introResults');
      renderIntroResult(document.getElementById('introResultA'), a, '導入文 A');
      renderIntroResult(document.getElementById('introResultB'), b, '導入文 B');
      grid.style.display = '';
    });
  }

  return { init };
})();

/* ══════════════════════════════════════════════════════════════════════
   Boot
   ══════════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  ForgeVault.init();
  ForgeMixer.init();
  ForgePath.init();
  ForgeCompare.init();
});
