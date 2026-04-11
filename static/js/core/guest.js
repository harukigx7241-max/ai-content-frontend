'use strict';
/**
 * static/js/core/guest.js
 * ゲスト利用制限 — 未ログインユーザーの1日あたり生成回数を localStorage で管理する。
 *
 * 仕様:
 *   - 未ログイン: 1日 DAILY_LIMIT 回まで生成可能
 *   - localStorage キー pguild_guest に { date, count } を保存
 *   - 日付が変わるとカウントを 0 にリセット
 *   - 上限到達時: 登録を促すモーダルを表示
 *   - ログイン済み (window._pguildLoggedIn === true): 制限なし
 *
 * 依存:
 *   - window._pguildLoggedIn : auth nav スクリプトが設定する (true/false)
 *   - #guestUsageBadge       : 残回数表示バッジ要素
 *   - #guestLimitModal        : 上限到達モーダル要素
 */
const GuestUsage = {
  STORAGE_KEY: 'pguild_guest',
  DAILY_LIMIT: 3,

  /* ── 内部ヘルパー ──────────────────────────────────── */
  _today() {
    return new Date().toISOString().slice(0, 10); // "YYYY-MM-DD"
  },

  _load() {
    try {
      const d = JSON.parse(localStorage.getItem(this.STORAGE_KEY) || '{}');
      if (d.date !== this._today()) return { date: this._today(), count: 0 };
      return d;
    } catch {
      return { date: this._today(), count: 0 };
    }
  },

  _save(d) {
    try { localStorage.setItem(this.STORAGE_KEY, JSON.stringify(d)); } catch {}
  },

  /* ── 公開 API ──────────────────────────────────────── */

  /** ログイン済みか */
  isLoggedIn() {
    return window._pguildLoggedIn === true;
  },

  /**
   * 生成を許可するか返す。
   * @returns {{ allowed: boolean, count: number, max: number }}
   */
  checkLimit() {
    if (this.isLoggedIn()) return { allowed: true, count: 0, max: this.DAILY_LIMIT };
    const s = this._load();
    return {
      allowed: s.count < this.DAILY_LIMIT,
      count:   s.count,
      max:     this.DAILY_LIMIT,
    };
  },

  /** 生成成功後に呼ぶ。カウントを1増やしてバッジを更新する。 */
  increment() {
    if (this.isLoggedIn()) return;
    const s = this._load();
    s.count = (s.count || 0) + 1;
    this._save(s);
    this._updateBadge();
  },

  /** 残回数バッジを更新する。ログイン済みなら非表示。 */
  _updateBadge() {
    const el = document.getElementById('guestUsageBadge');
    if (!el) return;

    if (this.isLoggedIn()) {
      el.style.display = 'none';
      return;
    }

    const s         = this._load();
    const remaining = Math.max(0, this.DAILY_LIMIT - s.count);
    el.style.display = '';
    const remEl = el.querySelector('.guest-remaining');
    if (remEl) remEl.textContent = remaining;
    el.classList.toggle('exhausted', remaining === 0);
  },

  /** 上限到達モーダルを表示する。 */
  showLimitModal() {
    const el = document.getElementById('guestLimitModal');
    if (el) el.classList.add('show');
  },

  /** 初期化 (DOMContentLoaded 後に呼ぶ)。 */
  init() {
    // auth/me の非同期完了を待って 600ms 後にバッジを初期化する
    setTimeout(() => this._updateBadge(), 600);
    // バッジクリックでモーダルを開く
    const badge = document.getElementById('guestUsageBadge');
    if (badge) {
      badge.addEventListener('click', () => {
        if (!this.isLoggedIn()) this.showLimitModal();
      });
    }
  },
};
