html = open('static/index.html').read() if False else r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>CoParent AI</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--night:#0f0e0d;--dusk:#1c1917;--ember:#2c2420;--bronze:#8b5e3c;--gold:#c9943a;--cream:#f5f0e8;--mist:#e8e2d9;--fog:#c4bdb4;--sage:#4a7c59;--sage-dim:#2d4d38;--r:20px;}
body{font-family:'Jost',sans-serif;background:var(--night);color:var(--cream);min-height:100dvh;font-size:15px;line-height:1.6;overflow-x:hidden;}
header{position:sticky;top:0;z-index:100;background:rgba(15,14,13,.92);backdrop-filter:blur(12px);border-bottom:1px solid rgba(201,148,58,.15);padding:16px 20px;display:flex;align-items:center;gap:12px;}
.logo{font-family:'Cormorant Garamond',serif;font-size:24px;font-weight:500;background:linear-gradient(135deg,var(--gold),var(--cream));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.logo span{font-style:italic;}
#backBtn{background:none;border:none;color:var(--fog);font-size:20px;cursor:pointer;padding:0 4px;display:none;transition:color .2s;}
#backBtn.visible{display:block;}
#backBtn:hover{color:var(--gold);}
.screen{display:none;padding:28px 20px 80px;max-width:480px;margin:0 auto;position:relative;z-index:1;}
.screen.active{display:block;animation:fadeUp .3s ease both;}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
h2{font-family:'Cormorant Garamond',serif;font-size:34px;font-weight:500;line-height:1.2;margin-bottom:8px;}
h2 em{font-style:italic;color:var(--gold);}
.eyebrow{font-size:10px;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--gold);opacity:.75;margin-bottom:14px;}
.subtitle{color:var(--fog);font-size:13px;margin-bottom:32px;font-weight:300;letter-spacing:.02em;}
.card{background:var(--dusk);border:1px solid rgba(201,148,58,.1);border-radius:var(--r);padding:22px;margin-bottom:14px;transition:border-color .2s;}
.card:focus-within{border-color:rgba(201,148,58,.3);}
.card-label{font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);margin-bottom:16px;opacity:.75;}
label{display:block;font-size:12px;font-weight:500;color:var(--fog);margin-bottom:6px;letter-spacing:.03em;}
input,textarea,select{width:100%;padding:13px 16px;background:var(--ember);border:1px solid rgba(255,255,255,.07);border-radius:12px;font-family:'Jost',sans-serif;font-size:15px;color:var(--cream);outline:none;transition:border-color .2s;margin-bottom:16px;-webkit-appearance:none;}
input:focus,textarea:focus,select:focus{border-color:rgba(201,148,58,.45);}
input::placeholder,textarea::placeholder{color:rgba(196,189,180,.3);}
textarea{resize:none;min-height:100px;}
select{cursor:pointer;}
select option{background:var(--dusk);}
.btn{display:block;width:100%;padding:16px;border:none;border-radius:14px;font-family:'Jost',sans-serif;font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;transition:all .2s;text-align:center;}
.btn:active{transform:scale(.98);}
.btn-primary{background:linear-gradient(135deg,var(--bronze),var(--gold));color:var(--night);box-shadow:0 4px 24px rgba(201,148,58,.2);}
.btn-primary:hover{box-shadow:0 6px 32px rgba(201,148,58,.35);transform:translateY(-1px);}
.btn-green{background:linear-gradient(135deg,var(--sage-dim),var(--sage));color:var(--cream);margin-bottom:14px;box-shadow:0 4px 20px rgba(74,124,89,.15);}
.btn-green:hover{transform:translateY(-1px);}
.btn-ghost{background:transparent;color:var(--fog);border:1px solid rgba(255,255,255,.1);font-size:12px;padding:14px;}
.btn-ghost:hover{border-color:rgba(201,148,58,.3);color:var(--cream);}
.btn:disabled{opacity:.35;cursor:not-allowed;transform:none !important;box-shadow:none !important;}
.tag-list{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;min-height:4px;}
.tag{background:rgba(74,124,89,.18);border:1px solid rgba(74,124,89,.35);color:#7fbf93;border-radius:20px;padding:5px 12px;font-size:12px;font-weight:500;display:flex;align-items:center;gap:6px;}
.tag-x{cursor:pointer;font-size:15px;opacity:.55;transition:opacity .15s;}
.tag-x:hover{opacity:1;}
.tag-row{display:flex;gap:8px;}
.tag-row input{margin-bottom:0;flex:1;}
.tag-row button{padding:13px 16px;background:rgba(74,124,89,.25);border:1px solid rgba(74,124,89,.35);color:#7fbf93;border-radius:12px;font-size:18px;cursor:pointer;flex-shrink:0;}
.neg-item{display:flex;align-items:center;gap:14px;padding:18px 0;border-bottom:1px solid rgba(255,255,255,.05);cursor:pointer;transition:opacity .15s;}
.neg-item:hover{opacity:.7;}
.neg-item:last-child{border-bottom:none;}
.neg-icon{font-size:20px;flex-shrink:0;width:32px;text-align:center;opacity:.8;}
.neg-topic{font-weight:500;font-size:14px;}
.neg-meta{font-size:11px;color:var(--fog);margin-top:3px;}
.badge{margin-left:auto;font-size:10px;font-weight:600;padding:4px 10px;border-radius:20px;flex-shrink:0;letter-spacing:.06em;text-transform:uppercase;}
.badge-agreed{background:rgba(74,124,89,.2);color:#7fbf93;border:1px solid rgba(74,124,89,.3);}
.badge-progress{background:rgba(61,107,138,.2);color:#7db3d4;border:1px solid rgba(61,107,138,.3);}
.badge-deadlocked{background:rgba(155,74,74,.2);color:#d4827b;border:1px solid rgba(155,74,74,.3);}
.empty-state{text-align:center;padding:48px 0;color:var(--fog);}
.empty-icon{font-size:40px;margin-bottom:14px;opacity:.5;}
.empty-state p{font-size:13px;line-height:1.7;}
.transcript{display:flex;flex-direction:column;gap:16px;margin-bottom:28px;}
.bubble{max-width:90%;padding:14px 18px;border-radius:18px;font-size:13px;line-height:1.7;}
.bubble.agent-a{background:rgba(61,107,138,.18);border:1px solid rgba(61,107,138,.22);align-self:flex-start;border-bottom-left-radius:4px;}
.bubble.agent-b{background:rgba(155,74,74,.18);border:1px solid rgba(155,74,74,.22);align-self:flex-end;border-bottom-right-radius:4px;}
.bubble .who{font-size:10px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;margin-bottom:6px;}
.bubble.agent-a .who{color:#7db3d4;}
.bubble.agent-b .who{color:#d4827b;}
.agreement-box{background:rgba(74,124,89,.1);border:1px solid rgba(74,124,89,.28);border-radius:var(--r);padding:22px;margin-bottom:22px;}
.agreement-box h3{font-family:'Cormorant Garamond',serif;font-size:22px;font-weight:500;color:#7fbf93;margin-bottom:12px;}
.agreement-box p{font-size:13px;white-space:pre-wrap;line-height:1.8;color:var(--mist);}
.deadlock-box{background:rgba(155,74,74,.1);border:1px solid rgba(155,74,74,.28);border-radius:var(--r);padding:20px;margin-bottom:22px;}
.deadlock-box h3{font-family:'Cormorant Garamond',serif;color:#d4827b;font-size:22px;font-weight:500;margin-bottom:6px;}
.deadlock-box p{font-size:13px;color:var(--mist);}
.loading{display:none;flex-direction:column;align-items:center;justify-content:center;padding:80px 20px;gap:24px;text-align:center;}
.loading.visible{display:flex;}
.spinner-wrap{position:relative;width:56px;height:56px;}
.spinner{width:56px;height:56px;border:1.5px solid rgba(201,148,58,.1);border-top-color:var(--gold);border-radius:50%;animation:spin 1.2s cubic-bezier(.6,.1,.4,.9) infinite;}
@keyframes spin{to{transform:rotate(360deg)}}
.spinner-dot{position:absolute;top:50%;left:50%;width:6px;height:6px;background:var(--gold);border-radius:50%;transform:translate(-50%,-50%);animation:pulse 1.2s ease infinite;}
@keyframes pulse{0%,100%{opacity:.3;transform:translate(-50%,-50%) scale(.8)}50%{opacity:1;transform:translate(-50%,-50%) scale(1.2)}}
.loading-text{color:var(--fog);font-size:13px;letter-spacing:.04em;}
.loading-sub{color:rgba(196,189,180,.35);font-size:11px;margin-top:-18px;}
.toast{position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--dusk);border:1px solid rgba(201,148,58,.2);color:var(--cream);padding:12px 22px;border-radius:24px;font-size:13px;font-weight:500;transition:transform .3s cubic-bezier(.34,1.56,.64,1);z-index:999;white-space:nowrap;box-shadow:0 8px 32px rgba(0,0,0,.5);}
.toast.show{transform:translateX(-50%) translateY(0);}
.section-title{font-size:10px;font-weight:600;color:var(--gold);opacity:.65;text-transform:uppercase;letter-spacing:.12em;margin-bottom:16px;}
.result-topic{font-family:'Cormorant Garamond',serif;font-size:28px;font-weight:500;margin-bottom:22px;line-height:1.3;}
.hero{padding:32px 0 4px;}
</style>
</head>
<body>
<header>
  <button id="backBtn" onclick="goBack()">←</button>
  <div class="logo">Co<span>Parent</span> AI</div>
</header>
<div class="toast" id="toast"></div>
<div class="screen active" id="screen-welcome">
  <div class="hero">
    <div class="eyebrow">Beta</div>
    <h2>Let your <em>agents</em><br>do the talking.</h2>
    <p class="subtitle">AI negotiates co-parenting decisions so you don't have to.</p>
  </div>
  <div class="card">
    <div class="card-label">Children</div>
    <label>First names, comma separated</label>
    <input type="text" id="childNames" placeholder="e.g. Emma, Lucas" autocomplete="off">
  </div>
  <div class="card">
    <div class="card-label">Parent A — You</div>
    <label>Your name</label>
    <input type="text" id="parentAName" placeholder="Your name" autocomplete="off">
    <label>Your priorities</label>
    <div class="tag-list" id="tagsA"></div>
    <div class="tag-row">
      <input type="text" id="tagInputA" placeholder="e.g. School nights home by 7pm" autocomplete="off">
      <button onclick="addTag('A')">+</button>
    </div>
  </div>
  <div class="card">
    <div class="card-label">Parent B</div>
    <label>Their name</label>
    <input type="text" id="parentBName" placeholder="Other parent's name" autocomplete="off">
    <label>Their priorities</label>
    <div class="tag-list" id="tagsB"></div>
    <div class="tag-row">
      <input type="text" id="tagInputB" placeholder="e.g. Soccer on Saturdays" autocomplete="off">
      <button onclick="addTag('B')">+</button>
    </div>
  </div>
  <button class="btn btn-primary" onclick="setup()">Get started</button>
</div>
<div class="screen" id="screen-dashboard">
  <div class="hero">
    <div class="eyebrow">Dashboard</div>
    <h2>Hello, <em id="dashName">there</em></h2>
    <p class="subtitle" id="dashSubtitle"></p>
  </div>
  <button class="btn btn-green" onclick="goTo('screen-new-neg')">+ New negotiation</button>
  <div class="card">
    <div class="card-label">Negotiations</div>
    <div id="negList"><div class="empty-state"><div class="empty-icon">🕊</div><p>No negotiations yet.<br>Start one above.</p></div></div>
  </div>
</div>
<div class="screen" id="screen-new-neg">
  <div class="hero">
    <div class="eyebrow">New negotiation</div>
    <h2>What needs to be <em>decided?</em></h2>
    <p class="subtitle">Your agents will handle the rest.</p>
  </div>
  <div class="card">
    <label>Topic</label>
    <textarea id="negTopic" placeholder="e.g. Holiday schedule for Christmas and Thanksgiving"></textarea>
    <label>Who is raising this?</label>
    <select id="initiatedBy">
      <option value="parent_a" id="optA">Parent A</option>
      <option value="parent_b" id="optB">Parent B</option>
    </select>
  </div>
  <button class="btn btn-primary" id="startNegBtn" onclick="startNegotiation()">Start negotiation</button>
</div>
<div class="screen" id="screen-result">
  <div class="loading" id="loadingState">
    <div class="spinner-wrap"><div class="spinner"></div><div class="spinner-dot"></div></div>
    <p class="loading-text">Agents are negotiating...</p>
    <p class="loading-sub">This takes about 30 seconds</p>
  </div>
  <div id="resultContent" style="display:none">
    <p class="result-topic" id="resultTopic"></p>
    <div id="agreementBox" class="agreement-box" style="display:none">
      <h3>Agreement reached</h3>
      <p id="agreementText"></p>
    </div>
    <div id="deadlockBox" class="deadlock-box" style="display:none">
      <h3>Could not agree</h3>
      <p>Try adding more specific priorities or rephrasing the topic.</p>
    </div>
    <div class="section-title">Full transcript</div>
    <div class="transcript" id="transcriptEl"></div>
    <button class="btn btn-ghost" onclick="goTo('screen-dashboard')">Back</button>
  </div>
</div>
<script>
const state={familyId:null,parentAId:null,parentBId:null,parentAName:'',parentBName:'',childNames:[],tagsA:[],tagsB:[],history:['screen-welcome']};
function goTo(id){document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active');state.history.push(id);document.getElementById('backBtn').classList.toggle('visible',id!=='screen-welcome'&&id!=='screen-dashboard');window.scrollTo(0,0);}
function goBack(){state.history.pop();const prev=state.history.at(-1)||'screen-dashboard';document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(prev).classList.add('active');document.getElementById('backBtn').classList.toggle('visible',prev!=='screen-welcome'&&prev!=='screen-dashboard');window.scrollTo(0,0);}
function addTag(p){const inp=document.getElementById('tagInput'+p);const v=inp.value.trim();if(!v)return;state['tags'+p].push(v);renderTags(p);inp.value='';}
function removeTag(p,i){state['tags'+p].splice(i,1);renderTags(p);}
function renderTags(p){document.getElementById('tags'+p).innerHTML=state['tags'+p].map((t,i)=>`<span class="tag">${esc(t)}<span class="tag-x" onclick="removeTag('${p}',${i})">x</span></span>`).join('');}
['A','B'].forEach(p=>document.getElementById('tagInput'+p).addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();addTag(p);}}));
async function setup(){
  const childNames=document.getElementById('childNames').value.split(',').map(s=>s.trim()).filter(Boolean);
  const parentAName=document.getElementById('parentAName').value.trim();
  const parentBName=document.getElementById('parentBName').value.trim();
  if(!childNames.length||!parentAName||!parentBName){toast('Please fill in all fields');return;}
  const prefsA={};state.tagsA.forEach((t,i)=>prefsA['priority_'+(i+1)]=t);
  const prefsB={};state.tagsB.forEach((t,i)=>prefsB['priority_'+(i+1)]=t);
  try{
    const res=await api('POST','/families',{child_names:childNames,parent_a_name:parentAName,parent_b_name:parentBName,parent_a_preferences:prefsA,parent_b_preferences:prefsB});
    Object.assign(state,{familyId:res.family_id,parentAId:res.parent_a_id,parentBId:res.parent_b_id,parentAName,parentBName,childNames});
    localStorage.setItem('cp_state',JSON.stringify({familyId:res.family_id,parentAId:res.parent_a_id,parentBId:res.parent_b_id,parentAName,parentBName,childNames}));
    applySession();await loadNegs();goTo('screen-dashboard');
  }catch(e){toast('Setup failed');}
}
function applySession(){
  document.getElementById('dashName').textContent=state.parentAName;
  document.getElementById('dashSubtitle').textContent='Negotiating for '+state.childNames.join(' & ')+' with '+state.parentBName;
  document.getElementById('optA').textContent=state.parentAName;
  document.getElementById('optB').textContent=state.parentBName;
}
async function loadNegs(){
  try{
    const res=await api('GET','/families/'+state.familyId+'/negotiations');
    const el=document.getElementById('negList');
    if(!res.negotiations.length){el.innerHTML='<div class="empty-state"><div class="empty-icon">🕊</div><p>No negotiations yet.<br>Start one above.</p></div>';return;}
    el.innerHTML=res.negotiations.map(n=>{
      const icon=n.status==='agreed'?'✦':n.status==='deadlocked'?'!':'o';
      const bc=n.status==='agreed'?'badge-agreed':n.status==='deadlocked'?'badge-deadlocked':'badge-progress';
      const date=new Date(n.created_at+'Z').toLocaleDateString('en-US',{month:'short',day:'numeric'});
      return '<div class="neg-item" onclick="viewNeg(\''+n.id+'\')"><div class="neg-icon">'+icon+'</div><div><div class="neg-topic">'+esc(n.topic)+'</div><div class="neg-meta">'+date+'</div></div><span class="badge '+bc+'">'+n.status+'</span></div>';
    }).join('');
  }catch(e){}
}
async function startNegotiation(){
  const topic=document.getElementById('negTopic').value.trim();
  if(!topic){toast('Please describe what needs to be decided');return;}
  const btn=document.getElementById('startNegBtn');
  btn.disabled=true;btn.textContent='Starting...';
  goTo('screen-result');
  document.getElementById('loadingState').classList.add('visible');
  document.getElementById('resultContent').style.display='none';
  try{
    const res=await api('POST','/negotiations',{family_id:state.familyId,topic:topic,initiated_by:document.getElementById('initiatedBy').value});
    renderResult(res);document.getElementById('negTopic').value='';await loadNegs();
  }catch(e){toast('Negotiation failed');goBack();}
  finally{btn.disabled=false;btn.textContent='Start negotiation';document.getElementById('loadingState').classList.remove('visible');}
}
async function viewNeg(id){
  goTo('screen-result');
  document.getElementById('loadingState').classList.add('visible');
  document.getElementById('resultContent').style.display='none';
  try{
    const res=await api('GET','/negotiations/'+id);
    renderResult(Object.assign({},res,{rounds:res.transcript.map(m=>({role:m.role,sender:m.sender,content:m.content}))}));
  }catch(e){toast('Could not load');goBack();}
  finally{document.getElementById('loadingState').classList.remove('visible');}
}
function renderResult(res){
  document.getElementById('resultTopic').textContent=res.topic;
  document.getElementById('agreementBox').style.display=res.status==='agreed'?'block':'none';
  document.getElementById('deadlockBox').style.display=res.status==='deadlocked'?'block':'none';
  if(res.agreement)document.getElementById('agreementText').textContent=res.agreement;
  document.getElementById('transcriptEl').innerHTML=(res.rounds||[]).map(m=>'<div class="bubble '+(m.role==='agent_a'?'agent-a':'agent-b')+'"><div class="who">'+esc(m.sender)+'</div>'+esc(m.content)+'</div>').join('');
  document.getElementById('resultContent').style.display='block';
}
async function api(method,path,body){
  const opts={method:method,headers:{'Content-Type':'application/json'}};
  if(body)opts.body=JSON.stringify(body);
  const res=await fetch(path,opts);
  if(!res.ok)throw new Error(await res.text());
  return res.json();
}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function toast(msg){const el=document.getElementById('toast');el.textContent=msg;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),3200);}
(async()=>{const saved=localStorage.getItem('cp_state');if(saved){Object.assign(state,JSON.parse(saved));applySession();await loadNegs();goTo('screen-dashboard');}})();
</script>
</body>
</html>"""

with open('static/index.html', 'w') as f:
    f.write(html)
print("Done! UI updated.")
