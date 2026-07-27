// Klien fetch tipis untuk backend SIPREBAR (FastAPI, lihat backend/main.py).
//
// Cakupan yang dilayani backend cuma dua: CRUD data historis dan inferensi
// LSTM untuk data baru. Forecast 2026-2028, gap analysis RUED, dan
// perbandingan ARIMA/Naive TETAP statis dari data.js -- tidak ada fungsi di
// sini yang dipakai untuk itu.

export const API_BASE = 'http://localhost:8000';

async function parseJsonSafe(res) {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

function pesanDariDetail(detail, fallback) {
  if (!detail) return fallback;
  if (Array.isArray(detail)) {
    // Error validasi Pydantic (422): list of {loc, msg, ...}
    return detail.map(d => d.msg || JSON.stringify(d)).join('; ');
  }
  return String(detail);
}

async function request(path, options) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error(
      `Tidak dapat terhubung ke backend di ${API_BASE}. Pastikan server backend sudah dijalankan.`
    );
  }
  const body = await parseJsonSafe(res);
  if (!res.ok) {
    throw new Error(pesanDariDetail(body?.detail, `Permintaan gagal (HTTP ${res.status}).`));
  }
  return body;
}

export function apiGet(path) {
  return request(path);
}

export function apiPost(path, payload) {
  return request(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function apiPut(path, payload) {
  return request(path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

export function apiDelete(path) {
  return request(path, { method: 'DELETE' });
}

export function apiPostForm(path, formData) {
  return request(path, { method: 'POST', body: formData });
}

// Unduh respons endpoint sebagai file (dipakai untuk GET /api/data/export).
export async function apiDownload(path, filename) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`);
  } catch {
    throw new Error(
      `Tidak dapat terhubung ke backend di ${API_BASE}. Pastikan server backend sudah dijalankan.`
    );
  }
  if (!res.ok) {
    const body = await parseJsonSafe(res);
    throw new Error(pesanDariDetail(body?.detail, `Gagal mengunduh data (HTTP ${res.status}).`));
  }
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
