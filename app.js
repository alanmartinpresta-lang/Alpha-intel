async function api(path, opts={}){const r=await fetch(path,{headers:{"Content-Type":"application/json"},...opts});return r.json()}
function esc(s){return String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;")}
async function refresh(){
 try{
  const s=await api("/api/state"); document.querySelector("#status").textContent="● ONLINE";
  document.querySelector("#metrics").innerHTML=[
   ["Cycle",s.cycle],["Énergie",s.energy.toFixed(2)],["Intégrité",s.integrity.toFixed(2)],
   ["Exploration",s.exploration.toFixed(2)],["Apprentissage",s.learning.toFixed(2)],
   ["Adaptation",s.adaptation.toFixed(2)],["Mémoires",s.memory_count],["Expériences",s.experiment_count],["Évolutions",s.evolution_count]
  ].map(x=>`<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #181818"><span>${x[0]}</span><b>${x[1]}</b></div>`).join("");
  document.querySelector("#self").textContent=JSON.stringify(s.self_model,null,2);
  const m=await api("/api/memories"); document.querySelector("#memory").textContent=m.slice(-20).map(x=>`[${x.source}] ${x.content}`).join("\n\n");
  const e=await api("/api/evolution"); document.querySelector("#journal").textContent=e.slice(-15).map(x=>`${x.created_at}\n${x.reason}\n${x.score_before} → ${x.score_after}`).join("\n\n");
 }catch(e){document.querySelector("#status").textContent="● OFFLINE"}
}
async function chat(){
 const q=document.querySelector("#q").value.trim();if(!q)return;
 const d=await api("/api/chat",{method:"POST",body:JSON.stringify({question:q})});
 document.querySelector("#chat").innerHTML+=`<div class="msg"><b>TOI</b><br>${esc(q)}</div><div class="msg alpha"><b>ALPHA</b><br>${esc(d.response||d.error||"")}</div>`;
 document.querySelector("#q").value="";refresh();
}
async function research(){
 const url=document.querySelector("#url").value.trim();if(!url)return;
 const d=await api("/api/research",{method:"POST",body:JSON.stringify({url})});
 document.querySelector("#research").textContent=d.ok?d.preview:(d.error||"Erreur");
 refresh();
}
async function evolve(){
 const d=await api("/api/evolve",{method:"POST",body:"{}"});
 document.querySelector("#evo").textContent=JSON.stringify(d,null,2);refresh();
}
refresh();setInterval(refresh,5000);
