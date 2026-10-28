(payload => {
 const key='__codexWeeklyMonitor';
 if (!window[key]) {
  const state={payload:null};
  state.render=()=>{
   const roots=[...document.querySelectorAll('[data-codex-composer-root]')].filter(e=>e.getBoundingClientRect().width>0);
   document.querySelectorAll('[data-codex-weekly-monitor]').forEach(e=>{if(!roots.includes(e.parentElement))e.remove()});
   for(const root of roots){
    let row=root.querySelector(':scope > [data-codex-weekly-monitor]');
    if(!row){row=document.createElement('div');row.dataset.codexWeeklyMonitor='';row.setAttribute('role','status');row.style.cssText='font:12px/20px var(--font-sans,Segoe UI,sans-serif);color:var(--text-tertiary,#999);text-align:center;padding:4px 8px 0;white-space:normal;';root.appendChild(row)}
    const p=state.payload||{}, age=(Date.now()/1000)-(p.updatedAt||0);
    let text='Codex 周额度：读取中…';
    if(p.weekly){
     const expired=Date.now()/1000>=p.weekly.resetsAt;
     const stale=p.error||age>90||expired;
     text=expired?'Codex 周额度：已到重置时间，等待刷新':`Codex 周额度：已用 ${p.weekly.usedPercent}% · 剩余 ${Math.max(0,100-p.weekly.usedPercent)}% · ${new Date(p.weekly.resetsAt*1000).toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false})} 重置`;
     if(stale&&!expired)text+=' · 数据待刷新';
    }else if(p.error)text='Codex 周额度：读取失败，等待重试';
    else if(p.updatedAt)text='Codex 周额度：账号未返回周窗口';
    if(row.textContent!==text)row.textContent=text;
    row.title='账号共享额度 · 每30秒刷新'+(p.updatedAt?' · 上次成功：'+new Date(p.updatedAt*1000).toLocaleTimeString('zh-CN'):'');
   }
  };
  state.timer=setInterval(state.render,1000);
  window[key]=state;
 }
 window[key].payload=payload; window[key].render();
 return {rows:document.querySelectorAll('[data-codex-weekly-monitor]').length,text:[...document.querySelectorAll('[data-codex-weekly-monitor]')].map(e=>e.textContent)};
})