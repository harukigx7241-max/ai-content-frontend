'use strict';
// ============================================================
//  app.js – AI Content Pro フロントエンド (React 18, No-JSX)
// ============================================================

// ── React helpers ─────────────────────────────────────────
const { createElement: ce, useState, useEffect, useRef, useCallback, useMemo } = React;
const e = (tag, props, ...c) => ce(tag, props, ...c);
const div = (p, ...c) => e('div', p, ...c);
const span = (p, ...c) => e('span', p, ...c);
const p = (props, ...c) => e('p', props, ...c);
const h1 = (props, ...c) => e('h1', props, ...c);
const h2 = (props, ...c) => e('h2', props, ...c);
const h3 = (props, ...c) => e('h3', props, ...c);
const button = (props, ...c) => e('button', props, ...c);
const input = (props) => e('input', props);
const textarea = (props) => e('textarea', props);
const select = (props, ...c) => e('select', props, ...c);
const option = (props, ...c) => e('option', props, ...c);
const label = (props, ...c) => e('label', props, ...c);
const a = (props, ...c) => e('a', props, ...c);
const ul = (props, ...c) => e('ul', props, ...c);
const li = (props, ...c) => e('li', props, ...c);
const nav = (props, ...c) => e('nav', props, ...c);
const header = (props, ...c) => e('header', props, ...c);
const strong = (props, ...c) => e('strong', props, ...c);
const table = (props, ...c) => e('table', props, ...c);
const thead = (props, ...c) => e('thead', props, ...c);
const tbody = (props, ...c) => e('tbody', props, ...c);
const tr = (props, ...c) => e('tr', props, ...c);
const th = (props, ...c) => e('th', props, ...c);
const td = (props, ...c) => e('td', props, ...c);
const section = (props, ...c) => e('section', props, ...c);
const form = (props, ...c) => e('form', props, ...c);

// ── API Client ─────────────────────────────────────────────
const API = {
  async req(method, path, body, token) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json',
                  ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(path, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  },
  login:    (e, pw)   => API.req('POST', '/api/auth/login',    { email:e, password:pw }),
  register: (e,pw,u,c)=> API.req('POST', '/api/auth/register', { email:e, password:pw, username:u, invite_code:c }),
  logout:   (t)       => API.req('POST', '/api/auth/logout',   null, t),
  me:       (t)       => API.req('GET',  '/api/user/me',       null, t),
  updSettings:(s,t)   => API.req('PUT',  '/api/user/settings', s, t),
  generate: (d, t)    => API.req('POST', '/api/generate',      d, t),
  magicGen: (d, t)    => API.req('POST', '/api/magic_generate',d, t),
  extractPersona:(txt,t)=>API.req('POST','/api/persona/extract',{text:txt},t),
  savePW:   (pw,v,t)  => API.req('POST', '/api/passphrase/save',{passphrase:pw,vals:v},t),
  loadPW:   (pw,t)    => API.req('POST', '/api/passphrase/load',{passphrase:pw},t),
  notices:  (t)       => API.req('GET',  '/api/notices',       null, t),
  adminLogin:(pw)     => API.req('POST', '/api/admin/login',   {password:pw}),
  adminStats:(t)      => API.req('GET',  '/api/admin/stats',   null, t),
  adminInvites:(t)    => API.req('GET',  '/api/admin/invites', null, t),
  adminCreateInvite:(t)=>API.req('POST', '/api/admin/invite',  {}, t),
  adminUpdateUser:(id,d,t)=>API.req('PUT',`/api/admin/user/${id}`,d,t),
  adminNotice:(msg,type,t)=>API.req('POST','/api/admin/notice',{message:msg,type},t),
};

// ── Utilities ──────────────────────────────────────────────
function parseOutput(text) {
  const sectionRegex = /---【(.+?)】---/g;
  const parts = text.split(sectionRegex);
  if (parts.length < 3) return null;
  const sections = [];
  for (let i = 1; i < parts.length; i += 2) {
    sections.push({ name: parts[i], content: (parts[i+1] || '').trim() });
  }
  return sections;
}

function checkCompliance(text) {
  if (!text) return [];
  return COMPLIANCE_NG_WORDS.filter(w => text.includes(w));
}

function maskApiKey(key) {
  if (!key || key.length < 8) return key;
  return key.substring(0, 6) + '****' + key.substring(key.length - 4);
}

// ── Toast system ───────────────────────────────────────────
let _toastId = 0;
let _toastSetFn = null;
function toast(msg, type = 'success') {
  if (!_toastSetFn) return;
  const id = ++_toastId;
  _toastSetFn(prev => [...prev, { id, msg, type }]);
  setTimeout(() => _toastSetFn(prev => prev.filter(t => t.id !== id)), 3200);
}

function ToastContainer() {
  const [toasts, setToasts] = useState([]);
  useEffect(() => { _toastSetFn = setToasts; }, []);
  return div({ style: { position:'fixed', top:20, right:20, zIndex:9999, display:'flex', flexDirection:'column', gap:8, pointerEvents:'none' } },
    ...toasts.map(t =>
      div({ key: t.id, className: `toast ${t.type}`, style:{display:'flex',alignItems:'center',gap:8} },
        span({}, t.type === 'success' ? '✅' : t.type === 'error' ? '❌' : t.type === 'warning' ? '⚠️' : 'ℹ️'),
        span({}, t.msg)
      )
    )
  );
}

// ── Spinner ────────────────────────────────────────────────
function Spinner() {
  return div({ className: 'spinner' });
}

