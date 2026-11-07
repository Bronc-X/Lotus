// 兜底路线：在评论区逐个点「展开N条回复 / 展开更多」，由页面自己发请求，响应由 page_hook.js 转存。
// 可选 window.__DYC_UI_MAX = N：只点 N 次就停（用来给主路线采集真实的楼中楼请求模板）。
// 进度在 window.__dyc：status ui_running → ui_done ｜ ui_captcha（等用户手动过验证码，过了自动继续）
(() => {
  const S = window.__dyc;
  if (!S) return 'not hooked: 先注入 page_hook.js';
  const max = window.__DYC_UI_MAX || Infinity;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const captcha = () => [...document.querySelectorAll('[class*="captcha"], [id*="captcha"]')]
    .some(e => e.offsetParent && e.getBoundingClientRect().width > 200);
  const pattern = /^展开(\d+条回复|更多)$/;
  const text = e => (e.innerText || '').trim();
  // 只取最内层匹配的元素，避免父子元素各点一次
  const nextButton = () => [...document.querySelectorAll('button, span, div, p')].find(e =>
    !e.__dycDone && e.offsetParent && pattern.test(text(e)) && ![...e.children].some(c => pattern.test(text(c))));

  S.status = 'ui_running';
  S.clicks = 0;
  (async () => {
    let idle = 0;
    while (idle < 6 && S.clicks < max) {
      if (captcha()) { S.status = 'ui_captcha'; await sleep(3000); continue; }
      S.status = 'ui_running';
      const btn = nextButton();
      if (btn) {
        btn.__dycDone = true;
        btn.scrollIntoView({ block: 'center' });
        await sleep(800);
        btn.click();
        S.clicks++;
        idle = 0;
        await sleep(3000 + Math.random() * 3000);
      } else {
        window.scrollBy(0, 700);
        idle++;
        await sleep(2500 + Math.random() * 1500);
      }
    }
    S.status = 'ui_done';
  })().catch(e => { S.status = 'error'; S.reason = String(e); });
  return 'started';
})();
