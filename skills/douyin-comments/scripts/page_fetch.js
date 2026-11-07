// 主路线：照抄页面真实请求的参数，只替换 aweme_id / cursor / comment_id，签名交给页面 SDK。
// 先设 window.__DYC_CFG = { awemeId: '...' }，再执行本文件。进度在 window.__dyc：
//   status: running → done ｜ fallback（附 reason，转兜底路线）｜ need_template ｜ error
(() => {
  const S = window.__dyc;
  if (!S) return 'not hooked: 先注入 page_hook.js';
  const RECV = window.__DYC_RECV || 'http://127.0.0.1:8765';
  const cfg = window.__DYC_CFG || {};
  const T = S.templates;
  if (!cfg.awemeId) return 'missing window.__DYC_CFG.awemeId';
  if (!T.top) { S.status = 'need_template'; return 'need_template: 评论区还没加载出一级评论'; }
  if (!T.reply) {
    // 没点过「展开回复」时，从一级评论模板派生：公共参数相同，只换路径和业务参数
    const u = new URL(T.top.url, location.origin);
    u.pathname = '/aweme/v1/web/comment/list/reply/';
    u.searchParams.delete('aweme_id');
    T.reply = { url: u.pathname + u.search, headers: T.top.headers, derived: true };
  }

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const pace = async () => {
    S.requests++;
    await sleep(S.requests % 15 === 0 ? 8000 + Math.random() * 7000 : 2000 + Math.random() * 2000);
  };
  const build = (tpl, patch) => {
    const u = new URL(tpl.url, location.origin);
    ['a_bogus', 'X-Bogus', '_signature'].forEach(k => u.searchParams.delete(k));
    const ms = localStorage.getItem('xmst');
    if (ms && u.searchParams.has('msToken')) u.searchParams.set('msToken', ms);
    for (const [k, v] of Object.entries(patch)) u.searchParams.set(k, v);
    return u.pathname + u.search;
  };
  // 不能依赖 xhr.timeout：页面 SDK 包过的 XHR 在风控挂起时不会触发超时
  const get = (url, headers) => Promise.race([
    new Promise(res => {
      const x = new XMLHttpRequest();
      x.__dycSelf = true;
      x.open('GET', url);
      x.withCredentials = true;
      for (const [k, v] of Object.entries(headers || {})) { try { x.setRequestHeader(k, v); } catch (e) {} }
      x.onload = () => res(x.responseText);
      x.onerror = () => res('');
      x.send();
    }),
    sleep(20000).then(() => 'TIMEOUT'),
  ]);
  const parse = t => { try { const j = JSON.parse(t); return j && j.status_code === 0 ? j : null; } catch (e) { return null; } };
  const post = (name, body) => fetch(`${RECV}/${name}`, { method: 'POST', body });
  const pad = n => String(n).padStart(4, '0');

  Object.assign(S, { status: 'running', phase: 'detail', top: 0, replies: 0, requests: 0, need: 0, done: 0, reason: '' });
  (async () => {
    if (!cfg.skipDetail) {
      const t = await get(build(T.top, { aweme_id: cfg.awemeId }).replace('/comment/list/', '/aweme/detail/'), T.top.headers);
      if (parse(t)) await post('detail.json', t);
      await pace();
    }

    S.phase = 'top';
    const threads = [];
    let cursor = 0, more = 1, page = 0;
    while (more && page < 500) {
      const t = await get(build(T.top, { aweme_id: cfg.awemeId, cursor, count: 20 }), T.top.headers);
      const j = parse(t);
      if (!j) { S.status = 'fallback'; S.reason = `top p${page}: ${String(t).slice(0, 80)}`; return; }
      await post(`top_${pad(page)}.json`, t);
      const list = j.comments || [];
      list.forEach(c => { S.top++; if (c.reply_comment_total > 0) threads.push(c.cid); });
      more = j.has_more && list.length > 0;
      cursor = j.cursor;
      page++;
      await pace();
    }

    S.phase = 'reply';
    S.need = threads.length;
    const skip = new Set(cfg.skipThreads || []);
    for (const cid of threads) {
      if (skip.has(cid)) { S.done++; continue; }
      let rc = 0, rm = 1, n = 0;
      while (rm && n < 50) {
        const t = await get(build(T.reply, { item_id: cfg.awemeId, comment_id: cid, cursor: rc, count: 20 }), T.reply.headers);
        const j = parse(t);
        if (!j) { S.status = 'fallback'; S.failedAt = cid; S.reason = `reply ${cid}: ${String(t).slice(0, 80)}`; return; }
        await post(`reply_${cid}_${pad(n)}.json`, t);
        const list = j.comments || [];
        S.replies += list.length;
        rm = j.has_more && list.length > 0;
        rc = j.cursor;
        n++;
        await pace();
      }
      S.done++;
    }
    S.status = 'done';
  })().catch(e => { S.status = 'error'; S.reason = String(e); });
  return 'started';
})();
