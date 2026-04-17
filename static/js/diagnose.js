/* ═══════════════════════════════════════════════════════════════════════
   diagnose.js — Phase 8 診断 Lite
   DiagnosePanel: プロンプト診断 + 日本語品質チェック
   将来 PromptDoctorService / LanguageQualityService API 版に差し替え可能な構造
   ═══════════════════════════════════════════════════════════════════════ */

const DiagnosePanel = (() => {
  /* ── Helpers ─────────────────────────────────────────────────────── */
  function escHtml(s) {
    return String(s || '')
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function scoreClass(score) {
    if (score >= 70) return 'score-high';
    if (score >= 40) return 'score-mid';
    return 'score-low';
  }

  /* ── Render helpers ──────────────────────────────────────────────── */

  function renderList(items, cssClass, label) {
    if (!items || items.length === 0) return '';
    return `
      <div class="diag-section-title ${cssClass}-title">${escHtml(label)}</div>
      <ul class="diag-list ${cssClass}-list">
        ${items.map(i => `<li>${escHtml(i)}</li>`).join('')}
      </ul>`;
  }

  function renderUpgradeBanner(upgradeHint) {
    if (!upgradeHint) return '';
    return `
      <div class="diag-upgrade-banner">
        <div class="diag-upgrade-icon">🚀</div>
        <div class="diag-upgrade-body">
          <div class="diag-upgrade-title">
            AI版で更に深く診断できます
            <span class="diag-upgrade-badge">準備中</span>
          </div>
          <div class="diag-upgrade-text">${escHtml(upgradeHint)}</div>
        </div>
      </div>`;
  }

  /* ── Prompt diagnosis renderer ───────────────────────────────────── */
  function renderPromptResult(data) {
    const cls = scoreClass(data.score);
    const stars = '★'.repeat(data.stars) + '☆'.repeat(5 - data.stars);
    const modeLabel = data.mode === 'api' ? 'AI版' : data.mode === 'lite' ? 'Lite版' : 'Liteルールベース';
    const issuesHtml = renderList(data.issues, 'issues', '⚠️ 改善が必要な点');
    const hintsHtml  = renderList(data.hints,  'hints',  '💡 改善ヒント');
    const strengthsHtml = renderList(data.strengths, 'strengths', '✅ 良い点');
    const noIssues = (!data.issues || data.issues.length === 0)
      ? '<div class="diag-empty-ok">🎉 目立った問題はありません！</div>' : '';

    return `
      <div class="diag-result">
        <div class="diag-score-row">
          <div class="diag-score-circle ${cls}">
            <span class="diag-score-num">${data.score}</span>
            <span class="diag-score-unit">/ 100</span>
          </div>
          <div class="diag-score-meta">
            <div class="diag-stars" title="${data.stars}スター">${stars}</div>
            <div style="font-size:0.75rem;color:rgba(255,255,255,0.4);margin-bottom:4px">${escHtml(modeLabel)}</div>
          </div>
        </div>
        <div class="diag-bar-wrap">
          <div class="diag-bar-fill ${cls}" style="width:${data.score}%"></div>
        </div>
        ${noIssues}
        ${issuesHtml}
        ${hintsHtml}
        ${strengthsHtml}
        ${renderUpgradeBanner(data.upgrade_hint)}
      </div>`;
  }

  /* ── Quality check renderer ──────────────────────────────────────── */
  function renderQualityResult(data) {
    const cls = scoreClass(data.score);
    const toneMap = {
      desu_masu: 'です・ます調',
      da_dearu:  'だ・である調',
      mixed:     '⚠️ 文体混在',
      unknown:   '文体不明',
    };
    const toneLabel = toneMap[data.tone] || data.tone;
    const grade = data.grade || 'C';
    const modeLabel = data.mode === 'api' ? 'AI版' : 'Liteルールベース';

    const issuesHtml      = renderList(data.issues,      'issues',      '⚠️ 問題点');
    const suggestionsHtml = renderList(data.suggestions, 'suggestions', '✏️ 改善提案');
    const noIssues = (!data.issues || data.issues.length === 0)
      ? '<div class="diag-empty-ok">🎉 日本語品質に目立った問題はありません！</div>' : '';

    return `
      <div class="diag-result">
        <div class="diag-score-row">
          <div class="diag-score-circle ${cls}">
            <span class="diag-score-num">${data.score}</span>
            <span class="diag-score-unit">/ 100</span>
          </div>
          <div class="diag-score-meta">
            <div style="margin-bottom:4px">
              <span class="diag-grade grade-${grade}">グレード ${grade}</span>
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
              <span class="diag-tone-badge">文体: ${escHtml(toneLabel)}</span>
              <span style="font-size:0.72rem;color:rgba(255,255,255,0.35)">${escHtml(modeLabel)}</span>
            </div>
          </div>
        </div>
        <div class="diag-bar-wrap">
          <div class="diag-bar-fill ${cls}" style="width:${data.score}%"></div>
        </div>
        ${noIssues}
        ${issuesHtml}
        ${suggestionsHtml}
        ${renderUpgradeBanner(data.upgrade_hint)}
      </div>`;
  }

  /* ── API calls (pluggable — replace endpoint to switch to AI tier) ── */

  async function runPromptDiagnosis(text) {
    const res = await fetch('/api/diagnose/prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  async function runQualityCheck(text) {
    const res = await fetch('/api/diagnose/quality', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  /* ── Mode badge fetch ────────────────────────────────────────────── */
  async function fetchModeAndUpdateBadge() {
    try {
      const res = await fetch('/api/diagnose/status');
      if (!res.ok) return;
      const d = await res.json();
      const badge = document.getElementById('diagModeBadge');
      if (!badge) return;
      const mode = d.prompt_doctor?.mode || 'free';
      badge.textContent = mode.toUpperCase();
      badge.className = `diag-mode-badge mode-${mode}`;
    } catch { /* ignore */ }
  }

  /* ── Tab switching ───────────────────────────────────────────────── */
  function initTabs() {
    document.querySelectorAll('.diag-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.diag-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.diag-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.panel)?.classList.add('active');
      });
    });
  }

  /* ── Char counters ───────────────────────────────────────────────── */
  function initCharCounters() {
    [
      ['diagPromptInput', 'diagPromptChars'],
      ['diagQualityInput', 'diagQualityChars'],
    ].forEach(([inputId, counterId]) => {
      const input = document.getElementById(inputId);
      const counter = document.getElementById(counterId);
      if (!input || !counter) return;
      input.addEventListener('input', () => {
        counter.textContent = input.value.length;
      });
    });
  }

  /* ── Prompt diagnosis button ─────────────────────────────────────── */
  function initPromptDiagnosis() {
    const btn = document.getElementById('diagPromptRunBtn');
    const input = document.getElementById('diagPromptInput');
    const resultEl = document.getElementById('diagPromptResult');
    if (!btn || !input || !resultEl) return;

    btn.addEventListener('click', async () => {
      const text = input.value.trim();
      if (!text) {
        resultEl.innerHTML = '<div style="color:#fca5a5;font-size:0.82rem;margin-top:12px">⚠️ テキストを入力してください</div>';
        return;
      }
      btn.disabled = true;
      resultEl.innerHTML = '<div class="diag-loading">診断中</div>';
      try {
        const data = await runPromptDiagnosis(text);
        if (data.available === false) {
          resultEl.innerHTML = `<div style="color:rgba(255,255,255,0.4);font-size:0.82rem;margin-top:12px">⚠️ ${escHtml(data.hint || '診断サービスは現在利用できません')}</div>`;
        } else {
          const content = data.content || data;
          resultEl.innerHTML = renderPromptResult(content);
        }
      } catch (e) {
        resultEl.innerHTML = `<div style="color:#fca5a5;font-size:0.82rem;margin-top:12px">⚠️ 診断に失敗しました: ${escHtml(e.message)}</div>`;
      } finally {
        btn.disabled = false;
      }
    });
  }

  /* ── Quality check button ────────────────────────────────────────── */
  function initQualityCheck() {
    const btn = document.getElementById('diagQualityRunBtn');
    const input = document.getElementById('diagQualityInput');
    const resultEl = document.getElementById('diagQualityResult');
    if (!btn || !input || !resultEl) return;

    btn.addEventListener('click', async () => {
      const text = input.value.trim();
      if (!text) {
        resultEl.innerHTML = '<div style="color:#fca5a5;font-size:0.82rem;margin-top:12px">⚠️ テキストを入力してください</div>';
        return;
      }
      btn.disabled = true;
      resultEl.innerHTML = '<div class="diag-loading">チェック中</div>';
      try {
        const data = await runQualityCheck(text);
        if (data.available === false) {
          resultEl.innerHTML = `<div style="color:rgba(255,255,255,0.4);font-size:0.82rem;margin-top:12px">⚠️ ${escHtml(data.hint || 'サービスは現在利用できません')}</div>`;
        } else {
          const content = data.content || data;
          resultEl.innerHTML = renderQualityResult(content);
        }
      } catch (e) {
        resultEl.innerHTML = `<div style="color:#fca5a5;font-size:0.82rem;margin-top:12px">⚠️ チェックに失敗しました: ${escHtml(e.message)}</div>`;
      } finally {
        btn.disabled = false;
      }
    });
  }

  /* ── Pre-fill from existing output (called by other modules) ─────── */
  function fillAndOpen(text, mode = 'prompt') {
    if (mode === 'quality') {
      const input = document.getElementById('diagQualityInput');
      if (input) { input.value = text; input.dispatchEvent(new Event('input')); }
      /* switch to quality tab */
      document.querySelectorAll('.diag-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.panel === 'diagQualityPanel');
      });
      document.querySelectorAll('.diag-panel').forEach(p => {
        p.classList.toggle('active', p.id === 'diagQualityPanel');
      });
    } else {
      const input = document.getElementById('diagPromptInput');
      if (input) { input.value = text; input.dispatchEvent(new Event('input')); }
    }
    if (window.openModal) openModal('diagnoseLiteModal');
    else {
      const m = document.getElementById('diagnoseLiteModal');
      if (m) m.classList.add('is-open');
    }
  }

  /* ── Init ────────────────────────────────────────────────────────── */
  function init() {
    document.getElementById('diagnoseLaunchBtn')?.addEventListener('click', () => {
      fetchModeAndUpdateBadge();
      if (window.openModal) openModal('diagnoseLiteModal');
      else document.getElementById('diagnoseLiteModal')?.classList.add('is-open');
    });

    initTabs();
    initCharCounters();
    initPromptDiagnosis();
    initQualityCheck();
  }

  return { init, fillAndOpen };
})();

document.addEventListener('DOMContentLoaded', () => DiagnosePanel.init());
