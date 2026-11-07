// 在抖音视频页注入：记录评论接口的真实请求模板（URL + 请求头），并把页面自己发出的评论响应转存到本地接收服务。
// 每次打开 / 刷新页面后都要重新注入。返回 'hooked' 或 'already hooked'。
(() => {
  const RECV = window.__DYC_RECV || 'http://127.0.0.1:8765';
  if (window.__dycHooked) return 'already hooked';
  window.__dycHooked = true;
  window.__dyc = { status: 'hooked', templates: {}, uiCaptured: 0 };
  const S = window.__dyc;
  const kind = u => /\/comment\/list\/reply\//.test(u) ? 'reply' : /\/comment\/list\//.test(u) ? 'top' : null;
  const post = (name, body) => fetch(`${RECV}/${name}`, { method: 'POST', body }).catch(() => {});
  const remember = (k, url, headers) => {
    if (S.templates[k]) return;
    S.templates[k] = { url: String(url), headers: headers || {} };
    post(`template_${k}.json`, JSON.stringify(S.templates[k]));
  };
  const save = (k, text) => { S.uiCaptured++; post(`ui_${k}_${Date.now()}.json`, text); };

  const X = XMLHttpRequest.prototype, open = X.open, send = X.send, setH = X.setRequestHeader;
  X.open = function (m, u) { this.__dycUrl = u; this.__dycHeaders = {}; return open.apply(this, arguments); };
  X.setRequestHeader = function (k, v) { if (this.__dycHeaders) this.__dycHeaders[k] = v; return setH.apply(this, arguments); };
  X.send = function () {
    const k = kind(String(this.__dycUrl || ''));
    if (k && !this.__dycSelf) {
      remember(k, this.__dycUrl, this.__dycHeaders);
      this.addEventListener('load', () => save(k, this.responseText));
    }
    return send.apply(this, arguments);
  };

  const f = window.fetch;
  window.fetch = async function (input, init) {
    const u = typeof input === 'string' ? input : (input && input.url) || '';
    const k = kind(u);
    const r = await f.apply(this, arguments);
    if (k) {
      const h = input instanceof Request ? input.headers : (init && init.headers);
      remember(k, u, h ? Object.fromEntries(new Headers(h)) : {});
      r.clone().text().then(t => save(k, t));
    }
    return r;
  };
  return 'hooked';
})();
