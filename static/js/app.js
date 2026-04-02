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
    const h5 = (pr, ...c) => el('h5', pr, ...c);
    const h6 = (pr, ...c) => el('h6', pr, ...c);
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
    const SYS_VERSION = 'v71.9.1 Ultimate Master Edition';  
 
    const AppDB = {  
      get: () => {  
        let db = null;  
        try { db = JSON.parse(localStorage.getItem(DB_KEY)); } catch (e) {}  
        if (!db) {  
          db = {   
            config: { adminU: 'admin', adminP: 'admin123', announcement: '', inviteCodes: {}, popupMessage: '', popupId: 0 },   
            errorLogs: [], sharedPrompts: {},
            users: { 'admin': { nickname: '管理者', status: 'approved', credits: 99999, lastLogin: '', loginHistory: [], usage: { count: 0, tools: {}, apiCount: { openai: 0, anthropic: 0, google: 0 } }, perms: {}, settings: { aiModel: 'chatgpt_free', keys: {openai:'', anthropic:'', google:''}, theme: 'blue', tone: '丁寧で専門的', notifications: true, persona: '', knowledge: '', templateUrl: '', templates: ['','',''], myCharas: [] }, curProj: 'default', projects: { 'default': { name: '管理者領域', data: {} } }, usedInviteCode: '', readPopupId: 0 } }   
          };  
          localStorage.setItem(DB_KEY, JSON.stringify(db));  
        }  
        Object.keys(db.users).forEach(u => {
            if(db.users[u].credits === undefined) db.users[u].credits = 100;
            if(!db.users[u].settings.templates) db.users[u].settings.templates = ['', '', ''];
            if(!db.users[u].settings.myCharas) db.users[u].settings.myCharas = [];
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
    const ErrorAlert = ({ msg }) => div({ className: 'p-4 mb-4 bg-brand-danger/10 border border-brand-danger/30 rounded-xl text-brand-danger text-sm font-bold animate-in' }, '\u26A0\uFE0F エラー: ' + msg);

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
          recognition.onresult = (event) => { const text = event.results[0][0].transcript; onChange(f.id, (value ? value + '\n' + text : text)); };
          recognition.start();
      };
      const SpeechBtn = () => hasSpeech && button({ onClick: startSpeech, title: '音声入力', className: 'absolute right-2 bottom-2 p-2 rounded-full transition ' + (isListening ? 'bg-red-500/20 text-red-500 animate-pulse' : 'bg-white/5 text-slate-400 hover:text-brand hover:bg-brand/10') }, '\uD83C\uDFA4');
      
      const inputEl = () => {  
        if (f.t === 'text') return div({className:'relative w-full'}, input({ className: 'input-base pr-10', value, placeholder: f.ph||'', onChange: e => onChange(f.id, e.target.value) }), el(SpeechBtn));  
        if (f.t === 'area') return div({className:'relative w-full h-full'}, textarea({ className: 'input-base min-h-[100px] resize-y text-sm pb-10', value, placeholder: f.ph||'', onChange: e => onChange(f.id, e.target.value) }), el(SpeechBtn));  
        if (f.t === 'select') return select({ className: 'input-base text-sm', value, onChange: e => onChange(f.id, e.target.value) }, f.opts.map(o => option({ key: o, value: o, className: 'bg-bg-panel' }, o)));  
        if (f.t === 'check') return label({ className: 'flex items-center gap-3 cursor-pointer p-2' }, div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition' }, div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (value ? 'bg-brand left-5' : 'bg-gray-400') })), input({ type: 'checkbox', className: 'hidden', checked: !!value, onChange: e => onChange(f.id, e.target.checked) }), span({ className: 'text-sm font-bold text-slate-300' }, '機能を有効にする'));  
        if (f.t === 'image') return div({ className: 'mt-2' }, input({ type: 'file', accept: 'image/*', className: 'text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-bold file:bg-brand/20 file:text-brand hover:file:bg-brand/30 cursor-pointer transition', onChange: e => { const file = e.target.files[0]; if(file) { const reader = new FileReader(); reader.onload = ev => onChange(f.id, ev.target.result.split(',')[1]); reader.readAsDataURL(file); } } }), value ? span({className: 'ml-3 text-xs text-brand-success font-bold'}, '\u2713 画像セット済') : null);
        return null;  
      };  
      return div({ className: 'mb-6 animate-in relative' },  
        isMagicLoading && isMainMagic && div({ className: 'absolute inset-0 bg-black/60 z-10 rounded-2xl flex items-center justify-center backdrop-blur-sm' }, el(LoadingCircle)),
        div({ className: 'flex justify-between items-center mb-2 gap-2' }, span({ className: 'text-xs font-black text-slate-400 tracking-wider' }, f.l), isMainMagic && button({ onClick: () => onMagic(f.id), disabled: isMagicLoading, className: 'bg-gradient-to-r from-brand-accent to-red-500 text-white text-[10px] font-black px-3 py-1 rounded-full shadow-lg hover:brightness-110 transition disabled:opacity-50' }, '\u2728 魔法で入力')),  
        inputEl()  
      );  
    };  

    // ================================================================
    // UserSettingModal
    // ================================================================
    const UserSettingModal = ({ uData, onClose, onSave, user }) => {
        const [aiModel, setAiModel] = useState(uData.settings.aiModel);
        const [keys, setKeys] = useState(uData.settings.keys || {openai:'', anthropic:'', google:''});
        const [theme, setTheme] = useState(uData.settings.theme || 'blue');
        const [tone, setTone] = useState(uData.settings.tone || '丁寧で専門的');
        const [persona, setPersona] = useState(uData.settings.persona || '');
        const [knowledge, setKnowledge] = useState(uData.settings.knowledge || '');
        const [templates, setTemplates] = useState(uData.settings.templates || ['','','']);
        const [myCharas, setMyCharas] = useState(uData.settings.myCharas || []);
        
        const handleSave = () => {
            const db = AppDB.get();
            db.users[user].settings = Object.assign({}, db.users[user].settings, { aiModel, keys, theme, tone, persona, knowledge, templates, myCharas });
            AppDB.save(db);
            onSave(db);
        };

        return div({className: 'fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4'},
            div({className: 'glass-panel w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-3xl p-6 md:p-8 animate-in'},
                h2({className: 'text-xl font-black text-white mb-6 flex items-center gap-3'}, '⚙️ ユーザー設定'),
                div({className: 'space-y-6'},
                    div({},
                        label({className: 'block text-sm font-bold text-slate-300 mb-2'}, '🤖 デフォルトAIモデル'),
                        select({className: 'input-base', value: aiModel, onChange: e=>setAiModel(e.target.value)},
                            option({value: 'chatgpt_free'}, 'ChatGPT (標準)'), option({value: 'chatgpt_paid'}, 'ChatGPT (上位モデル/Web検索)'),
                            option({value: 'claude_free'}, 'Claude (標準)'), option({value: 'claude_paid'}, 'Claude (上位モデル)')
                        )
                    ),
                    div({},
                        label({className: 'block text-sm font-bold text-slate-300 mb-2'}, '🔑 あなたのAPIキー (任意)'),
                        p({className: 'text-xs text-slate-400 mb-2'}, '※設定するとシステムの制限を受けずに利用可能です'),
                        input({className: 'input-base mb-2', placeholder: 'OpenAI API Key (sk-...)', value: keys.openai, onChange: e=>setKeys({...keys, openai: e.target.value})}),
                        input({className: 'input-base mb-2', placeholder: 'Anthropic API Key (sk-ant-...)', value: keys.anthropic, onChange: e=>setKeys({...keys, anthropic: e.target.value})})
                    ),
                    div({ className: 'pt-6 border-t border-white/10' },
                        label({ className: 'block text-xs font-bold text-slate-400 mb-3 flex items-center gap-2' }, '\uD83C\uDFAD マイキャラ保存 (最大5体)'),
                        p({ className: 'text-[10px] text-slate-500 mb-3' }, '※保存したキャラは全ツールの「なりきりキャラクター」選択肢に追加されます。'),
                        myCharas.map((ch, ci) => div({ key: ci, className: 'mb-3 p-3 bg-white/5 border border-white/10 rounded-xl animate-in' },
                            div({ className: 'flex items-center gap-2 mb-2' },
                                span({ className: 'text-xs font-bold text-brand-light' }, '\uD83C\uDFAD キャラ ' + (ci+1)),
                                button({ onClick: () => { const nc = myCharas.filter((_, i) => i !== ci); setMyCharas(nc); }, className: 'ml-auto text-[10px] text-brand-danger hover:text-white' }, '削除')
                            ),
                            input({ className: 'input-base !py-1.5 text-xs mb-1.5', placeholder: 'キャラ名 (例: 元看護師の占い師さくら)', value: ch.name || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { name: e.target.value }); setMyCharas(nc); } }),
                            textarea({ className: 'input-base min-h-[60px] text-xs', placeholder: '性格・口調・特徴 (例: 30代女性。優しく寄り添う口調。「〜ですよね」が多い。)', value: ch.desc || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { desc: e.target.value }); setMyCharas(nc); } })
                        )),
                        myCharas.length < 5 && button({ onClick: () => setMyCharas(myCharas.concat([{ name: '', desc: '' }])), className: 'w-full glass-panel py-2.5 rounded-xl text-xs font-bold text-brand-light hover:bg-brand/10 transition border border-dashed border-white/20' }, '+ 新しいキャラを追加')
                    ),
                    div({ className: 'pt-6 border-t border-white/10 flex justify-end gap-3 mt-8' },
                        button({className: 'px-6 py-2 rounded-xl text-slate-400 hover:text-white', onClick: onClose}, 'キャンセル'),
                        button({className: 'btn-gradient px-8 py-2 rounded-xl font-bold', onClick: handleSave}, '設定を保存')
                    )
                )
            )
        );
    };

    // ================================================================
    // ToolCore (ツール実行・プレビュー)
    // ================================================================
    const ToolCore = ({ user, uData, db, toolId, toolConf, onBack, onUpdateUser }) => {
        const [formVals, setFormVals] = useState({});
        const [res, setRes] = useState('');
        const [isLoading, setIsLoading] = useState(false);
        const [isMagic, setIsMagic] = useState(false);
        const [genMode, setGenMode] = useState('auto');
        const [previewTab, setPreviewTab] = useState('all');
        const [previewMode, setPreviewMode] = useState('pc');
        const [err, setErr] = useState('');
        const [showHelp, setShowHelp] = useState(false);

        const enhancedFields = toolConf.fields.map(f => {
            if (f.l.includes('キャラクター') && f.opts) {
                const charaNames = (uData.settings.myCharas || []).map(c => c.name).filter(n => n);
                return { ...f, opts: [...new Set([...f.opts, ...charaNames])] };
            }
            return f;
        });

        const handleGenerate = async () => {
            setIsLoading(true); setErr('');
            let prompt = toolConf.build(formVals);
            if (genMode === 'prompt') {
                setRes(getAIPrefix(uData.settings.aiModel, uData.settings.knowledge) + prompt);
                setIsLoading(false);
                return;
            }
            try {
                const apiRes = await fetch('/api/auto_generate', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        prompt: getAIPrefix(uData.settings.aiModel, uData.settings.knowledge) + prompt,
                        ai_model: uData.settings.aiModel,
                        user_key: uData.settings.keys.openai // 簡易実装
                    })
                });
                const data = await apiRes.json();
                if(data.status === 'success') setRes(data.result);
                else setErr(data.message);
            } catch (e) { setErr('通信エラーが発生しました'); }
            setIsLoading(false);
        };

        const handleMagic = async (fid) => {
            setIsMagic(true);
            try {
                const apiRes = await fetch('/api/magic_generate', {
                    method: 'POST', headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({ tool_id: toolId, fields: enhancedFields.map(f=>({id:f.id, l:f.l, ph:f.ph})) })
                });
                const data = await apiRes.json();
                if(data.status === 'success') setFormVals({...formVals, ...data.data});
            } catch (e) { setErr('魔法の入力に失敗しました'); }
            setIsMagic(false);
        };

        const handleModify = async (actionType) => {
            if (!res) return;
            setIsLoading(true);
            let mPrompt = '';
            if (actionType === 'eyecatch_prompt') mPrompt = '以下の文章の内容を象徴する、MidjourneyやDALL-E 3などの画像生成AI向けの「英語のプロンプト」を1つだけ作成してください。出力は英語のプロンプトテキストのみにしてください。\n\n' + res;
            else if (actionType === 'line_cta') mPrompt = '以下の文章の末尾に、LINE公式アカウントへの登録を自然に促す誘導文（CTA）を3パターン追加してください。\n・「詳しくはプロフのLINEで💌」系の軽いもの\n・「LINE登録者限定で○○をプレゼント🎁」系の特典訴求\n・「今だけ無料で○○を配布中」系の緊急性訴求\n\n元の文章はそのまま残し、末尾にCTAを追加する形にしてください。\n\n' + res;
            
            try {
                const apiRes = await fetch('/api/auto_generate', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: mPrompt, ai_model: uData.settings.aiModel })
                });
                const data = await apiRes.json();
                if(data.status === 'success') setRes(actionType === 'line_cta' ? data.result : res + '\n\n---\nアイキャッチ画像プロンプト:\n' + data.result);
            } catch (e) { setErr('推敲エラー'); }
            setIsLoading(false);
        };

        return div({ className: 'flex flex-col h-full bg-bg' },
            div({ className: 'flex items-center justify-between p-4 border-b border-white/10 glass-panel shrink-0' },
                div({ className: 'flex items-center gap-4' },
                    button({ onClick: onBack, className: 'text-slate-400 hover:text-white transition p-2 rounded-full hover:bg-white/10' }, '← 戻る'),
                    div({ className: 'flex items-center gap-3' },
                        span({ className: 'text-2xl' }, toolConf.icon),
                        h2({ className: 'text-xl font-black text-white' }, toolConf.name),
                        toolConf.help && button({ onClick: () => setShowHelp(!showHelp), className: 'text-[10px] glass-panel px-2 py-1 rounded-lg text-slate-400 hover:text-white transition shrink-0' }, showHelp ? '✕ 閉じる' : '❓ 使い方')
                    )
                ),
                div({ className: 'flex gap-2 bg-black/40 p-1 rounded-xl' },
                    ['auto', 'prompt', 'god'].map(m => button({ key: m, onClick: () => setGenMode(m), className: 'px-4 py-1.5 rounded-lg text-xs font-bold transition ' + (genMode === m ? 'bg-brand text-white shadow-lg' : 'text-slate-400 hover:text-white') }, m === 'auto' ? '⚡ APIで生成' : m === 'prompt' ? '📋 プロンプトのみ' : '🔥 神丸投げ'))
                )
            ),
            div({ className: 'flex-1 overflow-hidden flex flex-col md:flex-row relative' },
                div({ className: 'w-full md:w-1/2 h-full overflow-y-auto p-4 md:p-6 custom-scrollbar border-r border-white/10' },
                    showHelp && toolConf.help && div({ className: 'mb-6 p-4 bg-brand/10 border border-brand/20 rounded-xl animate-in' },
                        div({ className: 'flex items-center gap-2 mb-2' }, span({ className: 'text-sm' }, '\u2753'), span({ className: 'text-xs font-black text-brand-light' }, toolConf.name + ' の使い方')),
                        p({ className: 'text-xs text-slate-300 leading-relaxed' }, toolConf.help)
                    ),
                    err && ErrorAlert({msg: err}),
                    
                    genMode === 'prompt' && div({ className: 'mb-6 p-4 bg-gradient-to-r from-brand-accent/10 to-orange-500/5 border border-brand-accent/20 rounded-xl animate-in' },
                        h4({ className: 'text-xs font-black text-brand-accent mb-3 flex items-center gap-2' }, '\uD83D\uDCCB プロンプトモード 3ステップ'),
                        div({ className: 'flex gap-3' },
                            div({ className: 'flex-1 text-center p-2.5 rounded-lg ' + (res ? 'bg-brand-success/20 border border-brand-success/30' : 'bg-brand-accent/20 border border-brand-accent/30') }, div({ className: 'text-lg mb-1' }, '\u2776'), p({ className: 'text-[10px] font-bold ' + (res ? 'text-brand-success' : 'text-brand-accent') }, res ? '\u2713 コピー済み' : 'プロンプトをコピー')),
                            div({ className: 'flex-1 text-center p-2.5 rounded-lg bg-white/5 border border-white/10' }, div({ className: 'text-lg mb-1' }, '\u2777'), p({ className: 'text-[10px] font-bold text-slate-400' }, 'ChatGPT等に貼り付けて生成')),
                            div({ className: 'flex-1 text-center p-2.5 rounded-lg bg-white/5 border border-white/10' }, div({ className: 'text-lg mb-1' }, '\u2778'), p({ className: 'text-[10px] font-bold text-slate-400' }, '結果を貼り付けてプレビュー'))
                        )
                    ),
                    
                    div({ className: 'space-y-6 flex-1' },
                        genMode === 'god' ? div({className: 'text-center p-8'}, p({className: 'text-brand-accent font-bold'}, '🔥 全自動でお任せ生成します')) :
                        enhancedFields.map(f => FormInput({ key: f.id, f, val: formVals[f.id], onChange: (id, v) => setFormVals({...formVals, [id]: v}), onMagic: handleMagic, isMagicLoading: isMagic })),
                        button({ onClick: handleGenerate, disabled: isLoading, className: 'w-full btn-gradient py-4 rounded-xl font-black text-lg flex justify-center items-center gap-2 shadow-xl' }, isLoading ? el(LoadingCircle) : '🚀 ' + (genMode === 'prompt' ? 'プロンプトを作成' : 'コンテンツを生成'))
                    )
                ),
                div({ className: 'w-full md:w-1/2 h-full bg-[#f8fafc] overflow-hidden flex flex-col relative' },
                    div({ className: 'flex items-center justify-between p-3 bg-white border-b border-slate-200 shrink-0' },
                        res && (() => {
                            const sectionMarkers = res.match(/---【[^】]+】---/g);
                            if (sectionMarkers && sectionMarkers.length >= 2) {
                                const sectionNames = sectionMarkers.map(m => m.replace(/---【|】---/g, ''));
                                return div({ className: 'flex gap-1 overflow-x-auto hide-scrollbar' },
                                    button({ onClick: () => setPreviewTab('all'), className: 'px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition ' + (previewTab === 'all' ? 'bg-brand text-white shadow-lg' : 'glass-panel text-slate-400 hover:text-slate-600') }, '\uD83D\uDCCB 全体'),
                                    sectionNames.map((name, i) => button({ key: i, onClick: () => setPreviewTab('sec_' + i), className: 'px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition ' + (previewTab === 'sec_' + i ? 'bg-brand text-white shadow-lg' : 'glass-panel text-slate-400 hover:text-slate-600') }, name))
                                );
                            }
                            return div({ className: 'text-slate-400 text-sm font-bold' }, 'プレビュー');
                        })(),
                        div({ className: 'flex gap-1' },
                            button({ onClick: () => setPreviewMode('mobile'), className: 'p-2 rounded-lg transition ' + (previewMode === 'mobile' ? 'bg-slate-200 text-brand' : 'text-slate-400 hover:bg-slate-100') }, '📱'),
                            button({ onClick: () => setPreviewMode('pc'), className: 'p-2 rounded-lg transition ' + (previewMode === 'pc' ? 'bg-slate-200 text-brand' : 'text-slate-400 hover:bg-slate-100') }, '💻')
                        )
                    ),
                    div({ className: 'flex-1 overflow-y-auto p-4 md:p-8 flex justify-center ' + (previewMode === 'mobile' ? 'bg-slate-800' : 'bg-slate-50') },
                        div({ className: 'w-full transition-all duration-300 ' + (previewMode === 'mobile' ? 'max-w-[390px] shadow-2xl rounded-[3rem] p-4 bg-white border-8 border-slate-900 overflow-hidden' : 'max-w-4xl') },
                            (() => {
                                if (previewTab.startsWith('sec_')) {
                                    const secIdx = parseInt(previewTab.replace('sec_', ''));
                                    const sections = res.split(/---【[^】]+】---/).filter(s => s.trim());
                                    const sectionContent = sections[secIdx] || res;
                                    return div({ className: 'preview-content text-black' }, div({ dangerouslySetInnerHTML: renderMarkdown(sectionContent.trim()) }));
                                }
                                return div({ className: 'preview-content text-black' }, div({ dangerouslySetInnerHTML: renderMarkdown(res || '結果がここに表示されます') }));
                            })()
                        )
                    ),
                    res && div({ className: 'p-3 bg-white border-t border-slate-200 shrink-0 flex items-center justify-between' },
                        span({ className: 'text-xs font-bold text-slate-400' }, res.length + ' 文字'),
                        div({ className: 'flex gap-2' },
                            button({ onClick: () => copyTextToClipboard(res), className: 'glass-panel !border-slate-300 px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition shadow-sm' }, '📋 コピー'),
                            button({ onClick: () => handleModify('eyecatch_prompt'), disabled: isLoading, className: 'glass-panel !border-brand/30 px-3 py-2 rounded-xl text-xs font-bold text-brand hover:bg-brand/10 transition shadow-sm' }, '🖼 アイキャッチ'),
                            button({ onClick: () => handleModify('line_cta'), disabled: isLoading, className: 'glass-panel !border-green-500/30 px-3 py-2 rounded-xl text-xs font-bold text-green-600 hover:bg-green-50 transition shadow-sm' }, '💚 LINE誘導追加')
                        )
                    )
                )
            )
        );
    };

    // ================================================================
    // 総合マニュアル (ManualModal)
    // ================================================================
    const ManualModal = ({ onClose }) => {
        const [activeTab, setActiveTab] = useState('basic');
        return div({ className: 'fixed inset-0 z-[200] flex items-center justify-center bg-black/80 p-4 animate-in backdrop-blur-sm' },
            div({ className: 'glass-panel rounded-3xl max-w-5xl w-full p-6 md:p-8 relative flex flex-col max-h-[90vh]' },
                button({ onClick: onClose, className: 'absolute top-5 right-5 text-slate-400 hover:text-white text-xl font-bold transition z-10' }, '\u2715'),
                h3({ className: 'text-2xl font-black text-white mb-6 pb-4 border-b border-white/10 flex items-center gap-2' }, '📖 AICP Pro 総合マニュアル'),
                div({ className: 'flex gap-2 mb-6 border-b border-white/10 pb-2 overflow-x-auto hide-scrollbar shrink-0' },
                    [{id:'basic', l:'🔰 基本の使い方'}, {id:'magic', l:'✨ 神丸投げ・自動補完'}, {id:'persona', l:'🎭 マイキャラ設定'}, {id:'tools', l:'🛠 各ツールの解説'}].map(t => 
                        button({ key: t.id, onClick: () => setActiveTab(t.id), className: 'px-4 py-2 rounded-full text-xs font-bold transition whitespace-nowrap ' + (activeTab === t.id ? 'bg-brand text-white' : 'text-slate-400 hover:bg-white/10') }, t.l)
                    )
                ),
                div({ className: 'overflow-y-auto flex-1 pr-4 custom-scrollbar text-slate-300 space-y-6 leading-relaxed text-sm relative' },
                    activeTab === 'basic' && div({ className: 'animate-in space-y-6' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '1. コンテンツの生成方法'),
                        p({}, '左側のフォームに必要な情報を入力し、画面下部の生成ボタンを押します。実行モードには以下の2種類があります。'),
                        ul({ className: 'list-disc pl-5 space-y-3 bg-white/5 p-4 rounded-xl' },
                            li({}, span({ className: 'font-bold text-white' }, '🚀 全自動生成 (API): '), 'システム内で直接AI（ChatGPT, Claude, Gemini）と通信し、結果を右画面に即座に表示します。'),
                            li({}, span({ className: 'font-bold text-white' }, '📋 プロンプトのみ作成: '), '高品質な指示文（プロンプト）を作成してコピーします。ご自身のChatGPT等に貼り付けて生成し、結果を本システムの「手動貼り付け」機能でプレビューに反映できます。')
                        ),
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2 mt-6' }, '2. プレビューと推敲（リライト）機能'),
                        p({}, '生成された結果は右側のプレビュー画面に表示されます。PC/スマホ表示の切り替えや、結果に対するワンクリックでの推敲が可能です。'),
                        ul({ className: 'list-disc pl-5 space-y-2' },
                            li({}, '「LINE誘導追加」「キャッチーに」「シンプルに」などのボタンを押すだけで、AIが文章を自動でブラッシュアップします。'),
                            li({}, 'SNSマルチ展開ボタンを使えば、1つの記事から「X(Twitter)用」「ショート動画用」「メルマガ用」などに瞬時に変換できます。')
                        )
                    ),
                    activeTab === 'magic' && div({ className: 'animate-in space-y-6' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '🔥 究極の「神丸投げ」機能'),
                        p({}, 'フォームを', span({ className: 'text-orange-400 font-bold bg-orange-400/20 px-1 rounded' }, '【すべて空欄】'), 'のまま生成ボタンを押すと「神丸投げモード」が発動します。'),
                        p({}, 'AIが自らWeb検索（Auto-Browsing）を行い、今日の日本の最新トレンドを分析した上で、最もバズりやすいテーマを自動選定し、コンテンツを丸ごと生成します。'),
                        div({ className: 'p-4 bg-orange-500/10 border border-orange-500/30 rounded-xl' },
                            p({ className: 'text-xs text-orange-200' }, '💡 おすすめ: 「今日は何を発信しようか迷った時」にとりあえず実行してみるのが最も効果的です。')
                        ),
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2 mt-6' }, '🌟 自動補完機能'),
                        p({}, '「テーマ」だけを入力し、他の項目を空欄にして生成すると、未入力の項目をAIがWeb検索結果をもとに最適な内容で自動的に補完して生成します。')
                    ),
                    activeTab === 'persona' && div({ className: 'animate-in space-y-6' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '🎭 マイ・ペルソナ（自分専用AI化）'),
                        p({}, '「⚙️ 個人設定」>「UI・出力」タブで、ご自身のプロフィールや文体のクセ（ペルソナ）を登録できます。'),
                        p({}, '過去のブログやSNSの文章を貼り付けるだけで、AIがあなたの特徴を自動で抽出する機能もあります。ここに設定した内容は、すべてのツールの生成結果に反映され、「あなたらしい」文章が出力されるようになります。'),
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2 mt-6' }, '👥 マイキャラ保存機能'),
                        p({}, '特定の用途に向けたキャラクター（例：熱血コンサルタント、優しい占い師など）を最大5体まで保存できます。'),
                        p({}, '保存したキャラは、SNS投稿ツールや動画台本ツールの「🎭 なりきりキャラクター」のプルダウンから簡単に呼び出すことができます。')
                    ),
                    activeTab === 'tools' && div({ className: 'animate-in space-y-8' },
                        h4({ className: 'text-lg font-bold text-brand-light border-l-4 border-brand-light pl-2' }, '🛠 収録ツール一覧と使い方'),
                        CATEGORIES.map(c => {
                            const catTools = Object.keys(TOOLS).filter(k => TOOLS[k].cat === c.id);
                            if (catTools.length === 0) return null;
                            return div({ key: c.id, className: 'space-y-4' },
                                h5({ className: 'font-black text-white text-base mb-3 border-b border-white/10 pb-2' }, c.name),
                                div({ className: 'grid grid-cols-1 lg:grid-cols-2 gap-4' },
                                    catTools.map(tId => {
                                        const t = TOOLS[tId];
                                        return div({ key: tId, className: 'p-5 bg-white/5 rounded-xl border border-white/10 hover:border-brand/50 transition flex flex-col h-full group' },
                                            h6({ className: 'font-black text-white text-sm mb-2 flex items-center gap-2' }, span({className: 'text-2xl group-hover:scale-125 transition-transform'}, t.icon), t.name),
                                            p({ className: 'text-xs text-slate-300 font-bold mb-4 flex-1' }, t.desc),
                                            t.help && p({ className: 'text-[11px] text-slate-400 leading-relaxed bg-black/40 p-3 rounded-lg mt-auto border border-white/5' }, '\uD83D\uDCA1 ', t.help)
                                        );
                                    })
                                )
                            );
                        })
                    )
                ),
                button({ onClick: onClose, className: 'w-full btn-gradient py-4 rounded-xl font-black mt-6 shadow-xl shrink-0' }, 'マニュアルを閉じる')
            )
        );
    };

    // ================================================================
    // MainApp (ログイン後のメイン画面)
    // ================================================================
    const MainApp = ({ db, user, onUpdateDB, onLogout }) => {
        const uData = db.users[user];
        const [curCat, setCurCat] = useState('mon');
        const [selTool, setSelTool] = useState(null);
        const [showSettings, setShowSettings] = useState(false);
        const [showManual, setShowManual] = useState(false);

        if (selTool) return el(ToolCore, { user, uData, db, toolId: selTool, toolConf: TOOLS[selTool], onBack: () => setSelTool(null), onUpdateUser: onUpdateDB });

        const catTools = Object.keys(TOOLS).filter(k => TOOLS[k].cat === curCat);

        return div({ className: 'flex h-screen bg-bg overflow-hidden text-slate-200' },
            div({ className: 'w-64 bg-panel border-r border-white/10 flex flex-col shrink-0' },
                div({ className: 'p-6 border-b border-white/10' }, h1({ className: 'text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-accent' }, 'AICP Pro'), p({ className: 'text-[10px] font-bold text-brand mt-1' }, SYS_VERSION)),
                div({ className: 'flex-1 overflow-y-auto py-4 space-y-1' },
                    CATEGORIES.map(c => button({ key: c.id, onClick: () => setCurCat(c.id), className: 'w-full text-left px-6 py-3 text-sm font-bold transition ' + (curCat === c.id ? 'bg-brand/10 text-brand border-r-4 border-brand' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200') }, c.name))
                ),
                div({ className: 'p-4 border-t border-white/10 space-y-2' },
                    button({ onClick: () => setShowManual(true), className: 'w-full bg-brand/20 hover:bg-brand/30 border border-brand/30 py-3 rounded-lg text-sm font-bold text-brand-light flex items-center justify-center gap-2 transition mb-2' }, '📖 総合マニュアル'),
                    button({ onClick: () => setShowSettings(true), className: 'w-full py-2 rounded-lg text-xs font-bold text-slate-300 hover:bg-white/10 transition flex items-center justify-center gap-2' }, '⚙️ 設定'),
                    button({ onClick: onLogout, className: 'w-full py-2 rounded-lg text-xs font-bold text-brand-danger hover:bg-brand-danger/10 transition flex items-center justify-center gap-2' }, '🚪 ログアウト')
                )
            ),
            div({ className: 'flex-1 overflow-y-auto p-8 relative' },
                div({ className: 'max-w-6xl mx-auto' },
                    h2({ className: 'text-2xl font-black mb-8 text-white' }, CATEGORIES.find(c => c.id === curCat)?.name),
                    div({ className: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' },
                        catTools.map(tId => {
                            const t = TOOLS[tId];
                            return div({ key: tId, onClick: () => setSelTool(tId), className: 'glass-panel p-6 rounded-2xl cursor-pointer group hover:bg-white/10 transition' },
                                div({ className: 'text-4xl mb-4 group-hover:scale-110 transition-transform origin-left' }, t.icon),
                                h3({ className: 'text-lg font-bold text-white mb-2' }, t.name),
                                p({ className: 'text-xs text-slate-400 line-clamp-2 leading-relaxed' }, t.desc)
                            )
                        })
                    )
                )
            ),
            showSettings && el(UserSettingModal, { uData, user, onClose: () => setShowSettings(false), onSave: (ndb) => { onUpdateDB(ndb); setShowSettings(false); } }),
            showManual && el(ManualModal, { onClose: () => setShowManual(false) })
        );
    };

    // ================================================================
    // AuthBox
    // ================================================================
    const AuthBox = ({ onLogin }) => {
        const [id, setId] = useState('');
        const [pass, setPass] = useState('');
        const [err, setErr] = useState('');
        
        const handle = () => {
            const db = AppDB.get();
            if(db.users[id]) {
                if(id === 'admin' && pass === db.config.adminP) onLogin(id);
                else if(id !== 'admin' && pass === 'password') onLogin(id); // 開発用簡易パスワード
                else setErr('パスワードが違います (一般ユーザーは "password" でログイン)');
            } else {
                setErr('ユーザーが存在しません (admin / admin123 を使用可能)');
            }
        };

        return div({className: 'flex h-screen items-center justify-center relative overflow-hidden bg-[#020617]'},
            div({className: 'absolute inset-0 bg-[url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.03\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")]'}),
            div({className: 'glass-panel p-8 md:p-12 rounded-3xl w-full max-w-md relative z-10 animate-in border border-white/10 shadow-2xl'},
                div({className: 'text-center mb-8'},
                    h2({className: 'text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-brand-light to-brand-accent mb-2'}, 'AICP Pro'),
                    p({className: 'text-xs text-slate-400 font-bold tracking-widest'}, 'ULTIMATE SAAS EDITION')
                ),
                err && ErrorAlert({msg: err}),
                div({className: 'space-y-4'},
                    input({className: 'input-base py-4 px-5 text-base rounded-2xl bg-black/40', placeholder: 'ユーザーID', value: id, onChange: e=>setId(e.target.value)}),
                    input({className: 'input-base py-4 px-5 text-base rounded-2xl bg-black/40', type: 'password', placeholder: 'パスワード', value: pass, onKeyDown: e => e.key === 'Enter' && handle(), onChange: e=>setPass(e.target.value)}),
                    button({className: 'btn-gradient w-full py-4 rounded-2xl font-black text-lg shadow-xl mt-4', onClick: handle}, 'ログイン')
                )
            )
        );
    };

    // ================================================================
    // App (Root Component)
    // ================================================================
    const App = () => {
        const [db, setDb] = useState(null);
        const [user, setUser] = useState(null);

        useEffect(() => {
            const initialDb = AppDB.get();
            setDb(initialDb);
            const sess = sessionStorage.getItem(SESS_KEY);
            if (sess && initialDb.users[sess]) setUser(sess);
        }, []);

        const handleLogin = (u) => {
            sessionStorage.setItem(SESS_KEY, u);
            setUser(u);
        };

        const handleLogout = () => {
            sessionStorage.removeItem(SESS_KEY);
            setUser(null);
        };

        const handleUpdateDB = (newDb) => {
            setDb(newDb);
            AppDB.save(newDb);
        };

        if (!db) return div({className: 'flex h-screen items-center justify-center'}, el(LoadingCircle));
        if (!user) return el(AuthBox, { onLogin: handleLogin });
        return el(MainApp, { db, user, onUpdateDB: handleUpdateDB, onLogout: handleLogout });
    };

    ReactDOM.createRoot(document.getElementById('root')).render(el(App));
})();