// ── Auth Page ──────────────────────────────────────────────
function AuthPage({ onLogin }) {
  const [tab, setTab] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await API.login(email, password);
      localStorage.setItem('aicp_token', data.token);
      onLogin(data.user, data.token);
      toast('ログインしました！', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setLoading(false); }
  }

  async function handleRegister(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await API.register(email, password, username, inviteCode);
      localStorage.setItem('aicp_token', data.token);
      onLogin(data.user, data.token);
      toast('アカウントを作成しました！', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setLoading(false); }
  }

  async function handleAdminLogin(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await API.adminLogin(adminPassword);
      localStorage.setItem('aicp_token', data.token);
      onLogin(data.user, data.token);
      toast('管理者としてログインしました', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setLoading(false); }
  }

  return div({ className: 'auth-bg', style:{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',padding:'20px'} },
    div({ style:{width:'100%',maxWidth:'420px'} },
      // Logo
      div({ style:{textAlign:'center',marginBottom:'32px'} },
        div({ style:{fontSize:'48px',marginBottom:'8px'} }, '🤖'),
        h1({ className:'gradient-text', style:{fontSize:'28px',fontWeight:800,margin:0} }, 'AI Content Pro'),
        p({ style:{color:'#64748b',marginTop:'4px',fontSize:'14px'} }, '日本特化型 AIコンテンツ生成SaaS')
      ),
      // Card
      div({ className:'glass', style:{padding:'32px'} },
        // Tabs
        div({ style:{display:'flex',gap:'4px',marginBottom:'24px',background:'#0d0d1a',borderRadius:'10px',padding:'4px'} },
          ...[['login','ログイン'],['register','新規登録'],['admin','管理者']].map(([id, name]) =>
            button({ key:id, onClick:()=>setTab(id),
              style:{flex:1,padding:'8px',borderRadius:'8px',border:'none',cursor:'pointer',fontSize:'13px',fontWeight:600,
                     background: tab===id ? '#7c3aed' : 'transparent',
                     color: tab===id ? 'white' : '#64748b',
                     transition:'all .15s'} }, name)
          )
        ),

        tab === 'login' && form({ onSubmit: handleLogin, style:{display:'flex',flexDirection:'column',gap:'16px'} },
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'4px'} }, 'メールアドレス'),
            input({ type:'email', value:email, onChange:ev=>setEmail(ev.target.value),
              className:'field-input', placeholder:'you@example.com', required:true })
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'4px'} }, 'パスワード'),
            input({ type:'password', value:password, onChange:ev=>setPassword(ev.target.value),
              className:'field-input', placeholder:'••••••••', required:true })
          ),
          button({ type:'submit', className:'btn-brand', disabled:loading, style:{padding:'12px',fontSize:'15px',width:'100%'} },
            loading ? '...ログイン中' : '🚀 ログイン')
        ),

        tab === 'register' && form({ onSubmit: handleRegister, style:{display:'flex',flexDirection:'column',gap:'16px'} },
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'4px'} }, 'ニックネーム'),
            input({ type:'text', value:username, onChange:ev=>setUsername(ev.target.value),
              className:'field-input', placeholder:'例: さくらさん', required:true })
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'4px'} }, 'メールアドレス'),
            input({ type:'email', value:email, onChange:ev=>setEmail(ev.target.value),
              className:'field-input', placeholder:'you@example.com', required:true })
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'4px'} }, 'パスワード'),
            input({ type:'password', value:password, onChange:ev=>setPassword(ev.target.value),
              className:'field-input', placeholder:'8文字以上推奨', required:true })
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'4px'} }, '招待コード'),
            input({ type:'text', value:inviteCode, onChange:ev=>setInviteCode(ev.target.value),
              className:'field-input', placeholder:'XXXXXXXX', required:true, style:{textTransform:'uppercase'} })
          ),
          button({ type:'submit', className:'btn-brand', disabled:loading, style:{padding:'12px',fontSize:'15px',width:'100%'} },
            loading ? '...登録中' : '✨ アカウントを作成')
        ),

        tab === 'admin' && form({ onSubmit: handleAdminLogin, style:{display:'flex',flexDirection:'column',gap:'16px'} },
          p({ style:{color:'#94a3b8',fontSize:'13px',textAlign:'center'} }, '管理者専用ログイン'),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'4px'} }, '管理者パスワード'),
            input({ type:'password', value:adminPassword, onChange:ev=>setAdminPassword(ev.target.value),
              className:'field-input', placeholder:'管理者パスワード', required:true })
          ),
          button({ type:'submit', className:'btn-brand', disabled:loading, style:{padding:'12px',fontSize:'15px',width:'100%',background:'linear-gradient(135deg,#dc2626,#7f1d1d)'} },
            loading ? '...ログイン中' : '🔑 管理者ログイン')
        )
      )
    )
  );
}

// ── Sidebar ────────────────────────────────────────────────
function Sidebar({ currentTool, onSelectTool, isOpen, onClose }) {
  const [expandedCat, setExpandedCat] = useState('note');
  const toolsByCategory = useMemo(() => {
    const map = {};
    CATEGORIES.forEach(c => { map[c.id] = TOOLS.filter(t => t.category === c.id); });
    return map;
  }, []);

  return div({
    className: 'sidebar',
    style:{ width:260, minHeight:'100vh', background:'#13132b',
            borderRight:'1px solid rgba(124,58,237,.15)',
            paddingBottom:24, overflowY:'auto',
            position:'fixed', top:60, left:0, bottom:0, zIndex:30 }
  },
    div({ style:{padding:'16px 12px 8px'} },
      p({ style:{fontSize:'11px',fontWeight:700,color:'#475569',textTransform:'uppercase',letterSpacing:'.1em'} }, '🛠 ツール一覧')
    ),
    ...CATEGORIES.map(cat =>
      div({ key: cat.id },
        // Category header (clickable)
        div({
          onClick: () => setExpandedCat(expandedCat === cat.id ? null : cat.id),
          style:{ padding:'8px 16px', display:'flex', justifyContent:'space-between',
                  alignItems:'center', cursor:'pointer', userSelect:'none',
                  background: expandedCat === cat.id ? 'rgba(124,58,237,.08)' : 'transparent',
                  borderTop: '1px solid rgba(255,255,255,.04)' }
        },
          span({ style:{display:'flex',alignItems:'center',gap:'8px',fontSize:'12px',fontWeight:700,
                         color: expandedCat === cat.id ? '#c4b5fd' : '#64748b'} },
            span({}, cat.emoji), span({}, cat.name)
          ),
          span({ style:{fontSize:'10px',color:'#475569'} }, expandedCat === cat.id ? '▼' : '▶')
        ),
        // Tool list
        expandedCat === cat.id && div({ style:{paddingBottom:'4px'} },
          ...(toolsByCategory[cat.id] || []).map(tool =>
            div({
              key: tool.id,
              className: `tool-item ${currentTool?.id === tool.id ? 'active' : ''}`,
              onClick: () => { onSelectTool(tool); if(onClose) onClose(); }
            },
              span({ style:{fontSize:'16px'} }, tool.emoji),
              span({ style:{flex:1,lineHeight:1.3} }, tool.name)
            )
          )
        )
      )
    )
  );
}

