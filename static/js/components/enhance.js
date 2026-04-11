'use strict';
/**
 * static/js/components/enhance.js
 * Phase 1: プロンプト強化パネル
 *
 * 責務:
 *   1. 空欄補完ウィジェット — フォーム上部に注入、ヒント→フォーム入力案を生成
 *   2. 強化パネル — result-area 下部に注入、生成後に表示
 *      ・前置き不要モード  → /api/enhance/direct_output
 *      ・note装飾モード    → /api/enhance/note_format  (note タブのみ)
 *      ・AI深層最適化      → /api/enhance/ai_optimize
 *      ・画像プロンプト生成 → /api/enhance/image_prompt
 *
 * 設計方針:
 *   - app.js の既存メソッドには触れない (App.showToast / App.copyText は window 経由で参照)
 *   - 注入ずみカードを WeakSet で追跡し二重注入を防ぐ
 *   - promptReady カスタムイベント (app.js が dispatch) をトリガーに強化パネルを表示
 *
 * TODO: Phase 3+ - ユーザー設定でデフォルト強化モードを保存できるようにする
 */

const Enhance = {
  _initialized: new WeakSet(),

  /** app.js の App.init() から呼ばれるエントリポイント */
  init() {
    document.querySelectorAll('.card[data-endpoint]').forEach(card => {
      if (this._initialized.has(card)) return;
      this._initialized.add(card);

      // バンドルカードは除外（結果構造が異なる）
      if (card.dataset.endpoint === '/api/project/bundle') return;

      this._injectAutocomplete(card);
      this._injectEnhancePanel(card);
    });
  },

  // ═══════════════════════════════════════════════════════════════════
  // 1. 空欄補完ウィジェット
  // ═══════════════════════════════════════════════════════════════════

  _injectAutocomplete(card) {
    const cardBody = card.querySelector('.card-body');
    if (!cardBody) return;

    // /api/note/article → category="note", tool="article"
    const parts = (card.dataset.endpoint || '').split('/');
    const category = parts[2] || '';
    const tool     = parts[3] || '';
    if (!category || !tool) return;

    const widget = document.createElement('div');
    widget.className = 'autocomplete-widget';
    widget.innerHTML = `
      <button class="autocomplete-toggle-btn" type="button">
        💡 AIにフォーム入力を提案してもらう
      </button>
      <div class="autocomplete-panel" style="display:none">
        <textarea
          class="autocomplete-hint-input"
          placeholder="作りたいものをひとことで入力してください（例: noteで月5万円稼ぐ方法）"
          rows="2"
        ></textarea>
        <div class="autocomplete-panel-footer">
          <button class="autocomplete-run-btn" type="button">✦ 入力案を提案</button>
          <span class="autocomplete-hint-label">各フォーム項目の入力案を AI が生成します</span>
        </div>
        <div class="autocomplete-result" style="display:none">
          <div class="autocomplete-result-label">
            📋 入力案（コピーして各フォーム欄に貼り付けてください）
          </div>
          <textarea class="result-textarea autocomplete-result-textarea" rows="10"></textarea>
          <button class="copy-btn autocomplete-copy-btn" type="button">コピー</button>
        </div>
      </div>
    `;

    // フォームの最初の要素の前に挿入
    const anchor = cardBody.querySelector('.template-chips, .ai-mode-row, .quality-score-row, .field-group');
    if (anchor) {
      cardBody.insertBefore(widget, anchor);
    } else {
      cardBody.prepend(widget);
    }

    // ─── イベント ───────────────────────────────────────────────────

    const toggleBtn  = widget.querySelector('.autocomplete-toggle-btn');
    const panel      = widget.querySelector('.autocomplete-panel');
    const runBtn     = widget.querySelector('.autocomplete-run-btn');
    const hintInput  = widget.querySelector('.autocomplete-hint-input');
    const resultEl   = widget.querySelector('.autocomplete-result');
    const resultTA   = widget.querySelector('.autocomplete-result-textarea');
    const copyBtn    = widget.querySelector('.autocomplete-copy-btn');

    toggleBtn.addEventListener('click', () => {
      const open = panel.style.display !== 'none';
      panel.style.display = open ? 'none' : 'block';
      toggleBtn.textContent = open ? '💡 AIにフォーム入力を提案してもらう' : '✕ 閉じる';
    });

    runBtn.addEventListener('click', () => this._runAutocomplete({
      card, category, tool, hintInput, runBtn, resultEl, resultTA,
    }));

    // Ctrl+Enter でも実行
    hintInput.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runBtn.click();
    });

    copyBtn.addEventListener('click', () => this._copy(copyBtn, resultTA.value));
  },

  async _runAutocomplete({ card, category, tool, hintInput, runBtn, resultEl, resultTA }) {
    const hint = hintInput.value.trim();
    if (!hint) { hintInput.focus(); return; }

    const ai_mode = card.querySelector('.ai-mode-input')?.value || 'ChatGPT';

    runBtn.disabled = true;
    runBtn.textContent = '生成中...';
    try {
      const data = await this._post('/api/enhance/autocomplete', { category, tool, hint, ai_mode });
      resultTA.value = data.prompt || '';
      resultEl.style.display = 'block';
      this._toast('入力案を生成しました', 'success');
    } catch {
      this._toast('生成に失敗しました', 'error');
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = '✦ 入力案を提案';
    }
  },

  // ═══════════════════════════════════════════════════════════════════
  // 2. 強化パネル
  // ═══════════════════════════════════════════════════════════════════

  _injectEnhancePanel(card) {
    const resultArea = card.querySelector('.result-area');
    if (!resultArea) return;

    const category = (card.dataset.endpoint || '').split('/')[2] || '';

    const panel = document.createElement('div');
    panel.className = 'enhance-panel';
    panel.style.display = 'none';
    panel.innerHTML = `
      <div class="enhance-panel-header">✦ プロンプト強化</div>
      <div class="enhance-panel-actions">
        <button class="enhance-btn" data-action="direct_output" title="前置き不要の完成文出力指示を追加">
          ⚡ 前置き不要
        </button>
        ${category === 'note' ? `
        <button class="enhance-btn" data-action="note_format" title="note.com向け装飾指示を追加">
          📝 note装飾
        </button>` : ''}
        <button class="enhance-btn" data-action="ai_optimize" title="AIプラン別の深い最適化指示を追加">
          🎯 AI深層最適化
        </button>
        <button class="enhance-btn" data-action="image_prompt" title="記事テーマから画像生成AIプロンプトを作成">
          🖼 画像プロンプト
        </button>
      </div>

      <!-- 画像プロンプト専用結果エリア -->
      <div class="enhance-image-result" style="display:none">
        <div class="enhance-image-result-header">
          <span class="enhance-result-label">🖼 画像生成プロンプト</span>
          <div class="enhance-image-options">
            <select class="enhance-image-platform">
              <option value="Midjourney">Midjourney</option>
              <option value="DALL-E">DALL-E</option>
              <option value="StableDiffusion">Stable Diffusion</option>
              <option value="Adobe Firefly">Adobe Firefly</option>
            </select>
            <select class="enhance-image-type">
              <option value="thumbnail">サムネイル</option>
              <option value="section">記事内挿絵</option>
              <option value="social">SNS告知</option>
              <option value="cover">カバー画像</option>
            </select>
            <button class="enhance-btn enhance-image-regen-btn" style="padding:4px 10px;font-size:0.75rem">再生成</button>
          </div>
        </div>
        <textarea class="result-textarea enhance-image-textarea" rows="9"></textarea>
        <div style="display:flex;gap:8px;margin-top:6px">
          <button class="copy-btn enhance-image-copy-btn" type="button">コピー</button>
          <span style="font-size:0.72rem;color:var(--text-muted);align-self:center">このプロンプトを Midjourney / DALL-E 等に貼り付けてください</span>
        </div>
      </div>
    `;

    resultArea.appendChild(panel);

    // promptReady イベントで表示 (app.js が dispatch)
    card.addEventListener('promptReady', () => {
      panel.style.display = 'block';
    });

    // 強化ボタン
    panel.querySelectorAll('.enhance-btn[data-action]').forEach(btn => {
      btn.addEventListener('click', () => this._runEnhance(btn.dataset.action, card, panel));
    });

    // 画像再生成
    const regenBtn = panel.querySelector('.enhance-image-regen-btn');
    regenBtn?.addEventListener('click', () => this._runEnhance('image_prompt', card, panel));

    // 画像プロンプトコピー
    const imgCopyBtn = panel.querySelector('.enhance-image-copy-btn');
    const imgTA      = panel.querySelector('.enhance-image-textarea');
    imgCopyBtn?.addEventListener('click', () => this._copy(imgCopyBtn, imgTA?.value || ''));
  },

  async _runEnhance(action, card, panel) {
    // 既存の生成プロンプト textarea (enhance-image-textarea は除外)
    const ta = card.querySelector('.result-area .result-textarea:not(.enhance-image-textarea):not(.autocomplete-result-textarea)');
    if (!ta || !ta.value.trim()) {
      this._toast('先にプロンプトを生成してください', 'warning');
      return;
    }

    const ai_mode = card.querySelector('.ai-mode-input')?.value || 'ChatGPT';
    const prompt  = ta.value;

    const btn = panel.querySelector(`[data-action="${action}"]`);
    const origLabel = btn?.textContent;
    if (btn) { btn.disabled = true; btn.textContent = '処理中...'; }

    try {
      if (action === 'image_prompt') {
        await this._runImagePrompt(card, panel, ai_mode);
      } else {
        const endpointMap = {
          direct_output: '/api/enhance/direct_output',
          note_format:   '/api/enhance/note_format',
          ai_optimize:   '/api/enhance/ai_optimize',
        };
        const ep = endpointMap[action];
        if (!ep) return;

        const body = action === 'ai_optimize' ? { prompt, ai_mode } : { prompt };
        const data = await this._post(ep, body);
        ta.value = data.prompt || '';

        // 字数カウント更新
        const cc = card.querySelector('.char-count');
        if (cc) cc.textContent = ta.value.length.toLocaleString('ja-JP') + '字';

        const labels = {
          direct_output: '前置き不要モードを適用しました',
          note_format:   'note装飾モードを適用しました',
          ai_optimize:   'AI深層最適化を適用しました',
        };
        this._toast(labels[action] || 'プロンプトを強化しました', 'success');
      }
    } catch {
      this._toast('強化処理に失敗しました', 'error');
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = origLabel; }
    }
  },

  async _runImagePrompt(card, panel, ai_mode) {
    // テーマをフォームから取得（なければ生成済みプロンプトの冒頭100字）
    const themeInput = card.querySelector('input[name="theme"], textarea[name="theme"]');
    const topicInput = card.querySelector('input[name="topic"], textarea[name="topic"]');
    const ta         = card.querySelector('.result-area .result-textarea:not(.enhance-image-textarea):not(.autocomplete-result-textarea)');
    const theme      = themeInput?.value || topicInput?.value || ta?.value?.slice(0, 100) || '';

    const platform   = panel.querySelector('.enhance-image-platform')?.value || 'Midjourney';
    const image_type = panel.querySelector('.enhance-image-type')?.value || 'thumbnail';
    const style      = 'モダン・クリーン・プロフェッショナル';

    const data = await this._post('/api/enhance/image_prompt', {
      theme, image_type, style, platform, ai_mode,
    });

    const imgResult = panel.querySelector('.enhance-image-result');
    const imgTA     = panel.querySelector('.enhance-image-textarea');
    if (imgResult && imgTA) {
      imgTA.value = data.prompt || '';
      imgResult.style.display = 'block';
    }
    this._toast('画像生成プロンプトを作成しました', 'success');
  },

  // ═══════════════════════════════════════════════════════════════════
  // ユーティリティ
  // ═══════════════════════════════════════════════════════════════════

  async _post(endpoint, body) {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  },

  _toast(message, type = 'success') {
    // app.js の App.showToast を優先、なければ console.log にフォールバック
    if (window.App?.showToast) {
      window.App.showToast(message, type);
    } else {
      console.log(`[Enhance] ${type}: ${message}`);
    }
  },

  _copy(btn, text) {
    if (!text) return;
    if (window.App?.copyText) {
      window.App.copyText(btn, text);
    } else {
      navigator.clipboard.writeText(text).catch(() => {});
    }
  },
};

window.Enhance = Enhance;
