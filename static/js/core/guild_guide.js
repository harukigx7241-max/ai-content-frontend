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
      '職人技の有料記事は「無料エリア」で読者の心を掴み、「有料エリア」で本当の価値を届ける設計が大切です。まずターゲットの悩みを具体的に書いてみましょう！',
      '見出しは工房の看板。「数字・結果・期間」を盛り込むと読まれる確率が変わります。タイトル生成ツールも試してみてください。',
      '購入者への特典を用意すると、満足度と口コミが大きく育ちます。プロンプト生成後は特典ツールも鍛えてみましょう！',
    ],
    cw: [
      '採用を勝ち取る提案文の最初の1行は「あなたの課題を解決できます」という視点から始めましょう。自己紹介より先に相手の関心を掴むのが職人の技です。',
      '受注者プロフィールは「実績 → 強み → 未来の約束」の順で鍛えると説得力が増します。工房で叩いてみましょう。',
      '単価交渉は実績という武器を積んでから。まず5〜10件で評判を積み上げ、そのあと自信を持って交渉を。',
    ],
    fortune: [
      '鑑定師としての個性が、選ばれる理由になります。他の占い師との差別化ポイントを工房で言語化してみましょう。',
      '鑑定師のSNS集客は「鑑定の世界観・雰囲気」を伝えることが肝心。実際の鑑定の空気感を少し見せると信頼が育ちます。',
      '鑑定書の品質が口コミという財産を生みます。工房でテンプレートをAIと共に鍛え、そこに自分の感性を吹き込むのがコツです。',
    ],
    sns: [
      'Xで反響を生む投稿は「悩み共感 → 解決への道筋 → 行動の一歩」の3段構成が基本。まずターゲットの悩みを深掘りして工房で鍛えましょう。',
      'Instagramは「ビジュアル × 保存したくなる知識」の組み合わせが鍵。キャプション工房でハッシュタグも一緒に鍛えましょう。',
      'Threadsはシリーズ投稿で専門家としての積み上げが効果的。同じテーマで複数の工房ログを連続して投稿してみましょう。',
    ],
    // 汎用ヒント
    generic: [
      'プロンプトを生成したら、AIに貼り付ける前に少し手を加えると精度がさらに上がります。職人の仕上げを忘れずに。',
      '気に入ったプロンプトは⭐ 保管庫に収めておきましょう。工房の名品はいつでも取り出せるようにしておくのが職人流です。',
      'プロンプトの出来に満足したら、ギルド広場の掲示板に投稿して仲間の参考にしましょう！',
    ],
    // ゲスト向け
    guest: [
      '見習い冒険者は1日3回まで工房を無料で使えます。ギルドに参加すると無制限で鍛え放題になります！',
      '気に入ったプロンプトを保管庫に収めたいですよね？ギルドに参加するとプロンプト保管庫が開放されます。',
    ],
  };

  // キャラクター名
  const GUIDE_NAME = '工房の親方';
  const GUIDE_ICON = '⚒️';

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