// ── Tool Input Panel ───────────────────────────────────────
function ToolInputPanel({ tool, vals, onChange, onGenerate, onMagicGenerate, isGenerating, abTest, setAbTest, modelType, setModelType, user }) {
  if (!tool) return div({ style:{padding:32,textAlign:'center',color:'#475569'} },
    div({ style:{fontSize:'48px',marginBottom:'16px'} }, '👈'),
    p({ style:{fontSize:'16px'} }, 'サイドバーからツールを選んでください')
  );

  const allEmpty = tool.inputs.every(inp => !vals[inp.id] || !vals[inp.id].toString().trim());
  const someEmpty = !allEmpty && tool.inputs.some(inp => !vals[inp.id] || !vals[inp.id].toString().trim());

  return div({ style:{padding:'20px 24px',overflowY:'auto',flex:1} },
    // Tool header
    div({ style:{marginBottom:'20px'} },
      div({ style:{display:'flex',alignItems:'center',gap:'10px',marginBottom:'4px'} },
        span({ style:{fontSize:'28px'} }, tool.emoji),
        h2({ style:{fontSize:'18px',fontWeight:800,color:'#e2e8f0',margin:0} }, tool.name)
      ),
      p({ style:{color:'#64748b',fontSize:'13px',margin:0} }, tool.description)
    ),

    // Input fields
    div({ style:{display:'flex',flexDirection:'column',gap:'16px',marginBottom:'24px'} },
      ...tool.inputs.map(inp =>
        div({ key: inp.id },
          label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'6px'} },
            inp.label,
            span({ style:{color:'#475569',fontWeight:400,marginLeft:4} }, '（空欄でAIが設定）')
          ),
          inp.type === 'textarea' ?
            textarea({ value: vals[inp.id] || '', onChange: ev => onChange(inp.id, ev.target.value),
              className:'field-input', placeholder: inp.placeholder || '', rows:3 }) :
          inp.type === 'select' ?
            select({ value: vals[inp.id] || inp.options[0], onChange: ev => onChange(inp.id, ev.target.value),
              className:'field-input' },
              ...(inp.options || []).map(opt => option({ key:opt, value:opt }, opt))
            ) :
            input({ type: inp.type || 'text', value: vals[inp.id] || '',
              onChange: ev => onChange(inp.id, ev.target.value),
              className:'field-input', placeholder: inp.placeholder || '' })
        )
      )
    ),

    // Options bar
    div({ style:{display:'flex',flexWrap:'wrap',gap:'12px',marginBottom:'20px',alignItems:'center'} },
      // A/B test toggle
      label({ style:{display:'flex',alignItems:'center',gap:'8px',cursor:'pointer',userSelect:'none'} },
        input({ type:'checkbox', checked:abTest, onChange:ev=>setAbTest(ev.target.checked),
          style:{accentColor:'#7c3aed',width:16,height:16} }),
        span({ style:{fontSize:'13px',color:'#94a3b8',fontWeight:600} }, '🔀 A/Bテスト')
      ),
      // Model selector
      div({ style:{display:'flex',gap:'6px',marginLeft:'auto'} },
        ...[['free','⚡ 無料'],['pro','👑 プロ']].map(([val,label_]) =>
          button({ key:val, onClick:()=>setModelType(val),
            style:{padding:'6px 12px',borderRadius:'20px',border:'1px solid',fontSize:'12px',fontWeight:600,cursor:'pointer',
                   borderColor: modelType===val ? '#7c3aed' : '#1e1e3f',
                   background: modelType===val ? 'rgba(124,58,237,.3)' : 'transparent',
                   color: modelType===val ? '#a78bfa' : '#475569',
                   transition:'all .15s'} }, label_)
        )
      )
    ),

    // Buttons
    div({ style:{display:'flex',gap:'10px',flexWrap:'wrap'} },
      // Main generate
      button({
        className:'btn-brand', onClick: onGenerate,
        disabled: isGenerating,
        style:{flex:1,minWidth:140,padding:'13px 20px',fontSize:'15px',display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}
      },
        isGenerating ? ce(Spinner) : span({}, '⚡'),
        isGenerating ? '生成中...' : '生成する'
      ),
      // Magic generate
      button({
        className:'btn-magic', onClick: onMagicGenerate,
        disabled: isGenerating,
        style:{flex:1,minWidth:140,padding:'13px 20px',fontSize:'14px',display:'flex',alignItems:'center',justifyContent:'center',gap:'8px'}
      },
        isGenerating ? ce(Spinner) : span({}, '🌟'),
        isGenerating ? '魔法実行中...' : (allEmpty ? '✨ 神丸投げ' : (someEmpty ? '🤖 自動補完' : '✨ 神丸投げ'))
      )
    ),

    // Credit info
    user && !user.is_admin && div({ style:{marginTop:12,padding:'8px 12px',borderRadius:8,background:'rgba(245,158,11,.08)',border:'1px solid rgba(245,158,11,.15)',fontSize:'12px',color:'#94a3b8'} },
      span({},
        user.api_keys && (user.api_keys.openai || user.api_keys.anthropic || user.api_keys.google)
          ? '🔑 APIキー登録済み（クレジット消費なし）'
          : `💳 残クレジット: ${user.credits || 0}枚`
      )
    )
  );
}

