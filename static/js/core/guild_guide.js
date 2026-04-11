/**
 * static/js/core/guild_guide.js — ギルドガイドAIウィジェット
 *
 * 特徴:
 *   - LLM APIなし: スクリプトベースのコンテキスト対応ヒント
 *   - タブ切替に連動してキャラクターの台詞が変わる
 *   - ログイン状態・ゲスト残り回数に応じてメッセージが変わる
 *   - ユーザーがクリックして開閉できる
 *   - 閉じた状態は localStorage に保存 (セッション中は非表示)
 */
const GuildGuide = (() => {
  const STORAGE_KEY = 'pguild_guide_dismissed';

  // ── ヒントデータ ──────────────────────────────────────────────
  const TIPS = {
    // タブID → メッセージ配列 (ランダムで1つ選ぶ)
    note: [
      '有料記事は「無料エリア」で読者を引き込み、「有料エリア」で価値を届ける設計が重要です。まずターゲットの悩みを具体的に書いてみましょう！',
      'タイトルは記事の顔。「数字」「結果」「期間」を入れると売上が変わります。タイトル生成ツールも試してみてください。',
      '購入者特典を用意すると、満足度とリピート率が大きく上がります。プロンプト生成後は特典ツールも使ってみましょう！',
    ],
    cw: [
      '提案文の最初の1行で採用率が決まります。「私はできます」より「あなたの課題を解決できます」という視点で書きましょう。',
      'CWのプロフィールは「実績 → 強み → 未来の約束」の順で書くと説得力が増します。',
      '単価交渉は実績を積んでから。まず5〜10件で評価を集め、そのあと自信を持って交渉しましょう。',
    ],
    fortune: [
      'ココナラでは「鑑定スタイルの個性」が選ばれる理由になります。他との差別化ポイントを明確にしましょう。',
      '占い師のSNS集客は「鑑定結果の雰囲気」を伝えることが大切。実際の鑑定を少し見せると信頼感が上がります。',
      '鑑定書のクオリティが口コミを生みます。テンプレートをAIで生成し、そこに自分の感性を加えるのがコツです。',
    ],
    sns: [
      'Xで伸びる投稿は「悩み共感 → 解決策示唆 → 行動促進」の3段構成が基本。まずターゲットの悩みを深掘りしてみましょう。',
      'Instagramはキャプションよりも「ビジュアル × 保存したくなる情報」が鍵。ハッシュタグは30個全て活用しましょう。',
      'Threadsはシリーズ投稿で権威性を積み上げるのが効果的。同じテーマで複数投稿を続けましょう。',
    ],
    // 汎用ヒント
    generic: [
      'プロンプトを生成したら、AIに貼り付ける前に少しカスタマイズすると精度がさらに上がります。',
      '生成したプロンプトが気に入ったら⭐ 保存しておきましょう。あとでいつでも使えます。',
      'プロンプトの出来に満足したら、ギルド広場に投稿して仲間のヒントになりましょう！',
    ],
    // ゲスト向け
    guest: [
      'ゲストは1日3回まで無料で使えます。ギルドに参加すると無制限になります！',
      '気に入ったプロンプトは保存しておきたいですよね？ギルドに参加するとプロンプト保管庫が使えます。',
    ],
  };

  // キャラクター名
  const GUIDE_NAME = 'ギルドマスター';
  const GUIDE_ICON = '🧙';

  let _el = null;        // ウィジェット DOM要素
  let _currentTab = 'note';
  let _isOpen = true;

  /* ── DOM 構築 ────────────────────────────────────────────────── */
  function _build() {
    const el = document.createElement('div');
    el.id = 'guildGuide';
    el.className = 'guild-guide-widget';
    el.innerHTML = `
      <div class="gg-header" id="ggHeader">
        <span class="gg-avatar">${GUIDE_ICON}</span>
        <span class="gg-name">${GUIDE_NAME}</span>
        <button class="gg-toggle" id="ggToggle" aria-label="ガイドを閉じる">▾</button>
      </div>
      <div class="gg-body" id="ggBody">
        <p class="gg-text" id="ggText"></p>
        <div class="gg-footer">
          <button class="gg-next" id="ggNext">別のヒント ↻</button>
          <button class="gg-dismiss" id="ggDismiss">非表示</button>
        </div>
      </div>
    `;
    document.body.appendChild(el);
    _el = el;

    // イベント
    document.getElementById('ggToggle').addEventListener('click', _toggleOpen);
    document.getElementById('ggNext').addEventListener('click', _showNextTip);
    document.getElementById('ggDismiss').addEventListener('click', _dismiss);

    // タブ切替検知
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        if (tab) { _currentTab = tab; _showNextTip(); }
      });
    });

    _showNextTip();
  }

  /* ── ヒント表示 ──────────────────────────────────────────────── */
  let _tipIndices = {};  // タブ別の現在インデックス

  function _getTips() {
    // ゲストで残り回数少ない場合はゲスト向けヒント
    if (window.GuestUsage && !GuestUsage.isLoggedIn()) {
      const g = GuestUsage.checkLimit();
      if (!g.allowed || g.count >= g.max - 1) return TIPS.guest;
    }
    return TIPS[_currentTab] || TIPS.generic;
  }

  function _showNextTip() {
    const tips = _getTips();
    const idx = (_tipIndices[_currentTab] || 0) % tips.length;
    _tipIndices[_currentTab] = idx + 1;
    const textEl = document.getElementById('ggText');
    if (textEl) {
      textEl.style.opacity = '0';
      setTimeout(() => {
        textEl.textContent = tips[idx];
        textEl.style.opacity = '1';
      }, 150);
    }
  }

  /* ── 開閉 ────────────────────────────────────────────────────── */
  function _toggleOpen() {
    _isOpen = !_isOpen;
    const body   = document.getElementById('ggBody');
    const toggle = document.getElementById('ggToggle');
    if (body)   body.style.display   = _isOpen ? '' : 'none';
    if (toggle) toggle.textContent   = _isOpen ? '▾' : '▴';
  }

  function _dismiss() {
    if (_el) {
      _el.style.animation = 'gg-fadeout 0.3s ease forwards';
      setTimeout(() => { if (_el) _el.remove(); _el = null; }, 350);
    }
    try { sessionStorage.setItem(STORAGE_KEY, '1'); } catch {}
  }

  /* ── 初期化 ──────────────────────────────────────────────────── */
  function init() {
    // セッション中に非表示にされていたら表示しない
    try {
      if (sessionStorage.getItem(STORAGE_KEY)) return;
    } catch {}

    // モバイル幅では非表示 (幅 < 640px)
    if (window.innerWidth < 640) return;

    // DOMContentLoaded 後に少し遅延して表示
    setTimeout(_build, 1200);
  }

  return { init };
})();

// 自動初期化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => GuildGuide.init());
} else {
  GuildGuide.init();
}
