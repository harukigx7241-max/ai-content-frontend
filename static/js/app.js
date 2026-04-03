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
    const SYS_VERSION = 'v72.0.1 Ultimate SaaS Edition';  
 
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
        ? '有料版(最上位モデル)です。最高の創造性を発揮してください。\n※【最重要】最新の事実確認が必要な場合は、必ず「Web検索」を使用して情報を取得し、日本の文脈に合わせて出力してください。'
        : '無料版です。簡潔かつ的確に要求を満たしてください。';
      let tone = settings && settings.tone ? '\n※出力のトーン・文体は「' + settings.tone + '」で統一してください。' : '';
      let personaText = settings && settings.persona ? '\n※【マイ・ペルソナ】以下の情報を私（AI）自身の設定として完全に憑依させてください：\n' + settings.persona + '\n' : '';
      return '【システム指示：' + aiName + ' ' + spec + '】\nあなたはトップレベルのAIアシスタントです。' + tone + personaText + '\n\n';
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
        textArea.style.position = "fixed"; textArea.style.left = "-9999px";
        document.body.appendChild(textArea);
        textArea.focus(); textArea.select();
        try { document.execCommand('copy'); } catch (err) {}
        document.body.removeChild(textArea);
    };
 
    const LoadingCircle = () => div({ className: 'w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin' });
    const ErrorAlert = ({ msg }) => div({ className: 'p-4 mb-4 bg-brand-danger/10 border border-brand-danger/30 rounded-xl text-brand-danger text-sm font-bold animate-in' }, '\u26A0\uFE0F エラー: ' + msg);

    const FormInput = ({ f, val, onChange, onMagic, isMagicLoading }) => {  
      const isMainMagic = f.isMainMagic;  
      const value = val !== undefined ? val : (f.t === 'check' ? false : (f.opts ? f.opts[0] : ''));  
      
      const inputEl = () => {  
        if (f.t === 'text') return input({ className: 'input-base', value, placeholder: f.ph||'', onChange: e => onChange(f.id, e.target.value) });  
        if (f.t === 'area') return textarea({ className: 'input-base min-h-[100px] resize-y text-sm', value, placeholder: f.ph||'', onChange: e => onChange(f.id, e.target.value) });  
        if (f.t === 'select') return select({ className: 'input-base text-sm bg-bg-panel', value, onChange: e => onChange(f.id, e.target.value) }, f.opts.map(o => option({ key: o, value: o }, o)));  
        if (f.t === 'check') return label({ className: 'flex items-center gap-3 cursor-pointer p-2' }, div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition' }, div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (value ? 'bg-brand left-5' : 'bg-gray-400') })), input({ type: 'checkbox', className: 'hidden', checked: !!value, onChange: e => onChange(f.id, e.target.checked) }), span({ className: 'text-sm font-bold text-slate-300' }, '機能を有効にする'));  
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
        const [myCharas, setMyCharas] = useState(uData.settings.myCharas || []);
        
        const handleSave = () => {
            const db = AppDB.get();
            db.users[user].settings = Object.assign({}, db.users[user].settings, { aiModel, keys, theme, tone, persona, knowledge, myCharas });
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
                            textarea({ className: 'input-base min-h-[60px] text-xs', placeholder: '性格・口調・特徴', value: ch.desc || '', onChange: e => { const nc = myCharas.slice(); nc[ci] = Object.assign({}, nc[ci], { desc: e.target.value }); setMyCharas(nc); } })
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
                        user_key: uData.settings.keys.openai
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
            if (actionType === 'eyecatch_prompt') mPrompt = '以下の文章の内容を象徴する、Midjourneyなどの画像生成AI向けの「英語のプロンプト」を1つ作成してください。\n\n' + res;
            else if (actionType === 'line_cta') mPrompt = '以下の文章の末尾に、LINE公式アカウントへの登録を自然に促す誘導文（CTA）を3パターン追加してください。\n元の文章はそのまま残し、末尾にCTAを追加する形にしてください。\n\n' + res;
            
            try {
                const apiRes = await fetch('/api/auto_generate', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ prompt: mPrompt, ai_model: uData.settings.aiModel })
                });
                const data = await apiRes.json();
                if(data.status === 'success') setRes(actionType === 'line_cta' ? data.result : res + '\n\n---\nアイキャッチプロンプト:\n' + data.result);
            } catch (e) { setErr('推敲エラー'); }
            setIsLoading(false);
        };

        return div({ className: 'flex flex-col h-full bg-bg' },
            div({ className: 'flex items-center justify-between p-4 border-b border-white/10 glass-panel shrink-0' },
                div({ className: 'flex items-center gap-4' },
                    button({ onClick: onBack, className: 'text-slate-400 hover:text-white transition p-2 rounded-full hover:bg-white/10' }, '← 戻る'),
                    div({ className: 'flex items-center gap-3' },
                        span({ className: 'text-2xl' }, toolConf.icon),
                        h2({ className: 'text-xl font-black text-white' }, toolConf.name)
                    )
                ),
                div({ className: 'flex gap-2 bg-black/40 p-1 rounded-xl' },
                    ['auto', 'prompt', 'god'].map(m => button({ key: m, onClick: () => setGenMode(m), className: 'px-4 py-1.5 rounded-lg text-xs font-bold transition ' + (genMode === m ? 'bg-brand text-white shadow-lg' : 'text-slate-400 hover:text-white') }, m === 'auto' ? '⚡ APIで生成' : m === 'prompt' ? '📋 プロンプトのみ' : '🔥 神丸投げ'))
                )
            ),
            div({ className: 'flex-1 overflow-hidden flex flex-col md:flex-row relative' },
                div({ className: 'w-full md:w-1/2 h-full overflow-y-auto p-4 md:p-6 custom-scrollbar border-r border-white/10' },
                    err && ErrorAlert({msg: err}),
                    div({ className: 'space-y-6 flex-1' },
                        genMode === 'god' ? div({className: 'text-center p-8'}, p({className: 'text-brand-accent font-bold'}, '🔥 全自動でお任せ生成します')) :
                        enhancedFields.map(f => FormInput({ key: f.id, f, val: formVals[f.id], onChange: (id, v) => setFormVals({...formVals, [id]: v}), onMagic: handleMagic, isMagicLoading: isMagic })),
                        button({ onClick: handleGenerate, disabled: isLoading, className: 'w-full btn-gradient py-4 rounded-xl font-black text-lg flex justify-center items-center gap-2 shadow-xl' }, isLoading ? el(LoadingCircle) : '🚀 コンテンツを生成')
                    )
                ),
                div({ className: 'w-full md:w-1/2 h-full bg-[#f8fafc] overflow-hidden flex flex-col relative' },
                    div({ className: 'flex items-center justify-between p-3 bg-white border-b border-slate-200 shrink-0' },
                        res && (() => {
                            if (toolId === 'sns_cal') return div({ className: 'text-brand text-sm font-bold flex items-center gap-2 px-3 py-1.5 bg-brand/10 rounded-lg' }, '📅 カレンダービュー');
                            const sectionMarkers = res.match(/---【[^】]+】---/g);
                            if (toolId === 'note' && sectionMarkers && sectionMarkers.length >= 2) {
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
                            (toolId === 'sns_cal' && res ?
                                (() => {
                                    const lines = res.split('\n').filter(l => l.trim().length > 0);
                                    let items = [];
                                    for (let line of lines) {
                                        if (line.includes('---')) continue;
                                        let cols = [];
                                        if (line.includes('|')) cols = line.split('|').map(s => s.trim()).filter(s => s);
                                        else if (line.includes(',')) cols = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map(s => s.trim().replace(/^"|"$/g, ''));
                                        else if (line.includes('\t')) cols = line.split('\t').map(s => s.trim());
                                        if (cols.length >= 2 && !cols.some(c => c.includes('曜日') || c.includes('投稿文の要点'))) items.push(cols);
                                    }
                                    if (items.length === 0) return div({ className: 'preview-content text-black' }, div({ dangerouslySetInnerHTML: renderMarkdown(res) })); 
                                    return div({ id: 'preview-tab-content', className: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 md:p-6 bg-slate-100 rounded-2xl shadow-inner overflow-y-auto custom-scrollbar' + (previewMode === 'mobile' ? ' grid-cols-1' : '') },
                                        items.map((cols, i) => {
                                            const dayStr = cols[0].length < 15 ? cols[0] : (cols[1] ? cols[1] : `Day ${i+1}`);
                                            const contentStr = cols[cols.length - 1];
                                            const themeStr = cols.length > 2 ? cols[cols.length - 2] : '';
                                            return div({ key: i, className: 'bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col hover:shadow-lg transition overflow-hidden relative' },
                                                div({ className: 'absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-brand to-brand-accent' }),
                                                div({ className: 'bg-brand/5 border-b border-brand/10 px-4 py-2 flex justify-between items-center' },
                                                    span({ className: 'text-sm font-black text-brand' }, `📅 ${i+1}日目`),
                                                    span({ className: 'text-[10px] font-bold text-slate-500 bg-white px-2 py-1 rounded-full shadow-sm' }, dayStr)
                                                ),
                                                div({ className: 'p-4 flex-1 flex flex-col gap-3' },
                                                    themeStr && div({}, span({ className: 'text-[10px] font-bold text-slate-400 block' }, '🎯 テーマ'), p({ className: 'text-xs font-bold text-slate-700' }, themeStr)),
                                                    div({ className: 'flex-1' }, span({ className: 'text-[10px] font-bold text-slate-400 block' }, '📝 投稿内容'), div({ className: 'text-xs text-slate-700 leading-relaxed overflow-y-auto max-h-[150px] custom-scrollbar', dangerouslySetInnerHTML: renderMarkdown(contentStr) }))
                                                )
                                            );
                                        })
                                    );
                                })()
                            : (() => {
                                if (previewTab.startsWith('sec_')) {
                                    const secIdx = parseInt(previewTab.replace('sec_', ''));
                                    const sections = res.split(/---【[^】]+】---/).filter(s => s.trim());
                                    const sectionContent = sections[secIdx] || res;
                                    return div({ className: 'preview-content text-black' }, div({ dangerouslySetInnerHTML: renderMarkdown(sectionContent.trim()) }));
                                }
                                return div({ className: 'preview-content text-black' }, div({ dangerouslySetInnerHTML: renderMarkdown(res || '結果がここに表示されます') }));
                            })()
                            )
                        )
                    ),
                    res && div({ className: 'p-3 bg-white border-t border-slate-200 shrink-0 flex items-center justify-between' },
                        span({ className: 'text-xs font-bold text-slate-400' }, res.length + ' 文字'),
                        div({ className: 'flex gap-2' },
                            button({ onClick: () => copyTextToClipboard(res), className: 'glass-panel !border-slate-300 px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-100 transition shadow-sm' }, '📋 コピー'),
                            button({ onClick: () => handleModify('line_cta'), disabled: isLoading, className: 'glass-panel !border-green-500/30 px-3 py-2 rounded-xl text-xs font-bold text-green-600 hover:bg-green-50 transition shadow-sm' }, '💚 LINE誘導追加')
                        )
                    )
                )
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

        if (selTool) return el(ToolCore, { user, uData, db, toolId: selTool, toolConf: TOOLS[selTool], onBack: () => setSelTool(null), onUpdateUser: onUpdateDB });

        const catTools = Object.keys(TOOLS).filter(k => TOOLS[k].cat === curCat);

        return div({ className: 'flex h-screen bg-bg overflow-hidden text-slate-200' },
            div({ className: 'w-64 bg-panel border-r border-white/10 flex flex-col shrink-0' },
                div({ className: 'p-6 border-b border-white/10' }, h1({ className: 'text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-brand to-brand-accent' }, 'AICP Pro'), p({ className: 'text-[10px] font-bold text-brand mt-1' }, SYS_VERSION)),
                div({ className: 'flex-1 overflow-y-auto py-4 space-y-1' },
                    CATEGORIES.map(c => button({ key: c.id, onClick: () => setCurCat(c.id), className: 'w-full text-left px-6 py-3 text-sm font-bold transition ' + (curCat === c.id ? 'bg-brand/10 text-brand border-r-4 border-brand' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200') }, c.name))
                ),
                div({ className: 'p-4 border-t border-white/10 space-y-2' },
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
            showSettings && el(UserSettingModal, { uData, user, onClose: () => setShowSettings(false), onSave: (ndb) => { onUpdateDB(ndb); setShowSettings(false); } })
        );
    };

    // ================================================================
    // AuthBox (利用規約同意 UI を完全に修復・搭載)
    // ================================================================
    const AuthBox = ({ onLogin }) => {
        const [isRegister, setIsRegister] = useState(false);
        const [id, setId] = useState('');
        const [pass, setPass] = useState('');
        const [err, setErr] = useState('');
        const [regAgreed, setRegAgreed] = useState(false);
        const [showTerms, setShowTerms] = useState(false);
        
        const handle = () => {
            const db = AppDB.get();
            if(db.users[id]) {
                if(id === 'admin' && pass === db.config.adminP) onLogin(id);
                else if(id !== 'admin' && pass === 'password') onLogin(id);
                else setErr('パスワードが違います');
            } else setErr('ユーザーが存在しません');
        };

        const register = () => {
            setErr('登録申請を受け付けました（現在はデモ用です）');
        };

        return div({className: 'flex h-screen items-center justify-center relative overflow-hidden bg-[#020617]'},
            div({className: 'glass-panel p-8 md:p-12 rounded-3xl w-full max-w-md relative z-10 animate-in border border-white/10 shadow-2xl'},
                div({className: 'text-center mb-8'}, h2({className: 'text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-brand-light to-brand-accent mb-2'}, 'AICP Pro')),
                err && ErrorAlert({msg: err}),
                div({className: 'space-y-4'},
                    input({className: 'input-base py-4 px-5 text-base rounded-2xl bg-black/40', placeholder: 'ユーザーID', value: id, onChange: e=>setId(e.target.value)}),
                    input({className: 'input-base py-4 px-5 text-base rounded-2xl bg-black/40', type: 'password', placeholder: 'パスワード', value: pass, onKeyDown: e => e.key === 'Enter' && (!isRegister ? handle() : register()), onChange: e=>setPass(e.target.value)}),
                    
                    isRegister && div ({ className: 'flex items-center gap-3 p-3 mt-4 bg-black/30 rounded-xl border border-white/5' },
                        div({ className: 'w-10 h-6 bg-gray-700 rounded-full relative transition shrink-0 cursor-not-allowed opacity-80' },
                            div({ className: 'absolute top-1 left-1 w-4 h-4 rounded-full transition ' + (regAgreed ? 'bg-brand left-5': 'bg-gray-400') })
                        ),
                        button({ onClick: () => setShowTerms (true), className: 'text-xs text-brand hover:text-brand-light font-bold leading-relaxed text-left underline underline-offset-4'}, '利用規約およびプライバシーポリシーを確認し、同意する')
                    ),

                    !isRegister ? button({className: 'btn-gradient w-full py-4 rounded-2xl font-black text-lg shadow-xl mt-4', onClick: handle}, 'ログイン')
                                : button({onClick: register, disabled: !regAgreed, className: 'w-full btn-gradient py-4 rounded-xl text-lg mt-4 shadow-lg shadow-brand/20 disabled:opacity-50 disabled:cursor-not-allowed'}, '登録申請する'),
                    
                    button({className: 'w-full text-slate-400 text-sm mt-4 hover:text-white', onClick: () => setIsRegister(!isRegister)}, isRegister ? '既存アカウントでログイン' : '新規アカウント登録申請')
                )
            ),
            showTerms && div({className: 'fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4'},
                div({className: 'glass-panel p-8 rounded-2xl max-w-lg w-full'},
                    h3({className: 'text-xl font-bold text-white mb-4'}, '利用規約 / プライバシーポリシー'),
                    div({className: 'h-64 overflow-y-auto text-sm text-slate-300 mb-6 bg-black/30 p-4 rounded-lg'}, 'ここに利用規約とプライバシーポリシーが記載されます。内容を確認し、同意する場合は下の「同意する」ボタンを押してください。'),
                    div({className: 'flex justify-end gap-4'},
                        button({className: 'px-4 py-2 rounded-lg text-slate-400 hover:bg-white/10', onClick: () => setShowTerms(false)}, '閉じる'),
                        button({className: 'px-4 py-2 rounded-lg btn-gradient', onClick: () => { setRegAgreed(true); setShowTerms(false); }}, '同意する')
                    )
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
        useEffect(() => { const initialDb = AppDB.get(); setDb(initialDb); const sess = sessionStorage.getItem(SESS_KEY); if (sess && initialDb.users[sess]) setUser(sess); }, []);
        const handleLogin = (u) => { sessionStorage.setItem(SESS_KEY, u); setUser(u); };
        const handleLogout = () => { sessionStorage.removeItem(SESS_KEY); setUser(null); };
        const handleUpdateDB = (newDb) => { setDb(newDb); AppDB.save(newDb); };
        if (!db) return div({className: 'flex h-screen items-center justify-center'}, el(LoadingCircle));
        if (!user) return el(AuthBox, { onLogin: handleLogin });
        return el(MainApp, { db, user, onUpdateDB: handleUpdateDB, onLogout: handleLogout });
    };

    ReactDOM.createRoot(document.getElementById('root')).render(el(App));
})();
