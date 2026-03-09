const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export function healthCheck() {
  return request('/health');
}

export function analyze(payload) {
  return request('/analyze', { method: 'POST', body: JSON.stringify(payload) });
}

export function simulate(payload) {
  return request('/simulate', { method: 'POST', body: JSON.stringify(payload) });
}

export function roiEstimate(payload) {
  return request('/roi-estimate', { method: 'POST', body: JSON.stringify(payload) });
}

export function pilotReadiness(payload) {
  return request('/pilot-readiness', { method: 'POST', body: JSON.stringify(payload) });
}

export function prPreview(payload) {
  return request('/pr-preview', { method: 'POST', body: JSON.stringify(payload) });
}
