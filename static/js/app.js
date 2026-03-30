(function() {  
    'use strict';  
    const el = React.createElement;  
    const { useState, useEffect, Component, Fragment, useRef } = React;  
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
    const option = (pr, ...c) => el('option', pr, ...c);
    const table = (pr, ...c) => el('table', pr, ...c);
    const thead = (pr, ...c) => el('thead', pr, ...c);
    const tbody = (pr, ...c) => el('tbody', pr, ...c);
    const tr = (pr, ...c) => el('tr', pr, ...c);
    const th = (pr, ...c) => el('th', pr, ...c);
    const td = (pr, ...c) => el('td', pr, ...c);
 
    const DB_KEY = 'AICP_v70_BYOK_DB';   
    const SESS_KEY = 'AICP_v70_Session';  
    const SYS_VERSION = 'v71.1.3 Ultimate Auto-Browsing Edition';  
 
    const AppDB = {  
      get: () => {  
        let db = null;  
        try { db = JSON.parse(localStorage.getItem(DB_KEY)); } catch (e) {}  
        if (!db) {  
          db = {   
            config: { adminU: 'admin', adminP: 'admin123', announcement: '', inviteCodes: {}, popupMessage: '', popupId: 0 },   
            errorLogs: [], sharedPrompts: {},
            users: { 'admin': { nickname: '管理者', status: 'approved', credits: 99999, lastLogin: '', loginHistory: [], usage: { count: 0, tools: {}, apiCount: { openai: 0, anthropic: 0, google: 0 } }, perms: {}, settings: { aiModel: 'chatgpt_free', keys: {openai:'', anthropic:'', google:''}, theme: 'blue', tone: '丁寧で専門的', notifications: true, persona: '', knowledge: '', templateUrl: '' }, curProj: 'default', projects: { 'default': { name: '管理者領域', data: {} } }, usedInviteCode: '', readPopupId: 0 } }   
          };  
          localStorage.setItem(DB_KEY, JSON.stringify(db));  
        }  
        Object.keys(db.users).forEach(u => {
            if(db.users[u].credits === undefined) db.users[u].credits = 100;
            if(!db.users[u].settings.templates) db.users[u].settings.templates = ['', '', ''];
        });
        return db;  
      },  
      save: (db) => { try { localStorage.setItem(DB_KEY, JSON.stringify(db)); } catch (e) {} }  
    };  
 
    const getAIPrefix = (modelId, settings) => {  
      const isPaid = modelId.includes('paid');  
      let aiName = modelId.includes('claude') ? 'Claude' : modelId.includes('gemini') ? 'Gemini' : 'ChatGPT';
      let spec = isPaid
        ? '有料版(最上位モデル)です。最高の創造性を発揮してください。\n※【最重要】最新のトレンドや正確な事実確認が必要な場合は、必ず「Web検索（ブラウジング機能）」を使用して情報を取得してください。\nその際、海外の情報を直訳したり、検索結果をそのまま羅列するのではなく、必ず「日本の文化・市場・SNSの文脈」に合わせて解釈し、読者が直感的に理解できるわかりやすく魅力的な表現に変換した上で出力に反映させてください。'
        : '無料版です。簡潔かつ的確に要求を満たしてください。';
      let tone = settings && settings.tone ? '\n※出力のトーン・文体は「' + settings.tone + '」で統一してください。' : '';
      let personaText = settings && settings.persona ? '\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\n' + settings.persona + '\n' : '';
      let knowledgeText = settings && settings.knowledge ? '\n※【マイ・ナレッジ】以下の情報を前提知識として活用してください：\n' + settings.knowledge + '\n' : '';
      return '【システム指示：' + aiName + ' ' + spec + '】\nあなたは世界トップクラスの専門家（AI）アシスタントです。' + tone + personaText + knowledgeText + '\n\n';
    };  

    const getUserLevel = (count) => {
        if (count >= 50) return { name: '神', icon: '👑', color: 'text-yellow-400', border: 'border-yellow-400/50' };
        if (count >= 20) return { name: 'マスター', icon: '💎', color: 'text-purple-400', border: 'border-purple-400/50' };
        if (count >= 5) return { name: 'レギュラー', icon: '⭐', color: 'text-brand-light', border: 'border-brand-light/50' };
        return { name: 'ビギナー', icon: '🌱', color: 'text-slate-400', border: 'border-white/10' };
    };
 
    const renderMarkdown = (text) => {  
      if (!text) return { __html: '' };  
      let html = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');  
      html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');  
      html = html.replace(/^### (.*$)/gim, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>');  
      html = html.replace(/^## (.*$)/gim, '<h2 class="text-xl font-black mt-6 mb-3 border-l-4 border-brand pl-2">$1</h2>');  
      html = html.replace(/^# (.*$)/gim, '<h1 class="text-2xl font-black mt-8 mb-4 border-b border-gray-200 pb-2">$1</h1>');  
      html = html.replace(/^\- (.*$)/gim, '<ul class="list-disc pl-5 mb-2"><li>$1</li></ul>');  
      html = html.replace(/<\/ul>\n*<ul class="list-disc pl-5 mb-2">/gim, '');  
      html = html.replace(/\n/g, '<br/>');  
      return { __html: html };  
    };  

    const copyTextToClipboard = (text) => {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try { document.execCommand('copy'); } catch (err) { console.error('Copy failed', err); }
        document.body.removeChild(textArea);
    };
 
    const LoadingCircle = () => div({ className: 'w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin' });
    const ErrorAlert = ({ msg }) => div({ className: 'p-4 bg-brand-danger/10 border border-brand-danger/30 rounded-xl text-brand-danger text-sm font-bold animate-in' }, '\u26A0\uFE0F エラー: ' + msg);

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
          div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition' },   
            div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (value ? 'bg-brand left-5' : 'bg-gray-400') })  
          ),  
          el('input', { type: 'checkbox', className: 'hidden', checked: !!value, onChange: e => onChange(f.id, e.target.checked) }),  
          span({ className: 'text-sm font-bold text-slate-300' }, '機能を有効にする')  
        );  
        if (f.t === 'image') return div({ className: 'mt-2' },
            el('input', { type: 'file', accept: 'image/*', className: 'text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-brand/20 file:text-brand hover:file:bg-brand/30 cursor-pointer transition',
                onChange: e => {
                    const file = e.target.files[0];
                    if(file) {
                        const reader = new FileReader();
                        reader.onload = ev => onChange(f.id, ev.target.result.split(',')[1]);
                        reader.readAsDataURL(file);
                    }
                }
            }),
            value ? span({className: 'ml-3 text-xs text-brand-success font-bold'}, '\u2713 画像セット済') : null
        );
        return null;  
      };  
 
      return div({ className: 'mb-6 animate-in relative' },  
        isMagicLoading && isMainMagic && div({ className: 'absolute inset-0 bg-black/60 z-10 rounded-2xl flex items-center justify-center backdrop-blur-sm' }, el(LoadingCircle)),
        div({ className: 'flex justify-between items-center mb-2 gap-2' },  
          span({ className: 'text-xs font-black text-slate-400 tracking-wider' }, f.l),  
          isMainMagic && button({   
            onClick: () => onMagic(f.id),  
            disabled: isMagicLoading,
            className: 'bg-gradient-to-r from-brand-accent to-red-500 text-white text-[10px] font-black px-3 py-1 rounded-full shadow-lg hover:brightness-110 transition disabled:opacity-50'  
          }, '\u2728 魔法で入力')
        ),  
        inputEl()  
      );  
    };  
 
    const UserSettingModal = ({ user, onClose }) => {
        const [db, setDb] = useState(AppDB.get());
        const uData = db.users[user];
        const [tab, setTab] = useState('api');
        
        const [keys, setKeys] = useState(uData.settings.keys);
        const [aiModel, setAiModel] = useState(uData.settings.aiModel);
        const [theme, setTheme] = useState(uData.settings.theme);
        const [tone, setTone] = useState(uData.settings.tone);
        const [persona, setPersona] = useState(uData.settings.persona || '');
        const [knowledge, setKnowledge] = useState(uData.settings.knowledge || '');
        const [templateUrl, setTemplateUrl] = useState(uData.settings.templateUrl || '');
        const [notif, setNotif] = useState(uData.settings.notifications);
        const [templates, setTemplates] = useState(uData.settings.templates);
        
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
            ndb.users[user].settings = Object.assign({}, ndb.users[user].settings, { keys, aiModel, theme, tone, persona, knowledge, templateUrl, notifications: notif, templates });
            AppDB.save(ndb);
            onClose();
            window.location.reload(); 
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
                        const ndb = AppDB.get();
                        ndb.users[user] = Object.assign({}, ndb.users[user], imported);
                        AppDB.save(ndb);
                        showToast('個人データを復元しました。再読み込みします...');
                        setTimeout(() => window.location.reload(), 1500);
                    } else {
                        alert('無効なデータファイルです。');
                    }
                } 
                catch(err) { alert('ファイルの読み込みに失敗しました。'); }
            };
            reader.readAsText(file);
        };

        const handleDeleteReq = () => {
            if(confirm('本当にアカウントの退会（データ削除）を申請しますか？この操作は取り消せません。')) {
                const ndb = AppDB.get(); ndb.users[user].status = 'delete_requested'; AppDB.save(ndb);
                alert('退会申請を受け付けました。自動的にログアウトします。');
                localStorage.removeItem(SESS_KEY); window.location.reload();
            }
        };
        
        const extractPersona = async () => {
            if(!personaSource) return alert('文章を入力してください');
            setIsExtracting(true);
            
            let tried = [];
            let lastError = '';
            let meaningfulError = ''; 
            let order = ['openai', 'google', 'anthropic'];
            let success = false;

            for (let provider of order) {
                let ai_model = provider === 'anthropic' ? 'claude_free' : provider === 'google' ? 'gemini_free' : 'chatgpt_free';
                try {
                    const res = await fetch('/api/auto_generate', {
                        method: 'POST', headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ prompt: '以下の文章を分析し、筆者の「職業、専門性、性格、文章のクセ（語尾など）」を詳細に抽出し、AIに憑依させるためのプロンプト（マイ・ペルソナ設定）を作成してください。出力はペルソナ設定のテキストのみにしてください。\n\n' + personaSource, user_api_key: keys[provider], ai_model: ai_model })
                    });
                    const data = await res.json();
                    if(data.status === 'success') {
                        setPersona(data.result);
                        setPersonaSource('');
                        setShowPersonaExtractor(false);
                        
                        const ndb = AppDB.get();
                        if(!ndb.users[user].usage.apiCount) ndb.users[user].usage.apiCount = { openai: 0, anthropic: 0, google: 0 };
                        ndb.users[user].usage.apiCount[provider] = (ndb.users[user].usage.apiCount[provider] || 0) + 1;
                        AppDB.save(ndb);

                        if (tried.length > 0) showToast('\uD83D\uDCA1 ' + provider.toUpperCase() + 'を使用してペルソナを自動抽出しました！');
                        else showToast('\u2728 ペルソナを自動抽出しました！');
                        success = true;
                        break;
                    } else {
                        lastError = data.message;
                        if (!data.message.includes('APIキーが設定されていません') && !meaningfulError) {
                            meaningfulError = '[' + provider.toUpperCase() + '] ' + data.message;
                        }
                        tried.push(provider);
                        if (data.message.includes('APIキーが設定されていません') || data.message.includes('insufficient_quota') || data.message.includes('429') || data.message.includes('エラー') || data.message.includes('API key not valid')) {
                            if (tried.length < order.length) showToast('\u26A0\uFE0F ' + provider.toUpperCase() + 'エラー。別のAIで再試行中...');
                            continue;
                        } else { break; }
                    }
                } catch(e) {
                    lastError = '通信エラーが発生しました';
                    if (!meaningfulError) meaningfulError = '[' + provider.toUpperCase() + '] ' + lastError;
                    tried.push(provider);
                }
            }
            if(!success) {
                let finalError = meaningfulError || 'APIキーが設定されていないか、利用できません。設定を確認してください。\n詳細: ' + lastError;
                alert('抽出エラー: \n' + finalError);
            }
            setIsExtracting(false);
        };

        const keyInput = (lang, provider, ph) => div({ className: 'mb-4' },
            label({ className: 'block text-xs font-bold text-slate-400 mb-1.5' }, lang + ' APIキー (' + provider + ')'),
            el('input', { type: 'password', className: 'input-base !py-2.5 text-sm font-mono', placeholder: ph, value: keys[provider], onChange: e => setKeys(Object.assign({}, keys, { [provider]: e.target.value })) })
        );

        return div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4 animate-in' },
            toast && div({ className: 'fixed top-8 left-1/2 transform -translate-x-1/2 bg-brand text-white px-6 py-3 rounded-full shadow-2xl z-[999] font-bold text-sm animate-in' }, toast),
            div({ className: 'glass-panel rounded-3xl max-w-2xl w-full p-8 relative flex flex-col max-h-[90vh]' },
                button({ onClick: onClose, className: 'absolute top-5 right-5 text-slate-400 hover:text-white text-xl font-bold transition' }, '\u2715'),
                h3({ className: 'text-xl font-black text-white mb-6 pb-4 border-b border-white/10' }, '\u2699\uFE0F 個人設定 (General Settings)'),
                
                div({ className: 'flex gap-2 mb-6 border-b border-white/10 pb-2 overflow-x-auto hide-scrollbar' },
                    ['api', 'ui', 'knowledge', 'account', 'data'].map(t => button({ key: t, onClick: () => setTab(t), className: 'px-4 py-2 rounded-full text-xs font-bold transition whitespace-nowrap ' + (tab === t ? 'bg-brand text-white' : 'text-slate-400 hover:bg-white/10') }, 
                        t === 'api' ? '\uD83D\uDD11 API設定' : 
                        t === 'ui' ? '\uD83C\uDFA8 UI・出力' : 
                        t === 'knowledge' ? '\uD83D\uDCDA ナレッジ' : 
                        t === 'account' ? '\uD83D\uDC64 アカウント・セキュリティ' : '\uD83D\uDCBE データ管理'))
                ),

                div({ className: 'overflow-y-auto flex-1 pr-3 hide-scrollbar space-y-6' },
                    tab === 'api' && div({ className: 'animate-in' },
                        div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl leading-relaxed text-slate-300' },
                            p({ className: 'text-xs font-bold text-brand-light mb-2' }, '\u26A0\uFE0F APIキーの登録と注意点'),
                            p({ className: 'text-[10px] mb-1' }, '・ここで登録したキーはご自身のブラウザ内にのみ安全に保存され、サーバーには送信されません。'),
                            p({ className: 'text-[10px] mb-1' }, '・各AIの無料枠や課金上限にご注意ください。1つのAPIが上限や未設定でエラーになった場合、自動的に他の登録済みAPIへフォールバック(自動切り替え)して生成を継続します。'),
                            div({ className: 'flex flex-wrap gap-3 mt-3 text-[10px]' },
                                el('a', { href: 'https://platform.openai.com/api-keys', target: '_blank', className: 'text-brand hover:underline font-bold' }, '\uD83D\uDD17 OpenAIキー取得'),
                                el('a', { href: 'https://aistudio.google.com/app/apikey', target: '_blank', className: 'text-brand hover:underline font-bold' }, '\uD83D\uDD17 Geminiキー取得'),
                                el('a', { href: 'https://console.anthropic.com/settings/keys', target: '_blank', className: 'text-brand hover:underline font-bold' }, '\uD83D\uDD17 Claudeキー取得')
                            )
                        ),
                        
                        div({ className: 'flex gap-2 mb-6' },
                            div({ className: 'flex-1 glass-panel p-3 rounded-xl text-center border-white/5' },
                                p({ className: 'text-[10px] text-slate-400 mb-1' }, 'ChatGPT 使用目安'),
                                p({ className: 'text-lg font-bold text-white' }, (uData.usage && uData.usage.apiCount ? uData.usage.apiCount.openai : 0) + '回')
                            ),
                            div({ className: 'flex-1 glass-panel p-3 rounded-xl text-center border-white/5' },
                                p({ className: 'text-[10px] text-slate-400 mb-1' }, 'Gemini 使用目安'),
                                p({ className: 'text-lg font-bold text-white' }, (uData.usage && uData.usage.apiCount ? uData.usage.apiCount.google : 0) + '回')
                            ),
                            div({ className: 'flex-1 glass-panel p-3 rounded-xl text-center border-white/5' },
                                p({ className: 'text-[10px] text-slate-400 mb-1' }, 'Claude 使用目安'),
                                p({ className: 'text-lg font-bold text-white' }, (uData.usage && uData.usage.apiCount ? uData.usage.apiCount.anthropic : 0) + '回')
                            )
                        ),

                        keyInput('ChatGPT (OpenAI)', 'openai', 'sk-...'),
                        keyInput('Claude (Anthropic)', 'anthropic', 'sk-ant-...'),
                        keyInput('Gemini (Google)', 'google', 'AIza...'),
                        div({ className: 'mt-6 pt-6 border-t border-white/10' },
                            label({ className: 'block text-xs font-bold text-slate-400 mb-1.5' }, '\uD83E\uDD16 デフォルトAIモデル'),
                            el('select', { className: 'input-base !py-2.5 text-sm', value: aiModel, onChange: e => setAiModel(e.target.value) },
                                option({ value: 'chatgpt_free' }, 'ChatGPT (無料版)'), option({ value: 'chatgpt_paid' }, 'ChatGPT Plus (有料版)'),
                                option({ value: 'claude_free' }, 'Claude 3 (無料版)'), option({ value: 'claude_paid' }, 'Claude 3 Pro (有料版)'),
                                option({ value: 'gemini_free' }, 'Gemini (無料版)'), option({ value: 'gemini_paid' }, 'Gemini Advanced (有料版)')
                            )
                        )
                    ),
                    tab === 'ui' && div({ className: 'animate-in space-y-6' },
                        div({}, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83C\uDFA8 UIテーマカラー'),
                            div({ className: 'flex gap-3' },
                                ['blue', 'purple', 'emerald'].map(c => button({ key: c, onClick: () => setTheme(c), className: 'w-12 h-12 rounded-full border-4 transition ' + (theme === c ? 'border-white scale-110' : 'border-transparent opacity-50 hover:opacity-100') + ' ' + (c==='blue'?'bg-[#0ea5e9]':c==='purple'?'bg-[#a855f7]':'bg-[#10b981]') }))
                            )
                        ),
                        div({}, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83D\uDDE3\uFE0F デフォルト出力トーン (文体)'),
                            el('select', { className: 'input-base !py-2.5 text-sm', value: tone, onChange: e => setTone(e.target.value) }, option({ value: '丁寧で専門的' }, '丁寧で専門的 (おすすめ)'), option({ value: '親しみやすいタメ口' }, '親しみやすいタメ口'), option({ value: '情熱的でセールス寄り' }, '情熱的でセールス寄り'), option({ value: '論理的で簡潔' }, '論理的で簡潔'))
                        ),
                        div({ className: 'pt-6 border-t border-white/10' }, 
                            label({ className: 'block text-xs font-bold text-slate-400 mb-2 flex justify-between items-center' }, 
                                '\uD83D\uDC64 マイ・ペルソナ（自分専用AI化）',
                                button({ onClick: () => setShowPersonaExtractor(!showPersonaExtractor), className: 'text-brand hover:text-brand-light flex items-center gap-1' }, '\u2728 自動抽出ツール')
                            ),
                            showPersonaExtractor && div({ className: 'mb-4 p-4 bg-brand/10 border border-brand/20 rounded-xl animate-in' },
                                textarea({ className: 'input-base min-h-[100px] text-xs mb-2', placeholder: '過去に書いたブログや日記、ツイートなどをここに貼り付けてください...', value: personaSource, onChange: e => setPersonaSource(e.target.value) }),
                                button({ onClick: extractPersona, disabled: isExtracting, className: 'w-full btn-gradient py-2 rounded-lg text-xs font-bold' }, isExtracting ? '抽出中...' : '文章からペルソナを自動抽出')
                            ),
                            textarea({ className: 'input-base min-h-[100px] text-xs', placeholder: '例: 私はプロのWebマーケターです。実績は〇〇で、文章は論理的かつ情熱的に書きます。', value: persona, onChange: e => setPersona(e.target.value) }),
                            p({ className: 'text-[10px] text-slate-500 mt-1' }, '※ここに設定したあなたの特徴やルールは、すべてのツールでAIに完全に憑依されます。')
                        ),
                        label({ className: 'flex items-center gap-3 cursor-pointer p-3 bg-white/5 rounded-xl mt-4' },   
                            div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition shrink-0' }, div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (notif ? 'bg-brand left-5' : 'bg-gray-400') })),  
                            el('input', { type: 'checkbox', className: 'hidden', checked: notif, onChange: e => setNotif(e.target.checked) }),  
                            span({ className: 'text-sm font-bold text-slate-300' }, '\uD83D\uDD14 システム内ポップアップ通知を有効にする')  
                        ),
                        div({ className: 'pt-6 border-t border-white/10' }, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83C\uDFAD マイ・プロンプトテンプレート (備忘録)'),
                            [0, 1, 2].map(i => textarea({ key: i, className: 'input-base min-h-[60px] text-xs mb-2', placeholder: 'テンプレート ' + (i+1), value: templates[i], onChange: e => { const nt = templates.slice(); nt[i] = e.target.value; setTemplates(nt); } }))
                        )
                    ),
                    tab === 'knowledge' && div({ className: 'animate-in space-y-6' },
                        div({}, label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83D\uDCDA マイ・ナレッジ（前提知識・RAGデータ）'),
                            textarea({ className: 'input-base min-h-[200px] text-xs leading-relaxed', placeholder: '例: 自社商品の仕様、過去のブログ記事、よく使う専門用語などを登録しておくと、AIがこの知識を元に記事を生成します。', value: knowledge, onChange: e => setKnowledge(e.target.value) }),
                            p({ className: 'text-[10px] text-slate-500 mt-2' }, '※ここに登録した情報は、すべてのツールでAIの前提知識として活用されます。')
                        ),
                        div({ className: 'pt-6 border-t border-white/10' }, 
                            label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83C\uDF10 Web連携 無限テンプレートURL (note記事用)'),
                            input({ className: 'input-base !py-2.5 text-sm font-mono', placeholder: '例: https://raw.githubusercontent.com/.../templates.json', value: templateUrl, onChange: e => setTemplateUrl(e.target.value) }),
                            p({ className: 'text-[10px] text-slate-500 mt-2' }, '※GitHub Gist等で公開したJSONファイルのURLを指定すると、外部からテンプレートを自動同期できます。')
                        )
                    ),
                    tab === 'account' && div({ className: 'animate-in space-y-6' },
                        div({ className: 'flex gap-4 p-4 bg-brand/10 rounded-xl border border-brand/20' },
                            div({ className: 'flex-1' }, p({ className: 'text-xs text-brand mb-1 font-bold' }, '\uD83E\uDE99 残りクレジット'), p({ className: 'text-2xl font-black text-white' }, uData.credits)),
                            div({ className: 'flex-1' }, p({ className: 'text-xs text-brand mb-1 font-bold' }, '\uD83D\uDCC8 総生成回数'), p({ className: 'text-2xl font-black text-white' }, (uData.usage && uData.usage.count) || 0))
                        ),
                        div({ className: 'p-5 bg-white/5 border border-white/10 rounded-2xl' },
                            div({ className: 'flex justify-between items-center mb-4' },
                                h4({ className: 'text-sm font-bold text-white flex items-center gap-2' }, '\uD83D\uDC64 プロフィール情報'),
                                uData.changeRequest ? span({ className: 'text-xs bg-brand-accent/20 text-brand-accent px-2 py-1 rounded-lg font-bold' }, '\uD83D\uDCDD 管理者へ変更申請中') :
                                button({ onClick: () => setShowReqForm(!showReqForm), className: 'text-xs text-brand hover:text-brand-light font-bold underline' }, showReqForm ? 'キャンセル' : '変更を申請する')
                            ),
                            showReqForm && !uData.changeRequest ? div({ className: 'mb-4 p-4 bg-black/30 rounded-xl border border-white/5 animate-in' },
                                p({ className: 'text-xs text-slate-400 mb-3' }, 'アカウント名とSNSの変更は管理者の承認が必要です。'),
                                input({ className: 'input-base !py-2 text-sm mb-2', placeholder: '新しいアカウント名', value: reqNickname, onChange: e => setReqNickname(e.target.value) }),
                                input({ className: 'input-base !py-2 text-sm font-mono mb-3', placeholder: '新しい連携SNS (@ユーザー名)', value: reqSns, onChange: e => setReqSns(e.target.value) }),
                                button({ onClick: () => {
                                    if(!reqNickname.trim() || !reqSns.trim()) { alert('入力してください'); return; }
                                    const ndb = AppDB.get();
                                    ndb.users[user].changeRequest = { nickname: reqNickname, sns: reqSns };
                                    AppDB.save(ndb); setDb(ndb); setShowReqForm(false); showToast('変更申請を送信しました。');
                                }, className: 'w-full btn-gradient py-2 rounded-lg text-sm font-bold' }, '管理者に申請を送信')
                            ) : null,
                            div({ className: 'mb-3' },
                                label({ className: 'block text-xs font-bold text-slate-500 mb-1' }, 'アカウント表示名'),
                                input({ className: 'input-base !py-2.5 text-sm text-slate-300 bg-black/50 cursor-not-allowed', value: uData.nickname, readOnly: true })
                            ),
                            div({},
                                label({ className: 'block text-xs font-bold text-slate-500 mb-1' }, '連携SNSアカウント'),
                                input({ className: 'input-base !py-2.5 text-sm font-mono text-slate-300 bg-black/50 cursor-not-allowed', value: uData.sns || '', readOnly: true })
                            )
                        ),
                        div({ className: 'p-5 bg-white/5 border border-white/10 rounded-2xl' },
                            h4({ className: 'text-sm font-bold text-white mb-4 flex items-center gap-2' }, '\uD83D\uDD12 パスワード再設定'),
                            input({ type: 'password', className: 'input-base !py-2 text-sm mb-2', placeholder: '現在のパスワード', value: currentPass, onChange: e => setCurrentPass(e.target.value) }),
                            input({ type: 'password', className: 'input-base !py-2 text-sm mb-2', placeholder: '新しいパスワード (6文字以上)', value: newPass, onChange: e => setNewPass(e.target.value) }),
                            input({ type: 'password', className: 'input-base !py-2 text-sm mb-3', placeholder: '新しいパスワード (確認用)', value: newPassConfirm, onChange: e => setNewPassConfirm(e.target.value) }),
                            button({ onClick: () => {
                                if(!uData.password) { alert('初期パスワードが設定されていません。管理者に連絡してください。'); return; }
                                if(currentPass !== uData.password) { alert('現在のパスワードが違います。'); return; }
                                if(newPass.length < 6) { alert('新しいパスワードは6文字以上にしてください。'); return; }
                                if(newPass !== newPassConfirm) { alert('新しいパスワードが一致しません。'); return; }
                                const ndb = AppDB.get(); ndb.users[user].password = newPass; AppDB.save(ndb); setDb(ndb);
                                setCurrentPass(''); setNewPass(''); setNewPassConfirm(''); showToast('パスワードを更新しました！');
                            }, className: 'w-full glass-panel py-2 rounded-lg text-sm font-bold text-white hover:bg-white/10 transition' }, 'パスワードを変更する')
                        ),
                        div({ className: 'p-5 bg-white/5 border border-white/10 rounded-2xl' },
                            h4({ className: 'text-sm font-bold text-white mb-3 flex items-center gap-2' }, '\uD83D\uDCCB 直近のログイン履歴'),
                            uData.loginHistory && uData.loginHistory.length > 0 ? 
                                ul({ className: 'space-y-2' }, uData.loginHistory.map((time, i) => li({ key: i, className: 'text-xs text-slate-400 flex items-center gap-2' }, span({className:'w-2 h-2 rounded-full bg-brand-success'}), time)))
                                : p({ className: 'text-xs text-slate-500' }, '記録がありません')
                        )
                    ),
                    tab === 'data' && div({ className: 'animate-in space-y-6' },
                        div({ className: 'p-5 bg-white/5 border border-white/10 rounded-2xl flex flex-col gap-3' },
                            h4({ className: 'text-sm font-bold text-white mb-2' }, '\uD83D\uDCBE パーソナルデータの管理'),
                            button({ onClick: handleExport, className: 'glass-panel py-3 rounded-xl text-sm font-bold text-white hover:bg-white/10 transition' }, '\uD83D\uDCE5 個人データをダウンロード (JSON)'),
                            div({ className: 'relative w-full' },
                                button({ className: 'w-full glass-panel py-3 rounded-xl text-sm font-bold text-white hover:bg-white/10 transition' }, '\uD83D\uDCE4 個人データを復元 (JSON)'),
                                input({ type: 'file', accept: '.json', onChange: handleImport, className: 'absolute inset-0 w-full h-full opacity-0 cursor-pointer' })
                            )
                        ),
                        div({ className: 'p-5 bg-white/5 border border-white/10 rounded-2xl flex flex-col gap-3' },
                            h4({ className: 'text-sm font-bold text-brand-accent mb-2 flex items-center gap-2' }, '\u26A1 有能神機能ツール'),
                            button({ onClick: () => {
                                if(confirm('ブラウザに自動保存されている最新のシステムバックアップからデータを復元しますか？')) {
                                    const backup = localStorage.getItem('AICP_v70_BACKUP');
                                    if(backup) { localStorage.setItem(DB_KEY, backup); alert('復元しました。ページを再読み込みします。'); window.location.reload(); }
                                    else { alert('バックアップが見つかりません。'); }
                                }
                            }, className: 'glass-panel py-3 rounded-xl text-sm font-bold text-white hover:bg-brand-accent/20 hover:text-brand-accent transition' }, '\uD83D\uDD04 ローカル自動バックアップからシステム復元'),
                            button({ onClick: () => {
                                if(confirm('全ツールの入力内容や生成結果（キャッシュ）をクリアしますか？')) {
                                    const ndb = AppDB.get();
                                    ndb.users[user].projects[uData.curProj].data = {};
                                    AppDB.save(ndb);
                                    alert('キャッシュをクリアしました。ページを再読み込みします。'); window.location.reload();
                                }
                            }, className: 'glass-panel py-3 rounded-xl text-sm font-bold text-white hover:bg-brand-accent/20 hover:text-brand-accent transition' }, '\uD83E\uDDF9 全ツールのキャッシュを一括クリア')
                        ),
                        div({ className: 'pt-4' },
                            button({ onClick: handleDeleteReq, className: 'w-full bg-brand-danger/20 text-brand-danger py-4 rounded-xl text-sm font-bold hover:bg-brand-danger/30 transition' }, '\uD83D\uDEAA アカウント退会（全データ削除）を申請')
                        )
                    )
                ),
                button({ onClick: save, className: 'w-full btn-gradient py-4 rounded-xl font-black mt-6 shadow-xl' }, '設定を保存して閉じる')
            )
        );
    };

    // ================================================================
    // ToolCore - メインツール実行コンポーネント
    // ================================================================
    const ToolCore = ({ tid, user, role, onBack }) => {  
      const conf = TOOLS[tid];  
      const [db, setDb] = useState(AppDB.get());  
      const uData = db.users[user];  
      const userKeys = uData.settings.keys;
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
      const [magicAI, setMagicAI] = useState('openai');
      
      const [trends, setTrends] = useState([]);
      const [urlInput, setUrlInput] = useState('');
      const [keywordInput, setKeywordInput] = useState('');
      const [showAdvancedMagic, setShowAdvancedMagic] = useState(false);
      const [brainstormIdeas, setBrainstormIdeas] = useState([]);
      
      // ▼▼▼ Web同期テンプレート: ローカルJSONファイルへのフォールバックを廃止 ▼▼▼
      const [webTemplates, setWebTemplates] = useState([]);
      const [isLoadingWebTemplates, setIsLoadingWebTemplates] = useState(false);
      
      const fetchWebTemplates = async () => {
          // URLが設定されていない場合は何もしない（ローカルJSONへのフォールバックなし）
          const templateUrl = uData.settings.templateUrl;
          if (!templateUrl || templateUrl.trim() === '') {
              setWebTemplates([]);
              setIsLoadingWebTemplates(false);
              return;
          }
          setIsLoadingWebTemplates(true);
          try {
              const response = await fetch(templateUrl);
              if (!response.ok) throw new Error('HTTP ' + response.status);
              const data = await response.json();
              if (Array.isArray(data)) {
                  setWebTemplates(data);
              } else {
                  setWebTemplates([]);
              }
          } catch(e) {
              console.error("Template fetch error:", e);
              setWebTemplates([]);
          }
          setIsLoadingWebTemplates(false);
      };

      useEffect(() => { 
          const left = document.getElementById('tool-left-panel');
          if (left) left.scrollTop = 0;
          const right = document.getElementById('tool-right-panel');
          if (right) right.scrollTop = 0;
      }, [tid]);  
      
      useEffect(() => {
          fetch('/api/trends').then(r=>r.json()).then(d => {
              if(d.status === 'success') setTrends(d.data);
          }).catch(e=>{});
      }, []);

      useEffect(() => {
          if(tid === 'note') fetchWebTemplates();
      }, [tid]);

      const showToast = (msg) => {
          if(!uData.settings.notifications) return;
          setToast(msg);
          setTimeout(() => setToast(''), 4000);
      };
 
      const updateRes = (v) => {  
        setRes(v);  
        if (role !== 'admin') {  
          const ndb = AppDB.get();  
          if (!ndb.users[user].projects[uData.curProj].data[tid]) ndb.users[user].projects[uData.curProj].data[tid] = {};  
          ndb.users[user].projects[uData.curProj].data[tid].res = v;  
          AppDB.save(ndb);  
        }  
      };  

      // ================================================================
      // フォールバック付きAPI呼び出し（バグ修正: 全プロバイダーを対象に）
      // ================================================================
      const fetchWithFallback = async (endpoint, basePayload, defaultProvider, fallbackProviders) => {
          let tried = [];
          let lastError = '';
          let meaningfulError = ''; 
          // 重複を排除しつつ全プロバイダー順序を構成
          const allProviders = ['openai', 'google', 'anthropic'];
          let order = [defaultProvider].concat(allProviders.filter(p => p !== defaultProvider));

          for (let provider of order) {
              let payload = Object.assign({}, basePayload);
              
              if (endpoint === '/api/auto_generate') {
                  let model = provider === 'anthropic' ? 'claude_free' : provider === 'google' ? 'gemini_free' : 'chatgpt_free';
                  if (basePayload.ai_model && basePayload.ai_model.includes('paid')) {
                      model = model.replace('free', 'paid');
                  }
                  payload.ai_model = model;
                  payload.user_api_key = userKeys[provider];
              } else if (endpoint === '/api/magic_generate') {
                  payload.prompt_instruction = provider;
                  payload.user_keys = { [provider]: userKeys[provider] };
              }

              try {
                  const res = await fetch(endpoint, {
                      method: 'POST', headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify(payload)
                  });
                  const data = await res.json();
                  
                  if (data.status === 'success') {
                      return { success: true, data: data, provider: provider, tried: tried.length };
                  } else {
                      let msg = data.message;
                      if (msg.includes('insufficient_quota') || msg.includes('429')) {
                          msg = 'APIの利用限度額（クレジット残高）が不足しています。チャージするか、別のAPIキーを登録してください。';
                      }
                      if (!data.message.includes('APIキーが設定されていません') && !meaningfulError) {
                          meaningfulError = '[' + provider.toUpperCase() + '] ' + msg;
                      }
                      lastError = msg;
                      tried.push(provider);

                      const isRetryableError = data.message.includes('APIキーが設定されていません') || data.message.includes('insufficient_quota') || data.message.includes('429') || data.message.includes('エラー') || data.message.includes('API key not valid');
                      if (isRetryableError) {
                          if (tried.length < order.length) {
                              showToast('\u26A0\uFE0F ' + provider.toUpperCase() + 'でエラー。別のAIに自動切り替え中...');
                          }
                          continue; 
                      } else { break; }
                  }
              } catch (e) {
                  lastError = '通信エラー: Pythonサーバーと接続できません。';
                  if (!meaningfulError) meaningfulError = '[' + provider.toUpperCase() + '] ' + lastError;
                  tried.push(provider);
              }
          }
          let finalError = meaningfulError || '[' + defaultProvider.toUpperCase() + '] APIキーが設定されていないか、利用できません。設定を確認してください。\n詳細: ' + lastError;
          return { success: false, error: finalError };
      };
 
      // ================================================================
      // 魔法で入力（フォールバックバグ修正済み）
      // ================================================================
      const handleMagic = async (fid, extraParams) => {  
        if (role !== 'admin' && uData.credits <= 0) { setError('クレジット（生成可能回数）が不足しています。'); return; }
        setIsMagicLoading(true); setError('');
        const reqFields = conf.fields.map(f => ({ id: f.id, l: f.l, ph: f.ph||'', val: vals[f.id]||'' }));
        
        let basePayload = { 
            tool_id: tid, 
            fields: reqFields, 
            target_fid: fid,
            url: (extraParams && extraParams.url) || urlInput || '',
            keyword: (extraParams && extraParams.keyword) || null
        };

        // ▼▼▼ バグ修正: fallbackProvidersを全プロバイダーに修正 ▼▼▼
        const result = await fetchWithFallback('/api/magic_generate', basePayload, magicAI, ['openai', 'google', 'anthropic']);

        if (result.success) {
            const data = result.data;
            const ndb = AppDB.get();
            if (role !== 'admin') { ndb.users[user].credits = Math.max(0, (ndb.users[user].credits || 0) - 1); }
            ndb.users[user].usage.count = (ndb.users[user].usage.count || 0) + 1;
            ndb.users[user].usage.tools[tid] = (ndb.users[user].usage.tools[tid] || 0) + 1;
            if(!ndb.users[user].usage.apiCount) ndb.users[user].usage.apiCount = { openai: 0, anthropic: 0, google: 0 };
            ndb.users[user].usage.apiCount[result.provider] = (ndb.users[user].usage.apiCount[result.provider] || 0) + 1;
            
            const newVals = Object.assign({}, vals, data.data);
            setVals(newVals);
            if (role !== 'admin') {  
                if(!ndb.users[user].projects[uData.curProj].data[tid]) ndb.users[user].projects[uData.curProj].data[tid] = {};
                ndb.users[user].projects[uData.curProj].data[tid] = newVals; 
            }
            AppDB.save(ndb);
            if(result.tried > 0) showToast('\uD83D\uDCA1 ' + result.provider.toUpperCase() + 'を使用して魔法を実行しました！');
            else showToast('\uD83D\uDCAB 魔法で全項目を入力しました！');
        } else { 
            setError(result.error); 
            const ldb = AppDB.get(); ldb.errorLogs.unshift({ time: new Date().toLocaleString('ja-JP'), user, tool: 'Magic: '+tid, msg: result.error });
            if(ldb.errorLogs.length > 50) ldb.errorLogs.pop(); AppDB.save(ldb);
        }
        setIsMagicLoading(false);
      };  

      // ================================================================
      // 究極のAI丸投げ機能 - getFinalPrompt（完全リライト）
      // ================================================================
      const getAutoBrowsingMode = () => {
          if (conf.isImagePrompt) return 'none';
          
          const textFields = conf.fields.filter(f => f.t !== 'image' && f.t !== 'check' && f.t !== 'select');
          const filledCount = textFields.filter(f => vals[f.id] && vals[f.id].trim() !== '').length;
          
          if (filledCount === 0) return 'god'; // 完全白紙・神丸投げモード
          if (filledCount < textFields.length) return 'auto'; // 自動補完モード
          return 'full'; // 全項目入力済み
      };

      const getFinalPrompt = () => {
          let promptText = conf.build(vals);
          if (conf.isImagePrompt) return promptText;
          
          // --- 究極のAI丸投げ機能 コア実装 ---
          let emptyFields = [];
          let filledFields = [];
          let mainThemeValue = '';
          const today = new Date().toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
          
          conf.fields.forEach(f => {
              if (f.t === 'image' || f.t === 'check') return; // 画像・チェックは除外
              const val = vals[f.id] || '';
              if (!val || val.trim() === '') {
                  emptyFields.push(f.l);
              } else {
                  filledFields.push({ label: f.l, value: val });
                  if (f.isMainMagic || ['theme', 'topic', 'prod', 'kw'].includes(f.id)) {
                      mainThemeValue = val;
                  }
              }
          });
          
          const isGodMode = filledFields.length === 0; // 完全白紙
          const isAutoMode = emptyFields.length > 0 && !isGodMode; // 部分未入力
          
          let magicBlock = '';
          
          if (isGodMode) {
              // ===== 完全白紙（神丸投げ）モード =====
              magicBlock = `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥【STELLA NOTE - 究極AI丸投げ SYSTEM 発動】🔥
　　　　完全白紙「神丸投げ」モード
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【状況】ユーザーからの入力は一切ありません。
　　　あなた（AI）が全てを考えて最高の出力をしてください。

【必須ステップ① トレンド調査（Web検索必須）】
今すぐ「Web検索（ブラウジング機能）」を使って以下を調査してください：
・${today}現在の日本のX(Twitter)、Instagram、TikTokのトレンド
・Googleトレンドで急上昇中のキーワード（日本）
・noteや個人ブログ界隈で今週バズっているテーマ
・副業・マネー・美容・自己啓発カテゴリの最新需要

【必須ステップ② テーマ選定と宣言】
調査結果から「今最も読者の反応が期待できる1テーマ」を選定し、
出力の冒頭に以下の形式で宣言してください：

▶ 選定テーマ: 「XXXX」
▶ 選定理由: （Web検索で確認したトレンドデータを根拠に1〜2文で説明）
▶ ターゲット読者: （具体的な人物像）

【必須ステップ③ 全項目の自動最適化と執筆】
宣言したテーマに基づいて、このツールの全項目を最適な値に設定し、
最高品質のコンテンツを出力してください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
          } else if (isAutoMode) {
              // ===== 自動補完（テーマ指定）モード =====
              const mainLabel = mainThemeValue ? 'メインテーマ「' + mainThemeValue + '」' : '入力済みの情報';
              magicBlock = `
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟【STELLA NOTE - AI自動補完 SYSTEM 発動】🌟
　　テーマ指定「自動補完」モード
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【状況】${mainLabel}は確定。未入力項目を自動補完してください。

▶ 確定済み入力:
${filledFields.map(f => '　・' + f.label + ': 「' + f.value + '」').join('\n')}

▶ 自動補完が必要な項目:
${emptyFields.map(f => '　・【' + f + '】').join('\n')}

【必須アクション：Web検索による最適補完（${today}時点）】
必ず「Web検索（ブラウジング機能）」を使用して以下を調査し、
未入力項目を最適な内容で補完してください：

1. ${mainLabel}に関する日本での最新トレンド・需要・市場規模
2. このテーマで最もスコアを稼ぐターゲット読者の悩み・欲求
3. 競合コンテンツの傾向と差別化できるポイント
4. 効果的な価格帯・訴求軸

【補完の注意事項】
・単なる推測ではなく、Web検索結果に基づいた根拠ある内容にすること
・海外情報は日本の文化・市場・SNS文脈に合わせてローカライズすること
・直訳・コピーではなく、読者が直感的に理解できる表現に変換すること

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`;
          }
          
          // 入力値のサマリ（未入力フィールドには補完指示）
          let inputSummary = conf.fields.map(f => {
              if (f.t === 'image') return null;
              const val = vals[f.id];
              
              if (f.t === 'check') {
                  return '【' + f.l + '】\n' + (val ? '有効' : '無効');
              }
              if (f.t === 'select') {
                  return '【' + f.l + '】\n' + (val || (f.opts && f.opts[0]) || '');
              }
              if (!val || val.toString().trim() === '') {
                  return '【' + f.l + '】\n⚡ AI自動補完 → 上記調査結果に基づき最適な内容を設定してください';
              }
              return '【' + f.l + '】\n' + val;
          }).filter(Boolean).join('\n\n');

          let targetAiModel = genMode === 'api' ? aiModel : promptAiModel;
          return getAIPrefix(targetAiModel, uData.settings) + magicBlock + '\n' + promptText + '\n\n' + inputSummary;
      };

      const handleCopyPrompt = () => {
          const promptText = getFinalPrompt();
          copy(promptText, 'prompt');
          const mode = getAutoBrowsingMode();
          if (mode === 'god') showToast('\uD83D\uDD25 神丸投げプロンプトをコピーしました！有料版AIに貼り付けてください。');
          else if (mode === 'auto') showToast('\uD83C\uDF1F 自動補完プロンプトをコピーしました！AIに貼り付けてください。');
          else showToast('\uD83D\uDCCB プロンプトをコピーしました！');
      };

      const handleGenerate = async () => {  
        if (role !== 'admin' && uData.credits <= 0) { setError('クレジット（生成可能回数）が不足しています。'); return; }
        setIsLoading(true); setError('');
        
        let imageBase64 = null;
        if (conf.fields.some(f => f.t === 'image')) {
            imageBase64 = vals['image']; 
            if (!imageBase64) { setError('対象の画像をアップロードしてください。'); setIsLoading(false); return; }
        }

        const fullPrompt = getFinalPrompt();
        const isImage = conf.isImagePrompt;
        
        const endpoint = isImage ? '/api/magic_generate' : '/api/auto_generate';
        const defaultProvider = isImage ? imageAI : (aiModel.includes('claude') ? 'anthropic' : aiModel.includes('gemini') ? 'google' : 'openai');
        
        let basePayload = isImage ? 
            { tool_id: tid, fields: conf.fields.map(f => Object.assign({}, f, {val: vals[f.id]||''})) } :
            { prompt: fullPrompt, image_base64: imageBase64, ai_model: aiModel };

        const result = await fetchWithFallback(endpoint, basePayload, defaultProvider, ['openai', 'google', 'anthropic']);

        if (result.success) {
            const data = result.data;
            const ndb = AppDB.get();
            if (role !== 'admin') { ndb.users[user].credits = Math.max(0, (ndb.users[user].credits || 0) - 1); }
            ndb.users[user].usage.count = (ndb.users[user].usage.count || 0) + 1;
            ndb.users[user].usage.tools[tid] = (ndb.users[user].usage.tools[tid] || 0) + 1;
            if(!ndb.users[user].usage.apiCount) ndb.users[user].usage.apiCount = { openai: 0, anthropic: 0, google: 0 };
            ndb.users[user].usage.apiCount[result.provider] = (ndb.users[user].usage.apiCount[result.provider] || 0) + 1;
            
            setRes(isImage ? data.data : data.result);
            if (role !== 'admin') {
                if (!ndb.users[user].projects[uData.curProj].data[tid]) ndb.users[user].projects[uData.curProj].data[tid] = {};
                ndb.users[user].projects[uData.curProj].data[tid].res = isImage ? data.data : data.result;
            }
            AppDB.save(ndb);
            if(result.tried > 0) showToast('\uD83D\uDCA1 ' + result.provider.toUpperCase() + 'へ切り替えて生成に成功しました！');
            else showToast('\u2728 コンテンツの生成が完了しました！');
        } else { 
            setError(result.error); 
            const ldb = AppDB.get(); ldb.errorLogs.unshift({ time: new Date().toLocaleString('ja-JP'), user, tool: tid, msg: result.error });
            if(ldb.errorLogs.length > 50) ldb.errorLogs.pop(); AppDB.save(ldb);
        }
        setIsLoading(false);
      };  

      const handleModify = async (actionType) => {
          if (role !== 'admin' && uData.credits <= 0) { setError('クレジット（生成可能回数）が不足しています。'); return; }
          setIsLoading(true); setError('');
          let prompt = '';
          
          if (actionType === 'x_thread') prompt = '以下の文章を元に、X(Twitter)でバズるツリー投稿（スレッド形式）を作成してください。\n\n' + res;
          else if (actionType === 'short_vid') prompt = '以下の文章を元に、TikTok/Shorts用のショート動画の台本を作成してください。開始1秒で惹きつけるフックを必ず入れてください。\n\n' + res;
          else if (actionType === 'insta_carousel') prompt = '以下の文章を元に、Instagramのカルーセル投稿（画像スライド7〜10枚程度）の構成を作成してください。\n\n' + res;
          else if (actionType === 'line_msg') prompt = '以下の文章を元に、LINE公式アカウントの配信メッセージを作成してください。URLクリックなどの行動を促す構成にしてください。\n\n' + res;
          else if (actionType === 'voicy') prompt = '以下の文章を元に、音声配信（Voicyやstand.fmなど）用の台本を作成してください。耳で聞いてわかりやすい「話し言葉」に特化させてください。\n\n' + res;
          else if (actionType === 'step_mail') prompt = '以下の文章を元に、メルマガ（ステップメール）の1通分の原稿を作成してください。PASONAの法則を用いて構成にしてください。\n\n' + res;
          else if (actionType === 'seo_blog') prompt = '以下の文章を元に、SEOに特化した網羅的なブログ記事の構成案と本文を作成してください。\n\n' + res;
          else if (actionType === 'pr_release') prompt = '以下の文章を元に、プレスリリースやPR用の公式な文章を作成してください。\n\n' + res;
          else if (actionType === 'catchy') prompt = '以下の文章を、もっとキャッチーで読者の感情を強く揺さぶる（バズりやすい）表現に推敲してください。\n\n' + res;
          else if (actionType === 'simple') prompt = '以下の文章を、専門用語を使わずに「小学生でも理解できる」くらいシンプルでわかりやすい表現に推敲してください。\n\n' + res;
          else if (actionType === 'compliance') prompt = '以下の文章について、炎上リスク、差別的表現、薬機法や景表法違反のリスクがないかコンプライアンスチェックを行い、問題があれば修正した安全な文章を提案してください。\n\n' + res;
          else if (actionType === 'eyecatch_prompt') prompt = '以下の文章の内容を象徴する、MidjourneyやDALL-E 3などの画像生成AI向けの「英語のプロンプト」を1つだけ作成してください。出力は英語のプロンプトテキストのみにしてください。\n\n' + res;
       
          let currentProvider = aiModel.includes('claude') ? 'anthropic' : aiModel.includes('gemini') ? 'google' : 'openai';
          let basePayload = { prompt: prompt, ai_model: aiModel };

          const result = await fetchWithFallback('/api/auto_generate', basePayload, currentProvider, ['openai', 'google', 'anthropic']);
          
          if (result.success) {
              const actionNames = {
                  'x_thread': 'Xツリー投稿', 'short_vid': 'ショート動画台本', 'insta_carousel': 'Instaカルーセル構成',
                  'line_msg': 'LINE配信メッセージ', 'voicy': '音声配信台本', 'step_mail': 'メルマガ原稿',
                  'seo_blog': 'SEOブログ記事', 'pr_release': 'PR文', 'catchy': 'キャッチーに推敲',
                  'simple': 'シンプルに推敲', 'compliance': 'コンプラチェック', 'eyecatch_prompt': 'アイキャッチ画像プロンプト'
              };
              const newRes = res + '\n\n---\n\n### \uD83D\uDD04 追加結果 (' + (actionNames[actionType] || actionType) + ')\n\n' + result.data.result;
              
              const ndb = AppDB.get();
              if(!ndb.users[user].usage.apiCount) ndb.users[user].usage.apiCount = { openai: 0, anthropic: 0, google: 0 };
              ndb.users[user].usage.apiCount[result.provider] = (ndb.users[user].usage.apiCount[result.provider] || 0) + 1;
              AppDB.save(ndb);

              updateRes(newRes);
              if(result.tried > 0) showToast('\uD83D\uDCA1 ' + result.provider.toUpperCase() + 'を使用して推敲が完了しました！');
              else showToast('\u2728 ' + (actionNames[actionType] || '') + ' が完了しました！');
          } else { 
              setError(result.error); 
          }
          setIsLoading(false);
      };
 
      const copy = (text, key) => {
          copyTextToClipboard(text);
          setCopied(Object.assign({}, copied, { [key]: true }));
          setTimeout(() => setCopied(prev => Object.assign({}, prev, { [key]: false })), 2000);
      };

      const handleShare = () => {
          if (!shareCode.trim()) { alert('合言葉を入力してください'); return; }
          const ndb = AppDB.get();
          ndb.sharedPrompts[shareCode] = { tid, vals };
          AppDB.save(ndb);
          showToast('合言葉「' + shareCode + '」で共有しました！');
          setShareCode('');
      };
      
      const handleLoadShare = () => {
          if (!loadCode.trim()) return;
          const ndb = AppDB.get();
          const shared = ndb.sharedPrompts[loadCode];
          if (shared && shared.tid === tid) {
              setVals(shared.vals);
              showToast('合言葉「' + loadCode + '」から復元しました！');
              setLoadCode('');
          } else {
              alert('無効な合言葉か、別のツール用の合言葉です。');
          }
      };

      const handlePartialCopy = (part) => {
          if (!res) return;
          let extract = '';
          try {
              if (part === 'title') {
                  extract = res.split('---【無料エリア】---')[0].replace(/---【タイトル案】---/g, '').trim();
              } else if (part === 'free') {
                  extract = res.split('---【無料エリア】---')[1].split('---【有料エリア】---')[0].trim();
              } else if (part === 'paid') {
                  extract = res.split('---【有料エリア】---')[1].split('---【SEO・ハッシュタグ】---')[0].trim();
              } else if (part === 'seo') {
                  extract = res.split('---【SEO・ハッシュタグ】---')[1].trim();
              }
          } catch (e) {
              extract = '抽出に失敗しました。出力形式が正しくない可能性があります。Rawコピーを使用してください。';
          }
          
          if(extract) {
              copyTextToClipboard(extract);
              setCopied(Object.assign({}, copied, { [part]: true }));
              setTimeout(() => setCopied(prev => Object.assign({}, prev, { [part]: false })), 2000);
              showToast('\uD83D\uDCCB コピーしました！ noteに貼り付けてください。');
          }
      };

      const getScore = () => {
          if (!res || conf.isImagePrompt) return null;
          const len = res.length;
          const time = Math.ceil(len / 500);
          const kanjiMatch = res.match(/[\u4e00-\u9faf]/g);
          const kanjiRatio = kanjiMatch ? Math.round((kanjiMatch.length / len) * 100) : 0;
          let readScore = 100;
          if (kanjiRatio < 15) readScore -= (15 - kanjiRatio) * 2;
          if (kanjiRatio > 35) readScore -= (kanjiRatio - 35) * 2;
          readScore = Math.max(0, Math.min(100, readScore));
          return { len, time, readScore };
      };
      const score = getScore();
      const autoBrowsingMode = getAutoBrowsingMode();

      // ================================================================
      // 丸投げモードバッジ（UI）
      // ================================================================
      const AutoBrowsingBadge = () => {
          if (autoBrowsingMode === 'none' || autoBrowsingMode === 'full') return null;
          
          if (autoBrowsingMode === 'god') {
              return div({ className: 'mb-4 p-4 bg-gradient-to-r from-orange-500/20 to-red-500/20 border border-orange-500/40 rounded-xl animate-in' },
                  div({ className: 'flex items-center gap-2 mb-2' },
                      span({ className: 'text-lg' }, '\uD83D\uDD25'),
                      span({ className: 'text-sm font-black text-orange-300' }, '完全白紙「神丸投げ」モード 発動中'),
                  ),
                  p({ className: 'text-[11px] text-orange-200/80 leading-relaxed' }, '全項目が未入力です。このまま生成すると、AIがWeb検索でトレンドを調査し、テーマ選定から全て自動で行います。有料版（ChatGPT Plus / Claude Pro / Gemini Advanced）での実行を強く推奨します。')
              );
          }
          
          if (autoBrowsingMode === 'auto') {
              return div({ className: 'mb-4 p-3 bg-brand/10 border border-brand/30 rounded-xl animate-in' },
                  div({ className: 'flex items-center gap-2 mb-1' },
                      span({ className: 'text-sm' }, '\uD83C\uDF1F'),
                      span({ className: 'text-xs font-black text-brand-light' }, '自動補完モード 発動中'),
                  ),
                  p({ className: 'text-[10px] text-slate-300 leading-relaxed' }, '一部の項目が未入力です。AIがWeb検索で最新トレンドをリサーチし、未入力項目を自動補完します。')
              );
          }
          return null;
      };

      return div({ className: 'flex flex-col lg:flex-row h-full w-full animate-in relative lg:overflow-hidden' },  
        
        toast && div({ className: 'fixed top-4 lg:top-8 left-1/2 transform -translate-x-1/2 bg-brand text-white px-6 py-3 rounded-full shadow-2xl z-[999] font-bold text-sm animate-in flex items-center gap-2' }, toast),

        div({ id: 'tool-left-panel', className: 'w-full lg:w-[400px] border-b lg:border-b-0 lg:border-r border-white/10 p-6 md:p-8 shrink-0 flex flex-col lg:h-full lg:overflow-y-auto hide-scrollbar' },
          div({ className: 'flex items-center gap-3 mb-8' },
              button({ onClick: onBack, className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-white/10' }, '\u2190'),
              h2({ className: 'text-xl font-black text-white' }, conf.name)
          ),

          // トレンドパネル
          trends.length > 0 && div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl animate-in' },
              h4({ className: 'text-xs font-bold text-brand mb-2 flex items-center gap-2' }, '\uD83D\uDD25 急上昇トレンド・ジャック'),
              div({ className: 'flex flex-wrap gap-2' },
                  trends.map((t, i) => button({ 
                      key: i, 
                      onClick: () => { handleMagic('all', { keyword: 'トレンド: ' + t.title }); }, 
                      className: 'text-[10px] bg-white/10 hover:bg-brand/20 px-3 py-1.5 rounded-lg text-slate-200 transition text-left truncate max-w-full' 
                  }, '\uD83D\uDCC8 ' + t.title))
              ),
              p({ className: 'text-[9px] text-slate-500 mt-2' }, '※クリックするとこのトレンドに乗ったテーマで全項目を自動入力します。')
          ),

          // マジックツールパネル
          div({ className: 'mb-6 p-4 bg-white/5 border border-white/10 rounded-xl' },
              div({ className: 'flex justify-between items-center mb-3' },
                  h4({ className: 'text-xs font-bold text-brand-light flex items-center gap-2' }, '\u2728 神機能マジック・ツール'),
                  div({ className: 'flex items-center gap-2' },
                      el('select', { className: 'input-base !py-1 !px-2 text-xs w-auto h-8', value: magicAI, onChange: e => setMagicAI(e.target.value) },
                          option({ value: 'openai' }, 'ChatGPT'), option({ value: 'anthropic' }, 'Claude'), option({ value: 'google' }, 'Gemini')
                      ),
                      button({ onClick: () => setShowAdvancedMagic(!showAdvancedMagic), className: 'text-[10px] text-slate-400 hover:text-white' }, showAdvancedMagic ? '閉じる' : '展開する')
                  )
              ),
              
              // note用テンプレートパネル（URLが設定されている場合のみ表示）
              tid === 'note' && div({ className: 'mb-4 pt-4 border-t border-white/10' },
                  div({ className: 'flex justify-between items-center mb-2' },
                      h4({ className: 'text-[10px] font-bold text-slate-400' }, '\uD83C\uDF10 Web同期 無限テンプレート'),
                      button({ onClick: fetchWebTemplates, disabled: isLoadingWebTemplates, className: 'text-[10px] text-brand hover:text-brand-light transition' }, isLoadingWebTemplates ? '同期中...' : '\uD83D\uDD04 更新')
                  ),
                  webTemplates.length > 0 ? div({ className: 'space-y-2' },
                      webTemplates.map((temp, i) => button({
                          key: i,
                          onClick: () => {
                              setVals(Object.assign({}, vals, temp.data));
                              showToast('\uD83C\uDFB81 テンプレート「' + temp.title + '」をセットしました！');
                          },
                          className: 'w-full text-left bg-gradient-to-r from-purple-500/10 to-pink-500/10 hover:from-purple-500/30 hover:to-pink-500/30 border border-purple-500/30 text-slate-200 text-xs font-bold py-2 px-3 rounded-lg transition'
                      }, temp.title))
                  ) : div({ className: 'p-3 bg-black/20 rounded-lg border border-dashed border-white/10 text-center' },
                      p({ className: 'text-[10px] text-slate-500 mb-1' }, 'テンプレートが未設定です'),
                      p({ className: 'text-[10px] text-slate-600' }, '個人設定 > ナレッジ > Web連携テンプレートURLを登録してください')
                  )
              ),

              button({ 
                  onClick: () => handleMagic('all'), 
                  disabled: isMagicLoading,
                  className: 'w-full bg-gradient-to-r from-brand-accent to-red-500 text-white text-xs font-bold py-2 rounded-lg shadow-lg hover:brightness-110 transition disabled:opacity-50 mb-2' 
              }, isMagicLoading ? '魔法詠唱中...' : '\uD83D\uDCAB コンテキスト連鎖マジック (全項目を一撃で埋める)'),
              
              showAdvancedMagic && div({ className: 'space-y-3 mt-3 pt-3 border-t border-white/10 animate-in' },
                  div({},
                      label({ className: 'block text-[10px] font-bold text-slate-400 mb-1' }, '\uD83D\uDD17 URLスクレイピング (競合を丸裸にする)'),
                      div({ className: 'flex gap-2' },
                          input({ className: 'input-base !py-1.5 text-xs flex-1', placeholder: '参考URLを入力...', value: urlInput, onChange: e => setUrlInput(e.target.value) }),
                          button({ onClick: () => handleMagic('all'), disabled: !urlInput || isMagicLoading, className: 'glass-panel px-3 rounded-lg text-xs font-bold hover:bg-white/10 disabled:opacity-50' }, '抽出')
                      )
                  ),
                  div({},
                      label({ className: 'block text-[10px] font-bold text-slate-400 mb-1' }, '\uD83D\uDCA1 逆算ブレインストーミング'),
                      div({ className: 'flex gap-2' },
                          input({ className: 'input-base !py-1.5 text-xs flex-1', placeholder: '例: ダイエット、AI...', value: keywordInput, onChange: e => setKeywordInput(e.target.value) }),
                          button({ 
                              onClick: async () => {
                                  if(!keywordInput) return;
                                  setIsMagicLoading(true);
                                  try {
                                      const resp = await fetch('/api/auto_generate', {
                                          method: 'POST', headers: {'Content-Type': 'application/json'},
                                          body: JSON.stringify({ prompt: 'キーワード「' + keywordInput + '」に関連する、バズりやすいコンテンツの切り口・コンセプト案を3つ、箇条書きで短く提案してください。', user_api_key: userKeys.openai, ai_model: 'chatgpt_free' })
                                      });
                                      const data = await resp.json();
                                      if(data.status === 'success') {
                                          const ideas = data.result.split('\n').filter(l => l.trim().length > 0);
                                          setBrainstormIdeas(ideas);
                                      }
                                  } catch(e) {}
                                  setIsMagicLoading(false);
                              }, 
                              disabled: !keywordInput || isMagicLoading, 
                              className: 'glass-panel px-3 rounded-lg text-xs font-bold hover:bg-white/10 disabled:opacity-50' 
                          }, '考案')
                      ),
                      brainstormIdeas.length > 0 && div({ className: 'mt-2 space-y-1' },
                          brainstormIdeas.map((idea, i) => button({
                              key: i,
                              onClick: () => { handleMagic('all', { keyword: idea }); setBrainstormIdeas([]); },
                              className: 'block w-full text-left text-[10px] bg-white/5 hover:bg-brand/20 p-2 rounded text-slate-300 transition'
                          }, idea))
                      )
                  )
              )
          ),

          // 実行モード選択
          div({ className: 'mb-8 pb-6 border-b border-white/10' },
              div({ className: 'mb-4' },
                  label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\u2699\uFE0F 実行モードの選択'),
                  div({ className: 'flex gap-2' },
                      button({ onClick: () => setGenMode('api'), className: 'flex-1 py-2 rounded-lg text-xs font-bold border transition ' + (genMode === 'api' ? 'bg-brand/20 border-brand text-white' : 'bg-black/30 border-white/5 text-slate-400 hover:bg-white/5') }, 'APIで自動生成'),
                      button({ onClick: () => setGenMode('prompt'), className: 'flex-1 py-2 rounded-lg text-xs font-bold border transition ' + (genMode === 'prompt' ? 'bg-brand/20 border-brand text-white' : 'bg-black/30 border-white/5 text-slate-400 hover:bg-white/5') }, 'プロンプトのみ作成')
                  )
              ),
              (genMode === 'prompt' && !conf.isImagePrompt) && div({ className: 'animate-in' },
                  label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83E\uDD16 コピー先のAIバージョンを選択'),
                  el('select', { className: 'input-base !py-2.5 text-sm', value: promptAiModel, onChange: e => setPromptAiModel(e.target.value) },
                      option({ value: 'chatgpt_free' }, 'ChatGPT (無料版)'),
                      option({ value: 'chatgpt_paid' }, 'ChatGPT Plus (有料版) ★推奨'),
                      option({ value: 'claude_free' }, 'Claude (無料版)'),
                      option({ value: 'claude_paid' }, 'Claude Pro (有料版) ★推奨'),
                      option({ value: 'gemini_free' }, 'Gemini (無料版)'),
                      option({ value: 'gemini_paid' }, 'Gemini Advanced (有料版) ★推奨')
                  ),
                  p({ className: 'text-[10px] text-slate-500 mt-2' }, '※有料版を選択するとWeb検索機能を用いた情報取得の指示が追加され、丸投げ機能の精度が大幅に向上します。')
              )
          ),

          // ▼▼▼ 究極のAI丸投げ機能の説明バナー ▼▼▼
          !conf.isImagePrompt && div({ className: 'mb-6 overflow-hidden rounded-xl border border-brand-light/20 animate-in' },
              div({ className: 'bg-gradient-to-r from-brand/20 to-brand-light/10 px-4 py-3 flex items-center gap-2' },
                  span({ className: 'text-sm' }, '\uD83D\uDE80'),
                  span({ className: 'text-xs font-black text-brand-light' }, '究極のAI丸投げ機能 ON')
              ),
              div({ className: 'p-4 bg-black/20' },
                  div({ className: 'flex flex-col gap-2' },
                      div({ className: 'flex items-start gap-2' },
                          span({ className: 'text-[10px] bg-orange-500/20 text-orange-300 font-black px-2 py-0.5 rounded-full shrink-0 mt-0.5' }, '神丸投げ'),
                          p({ className: 'text-[10px] text-slate-300 leading-relaxed' }, '全項目を未入力のまま生成 → AIがWebでトレンドを調査し、テーマから全て自動決定')
                      ),
                      div({ className: 'flex items-start gap-2' },
                          span({ className: 'text-[10px] bg-brand/20 text-brand-light font-black px-2 py-0.5 rounded-full shrink-0 mt-0.5' }, '自動補完'),
                          p({ className: 'text-[10px] text-slate-300 leading-relaxed' }, 'テーマだけ入力して生成 → AIがWebでリサーチし、残りを最適化')
                      )
                  )
              )
          ),

          // フォーム入力エリア
          div({ className: 'space-y-6 flex-1' }, 
              conf.fields.map(f => el(FormInput, { 
                  key: f.id, f, val: vals[f.id], 
                  onChange: (id, v) => {
                      const nv = Object.assign({}, vals, { [id]: v });
                      setVals(nv);
                      if (role !== 'admin') {  
                          const ndb = AppDB.get(); ndb.users[user].projects[uData.curProj].data[tid] = nv; AppDB.save(ndb);  
                      }
                  }, onMagic: handleMagic, isMagicLoading 
              }))
          ),

          // 丸投げモードバッジ
          el(AutoBrowsingBadge),

          button({ onClick: () => { setVals({}); updateRes(''); setError(''); setUrlInput(''); setKeywordInput(''); setBrainstormIdeas([]); }, className: 'text-xs text-slate-500 hover:text-white mt-4 w-full text-right' }, '\uD83D\uDDD1\uFE0F クリア'),

          conf.isImagePrompt && div({ className: 'mt-8 pt-6 border-t border-white/10' },
              label({ className: 'block text-xs font-bold text-slate-400 mb-2' }, '\uD83D\uDD2E プロンプトを作成するAIを選択 (BYOK)'),
              div({ className: 'flex gap-2' },
                  ['openai', 'anthropic', 'google'].map(p => button({
                      key: p, onClick: () => setImageAI(p),
                      className: 'flex-1 py-2 rounded-lg text-xs font-bold border transition ' + (imageAI === p ? 'bg-brand/20 border-brand text-white' : 'bg-black/30 border-white/5 text-slate-400 hover:bg-white/5')
                  }, p.toUpperCase()))
              )
          ),

          (genMode === 'api' || !conf.isImagePrompt) && label({ className: 'flex items-center gap-3 cursor-pointer p-3 bg-white/5 rounded-xl mt-4 border border-white/10' },   
              div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition shrink-0' }, div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (abTest ? 'bg-brand left-5' : 'bg-gray-400') })),  
              el('input', { type: 'checkbox', className: 'hidden', checked: abTest, onChange: e => setAbTest(e.target.checked) }),  
              span({ className: 'text-xs font-bold text-slate-300' }, '\u2696\uFE0F A/Bテスト（2パターン同時に出力する）')  
          ),

          // 生成ボタン
          div({ className: 'flex flex-col gap-3 mt-8 pt-6 border-t border-white/10' },
              button({ 
                  onClick: genMode === 'api' ? handleGenerate : handleCopyPrompt, 
                  disabled: isLoading || isMagicLoading, 
                  className: 'w-full btn-gradient py-4 rounded-xl font-black text-lg flex items-center justify-center gap-3 shadow-xl shadow-brand/20' 
              }, 
                  isLoading ? [el(LoadingCircle), '魔法をかけています...'] :
                  (genMode === 'api' 
                      ? ['\u2728 ' + (conf.isImagePrompt ? '呪文' : 'コンテンツ') + 'を全自動生成 (API)']
                      : ['\uD83D\uDCCB ' + (autoBrowsingMode === 'god' ? '神丸投げプロンプトをコピー' : autoBrowsingMode === 'auto' ? '自動補完プロンプトをコピー' : 'プロンプトをコピー')])
              )
          ),
          
          div({ className: 'mt-6 p-4 bg-white/5 rounded-xl border border-white/10 text-sm animate-in' },
              h4({ className: 'text-xs font-bold text-slate-400 mb-3 flex items-center gap-2' }, '\uD83E\uDD1D 合言葉で設定を共有・復元'),
              div({ className: 'flex flex-col gap-3' },
                  div({ className: 'flex gap-2' },
                      input({ className: 'input-base !py-2 text-xs flex-1', placeholder: '合言葉を入力して保存', value: shareCode, onChange: e => setShareCode(e.target.value) }),
                      button({ onClick: handleShare, className: 'glass-panel px-3 rounded-lg text-xs font-bold hover:bg-white/10 whitespace-nowrap' }, '保存')
                  ),
                  div({ className: 'flex gap-2' },
                      input({ className: 'input-base !py-2 text-xs flex-1', placeholder: '合言葉で復元', value: loadCode, onChange: e => setLoadCode(e.target.value) }),
                      button({ onClick: handleLoadShare, className: 'glass-panel px-3 rounded-lg text-xs font-bold hover:bg-white/10 whitespace-nowrap' }, '復元')
                  )
              )
          ),
          error && div({ className: 'mt-4' }, el(ErrorAlert, { msg: error }))
        ),

        // 右パネル（プレビュー）
        div({ id: 'tool-right-panel', className: 'flex-1 bg-black p-6 md:p-10 min-h-[500px] lg:min-h-0 lg:h-full lg:overflow-y-auto hide-scrollbar' },
            res ? div({ className: 'animate-in flex flex-col h-full' },
                div({ className: 'flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-4' },
                    h3({ className: 'text-sm font-black text-slate-400 uppercase tracking-wider' }, '\uD83D\uDC40 プレビュー (生成結果)'),
                    div({ className: 'flex gap-2' },
                        button({ onClick: () => copy(res, 'raw'), className: 'glass-panel px-4 py-2 rounded-lg text-xs font-bold transition ' + (copied.raw ? 'text-brand-success' : 'text-slate-300') }, copied.raw ? '\u2713' : '\uD83D\uDCCB Rawコピー'),
                        !conf.isImagePrompt && button({ onClick: () => {
                            const elNode = document.getElementById('preview-content');
                            if(elNode) {
                                const range = document.createRange(); range.selectNodeContents(elNode);
                                const sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
                                try { document.execCommand('copy'); copy('', 'rich'); } catch(e){}
                                sel.removeAllRanges(); 
                            }
                        }, className: 'btn-gradient px-4 py-2 rounded-lg text-xs font-bold transition ' + (copied.rich ? 'border-brand-success' : '') }, copied.rich ? '\u2713 コピー済' : '\uD83D\uDCCB 装飾コピー')
                    )
                ),
                
                (tid === 'note' && res) && div({ className: 'flex flex-wrap gap-2 mb-4 p-3 bg-brand/10 border border-brand/20 rounded-xl animate-in items-center' },
                    span({ className: 'text-xs font-bold text-brand mr-1' }, '\u2702\uFE0F note個別コピー:'),
                    button({ onClick: () => handlePartialCopy('title'), className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold transition ' + (copied.title ? 'bg-brand-success/20 text-brand-success border-brand-success' : 'text-white hover:bg-white/10') }, copied.title ? '\u2713 コピー済' : 'タイトル案'),
                    button({ onClick: () => handlePartialCopy('free'), className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold transition ' + (copied.free ? 'bg-brand-success/20 text-brand-success border-brand-success' : 'text-white hover:bg-white/10') }, copied.free ? '\u2713 コピー済' : '無料エリア'),
                    button({ onClick: () => handlePartialCopy('paid'), className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold transition ' + (copied.paid ? 'bg-brand-success/20 text-brand-success border-brand-success' : 'text-white hover:bg-white/10') }, copied.paid ? '\u2713 コピー済' : '有料エリア'),
                    button({ onClick: () => handlePartialCopy('seo'), className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold transition ' + (copied.seo ? 'bg-brand-success/20 text-brand-success border-brand-success' : 'text-white hover:bg-white/10') }, copied.seo ? '\u2713 コピー済' : 'SEO・タグ')
                ),

                score && div({ className: 'flex flex-wrap gap-3 mb-4 animate-in' },
                    div({ className: 'bg-white/5 px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2' }, span({ className: 'text-xs text-slate-400' }, '文字数:'), span({ className: 'text-sm font-bold text-white' }, score.len)),
                    div({ className: 'bg-white/5 px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2' }, span({ className: 'text-xs text-slate-400' }, '読了目安:'), span({ className: 'text-sm font-bold text-white' }, '約' + score.time + '分')),
                    div({ className: 'bg-white/5 px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2' }, span({ className: 'text-xs text-slate-400' }, '読みやすさ:'), span({ className: 'text-sm font-bold ' + (score.readScore >= 80 ? 'text-brand-success' : score.readScore >= 50 ? 'text-brand-accent' : 'text-brand-danger') }, score.readScore + '点'))
                ),
                div({ id: 'preview-content', className: 'bg-white p-6 md:p-8 rounded-2xl shadow-inner flex-1 overflow-x-auto ' + (conf.isImagePrompt ? 'font-mono text-sm text-black whitespace-pre-wrap bg-gray-100' : 'preview-content text-black') }, 
                    conf.isImagePrompt ? res : div({ dangerouslySetInnerHTML: renderMarkdown(res) })
                ),
                !conf.isImagePrompt && div({ className: 'mt-6 space-y-4' },
                    div({ className: 'p-4 bg-white/5 border border-white/10 rounded-2xl' },
                        h4({ className: 'text-xs font-bold text-brand mb-3 flex items-center gap-2' }, '\uD83E\uDDD1\u200D\uD83C\uDFEB AI自動推敲（赤ペン先生）'),
                        div({ className: 'flex flex-wrap gap-2' },
                            button({ onClick: () => handleModify('catchy'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand/20 transition disabled:opacity-50' }, '\u2728 もっとキャッチーに'),
                            button({ onClick: () => handleModify('simple'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand/20 transition disabled:opacity-50' }, '\uD83D\uDC76 小学生でもわかるように'),
                            button({ onClick: () => handleModify('compliance'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand/20 transition disabled:opacity-50' }, '\uD83D\uDEA8 コンプラ・炎上チェック'),
                            button({ onClick: () => handleModify('eyecatch_prompt'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-brand-accent hover:text-white hover:bg-brand-accent/20 transition disabled:opacity-50' }, '\uD83D\uDDBC\uFE0F アイキャッチ生成プロンプトを作成')
                        )
                    ),
                    div({ className: 'p-4 bg-white/5 border border-white/10 rounded-2xl' },
                        h4({ className: 'text-xs font-bold text-brand-light mb-3 flex items-center gap-2' }, '\uD83D\uDD04 ワンクリック・マルチ展開'),
                        div({ className: 'flex flex-wrap gap-2' },
                            button({ onClick: () => handleModify('x_thread'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, 'X(Twitter)ツリー'),
                            button({ onClick: () => handleModify('short_vid'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, 'ショート動画'),
                            button({ onClick: () => handleModify('insta_carousel'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, 'Instagramカルーセル'),
                            button({ onClick: () => handleModify('line_msg'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, 'LINE配信'),
                            button({ onClick: () => handleModify('voicy'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-lg text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, '音声配信(Voicy等)'),
                            button({ onClick: () => handleModify('step_mail'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, 'メルマガ'),
                            button({ onClick: () => handleModify('seo_blog'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, 'SEOブログ'),
                            button({ onClick: () => handleModify('pr_release'), disabled: isLoading, className: 'glass-panel px-3 py-1.5 rounded-xl text-xs font-bold text-slate-300 hover:text-white hover:bg-brand-light/20 transition disabled:opacity-50' }, 'PR・プレスリリース')
                        )
                    )
                )
            ) : div({ className: 'flex flex-col h-full' },
                div({ className: 'flex-1 flex flex-col items-center justify-center text-center p-10' },
                    div({ className: 'text-slate-600 mb-8' },
                        div({ className: 'text-6xl mb-4' }, conf.icon),
                        div({ className: 'font-bold' }, '左側のフォームを入力して'),
                        div({ className: 'font-bold' }, '「全自動生成」または「プロンプトコピー」を選択してください')
                    ),
                    div({ className: 'w-full max-w-2xl bg-white/5 p-6 rounded-2xl border border-white/10 animate-in' },
                        h4({ className: 'text-sm font-bold text-white mb-3 flex items-center gap-2 justify-center' }, '\uD83D\uDCDD Web版AIで生成したテキストを貼り付けて反映'),
                        textarea({ className: 'input-base min-h-[150px] text-xs mb-3', placeholder: 'Web版AIなどで手動生成した結果をここに貼り付けてください...', value: manualInput, onChange: e => setManualInput(e.target.value) }),
                        button({ onClick: () => { if(manualInput.trim()) { updateRes(manualInput); setManualInput(''); } }, className: 'w-full btn-gradient py-3 rounded-xl text-sm font-bold shadow-lg' }, '結果をプレビューに反映して保存')
                    )
                )
            )
        )
      );
    };  
 
    const AdminDashboard = ({ user }) => {
        const [db, setDb] = useState(AppDB.get());
        const [toast, setToast] = useState('');
        const [tab, setTab] = useState('users'); 
        const [actionModal, setActionModal] = useState(null);
        const [ann, setAnn] = useState(db.config.announcement);
        const [popupMsg, setPopupMsg] = useState(db.config.popupMessage || '');
        const [ic, setIc] = useState('');
        
        const [adminOpenAI, setAdminOpenAI] = useState('');
        const [adminGoogle, setAdminGoogle] = useState('');
        const [adminAnthropic, setAdminAnthropic] = useState('');

        const showToast = (msg) => { setToast(msg); setTimeout(() => setToast(''), 3000); };

        const handleSaveAdminKeys = async () => {
            try {
                const res = await fetch('/api/admin/update_keys', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ openai_api_key: adminOpenAI, anthropic_api_key: adminAnthropic, google_api_key: adminGoogle })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast('システム共通APIキーを安全に保存しました！');
                    setAdminOpenAI(''); setAdminGoogle(''); setAdminAnthropic('');
                } else {
                    alert('エラー: ' + data.message);
                }
            } catch(e) {
                alert('APIキーの保存に失敗しました。サーバーとの通信を確認してください。');
            }
        };

        const handleStatus = (username, newStatus) => {
            const ndb = Object.assign({}, db); ndb.users[username].status = newStatus; AppDB.save(ndb); setDb(ndb); showToast('ステータスを更新しました');
        };

        const handleResetPass = (username) => {
            if(confirm('本当にパスワードをリセットしますか？')) {
                const newPass = Math.random().toString(36).substring(2, 8);
                const ndb = Object.assign({}, db); ndb.users[username].password = newPass; AppDB.save(ndb); setDb(ndb);
                alert(username + ' の新しいパスワード: ' + newPass + '\n※ユーザーにこのパスワードをお伝えください。');
            }
        };

        const handleDelete = (username) => {
            if(confirm(username + ' を完全に削除しますか？この操作は取り消せません。')) {
                const ndb = Object.assign({}, db); delete ndb.users[username]; AppDB.save(ndb); setDb(ndb); showToast('削除しました。');
            }
        };

        const handleExport = () => {
            const blob = new Blob([localStorage.getItem(DB_KEY)], {type: "application/json"});
            const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href = url;
            a.download = 'aicp_backup_' + new Date().toISOString().slice(0,10) + '.json'; a.click(); URL.revokeObjectURL(url);
        };

        const handleImport = (e) => {
            const file = e.target.files[0]; if(!file) return;
            const reader = new FileReader();
            reader.onload = (ev) => {
                try { const imported = JSON.parse(ev.target.result); AppDB.save(imported); setDb(imported); showToast('復元が完了しました。'); } 
                catch(err) { alert('ファイルの読み込みに失敗しました。'); }
            };
            reader.readAsText(file);
        };

        const ActionModalWrapper = () => {
            if (!actionModal) return null;
            const { type, target, value } = actionModal;
            
            return div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4 animate-in' },
                div({ className: 'glass-panel p-8 rounded-3xl w-full max-w-lg relative flex flex-col max-h-[80vh]' },
                    type === 'credits' && div({},
                        h3({ className: 'text-lg font-bold text-white mb-4' }, '\uD83E\uDE99 クレジット付与/編集 (' + target + ')'),
                        p({ className: 'text-sm text-slate-400 mb-2' }, 'ユーザーに付与する残り生成回数を入力してください。'),
                        input({ type: 'number', className: 'input-base mb-6', value: value, onChange: e => setActionModal(Object.assign({}, actionModal, { value: e.target.value })) }),
                        div({ className: 'flex gap-3' },
                            button({ onClick: () => setActionModal(null), className: 'flex-1 glass-panel py-3 rounded-xl font-bold text-white hover:bg-white/10' }, 'キャンセル'),
                            button({ onClick: () => { const ndb = Object.assign({}, db); ndb.users[target].credits = parseInt(value, 10); AppDB.save(ndb); setDb(ndb); setActionModal(null); showToast('更新しました。'); }, className: 'flex-1 btn-gradient py-3 rounded-xl font-bold' }, '保存する')
                        )
                    ),
                    type === 'perms' && div({ className: 'flex flex-col h-full' },
                        h3({ className: 'text-lg font-bold text-white mb-4 shrink-0' }, '\uD83D\uDD10 ツール権限設定 (' + target + ')'),
                        p({ className: 'text-sm text-slate-400 mb-4 shrink-0' }, 'チェックを外すと、そのユーザーはツールを使用できなくなります。'),
                        div({ className: 'overflow-y-auto hide-scrollbar flex-1 mb-6 space-y-4' },
                            CATEGORIES.map(cat => div({ key: cat.id },
                                h4({ className: 'text-xs font-bold text-brand uppercase mb-2 mt-4' }, cat.name),
                                Object.keys(TOOLS).filter(k=>TOOLS[k].cat===cat.id).map(tid2 => label({ key: tid2, className: 'flex items-center gap-3 p-2 bg-white/5 rounded-lg mb-1 cursor-pointer hover:bg-white/10' },
                                    el('input', { type: 'checkbox', checked: value[tid2] !== false, onChange: e => setActionModal(Object.assign({}, actionModal, { value: Object.assign({}, value, { [tid2]: e.target.checked }) })) }),
                                    span({ className: 'text-sm text-slate-200' }, TOOLS[tid2].name)
                                ))
                            ))
                        ),
                        div({ className: 'flex gap-3 shrink-0' },
                            button({ onClick: () => setActionModal(null), className: 'flex-1 glass-panel py-3 rounded-xl font-bold text-white hover:bg-white/10' }, 'キャンセル'),
                            button({ onClick: () => { const ndb = Object.assign({}, db); ndb.users[target].perms = value; AppDB.save(ndb); setDb(ndb); setActionModal(null); showToast('更新しました。'); }, className: 'flex-1 btn-gradient py-3 rounded-xl font-bold' }, '権限を保存する')
                        )
                    ),
                    type === 'change_req' && div({},
                        h3({ className: 'text-lg font-bold text-white mb-4' }, '\uD83D\uDCDD プロフィール変更申請 (' + target + ')'),
                        p({ className: 'text-sm text-slate-400 mb-4' }, 'ユーザーから以下のプロフィール変更申請が届いています。'),
                        div({ className: 'bg-white/5 p-4 rounded-xl mb-6' },
                            div({ className: 'mb-2' }, span({ className: 'text-xs text-slate-500 inline-block w-24' }, '現在のアカウント名:'), span({ className: 'text-sm text-white line-through' }, db.users[target].nickname)),
                            div({ className: 'mb-4' }, span({ className: 'text-xs text-brand font-bold inline-block w-24' }, '新アカウント名:'), span({ className: 'text-sm font-bold text-brand-light' }, value.nickname)),
                            div({ className: 'mb-2' }, span({ className: 'text-xs text-slate-500 inline-block w-24' }, '現在のSNS:'), span({ className: 'text-sm text-white line-through' }, db.users[target].sns)),
                            div({ className: 'mb-2' }, span({ className: 'text-xs text-brand font-bold inline-block w-24' }, '新しいSNS:'), span({ className: 'text-sm font-bold text-brand-light' }, value.sns))
                        ),
                        div({ className: 'flex gap-3' },
                            button({ onClick: () => { const ndb=Object.assign({}, db); delete ndb.users[target].changeRequest; AppDB.save(ndb); setDb(ndb); setActionModal(null); showToast('申請を拒否しました。'); }, className: 'flex-1 glass-panel py-3 rounded-xl font-bold text-white hover:bg-white/10' }, '拒否して消去'),
                            button({ onClick: () => { 
                                const ndb=Object.assign({}, db); 
                                ndb.users[target].nickname = value.nickname;
                                ndb.users[target].sns = value.sns;
                                delete ndb.users[target].changeRequest;
                                AppDB.save(ndb); setDb(ndb); setActionModal(null); showToast('承認して反映しました。'); 
                            }, className: 'flex-1 btn-gradient py-3 rounded-xl font-bold' }, '承認して反映')
                        )
                    )
                )
            );
        };

        const renderUsers = () => {
            const users = Object.keys(db.users).filter(k => k !== 'admin');
            return div({ className: 'glass-panel rounded-2xl overflow-hidden' },
                div({ className: 'overflow-x-auto hide-scrollbar' },
                    table({ className: 'w-full text-left min-w-[800px]' },
                        thead({}, tr({ className: 'border-b border-white/10 bg-white/5' }, th({className:'p-4 text-xs font-bold text-slate-400'}, 'ユーザー名 / SNS'), th({className:'p-4 text-xs font-bold text-slate-400'}, '状態 / ログイン'), th({className:'p-4 text-xs font-bold text-slate-400'}, '利用状況'), th({className:'p-4 text-xs font-bold text-slate-400 w-[300px]'}, '管理操作'))),
                        tbody({}, users.map(u => tr({ key: u, className: 'border-b border-white/5 hover:bg-white/5 transition' },
                            td({ className: 'p-4' }, 
                                div({ className: 'font-bold text-white text-sm' }, u), 
                                div({ className: 'text-xs text-slate-500' }, db.users[u].sns),
                                db.users[u].usedInviteCode && span({ className: 'text-[10px] bg-brand-light/20 text-brand-light px-2 py-0.5 rounded-full mt-1 inline-block' }, '招待コード: ' + db.users[u].usedInviteCode)
                            ),
                            td({ className: 'p-4' }, 
                                span({ className: 'text-[10px] font-black px-2 py-0.5 rounded-full ' + (db.users[u].status==='approved'?'bg-brand-success/20 text-brand-success':db.users[u].status==='pending'?'bg-brand-accent/20 text-brand-accent':'bg-brand-danger/20 text-brand-danger') }, db.users[u].status.toUpperCase()),
                                div({ className: 'text-[10px] text-slate-500 mt-1' }, db.users[u].lastLogin)
                            ),
                            td({ className: 'p-4' }, 
                                div({ className: 'text-xs text-slate-300 font-bold' }, '\uD83E\uDE99 ' + db.users[u].credits),
                                div({ className: 'text-[10px] text-slate-500' }, '生成: ' + db.users[u].usage.count + '回')
                            ),
                            td({ className: 'p-4 flex flex-wrap gap-1' }, 
                                db.users[u].changeRequest && button({ onClick:()=>setActionModal({type:'change_req', target:u, value:db.users[u].changeRequest}), className: 'px-2 py-1 bg-brand-accent text-white rounded text-[10px] font-bold hover:bg-brand-accent/80 shadow-lg shadow-brand-accent/30 animate-pulse' }, '変更申請あり'),
                                db.users[u].status === 'pending' ? button({ onClick:()=>handleStatus(u,'approved'), className: 'px-2 py-1 bg-brand-success/20 text-brand-success rounded text-[10px] font-bold hover:bg-brand-success/30' }, '承認') :
                                db.users[u].status === 'delete_requested' ? button({ onClick:()=>handleDelete(u), className: 'px-2 py-1 bg-brand-danger text-white rounded text-[10px] font-bold hover:bg-brand-danger/80 shadow-lg shadow-brand-danger/30' }, '退会処理') :
                                db.users[u].status === 'suspended' ? button({ onClick:()=>handleStatus(u,'approved'), className: 'px-2 py-1 bg-slate-700 text-white rounded text-[10px] font-bold hover:bg-slate-600' }, '凍結解除') :
                                button({ onClick:()=>handleStatus(u,'suspended'), className: 'px-2 py-1 bg-brand-accent/20 text-brand-accent rounded text-[10px] font-bold hover:bg-brand-accent/30' }, '凍結'),
                                button({ onClick:()=>setActionModal({type:'perms', target:u, value:db.users[u].perms||{}}), className: 'px-2 py-1 bg-brand/20 text-brand-light rounded text-[10px] font-bold hover:bg-brand/30' }, '権限'),
                                button({ onClick:()=>setActionModal({type:'credits', target:u, value:db.users[u].credits}), className: 'px-2 py-1 bg-purple-500/20 text-purple-400 rounded text-[10px] font-bold hover:bg-purple-500/30' }, '\uD83E\uDE99'),
                                button({ onClick:()=>handleResetPass(u), className: 'px-2 py-1 bg-slate-700 text-white rounded text-[10px] font-bold hover:bg-slate-600' }, 'パス変'),
                                button({ onClick:()=>handleDelete(u), className: 'px-2 py-1 bg-brand-danger/20 text-brand-danger rounded text-[10px] font-bold hover:bg-brand-danger/30' }, '削除')
                            )
                        )))
                    )
                )
            );
        };

        const renderAnalytics = () => {
            let toolCounts = {};
            Object.values(db.users).forEach(u => { if(u.usage && u.usage.tools) Object.entries(u.usage.tools).forEach(function(entry) { toolCounts[entry[0]] = (toolCounts[entry[0]] || 0) + entry[1]; }); });
            const ranking = Object.entries(toolCounts).sort((a,b) => b[1] - a[1]).slice(0, 10);
            return div({ className: 'glass-panel p-8 rounded-2xl' },
                h3({ className: 'text-xl font-bold mb-6 text-white' }, '\uD83C\uDFC6 人気ツール TOP 10'),
                ranking.length === 0 ? p({className:'text-slate-400'}, 'まだ利用データがありません。') :
                table({ className: 'w-full text-left text-sm' },
                    thead({}, tr({ className: 'border-b border-white/10' }, th({className:'p-3 w-16'}, '順位'), th({className:'p-3'}, 'ツール名'), th({className:'p-3 w-24 text-right'}, '利用回数'))),
                    tbody({}, ranking.map(function(entry, i) { const t = TOOLS[entry[0]]; return tr({ key: entry[0], className: 'border-b border-white/5' }, td({className:'p-3 font-bold text-slate-400'}, (i+1) + '位'), td({className:'p-3'}, span({className:'mr-2 text-lg'}, t ? t.icon : '\uD83D\uDD27'), t ? t.name : entry[0]), td({className:'p-3 text-right font-bold text-brand'}, entry[1])); }))
                )
            );
        };

        const renderSystem = () => {
            return div({ className: 'space-y-6' },
                div({ className: 'glass-panel p-8 rounded-2xl' },
                    h3({ className: 'text-lg font-bold text-white mb-4' }, '\uD83D\uDD11 システム共通APIキー登録'),
                    p({ className: 'text-sm text-slate-400 mb-4' }, 'ユーザーが個人設定でAPIキーを登録していない場合に、システム側で肩代わりするAPIキーを設定します。'),
                    div({ className: 'space-y-3 mb-4' },
                        input({ type: 'password', className: 'input-base text-sm font-mono', placeholder: 'ChatGPT (OpenAI) APIキー (sk-...)', value: adminOpenAI, onChange: e => setAdminOpenAI(e.target.value) }),
                        input({ type: 'password', className: 'input-base text-sm font-mono', placeholder: 'Gemini (Google) APIキー (AIza...)', value: adminGoogle, onChange: e => setAdminGoogle(e.target.value) }),
                        input({ type: 'password', className: 'input-base text-sm font-mono', placeholder: 'Claude (Anthropic) APIキー (sk-ant...)', value: adminAnthropic, onChange: e => setAdminAnthropic(e.target.value) })
                    ),
                    button({ onClick: handleSaveAdminKeys, className: 'btn-gradient px-6 py-2 rounded-lg font-bold text-sm' }, 'サーバーに安全に保存する')
                ),
                div({ className: 'glass-panel p-8 rounded-2xl' },
                    h3({ className: 'text-lg font-bold text-white mb-4' }, '\uD83D\uDCE2 ホーム画面お知らせ配信'),
                    textarea({ className: 'input-base min-h-[100px] text-sm mb-4', value: ann, onChange: e => setAnn(e.target.value), placeholder: '全ユーザーのホーム画面トップに表示されます' }),
                    button({ onClick: () => { const ndb = Object.assign({}, db); ndb.config.announcement = ann; AppDB.save(ndb); setDb(ndb); showToast('お知らせを更新しました'); }, className: 'btn-gradient px-6 py-2 rounded-lg font-bold text-sm' }, '配信する')
                ),
                div({ className: 'glass-panel p-8 rounded-2xl' },
                    h3({ className: 'text-lg font-bold text-white mb-4' }, '\uD83D\uDD14 全ユーザー強制ログイン時ポップアップ'),
                    textarea({ className: 'input-base min-h-[100px] text-sm mb-4', value: popupMsg, onChange: e => setPopupMsg(e.target.value), placeholder: '次回ログイン時に全ユーザーに強制的に表示されるメッセージです' }),
                    button({ onClick: () => { const ndb = Object.assign({}, db); ndb.config.popupMessage = popupMsg; ndb.config.popupId = Date.now(); AppDB.save(ndb); setDb(ndb); showToast('強制ポップアップを更新・配信しました'); }, className: 'btn-gradient px-6 py-2 rounded-lg font-bold text-sm' }, '全ユーザーに配信する')
                ),
                div({ className: 'glass-panel p-8 rounded-2xl' },
                    h3({ className: 'text-lg font-bold text-white mb-4' }, '\uD83C\uDF9F\uFE0F 招待コード (1回使い捨て・即時承認)'),
                    div({ className: 'flex gap-2 mb-4' },
                        input({ className: 'input-base text-sm font-mono', value: ic, onChange: e => setIc(e.target.value), placeholder: '新しい招待コードを入力 (例: VIP2024)' }),
                        button({ onClick: () => { if(!ic)return; const ndb=Object.assign({},db); ndb.config.inviteCodes[ic]=true; AppDB.save(ndb); setDb(ndb); setIc(''); showToast('発行しました'); }, className: 'btn-gradient px-6 py-2 rounded-lg font-bold text-sm whitespace-nowrap' }, '発行')
                    ),
                    div({ className: 'flex flex-wrap gap-2' }, Object.keys(db.config.inviteCodes).map(code => div({ key: code, className: 'bg-white/10 px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-2' }, code, button({ onClick: () => { const ndb=Object.assign({},db); delete ndb.config.inviteCodes[code]; AppDB.save(ndb); setDb(ndb); }, className: 'text-brand-danger hover:text-white' }, '\u2715'))))
                ),
                div({ className: 'glass-panel p-8 rounded-2xl' },
                    h3({ className: 'text-lg font-bold text-white mb-4' }, '\uD83D\uDCE6 データベース・バックアップ'),
                    p({ className: 'text-sm text-slate-400 mb-6' }, '全ユーザーデータ、設定、履歴をJSONファイルでダウンロード/復元します。'),
                    div({ className: 'flex gap-4' },
                        button({ onClick: handleExport, className: 'btn-gradient px-6 py-3 rounded-xl font-bold text-sm shadow-lg' }, '\u2B07\uFE0F バックアップをDL'),
                        div({ className: 'relative' },
                            button({ className: 'glass-panel px-6 py-3 rounded-xl font-bold text-sm hover:bg-white/10 transition' }, '\u2B06\uFE0F データを復元'),
                            input({ type: 'file', accept: '.json', onChange: handleImport, className: 'absolute inset-0 w-full h-full opacity-0 cursor-pointer' })
                        )
                    )
                )
            );
        };

        const renderLogs = () => div({ className: 'glass-panel p-6 rounded-2xl overflow-x-auto hide-scrollbar' },
            table({ className: 'w-full text-left min-w-[600px]' },
                thead({}, tr({ className: 'border-b border-white/10 bg-white/5' }, th({className:'p-3 text-xs'}, '日時'), th({className:'p-3 text-xs'}, 'ユーザー'), th({className:'p-3 text-xs'}, 'ツール'), th({className:'p-3 text-xs'}, 'エラー内容'))),
                tbody({}, db.errorLogs.map((log, i) => tr({ key: i, className: 'border-b border-white/5' }, td({className:'p-3 text-[10px] text-slate-400'}, log.time), td({className:'p-3 text-xs font-bold'}, log.user), td({className:'p-3 text-xs'}, log.tool), td({className:'p-3 text-xs text-brand-danger break-all'}, log.msg))))
            )
        );

        return div({ className: 'w-full max-w-6xl mx-auto p-6 md:p-12 animate-in relative' },
            toast && div({ className: 'fixed top-4 lg:top-8 left-1/2 transform -translate-x-1/2 bg-brand text-white px-6 py-3 rounded-full shadow-2xl z-[999] font-bold text-sm animate-in' }, toast),
            el(ActionModalWrapper),
            div({ className: 'mb-8' },
                h1({ className: 'text-4xl font-black text-white mb-3 tracking-tight' }, '\uD83D\uDC51 管理者ダッシュボード'),
                p({ className: 'text-slate-400 text-lg' }, 'SaaSの全データとユーザーをここで管理します。')
            ),
            div({ className: 'flex overflow-x-auto hide-scrollbar gap-2 mb-8 pb-2 border-b border-white/10' },
                ['users', 'analytics', 'system', 'logs'].map(t => button({ key: t, onClick: () => setTab(t), className: 'px-6 py-2.5 rounded-full text-sm font-bold transition whitespace-nowrap ' + (tab === t ? 'bg-brand text-white' : 'glass-panel text-slate-400 hover:text-white hover:bg-white/10') }, t === 'users' ? '\uD83D\uDC65 ユーザー管理' : t === 'analytics' ? '\uD83D\uDCC8 分析・ランキング' : t === 'system' ? '\u2699\uFE0F システム設定' : '\u26A0\uFE0F エラーログ'))
            ),
            tab === 'users' && renderUsers(),
            tab === 'analytics' && renderAnalytics(),
            tab === 'system' && renderSystem(),
            tab === 'logs' && renderLogs()
        );
    };
 
    const MainApp = (props) => {  
      const [screen, setScreen] = useState('home');  
      const [activeCat, setActiveCat] = useState('omega');
      const [showSettings, setShowSettings] = useState(false);
      const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
      const [showPopup, setShowPopup] = useState(false);
      
      const db = AppDB.get();  
      const uData = db.users[props.user];  
 
      useEffect(() => { 
          if(props.role === 'admin') {
              setScreen('admin_dashboard');
          } else if (db.config.popupId && uData.readPopupId !== db.config.popupId) {
              setShowPopup(true);
          }
      }, [props.role]);

      useEffect(() => { 
          const container = document.getElementById('main-scroll-container');
          if (container) container.scrollTop = 0;
      }, [screen, activeCat]);  

      useEffect(() => {
          const t = uData.settings.theme || 'blue';
          const root = document.documentElement;
          if(t === 'purple') {
              root.style.setProperty('--brand', '#a855f7'); root.style.setProperty('--brand-light', '#c084fc'); root.style.setProperty('--brand-dark', '#7e22ce');
          } else if(t === 'emerald') {
              root.style.setProperty('--brand', '#10b981'); root.style.setProperty('--brand-light', '#34d399'); root.style.setProperty('--brand-dark', '#047857');
          } else {
              root.style.setProperty('--brand', '#0ea5e9'); root.style.setProperty('--brand-light', '#38bdf8'); root.style.setProperty('--brand-dark', '#0369a1');
          }
      }, [uData.settings.theme]);

      const openTool = (tid) => {  
        if (tid === 'admin_dashboard') { setScreen('admin_dashboard'); setIsMobileMenuOpen(false); return; }
        const t = TOOLS[tid];
        const isLocked = t.reqLevel && (uData.usage && uData.usage.count || 0) < t.reqLevel && props.role !== 'admin';
        if (isLocked) return alert('\uD83D\uDD12 このツールは生成回数' + t.reqLevel + '回以上の「' + getUserLevel(t.reqLevel).name + '」レベルで解放されます。');

        const isPermitted = props.role === 'admin' || (uData.perms[tid] !== undefined ? uData.perms[tid] : true);  
        if (!isPermitted) return alert('\uD83D\uDD12 このツールは現在管理者によって制限されています。');  
        setScreen(tid);  
        setIsMobileMenuOpen(false);
      };  
 
      const closePopup = () => {
          const ndb = AppDB.get();
          ndb.users[props.user].readPopupId = ndb.config.popupId;
          AppDB.save(ndb);
          setShowPopup(false);
      };

      const ForcePopupModal = () => div({ className: 'fixed inset-0 z-[1000] flex items-center justify-center bg-black/90 p-4 animate-in' },
          div({ className: 'glass-panel rounded-3xl max-w-lg w-full p-8 relative flex flex-col max-h-[80vh] border-brand shadow-2xl shadow-brand/20' },
              h3({ className: 'text-2xl font-black text-white mb-4 pb-4 border-b border-white/10 flex items-center gap-2' }, '\uD83D\uDCE2 重要なお知らせ'),
              div({ className: 'overflow-y-auto flex-1 pr-4 hide-scrollbar text-base text-slate-200 space-y-4 mb-8 leading-relaxed whitespace-pre-wrap font-bold' }, db.config.popupMessage),
              button({ onClick: closePopup, className: 'w-full btn-gradient py-4 rounded-xl font-black shadow-xl text-lg' }, '確認して次へ')
          )
      );

      const userLevel = getUserLevel((uData.usage && uData.usage.count) || 0);

      const Sidebar = () => div({ className: 'fixed lg:relative inset-y-0 left-0 z-50 transform ' + (isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full') + ' lg:translate-x-0 transition-transform duration-300 w-[260px] h-full bg-bg-panel border-r border-white/10 p-6 flex flex-col shrink-0' },
          button({ className: 'lg:hidden absolute top-4 right-4 text-slate-400 hover:text-white text-2xl font-bold', onClick: () => setIsMobileMenuOpen(false) }, '\u2715'),
          div({ className: 'flex items-center gap-2 mb-10 mt-2 lg:mt-0 cursor-pointer', onClick: () => { setScreen('home'); setIsMobileMenuOpen(false); } }, 
              div({ className: 'w-3 h-8 bg-brand rounded-full' }),
              h1({ className: 'text-2xl font-black text-white tracking-tighter' }, 'AICP Pro')
          ),
          div({ className: 'flex-1 space-y-2 overflow-y-auto hide-scrollbar pb-10' },
              props.role === 'admin' && div({ className: 'mb-6' },
                  h2({ className: 'text-[10px] font-black text-brand uppercase tracking-[0.2em] mt-6 mb-2 ml-2' }, '\uD83D\uDC51 管理者メニュー'),
                  button({
                      onClick: () => openTool('admin_dashboard'),
                      className: 'w-full text-left p-3 rounded-lg text-sm font-bold flex items-center gap-3 hover:bg-white/5 transition ' + (screen==='admin_dashboard'?'bg-brand/10 text-white':'text-slate-300')
                  }, span({className:'text-lg'}, '\uD83D\uDEE1\uFE0F'), 'ダッシュボード')
              ),
              
              h2({ className: 'text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mt-6 mb-2 ml-2' }, '\uD83D\uDCE6 ツールカテゴリー'),
              CATEGORIES.map(cat => button({
                  key: cat.id, 
                  onClick: () => { setActiveCat(cat.id); setScreen('home'); setIsMobileMenuOpen(false); },
                  className: 'w-full text-left p-3 rounded-lg text-sm font-bold flex items-center gap-3 hover:bg-white/5 transition ' + (activeCat===cat.id && screen==='home' ? 'bg-brand/10 text-white' : 'text-slate-300')
              }, span({className:'text-lg w-6 text-center'}, cat.id === 'omega' ? '\uD83D\uDD25' : cat.id === 'mon' ? '\uD83D\uDCDD' : cat.id === 'cw' ? '\uD83D\uDCBC' : cat.id === 'sns' ? '\uD83D\uDE80' : cat.id === 'fun' ? '\uD83D\uDCAC' : '\u2728'), cat.name))
          ),
          div({ className: 'mt-auto pt-6 border-t border-white/10 space-y-3 bg-bg-panel' },
              button({ onClick: () => setShowSettings(true), className: 'w-full bg-white/5 hover:bg-white/10 p-3 rounded-lg text-sm font-bold text-slate-300 flex items-center gap-3 transition' }, '\u2699\uFE0F 個人設定'),
              button({ onClick: props.onLogout, className: 'w-full text-left p-3 rounded-lg text-sm font-bold text-slate-500 hover:text-white transition' }, '\uD83D\uDC4B ログアウト')
          )
      );

      const MobileHeader = () => div({ className: 'lg:hidden flex items-center justify-between p-4 bg-bg-panel border-b border-white/10 w-full shrink-0' },
          div({ className: 'flex items-center gap-2 cursor-pointer', onClick: () => { setScreen('home'); setIsMobileMenuOpen(false); } },
              div({ className: 'w-2 h-6 bg-brand rounded-full' }),
              h1({ className: 'text-xl font-black text-white' }, 'AICP Pro')
          ),
          button({ onClick: () => setIsMobileMenuOpen(true), className: 'text-white text-3xl leading-none px-2 pb-1' }, '\u2261')
      );

      return div({ className: 'flex h-full w-full relative overflow-hidden' },  
        showPopup && el(ForcePopupModal),
        isMobileMenuOpen && div({ className: 'fixed inset-0 bg-black/60 z-40 lg:hidden', onClick: () => setIsMobileMenuOpen(false) }),
        el(Sidebar), showSettings && el(UserSettingModal, { user: props.user, onClose: () => setShowSettings(false) }),
        
        div({ className: 'flex-1 flex flex-col min-w-0 h-full bg-bg relative' },
            el(MobileHeader),
            div({ id: 'main-scroll-container', className: 'flex-1 overflow-y-auto hide-scrollbar' },
                screen === 'admin_dashboard' && props.role === 'admin' && el(AdminDashboard, { user: props.user }),
                
                screen === 'home' && div({ className: 'max-w-6xl mx-auto p-6 md:p-12' },
                    db.config.announcement && div({ className: 'mb-8 bg-brand/10 border border-brand/30 p-5 rounded-2xl animate-in' },
                        h3({ className: 'text-brand font-bold mb-2 flex items-center gap-2' }, '\uD83D\uDCE2 管理者からのお知らせ'),
                        p({ className: 'text-sm text-slate-200 whitespace-pre-wrap leading-relaxed' }, db.config.announcement)
                    ),
                    div({ className: 'mb-12 flex flex-col md:flex-row md:justify-between md:items-end gap-6' },
                        div({},
                            h1({ className: 'text-4xl md:text-5xl font-black text-white mb-3 tracking-tight flex items-center gap-3' }, 
                                'こんにちは、' + uData.nickname + 'さん',
                                props.role !== 'admin' && span({ className: 'text-sm px-3 py-1 rounded-full bg-white/5 border ' + userLevel.border + ' ' + userLevel.color }, userLevel.icon + ' ' + userLevel.name)
                            ),
                            p({ className: 'text-slate-400 text-lg' }, '今日はどのコンテンツを作成しますか？使用するツールを選択してください。')
                        ),
                        props.role !== 'admin' && div({ className: 'glass-panel px-6 py-4 rounded-2xl shrink-0 text-center md:text-right border-brand-accent/30' },
                            p({ className: 'text-xs text-slate-400 font-bold mb-1' }, '残り生成枠 (クレジット)'),
                            p({ className: 'text-3xl font-black text-brand-accent' }, '\uD83E\uDE99 ' + (uData.credits || 0))
                        )
                    ),
                    
                    CATEGORIES.filter(c => c.id === activeCat).map(cat => div({ key: 'p-'+cat.id, className: 'mb-12 animate-in' },
                        h2({ className: 'text-2xl font-black text-white mb-6 border-b border-white/10 pb-4' }, cat.name),
                        div({ className: 'grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6' },
                            Object.keys(TOOLS).filter(k=>TOOLS[k].cat===cat.id).map(tid => {
                                const t = TOOLS[tid];
                                const isLocked = t.reqLevel && ((uData.usage && uData.usage.count) || 0) < t.reqLevel && props.role !== 'admin';
                                return div({ key: tid, onClick: () => !isLocked && openTool(tid), className: 'glass-panel p-6 rounded-2xl transition-all group ' + (isLocked ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:-translate-y-1 hover:border-brand/40') },
                                    div({ className: 'flex justify-between items-start mb-4' },
                                        div({ className: 'text-4xl group-hover:scale-110 transition' }, isLocked ? '\uD83D\uDD12' : t.icon),
                                        t.cat==='mon'&&span({className:'bg-brand/10 text-brand text-[10px] font-black px-3 py-1 rounded-full'},'収益化')
                                    ),
                                    h3({ className: 'text-lg font-black text-white mb-2' }, t.name),
                                    p({ className: 'text-xs text-slate-400 leading-relaxed line-clamp-2' }, isLocked ? '※この機能は生成回数' + t.reqLevel + '回以上の「' + getUserLevel(t.reqLevel).name + '」レベルで解放されます。' : t.desc)
                                );
                            })
                        )
                    ))
                ),
                TOOLS[screen] && el(ToolCore, { tid: screen, user: props.user, role: props.role, onBack: () => setScreen('home') })
            )
        )
      );  
    };  
 
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
        setErr(''); setMsg('');
        const db = AppDB.get();  
        if (nickname === db.config.adminU && pass === db.config.adminP) {  
          db.users['admin'].lastLogin = new Date().toLocaleString('ja-JP'); AppDB.save(db);
          localStorage.setItem(SESS_KEY, JSON.stringify({ u: 'admin', r: 'admin' }));  
          props.onLogin('admin', 'admin');  
          return;  
        }  
        if(nickname && db.users[nickname]) {
            if (db.users[nickname].password && db.users[nickname].password !== pass && db.users[nickname].status !== 'pending') {
                setErr('ユーザー名またはパスワードが違います。');
                return;
            }
            if (db.users[nickname].status === 'suspended') {
                setErr('このアカウントは管理者により凍結されています。');
                return;
            }
            if (db.users[nickname].status === 'approved') {
                db.users[nickname].lastLogin = new Date().toLocaleString('ja-JP'); 
                if(!db.users[nickname].loginHistory) db.users[nickname].loginHistory = [];
                db.users[nickname].loginHistory.unshift(db.users[nickname].lastLogin);
                if(db.users[nickname].loginHistory.length > 5) db.users[nickname].loginHistory.pop();
                AppDB.save(db);
                localStorage.setItem('AICP_v70_BACKUP', JSON.stringify(db));
                localStorage.setItem(SESS_KEY, JSON.stringify({ u: nickname, r: 'approved' }));
                props.onLogin(nickname, 'approved');
            } else if (db.users[nickname].status === 'pending') {
                setErr('現在、管理者の承認待ちです。承認されるまでお待ちください。');
            } else if (db.users[nickname].status === 'delete_requested') {
                setErr('このアカウントは退会申請中です。');
            } else {
                setErr('このアカウントは現在利用できません。');
            }
        } else { 
            setErr('ユーザー名またはパスワードが違います。'); 
        }
      };  

      const register = () => {
          setErr(''); setMsg('');
          if (!regUsername.trim() || regUsername.trim() === '@') { setErr('ユーザー名を入力してください。'); return; }
          if (regPass.length < 6) { setErr('パスワードは6文字以上で設定してください。'); return; }
          if (!regAgreed) { setErr('利用規約に同意してください。'); return; }

          const db = AppDB.get();
          if (db.users[regUsername]) { setErr('このユーザー名は既に登録されています。'); return; }
          
          let initialStatus = 'pending';
          if (regInviteCode) {
              if (db.config.inviteCodes[regInviteCode]) {
                  initialStatus = 'approved';
                  delete db.config.inviteCodes[regInviteCode];
              } else {
                  setErr('入力された招待コードは無効です。'); return;
              }
          }

          db.users[regUsername] = {
              nickname: regUsername, sns: regSns, status: initialStatus, password: regPass, credits: 100, lastLogin: '-', loginHistory: [],
              usedInviteCode: regInviteCode || '', readPopupId: 0,
              usage: { count: 0, tools: {}, apiCount: { openai: 0, anthropic: 0, google: 0 } }, perms: {}, settings: { aiModel: 'chatgpt_free', keys: {openai:'', anthropic:'', google:''}, theme: 'blue', tone: '丁寧で専門的', notifications: true, persona: '', knowledge: '', templateUrl: '' },
              curProj: 'default', projects: { 'default': { name: 'マイスペース', data: {} } }
          };
          AppDB.save(db);
          
          if (initialStatus === 'approved') {
              setMsg('招待コードが適用され、即時登録されました！ログインしてください。');
          } else {
              setMsg('登録申請が完了しました！管理者の承認をお待ちください。');
          }
          setRegUsername(regSns === 'X(Twitter)' ? '@' : ''); setRegPass(''); setRegInviteCode(''); setRegAgreed(false); setMode('login');
      };

      const TermsModal = () => div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4 animate-in' },
          div({ className: 'glass-panel rounded-3xl max-w-lg w-full p-8 relative flex flex-col max-h-[80vh]' },
              h3({ className: 'text-xl font-black text-white mb-4 pb-4 border-b border-white/10' }, '\uD83D\uDCDC 利用規約'),
              div({ className: 'overflow-y-auto flex-1 pr-4 hide-scrollbar text-sm text-slate-300 space-y-4 mb-6 leading-relaxed' },
                  p({}, '本システム（AI Content Pro）をご利用いただくにあたり、以下の規約に同意していただく必要があります。'),
                  ul({ className: 'list-disc pl-5 space-y-3 mt-2' },
                      li({}, '第1条（禁止事項）：本システムのアクセスURL、アカウント情報、およびシステム自体の第三者への共有・譲渡・販売・配布を固く禁じます。'),
                      li({}, '第2条（自作発言の禁止）：本システムが生成したコンテンツを除き、本システム自体の設計やUI、機能について、自身が作成したと虚偽の申告をすることを禁じます。'),
                      li({}, '第3条（複製の禁止）：本システムのソースコード、UIデザイン、機能構造等の無断複製、リバースエンジニアリング、および類似サービスの作成を禁じます。'),
                      li({}, '第4条（利用停止）：上記に違反した場合、または管理者が不適切と判断した場合、事前通知なくアカウントを直ちに停止・削除できるものとします。')
                  ),
                  p({ className: 'text-brand-danger font-bold mt-6 bg-brand-danger/10 p-3 rounded-lg border border-brand-danger/20' }, '※上記規約に違反した場合、法的措置を取らせていただく場合がございます。')
              ),
              button({ onClick: () => { setRegAgreed(true); setShowTerms(false); }, className: 'w-full btn-gradient py-4 rounded-xl font-black shadow-xl mt-2' }, '規約を確認し、同意する')
          )
      );
 
      return div({ className: 'w-full h-full flex items-center justify-center p-4' },  
        showTerms && el(TermsModal),
        div({ className: 'glass-panel rounded-3xl p-10 md:p-16 shadow-2xl text-center max-w-lg w-full relative overflow-hidden' },  
          h2({ className: 'text-3xl font-black mb-8 tracking-tight text-white' }, 'AI Content Pro'),  
          
          div({ className: 'flex mb-8 border-b border-white/10' },
              button({ onClick: () => { setMode('login'); setErr(''); setMsg(''); }, className: 'flex-1 pb-3 font-bold transition-colors ' + (mode === 'login' ? 'text-brand border-b-2 border-brand' : 'text-slate-500 hover:text-slate-300') }, 'ログイン'),
              button({ onClick: () => { setMode('register'); setErr(''); setMsg(''); }, className: 'flex-1 pb-3 font-bold transition-colors ' + (mode === 'register' ? 'text-brand border-b-2 border-brand' : 'text-slate-500 hover:text-slate-300') }, '新規登録')
          ),

          msg && p({ className: 'text-brand-success text-sm font-bold text-center mb-6 bg-brand-success/10 p-3 rounded-lg border border-brand-success/20' }, msg),
          err && p({ className: 'text-brand-danger text-sm font-bold text-center mb-6 bg-brand-danger/10 p-3 rounded-lg border border-brand-danger/20' }, err),

          mode === 'login' ? div({ className: 'space-y-5 text-left animate-in' },  
            input({ className: 'input-base text-center', placeholder: 'SNSユーザー名 / ニックネーム', value: nickname, onChange: e => setNickname(e.target.value) }),  
            input({ type: 'password', className: 'input-base text-center font-mono', placeholder: 'パスワード', value: pass, onChange: e => setPass(e.target.value), onKeyDown: e => { if(e.key === 'Enter') login(); } }),  
            button({ onClick: login, className: 'w-full btn-gradient py-4 rounded-xl text-lg mt-4 shadow-lg shadow-brand/20' }, 'ログインする')  
          ) : div({ className: 'space-y-5 text-left animate-in' },
            el('select', { className: 'input-base text-center text-sm', value: regSns, onChange: e => {
                const val = e.target.value;
                setRegSns(val);
                if (val === 'X(Twitter)') {
                    if (!regUsername || regUsername === '') setRegUsername('@');
                    else if (!regUsername.startsWith('@')) setRegUsername('@' + regUsername);
                } else if (val === 'Threads') {
                    if (regUsername === '@') setRegUsername('');
                    else if (regUsername.startsWith('@')) setRegUsername(regUsername.substring(1));
                }
            }},
                option({ value: 'X(Twitter)' }, 'X (Twitter)で登録'),
                option({ value: 'Threads' }, 'Threadsで登録')
            ),
            input({ className: 'input-base text-center font-mono', placeholder: regSns === 'X(Twitter)' ? '@から始まるユーザー名' : 'ユーザー名', value: regUsername, onChange: e => setRegUsername(e.target.value) }),
            input({ type: 'password', className: 'input-base text-center font-mono mt-2', placeholder: 'パスワードを設定 (6文字以上)', value: regPass, onChange: e => setRegPass(e.target.value) }),
            input({ className: 'input-base text-center font-mono mt-2', placeholder: '招待コード (お持ちの場合)', value: regInviteCode, onChange: e => setRegInviteCode(e.target.value) }),
            p({ className: 'text-[10px] text-slate-400 leading-tight mt-1' }, '※パスワードは暗号化され、管理者でも確認できません。忘れないようご注意ください。'),
            
            div({ className: 'flex items-center gap-3 p-3 mt-4 bg-black/30 rounded-xl border border-white/5' },
                div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition shrink-0 cursor-not-allowed opacity-80' },   
                    div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (regAgreed ? 'bg-brand left-5' : 'bg-gray-400') })  
                ),  
                button({ onClick: () => setShowTerms(true), className: 'text-xs text-brand hover:text-brand-light font-bold leading-relaxed text-left underline underline-offset-4' }, '利用規約およびプライバシーポリシーを確認し、同意する')  
            ),
            
            button({ onClick: register, disabled: !regAgreed, className: 'w-full btn-gradient py-4 rounded-xl text-lg mt-4 shadow-lg shadow-brand/20 disabled:opacity-50 disabled:cursor-not-allowed' }, '登録申請する')
          )
        )  
      );  
    };  
 
    const App = () => {  
      const [auth, setAuth] = useState({ u: null, r: null });  
      useEffect(() => {  
        const session = localStorage.getItem(SESS_KEY);  
        if (session) {
            try { setAuth(JSON.parse(session)); } catch(e) { localStorage.removeItem(SESS_KEY); }
        }
      }, []);  
 
      if (!auth.u) return el(AuthBox, { onLogin: (u, r) => setAuth({ u, r }) });  
      return el(MainApp, { user: auth.u, role: auth.r, onLogout: () => { localStorage.removeItem(SESS_KEY); setAuth({ u: null, r: null }); } });  
    };  
 
    ReactDOM.createRoot(document.getElementById('root')).render(el(App));  
  })();