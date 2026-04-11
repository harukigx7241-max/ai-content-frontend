'use strict';

const App = {

  // ═══════════════════════════════════════════
  // Tab Switching
  // ═══════════════════════════════════════════
  initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => this.switchTab(btn.dataset.tab));
    });
    // Keyboard: left/right arrow keys to switch tabs
    document.addEventListener('keydown', e => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
      const tabs = ['note', 'cw', 'fortune', 'sns'];
      const active = document.querySelector('.tab-btn.active')?.dataset.tab;
      const idx = tabs.indexOf(active);
      if (e.key === 'ArrowRight' && idx < tabs.length - 1) this.switchTab(tabs[idx + 1]);
      if (e.key === 'ArrowLeft'  && idx > 0)               this.switchTab(tabs[idx - 1]);
    });
  },

  switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    const btn   = document.querySelector(`.tab-btn[data-tab="${tabId}"]`);
    const panel = document.getElementById(`tab-${tabId}`);
    if (btn)   btn.classList.add('active');
    if (panel) panel.classList.add('active');
    // タブ切替音
    if (window.Effects) Effects.play('click');
    // ボトムナビ同期
    this.updateBottomNav(tabId);
  },

  updateBottomNav(tabId) {
    const map = { note: 'mbnNote', cw: 'mbnCw', fortune: 'mbnFortune', sns: 'mbnSns' };
    Object.values(map).forEach(id => document.getElementById(id)?.classList.remove('active'));
    if (map[tabId]) document.getElementById(map[tabId])?.classList.add('active');
  },

  // ═══════════════════════════════════════════
  // AI Mode Selector
  // ═══════════════════════════════════════════
  initAiModeSelectors() {
    document.querySelectorAll('.ai-mode-row').forEach(row => {
      const btns  = row.querySelectorAll('.ai-mode-btn');
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

  // ═══════════════════════════════════════════
  // Template Gallery
  // ═══════════════════════════════════════════
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
        this.updateQualityScore(card);
        const btn = card.querySelector('.generate-btn');
        if (btn && !btn.classList.contains('ready-pulse')) {
          btn.classList.add('ready-pulse');
          setTimeout(() => btn.classList.remove('ready-pulse'), 3000);
        }
        this.showToast('テンプレートを読み込みました', 'info');
      });
    });
  },

  // ═══════════════════════════════════════════
  // Quality Score
  // ═══════════════════════════════════════════
  initQualityScores() {
    document.querySelectorAll('.card').forEach(card => {
      card.querySelectorAll('input[type="text"], textarea').forEach(inp => {
        inp.addEventListener('input', () => this.updateQualityScore(card));
      });
    });
  },

  updateQualityScore(card) {
    const scoreEl = card.querySelector('.quality-stars');
    const hintEl  = card.querySelector('.quality-hint');
    if (!scoreEl) return;
    const inputs = [...card.querySelectorAll('input[type="text"]')].filter(el => !el.closest('.ai-mode-row'));
    const filled = inputs.filter(i => i.value.trim().length > 5).length;
    const total  = inputs.length || 1;
    const ratio  = filled / total;
    const map = [
      [1.0,  '★★★★★', '最高精度のプロンプトです！'],
      [0.75, '★★★★☆', 'あと少しで最高精度！'],
      [0.5,  '★★★☆☆', 'もう少し詳しく入力するとUP'],
      [0.25, '★★☆☆☆', '必須項目(*)を入力してください'],
      [0,    '★☆☆☆☆', '入力を充実させると精度UP'],
    ];
    const [, stars, hint] = map.find(([t]) => ratio >= t);
    scoreEl.textContent = stars;
    if (hintEl) hintEl.textContent = hint;
  },

  // ═══════════════════════════════════════════
  // Dynamic Enhancements (injected into DOM)
  // ═══════════════════════════════════════════
  enhanceCards() {
    document.querySelectorAll('.card[data-endpoint]').forEach(card => {
      // 1. Keyboard hint under generate btn
      const btn = card.querySelector('.generate-btn');
      if (btn && !card.querySelector('.kbd-hint')) {
        const hint = document.createElement('div');
        hint.className = 'kbd-hint';
        hint.innerHTML = '<kbd>Ctrl</kbd> + <kbd>Enter</kbd> でも生成できます';
        btn.after(hint);
      }

      // 2. Progress bar
      const resultArea = card.querySelector('.result-area');
      if (resultArea && !card.querySelector('.progress-bar-track')) {
        const track = document.createElement('div');
        track.className = 'progress-bar-track';
        track.innerHTML = '<div class="progress-bar-fill"></div>';
        btn?.after(track);
      }

      // 3. Inject expand / share / remix buttons into result-area
      if (resultArea && !resultArea.querySelector('.expand-btn')) {
        const actions = resultArea.querySelector('.result-actions');
        if (actions) {
          // Expand button
          const expandBtn = document.createElement('button');
          expandBtn.className = 'expand-btn';
          expandBtn.textContent = '⛶ 全画面';
          actions.prepend(expandBtn);

          // Share button
          const shareBtn = document.createElement('button');
          shareBtn.className = 'share-btn';
          shareBtn.textContent = '🔗 共有';
          actions.insertBefore(shareBtn, actions.firstChild);
        }

        // Remix toggle
        const ta = resultArea.querySelector('.result-textarea');
        if (ta) {
          // Char count row
          const ccRow = document.createElement('div');
          ccRow.className = 'char-count-row';
          ccRow.innerHTML = '<span class="char-count">0字</span>';
          ta.after(ccRow);

          // Share URL box
          const shareBox = document.createElement('div');
          shareBox.className = 'share-url-box';
          shareBox.innerHTML = '<button class="share-url-copy">コピー</button><span class="share-url-text"></span>';
          ccRow.after(shareBox);

          // Remix panel
          const remixPanel = document.createElement('div');
          remixPanel.className = 'remix-panel';
          remixPanel.innerHTML = `
            <div class="remix-panel-label">🔁 別アングルで再生成</div>
            <div class="remix-variants">
              <button class="remix-variant-btn active" data-variant="emotional">💗 感情・共感型</button>
              <button class="remix-variant-btn" data-variant="logical">📊 データ・論理型</button>
              <button class="remix-variant-btn" data-variant="story">📖 ストーリー型</button>
              <button class="remix-variant-btn" data-variant="beginner">🌱 超初心者向け</button>
            </div>
            <button class="remix-generate-btn">🔁 このアングルで再生成</button>
          `;
          shareBox.after(remixPanel);

          // Remix toggle btn in actions
          const actions2 = resultArea.querySelector('.result-actions');
          if (actions2) {
            const remixToggle = document.createElement('button');
            remixToggle.className = 'remix-toggle-btn';
            remixToggle.textContent = '🔁';
            remixToggle.title = 'リミックス';
            actions2.appendChild(remixToggle);
          }

          // Live char count
          ta.addEventListener('input', () => {
            const cc = ccRow.querySelector('.char-count');
            if (cc) cc.textContent = ta.value.length.toLocaleString('ja-JP') + '字';
          });
        }
      }
    });
  },

  // ═══════════════════════════════════════════
  // Tool Cards: Generic Form Handler
  // ═══════════════════════════════════════════
  initToolCards() {
    document.querySelectorAll('.card[data-endpoint]').forEach(card => {
      const btn      = card.querySelector('.generate-btn');
      const endpoint = card.dataset.endpoint;
      if (!btn || !endpoint) return;

      btn.addEventListener('click', () => this.handleGenerate(card, endpoint));

      // Ctrl+Enter shortcut
      card.addEventListener('keydown', e => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
          e.preventDefault();
          this.handleGenerate(card, endpoint);
        }
      });
    });
  },

  serializeForm(card) {
    const data = {};
    card.querySelectorAll('[name]').forEach(el => {
      if (el.name && el.value !== undefined) data[el.name] = el.value;
    });
    return data;
  },

  async handleGenerate(card, endpoint) {
    const btn        = card.querySelector('.generate-btn');
    const resultArea = card.querySelector('.result-area');
    const textarea   = card.querySelector('.result-textarea');
    const track      = card.querySelector('.progress-bar-track');

    // ゲスト利用制限チェック
    if (window.GuestUsage) {
      const g = window.GuestUsage.checkLimit();
      if (!g.allowed) {
        window.GuestUsage.showLimitModal();
        return;
      }
    }

    // Validate required text inputs
    const textInputs = [...card.querySelectorAll('input[type="text"][name]')]
      .filter(el => !el.closest('.ai-mode-row'));
    const empties = textInputs.filter(el => el.value.trim() === '');
    if (empties.length > 0) {
      empties[0].focus();
      empties[0].style.borderColor = 'rgba(244,114,182,0.8)';
      empties[0].style.boxShadow = '0 0 0 3px rgba(244,114,182,0.15)';
      setTimeout(() => {
        empties[0].style.borderColor = '';
        empties[0].style.boxShadow = '';
      }, 1800);
      this.showToast('必須項目を入力してください', 'warning');
      return;
    }

    this.setLoading(btn, true, track);

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.serializeForm(card))
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const text = data.prompt || '';

      resultArea.classList.add('show');
      await this.typewriterEffect(textarea, text);
      card.dispatchEvent(new CustomEvent('promptReady', { bubbles: false })); // Phase 1: enhance panel trigger
      if (window.Storage && text) window.Storage.addHistory(endpoint, text); // Phase 1: auto history

      // Update char count
      const cc = card.querySelector('.char-count');
      if (cc) cc.textContent = text.length.toLocaleString('ja-JP') + '字';

      // Show remix panel
      const remixPanel = card.querySelector('.remix-panel');
      if (remixPanel) remixPanel.classList.add('show');

      // Smooth scroll to result
      setTimeout(() => resultArea.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 100);

      // ゲスト利用カウントアップ（ログイン済みは無視）
      if (window.GuestUsage) window.GuestUsage.increment();
      // 効果音
      if (window.Effects) Effects.play('success');

      this.showToast('プロンプト生成完了！コピーして使おう ✓', 'success');

    } catch (err) {
      if (textarea) textarea.value = `エラーが発生しました。\n${err.message}`;
      resultArea.classList.add('show');
      this.showToast(`エラー: ${err.message}`, 'error');
    } finally {
      this.setLoading(btn, false, track);
    }
  },

  setLoading(btn, isLoading, track) {
    if (isLoading) {
      btn.classList.add('loading');
      btn.dataset.origText = btn.textContent;
      btn.textContent = '✦ 生成中...';
      if (track) track.classList.add('running');
    } else {
      btn.classList.remove('loading');
      if (btn.dataset.origText) btn.textContent = btn.dataset.origText;
      if (track) { track.classList.remove('running'); }
    }
  },

  // ═══════════════════════════════════════════
  // Typewriter Effect
  // ═══════════════════════════════════════════
  async typewriterEffect(textarea, text) {
    if (!textarea) return;
    textarea.value = '';
    textarea.classList.add('typing-cursor');

    const CHUNK = 12; // chars per frame
    let i = 0;
    return new Promise(resolve => {
      const tick = () => {
        if (i >= text.length) {
          textarea.classList.remove('typing-cursor');
          resolve();
          return;
        }
        textarea.value += text.slice(i, i + CHUNK);
        i += CHUNK;
        // Auto-scroll textarea
        textarea.scrollTop = textarea.scrollHeight;
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  },

  // ═══════════════════════════════════════════
  // Copy Buttons
  // ═══════════════════════════════════════════
  initCopyButtons() {
    document.addEventListener('click', e => {
      const btn = e.target.closest('.copy-btn');
      if (!btn) return;
      let text = '';

      if (btn.id === 'bundleCopyBtn')      text = document.getElementById('bundleResultText')?.value || '';
      else if (btn.id === 'fullscreenCopyBtn') text = document.getElementById('fullscreenTextarea')?.value || '';
      else if (btn.id === 'sharedCopyBtn')    text = document.getElementById('sharedPreview')?.textContent || '';
      else {
        const ta = btn.closest('.result-area, .bundle-results')
          ?.querySelector('.result-textarea, #bundleResultText');
        text = ta?.value || '';
      }

      if (text.trim()) this.copyText(btn, text);
    });

    // Share URL box inner copy
    document.addEventListener('click', e => {
      if (e.target.classList.contains('share-url-copy')) {
        const box = e.target.closest('.share-url-box');
        const url = box?.querySelector('.share-url-text')?.textContent || '';
        if (url) {
          navigator.clipboard.writeText(url).then(() => {
            e.target.textContent = 'コピー済み ✓';
            setTimeout(() => { e.target.textContent = 'コピー'; }, 2000);
          });
        }
      }
    });
  },

  copyText(btn, text) {
    navigator.clipboard.writeText(text).then(() => {
      btn.classList.add('copied');
      const prev = btn.textContent;
      btn.textContent = 'コピー済み ✓';
      setTimeout(() => { btn.textContent = prev; btn.classList.remove('copied'); }, 2000);
      if (window.Effects) { Effects.play('copy'); Effects.ripple(btn); }
      this.showToast('クリップボードにコピーしました', 'success');
    }).catch(() => this.showToast('コピーに失敗しました', 'error'));
  },

  // ═══════════════════════════════════════════
  // Fullscreen Modal
  // ═══════════════════════════════════════════
  _fullscreenSource: null, // reference to source textarea

  initFullscreen() {
    const overlay  = document.getElementById('fullscreenOverlay');
    const closeBtn = document.getElementById('fullscreenClose');
    const fsTa     = document.getElementById('fullscreenTextarea');
    const fsCount  = document.getElementById('fullscreenCharCount');
    const fsCopy   = document.getElementById('fullscreenCopyBtn');
    const fsSave   = document.getElementById('fullscreenSaveBtn');

    if (!overlay) return;

    // Open fullscreen via expand-btn
    document.addEventListener('click', e => {
      const expandBtn = e.target.closest('.expand-btn');
      if (!expandBtn) return;
      const resultArea = expandBtn.closest('.result-area');
      const sourceTa   = resultArea?.querySelector('.result-textarea');
      const card       = expandBtn.closest('.card');
      const titleEl    = card?.querySelector('.card-title');

      if (!sourceTa) return;
      this._fullscreenSource = sourceTa;
      fsTa.value = sourceTa.value;
      fsCount.textContent = fsTa.value.length.toLocaleString('ja-JP') + '字';
      document.getElementById('fullscreenTitle').textContent = `✦ ${titleEl?.textContent || 'プロンプト'} — 全画面編集`;

      // Save button
      if (fsSave) {
        fsSave.style.display = 'inline-flex';
        fsSave.onclick = () => {
          const title = titleEl?.textContent || 'プロンプト';
          this.saveToHistory(title, fsTa.value);
          this.showToast('プロンプトを保存しました ⭐', 'success');
        };
      }

      overlay.classList.add('open');
      setTimeout(() => fsTa.focus(), 300);
    });

    // Sync back to source on edit
    fsTa?.addEventListener('input', () => {
      if (this._fullscreenSource) this._fullscreenSource.value = fsTa.value;
      if (fsCount) fsCount.textContent = fsTa.value.length.toLocaleString('ja-JP') + '字';
      // Sync char count in card
      if (this._fullscreenSource) {
        const card = this._fullscreenSource.closest('.card');
        const cc = card?.querySelector('.char-count');
        if (cc) cc.textContent = fsTa.value.length.toLocaleString('ja-JP') + '字';
      }
    });

    // Close
    const close = () => overlay.classList.remove('open');
    closeBtn?.addEventListener('click', close);
    overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && overlay.classList.contains('open')) close();
    });
  },

  // ═══════════════════════════════════════════
  // URL Share
  // ═══════════════════════════════════════════
  initShareButtons() {
    document.addEventListener('click', e => {
      const shareBtn = e.target.closest('.share-btn');
      if (!shareBtn) return;
      const resultArea = shareBtn.closest('.result-area');
      const ta = resultArea?.querySelector('.result-textarea');
      const shareBox = resultArea?.querySelector('.share-url-box');
      if (!ta || !ta.value.trim()) { this.showToast('先にプロンプトを生成してください', 'warning'); return; }

      const encoded = btoa(encodeURIComponent(ta.value));
      const url = `${location.origin}${location.pathname}#share=${encoded}`;

      if (shareBox) {
        const textEl = shareBox.querySelector('.share-url-text');
        if (textEl) textEl.textContent = url;
        shareBox.classList.toggle('show');
      }

      navigator.clipboard.writeText(url).then(() => {
        this.showToast('共有リンクをクリップボードにコピーしました 🔗', 'success');
        shareBtn.textContent = '✓ リンクコピー';
        setTimeout(() => { shareBtn.textContent = '🔗 共有'; }, 3000);
      });
    });

    // Check for shared prompt on load
    this.checkSharedPrompt();
  },

  checkSharedPrompt() {
    const hash = location.hash;
    if (!hash.startsWith('#share=')) return;
    try {
      const encoded = hash.slice(7);
      const text = decodeURIComponent(atob(encoded));
      const banner = document.getElementById('sharedBanner');
      const preview = document.getElementById('sharedPreview');
      const copyBtn = document.getElementById('sharedCopyBtn');
      if (banner && preview) {
        preview.textContent = text.slice(0, 300) + (text.length > 300 ? '...' : '');
        banner.classList.add('show');
        if (copyBtn) {
          copyBtn.addEventListener('click', () => this.copyText(copyBtn, text));
        }
        // Auto hide after 15s
        setTimeout(() => banner.classList.remove('show'), 15000);
      }
    } catch { /* ignore */ }
  },

  // ═══════════════════════════════════════════
  // Remix
  // ═══════════════════════════════════════════
  initRemix() {
    // Variant selector
    document.addEventListener('click', e => {
      const variantBtn = e.target.closest('.remix-variant-btn');
      if (!variantBtn) return;
      const panel = variantBtn.closest('.remix-panel');
      panel?.querySelectorAll('.remix-variant-btn').forEach(b => b.classList.remove('active'));
      variantBtn.classList.add('active');
    });

    // Remix toggle btn
    document.addEventListener('click', e => {
      const toggleBtn = e.target.closest('.remix-toggle-btn');
      if (!toggleBtn) return;
      const resultArea = toggleBtn.closest('.result-area');
      const panel = resultArea?.querySelector('.remix-panel');
      if (panel) panel.classList.toggle('show');
    });

    // Remix generate
    document.addEventListener('click', async e => {
      const genBtn = e.target.closest('.remix-generate-btn');
      if (!genBtn) return;
      const panel      = genBtn.closest('.remix-panel');
      const resultArea = genBtn.closest('.result-area');
      const ta         = resultArea?.querySelector('.result-textarea');
      const activeVariant = panel?.querySelector('.remix-variant-btn.active')?.dataset.variant || 'emotional';
      const aiMode = resultArea?.closest('.card')?.querySelector('.ai-mode-input')?.value || 'ChatGPT';

      if (!ta?.value.trim()) { this.showToast('先にプロンプトを生成してください', 'warning'); return; }

      genBtn.classList.add('loading');
      genBtn.textContent = '🔁 生成中...';

      try {
        const res = await fetch('/api/remix', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ original_prompt: ta.value, variant: activeVariant, ai_mode: aiMode })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        await this.typewriterEffect(ta, data.prompt || '');

        const cc = resultArea.closest('.card')?.querySelector('.char-count');
        if (cc) cc.textContent = (data.prompt?.length || 0).toLocaleString('ja-JP') + '字';

        const variantLabels = { emotional:'感情・共感型', logical:'データ・論理型', story:'ストーリー型', beginner:'超初心者向け' };
        this.showToast(`「${variantLabels[activeVariant] || activeVariant}」で再生成しました`, 'success');
      } catch (err) {
        this.showToast(`エラー: ${err.message}`, 'error');
      } finally {
        genBtn.classList.remove('loading');
        genBtn.textContent = '🔁 このアングルで再生成';
      }
    });
  },

  // ═══════════════════════════════════════════
  // Toast Notifications
  // ═══════════════════════════════════════════
  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const icons = { success:'✓', info:'✦', warning:'⚠', error:'✕' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-icon">${icons[type] || '✦'}</span>${message}`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('hide');
      toast.addEventListener('animationend', () => toast.remove());
    }, 3000);
  },

  // ═══════════════════════════════════════════
  // Save / History
  // ═══════════════════════════════════════════
  HISTORY_KEY: 'promptHistory',
  MAX_HISTORY: 30,

  initSaveButtons() {
    document.addEventListener('click', e => {
      const btn = e.target.closest('.save-btn');
      if (!btn || btn.id === 'fullscreenSaveBtn') return;
      const ta = btn.closest('.result-area')?.querySelector('.result-textarea');
      if (!ta?.value.trim()) { this.showToast('先にプロンプトを生成してください', 'warning'); return; }
      const title = btn.closest('.card')?.querySelector('.card-title')?.textContent || 'プロンプト';
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
    this.showToast(`「${title}」を保存しました ⭐`, 'success');
  },

  getHistory() {
    try { return JSON.parse(localStorage.getItem(this.HISTORY_KEY) || '[]'); }
    catch { return []; }
  },

  renderHistory() {
    const list    = document.getElementById('historyList');
    const badge   = document.getElementById('historyBadge');
    const history = this.getHistory();
    if (badge) badge.textContent = history.length > 0 ? String(history.length) : '';
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
          <span>${String(item.prompt).length.toLocaleString('ja-JP')}字</span>
        </div>
        <div class="history-item-actions">
          <button class="history-action-btn" data-action="copy"     data-id="${item.id}">コピー</button>
          <button class="history-action-btn" data-action="expand"   data-id="${item.id}">全画面</button>
          <button class="history-action-btn" data-action="delete"   data-id="${item.id}">削除</button>
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
        this.showToast('履歴を削除しました', 'info');
      }
    });

    document.addEventListener('click', e => {
      const btn = e.target.closest('.history-action-btn');
      if (!btn) return;
      const id     = Number(btn.dataset.id);
      const action = btn.dataset.action;
      const history = this.getHistory();
      const item   = history.find(h => h.id === id);
      if (!item) return;

      if (action === 'copy') {
        navigator.clipboard.writeText(item.prompt).then(() => {
          btn.textContent = '✓';
          this.showToast('コピーしました', 'success');
          setTimeout(() => { btn.textContent = 'コピー'; }, 2000);
        });
      } else if (action === 'expand') {
        const fsTa    = document.getElementById('fullscreenTextarea');
        const overlay = document.getElementById('fullscreenOverlay');
        const title   = document.getElementById('fullscreenTitle');
        if (fsTa && overlay) {
          this._fullscreenSource = null;
          fsTa.value = item.prompt;
          if (title) title.textContent = `✦ ${item.title}`;
          const fsCount = document.getElementById('fullscreenCharCount');
          if (fsCount) fsCount.textContent = item.prompt.length.toLocaleString('ja-JP') + '字';
          overlay.classList.add('open');
        }
      } else if (action === 'delete') {
        const updated = history.filter(h => h.id !== id);
        localStorage.setItem(this.HISTORY_KEY, JSON.stringify(updated));
        this.renderHistory();
        this.showToast('削除しました', 'info');
      }
    });

    document.addEventListener('click', e => {
      if (panel?.classList.contains('open') && !panel.contains(e.target) && !toggle?.contains(e.target))
        panel.classList.remove('open');
    });
  },

  // ═══════════════════════════════════════════
  // Revenue Simulator
  // ═══════════════════════════════════════════
  initSimulator() {
    const els = ['sim-price','sim-sales','sim-months'].map(id => document.getElementById(id));
    if (!els[0]) return;
    const update = () => {
      const [p, s, m] = els.map(el => parseFloat(el?.value) || 0);
      const monthly = p * s;
      const annual  = monthly * 12;
      const total   = monthly * (m || 1);
      const fmt = n => '¥' + Math.round(n).toLocaleString('ja-JP');
      document.getElementById('sim-monthly').textContent = fmt(monthly);
      document.getElementById('sim-annual').textContent  = fmt(annual);
      document.getElementById('sim-total').textContent   = fmt(total);
    };
    els.forEach(el => el?.addEventListener('input', update));
    update();
  },

  // ═══════════════════════════════════════════
  // Bundle / Project Mode
  // ═══════════════════════════════════════════
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
        this.showToast('テーマを入力してください', 'warning');
        return;
      }
      btn.textContent = '⚡ 生成中...';
      btn.disabled = true;
      try {
        const res = await fetch('/api/project/bundle', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ theme, target: target || 'プロンプト初心者', ai_mode: aiMode })
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        bundleData = await res.json();
        activeKey  = Object.keys(bundleData)[0] || '';

        tabsEl.innerHTML = Object.keys(bundleData).map(key => `
          <button class="bundle-result-tab${key === activeKey ? ' active' : ''}" data-key="${key}">
            ${labels[key] || key}
          </button>
        `).join('');

        textEl.value = bundleData[activeKey] || '';
        results.classList.add('show');

        tabsEl.querySelectorAll('.bundle-result-tab').forEach(t => {
          t.addEventListener('click', () => {
            tabsEl.querySelectorAll('.bundle-result-tab').forEach(x => x.classList.remove('active'));
            t.classList.add('active');
            activeKey = t.dataset.key;
            textEl.value = bundleData[activeKey] || '';
          });
        });

        this.showToast(`5種類のプロンプトを一括生成しました ⚡`, 'success');
        results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } catch (err) {
        textEl.value = `エラー: ${err.message}`;
        results.classList.add('show');
        this.showToast(`エラー: ${err.message}`, 'error');
      } finally {
        btn.textContent = '⚡ 一括生成';
        btn.disabled = false;
      }
    });
  },

  // ═══════════════════════════════════════════
  // Init
  // ═══════════════════════════════════════════
  init() {
    this.initTabs();
    this.initAiModeSelectors();
    this.initTemplateChips();
    this.initQualityScores();
    this.enhanceCards();          // inject dynamic UI elements
    this.initToolCards();
    this.initCopyButtons();
    this.initFullscreen();
    this.initShareButtons();
    this.initRemix();
    this.initSaveButtons();
    this.initHistoryPanel();
    this.initSimulator();
    this.initBundle();
    this.renderHistory();
    if (window.Enhance) window.Enhance.init(); // Phase 1: enhance panel
    if (window.Storage) window.Storage.init(); // Phase 1: form auto-save
    this.initMobileMenu();
    document.body.classList.add('has-bottom-nav');
  },

  // ═══════════════════════════════════════════
  // Mobile Hamburger + Drawer
  // ═══════════════════════════════════════════
  initMobileMenu() {
    const btn    = document.getElementById('hamburgerBtn');
    const drawer = document.getElementById('mobileDrawer');
    if (!btn || !drawer) return;

    btn.addEventListener('click', () => {
      const isOpen = drawer.classList.toggle('open');
      btn.classList.toggle('open', isOpen);
      btn.setAttribute('aria-expanded', isOpen);
      drawer.setAttribute('aria-hidden', !isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
      if (window.Effects) Effects.play(isOpen ? 'open' : 'close');
    });

    // ドロワー外タップで閉じる
    document.addEventListener('click', e => {
      if (drawer.classList.contains('open') &&
          !drawer.contains(e.target) && !btn.contains(e.target)) {
        drawer.classList.remove('open');
        btn.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        drawer.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      }
    });

    // Esc で閉じる
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape' && drawer.classList.contains('open')) {
        drawer.classList.remove('open');
        btn.classList.remove('open');
        btn.setAttribute('aria-expanded', 'false');
        drawer.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
      }
    });
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
