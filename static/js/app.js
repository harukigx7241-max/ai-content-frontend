(function() {  
    'use strict';  
    const el = React.createElement;  
    const { useState, useEffect, Component, Fragment, useRef } = React;  
    
    // 汎用コンポーネントヘルパー
    const div = (pr, ...c) => el('div', pr, ...c);  
    const span = (pr, ...c) => el('span', pr, ...c);  
    const button = (pr, ...c) => el('button', pr, ...c);  
    const h1 = (pr, ...c) => el('h1', pr, ...c);
    const h2 = (pr, ...c) => el('h2', pr, ...c);
    const h3 = (pr, ...c) => el('h3', pr, ...c);
    const h4 = (pr, ...c) => el('h4', pr, ...c);
    const p = (pr, ...c) => el('p', pr, ...c);
    const ul = (pr, ...c) => el('ul', pr, ...c);
    const li = (pr, ...c) => el('li', pr, ...c);
    const label = (pr, ...c) => el('label', pr, ...c);
    const input = (pr, ...c) => el('input', pr, ...c);
    const textarea = (pr, ...c) => el('textarea', pr, ...c);
    const select = (pr, ...c) => el('select', pr, ...c);
    const option = (pr, ...c) => el('option', pr, ...c);
    const table = (pr, ...c) => el('table', pr, ...c);
    const thead = (pr, ...c) => el('thead', pr, ...c);
    const tbody = (pr, ...c) => el('tbody', pr, ...c);
    const tr = (pr, ...c) => el('tr', pr, ...c);
    const th = (pr, ...c) => el('th', pr, ...c);
    const td = (pr, ...c) => el('td', pr, ...c);
 
    const DB_KEY = 'AICP_v70_BYOK_DB';   
    const SESS_KEY = 'AICP_v70_Session';  
    const SYS_VERSION = 'v73.0.0 Ultimate SaaS Edition';  
 
    // ================================================================
    // データベース管理
    // ================================================================
    const AppDB = {  
      get: () => {  
        let db = null;  
        try { db = JSON.parse(localStorage.getItem(DB_KEY)); } catch (e) {}  
        if (!db) {  
          db = {   
            config: { adminU: 'admin', adminP: 'admin123', announcement: '', inviteCodes: {}, popupMessage: '', popupId: 0 },   
            errorLogs: [], sharedPrompts: {}, sharedTools: [], // ギャラリー用追加
            users: { 'admin': { nickname: '管理者', status: 'approved', credits: 99999, lastLogin: '', loginHistory: [], usage: { count: 0, tools: {}, apiCount: { openai: 0, anthropic: 0, google: 0 } }, perms: {}, settings: { aiModel: 'chatgpt_free', keys: {openai:'', anthropic:'', google:''}, theme: 'blue', tone: '丁寧で専門的', notifications: true, persona: '', knowledge: '', templateUrl: '' }, curProj: 'default', projects: { 'default': { name: '管理者領域', data: {} } }, usedInviteCode: '', readPopupId: 0, favoriteTools: [], myTools: [] } }   
          };  
          localStorage.setItem(DB_KEY, JSON.stringify(db));  
        }  
        Object.keys(db.users).forEach(u => {
            if(db.users[u].credits === undefined) db.users[u].credits = 100;
            if(!db.users[u].settings.templates) db.users[u].settings.templates = ['', '', ''];
            if(!db.users[u].settings.myCharas) db.users[u].settings.myCharas = [];
            if(!db.users[u].favoriteTools) db.users[u].favoriteTools = [];
            if(!db.users[u].myTools) db.users[u].myTools = [];
        });
        if(!db.sharedTools) db.sharedTools = [];
        return db;  
      },  
      save: (db) => { try { localStorage.setItem(DB_KEY, JSON.stringify(db)); } catch (e) {} }  
    };  
 
    // ================================================================
    // ユーティリティ関数群 (トリミング、CSV出力等 v73新機能統合)
    // ================================================================
    const getAIPrefix = (modelId, settings) => {  
      const isPaid = modelId && modelId.includes('paid');  
      let aiName = (modelId||'').includes('claude') ? 'Claude' : (modelId||'').includes('gemini') ? 'Gemini' : 'ChatGPT';
      let spec = isPaid
        ? '有料版(最上位モデル)です。最高の創造性を発揮してください。\n※【最重要】最新のトレンドや正確な事実確認が必要な場合は、必ず「Web検索（ブラウジング機能）」を使用して情報を取得してください。\nその際、海外の情報を直訳したり、検索結果をそのまま羅列するのではなく、必ず「日本の文化・市場・SNSの文脈」に合わせて解釈し、読者が直感的に理解できるわかりやすく魅力的な表現に変換した上で出力に反映させてください。'
        : '無料版です。簡潔かつ的確に要求を満たしてください。';
      let tone = settings && settings.tone ? '\n※出力のトーン・文体は「' + settings.tone + '」で統一してください。' : '';
      let personaText = settings && settings.persona ? '\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\n' + settings.persona + '\n' : '';
      let knowledgeText = settings && settings.knowledge ? '\n※【マイ・ナレッジ】以下の情報を前提知識として活用してください：\n' + settings.knowledge + '\n' : '';
      return `【システム指示：${aiName} ${spec}】\nあなたは世界トップクラスの専門家（AI）アシスタントです。${tone}${personaText}${knowledgeText}\n\n※AIとしての挨拶（承知しました、以下が作成した文章です等）や解説などは一切出力せず、純粋なコンテンツのテキストのみを直接出力すること。\n\n`;
    };  

    const getUserLevel = (count) => {
        if (count >= 50) return { name: '神', icon: '👑', color: 'text-yellow-400', border: 'border-yellow-400/50' };
        if (count >= 20) return { name: 'マスター', icon: '💎', color: 'text-purple-400', border: 'border-purple-400/50' };
        if (count >= 5) return { name: 'レギュラー', icon: '⭐', color: 'text-brand-light', border: 'border-brand-light/50' };
        return { name: 'ビギナー', icon: '🌱', color: 'text-slate-400', border: 'border-white/10' };
    };

    const trimAIResponse = (text) => {
        if(!text) return "";
        let cleaned = text.replace(/^(承知いたしました|承知しました|はい、|以下の通り).*?\n+/g, '');
        cleaned = cleaned.replace(/いかがでしょうか[。？]?.*$/g, '');
        return cleaned.trim();
    };

    const exportToCSV = (text, filename) => {
        let csvContent = "data:text/csv;charset=utf-8,\uFEFF";
        const lines = text.split('\n');
        lines.forEach(line => {
            if (line.includes('|')) {
                const row = line.split('|').map(cell => `"${cell.trim().replace(/"/g, '""')}"`).filter(c => c !== '""').join(',');
                if(row && !row.includes('---')) csvContent += row + "\r\n";
            }
        });
        if(csvContent === "data:text/csv;charset=utf-8,\uFEFF") csvContent += text;
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a"); link.setAttribute("href", encodedUri); link.setAttribute("download", filename + ".csv");
        document.body.appendChild(link); link.click(); document.body.removeChild(link);
    };

    const downloadText = (text, filename) => {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
        element.setAttribute('download', filename + '.txt');
        element.style.display = 'none';
        document.body.appendChild(element); element.click(); document.body.removeChild(element);
    };

    const renderMarkdown = (text) => {  
      if (!text) return { __html: '' };  
      let html = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');  
      html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');  
      html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>');  
      html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-black mt-6 mb-3 border-l-4 border-brand pl-2">$1</h2>');  
      html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-black mt-8 mb-4 border-b border-gray-200 pb-2">$1</h1>');  
      html = html.replace(/^\- (.*$)/gim, '<ul class="list-disc pl-5 mb-2"><li>$1</li></ul>');  
      html = html.replace(/\n/g, '<br/>');  
      return { __html: html };  
    };  

    const copyTextToClipboard = (text, isFreeUser) => {
        let final = text;
        if (isFreeUser) final += "\n\n--- Created by AICP Pro ---";
        const textArea = document.createElement("textarea");
        textArea.value = final;
        textArea.style.position = "fixed"; textArea.style.left = "-9999px";
        document.body.appendChild(textArea); textArea.focus(); textArea.select();
        try { document.execCommand('copy'); } catch (err) {}
        document.body.removeChild(textArea);
    };
 
    const LoadingCircle = () => div({ className: 'w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin' });
    const ErrorAlert = ({ msg }) => div({ className: 'p-4 bg-brand-danger/10 border border-brand-danger/30 rounded-xl text-brand-danger text-sm font-bold animate-in' }, '\u26A0\uFE0F エラー: ' + msg);

    // ================================================================
    // FormInput コンポーネント (音声入力・魔法の杖対応)
    // ================================================================
    const FormInput = ({ f, val, onChange, onMagic, isMagicLoading }) => {  
      const isMainMagic = f.isMainMagic;  
      const value = val !== undefined ? val : (f.t === 'check' ? false : (f.opts ? f.opts[0] : ''));  
      const hasSpeech = window.SpeechRecognition || window.webkitSpeechRecognition;
      const [isListening, setIsListening] = useState(false);

      const startSpeech = () => {
          const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
          if (!SpeechRecognition) return;
          const recognition = new SpeechRecognition();
          recognition.lang = 'ja-JP';
          recognition.onstart = () => setIsListening(true);
          recognition.onend = () => setIsListening(false);
          recognition.onresult = (event) => {
              const text = event.results[0][0].transcript;
              onChange(f.id, (value ? value + '\n' + text : text));
          };
          recognition.start();
      };

      const SpeechBtn = () => hasSpeech && button({ 
          onClick: startSpeech, title: '音声入力',
          className: 'absolute right-2 bottom-2 p-2 rounded-full transition ' + (isListening ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-white/5 text-slate-400 hover:text-brand hover:bg-brand/10')
      }, '\uD83C\uDFA4');
 
      const inputEl = () => {  
        if (f.t === 'text') return div({className:'relative w-full'}, el('input', { className: 'input-base pr-10', value, placeholder: f.ph||'', onChange: e => onChange(f.id, e.target.value) }), el(SpeechBtn));  
        if (f.t === 'area') return div({className:'relative w-full h-full'}, el('textarea', { className: 'input-base min-h-[100px] resize-y text-sm pb-10', value, placeholder: f.ph||'', onChange: e => onChange(f.id, e.target.value) }), el(SpeechBtn));  
        if (f.t === 'select') return el('select', { className: 'input-base text-sm', value, onChange: e => onChange(f.id, e.target.value) }, f.opts.map(o => el('option', { key: o, value: o, className: 'bg-bg-panel' }, o)));  
        if (f.t === 'check') return el('label', { className: 'flex items-center gap-3 cursor-pointer p-2' },   
          div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition' }, div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (value ? 'bg-brand left-5' : 'bg-gray-400') })),  
          el('input', { type: 'checkbox', className: 'hidden', checked: !!value, onChange: e => onChange(f.id, e.target.checked) }),  
          span({ className: 'text-sm font-bold text-slate-300' }, '機能を有効にする')  
        );  
        if (f.t === 'image') return div({ className: 'mt-2' },
            el('input', { type: 'file', accept: 'image/*', className: 'text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-brand/20 file:text-brand hover:file:bg-brand/30 cursor-pointer transition',
                onChange: e => { const file = e.target.files[0]; if(file) { const reader = new FileReader(); reader.onload = ev => onChange(f.id, ev.target.result.split(',')[1]); reader.readAsDataURL(file); } }
            }), value ? span({className: 'ml-3 text-xs text-brand-success font-bold'}, '\u2713 画像セット済') : null
        );
        return null;  
      };  
 
      return div({ className: 'mb-6 animate-in relative' },  
        isMagicLoading && isMainMagic && div({ className: 'absolute inset-0 bg-black/60 z-10 rounded-2xl flex items-center justify-center backdrop-blur-sm' }, el(LoadingCircle)),
        div({ className: 'flex justify-between items-center mb-2 gap-2' },  
          span({ className: 'text-xs font-black text-slate-400 tracking-wider' }, f.l),  
          isMainMagic && button({ onClick: () => onMagic(f.id), disabled: isMagicLoading, className: 'bg-gradient-to-r from-brand-accent to-red-500 text-white text-[10px] font-black px-3 py-1 rounded-full shadow-lg hover:brightness-110 transition disabled:opacity-50' }, '\u2728 魔法で入力')
        ),  
        inputEl()  
      );  
    };  
 
    // ================================================================
    // UserSettingModal (UI大改修・4タブ化・初心者最適化・ペルソナ抽出)
    // ================================================================
    const UserSettingModal = ({ user, onClose }) => {
        const [db, setDb] = useState(AppDB.get());
        const uData = db.users[user];
        const [tab, setTab] = useState('account'); // account, ai, theme, advanced, data
        
        const [keys, setKeys] = useState(uData.settings.keys || {});
        const [aiModel, setAiModel] = useState(uData.settings.aiModel);
        const [theme, setTheme] = useState(uData.settings.theme);
        const [tone, setTone] = useState(uData.settings.tone);
        const [persona, setPersona] = useState(uData.settings.persona || '');
        const [knowledge, setKnowledge] = useState(uData.settings.knowledge || '');
        const [templateUrl, setTemplateUrl] = useState(uData.settings.templateUrl || '');
        const [notif, setNotif] = useState(uData.settings.notifications);
        const [templates, setTemplates] = useState(uData.settings.templates || ['','','']);
        const [myCharas, setMyCharas] = useState(uData.settings.myCharas || []);
        
        const [reqNickname, setReqNickname] = useState(uData.changeRequest ? uData.changeRequest.nickname : uData.nickname);
        const [reqSns, setReqSns] = useState(uData.changeRequest ? uData.changeRequest.sns : (uData.sns || ''));
        const [showReqForm, setShowReqForm] = useState(false);

        const [currentPass, setCurrentPass] = useState('');
        const [newPass, setNewPass] = useState('');
        const [newPassConfirm, setNewPassConfirm] = useState('');

        const [toast, setToast] = useState('');
        const [showPersonaExtractor, setShowPersonaExtractor] = useState(false);
        const [personaSource, setPersonaSource] = useState('');
        const [isExtracting, setIsExtracting] = useState(false);

        const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

        const save = () => {
            const ndb = AppDB.get();
            ndb.users[user].settings = Object.assign({}, ndb.users[user].settings, { keys, aiModel, theme, tone, persona, knowledge, templateUrl, notifications: notif, templates, myCharas });
            AppDB.save(ndb); onClose(); window.location.reload(); 
        };

        const handleExport = () => {
            const blob = new Blob([JSON.stringify(uData, null, 2)], {type: "application/json"});
            const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url;
            a.download = 'aicp_mydata_' + new Date().toISOString().slice(0,10) + '.json'; a.click(); URL.revokeObjectURL(url);
            showToast('個人データをダウンロードしました');
        };

        const handleImport = (e) => {
            const file = e.target.files[0]; if(!file) return;
            const reader = new FileReader();
            reader.onload = (ev) => {
                try { 
                    const imported = JSON.parse(ev.target.result);
                    if (imported && imported.settings) {
                        const ndb = AppDB.get(); ndb.users[user] = Object.assign({}, ndb.users[user], imported); AppDB.save(ndb);
                        showToast('データを復元しました。再読み込みします...'); setTimeout(() => window.location.reload(), 1500);
                    } else { alert('無効なデータファイルです。'); }
                } catch(err) { alert('読み込み失敗'); }
            };
            reader.readAsText(file);
        };

        const handleDeleteReq = () => {
            if(confirm('本当に退会（データ削除）を申請しますか？')) {
                const ndb = AppDB.get(); ndb.users[user].status = 'delete_requested'; AppDB.save(ndb);
                alert('退会申請を受け付けました。ログアウトします。'); localStorage.removeItem(SESS_KEY); window.location.reload();
            }
        };
        
        const extractPersona = async () => {
            if(!personaSource) return alert('文章を入力してください');
            setIsExtracting(true);
            let tried = []; let lastError = ''; let meaningfulError = ''; let order = ['openai', 'google', 'anthropic']; let success = false;
            for (let provider of order) {
                let ai_model = provider === 'anthropic' ? 'claude_free' : provider === 'google' ? 'gemini_free' : 'chatgpt_free';
                try {
                    const res = await fetch('/api/auto_generate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ prompt: '以下の文章を分析し、筆者の「職業、専門性、性格、文章のクセ」を詳細に抽出し、AIに憑依させるためのプロンプト（マイ・ペルソナ設定）を作成してください。出力はテキストのみにしてください。\n\n' + personaSource, user_api_key: keys[provider], ai_model: ai_model }) });
                    const data = await res.json();
                    if(data.status === 'success') {
                        setPersona(data.result); setPersonaSource(''); setShowPersonaExtractor(false);
                        const ndb = AppDB.get(); if(!ndb.users[user].usage.apiCount) ndb.users[user].usage.apiCount = { openai: 0, anthropic: 0, google: 0 };
                        ndb.users[user].usage.apiCount[provider] = (ndb.users[user].usage.apiCount[provider] || 0) + 1; AppDB.save(ndb);
                        showToast(tried.length > 0 ? '\uD83D\uDCA1 ' + provider.toUpperCase() + 'で抽出しました！' : '\u2728 自動抽出しました！');
                        success = true; break;
                    } else {
                        lastError = data.message;
                        if (!data.message.includes('設定されていません') && !meaningfulError) meaningfulError = '[' + provider.toUpperCase() + '] ' + data.message;
                        tried.push(provider);
                        if (data.message.includes('設定されていません') || data.message.includes('quota') || data.message.includes('429')) {
                            if (tried.length < order.length) showToast('\u26A0\uFE0F ' + provider.toUpperCase() + 'エラー。別AIで再試行...');
                            continue;
                        } else { break; }
                    }
                } catch(e) { lastError = '通信エラー'; tried.push(provider); }
            }
            if(!success) alert('抽出エラー: \n' + (meaningfulError || 'APIキーを確認してください。'));
            setIsExtracting(false);
        };

        const keyInput = (lang, provider, ph) => div({ className: 'mb-4' },
            label({ className: 'block text-xs font-bold text-slate-400 mb-1.5' }, lang + ' APIキー (' + provider + ')'),
            el('input', { type: 'password', className: 'input-base !py-2.5 text-sm font-mono', placeholder: ph, value: keys[provider]||'', onChange: e => setKeys(Object.assign({}, keys, { [provider]: e.target.value })) })
        );

        return div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4 animate-in' },
            toast && div({ className: 'fixed top-8 left-1/2 transform -translate-x-1/2 bg-brand text-white px-6 py-3 rounded-full shadow-2xl z-[999] font-bold text-sm animate-in' }, toast),
            div({ className: 'glass-panel rounded-3xl max-w-2xl w-full p-6 md:p-8 relative flex flex-col max-h-[90vh]' },
                button({ onClick: onClose, className: 'absolute top-5 right-5 text-slate-400 hover:text-white text-xl font-bold transition' }, '\u2715'),
                div({className: 'flex justify-between items-center mb-6 pb-4 border-b border-white/10'},
                    h3({ className: 'text-xl font-black text-white' }, '\u2699\uFE0F 個人設定'),
                    div({className:'text-right hidden sm:block'}, span({className:'text-[10px] text-brand-light'}, '現在のランク: '), span({className:'text-sm font-bold text-white'}, getUserLevel(uData.usage.count||0).name), span({className:'text-[10px] text-brand-light ml-3'}, '残クレジット: '), span({className:'text-sm font-bold text-white'}, uData.credits))
                ),
                
                div({ className: 'flex gap-2 mb-6 border-b border-white/10 pb-2 overflow-x-auto hide-scrollbar' },
                    ['account', 'ai', 'ui', 'advanced', 'data'].map(t => button({ key: t, onClick: () => setTab(t), className: 'px-4 py-2 rounded-full text-xs font-bold transition whitespace-nowrap ' + (tab === t ? 'bg-brand text-white' : 'text-slate-400 hover:bg-white/10') }, 
                        t === 'account' ? '\uD83D\uDC64 アカウント' :
                        t === 'ai' ? '\uD83E\uDDE0 AIカスタマイズ' : 
                        t === 'ui' ? '\uD83C\uDFA8 見た目・テーマ' : 
                        t === 'advanced' ? '\u2699\uFE0F 高度な設定(API)' : '\uD83D\uDCBE データ管理'))
                ),

                div({ className: 'overflow-y-auto flex-1 pr-3 hide-scrollbar space-y-6' },
                    tab === 'account' && div({ className: 'animate-in space-y-6' },
                        div({ className: 'flex gap-4 p-4 bg-brand/10 rounded-xl border border-brand/20' },
                            div({ className: 'flex-1' }, p({ className: 'text-xs text-brand mb-1 font-bold' }, '\uD83E\uDE99 残りクレジット'), p({ className: 'text-2xl font-black text-white' }, uData.credits)),
                            div({ className: 'flex-1' }, p({ className: 'text-xs text-brand mb-1 font-bold' }, '\uD83D\uDCC8 総生成回数'), p({ className: 'text-2xl font-black text-white' }, uData.usage.count || 0))
                        ),
                        div({ className: 'p-5 bg-white/5 rounded-2xl' },
                            h4({ className: 'text-sm font-bold text-white mb-2' }, 'プロフィール・SNS情報'),
                            p({ className: 'text-xs text-slate-400 mb-3' }, '※変更は管理者の承認が必要です'),
                            input({ className: 'input-base !py-2 text-sm mb-2', placeholder: '新アカウント名', value: reqNickname, onChange: e => setReqNickname(e.target.value) }),
                            input({ className: 'input-base !py-2 text-sm mb-3', placeholder: '新SNS', value: reqSns, onChange: e => setReqSns(e.target.value) }),
                            button({ onClick: () => {
                                const ndb = AppDB.get(); ndb.users[user].changeRequest = { nickname: reqNickname, sns: reqSns };
                                AppDB.save(ndb); setDb(ndb); showToast('変更申請を送信しました。');
                            }, className: 'w-full btn-gradient py-2 rounded-lg text-sm' }, '変更を申請')
                        ),
                        div({ className: 'p-5 bg-white/5 rounded-2xl' },
                            h4({ className: 'text-sm font-bold text-white mb-3' }, '\uD83D\uDD12 パスワード再設定'),
                            input({ type: 'password', className: 'input-base !py-2 text-sm mb-2', placeholder: '現在のパスワード', value: currentPass, onChange: e => setCurrentPass(e.target.value) }),
                            input({ type: 'password', className: 'input-base !py-2 text-sm mb-2', placeholder: '新パスワード', value: newPass, onChange: e => setNewPass(e.target.value) }),
                            input({ type: 'password', className: 'input-base !py-2 text-sm mb-3', placeholder: '新パスワード(確認)', value: newPassConfirm, onChange: e => setNewPassConfirm(e.target.value) }),
                            button({ onClick: () => {
                                if(currentPass !== uData.password) return alert('現在のパスワードが違います');
                                if(newPass.length < 6 || newPass !== newPassConfirm) return alert('パスワードが無効です');
                                const ndb = AppDB.get(); ndb.users[user].password = newPass; AppDB.save(ndb); setDb(ndb);
                                setCurrentPass(''); setNewPass(''); setNewPassConfirm(''); showToast('パスワードを更新しました');
                            }, className: 'w-full glass-panel py-2 rounded-lg text-sm hover:bg-white/10' }, 'パスワード変更')
                        ),
                        div({ className: 'p-5 bg-white/5 rounded-2xl' }, p({ className: 'text-xs text-slate-400 mb-2' }, 'あなたの招待コード:'), p({ className: 'text-lg font-mono text-white' }, uData.inviteCode||'未発行')),
                        button({ onClick: handleDeleteReq, className: 'w-full bg-brand-danger/20 text-brand-danger py-3 rounded-xl text-sm font-bold hover:bg-brand-danger/30' }, '\uD83D\uDEAA 退会（全データ削除）申請')
                    ),
                    tab === 'ai' && div({ className: 'animate-in space-y-6' },
                        div({ className: 'pt-2' }, 
                            label({ className: 'block text-xs font-bold text-slate-400 mb-2 flex justify-between items-center' }, 
                                span({}, '\uD83D\uDC64 マイ・ペルソナ（自分専用AI化）', span({className:'ml-2 text-[9px] bg-white/10 px-1 rounded cursor-help', title:'この内容が全てのツールで裏側で適用されます'}, '❔')),
                                button({ onClick: () => setShowPersonaExtractor(!showPersonaExtractor), className: 'text-brand hover:text-brand-light flex items-center gap-1' }, '\u2728 自動抽出ツール')
                            ),
                            showPersonaExtractor && div({ className: 'mb-4 p-4 bg-brand/10 border border-brand/20 rounded-xl animate-in' },
                                textarea({ className: 'input-base min-h-[100px] text-xs mb-2', placeholder: '過去に書いたブログや日記、ツイートなどをここに貼り付けてください...', value: personaSource, onChange: e => setPersonaSource(e.target.value) }),
                                button({ onClick: extractPersona, disabled: isExtracting, className: 'w-full btn-gradient py-2 rounded-lg text-xs font-bold' }, isExtracting ? '抽出中...' : '文章からペルソナを自動抽出')
                            ),
                            textarea({ className: 'input-base min-h-[120px] text-xs', placeholder: '例: 私はプロのWebマーケターです。実績は〇〇で、文章は論理的かつ情熱的に書きます。', value: persona, onChange: e => setPersona(e.target.value) })
                        ),
                        div({}, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83D\uDCDA マイ・ナレッジ（前提知識・RAG）', span({className:'ml-2 text-[9px] bg-white/10 px-1 rounded cursor-help', title:'自社商品の仕様や専門用語を登録しておくと、AIがそれを元に記事を作成します'}, '❔')),
                            textarea({ className: 'input-base min-h-[150px] text-xs leading-relaxed', placeholder: '例: 弊社の主力商品は「魔法の美容液」です。特徴は無添加・オーガニックであることです。', value: knowledge, onChange: e => setKnowledge(e.target.value) })
                        ),
                        div({ className: 'pt-6 border-t border-white/10' }, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83C\uDFAD マイキャラ保存 (最大5体)'),
                            myCharas.map((ch, ci) => div({ key: ci, className: 'mb-3 p-3 bg-white/5 border border-white/10 rounded-xl animate-in' },
                                div({ className: 'flex items-center justify-between mb-2' },
                                    span({ className: 'text-xs font-bold text-brand-light' }, 'キャラ ' + (ci+1)),
                                    button({ onClick: () => { const nc = myCharas.filter((_, i) => i !== ci); setMyCharas(nc); }, className: 'text-[10px] text-brand-danger' }, '削除')
                                ),
                                input({ className: 'input-base !py-1.5 text-xs mb-1.5', placeholder: 'キャラ名', value: ch.name || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { name: e.target.value }); setMyCharas(nc); } }),
                                textarea({ className: 'input-base min-h-[60px] text-xs', placeholder: '性格・口調', value: ch.desc || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { desc: e.target.value }); setMyCharas(nc); } })
                            )),
                            myCharas.length < 5 && button({ onClick: () => setMyCharas(myCharas.concat([{ name: '', desc: '' }])), className: 'w-full glass-panel py-2 rounded-xl text-xs font-bold hover:bg-brand/10' }, '+ 新しいキャラを追加')
                        )
                    ),
                    tab === 'ui' && div({ className: 'animate-in space-y-6' },
                        div({}, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83C\uDFA8 UIテーマ'),
                            select({ className: 'input-base !py-2.5 text-sm', value: theme, onChange: e => setTheme(e.target.value) },
                                option({ value: 'blue' }, '🌑 ダークブルー'), option({ value: 'purple' }, '🌑 ダークパープル'), option({ value: 'emerald' }, '🌑 ダークエメラルド'), option({ value: 'light' }, '☀️ ライトモード（白背景）')
                            )
                        ),
                        div({}, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83D\uDDE3\uFE0F デフォルト出力トーン'),
                            el('select', { className: 'input-base !py-2.5 text-sm', value: tone, onChange: e => setTone(e.target.value) }, option({ value: '丁寧で専門的' }, '丁寧で専門的'), option({ value: '親しみやすいタメ口' }, '親しみやすいタメ口'), option({ value: '情熱的でセールス寄り' }, '情熱的でセールス寄り'), option({ value: '論理的で簡潔' }, '論理的で簡潔'))
                        ),
                        label({ className: 'flex items-center gap-3 cursor-pointer p-3 bg-white/5 rounded-xl' },   
                            div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition shrink-0' }, div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (notif ? 'bg-brand left-5' : 'bg-gray-400') })),  
                            el('input', { type: 'checkbox', className: 'hidden', checked: notif, onChange: e => setNotif(e.target.checked) }),  
                            span({ className: 'text-sm font-bold text-slate-300' }, '\uD83D\uDD14 ポップアップ通知を有効にする')  
                        )
                    ),
                    tab === 'advanced' && div({ className: 'animate-in' },
                        div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl leading-relaxed text-slate-300' },
                            p({ className: 'text-xs font-bold text-brand-light mb-2' }, '\u26A0\uFE0F 自身のAPIキー登録 (任意)'),
                            p({ className: 'text-[10px] mb-1' }, '※APIキーを登録すると、クレジットを消費せずに生成可能になります。初心者の方は未設定のままでもシステム側のキーで動作します。')
                        ),
                        div({ className: 'flex gap-2 mb-6' },
                            div({ className: 'flex-1 glass-panel p-3 rounded-xl text-center border-white/5' }, p({ className: 'text-[10px] text-slate-400' }, 'ChatGPT'), p({ className: 'text-lg font-bold' }, (uData.usage.apiCount?.openai||0) + '回')),
                            div({ className: 'flex-1 glass-panel p-3 rounded-xl text-center border-white/5' }, p({ className: 'text-[10px] text-slate-400' }, 'Gemini'), p({ className: 'text-lg font-bold' }, (uData.usage.apiCount?.google||0) + '回')),
                            div({ className: 'flex-1 glass-panel p-3 rounded-xl text-center border-white/5' }, p({ className: 'text-[10px] text-slate-400' }, 'Claude'), p({ className: 'text-lg font-bold' }, (uData.usage.apiCount?.anthropic||0) + '回'))
                        ),
                        keyInput('ChatGPT', 'openai', 'sk-...'), keyInput('Claude', 'anthropic', 'sk-ant-...'), keyInput('Gemini', 'google', 'AIza...'),
                        div({ className: 'mt-6 pt-6 border-t border-white/10' },
                            label({ className: 'block text-xs font-bold text-slate-400 mb-1.5' }, '\uD83E\uDD16 デフォルトAIモデル'),
                            el('select', { className: 'input-base !py-2.5 text-sm', value: aiModel, onChange: e => setAiModel(e.target.value) },
                                option({ value: 'chatgpt_free' }, 'ChatGPT (無料版)'), option({ value: 'chatgpt_paid' }, 'ChatGPT Plus (有料版)'),
                                option({ value: 'claude_free' }, 'Claude 3 (無料版)'), option({ value: 'claude_paid' }, 'Claude 3 Pro (有料版)'),
                                option({ value: 'gemini_free' }, 'Gemini (無料版)'), option({ value: 'gemini_paid' }, 'Gemini Advanced (有料版)')
                            )
                        )
                    ),
                    tab === 'data' && div({ className: 'animate-in space-y-6' },
                        div({ className: 'p-5 bg-white/5 rounded-2xl flex flex-col gap-3' },
                            h4({ className: 'text-sm font-bold text-white mb-2' }, '\uD83D\uDCBE データ管理'),
                            button({ onClick: handleExport, className: 'glass-panel py-3 rounded-xl text-sm hover:bg-white/10' }, '\uD83D\uDCE5 データDL'),
                            div({ className: 'relative w-full' }, button({ className: 'w-full glass-panel py-3 rounded-xl text-sm hover:bg-white/10' }, '\uD83D\uDCE4 データ復元'), input({ type: 'file', accept: '.json', onChange: handleImport, className: 'absolute inset-0 w-full h-full opacity-0 cursor-pointer' }))
                        ),
                        div({ className: 'p-5 bg-white/5 rounded-2xl flex flex-col gap-3' },
                            button({ onClick: () => { if(confirm('キャッシュをクリアしますか？')){ const ndb=AppDB.get();ndb.users[user].projects[uData.curProj].data={};AppDB.save(ndb);window.location.reload(); } }, className: 'glass-panel py-3 rounded-xl text-sm text-brand-accent hover:bg-brand-accent/20' }, '\uD83E\uDDF9 キャッシュクリア')
                        )
                    )
                ),
                button({ onClick: save, className: 'w-full btn-gradient py-4 rounded-xl font-black mt-6 shadow-xl' }, '設定を保存して閉じる')
            )
        );
    };

    // ================================================================
    // ToolCore - メインツール実行コンポーネント (モバイルタブ・履歴・丸投げ対応)
    // ================================================================
    const ToolCore = ({ tid, user, role, onBack, onUpdateUser, customTools }) => {  
      const isCustom = tid.startsWith('my_');
      const conf = isCustom ? customTools.find(t=>t.id===tid) : window.AICP_TOOLS[tid];
      if(!conf) return null;

      const [db, setDb] = useState(AppDB.get());  
      const uData = db.users[user];  
      const userKeys = uData.settings.keys || {};
      const [vals, setVals] = useState(uData.projects[uData.curProj].data[tid] || {});  
      const [copied, setCopied] = useState({});  
      const [res, setRes] = useState((uData.projects[uData.curProj].data[tid] && uData.projects[uData.curProj].data[tid].res) || '');  
      const [error, setError] = useState('');
      const [isLoading, setIsLoading] = useState(false);
      const [isMagicLoading, setIsMagicLoading] = useState(false);
      const [aiModel, setAiModel] = useState(uData.settings.aiModel);
      const [imageAI, setImageAI] = useState('openai');
      const [toast, setToast] = useState('');
      const [genMode, setGenMode] = useState('api');
      const [promptAiModel, setPromptAiModel] = useState('chatgpt_paid');
      const [shareCode, setShareCode] = useState('');
      const [loadCode, setLoadCode] = useState('');
      const [abTest, setAbTest] = useState(false);
      const [manualInput, setManualInput] = useState('');
      const [previewTab, setPreviewTab] = useState('all'); 
      const [previewMode, setPreviewMode] = useState(window.innerWidth < 768 ? 'mobile' : 'pc'); 
      const [showPasteModal, setShowPasteModal] = useState(false);
      const [magicAI, setMagicAI] = useState('openai');
      const [mobileTab, setMobileTab] = useState('input');
      
      const [trends, setTrends] = useState([]);
      const [trendOpen, setTrendOpen] = useState(false);
      const [urlInput, setUrlInput] = useState('');
      const [keywordInput, setKeywordInput] = useState('');
      const [showAdvancedMagic, setShowAdvancedMagic] = useState(false);
      const [brainstormIdeas, setBrainstormIdeas] = useState([]);
      const [showHelp, setShowHelp] = useState(false);
      
      const [webTemplates, setWebTemplates] = useState([]);
      const [isLoadingWebTemplates, setIsLoadingWebTemplates] = useState(false);
      const [alerts, setAlerts] = useState([]);
      
      const fetchWebTemplates = async () => {
          const templateUrl = uData.settings.templateUrl;
          if (!templateUrl) return;
          setIsLoadingWebTemplates(true);
          try {
              const response = await fetch(templateUrl);
              const data = await response.json();
              setWebTemplates(Array.isArray(data) ? data : []);
          } catch(e) {}
          setIsLoadingWebTemplates(false);
      };

      useEffect(() => { 
          const left = document.getElementById('tool-left-panel'); if (left) left.scrollTop = 0;
          const right = document.getElementById('tool-right-panel'); if (right) right.scrollTop = 0;
          fetch('/api/trends').then(r=>r.json()).then(d => { if(d.status === 'success') setTrends(d.data); }).catch(e=>{});
          if(tid === 'note') fetchWebTemplates();
      }, [tid]);

      const showToast = (msg) => { if(!uData.settings.notifications) return; setToast(msg); setTimeout(() => setToast(''), 4000); };
 
      const updateRes = (v) => {  
        setRes(v);  
        if (role !== 'admin') {  
          const ndb = AppDB.get();  
          if (!ndb.users[user].projects[uData.curProj].data[tid]) ndb.users[user].projects[uData.curProj].data[tid] = {};  
          ndb.users[user].projects[uData.curProj].data[tid].res = v;  
          AppDB.save(ndb);  
        }  
      };  

      const fetchWithFallback = async (endpoint, basePayload, defaultProvider, fallbackProviders) => {
          let tried = []; let lastError = ''; let meaningfulError = ''; 
          const allProviders = ['openai', 'google', 'anthropic'];
          let order = [defaultProvider].concat(allProviders.filter(p => p !== defaultProvider));

          for (let provider of order) {
              let payload = Object.assign({}, basePayload);
              if (endpoint === '/api/auto_generate') {
                  let model = provider === 'anthropic' ? 'claude_free' : provider === 'google' ? 'gemini_free' : 'chatgpt_free';
                  if (basePayload.ai_model && basePayload.ai_model.includes('paid')) model = model.replace('free', 'paid');
                  payload.ai_model = model; payload.user_api_key = userKeys[provider];
              } else if (endpoint === '/api/magic_generate') {
                  payload.prompt_instruction = provider; payload.user_keys = { [provider]: userKeys[provider] };
              }
              try {
                  const res = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
                  const data = await res.json();
                  if (data.status === 'success') return { success: true, data: data, provider: provider, tried: tried.length };
                  let msg = data.message;
                  if (msg.includes('insufficient_quota') || msg.includes('429')) msg = 'API上限に達しました。';
                  if (!data.message.includes('設定されていません') && !meaningfulError) meaningfulError = '[' + provider.toUpperCase() + '] ' + msg;
                  lastError = msg; tried.push(provider);
                  if (data.message.includes('設定されていません') || data.message.includes('insufficient_quota') || data.message.includes('429') || data.message.includes('エラー')) {
                      if (tried.length < order.length) showToast('\u26A0\uFE0F ' + provider.toUpperCase() + 'でエラー。自動切り替え中...');
                      continue; 
                  } else { break; }
              } catch (e) { lastError = '通信エラー'; if (!meaningfulError) meaningfulError = '[' + provider.toUpperCase() + '] ' + lastError; tried.push(provider); }
          }
          return { success: false, error: meaningfulError || '[' + defaultProvider.toUpperCase() + '] APIエラー: ' + lastError };
      };
 
      const handleMagic = async (fid, extraParams) => {  
        if (role !== 'admin' && uData.credits <= 0) { setError('クレジット不足です。'); return; }
        setIsMagicLoading(true); setError('');
        const reqFields = conf.fields.map(f => ({ id: f.id, l: f.l, ph: f.ph||'', val: vals[f.id]||'' }));
        let basePayload = { tool_id: tid, fields: reqFields, target_fid: fid, url: (extraParams && extraParams.url) || urlInput || '', keyword: (extraParams && extraParams.keyword) || null };
        const result = await fetchWithFallback('/api/magic_generate', basePayload, magicAI, ['openai', 'google', 'anthropic']);

        if (result.success) {
            const ndb = AppDB.get();
            if (role !== 'admin') { ndb.users[user].credits = Math.max(0, (ndb.users[user].credits || 0) - 1); }
            ndb.users[user].usage.count = (ndb.users[user].usage.count || 0) + 1;
            if(!ndb.users[user].usage.apiCount) ndb.users[user].usage.apiCount = { openai: 0, anthropic: 0, google: 0 };
            ndb.users[user].usage.apiCount[result.provider] = (ndb.users[user].usage.apiCount[result.provider] || 0) + 1;
            
            const newVals = Object.assign({}, vals, result.data.data);
            setVals(newVals);
            if (role !== 'admin') {  
                if(!ndb.users[user].projects[uData.curProj].data[tid]) ndb.users[user].projects[uData.curProj].data[tid] = {};
                ndb.users[user].projects[uData.curProj].data[tid] = newVals; 
            }
            AppDB.save(ndb);
            showToast(result.tried > 0 ? '\uD83D\uDCA1 ' + result.provider.toUpperCase() + 'で魔法を実行！' : '\uD83D\uDCAB 魔法で入力しました！');
        } else { setError(result.error); }
        setIsMagicLoading(false);
      };  

      const getAutoBrowsingMode = () => {
          if (conf.isImagePrompt) return 'none';
          const textFields = conf.fields.filter(f => f.t !== 'image' && f.t !== 'check' && f.t !== 'select');
          const filledCount = textFields.filter(f => vals[f.id] && vals[f.id].trim() !== '').length;
          if (filledCount === 0) return 'god'; 
          if (filledCount < textFields.length) return 'auto';
          return 'full'; 
      };

      const getFinalPrompt = () => {
          let promptText = "";
          if (isCustom) {
              promptText = conf.buildPrompt;
              conf.fields.forEach(f => { promptText = promptText.replace(new RegExp(`{${f.id}}`, 'g'), vals[f.id]||''); });
          } else { promptText = conf.build ? conf.build(vals) : ''; }
          
          if (conf.isImagePrompt) return promptText;
          
          let emptyFields = []; let filledFields = []; let mainThemeValue = '';
          const today = new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
          
          conf.fields.forEach(f => {
              if (f.t === 'image' || f.t === 'check') return; 
              const val = vals[f.id] || '';
              if (!val || val.trim() === '') emptyFields.push(f.l);
              else { filledFields.push({ label: f.l, value: val }); if (f.isMainMagic || ['theme', 'topic', 'prod', 'kw'].includes(f.id)) mainThemeValue = val; }
          });
          
          const isGodMode = filledFields.length === 0;
          const isAutoMode = emptyFields.length > 0 && !isGodMode; 
          let magicBlock = '';
          
          if (isGodMode) {
              magicBlock = `\n🔥【STELLA NOTE - 神丸投げ LEVEL 3 SYSTEM】\n調査日時:${today}\nWeb検索を駆使してトレンド調査を行い、最適なテーマ選定から全項目の内容構築までを自動で行い、以下のプロンプトの要求に応えてください。\n`;
          } else if (isAutoMode) {
              magicBlock = `\n🌟【STELLA NOTE - AI自動補完 SYSTEM】\n調査日時:${today}\n未入力項目があります。Web検索で最新情報を調査し、最適な内容で補完した上で要求に応えてください。\n`;
          }
          
          let inputSummary = conf.fields.map(f => {
              if (f.t === 'image') return null; const val = vals[f.id];
              if (f.t === 'check') return '【' + f.l + '】\n' + (val ? '有効' : '無効');
              if (f.t === 'select') return '【' + f.l + '】\n' + (val || (f.opts && f.opts[0]) || '');
              if (!val || val.toString().trim() === '') return '【' + f.l + '】\n⚡ AI自動補完指示';
              return '【' + f.l + '】\n' + val;
          }).filter(Boolean).join('\n\n');

          let targetAiModel = genMode === 'api' ? aiModel : promptAiModel;
          return getAIPrefix(targetAiModel, uData.settings) + magicBlock + '\n' + promptText + '\n\n' + inputSummary;
      };

      const handleCopyPrompt = () => {
          copy(getFinalPrompt(), 'prompt');
          const mode = getAutoBrowsingMode();
          showToast(mode === 'god' ? '\uD83D\uDD25 神丸投げプロンプトをコピー！' : '\uD83D\uDCCB プロンプトをコピーしました！');
      };

      const handleGenerate = async () => {  
        if (role !== 'admin' && uData.credits <= 0) { setError('クレジットが不足しています。'); return; }
        setIsLoading(true); setError(''); setAlerts([]);
        
        let imageBase64 = null;
        if (conf.fields.some(f => f.t === 'image')) {
            imageBase64 = vals['image']; 
            if (!imageBase64) { setError('画像をアップロードしてください。'); setIsLoading(false); return; }
        }

        const fullPrompt = getFinalPrompt();
        const isImage = conf.isImagePrompt;
        const endpoint = isImage ? '/api/magic_generate' : '/api/auto_generate';
        const defaultProvider = isImage ? imageAI : (aiModel.includes('claude') ? 'anthropic' : aiModel.includes('gemini') ? 'google' : 'openai');
        
        let basePayload = isImage ? { tool_id: tid, fields: conf.fields.map(f => Object.assign({}, f, {val: vals[f.id]||''})) } : { prompt: fullPrompt, image_base64: imageBase64, ai_model: aiModel };

        const result = await fetchWithFallback(endpoint, basePayload, defaultProvider, ['openai', 'google', 'anthropic']);

        if (result.success) {
            const ndb = AppDB.get();
            if (role !== 'admin') { ndb.users[user].credits = Math.max(0, (ndb.users[user].credits || 0) - 1); }
            ndb.users[user].usage.count = (ndb.users[user].usage.count || 0) + 1;
            if(!ndb.users[user].usage.apiCount) ndb.users[user].usage.apiCount = { openai: 0, anthropic: 0, google: 0 };
            ndb.users[user].usage.apiCount[result.provider] = (ndb.users[user].usage.apiCount[result.provider] || 0) + 1;
            
            let finalRes = isImage ? result.data.data : trimAIResponse(result.data.result);
            setRes(finalRes); setPreviewTab('all');
            
            if(window.checkCompliance) {
                const compAlerts = window.checkCompliance(finalRes);
                if(compAlerts.length > 0) setAlerts(compAlerts);
            }

            if (role !== 'admin') {
                if (!ndb.users[user].projects[uData.curProj].data[tid]) ndb.users[user].projects[uData.curProj].data[tid] = {};
                ndb.users[user].projects[uData.curProj].data[tid].res = finalRes;
                if(!ndb.users[user].history) ndb.users[user].history = [];
                ndb.users[user].history.unshift({ tool: conf.name, date: new Date().toLocaleString(), result: finalRes });
                if(ndb.users[user].history.length > 5) ndb.users[user].history.pop();
            }
            AppDB.save(ndb); if(onUpdateUser) onUpdateUser(ndb);
            
            showToast(result.tried > 0 ? '\uD83D\uDCA1 ' + result.provider.toUpperCase() + 'で生成しました！' : '\u2728 生成完了！');
            if(window.innerWidth < 1024) setMobileTab('preview'); // スマホ版タブ自動遷移
        } else { setError(result.error); }
        setIsLoading(false);
      };  

      const modifyActionNames = { 'catchy': 'キャッチーに推敲', 'simple': 'シンプルに推敲', 'compliance': '炎上チェック', 'eyecatch_prompt': '画像プロンプト', 'line_cta': 'LINE誘導文追加', 'x_thread': 'Xツリー展開' };
      const buildModifyPrompt = (actionType, sourceText) => {
          if (actionType === 'catchy') return '以下の文章をよりキャッチーでバズりやすく推敲してください。\n\n' + sourceText;
          if (actionType === 'simple') return '以下の文章を小学生でも分かるシンプル表現にしてください。\n\n' + sourceText;
          if (actionType === 'compliance') return '以下の文章のコンプライアンス(薬機法・炎上)チェックと修正を行ってください。\n\n' + sourceText;
          if (actionType === 'line_cta') return '以下の末尾にLINE登録誘導文を追加してください。\n\n' + sourceText;
          if (actionType === 'x_thread') return '以下の文章をXのツリー投稿形式に分割してください。\n\n' + sourceText;
          return sourceText;
      };

      const handleModify = async (actionType) => {
          const builtPrompt = buildModifyPrompt(actionType, res);
          if (genMode === 'prompt') { copyTextToClipboard(builtPrompt); showToast('\uD83D\uDCCB 推敲プロンプトをコピーしました'); return; }
          if (role !== 'admin' && uData.credits <= 0) { setError('クレジット不足です'); return; }
          setIsLoading(true); setError('');

          let currentProvider = aiModel.includes('claude') ? 'anthropic' : aiModel.includes('gemini') ? 'google' : 'openai';
          const result = await fetchWithFallback('/api/auto_generate', { prompt: builtPrompt, ai_model: aiModel }, currentProvider, ['openai', 'google', 'anthropic']);
          
          if (result.success) {
              const newRes = res + '\n\n---\n\n### \uD83D\uDD04 追加結果 (' + (modifyActionNames[actionType]||actionType) + ')\n\n' + trimAIResponse(result.data.result);
              updateRes(newRes); showToast('\u2728 推敲完了！');
          } else { setError(result.error); }
          setIsLoading(false);
      };
 
      const copy = (text, key) => {
          copyTextToClipboard(text, role !== 'admin');
          setCopied(Object.assign({}, copied, { [key]: true }));
          setTimeout(() => setCopied(prev => Object.assign({}, prev, { [key]: false })), 2000);
      };

      const handleShare = () => {
          if (!shareCode.trim()) return alert('合言葉を入力してください');
          const ndb = AppDB.get(); ndb.sharedPrompts[shareCode] = { tid, vals }; AppDB.save(ndb);
          showToast('合言葉「' + shareCode + '」で保存しました！'); setShareCode('');
      };
      
      const handleLoadShare = () => {
          const ndb = AppDB.get(); const shared = ndb.sharedPrompts[loadCode];
          if (shared && shared.tid === tid) { setVals(shared.vals); showToast('復元しました！'); setLoadCode(''); } 
          else { alert('無効な合言葉です'); }
      };

      const handlePartialCopy = (part) => {
          if (!res) return;
          let extract = '';
          try {
              if (part === 'title') extract = res.split('---【無料エリア】---')[0].replace(/---【タイトル案】---/g, '').trim();
              else if (part === 'free') extract = res.split('---【無料エリア】---')[1].split('---【有料エリア】---')[0].trim();
              else if (part === 'paid') extract = res.split('---【有料エリア】---')[1].split('---【SEO・ハッシュタグ】---')[0].trim();
              else if (part === 'seo') extract = res.split('---【SEO・ハッシュタグ】---')[1].trim();
          } catch (e) { extract = res; }
          if(extract) {
              copyTextToClipboard(extract, role !== 'admin'); setCopied(Object.assign({}, copied, { [part]: true }));
              setTimeout(() => setCopied(prev => Object.assign({}, prev, { [part]: false })), 2000); showToast('\uD83D\uDCCB セクションをコピーしました！');
          }
      };

      const getScore = () => {
          if (!res || conf.isImagePrompt) return null;
          const len = res.length; const time = Math.ceil(len / 500);
          const kanjiMatch = res.match(/[\u4e00-\u9faf]/g); const kanjiRatio = kanjiMatch ? Math.round((kanjiMatch.length / len) * 100) : 0;
          let readScore = 100;
          if (kanjiRatio < 15) readScore -= (15 - kanjiRatio) * 2;
          if (kanjiRatio > 35) readScore -= (kanjiRatio - 35) * 2;
          return { len, time, readScore: Math.max(0, Math.min(100, readScore)) };
      };
      const score = getScore();
      const autoBrowsingMode = getAutoBrowsingMode();

      return div({ className: 'flex flex-col lg:flex-row h-full w-full animate-in relative lg:overflow-hidden' },  
        toast && div({ className: 'fixed top-4 lg:top-8 left-1/2 transform -translate-x-1/2 bg-brand text-white px-6 py-3 rounded-full shadow-2xl z-[999] font-bold text-sm animate-in' }, toast),

        // ▼ 手動貼り付けモーダル
        showPasteModal && div({ className: 'fixed inset-0 z-[300] bg-black/90 flex flex-col p-4 md:p-8 animate-in' },
            div({ className: 'flex items-center justify-between mb-4' },
                h3({ className: 'text-lg font-black text-white flex items-center gap-2' }, '\uD83D\uDCDD AI結果を貼り付け'),
                button({ onClick: () => setShowPasteModal(false), className: 'text-slate-400 hover:text-white text-2xl font-bold' }, '\u2715')
            ),
            textarea({ className: 'input-base flex-1 text-sm leading-relaxed resize-none mb-4', style: { minHeight: '60vh' }, placeholder: 'ここにAIの生成結果を貼り付けてください...', value: manualInput, onChange: e => setManualInput(e.target.value), autoFocus: true }),
            div({ className: 'flex gap-3' },
                button({ onClick: () => setShowPasteModal(false), className: 'flex-1 glass-panel py-3 rounded-xl font-bold text-white hover:bg-white/10' }, 'キャンセル'),
                button({ onClick: () => { if(manualInput.trim()) { updateRes(manualInput); setManualInput(''); setPreviewTab('all'); setShowPasteModal(false); } }, disabled: !manualInput.trim(), className: 'flex-1 btn-gradient py-3 rounded-xl font-black shadow-xl disabled:opacity-50' }, '\u2728 プレビューに反映')
            )
        ),

        // モバイル用タブ切替 UI
        div({ className: 'lg:hidden flex border-b border-white/10 bg-panel shrink-0' },
            button({ onClick: ()=>setMobileTab('input'), className: `flex-1 py-3 text-sm font-bold text-center ${mobileTab==='input' ? 'text-brand border-b-2 border-brand':'text-slate-400'}`}, '✏️ 入力・設定'),
            button({ onClick: ()=>setMobileTab('preview'), className: `flex-1 py-3 text-sm font-bold text-center ${mobileTab==='preview' ? 'text-brand border-b-2 border-brand':'text-slate-400'}`}, '👁️ プレビュー')
        ),

        // 左側（入力）
        div({ id: 'tool-left-panel', className: `w-full lg:w-[400px] lg:border-r border-white/10 p-6 md:p-8 shrink-0 flex flex-col lg:h-full lg:overflow-y-auto hide-scrollbar ${mobileTab==='input' ? 'block' : 'hidden lg:block'}` },
          div({ className: 'flex items-center gap-3 mb-6' },
              button({ onClick: onBack, className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-white/10' }, '\u2190'),
              h2({ className: 'text-xl font-black text-white' }, conf.name),
              conf.help && button({ onClick: () => setShowHelp(!showHelp), className: 'text-[10px] glass-panel px-2 py-1 rounded-lg text-slate-400 hover:text-white transition shrink-0 ml-auto' }, showHelp ? '✕ 閉じる' : '❓ 使い方')
          ),

          showHelp && conf.help && div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl' }, p({ className: 'text-xs text-slate-300 leading-relaxed' }, conf.help)),
          
          trends.length > 0 && div({ className: 'mb-4' },
              button({ onClick: () => setTrendOpen(!trendOpen), className: 'w-full flex items-center justify-between p-3 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10' },
                  div({ className: 'flex items-center gap-2' }, span({}, '\uD83D\uDD25'), span({ className: 'text-xs font-black text-white' }, '急上昇トレンド'), span({ className: 'text-[10px] bg-brand/20 text-brand-light px-1.5 rounded-full' }, trends.length + '件')),
                  span({ className: 'text-slate-400 text-xs' }, trendOpen ? '\u25B2 閉じる' : '\u25BC 開く')
              ),
              trendOpen && div({ className: 'mt-2 grid grid-cols-2 gap-2' },
                  trends.map((t, i) => button({ key: i, onClick: () => handleMagic('all', { keyword: t.title }), className: 'bg-white/5 border border-white/10 rounded-xl p-3 text-left hover:bg-white/10 transition group' },
                      p({ className: 'text-xs font-black text-white leading-tight line-clamp-2' }, t.title),
                      p({ className: 'text-[9px] text-slate-500 mt-1' }, 'タップで丸投げ \u2192')
                  ))
              )
          ),

          div({ className: 'mb-6 p-4 bg-white/5 border border-white/10 rounded-xl' },
              div({ className: 'flex justify-between items-center mb-3' },
                  h4({ className: 'text-xs font-bold text-brand-light flex items-center gap-2' }, '\u2728 魔法ツール'),
                  button({ onClick: () => setShowAdvancedMagic(!showAdvancedMagic), className: 'text-[10px] text-slate-400' }, showAdvancedMagic ? '閉じる' : '展開')
              ),
              button({ onClick: () => handleMagic('all'), disabled: isMagicLoading, className: 'w-full bg-gradient-to-r from-brand-accent to-red-500 text-white text-xs font-bold py-2 rounded-lg shadow-lg disabled:opacity-50' }, isMagicLoading ? '魔法詠唱中...' : '\uD83D\uDCAB 全項目を一撃で埋める'),
              
              showAdvancedMagic && div({ className: 'space-y-3 mt-3 pt-3 border-t border-white/10' },
                  div({}, label({ className: 'block text-[10px] text-slate-400 mb-1' }, '\uD83D\uDD17 URL抽出'),
                      div({ className: 'flex gap-2' }, input({ className: 'input-base !py-1.5 text-xs flex-1', value: urlInput, onChange: e => setUrlInput(e.target.value) }), button({ onClick: () => handleMagic('all'), disabled: !urlInput||isMagicLoading, className: 'glass-panel px-3 rounded-lg text-xs font-bold hover:bg-white/10 disabled:opacity-50'},'抽出'))
                  ),
                  div({}, label({ className: 'block text-[10px] text-slate-400 mb-1' }, '\uD83D\uDCA1 アイデア考案'),
                      div({ className: 'flex gap-2' }, input({ className: 'input-base !py-1.5 text-xs flex-1', value: keywordInput, onChange: e => setKeywordInput(e.target.value) }), button({ 
                          onClick: async () => {
                              if(!keywordInput) return; setIsMagicLoading(true);
                              try {
                                  const r = await fetch('/api/auto_generate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ prompt: 'キーワード「' + keywordInput + '」のコンテンツアイデアを3つ箇条書きで。', user_api_key: userKeys.openai, ai_model: 'chatgpt_free' }) });
                                  const d = await r.json(); if(d.status === 'success') setBrainstormIdeas(d.result.split('\n').filter(l => l.trim()));
                              } catch(e) {} setIsMagicLoading(false);
                          }, disabled: !keywordInput||isMagicLoading, className: 'glass-panel px-3 rounded-lg text-xs font-bold hover:bg-white/10 disabled:opacity-50' }, '考案')
                      )
                  ),
                  brainstormIdeas.length > 0 && div({ className: 'mt-2 space-y-1' }, brainstormIdeas.map((id, i) => button({ key: i, onClick: () => { handleMagic('all', { keyword: id }); setBrainstormIdeas([]); }, className: 'block w-full text-left text-[10px] bg-white/5 p-2 rounded text-slate-300' }, id)))
              )
          ),

          div({ className: 'mb-6 pb-6 border-b border-white/10' },
              div({ className: 'flex gap-2 mb-4' },
                  button({ onClick: () => setGenMode('api'), className: 'flex-1 py-2 rounded-lg text-xs font-bold border ' + (genMode === 'api' ? 'bg-brand/20 border-brand text-white' : 'bg-black/30 border-white/5 text-slate-400') }, 'API生成'),
                  button({ onClick: () => setGenMode('prompt'), className: 'flex-1 py-2 rounded-lg text-xs font-bold border ' + (genMode === 'prompt' ? 'bg-brand/20 border-brand text-white' : 'bg-black/30 border-white/5 text-slate-400') }, 'プロンプトのみ')
              )
          ),

          !conf.isImagePrompt && div({ className: 'mb-6 bg-black/20 border border-brand-light/20 rounded-xl p-4' },
              div({ className: 'flex items-center gap-2 mb-2' }, span({ className: 'text-xs font-black text-brand-light' }, '丸投げ状態: ' + (autoBrowsingMode==='god'?'神丸投げ':autoBrowsingMode==='auto'?'自動補完':'手動入力'))),
              p({ className: 'text-[10px] text-slate-400' }, autoBrowsingMode==='god'?'全自動でトレンドを調査し生成します。':autoBrowsingMode==='auto'?'未入力項目をAIが補完します。':'全項目が入力されています。')
          ),

          div({ className: 'space-y-6 flex-1' }, 
              conf.fields.map(f => el(FormInput, { key: f.id, f, val: vals[f.id], onChange: (id, v) => { const nv = Object.assign({}, vals, { [id]: v }); setVals(nv); if (role !== 'admin') { const ndb = AppDB.get(); ndb.users[user].projects[uData.curProj].data[tid] = nv; AppDB.save(ndb); } }, onMagic: handleMagic, isMagicLoading }))
          ),

          button({ onClick: () => { setVals({}); updateRes(''); setError(''); setUrlInput(''); setKeywordInput(''); setBrainstormIdeas([]); }, className: 'text-xs text-slate-500 hover:text-white mt-4 w-full text-right' }, '\uD83D\uDDD1\uFE0F クリア'),

          div({ className: 'mt-6 pt-6 border-t border-white/10' },
              button({ onClick: genMode === 'api' ? handleGenerate : handleCopyPrompt, disabled: isLoading || isMagicLoading, className: 'w-full btn-gradient py-4 rounded-xl font-black text-lg flex items-center justify-center gap-3 shadow-xl' }, 
                  isLoading ? [el(LoadingCircle), '魔法詠唱中...'] : (genMode === 'api' ? '\u2728 ' + (conf.isImagePrompt ? '呪文' : 'コンテンツ') + 'を生成' : '\uD83D\uDCCB プロンプトをコピー')
              )
          ),
          error && div({ className: 'mt-4' }, el(ErrorAlert, { msg: error }))
        ),

        // 右側（プレビュー）
        div({ id: 'tool-right-panel', className: `flex-1 bg-black min-h-[400px] lg:min-h-0 lg:h-full lg:overflow-y-auto flex flex-col ${mobileTab==='preview' ? 'block' : 'hidden lg:flex'}` },
            div({ className: 'flex flex-col gap-3 p-4 border-b border-white/10 bg-black/40 shrink-0' },
                div({ className: 'flex items-center justify-between' },
                    h3({ className: 'text-sm font-black text-slate-300 flex items-center gap-2' }, '\uD83D\uDC40 プレビュー', score && span({ className: 'text-[10px] text-slate-500' }, score.len + '文字')),
                    div({ className: 'flex gap-2' },
                        div({ className: 'flex bg-white/5 rounded-lg p-0.5 border border-white/10' },
                            button({ onClick: () => setPreviewMode('pc'), className: 'px-2 py-1 rounded text-xs font-bold transition ' + (previewMode === 'pc' ? 'bg-brand text-white' : 'text-slate-400') }, '\uD83D\uDCBB'),
                            button({ onClick: () => setPreviewMode('mobile'), className: 'px-2 py-1 rounded text-xs font-bold transition ' + (previewMode === 'mobile' ? 'bg-brand text-white' : 'text-slate-400') }, '\uD83D\uDCF1')
                        ),
                        button({ onClick: () => copy(res, 'raw'), className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold ' + (copied.raw?'text-brand-success':'text-slate-300') }, copied.raw ? '\u2713' : '\uD83D\uDCCB'),
                        button({ onClick: () => downloadText(res, conf.name), className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold text-slate-300' }, 'TXT'),
                        button({ onClick: () => exportToCSV(res, conf.name), className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold text-slate-300' }, 'CSV')
                    )
                ),
                alerts.length > 0 && div({ className: 'p-2 bg-brand-danger/10 border border-brand-danger/30 rounded-lg' }, alerts.map((a,i)=>p({key:i,className:'text-[10px] text-brand-danger'}, '\u26A0\uFE0F '+a))),
                tid === 'note' && res && div({ className: 'flex gap-1 overflow-x-auto hide-scrollbar' },
                    [{id:'all',l:'全体'},{id:'title',l:'タイトル'},{id:'free',l:'無料'},{id:'paid',l:'有料'},{id:'seo',l:'SEO'}].map(t => button({ key: t.id, onClick: ()=>setPreviewTab(t.id), className: 'px-3 py-1 rounded-lg text-xs font-bold ' + (previewTab===t.id?'bg-brand text-white':'glass-panel text-slate-400') }, t.l))
                )
            ),
            
            div({ className: 'flex-1 overflow-y-auto p-4 md:p-6' },
                div({ className: 'mx-auto transition-all duration-300 ' + (previewMode === 'mobile' ? 'max-w-[390px]' : 'max-w-full') },
                    conf.isImagePrompt ? div({ className: 'bg-gray-100 p-6 rounded-2xl font-mono text-sm text-black whitespace-pre-wrap' }, res) :
                    div({ className: 'bg-white p-5 md:p-8 rounded-2xl preview-content text-black leading-relaxed shadow-inner' }, div({ dangerouslySetInnerHTML: renderMarkdown(res) }))
                )
            ),
            
            !conf.isImagePrompt && div({ className: 'p-4 border-t border-white/10 shrink-0 bg-black/20' },
                h4({ className: 'text-[10px] font-black text-brand mb-2' }, '\uD83E\uDDD1\u200D\uD83C\uDFEB 推敲・展開'),
                div({ className: 'flex flex-wrap gap-1.5' },
                    ['catchy','simple','compliance','eyecatch_prompt','line_cta','x_thread','short_vid'].map(a => button({ key: a, onClick: ()=>handleModify(a), disabled: isLoading, className: 'glass-panel px-2 py-1 rounded text-[10px] text-slate-300' }, modifyActionNames[a]||a))
                )
            )
        )
      );
    };  

    // ================================================================
    // CommunityGallery (プロンプトギャラリー v73新機能)
    // ================================================================
    const CommunityGallery = ({ db, user, onUpdateDB, onBack }) => {
        const handleClone = (tool) => {
            const newDb = {...db};
            newDb.users[user].myTools.push({...tool, id: 'my_' + Date.now(), isCloned: true});
            AppDB.save(newDb); onUpdateDB(newDb);
            alert(`「${tool.name}」をマイツールにクローンしました！`);
        };

        return div({ className: 'flex flex-col h-full bg-bg p-6 lg:p-12 overflow-y-auto animate-in' },
            div({ className: 'flex items-center mb-8 gap-4' },
                button({ onClick: onBack, className: 'glass-panel px-4 py-2 rounded-lg text-sm font-bold text-slate-400 hover:text-white transition' }, '← 戻る'),
                h2({ className: 'text-3xl font-black text-white' }, '🌐 みんなのプロンプトギャラリー')
            ),
            div({ className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' },
                (db.sharedTools || []).length === 0 ? p({className: 'text-slate-400'}, 'まだ共有されたツールがありません。') :
                db.sharedTools.map((t, i) => div({ key: i, className: 'glass-panel p-6 rounded-2xl hover:border-brand/40 transition' },
                    h3({ className: 'text-xl font-bold text-white mb-2' }, t.name),
                    p({ className: 'text-sm text-slate-400 mb-4 line-clamp-3' }, t.desc),
                    div({ className: 'flex justify-between items-center text-xs text-slate-500 mb-4' }, span({}, `作者: ${t.author}`), span({}, `❤️ ${t.likes||0}  🔄 ${t.clones||0}`)),
                    button({ onClick: ()=>handleClone(t), className: 'w-full btn-gradient py-3 rounded-xl text-sm font-bold shadow-lg' }, '📥 クローンして使う')
                ))
            )
        );
    };

    // ================================================================
    // AdminDashboard (管理画面)
    // ================================================================
    const AdminDashboard = ({ user }) => {
        const [db, setDb] = useState(AppDB.get());
        const [toast, setToast] = useState('');
        const [tab, setTab] = useState('users'); 
        const [ann, setAnn] = useState(db.config.announcement);
        const [popupMsg, setPopupMsg] = useState(db.config.popupMessage || '');
        const [ic, setIc] = useState('');
        const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

        const handleStatus = (username, newStatus) => { const ndb = Object.assign({}, db); ndb.users[username].status = newStatus; AppDB.save(ndb); setDb(ndb); showToast('更新しました'); };
        const handleDelete = (username) => { if(confirm('完全に削除しますか？')) { const ndb = Object.assign({}, db); delete ndb.users[username]; AppDB.save(ndb); setDb(ndb); showToast('削除しました。'); } };

        const renderUsers = () => {
            const users = Object.keys(db.users).filter(k => k !== 'admin');
            return div({ className: 'glass-panel rounded-2xl overflow-x-auto' },
                table({ className: 'w-full text-left min-w-[800px]' },
                    thead({}, tr({ className: 'border-b border-white/10' }, th({className:'p-4'}, 'ユーザー'), th({className:'p-4'}, '状態'), th({className:'p-4'}, '利用'), th({className:'p-4'}, '操作'))),
                    tbody({}, users.map(u => {
                        const cost = ((db.users[u].usage?.count||0) * 0.5).toFixed(1); // API概算コスト
                        return tr({ key: u, className: 'border-b border-white/5' },
                        td({ className: 'p-4' }, div({ className: 'font-bold' }, u), div({ className: 'text-xs text-slate-500' }, db.users[u].sns)),
                        td({ className: 'p-4 text-xs' }, db.users[u].status, el('br'), db.users[u].lastLogin),
                        td({ className: 'p-4 text-xs' }, '🪙 ' + db.users[u].credits, el('br'), `生成 ${db.users[u].usage.count}回 (約${cost}円)`),
                        td({ className: 'p-4 flex gap-1' },
                            db.users[u].status === 'pending' ? button({ onClick:()=>handleStatus(u,'approved'), className: 'px-2 py-1 bg-brand-success/20 text-brand-success rounded' }, '承認') : button({ onClick:()=>handleStatus(u,'suspended'), className: 'px-2 py-1 bg-brand-accent/20 rounded' }, '凍結'),
                            button({ onClick:()=>handleDelete(u), className: 'px-2 py-1 bg-brand-danger/20 text-brand-danger rounded' }, '削除')
                        )
                    )}))
                )
            );
        };

        return div({ className: 'w-full max-w-6xl mx-auto p-6 md:p-12 animate-in' },
            toast && div({ className: 'fixed top-4 left-1/2 transform -translate-x-1/2 bg-brand text-white px-6 py-3 rounded-full' }, toast),
            h1({ className: 'text-3xl font-black mb-6' }, '👑 管理者ダッシュボード'),
            div({ className: 'flex gap-2 mb-6 border-b border-white/10 pb-2' }, ['users','system'].map(t => button({ key: t, onClick: () => setTab(t), className: 'px-4 py-2 rounded-full ' + (tab===t?'bg-brand':'bg-white/5') }, t))),
            tab === 'users' && renderUsers(),
            tab === 'system' && div({ className: 'space-y-6' },
                div({ className: 'glass-panel p-8 rounded-2xl' }, h3({className:'mb-4'}, 'お知らせ配信'), textarea({value:ann, onChange:e=>setAnn(e.target.value), className:'input-base mb-2 min-h-[100px]'}), button({onClick:()=>{const ndb={...db}; ndb.config.announcement=ann; AppDB.save(ndb); setDb(ndb);}, className:'btn-gradient px-4 py-2 rounded'}, '配信')),
                div({ className: 'glass-panel p-8 rounded-2xl' }, h3({className:'mb-4'}, '強制ポップアップ'), textarea({value:popupMsg, onChange:e=>setPopupMsg(e.target.value), className:'input-base mb-2 min-h-[100px]'}), button({onClick:()=>{const ndb={...db}; ndb.config.popupMessage=popupMsg; ndb.config.popupId=Date.now(); AppDB.save(ndb); setDb(ndb);}, className:'btn-gradient px-4 py-2 rounded'}, '配信')),
                div({ className: 'glass-panel p-8 rounded-2xl' }, h3({className:'mb-4'}, '招待コード (1回使い捨て)'), div({className:'flex gap-2'}, input({className:'input-base font-mono', value:ic, onChange:e=>setIc(e.target.value)}), button({onClick:()=>{if(!ic)return; const ndb={...db}; ndb.config.inviteCodes[ic]=true; AppDB.save(ndb); setDb(ndb); setIc('');}, className:'btn-gradient px-4 py-2 rounded'}, '発行')))
            )
        );
    };

    // ================================================================
    // MainApp (メイン画面: Sidebarにお気に入り追加)
    // ================================================================
    const MainApp = (props) => {  
      const [screen, setScreen] = useState('home');  
      const [activeCat, setActiveCat] = useState('omega');
      const [showSettings, setShowSettings] = useState(false);
      const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
      const [showPopup, setShowPopup] = useState(false);
      const [showGallery, setShowGallery] = useState(false);
      
      const db = AppDB.get();  
      const uData = db.users[props.user];  
 
      useEffect(() => { 
          if(props.role === 'admin') setScreen('admin_dashboard');
          else if (db.config.popupId && uData.readPopupId !== db.config.popupId) setShowPopup(true);
      }, [props.role]);

      const openTool = (tid) => {  
        if (tid === 'admin_dashboard') { setScreen('admin_dashboard'); setIsMobileMenuOpen(false); return; }
        const t = tid.startsWith('my_') ? uData.myTools.find(mt=>mt.id===tid) : window.AICP_TOOLS[tid];
        if(!t) return;
        const isLocked = t.reqLevel && ((uData.usage && uData.usage.count) || 0) < t.reqLevel && props.role !== 'admin';
        if (isLocked) return alert('生成回数不足によりロックされています。');
        setScreen(tid); setIsMobileMenuOpen(false); setShowGallery(false);
      };  

      const handleUpdateDB = (newDb) => { AppDB.save(newDb); };

      const toggleFav = (e, tid) => {
          e.stopPropagation();
          const ndb = AppDB.get();
          let favs = ndb.users[props.user].favoriteTools || [];
          if(favs.includes(tid)) favs = favs.filter(id => id !== tid); else favs.push(tid);
          ndb.users[props.user].favoriteTools = favs;
          AppDB.save(ndb); handleUpdateDB(ndb);
      };

      const ForcePopupModal = () => div({ className: 'fixed inset-0 z-[1000] flex items-center justify-center bg-black/90 p-4 animate-in' },
          div({ className: 'glass-panel rounded-3xl max-w-lg w-full p-8' }, h3({ className: 'text-2xl font-black mb-4' }, 'お知らせ'), p({className:'whitespace-pre-wrap mb-8'}, db.config.popupMessage), button({ onClick: () => { const ndb = AppDB.get(); ndb.users[props.user].readPopupId = ndb.config.popupId; AppDB.save(ndb); setShowPopup(false); }, className: 'w-full btn-gradient py-4 rounded-xl font-black' }, '確認して次へ'))
      );

      const Sidebar = () => div({ className: 'fixed lg:relative inset-y-0 left-0 z-50 transform ' + (isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full') + ' lg:translate-x-0 transition-transform duration-300 w-[260px] h-full bg-bg-panel border-r border-white/10 p-6 flex flex-col shrink-0' },
          button({ className: 'lg:hidden absolute top-4 right-4 text-slate-400 text-2xl', onClick: () => setIsMobileMenuOpen(false) }, '\u2715'),
          div({ className: 'flex items-center gap-2 mb-8 cursor-pointer', onClick: () => { setScreen('home'); setIsMobileMenuOpen(false); setShowGallery(false); } }, div({ className: 'w-3 h-8 bg-brand rounded-full' }), h1({ className: 'text-2xl font-black text-white' }, 'AICP Pro')),
          div({ className: 'flex-1 space-y-2 overflow-y-auto pb-10 custom-scrollbar' },
              props.role === 'admin' && div({ className: 'mb-6' }, button({ onClick: () => openTool('admin_dashboard'), className: 'w-full text-left p-3 rounded-lg text-sm font-bold ' + (screen==='admin_dashboard'?'bg-brand/10 text-white':'text-slate-300') }, '👑 ダッシュボード')),
              
              // お気に入り表示
              uData.favoriteTools?.length > 0 && div({ className: 'mb-6' },
                  h2({ className: 'text-[10px] font-black text-brand-accent uppercase tracking-[0.2em] mt-6 mb-2 ml-2' }, '⭐ お気に入り'),
                  uData.favoriteTools.map(tid => {
                      const t = window.AICP_TOOLS[tid] || uData.myTools?.find(mt=>mt.id===tid);
                      if(!t) return null;
                      return button({ key: `fav-${tid}`, onClick: () => openTool(tid), className: 'w-full text-left p-3 rounded-lg text-sm font-bold text-slate-300 hover:bg-white/5 truncate' }, t.icon + ' ' + t.name);
                  })
              ),

              h2({ className: 'text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mt-6 mb-2 ml-2' }, '📁 カテゴリー'),
              window.AICP_CATEGORIES.map(cat => button({ key: cat.id, onClick: () => { setActiveCat(cat.id); setScreen('home'); setShowGallery(false); setIsMobileMenuOpen(false); }, className: 'w-full text-left p-3 rounded-lg text-sm font-bold hover:bg-white/5 transition ' + (activeCat===cat.id && screen==='home' && !showGallery ? 'bg-brand/10 text-white' : 'text-slate-300') }, cat.name)),
              
              uData.myTools?.length > 0 && button({ onClick: () => { setActiveCat('mytools'); setScreen('home'); setShowGallery(false); setIsMobileMenuOpen(false); }, className: 'w-full text-left p-3 rounded-lg text-sm font-bold hover:bg-white/5 transition ' + (activeCat==='mytools' && screen==='home' && !showGallery ? 'bg-brand/10 text-white' : 'text-slate-300') }, '🛠️ マイツール'),
              
              div({className: 'my-4 border-t border-white/10'}),
              button({ onClick: () => { setShowGallery(true); setScreen('home'); setIsMobileMenuOpen(false); }, className: 'w-full text-left p-3 rounded-lg text-sm font-bold text-brand-accent hover:bg-white/5 ' + (showGallery?'bg-brand-accent/10':'') }, '🌐 プロンプトギャラリー')
          ),
          div({ className: 'mt-auto pt-6 border-t border-white/10 space-y-3' },
              button({ onClick: () => setShowSettings(true), className: 'w-full bg-white/5 p-3 rounded-lg text-sm font-bold text-slate-300 flex items-center gap-3' }, '\u2699\uFE0F 個人設定'),
              button({ onClick: props.onLogout, className: 'w-full text-left p-3 rounded-lg text-sm font-bold text-slate-500' }, '\uD83D\uDC4B ログアウト')
          )
      );

      const MobileHeader = () => div({ className: 'lg:hidden flex items-center justify-between p-4 bg-bg-panel border-b border-white/10 shrink-0' },
          div({ className: 'flex items-center gap-2 cursor-pointer', onClick: () => { setScreen('home'); setShowGallery(false); } }, div({ className: 'w-2 h-6 bg-brand rounded-full' }), h1({ className: 'text-xl font-black text-white' }, 'AICP Pro')),
          button({ onClick: () => setIsMobileMenuOpen(true), className: 'text-white text-3xl pb-1' }, '\u2261')
      );

      return div({ className: `flex h-full w-full relative overflow-hidden ${uData.settings?.theme === 'light' ? 'theme-light' : ''}` },  
        showPopup && el(ForcePopupModal),
        isMobileMenuOpen && div({ className: 'fixed inset-0 bg-black/60 z-40 lg:hidden', onClick: () => setIsMobileMenuOpen(false) }),
        el(Sidebar), showSettings && el(UserSettingModal, { user: props.user, onClose: () => setShowSettings(false) }),
        
        div({ className: 'flex-1 flex flex-col min-w-0 h-full bg-bg relative' },
            el(MobileHeader),
            div({ id: 'main-scroll-container', className: 'flex-1 overflow-y-auto hide-scrollbar' },
                screen === 'admin_dashboard' && props.role === 'admin' ? el(AdminDashboard, { user: props.user }) :
                showGallery ? el(CommunityGallery, { db, user: props.user, onUpdateDB: handleUpdateDB, onBack: ()=>setShowGallery(false) }) :
                screen === 'home' ? div({ className: 'max-w-6xl mx-auto p-6 md:p-12' },
                    uData.history && uData.history.length > 0 && div({className: 'mb-8'},
                        h4({className: 'text-xs font-bold text-slate-400 mb-3'}, '🕒 最近の生成履歴'),
                        div({className: 'flex gap-3 overflow-x-auto pb-2'}, uData.history.map((h, i) => div({key: i, className: 'glass-panel px-4 py-2 rounded-xl text-xs whitespace-nowrap shrink-0 border-white/5'}, span({className:'text-brand mr-2'}, h.tool), h.date)))
                    ),
                    div({ className: 'mb-12 flex justify-between items-end' },
                        div({}, h1({ className: 'text-4xl font-black text-white mb-3' }, 'こんにちは、' + uData.nickname + 'さん'), p({ className: 'text-slate-400' }, 'ツールを選択してください')),
                        props.role !== 'admin' && div({ className: 'glass-panel px-6 py-4 rounded-2xl text-right border-brand-accent/30 hidden md:block' }, p({ className: 'text-xs text-slate-400' }, '残りクレジット'), p({ className: 'text-3xl font-black text-brand-accent' }, '\uD83E\uDE99 ' + (uData.credits || 0)))
                    ),
                    
                    (activeCat === 'mytools' ? [{id:'mytools', name:'🛠️ マイツール'}] : window.AICP_CATEGORIES.filter(c => c.id === activeCat)).map(cat => div({ key: cat.id, className: 'mb-12 animate-in' },
                        h2({ className: 'text-2xl font-black text-white mb-6 border-b border-white/10 pb-4' }, cat.name),
                        div({ className: 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6' },
                            cat.id === 'mytools' && (uData.myTools||[]).map(t => div({ key: t.id, onClick: () => openTool(t.id), className: 'glass-panel p-6 rounded-2xl cursor-pointer hover:-translate-y-1 transition group relative' },
                                div({ className: 'absolute top-4 right-4 z-10 text-xl', onClick: (e)=>toggleFav(e, t.id) }, uData.favoriteTools?.includes(t.id) ? '⭐' : '☆'),
                                div({ className: 'text-4xl mb-4 group-hover:scale-110 transition' }, t.icon), h3({ className: 'text-lg font-black text-white mb-2' }, t.name), p({ className: 'text-xs text-slate-400 line-clamp-2' }, t.desc)
                            )),
                            cat.id !== 'mytools' && Object.keys(window.AICP_TOOLS||{}).filter(k=>window.AICP_TOOLS[k].cat===cat.id).map(tid => {
                                const t = window.AICP_TOOLS[tid];
                                return div({ key: tid, onClick: () => openTool(tid), className: 'glass-panel p-6 rounded-2xl cursor-pointer hover:-translate-y-1 transition group relative' },
                                    div({ className: 'absolute top-4 right-4 z-10 text-xl', onClick: (e)=>toggleFav(e, tid) }, uData.favoriteTools?.includes(tid) ? '⭐' : '☆'),
                                    div({ className: 'text-4xl mb-4 group-hover:scale-110 transition' }, t.icon), h3({ className: 'text-lg font-black text-white mb-2 pr-6' }, t.name), p({ className: 'text-xs text-slate-400 line-clamp-2' }, t.desc)
                                );
                            })
                        )
                    ))
                ) : (window.AICP_TOOLS[screen] || (uData.myTools&&uData.myTools.find(mt=>mt.id===screen))) && el(ToolCore, { tid: screen, user: props.user, role: props.role, onBack: () => setScreen('home'), onUpdateUser: handleUpdateDB, customTools: uData.myTools })
            )
        )
      );  
    };  
 
    // ================================================================
    // AuthBox (招待報酬・登録・利用規約)
    // ================================================================
    const AuthBox = (props) => {  
      const [mode, setMode] = useState('login');
      const [nickname, setNickname] = useState('');  
      const [pass, setPass] = useState('');  
      const [regSns, setRegSns] = useState('X(Twitter)');
      const [regUsername, setRegUsername] = useState('@');
      const [regPass, setRegPass] = useState(''); 
      const [regInviteCode, setRegInviteCode] = useState('');
      const [regAgreed, setRegAgreed] = useState(false);
      const [showTerms, setShowTerms] = useState(false);
      const [err, setErr] = useState('');  
      const [msg, setMsg] = useState('');
 
      const login = () => {  
        setErr(''); setMsg(''); const db = AppDB.get();  
        if (nickname === db.config.adminU && pass === db.config.adminP) {  
          db.users['admin'].lastLogin = new Date().toLocaleString('ja-JP'); AppDB.save(db);
          localStorage.setItem(SESS_KEY, JSON.stringify({ u: 'admin', r: 'admin' }));  
          props.onLogin('admin', 'admin'); return;  
        }  
        if(nickname && db.users[nickname]) {
            if (db.users[nickname].password && db.users[nickname].password !== pass && db.users[nickname].status !== 'pending') return setErr('パスワードが違います。');
            if (db.users[nickname].status === 'suspended') return setErr('凍結されています。');
            if (db.users[nickname].status === 'approved') {
                db.users[nickname].lastLogin = new Date().toLocaleString('ja-JP'); 
                AppDB.save(db); localStorage.setItem(SESS_KEY, JSON.stringify({ u: nickname, r: 'approved' })); props.onLogin(nickname, 'approved');
            } else if (db.users[nickname].status === 'pending') { setErr('承認待ちです。'); }
        } else { setErr('ユーザーが存在しません。'); }
      };  

      const register = () => {
          setErr(''); setMsg('');
          if (!regUsername.trim() || regUsername.trim() === '@') return setErr('ユーザー名を入力してください。');
          if (regPass.length < 6) return setErr('パスワードは6文字以上で設定してください。');
          if (!regAgreed) return setErr('利用規約に同意してください。');
          const db = AppDB.get();
          if (db.users[regUsername]) return setErr('このユーザー名は既に登録されています。');
          
          let initialStatus = 'pending';
          if (regInviteCode) {
              if (db.config.inviteCodes[regInviteCode]) { initialStatus = 'approved'; delete db.config.inviteCodes[regInviteCode]; }
              else {
                  // 招待コード報酬ロジック
                  let foundInviter = Object.keys(db.users).find(k => db.users[k].inviteCode === regInviteCode);
                  if (foundInviter) {
                      initialStatus = 'approved';
                      db.users[foundInviter].credits += 50; // 招待者に50クレジット付与
                  } else return setErr('招待コードが無効です。');
              }
          }

          db.users[regUsername] = {
              nickname: regUsername, sns: regSns, status: initialStatus, password: regPass, credits: regInviteCode ? 150 : 100, // 招待登録は150
              lastLogin: '-', loginHistory: [], usedInviteCode: regInviteCode || '', readPopupId: 0, inviteCode: 'USR'+Math.floor(Math.random()*100000),
              usage: { count: 0, tools: {}, apiCount: { openai: 0, anthropic: 0, google: 0 } }, perms: {}, settings: { aiModel: 'chatgpt_free', keys: {openai:'', anthropic:'', google:''}, theme: 'blue', tone: '丁寧で専門的', notifications: true, persona: '', knowledge: '', templateUrl: '' }, curProj: 'default', projects: { 'default': { name: 'マイスペース', data: {} } }
          };
          AppDB.save(db);
          setMsg(initialStatus === 'approved' ? '招待コードが適用され、登録されました！ログインしてください。' : '申請完了！承認をお待ちください。');
          setRegUsername('@'); setRegPass(''); setRegInviteCode(''); setRegAgreed(false); setMode('login');
      };

      const TermsModal = () => div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4' },
          div({ className: 'glass-panel rounded-3xl max-w-lg w-full p-8' }, h3({ className: 'text-xl font-black text-white mb-4' }, '\uD83D\uDCDC 利用規約'), p({className:'text-sm text-slate-300 mb-6 leading-relaxed'}, '本システムのご利用には以下の規約に同意が必要です。\n\n第1条(禁止事項): 第三者への共有・販売\n第2条(自作発言): システム自体の自作発言\n第3条(複製): ソースコード等の無断複製\n第4条(利用停止): 違反時のアカウント停止'), button({ onClick: () => { setRegAgreed(true); setShowTerms(false); }, className: 'w-full btn-gradient py-4 rounded-xl font-black' }, '同意する'))
      );
 
      return div({ className: 'w-full h-full flex items-center justify-center p-4' },  
        showTerms && el(TermsModal),
        div({ className: 'glass-panel rounded-3xl p-10 md:p-16 shadow-2xl text-center max-w-lg w-full relative' },  
          h2({ className: 'text-3xl font-black mb-8 tracking-tight text-white' }, 'AICP Pro'),  
          div({ className: 'flex mb-8 border-b border-white/10' },
              button({ onClick: () => { setMode('login'); setErr(''); setMsg(''); }, className: 'flex-1 pb-3 font-bold ' + (mode === 'login' ? 'text-brand border-b-2 border-brand' : 'text-slate-500') }, 'ログイン'),
              button({ onClick: () => { setMode('register'); setErr(''); setMsg(''); }, className: 'flex-1 pb-3 font-bold ' + (mode === 'register' ? 'text-brand border-b-2 border-brand' : 'text-slate-500') }, '新規登録')
          ),
          msg && p({ className: 'text-brand-success text-sm font-bold text-center mb-6 bg-brand-success/10 p-3 rounded-lg' }, msg),
          err && p({ className: 'text-brand-danger text-sm font-bold text-center mb-6 bg-brand-danger/10 p-3 rounded-lg' }, err),

          mode === 'login' ? div({ className: 'space-y-5 animate-in' },  
            input({ className: 'input-base text-center', placeholder: 'SNSユーザー名 / ニックネーム', value: nickname, onChange: e => setNickname(e.target.value) }),  
            input({ type: 'password', className: 'input-base text-center font-mono', placeholder: 'パスワード', value: pass, onChange: e => setPass(e.target.value), onKeyDown: e => { if(e.key === 'Enter') login(); } }),  
            button({ onClick: login, className: 'w-full btn-gradient py-4 rounded-xl text-lg mt-4 shadow-lg' }, 'ログインする')  
          ) : div({ className: 'space-y-5 animate-in' },
            el('select', { className: 'input-base text-center text-sm', value: regSns, onChange: e => { const val = e.target.value; setRegSns(val); if (val === 'X(Twitter)') setRegUsername('@'); else if (val === 'Threads') setRegUsername(''); }}, option({ value: 'X(Twitter)' }, 'X (Twitter)で登録'), option({ value: 'Threads' }, 'Threadsで登録')),
            input({ className: 'input-base text-center font-mono', placeholder: regSns === 'X(Twitter)' ? '@ユーザー名' : 'ユーザー名', value: regUsername, onChange: e => setRegUsername(e.target.value) }),
            input({ type: 'password', className: 'input-base text-center font-mono mt-2', placeholder: 'パスワードを設定 (6文字以上)', value: regPass, onChange: e => setRegPass(e.target.value) }),
            input({ className: 'input-base text-center font-mono mt-2', placeholder: '招待コード (お持ちの場合)', value: regInviteCode, onChange: e => setRegInviteCode(e.target.value) }),
            div({ className: 'flex items-center gap-3 p-3 mt-4 bg-black/30 rounded-xl' },
                div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition shrink-0 cursor-pointer' }, div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (regAgreed ? 'bg-brand left-5' : 'bg-gray-400') }) ),  
                button({ onClick: () => setShowTerms(true), className: 'text-xs text-brand hover:text-brand-light font-bold text-left underline' }, '利用規約を確認し、同意する')  
            ),
            button({ onClick: register, disabled: !regAgreed, className: 'w-full btn-gradient py-4 rounded-xl text-lg mt-4 disabled:opacity-50' }, '登録申請する')
          )
        )  
      );  
    };  
 
    const App = () => {  
      const [auth, setAuth] = useState({ u: null, r: null });  
      useEffect(() => {  
        const session = localStorage.getItem(SESS_KEY);  
        if (session) { try { setAuth(JSON.parse(session)); } catch(e) { localStorage.removeItem(SESS_KEY); } }
      }, []);  
      if (!auth.u) return el(AuthBox, { onLogin: (u, r) => setAuth({ u, r }) });  
      return el(MainApp, { user: auth.u, role: auth.r, onLogout: () => { localStorage.removeItem(SESS_KEY); setAuth({ u: null, r: null }); } });  
    };  
 
    ReactDOM.createRoot(document.getElementById('root')).render(el(App));  
})();