// ── Preview Panel ──────────────────────────────────────────
function PreviewPanel({ output, isGenerating, onCopy, onRefine, onAbTest }) {
  const [activeSection, setActiveSection] = useState('all');
  const sections = useMemo(() => output ? parseOutput(output) : null, [output]);
  const ngWords = useMemo(() => checkCompliance(output), [output]);

  const displayText = useMemo(() => {
    if (!output) return '';
    if (!sections || activeSection === 'all') return output;
    const sec = sections.find(s => s.name === activeSection);
    return sec ? sec.content : output;
  }, [output, sections, activeSection]);

  useEffect(() => { setActiveSection('all'); }, [output]);

  return div({ style:{display:'flex',flexDirection:'column',height:'100%'} },
    // Header
    div({ style:{padding:'16px 24px',borderBottom:'1px solid rgba(255,255,255,.05)',display:'flex',alignItems:'center',justifyContent:'space-between'} },
      span({ style:{fontWeight:700,fontSize:'14px',color:'#94a3b8'} }, '👁 プレビュー'),
      output && div({ style:{display:'flex',gap:'8px'} },
        button({ onClick:()=>onCopy(displayText), style:{padding:'6px 12px',borderRadius:'6px',background:'rgba(124,58,237,.2)',border:'1px solid rgba(124,58,237,.3)',color:'#a78bfa',fontSize:'12px',fontWeight:600,cursor:'pointer'} }, '📋 コピー'),
        button({ onClick:onRefine, style:{padding:'6px 12px',borderRadius:'6px',background:'rgba(6,182,212,.1)',border:'1px solid rgba(6,182,212,.2)',color:'#22d3ee',fontSize:'12px',fontWeight:600,cursor:'pointer'} }, '✨ 推敲')
      )
    ),

    // Content
    div({ style:{flex:1,overflowY:'auto',padding:'20px 24px'} },
      // Compliance alert
      ngWords.length > 0 && div({ className:'compliance-alert' },
        div({ style:{display:'flex',alignItems:'center',gap:'8px',marginBottom:'6px'} },
          span({ style:{fontSize:'20px'} }, '🚨'),
          strong({ style:{color:'#f87171',fontSize:'13px'} }, 'コンプライアンス警告')
        ),
        p({ style:{color:'#fca5a5',fontSize:'12px',margin:0} },
          `以下のNGワードが含まれています: ${ngWords.join('、')}`
        ),
        p({ style:{color:'#94a3b8',fontSize:'11px',marginTop:4,marginBottom:0} }, '薬機法・景表法に抵触する可能性があります。表現を修正してください。')
      ),

      // Section tabs
      sections && div({ style:{display:'flex',gap:'6px',marginBottom:'16px',flexWrap:'wrap'} },
        div({ className:`section-tab ${activeSection==='all'?'active':''}`,
              onClick:()=>setActiveSection('all') }, '📄 全体'),
        ...sections.map(s =>
          div({ key:s.name, className:`section-tab ${activeSection===s.name?'active':''}`,
                onClick:()=>setActiveSection(s.name) }, `【${s.name}】`)
        )
      ),

      // Loading shimmer
      isGenerating && !output && div({},
        ...[100,80,95,70,85].map((w,i) => div({ key:i, className:'shimmer', style:{width:`${w}%`} }))
      ),

      // Output text
      output && div({ className:'preview-content fade-in', style:{whiteSpace:'pre-wrap'} }, displayText),

      // Empty state
      !output && !isGenerating && div({ style:{textAlign:'center',padding:'48px 24px',color:'#374151'} },
        div({ style:{fontSize:'56px',marginBottom:'12px'} }, '💬'),
        p({ style:{fontSize:'15px',color:'#475569'} }, 'ここに生成結果が表示されます'),
        p({ style:{fontSize:'13px',color:'#374151'} }, '左のフォームに入力して「生成する」か「✨ 神丸投げ」を押してください')
      )
    ),

    // Action buttons
    output && div({ style:{padding:'12px 24px',borderTop:'1px solid rgba(255,255,255,.05)',display:'flex',gap:'8px',flexWrap:'wrap'} },
      ...[
        ['📋 全体コピー', ()=>onCopy(output)],
        ['🔀 A/Bテスト', onAbTest],
        ['✂️ キャッチーに推敲', onRefine],
      ].map(([label_, fn]) =>
        button({ key:label_, onClick:fn,
          style:{padding:'7px 12px',borderRadius:'8px',background:'rgba(255,255,255,.04)',border:'1px solid rgba(255,255,255,.08)',color:'#94a3b8',fontSize:'12px',cursor:'pointer',transition:'all .15s'} },
          label_)
      )
    )
  );
}

