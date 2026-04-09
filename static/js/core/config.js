'use strict';
/**
 * static/js/core/config.js
 * フロントエンド側の設定ヘルパー。
 * window.AppConfig はサーバーサイド (Jinja2) で index.html に埋め込まれる。
 * このファイルは AppConfig への型付きアクセスと、
 * 告知バーの初期化など起動時ロジックを担う。
 *
 * TODO: Phase 1+ で認証済みユーザー向けの設定 (マイページ情報等) を追加する。
 */

const Config = {
  /** 機能フラグを取得する */
  isFeatureEnabled(feature) {
    return window.AppConfig?.features?.[feature] ?? false;
  },

  /** 告知バー設定を取得する */
  getNoticeBanner() {
    return window.AppConfig?.noticeBanner ?? { enabled: false, text: '', link: '' };
  },

  /** メンテナンスモード中か */
  isMaintenanceMode() {
    return window.AppConfig?.maintenance ?? false;
  },

  /**
   * 起動時の初期化処理。
   * index.html の <script> ブロック内で window.AppConfig が設定された後に呼ばれる。
   */
  init() {
    this._initNoticeBanner();
    // TODO: Phase 2 - this._initAdminBar();
    // TODO: Phase 3 - this._initCommunityBadge();
  },

  _initNoticeBanner() {
    const banner = this.getNoticeBanner();
    if (!banner.enabled || !banner.text) return;

    const el = document.getElementById('noticeBanner');
    if (!el) return;

    const textEl = el.querySelector('.notice-banner-text');
    const linkEl = el.querySelector('.notice-banner-link');

    if (textEl) textEl.textContent = banner.text;
    if (linkEl) {
      if (banner.link) {
        linkEl.href = banner.link;
        linkEl.style.display = '';
      } else {
        linkEl.style.display = 'none';
      }
    }
    el.style.display = '';
  },
};

// グローバルに公開（app.js から参照可能）
window.Config = Config;
