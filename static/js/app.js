'use strict';

const App = {

  // ─── Tab Switching ───────────────────────────────────
  initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
    });
  },

  switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    const btn = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const panel = document.getElementById(`tab-${tabId}`);
    if (btn) btn.classList.add('active');
    if (panel) panel.classList.add('active');
  },

  // ─── AI Mode Selector ────────────────────────────────
  initAiModeSelectors() {
    document.querySelectorAll('.ai-mode-row').forEach(row => {
      const btns = row.querySelectorAll('.ai-mode-btn');
      const input = row.querySelector('.ai-mode-input');
      btns.forEach(btn => {
        btn.addEventListener('click', () => {
          btns.forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          if (input) input.value = btn.dataset.ai;
        });
      });
    });
  },

  // ─── Template Gallery ────────────────────────────────
  initTemplateChips() {
    document.querySelectorAll('.template-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const fillData = JSON.parse(chip.dataset.fill || '{}');
        const card = chip.closest('.card');
        if (!card) return;
        Object.entries(fillData).forEach(([name, val]) => {
          const el = card.querySelector(`[name="${name}"]`);
          if (el) el.value = val;
        });
        // Trigger quality score update
        this.updateQualityScore(card);
      });
    });
  },

  // ─── Quality Score ───────────────────────────────────
  initQualityScores() {
    document.querySelectorAll('.card').forEach(card => {
      const inputs = card.querySelectorAll('input[type="text"], textarea');
      inputs.forEach(inp => {
        inp.addEventListener('input', () => this.updateQualityScore(card));
      });
    });
  },

  updateQualityScore(card) {
    const scoreEl = card.querySelector('.quality-stars');
    const hintEl  = card.querySelector('.quality-hint');
    if (!scoreEl) return;
    const inputs = [...card.querySelectorAll('input[type="text"], textarea')];
    const filled = inputs.filter(i => i.value.trim().length > 3).length;
    const total  = inputs.length || 1;
    const ratio  = filled / total;
    let stars = '☆☆☆☆☆';
    let hint  = '入力を充実させると精度UP';
    if (ratio >= 1)         { stars = '★★★★★'; hint = '最高精度のプロンプトです！'; }
    else if (ratio >= 0.75) { stars = '★★★★☆'; hint = 'あと少しで最高精度！'; }
    else if (ratio >= 0.5)  { stars = '★★★☆☆'; hint = 'もう少し詳しく入力するとUP'; }
    else if (ratio >= 0.25) { stars = '★★☆☆☆'; hint = '必須項目(*)を入力してください'; }
    scoreEl.textContent = stars;
    if (hintEl) hintEl.textContent = hint;
  },

  // ─── Tool Cards: Generic Form Handler ────────────────
  initToolCards() {
    document.querySelectorAll('.card[data-endpoint]').forEach(card => {
      const btn      = card.querySelector('.generate-btn');
      const endpoint = card.dataset.endpoint;
      if (!btn || !endpoint) return;
      btn.addEventListener('click', () => this.handleGenerate(card, endpoint));
    });
  },

  serializeForm(card) {
    const data = {};
    card.querySelectorAll('[name]').forEach(el => {
      if (el.name && el.value !== undefined) data[el.name] = el.value;
    });
    return data;
  },

  validateRequired(card) {
    const required = card.querySelectorAll('input[type="text"][name]');
    // Only validate inputs that aren't hidden
    const empties = [...required].filter(el =>
      !el.closest('.ai-mode-row') && el.value.trim() === '' &&
      el.closest('.field-group')?.querySelector('label')?.textContent.includes('*')
    );
    return empties.length === 0;
  },

  async handleGenerate(card, endpoint) {
    const btn       = card.querySelector('.generate-btn');
    const resultArea = card.querySelector('.result-area');
    const textarea  = card.querySelector('.result-textarea');

    const body = this.serializeForm(card);

    // Simple validation: check required text inputs are non-empty
    const allTextInputs = [...card.querySelectorAll('input[type="text"][name]')]
      .filter(el => !el.closest('.ai-mode-row'));
    const emptyRequired = allTextInputs.filter(el => el.value.trim() === '');
    if (emptyRequired.length > 0) {
      emptyRequired[0].focus();
      emptyRequired[0].style.borderColor = 'rgba(244,114,182,0.8)';
      setTimeout(() => emptyRequired[0].style.borderColor = '', 1500);
      return;
    }

    this.setLoading(btn, true);

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const text = data.prompt || '';
      textarea.value = text;
      resultArea.classList.add('show');
    } catch (err) {
      textarea.value = `エラーが発生しました。\n${err.message}`;
      resultArea.classList.add('show');
    } finally {
      this.setLoading(btn, false);
    }
  },

  setLoading(btn, isLoading) {
    const textEl = btn.querySelector('.btn-text') || btn;
    if (isLoading) {
      btn.classList.add('loading');
      btn.dataset.origText = textEl.textContent;
      textEl.textContent = '生成中...';
    } else {
      btn.classList.remove('loading');
      if (btn.dataset.origText) textEl.textContent = btn.dataset.origText;
    }
  },

  // ─── Copy Buttons ─────────────────────────────────────
  initCopyButtons() {
    document.addEventListener('click', e => {
      const btn = e.target.closest('.copy-btn');
      if (!btn) return;
      // Bundle copy
      if (btn.id === 'bundleCopyBtn') {
        const ta = document.getElementById('bundleResultText');
        if (ta) this.copyText(btn, ta.value);
        return;
      }
      const ta = btn.closest('.result-area, .bundle-results')?.querySelector('.result-textarea, #bundleResultText');
      if (ta) this.copyText(btn, ta.value);
    });
  },

  copyText(btn, text) {
    if (!text.trim()) return;
    navigator.clipboard.writeText(text).then(() => {
      btn.classList.add('copied');
      const prev = btn.textContent;
      btn.textContent = 'コピー済み ✓';
      setTimeout(() => { btn.textContent = prev; btn.classList.remove('copied'); }, 2000);
    });
  },

  // ─── Save / History ──────────────────────────────────
  HISTORY_KEY: 'promptHistory',
  MAX_HISTORY: 30,

  initSaveButtons() {
    document.addEventListener('click', e => {
      const btn = e.target.closest('.save-btn');
      if (!btn) return;
      const ta = btn.closest('.result-area')?.querySelector('.result-textarea');
      if (!ta || !ta.value.trim()) return;
      const card = btn.closest('.card');
      const titleEl = card?.querySelector('.card-title');
      const title = titleEl ? titleEl.textContent : 'プロンプト';
      this.saveToHistory(title, ta.value);
      btn.textContent = '⭐ 保存済み';
      setTimeout(() => { btn.textContent = '⭐ 保存'; }, 2000);
    });
  },

  saveToHistory(title, prompt) {
    const history = this.getHistory();
    history.unshift({ id: Date.now(), title, prompt, date: new Date().toLocaleDateString('ja-JP') });
    if (history.length > this.MAX_HISTORY) history.splice(this.MAX_HISTORY);
    localStorage.setItem(this.HISTORY_KEY, JSON.stringify(history));
    this.renderHistory();
  },

  getHistory() {
    try { return JSON.parse(localStorage.getItem(this.HISTORY_KEY) || '[]'); }
    catch { return []; }
  },

  renderHistory() {
    const list    = document.getElementById('historyList');
    const badge   = document.getElementById('historyBadge');
    const history = this.getHistory();
    if (badge) badge.textContent = history.length > 0 ? history.length : '';
    if (!list) return;
    if (history.length === 0) {
      list.innerHTML = '<div class="history-empty">まだ保存されたプロンプトがありません<br>⭐ 保存ボタンで追加しよう</div>';
      return;
    }
    list.innerHTML = history.map(item => `
      <div class="history-item" data-id="${item.id}">
        <div class="history-item-title">${this.escHtml(item.title)}</div>
        <div class="history-item-meta">
          <span>${item.date}</span>
          <span>${String(item.prompt).length}字</span>
        </div>
        <div class="history-item-actions">
          <button class="history-action-btn" data-action="copy" data-id="${item.id}">コピー</button>
          <button class="history-action-btn" data-action="delete" data-id="${item.id}">削除</button>
        </div>
      </div>
    `).join('');
  },

  escHtml(str) {
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  },

  initHistoryPanel() {
    const toggle = document.getElementById('historyToggle');
    const panel  = document.getElementById('historyPanel');
    const clear  = document.getElementById('historyClearBtn');

    toggle?.addEventListener('click', () => panel?.classList.toggle('open'));

    clear?.addEventListener('click', () => {
      if (confirm('保存済みプロンプトをすべて削除しますか？')) {
        localStorage.removeItem(this.HISTORY_KEY);
        this.renderHistory();
      }
    });

    document.addEventListener('click', e => {
      const actionBtn = e.target.closest('.history-action-btn');
      if (!actionBtn) return;
      const id     = Number(actionBtn.dataset.id);
      const action = actionBtn.dataset.action;
      const history = this.getHistory();
      const item   = history.find(h => h.id === id);
      if (!item) return;
      if (action === 'copy') {
        navigator.clipboard.writeText(item.prompt).then(() => {
          actionBtn.textContent = 'コピー済み ✓';
          setTimeout(() => { actionBtn.textContent = 'コピー'; }, 2000);
        });
      } else if (action === 'delete') {
        const updated = history.filter(h => h.id !== id);
        localStorage.setItem(this.HISTORY_KEY, JSON.stringify(updated));
        this.renderHistory();
      }
    });

    // Close on outside click
    document.addEventListener('click', e => {
      if (panel?.classList.contains('open') &&
          !panel.contains(e.target) &&
          !toggle?.contains(e.target)) {
        panel.classList.remove('open');
      }
    });
  },

  // ─── Revenue Simulator ───────────────────────────────
  initSimulator() {
    const price  = document.getElementById('sim-price');
    const sales  = document.getElementById('sim-sales');
    const months = document.getElementById('sim-months');
    if (!price) return;
    const update = () => {
      const p = parseFloat(price.value) || 0;
      const s = parseFloat(sales.value) || 0;
      const m = parseFloat(months.value) || 1;
      const monthly = p * s;
      const annual  = monthly * 12;
      const total   = monthly * m;
      const fmt = n => '¥' + Math.round(n).toLocaleString('ja-JP');
      document.getElementById('sim-monthly').textContent = fmt(monthly);
      document.getElementById('sim-annual').textContent  = fmt(annual);
      document.getElementById('sim-total').textContent   = fmt(total);
    };
    [price, sales, months].forEach(el => el?.addEventListener('input', update));
    update();
  },

  // ─── Bundle / Project Mode ───────────────────────────
  initBundle() {
    const btn     = document.getElementById('bundleBtn');
    const results = document.getElementById('bundleResults');
    const tabsEl  = document.getElementById('bundleResultTabs');
    const textEl  = document.getElementById('bundleResultText');
    if (!btn) return;

    const labels = {
      note_article:  '📖 note記事',
      note_titles:   '🏷️ タイトル',
      note_gift:     '🎁 特典',
      sns_twitter:   '𝕏 X投稿',
      sns_instagram: '📸 Instagram',
    };

    let bundleData = {};
    let activeKey  = '';

    btn.addEventListener('click', async () => {
      const theme  = document.getElementById('bundle-theme')?.value.trim();
      const target = document.getElementById('bundle-target')?.value.trim();
      const aiMode = document.getElementById('bundle-ai')?.value || 'ChatGPT';
      if (!theme) {
        document.getElementById('bundle-theme')?.focus();
        return;
      }
      btn.textContent = '⚡ 生成中...';
      btn.disabled = true;
      try {
        const res = await fetch('/api/project/bundle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ theme, target: target || '副業初心者', ai_mode: aiMode })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        bundleData = await res.json();
        activeKey  = Object.keys(bundleData)[0] || '';

        // Render tabs
        tabsEl.innerHTML = Object.keys(bundleData).map(key => `
          <button class="bundle-result-tab${key === activeKey ? ' active' : ''}" data-key="${key}">
            ${labels[key] || key}
          </button>
        `).join('');

        textEl.value = bundleData[activeKey] || '';
        results.classList.add('show');

        // Tab click
        tabsEl.querySelectorAll('.bundle-result-tab').forEach(t => {
          t.addEventListener('click', () => {
            tabsEl.querySelectorAll('.bundle-result-tab').forEach(x => x.classList.remove('active'));
            t.classList.add('active');
            activeKey = t.dataset.key;
            textEl.value = bundleData[activeKey] || '';
          });
        });
      } catch (err) {
        textEl.value = `エラー: ${err.message}`;
        results.classList.add('show');
      } finally {
        btn.textContent = '⚡ 一括生成';
        btn.disabled = false;
      }
    });
  },

  // ─── Init ─────────────────────────────────────────────
  init() {
    this.initTabs();
    this.initAiModeSelectors();
    this.initTemplateChips();
    this.initQualityScores();
    this.initToolCards();
    this.initCopyButtons();
    this.initSaveButtons();
    this.initHistoryPanel();
    this.initSimulator();
    this.initBundle();
    this.renderHistory();
  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