// ── Settings Modal ─────────────────────────────────────────
function SettingsModal({ user, token, onClose, onUpdate }) {
  const [tab, setTab] = useState('keys');
  const [apiKeys, setApiKeys] = useState({
    openai: user?.api_keys?.openai || '',
    anthropic: user?.api_keys?.anthropic || '',
    google: user?.api_keys?.google || '',
  });
  const [persona, setPersona] = useState({
    base_personality: user?.settings?.persona?.base_personality || 'friendly',
    first_person: user?.settings?.persona?.first_person || '私',
    custom_style: user?.settings?.persona?.custom_style || '',
  });
  const [preferredAI, setPreferredAI] = useState(user?.settings?.preferred_ai || 'openai');
  const [personaText, setPersonaText] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [passphrase, setPassphrase] = useState('');
  const [loadPW, setLoadPW] = useState('');

  async function handleSave() {
    setSaving(true);
    try {
      const updated = await API.updSettings({
        api_keys: apiKeys,
        settings: { persona, preferred_ai: preferredAI },
      }, token);
      onUpdate(updated);
      toast('設定を保存しました', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setSaving(false); }
  }

  async function handleExtractPersona() {
    if (!personaText.trim()) return toast('文章を入力してください', 'warning');
    setExtracting(true);
    try {
      const r = await API.extractPersona(personaText, token);
      setPersona(prev => ({ ...prev, custom_style: r.persona }));
      toast('ペルソナを抽出しました', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setExtracting(false); }
  }

  async function handleSavePW() {
    if (!passphrase.trim()) return toast('合言葉を入力してください', 'warning');
    try {
      await API.savePW(passphrase, { persona, apiKeys }, token);
      toast('合言葉で設定を保存しました', 'success');
    } catch(err) { toast(err.message, 'error'); }
  }

  async function handleLoadPW() {
    if (!loadPW.trim()) return toast('合言葉を入力してください', 'warning');
    try {
      const r = await API.loadPW(loadPW, token);
      if (r.vals.persona) setPersona(r.vals.persona);
      if (r.vals.apiKeys) setApiKeys(r.vals.apiKeys);
      toast('設定を復元しました', 'success');
    } catch(err) { toast(err.message, 'error'); }
  }

  const tabs = [['keys','🔑 APIキー'],['persona','👤 ペルソナ'],['passphrase','🔐 合言葉']];

  return div({ className:'overlay-bg', onClick:e=>{if(e.target===e.currentTarget)onClose()} },
    div({ className:'modal-panel', style:{width:'min(580px,95vw)',maxHeight:'90vh',overflowY:'auto',padding:'0'} },
      // Modal header
      div({ style:{padding:'20px 24px',borderBottom:'1px solid rgba(255,255,255,.08)',display:'flex',justifyContent:'space-between',alignItems:'center'} },
        h2({ style:{margin:0,fontSize:'16px',fontWeight:700} }, '⚙️ 個人設定'),
        button({ onClick:onClose, style:{background:'none',border:'none',color:'#94a3b8',fontSize:'20px',cursor:'pointer',padding:'4px'} }, '✕')
      ),

      // Tabs
      div({ style:{display:'flex',borderBottom:'1px solid rgba(255,255,255,.06)',padding:'0 24px'} },
        ...tabs.map(([id,name]) =>
          button({ key:id, onClick:()=>setTab(id),
            style:{padding:'12px 16px',background:'none',border:'none',cursor:'pointer',fontSize:'13px',fontWeight:600,
                   color: tab===id ? '#a78bfa' : '#475569',
                   borderBottom: tab===id ? '2px solid #7c3aed' : '2px solid transparent',
                   transition:'all .15s'} }, name)
        )
      ),

      div({ style:{padding:'24px'} },
        // API Keys tab
        tab === 'keys' && div({ style:{display:'flex',flexDirection:'column',gap:'16px'} },
          p({ style:{color:'#94a3b8',fontSize:'13px',marginTop:0} },
            '🔑 APIキーを登録するとクレジット消費なしで無制限に利用できます（BYOK方式）'
          ),
          div({ style:{background:'rgba(245,158,11,.08)',border:'1px solid rgba(245,158,11,.2)',borderRadius:8,padding:'12px',fontSize:'12px',color:'#fbbf24'} },
            '⚠️ APIキーはサーバー上に暗号化して保存されます。フロントエンドには表示されません。'
          ),
          ...([
            ['openai', '🤖 OpenAI APIキー', 'sk-...'],
            ['anthropic', '🧠 Anthropic APIキー', 'sk-ant-...'],
            ['google', '🔍 Google APIキー', 'AIza...'],
          ]).map(([key, lbl, ph]) =>
            div({ key },
              label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'6px'} }, lbl),
              input({ type:'text', value:apiKeys[key], onChange:ev=>setApiKeys(prev=>({...prev,[key]:ev.target.value})),
                className:'field-input', placeholder:ph })
            )
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'6px'} }, '優先AI'),
            select({ value:preferredAI, onChange:ev=>setPreferredAI(ev.target.value), className:'field-input' },
              option({value:'openai'}, 'OpenAI (ChatGPT)'),
              option({value:'anthropic'}, 'Anthropic (Claude)'),
              option({value:'google'}, 'Google (Gemini)')
            )
          )
        ),

        // Persona tab
        tab === 'persona' && div({ style:{display:'flex',flexDirection:'column',gap:'16px'} },
          p({ style:{color:'#94a3b8',fontSize:'13px',marginTop:0} },
            '👤 ペルソナ設定で全ツールの文章がパーソナライズされます'
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'6px'} }, '一人称'),
            select({ value:persona.first_person, onChange:ev=>setPersona(p=>({...p,first_person:ev.target.value})), className:'field-input' },
              ...'私,僕,俺,自分,ウチ'.split(',').map(v_ => option({key:v_,value:v_}, v_))
            )
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'6px'} }, 'ベースの性格'),
            select({ value:persona.base_personality, onChange:ev=>setPersona(p=>({...p,base_personality:ev.target.value})), className:'field-input' },
              ...['friendly（親しみやすい）','professional（プロ・信頼感）','cool（クール・カリスマ）',
                  'energetic（熱血・エネルギッシュ）','mystical（神秘的・スピリチュアル）','comic（コミカル・エンタメ）']
                  .map(v_ => option({key:v_,value:v_.split('（')[0]}, v_))
            )
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'6px'} }, 'カスタムペルソナ（全ツールのシステムプロンプトに追加）'),
            textarea({ value:persona.custom_style, onChange:ev=>setPersona(p=>({...p,custom_style:ev.target.value})),
              className:'field-input', rows:4, placeholder:'例: あなたは独自の語り口を持ち、読者を引き込む文章を書くライターです。...' })
          ),
          // Auto-extract
          div({ style:{borderTop:'1px solid rgba(255,255,255,.06)',paddingTop:'16px'} },
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:'6px'} }, '🤖 自動抽出ツール（過去の文章を貼り付けてAI分析）'),
            textarea({ value:personaText, onChange:ev=>setPersonaText(ev.target.value),
              className:'field-input', rows:4, placeholder:'あなたの過去の投稿・記事・文章を貼り付けてください...' }),
            button({ onClick:handleExtractPersona, disabled:extracting,
              style:{marginTop:8,padding:'8px 16px',borderRadius:8,background:'rgba(6,182,212,.15)',border:'1px solid rgba(6,182,212,.3)',color:'#22d3ee',fontSize:'13px',cursor:'pointer',fontWeight:600} },
              extracting ? '分析中...' : '🔍 ペルソナを自動抽出')
          )
        ),

        // Passphrase tab
        tab === 'passphrase' && div({ style:{display:'flex',flexDirection:'column',gap:'16px'} },
          p({ style:{color:'#94a3b8',fontSize:'13px',marginTop:0} },
            '🔐 合言葉で現在の設定を保存し、別の端末や別セッションで復元できます'
          ),
          div({ style:{borderRadius:8,background:'rgba(124,58,237,.08)',border:'1px solid rgba(124,58,237,.2)',padding:'16px'} },
            h3({ style:{margin:'0 0 8px',fontSize:'13px',fontWeight:700,color:'#a78bfa'} }, '設定を保存'),
            div({ style:{display:'flex',gap:'8px'} },
              input({ type:'text', value:passphrase, onChange:ev=>setPassphrase(ev.target.value),
                className:'field-input', placeholder:'合言葉を入力（例: さくら2024）', style:{flex:1} }),
              button({ onClick:handleSavePW,
                style:{padding:'8px 16px',background:'#7c3aed',border:'none',borderRadius:8,color:'white',cursor:'pointer',fontWeight:600,whiteSpace:'nowrap'} },
                '💾 保存')
            )
          ),
          div({ style:{borderRadius:8,background:'rgba(6,182,212,.06)',border:'1px solid rgba(6,182,212,.15)',padding:'16px'} },
            h3({ style:{margin:'0 0 8px',fontSize:'13px',fontWeight:700,color:'#22d3ee'} }, '設定を復元'),
            div({ style:{display:'flex',gap:'8px'} },
              input({ type:'text', value:loadPW, onChange:ev=>setLoadPW(ev.target.value),
                className:'field-input', placeholder:'保存時の合言葉を入力', style:{flex:1} }),
              button({ onClick:handleLoadPW,
                style:{padding:'8px 16px',background:'rgba(6,182,212,.2)',border:'1px solid rgba(6,182,212,.4)',borderRadius:8,color:'#22d3ee',cursor:'pointer',fontWeight:600,whiteSpace:'nowrap'} },
                '🔄 復元')
            )
          )
        ),

        // Save button (keys and persona)
        (tab === 'keys' || tab === 'persona') && button({ onClick:handleSave, disabled:saving,
          className:'btn-brand', style:{width:'100%',padding:'12px',fontSize:'14px',marginTop:8} },
          saving ? '保存中...' : '💾 設定を保存'
        )
      )
    )
  );
}

