/**
 * static/js/congestion.js — 混雑状況ウィジェット (Phase 11)
 *
 * 機能:
 *  - GET /api/system/congestion を 60 秒ごとにポーリング
 *  - ヘッダーに混雑ピル (.congestion-pill) を挿入
 *  - medium 以上のとき混雑バナー (#congestionBanner) を表示
 *  - 外部から CongestionWidget.getLevel() で現在レベルを取得可能
 */
const CongestionWidget = (() => {
  'use strict';

  const POLL_INTERVAL_MS = 60_000;
  const API_URL = '/api/system/congestion';

  const COLOR_MAP = { low: '#34d399', medium: '#fbbf24', high: '#f97316', critical: '#f87171' };
  const ICON_MAP  = { low: '🟢', medium: '🟡', high: '🟠', critical: '🔴' };

  let _currentLevel = 'low';
  let _pillEl   = null;
  let _bannerEl = null;
  let _timer    = null;

  // ── DOM 初期化 ──────────────────────────────────────────────────
  function _createPill() {
    const pill = document.createElement('span');
    pill.className = 'congestion-pill';
    pill.dataset.level = 'low';
    pill.title = '現在の混雑状況';
    pill.innerHTML = '<span class="cong-pill-icon">🟢</span><span class="cong-pill-text">確認中...</span>';
    return pill;
  }

  function _createBanner() {
    const el = document.createElement('div');
    el.id = 'congestionBanner';
    el.className = 'congestion-banner';
    el.setAttribute('role', 'status');
    el.innerHTML = `
      <span style="font-size:1.2rem;flex-shrink:0" id="congBannerIcon"></span>
      <div class="congestion-banner-body">
        <div class="congestion-banner-title" id="congBannerTitle"></div>
        <div class="congestion-banner-detail" id="congBannerDetail"></div>
        <span class="congestion-banner-hint" id="congBannerHint" style="display:none"></span>
      </div>
      <button onclick="this.parentElement.classList.remove('show')"
              style="background:none;border:none;cursor:pointer;color:inherit;opacity:0.5;font-size:1rem;padding:0;flex-shrink:0"
              aria-label="閉じる">✕</button>
    `;
    return el;
  }

  // ── レンダリング ───────────────────────────────────────────────
  function _render(data) {
    _currentLevel = data.level || 'low';

    // ピル更新
    if (_pillEl) {
      _pillEl.dataset.level = _currentLevel;
      _pillEl.querySelector('.cong-pill-icon').textContent = ICON_MAP[_currentLevel] || '🟢';
      _pillEl.querySelector('.cong-pill-text').textContent = data.label || _currentLevel;
      _pillEl.title = `混雑状況: ${data.label}${data.active_approx ? ` (直近30分 ~${data.active_approx}人)` : ''}`;
    }

    // バナー更新 (medium 以上で表示)
    if (_bannerEl) {
      const showBanner = ['medium', 'high', 'critical'].includes(_currentLevel);
      _bannerEl.dataset.level = _currentLevel;

      if (showBanner) {
        _bannerEl.querySelector('#congBannerIcon').textContent  = ICON_MAP[_currentLevel];
        _bannerEl.querySelector('#congBannerTitle').textContent = data.label || '';
        _bannerEl.querySelector('#congBannerDetail').textContent = data.wait_estimate || '';

        const hintEl = _bannerEl.querySelector('#congBannerHint');
        if (data.light_mode_hint) {
          hintEl.textContent   = data.light_mode_hint;
          hintEl.style.display = '';
        } else {
          hintEl.style.display = 'none';
        }
        _bannerEl.classList.add('show');
      } else {
        _bannerEl.classList.remove('show');
      }
    }
  }

  // ── API フェッチ ───────────────────────────────────────────────
  async function _fetch() {
    try {
      const res = await fetch(API_URL, { cache: 'no-store' });
      if (!res.ok) return;
      const data = await res.json();
      _render(data);
    } catch { /* silent — ネットワークエラー時は現状維持 */ }
  }

  // ── 初期化 ────────────────────────────────────────────────────
  function init() {
    // ピルをヘッダーの auth-nav に挿入
    const authNav = document.getElementById('authNav');
    if (authNav) {
      _pillEl = _createPill();
      authNav.insertBefore(_pillEl, authNav.firstChild);
    }

    // バナーをメインコンテンツの先頭に挿入 (存在しない場合はスキップ)
    const heroSection = document.querySelector('.hero, main, .mypage-container, .admin-container');
    if (heroSection) {
      _bannerEl = _createBanner();
      heroSection.insertBefore(_bannerEl, heroSection.firstChild);
    }

    // 初回フェッチ & ポーリング開始
    _fetch();
    _timer = setInterval(_fetch, POLL_INTERVAL_MS);
  }

  function stop() {
    if (_timer) { clearInterval(_timer); _timer = null; }
  }

  function getLevel() { return _currentLevel; }

  return { init, stop, getLevel };
})();

document.addEventListener('DOMContentLoaded', () => CongestionWidget.init());
