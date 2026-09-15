const upstream = "http://tiktok-mcp.railway.internal:8000";
const port = Number(process.env.PORT || 8000);

const html = `<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>/TikTok طرابلس</title><style>*{box-sizing:border-box}body{margin:0;background:#0b0b0f;color:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Tahoma,sans-serif;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px}.card{width:min(560px,100%);background:#15151b;border:1px solid #2b2b34;border-radius:24px;padding:22px}.badge{display:inline-block;background:#ff2d55;padding:7px 11px;border-radius:999px;font-size:13px;font-weight:700}.title{font-size:30px;margin:14px 0 6px}.sub{color:#aaa;line-height:1.7}textarea{width:100%;min-height:150px;border-radius:18px;border:1px solid #34343f;background:#0f0f14;color:#fff;padding:16px;font-size:18px}button{width:100%;margin-top:14px;border:0;border-radius:16px;padding:16px;font-size:18px;font-weight:800;background:#fff;color:#111}.status{margin-top:16px;padding:14px;border-radius:14px;background:#0f0f14;color:#c9c9d0;display:none;line-height:1.6}video{width:100%;border-radius:16px;margin-top:16px;display:none;background:#000}</style></head><body><div class="card"><span class="badge">/TikTok</span><div class="title">صانع فيديو TikTok</div><p class="sub">اكتب الموضوع فقط. عربي، ترجمة إنجليزية، 9:16، حوالي 60 ثانية.</p><textarea id="topic">أفضل الأماكن المشهورة في طرابلس للأجانب</textarea><button id="go">إنشاء الفيديو</button><div id="status" class="status"></div><video id="video" controls playsinline></video></div><script>const g=document.getElementById("go"),s=document.getElementById("status"),v=document.getElementById("video"),t=document.getElementById("topic");function sh(x){s.style.display="block";s.textContent=x}async function poll(id){for(;;){await new Promise(r=>setTimeout(r,5000));let r=await fetch("/task/"+id),j=await r.json();if(j.status==="ready"){sh("تم إنشاء الفيديو ✅");v.src=j.video_url.replace("/videos/","/video/");v.style.display="block";g.disabled=false;return}if(j.status==="failed"){sh("فشل الإنشاء: "+(j.message||"خطأ"));g.disabled=false;return}sh("جاري إنشاء الفيديو…")}}g.onclick=async()=>{let q=t.value.trim();if(!q)return sh("اكتب الموضوع أولاً");g.disabled=true;v.style.display="none";sh("جاري بدء الإنشاء…");try{let r=await fetch("/create",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({topic:q})}),j=await r.json();if(!r.ok)throw new Error(j.error||"فشل بدء الإنشاء");sh("بدأ الإنشاء");poll(j.task_id)}catch(e){sh(e.message);g.disabled=false}}</script></body></html>`;

Bun.serve({
  hostname: "0.0.0.0",
  port,
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === "/health") return new Response("ok");
    if (u.pathname === "/") return new Response(html, {headers:{"content-type":"text/html; charset=utf-8"}});
    let target;
    if (u.pathname === "/create") target = upstream + "/web/create";
    else if (u.pathname.startsWith("/task/")) target = upstream + "/web/tasks/" + u.pathname.slice(6);
    else if (u.pathname.startsWith("/video/")) target = upstream + "/videos/" + u.pathname.slice(7);
    else return new Response("Not found", {status:404});
    try {
      const init = {method:req.method, headers:req.headers};
      if (req.method !== "GET" && req.method !== "HEAD") init.body = await req.arrayBuffer();
      const r = await fetch(target, init);
      return new Response(r.body, {status:r.status, headers:r.headers});
    } catch (e) {
      return Response.json({error:String(e)}, {status:502});
    }
  }
});
console.log("WEB_GATEWAY_READY", port);