// ── Admin Dashboard ─────────────────────────────────────────
function AdminDashboard({ token, onClose }) {
  const [stats, setStats] = useState(null);
  const [invites, setInvites] = useState([]);
  const [tab, setTab] = useState('stats');
  const [loading, setLoading] = useState(true);
  const [noticeMsg, setNoticeMsg] = useState('');
  const [noticeType, setNoticeType] = useState('notice');

  useEffect(() => {
    async function load() {
      try {
        const [s, inv] = await Promise.all([API.adminStats(token), API.adminInvites(token)]);
        setStats(s);
        setInvites(inv.invites || []);
      } catch(err) { toast(err.message, 'error'); }
      finally { setLoading(false); }
    }
    load();
  }, [token]);

  async function createInvite() {
    try {
      const r = await API.adminCreateInvite(token);
      toast(`招待コード発行: ${r.code}`, 'success');
      const inv = await API.adminInvites(token);
      setInvites(inv.invites || []);
    } catch(err) { toast(err.message, 'error'); }
  }

  async function updateUser(userId, updates) {
    try {
      await API.adminUpdateUser(userId, updates, token);
      const s = await API.adminStats(token);
      setStats(s);
      toast('ユーザーを更新しました', 'success');
    } catch(err) { toast(err.message, 'error'); }
  }

  async function sendNotice() {
    if (!noticeMsg.trim()) return toast('メッセージを入力してください', 'warning');
    try {
      await API.adminNotice(noticeMsg, noticeType, token);
      toast('お知らせを送信しました', 'success');
      setNoticeMsg('');
    } catch(err) { toast(err.message, 'error'); }
  }

  const tabs = [['stats','📊 統計'],['users','👥 ユーザー'],['invites','🎫 招待コード'],['notice','📣 お知らせ']];

  return div({ className:'overlay-bg', onClick:ev=>{if(ev.target===ev.currentTarget)onClose()} },
    div({ className:'modal-panel', style:{width:'min(900px,96vw)',maxHeight:'92vh',overflowY:'auto',padding:0} },
      div({ style:{padding:'20px 24px',borderBottom:'1px solid rgba(255,255,255,.08)',display:'flex',justifyContent:'space-between',alignItems:'center'} },
        h2({ style:{margin:0,fontSize:'16px',fontWeight:700} }, '🛡 管理者ダッシュボード'),
        button({ onClick:onClose, style:{background:'none',border:'none',color:'#94a3b8',fontSize:'20px',cursor:'pointer'} }, '✕')
      ),

      div({ style:{display:'flex',borderBottom:'1px solid rgba(255,255,255,.06)',padding:'0 24px',overflowX:'auto'} },
        ...tabs.map(([id,nm]) =>
          button({ key:id, onClick:()=>setTab(id),
            style:{padding:'12px 16px',background:'none',border:'none',cursor:'pointer',fontSize:'13px',fontWeight:600,whiteSpace:'nowrap',
                   color:tab===id?'#a78bfa':'#475569',
                   borderBottom:tab===id?'2px solid #7c3aed':'2px solid transparent'} }, nm)
        )
      ),

      div({ style:{padding:'24px'} },
        loading && div({ style:{textAlign:'center',padding:40} }, ce(Spinner)),

        // Stats
        !loading && tab === 'stats' && stats && div({ style:{display:'flex',flexDirection:'column',gap:'20px'} },
          div({ style:{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(160px,1fr))',gap:12} },
            ...[
              ['👥 総ユーザー数', stats.total_users, '#7c3aed'],
              ['✅ アクティブ', stats.active_users, '#059669'],
              ['⚡ 総生成回数', stats.total_generations, '#2563eb'],
              ['💴 推定コスト', `¥${stats.estimated_cost_jpy?.toLocaleString()}`, '#d97706'],
            ].map(([label_, val, color]) =>
              div({ key:label_, style:{background:'rgba(255,255,255,.04)',borderRadius:10,padding:'16px',textAlign:'center',border:`1px solid ${color}33`} },
                p({ style:{color:'#64748b',fontSize:'11px',fontWeight:700,margin:'0 0 4px'} }, label_),
                p({ style:{color,fontSize:'24px',fontWeight:800,margin:0} }, val)
              )
            )
          )
        ),

        // Users
        !loading && tab === 'users' && stats && div({ style:{overflowX:'auto'} },
          table({ style:{width:'100%',borderCollapse:'collapse',fontSize:'12px'} },
            thead({},
              tr({ style:{borderBottom:'1px solid rgba(255,255,255,.08)'} },
                ...'名前,メール,ステータス,クレジット,生成回数,推定コスト,操作'.split(',').map(h_ =>
                  th({ key:h_, style:{padding:'8px 12px',textAlign:'left',color:'#64748b',fontWeight:700,whiteSpace:'nowrap'} }, h_)
                )
              )
            ),
            tbody({},
              ...(stats.users || []).map(u =>
                tr({ key:u.id, style:{borderBottom:'1px solid rgba(255,255,255,.04)'} },
                  td({ style:{padding:'8px 12px',color:'#e2e8f0'} }, u.username || '—'),
                  td({ style:{padding:'8px 12px',color:'#94a3b8'} }, u.email),
                  td({ style:{padding:'8px 12px'} },
                    span({ style:{padding:'2px 8px',borderRadius:12,fontSize:'11px',fontWeight:700,
                                  background:u.status==='active'?'rgba(5,150,105,.2)':'rgba(220,38,38,.2)',
                                  color:u.status==='active'?'#34d399':'#f87171'} }, u.status)
                  ),
                  td({ style:{padding:'8px 12px',color:'#fbbf24',textAlign:'right'} }, u.credits),
                  td({ style:{padding:'8px 12px',color:'#94a3b8',textAlign:'right'} }, u.total_generations),
                  td({ style:{padding:'8px 12px',color:'#94a3b8',textAlign:'right'} }, `¥${u.cost_jpy}`),
                  td({ style:{padding:'8px 12px'} },
                    div({ style:{display:'flex',gap:4} },
                      button({ onClick:()=>updateUser(u.id,{credits:(u.credits||0)+100}),
                        style:{padding:'4px 8px',borderRadius:6,background:'rgba(5,150,105,.2)',border:'none',color:'#34d399',fontSize:'11px',cursor:'pointer'} }, '+100'),
                      button({ onClick:()=>updateUser(u.id,{status:u.status==='active'?'frozen':'active'}),
                        style:{padding:'4px 8px',borderRadius:6,background:'rgba(220,38,38,.15)',border:'none',color:'#f87171',fontSize:'11px',cursor:'pointer'} },
                        u.status==='active'?'凍結':'解除')
                    )
                  )
                )
              )
            )
          )
        ),

        // Invites
        !loading && tab === 'invites' && div({ style:{display:'flex',flexDirection:'column',gap:'16px'} },
          button({ onClick:createInvite, className:'btn-brand', style:{padding:'10px 20px',fontSize:'14px',alignSelf:'flex-start'} }, '＋ 招待コードを発行'),
          div({ style:{overflowX:'auto'} },
            table({ style:{width:'100%',borderCollapse:'collapse',fontSize:'12px'} },
              thead({},
                tr({ style:{borderBottom:'1px solid rgba(255,255,255,.08)'} },
                  ...['コード','作成日','使用状況'].map(h_ =>
                    th({ key:h_, style:{padding:'8px 12px',textAlign:'left',color:'#64748b',fontWeight:700} }, h_)
                  )
                )
              ),
              tbody({},
                ...invites.map(inv =>
                  tr({ key:inv.code, style:{borderBottom:'1px solid rgba(255,255,255,.04)'} },
                    td({ style:{padding:'8px 12px',fontFamily:'monospace',color:'#a78bfa',fontWeight:700,letterSpacing:2} }, inv.code),
                    td({ style:{padding:'8px 12px',color:'#64748b',fontSize:'11px'} }, inv.created_at?.substring(0,10) || '—'),
                    td({ style:{padding:'8px 12px'} },
                      span({ style:{padding:'2px 8px',borderRadius:12,fontSize:'11px',fontWeight:700,
                                    background:inv.used_by?'rgba(220,38,38,.2)':'rgba(5,150,105,.2)',
                                    color:inv.used_by?'#f87171':'#34d399'} },
                        inv.used_by ? `使用済み` : '未使用'
                      )
                    )
                  )
                )
              )
            )
          )
        ),

        // Notice
        !loading && tab === 'notice' && div({ style:{display:'flex',flexDirection:'column',gap:'16px'} },
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:6} }, 'お知らせの種類'),
            select({ value:noticeType, onChange:ev=>setNoticeType(ev.target.value), className:'field-input' },
              option({value:'notice'}, '📣 お知らせ（バナー表示）'),
              option({value:'popup'}, '🚨 強制ポップアップ（次回ログイン時）')
            )
          ),
          div({},
            label({ style:{display:'block',fontSize:'12px',fontWeight:600,color:'#94a3b8',marginBottom:6} }, 'メッセージ内容'),
            textarea({ value:noticeMsg, onChange:ev=>setNoticeMsg(ev.target.value),
              className:'field-input', rows:5, placeholder:'全ユーザーに送るメッセージを入力...' })
          ),
          button({ onClick:sendNotice, className:'btn-brand', style:{padding:'12px',fontSize:'14px'} }, '📣 送信する')
        )
      )
    )
  );
}

