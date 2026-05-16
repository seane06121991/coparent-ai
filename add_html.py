html = open('/dev/stdin').read() if False else """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>CoParent AI</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--clay:#f5ede3;--warm:#ede0d0;--sand:#c9b49a;--bark:#7c5c3e;--ink:#2b1f14;--sage:#6b8f71;--sage-l:#e8f0e9;--rose:#c2645a;--rose-l:#faeae8;--sky:#4a7fa5;--sky-l:#e6f0f7;--r:16px}
body{font-family:'DM Sans',sans-serif;background:var(--clay);color:var(--ink);min-height:100dvh;font-size:15px;line-height:1.5}
header{background:var(--bark);color:#fff;padding:18px 20px 16px;position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:12px}
.logo{font-family:'DM Serif Display',serif;font-size:22px;letter-spacing:-.3px}
.logo em{font-style:italic;color:var(--sand)}
#backBtn{background:none;border:none;color:#fff;font-size:22px;cursor:pointer;padding:0 4px;display:none}
#backBtn.visible{display:block}
.screen{display:none;padding:24px 20px 60px;max-width:520px;margin:0 auto}
.screen.active{display:block}
h2{font-family:'DM Serif Display',serif;font-size:26px;font-weight:400;margin-bottom:6px}
h2 em{font-style:italic;color:var(--bark)}
.subtitle{color:var(--bark);font-size:14px;margin-bottom:28px;font-weight:300}
.card{background:#fff;border-radius:var(--r);padding:20px;margin-bottom:16px;box-shadow:0 1px 3px rgba(43,31,20,.08)}
.card-label{font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--sand);margin-bottom:14px}
label{display:block;font-size:13px;font-weight:500;color:var(--bark);margin-bottom:5px}
input,textarea,select{width:100%;padding:12px 14px;border:1.5px solid var(--warm);border-radius:10px;font-family:inherit;font-size:15px;color:var(--ink);background:var(--clay);outline:none;transition:border-color .15s;margin-bottom:14px}
input:focus,textarea:focus,select:focus{border-color:var(--bark);background:#fff}
textarea{resize:none;min-height:90px}
.btn{display:block;width:100%;padding:15px;border:none;border-radius:12px;font-family:inherit;font-size:15px;font-weight:600;cursor:pointer;transition:opacity .15s,transform .1s;text-align:center}
.btn:active{transform:scale(.98)}
.btn-primary{background:var(--bark);color:#fff}
.btn-primary:hover{opacity:.9}
.btn-sage{background:var(--sage);color:#fff;margin-bottom:12px}
.btn-ghost{background:transparent;color:var(--bark);border:1.5px solid var(--sand)}
.btn:disabled{opacity:.45;cursor:not-allowed}
.tag-list{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px;min-height:10px}
.tag{background:var(--sage-l);color:var(--sage);border:1.5px solid var(--sage);border-radius:20px;padding:5px 12px;font-size:13px;font-weight:500;display:flex;align-items:center;gap:6px}
.tag-x{cursor:pointer;font-size:16px;line-height:1}
.tag-row{display:flex;gap:8px}
.tag-row input{margin-bottom:0;flex:1}
.tag-row button{padding:12px 16px;background:var(--sage);color:#fff;border:none;border-radius:10px;font-size:20px;cursor:pointer;flex-shrink:0}
.neg-item{display:flex;align-items:center;gap:14px;padding:16px 0;border-bottom:1px solid var(--warm);cursor:pointer}
.neg-item:last-child{border-bottom:none}
.neg-icon{font-size:24px;flex-shrink:0}
.neg-topic{font-weight:500;font-size:15px}
.neg-meta{font-size:12px;color:var(--sand);margin-top:2px}
.badge{margin-left:auto;font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;flex-shrink:0}
.badge-agreed{background:var(--sage-l);color:var(--sage)}
.badge-progress{background:var(--sky-l);color:var(--sky)}
.badge-deadlocked{background:var(--rose-l);color:var(--rose)}
.empty-state{text-align:center;padding:40px 0;color:var(--sand)}
.empty-icon{font-size:48px;margin-bottom:12px}
.transcript{display:flex;flex-direction:column;gap:14px;margin-bottom:24px}
.bubble{max-width:88%;padding:13px 16px;border-radius:18px;font-size:14px;line-height:1.55}
.bubble.agent-a{background:var(--sky-l);color:var(--ink);align-self:flex-start;border-bottom-left-radius:4px}
.bubble.agent-b{background:var(--rose-l);color:var(--ink);align-self:flex-end;border-bottom-right-radius:4px}
.bubble .who{font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;margin-bottom:5px}
.bubble.agent-a .who{color:var(--sky)}
.bubble.agent-b .who{color:var(--rose)}
.agreement-box{background:var(--sage-l);border:1.5px solid var(--sage);border-radius:var(--r);padding:20px;margin-bottom:20px}
.agreement-box h3{font-family:'DM Serif Display',serif;font-size:18px;color:var(--sage);margin-bottom:10px}
.agreement-box p{font-size:14px;white-space:pre-wrap;line-height:1.6}
.deadlock-box{background:var(--rose-l);border:1.5px solid var(--rose);border-radius:var(--r);padding:18px;margin-bottom:20px}
.deadlock-box h3{color:var(--rose);font-family:'DM Serif Display',serif;font-size:18px;margin-bottom:6px}
.deadlock-box p{font-size:14px}
.loading{display:none;flex-direction:column;align-items:center;justify-content:center;padding:60px 20px;gap:18px;text-align:center}
.loading.visible{display:flex}
.spinner{width:44px;height:44px;border:3px solid var(--warm);border-top-color:var(--bark);border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading p{color:var(--bark);font-size:14px;font-weight:300}
.toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%) translateY(80px);background:var(--ink);color:#fff;padding:12px 20px;border-radius:24px;font-size:14px;font-weight:500;transition:transform .3s;z-index:999;white-space:nowrap}
.toast.show{transform:translateX(-50%) translateY(0)}
.section-title{font-size:13px;font-weight:600;color:var(--sand);text-transform:uppercase;letter-spacing:.07em;margin-bottom:14px}
.result-topic{font-family:'DM Serif Display',serif;font-size:22px;margin-bottom:20px;line-height:1.3}
</style>
</head>
<body>
<header>
  <button id="backBtn" onclick="goBack()">←</button>
  <div class="logo">Co<em>Parent</em> AI</div>
</header>
<div class="toast" id="toast"></div>
<div class="screen active" id="screen-welcome">
  <h2>Let your <em>agents</em> talk.</h2>
  <p class="subtitle">Set up your co-parenting profile and let AI handle the hard conversations.</p>
  <div class="card">
    <div class="card-label">Children</div>
    <label>Kids first names (comma separated)</label>
    <input type="text" id="childNames" placeholder="e.g. Emma, Lucas" autocomplete="off">
  </div>
  <div class="card">
    <div class="card-label">Parent A — You</div>
    <label>Your name</label>
    <input type="text" id="parentAName" placeholder="Your name" autocomplete="off">
    <label>Your priorities (add as many as you like)</label>
    <div class="tag-list" id="tagsA"></div>
    <div class="tag-row">
      <input type="text" id="tagInputA" placeholder="e.g. School nights home by 7pm" autocomplete="off">
      <button onclick="addTag('A')">+</button>
    </div>
  </div>
  <div class="card">
    <div class="card-label">Parent B — Other parent</div>
    <label>Their name</label>
    <input type="text" id="parentBName" placeholder="Other parents name" autocomplete="off">
    <label>Their priorities</label>
    <div class="tag-list" id="tagsB"></div>
    <div class="tag-row">
      <input type="text" id="tagInputB" placeholder="e.g. Soccer on Saturdays" autocomplete="off">
      <button onclick="addTag('B')">+</button>
    </div>
  </div>
  <button class="btn btn-primary" onclick="setup()">Create our profile</button>
</div>
<div class="screen" id="screen-dashboard">
  <h2>Hi, <em id="dashName">there</em></h2>
  <p class="subtitle" id="dashSubtitle"></p>
  <button class="btn btn-sage" onclick="goTo('screen-new-neg')">+ Start a new negotiation</button>
  <div class="card">
    <div class="card-label">Past negotiations</div>
    <div id="negList"><div class="empty-state"><div class="empty-icon">🕊️</div><p>No negotiations yet. Start one above.</p></div></div>
  </div>
</div>
<div class="screen" id="screen-new-neg">
  <h2>New <em>negotiation</em></h2>
  <p class="subtitle">Describe what needs to be decided.</p>
  <div class="card">
    <div class="card-label">Topic</div>
    <label>What needs to be decided?</label>
    <textarea id="negTopic" placeholder="e.g. Holiday schedule for Christmas and Thanksgiving"></textarea>
    <label>Who is raising this?</label>
    <select id="initiatedBy">
      <option value="parent_a" id="optA">Parent A</option>
      <option value="parent_b" id="optB">Parent B</option>
    </select>
  </div>
  <button class="btn btn-primary" id="startNegBtn" onclick="startNegotiation()">Let the agents negotiate</button>
</div>
<div class="screen" id="screen-result">
  <div class="loading" id="loadingState">
    <div class="spinner"></div>
    <p>Your agents are negotiating. This usually takes about 30 seconds.</p>
  </div>
  <div id="resultContent" style="display:none">
    <p class="result-topic" id="resultTopic"></p>
    <div id="agreementBox" class="agreement-box" style="display:none">
      <h3>Agreement reached</h3>
      <p id="agreementText"></p>
    </div>
    <div id="deadlockBox" class="deadlock-box" style="display:none">
      <h3>Could not agree</h3>
      <p>The agents hit a deadlock. Try adding more specific preferences or revisit the topic.</p>
    </div>
    <div class="section-title">Full transcript</div>
    <div class="transcript" id="transcriptEl"></div>
    <button class="btn btn-ghost" onclick="goTo('screen-dashboard')">Back to dashboard</button>
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
  document.getElementById('dashSubtitle').textContent='Negotiating for '+state.childNames.join(' and ')+' with '+state.parentBName;
  document.getElementById('optA').textContent=state.parentAName;
  document.getElementById('optB').textContent=state.parentBName;
}
async function loadNegs(){
  try{
    const res=await api('GET','/families/'+state.familyId+'/negotiations');
    const el=document.getElementById('negList');
    if(!res.negotiations.length){el.innerHTML='<div class="empty-state"><div class="empty-icon">🕊️</div><p>No negotiations yet. Start one above.</p></div>';return;}
    el.innerHTML=res.negotiations.map(n=>{
      const icon=n.status==='agreed'?'✅':n.status==='deadlocked'?'⚠️':'💬';
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
  }catch(e){toast('Negotiation failed, try again');goBack();}
  finally{btn.disabled=false;btn.textContent='Let the agents negotiate';document.getElementById('loadingState').classList.remove('visible');}
}
async function viewNeg(id){
  goTo('screen-result');
  document.getElementById('loadingState').classList.add('visible');
  document.getElementById('resultContent').style.display='none';
  try{
    const res=await api('GET','/negotiations/'+id);
    renderResult(Object.assign({},res,{rounds:res.transcript.map(m=>({role:m.role,sender:m.sender,content:m.content}))}));
  }catch(e){toast('Could not load negotiation');goBack();}
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
(async()=>{
  const saved=localStorage.getItem('cp_state');
  if(saved){Object.assign(state,JSON.parse(saved));applySession();await loadNegs();goTo('screen-dashboard');}
})();
</script>
</body>
</html>"""

import os
os.makedirs('static', exist_ok=True)
with open('static/index.html', 'w') as f:
    f.write(html)
print("Created static/index.html")
