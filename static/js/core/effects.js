/**
 * static/js/core/effects.js — サウンド & アニメーション効果システム
 *
 * 設計:
 *   - Web Audio API でトーン生成 (音声ファイル不要)
 *   - prefers-reduced-motion を尊重
 *   - 設定は localStorage に保存 (キー: pguild_effects)
 *
 * API:
 *   Effects.play(name)          — 効果音を再生 ('click'|'success'|'error'|'like'|'save'|'copy'|'level_up')
 *   Effects.ripple(el)          — 要素にリップル波紋アニメーション
 *   Effects.sfxEnabled()        — 効果音が有効か
 *   Effects.animEnabled()       — アニメーションが有効か
 *   Effects.setSfx(bool)        — 効果音設定を保存
 *   Effects.setAnim(bool)       — アニメーション設定を保存
 *   Effects.init()              — 初期化 (DOMContentLoaded 後に呼ぶ)
 */
const Effects = (() => {
  const STORAGE_KEY = 'pguild_effects';
  let _ctx = null;  // AudioContext (lazy init)

  /* ── 設定 I/O ─────────────────────────────────────────────────── */
  function _load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch {}
    return { sfx: true, anim: true };
  }

  function _save(s) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); } catch {}
  }

  function sfxEnabled() { return _load().sfx !== false; }

  function animEnabled() {
    // prefers-reduced-motion を最優先
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return false;
    return _load().anim !== false;
  }

  function setSfx(val) {
    const s = _load(); s.sfx = !!val; _save(s);
  }

  function setAnim(val) {
    const s = _load(); s.anim = !!val; _save(s);
  }

  /* ── Web Audio ────────────────────────────────────────────────── */
  function _getCtx() {
    if (!_ctx) {
      try {
        _ctx = new (window.AudioContext || window.webkitAudioContext)();
      } catch { return null; }
    }
    return _ctx;
  }

  /**
   * シンプルなトーン再生
   * @param {number[]} freqs  — 周波数配列 (順番に鳴らす)
   * @param {number}   dur    — 1音の長さ (秒)
   * @param {string}   type   — oscillator type ('sine'|'square'|'triangle')
   * @param {number}   gain   — 音量 0–1
   */
  function _tone(freqs, dur = 0.08, type = 'sine', gain = 0.12) {
    const ctx = _getCtx();
    if (!ctx) return;
    let t = ctx.currentTime;
    freqs.forEach(freq => {
      const osc = ctx.createOscillator();
      const g   = ctx.createGain();
      osc.connect(g);
      g.connect(ctx.destination);
      osc.type = type;
      osc.frequency.setValueAtTime(freq, t);
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(gain, t + 0.01);
      g.gain.linearRampToValueAtTime(0, t + dur);
      osc.start(t);
      osc.stop(t + dur + 0.02);
      t += dur * 0.85;
    });
  }

  /* ── サウンド定義 ─────────────────────────────────────────────── */
  const SOUNDS = {
    click:    () => _tone([440],              0.05, 'sine',     0.08),
    success:  () => _tone([523, 659, 784],    0.07, 'sine',     0.12),
    error:    () => _tone([330, 220],         0.10, 'square',   0.08),
    like:     () => _tone([523, 784],         0.07, 'sine',     0.11),
    save:     () => _tone([440, 660],         0.07, 'triangle', 0.10),
    copy:     () => _tone([660, 880],         0.06, 'sine',     0.10),
    level_up: () => _tone([523,659,784,1047], 0.09, 'sine',     0.14),
    post:     () => _tone([440, 554, 659],    0.08, 'sine',     0.11),
  };

  function play(name) {
    if (!sfxEnabled()) return;
    const fn = SOUNDS[name];
    if (fn) { try { fn(); } catch {} }
  }

  /* ── アニメーション ───────────────────────────────────────────── */
  /**
   * 要素にリップル波紋エフェクトを追加する。
   * position: relative / overflow: hidden が付いていない場合は自動付与。
   */
  function ripple(el) {
    if (!animEnabled() || !el) return;
    const r = document.createElement('span');
    const rect = el.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    r.style.cssText = [
      'position:absolute',
      'border-radius:50%',
      'background:rgba(168,85,247,0.3)',
      'pointer-events:none',
      `width:${size}px`,
      `height:${size}px`,
      `left:${(rect.width - size) / 2}px`,
      `top:${(rect.height - size) / 2}px`,
      'transform:scale(0)',
      'animation:pguild-ripple 0.5s ease-out forwards',
    ].join(';');
    // overflow hidden が必要
    const prevPos = getComputedStyle(el).position;
    if (prevPos === 'static') el.style.position = 'relative';
    el.style.overflow = 'hidden';
    el.appendChild(r);
    r.addEventListener('animationend', () => r.remove(), { once: true });
  }

  /* ── CSS keyframes 注入 (1回のみ) ───────────────────────────── */
  function _injectCSS() {
    if (document.getElementById('pguild-effects-style')) return;
    const s = document.createElement('style');
    s.id = 'pguild-effects-style';
    s.textContent = '@keyframes pguild-ripple{to{transform:scale(2.8);opacity:0}}';
    document.head.appendChild(s);
  }

  /* ── 初期化 ──────────────────────────────────────────────────── */
  function init() {
    _injectCSS();
    // AudioContext は最初のユーザーインタラクションで resume が必要な場合がある
    document.addEventListener('click', () => {
      if (_ctx && _ctx.state === 'suspended') _ctx.resume().catch(() => {});
    }, { once: true });
  }

  return { play, ripple, sfxEnabled, animEnabled, setSfx, setAnim, init };
})();

// 自動初期化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Effects.init());
} else {
  Effects.init();
}