// ── Notice Banner ──────────────────────────────────────────
function NoticeBanner({ notices }) {
  const [dismissed, setDismissed] = useState([]);
  const visible = (notices || []).filter(n => !dismissed.includes(n.id)).slice(0, 1);
  if (!visible.length) return null;
  const notice = visible[0];
  return div({ style:{padding:'10px 24px',background:'linear-gradient(135deg,rgba(37,99,235,.2),rgba(124,58,237,.15))',borderBottom:'1px solid rgba(124,58,237,.2)',display:'flex',alignItems:'center',justifyContent:'space-between',fontSize:'13px',color:'#bfdbfe'} },
    span({}, `📣 ${notice.message}`),
    button({ onClick:()=>setDismissed(p=>[...p,notice.id]),
      style:{background:'none',border:'none',color:'#64748b',cursor:'pointer',fontSize:'18px',padding:'0 4px'} }, '✕')
  );
}

// ── Main App ───────────────────────────────────────────────
function MainApp({ user: initialUser, token, onLogout }) {
  const [user, setUser] = useState(initialUser);
  const [currentTool, setCurrentTool] = useState(TOOLS[0]);
  const [vals, setVals] = useState({});
  const [output, setOutput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [abTest, setAbTest] = useState(false);
  const [modelType, setModelType] = useState(user?.settings?.default_model || 'free');
  const [mobileTab, setMobileTab] = useState('input');
  const [showSettings, setShowSettings] = useState(false);
  const [showAdmin, setShowAdmin] = useState(false);
  const [notices, setNotices] = useState([]);

  useEffect(() => {
    API.notices(token).then(r => setNotices(r.notices || [])).catch(() => {});
  }, [token]);

  const handleValChange = useCallback((id, val) => {
    setVals(prev => ({ ...prev, [id]: val }));
  }, []);

  const handleToolSelect = useCallback((tool) => {
    setCurrentTool(tool);
    setVals({});
    setOutput('');
    setMobileTab('input');
  }, []);

  async function handleGenerate() {
    if (!currentTool) return;
    setIsGenerating(true);
    setOutput('');
    try {
      const messages = currentTool.buildMessages(vals);
      const r = await API.generate({ tool_id: currentTool.id, messages, ab_test: abTest, model_type: modelType }, token);
      setOutput(r.result);
      if (!user.api_keys?.openai && !user.api_keys?.anthropic && !user.api_keys?.google) {
        setUser(prev => ({ ...prev, credits: r.credits }));
      }
      setMobileTab('preview');
      toast('生成完了！', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setIsGenerating(false); }
  }

  async function handleMagicGenerate() {
    if (!currentTool) return;
    setIsGenerating(true);
    setOutput('');
    try {
      const r = await API.magicGen({ tool_id: currentTool.id, tool_name: currentTool.name, partial_vals: vals, model_type: modelType }, token);
      setOutput(r.result);
      if (!user.api_keys?.openai && !user.api_keys?.anthropic && !user.api_keys?.google) {
        setUser(prev => ({ ...prev, credits: r.credits }));
      }
      setMobileTab('preview');
      toast('✨ 神丸投げ完了！', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setIsGenerating(false); }
  }

  function handleCopy(text) {
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => toast('コピーしました！', 'success')).catch(() => toast('コピーに失敗しました', 'error'));
  }

  async function handleRefine() {
    if (!output) return toast('先に文章を生成してください', 'warning');
    setIsGenerating(true);
    try {
      const messages = [
        { role: 'system', content: 'あなたは日本最高峰のコピーライターです。' },
        { role: 'user', content: `以下の文章をより魅力的・キャッチーに推敲してください。意図と内容は変えずに、表現を洗練させてください。\n\n${output}` },
      ];
      const r = await API.generate({ tool_id: 'refine', messages, ab_test: false, model_type: modelType }, token);
      setOutput(r.result);
      toast('推敲完了！', 'success');
    } catch(err) { toast(err.message, 'error'); }
    finally { setIsGenerating(false); }
  }

  function handleAbTest() {
    setAbTest(true);
    toast('A/Bテストモードをオンにして再生成します', 'info');
    setTimeout(handleGenerate, 300);
  }

  const hasByok = user?.api_keys && (user.api_keys.openai || user.api_keys.anthropic || user.api_keys.google);

  return div({ style:{minHeight:'100vh',display:'flex',flexDirection:'column'} },
    // Top navbar
    header({ style:{height:60,background:'#0d0d1a',borderBottom:'1px solid rgba(124,58,237,.2)',display:'flex',alignItems:'center',padding:'0 20px',gap:12,position:'sticky',top:0,zIndex:40} },
      // Logo
      div({ style:{display:'flex',alignItems:'center',gap:8,marginRight:'auto'} },
        span({ style:{fontSize:'22px'} }, '🤖'),
        span({ className:'gradient-text', style:{fontWeight:800,fontSize:'16px',whiteSpace:'nowrap'} }, 'AI Content Pro'),
        span({ style:{fontSize:'10px',background:'rgba(124,58,237,.2)',color:'#a78bfa',padding:'2px 8px',borderRadius:12,fontWeight:700,letterSpacing:1} }, 'v74')
      ),
      // Credits / BYOK badge
      div({ className:'credits-badge' },
        hasByok ? '🔑 BYOK' : `💳 ${user?.credits || 0}枚`
      ),
      // Settings
      button({ onClick:()=>setShowSettings(true),
        style:{background:'rgba(255,255,255,.05)',border:'1px solid rgba(255,255,255,.08)',borderRadius:8,color:'#94a3b8',padding:'7px 12px',cursor:'pointer',fontSize:'13px',fontWeight:600} }, '⚙️'),
      // Admin (if admin)
      user?.is_admin && button({ onClick:()=>setShowAdmin(true),
        style:{background:'rgba(239,68,68,.1)',border:'1px solid rgba(239,68,68,.2)',borderRadius:8,color:'#f87171',padding:'7px 12px',cursor:'pointer',fontSize:'13px',fontWeight:600} }, '🛡 管理'),
      // Logout
      button({ onClick:onLogout,
        style:{background:'none',border:'1px solid rgba(255,255,255,.06)',borderRadius:8,color:'#64748b',padding:'7px 12px',cursor:'pointer',fontSize:'13px'} }, 'ログアウト')
    ),

    // Notice banner
    ce(NoticeBanner, { notices }),

    // Mobile tab bar
    div({ className:'mobile-tab-bar' },
      ...[['input','✏ 入力・設定'],['preview','👁 プレビュー']].map(([id,nm]) =>
        div({ key:id, className:`mobile-tab-btn ${mobileTab===id?'active':''}`, onClick:()=>setMobileTab(id) }, nm)
      )
    ),

    // Body
    div({ style:{display:'flex',flex:1,overflow:'hidden'} },
      // Sidebar (desktop)
      ce(Sidebar, { currentTool, onSelectTool:handleToolSelect }),

      // Main content
      div({ style:{marginLeft:260,flex:1,display:'flex',overflow:'hidden'} },
        // Input panel
        div({ style:{width:'min(480px,100%)',borderRight:'1px solid rgba(255,255,255,.05)',overflowY:'auto',
                      display: (typeof window !== 'undefined' && window.innerWidth < 768 && mobileTab !== 'input') ? 'none' : 'flex',
                      flexDirection:'column',paddingTop: typeof window !== 'undefined' && window.innerWidth < 768 ? 44 : 0} },
          ce(ToolInputPanel, {
            tool: currentTool, vals, onChange: handleValChange,
            onGenerate: handleGenerate, onMagicGenerate: handleMagicGenerate,
            isGenerating, abTest, setAbTest, modelType, setModelType, user,
          })
        ),

        // Preview panel
        div({ style:{flex:1,display:'flex',flexDirection:'column',overflow:'hidden',
                      display: typeof window !== 'undefined' && window.innerWidth < 768 && mobileTab !== 'preview' ? 'none' : 'flex',
                      paddingTop: typeof window !== 'undefined' && window.innerWidth < 768 ? 44 : 0} },
          ce(PreviewPanel, { output, isGenerating, onCopy:handleCopy, onRefine:handleRefine, onAbTest:handleAbTest })
        )
      )
    ),

    // Modals
    showSettings && ce(SettingsModal, { user, token, onClose:()=>setShowSettings(false), onUpdate:setUser }),
    showAdmin    && user?.is_admin && ce(AdminDashboard, { token, onClose:()=>setShowAdmin(false) })
  );
}

// ── Root App ───────────────────────────────────────────────
function App() {
  const [auth, setAuth] = useState({ token: null, user: null, loading: true });

  useEffect(() => {
    const token = localStorage.getItem('aicp_token');
    if (!token) { setAuth({ token:null, user:null, loading:false }); return; }
    API.me(token)
      .then(user => setAuth({ token, user, loading: false }))
      .catch(() => { localStorage.removeItem('aicp_token'); setAuth({ token:null, user:null, loading:false }); });
  }, []);

  function handleLogin(user, token) {
    setAuth({ token, user, loading: false });
  }

  function handleLogout() {
    API.logout(auth.token).catch(() => {});
    localStorage.removeItem('aicp_token');
    setAuth({ token: null, user: null, loading: false });
    toast('ログアウトしました', 'info');
  }

  if (auth.loading) {
    return div({ style:{minHeight:'100vh',display:'flex',alignItems:'center',justifyContent:'center',background:'#0d0d1a'} },
      div({ style:{textAlign:'center'} },
        div({ style:{fontSize:'48px',marginBottom:12} }, '🤖'),
        ce(Spinner),
        p({ style:{color:'#475569',marginTop:12} }, '読み込み中...')
      )
    );
  }

  return div({},
    ce(ToastContainer),
    auth.user
      ? ce(MainApp, { user: auth.user, token: auth.token, onLogout: handleLogout })
      : ce(AuthPage, { onLogin: handleLogin })
  );
}

// ── Mount ──────────────────────────────────────────────────
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(ce(App));
