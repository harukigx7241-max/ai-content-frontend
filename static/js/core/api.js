'use strict';
/**
 * static/js/core/api.js
 * fetch ラッパー stub。
 * Phase 0 では app.js の fetch 呼び出しをそのまま使うため、このファイルは未使用。
 * TODO: Phase 1+ で認証ヘッダー付与・共通エラー処理・リトライを実装する。
 *
 * 使用例 (将来):
 *   const data = await Api.post('/api/note/article', payload);
 */

const Api = {
  /**
   * POST リクエストを送信し JSON を返す。
   * TODO: Phase 1 - Authorization ヘッダーを追加する
   * TODO: Phase 1 - 503 (メンテナンス) を共通でハンドルする
   */
  async post(endpoint, body) {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'unknown' }));
      throw Object.assign(new Error(err.message ?? 'API error'), { status: res.status, data: err });
    }
    return res.json();
  },

  /**
   * GET リクエストを送信し JSON を返す。
   * TODO: Phase 1 - キャッシュ制御ヘッダーを追加する
   */
  async get(endpoint) {
    const res = await fetch(endpoint, {
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'unknown' }));
      throw Object.assign(new Error(err.message ?? 'API error'), { status: res.status, data: err });
    }
    return res.json();
  },
};

// グローバルに公開（将来 app.js から参照可能）
window.Api = Api;
