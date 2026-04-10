'use strict';
/**
 * static/js/core/storage.js
 * pguild:v1: キースキームを使った localStorage ラッパー。
 * フォーム自動保存・プロンプト履歴・お気に入りの基盤。
 *
 * キー構造:
 *   pguild:v1:form:{endpoint_escaped}   — フォーム入力値
 *   pguild:v1:history:{endpoint_escaped} — 生成履歴 (最大 MAX_HISTORY 件)
 *   pguild:v1:fav:list                  — お気に入り一覧
 *
 * TODO: Phase 2+ でマイページ実装時にこのキー構造をサーバー同期の基盤にする。
 */

const Storage = {
  PREFIX: 'pguild:v1:',
  MAX_HISTORY: 20,

  // ─── 低レベル API ────────────────────────────────────────────────

  _key(type, sub) {
    return `${this.PREFIX}${type}:${sub}`;
  },

  set(type, sub, value) {
    try {
      localStorage.setItem(this._key(type, sub), JSON.stringify(value));
    } catch (e) {
      // ストレージ容量超過などは無視
      console.warn('[Storage] set failed:', e);
    }
  },

  get(type, sub, fallback = null) {
    try {
      const raw = localStorage.getItem(this._key(type, sub));
      return raw !== null ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  },

  remove(type, sub) {
    try {
      localStorage.removeItem(this._key(type, sub));
    } catch {
      // ignore
    }
  },

  // ─── フォーム自動保存 ────────────────────────────────────────────

  _escapeKey(endpoint) {
    return endpoint.replace(/\//g, '_');
  },

  saveForm(endpoint, data) {
    this.set('form', this._escapeKey(endpoint), data);
  },

  loadForm(endpoint) {
    return this.get('form', this._escapeKey(endpoint), {});
  },

  // ─── プロンプト履歴 ──────────────────────────────────────────────

  addHistory(endpoint, prompt) {
    const sub = this._escapeKey(endpoint);
    const list = this.get('history', sub, []);
    // 同一プロンプトは先頭に移動（重複排除）
    const filtered = list.filter(item => item.prompt !== prompt);
    filtered.unshift({ prompt, endpoint, ts: Date.now() });
    if (filtered.length > this.MAX_HISTORY) filtered.length = this.MAX_HISTORY;
    this.set('history', sub, filtered);
  },

  getHistory(endpoint) {
    return this.get('history', this._escapeKey(endpoint), []);
  },

  getAllHistory() {
    const all = [];
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && k.startsWith(`${this.PREFIX}history:`)) {
          const items = JSON.parse(localStorage.getItem(k) || '[]');
          all.push(...items);
        }
      }
    } catch {
      // ignore
    }
    return all.sort((a, b) => b.ts - a.ts).slice(0, this.MAX_HISTORY);
  },

  // ─── お気に入り ──────────────────────────────────────────────────

  toggleFavorite(endpoint, prompt) {
    const favs = this.get('fav', 'list', []);
    const idx = favs.findIndex(f => f.prompt === prompt && f.endpoint === endpoint);
    if (idx >= 0) {
      favs.splice(idx, 1);
      this.set('fav', 'list', favs);
      return false; // 削除
    }
    favs.unshift({ endpoint, prompt, ts: Date.now() });
    this.set('fav', 'list', favs);
    return true; // 追加
  },

  isFavorite(endpoint, prompt) {
    const favs = this.get('fav', 'list', []);
    return favs.some(f => f.prompt === prompt && f.endpoint === endpoint);
  },

  getFavorites() {
    return this.get('fav', 'list', []);
  },

  // ─── 初期化 ──────────────────────────────────────────────────────

  init() {
    document.querySelectorAll('.card[data-endpoint]').forEach(card => {
      const endpoint = card.dataset.endpoint;
      if (!endpoint) return;

      // 保存済み入力値をフォームに復元（空欄のみ）
      const saved = this.loadForm(endpoint);
      if (saved && Object.keys(saved).length > 0) {
        Object.entries(saved).forEach(([name, value]) => {
          const el = card.querySelector(`[name="${name}"]`);
          if (el && !el.value) el.value = value;
        });
      }

      // フォーム変更時に保存
      card.querySelectorAll('input[name], textarea[name], select[name]').forEach(el => {
        el.addEventListener('change', () => {
          const current = this.loadForm(endpoint);
          current[el.name] = el.value;
          this.saveForm(endpoint, current);
        });
      });
    });
  },
};

window.Storage = Storage;
