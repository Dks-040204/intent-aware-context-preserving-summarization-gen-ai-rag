/* ═══════════════════════════════════════════════════════════════
   Contexto — app.js
   Fully connected to FastAPI backend at http://localhost:8000
   Endpoints used:
     GET  /health
     POST /auto-summarize  ← single doc (returns model metadata)
     POST /batch-summarize ← batch
     POST /keywords        ← keyword + phrase extraction
   ═══════════════════════════════════════════════════════════════ */

const API = (window.CONTEXTO_CONFIG && window.CONTEXTO_CONFIG.API_BASE_URL)
  ? window.CONTEXTO_CONFIG.API_BASE_URL
  : 'http://localhost:8000';   // fallback for local dev without config.js

/* ── State ──────────────────────────────────────────────────── */
let currentMode   = 'single';
let lastResult    = null;
let batchDocCount = 0;
let stageTimer    = null;

/* ── Init ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initDropZone();
  initBatchDocs();
  checkHealth();
  setInterval(checkHealth, 15_000);
});

/* ══════════════════════════════════════════════════════════════
   HEALTH CHECK
══════════════════════════════════════════════════════════════ */
async function checkHealth() {
  const dot   = document.getElementById('apiDot');
  const label = document.getElementById('apiLabel');
  try {
    const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(5000) });
    if (res.ok) {
      dot.className     = 'api-dot online';
      label.textContent = 'API Online';
    } else throw new Error();
  } catch {
    dot.className     = 'api-dot offline';
    label.textContent = 'API Offline';
  }
}

/* ══════════════════════════════════════════════════════════════
   MODE SWITCHING
══════════════════════════════════════════════════════════════ */
function switchMode(mode) {
  currentMode = mode;
  document.getElementById('tab-single').classList.toggle('active', mode === 'single');
  document.getElementById('tab-batch').classList.toggle('active',  mode === 'batch');
  document.getElementById('panel-single').classList.toggle('hidden', mode !== 'single');
  document.getElementById('panel-batch').classList.toggle('hidden',  mode !== 'batch');
  hide('loadingWrap');
  hide('resultsWrap');
}

/* ══════════════════════════════════════════════════════════════
   INPUT HELPERS
══════════════════════════════════════════════════════════════ */
function onDocInput() {
  const text  = document.getElementById('docInput').value.trim();
  const words = text ? text.split(/\s+/).length : 0;
  document.getElementById('wordCount').textContent =
    `${words.toLocaleString()} words · ${text.length.toLocaleString()} chars`;

  const chip = document.getElementById('complexityChip');
  if (!text) { chip.textContent = ''; chip.style.display = 'none'; return; }
  chip.style.display = 'inline';
  if      (words > 5000) { chip.textContent = 'Very Complex'; chip.style.color = '#ef4444'; }
  else if (words > 2000) { chip.textContent = 'Complex';      chip.style.color = '#f59e0b'; }
  else if (words > 500)  { chip.textContent = 'Moderate';     chip.style.color = '#a78bfa'; }
  else                   { chip.textContent = 'Simple';        chip.style.color = '#10b981'; }
}

function clearInput() {
  document.getElementById('docInput').value = '';
  onDocInput();
  hide('resultsWrap'); hide('loadingWrap');
  toast('Cleared', 'info');
}

function handleFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  loadFileIntoTextarea(file);
  e.target.value = '';
}

async function loadFileIntoTextarea(file) {
  const name = file.name.toLowerCase();
  try {
    let text = '';
    if (name.endsWith('.pdf')) {
      text = await parsePDF(file);
    } else if (name.endsWith('.docx')) {
      text = await parseDocx(file);
    } else if (name.endsWith('.doc')) {
      // Old binary .doc format is NOT supported by Mammoth (XML only)
      toast('Old .doc format is not supported. Please save your file as .docx and try again.', 'error');
      return;
    } else {
      // .txt / .md — plain text
      text = await file.text();
    }
    if (!text || !text.trim()) {
      toast(`No readable text found in ${file.name}`, 'error');
      return;
    }
    document.getElementById('docInput').value = text;
    onDocInput();
    toast(`Loaded: ${file.name}`, 'success');
  } catch (err) {
    toast(`Failed to read ${file.name}: ${err.message}`, 'error');
    console.error(err);
  }
}

/* Parse PDF using PDF.js (runs in-browser, no server needed) */
async function parsePDF(file) {
  // CDN build exposes window.pdfjsLib (not the module path key)
  const pdfjsLib = window.pdfjsLib || window['pdfjs-dist/build/pdf'];
  if (!pdfjsLib) throw new Error('PDF.js not loaded — please check your internet connection.');

  // Point the worker to the matching CDN version
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

  const arrayBuffer = await file.arrayBuffer();
  const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
  const pdf   = await loadingTask.promise;
  const pages = [];
  for (let i = 1; i <= pdf.numPages; i++) {
    const page    = await pdf.getPage(i);
    const content = await page.getTextContent();
    const pageText = content.items.map(item => item.str).join(' ');
    pages.push(pageText);
  }
  const text = pages.join('\n\n').trim();
  if (!text) throw new Error('No readable text found in PDF (may be a scanned/image-only PDF).');
  return text;
}

/* Parse DOCX using Mammoth.js (runs in-browser, .docx only) */
async function parseDocx(file) {
  if (typeof mammoth === 'undefined')
    throw new Error('Mammoth.js not loaded — check your internet connection.');
  try {
    const arrayBuffer = await file.arrayBuffer();
    const result = await mammoth.extractRawText({ arrayBuffer });
    if (result.messages && result.messages.length) {
      console.warn('Mammoth warnings:', result.messages);
    }
    const text = (result.value || '').trim();
    if (!text) throw new Error('No text found — the file may be empty or image-only.');
    return text;
  } catch (err) {
    // Mammoth throws on corrupt/non-docx zip — surface a clean message
    if (err.message && err.message.includes('children')) {
      throw new Error('Could not parse this .docx file. Make sure it is a valid Word document (.docx), not a renamed .doc file.');
    }
    throw err;
  }
}

/* ══════════════════════════════════════════════════════════════
   DRAG & DROP
══════════════════════════════════════════════════════════════ */
function initDropZone() {
  const zone = document.getElementById('dropZone');
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragging'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragging'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('dragging');
    const file = e.dataTransfer.files[0];
    if (!file) return;
    const ok = /\.(txt|md|pdf|docx)$/i.test(file.name);
    if (!ok) {
      toast('Supported formats: .txt, .md, .pdf, .docx  (old .doc not supported)', 'error'); return;
    }
    loadFileIntoTextarea(file);
  });
}

/* ══════════════════════════════════════════════════════════════
   BATCH DOCUMENTS
══════════════════════════════════════════════════════════════ */
function initBatchDocs() {
  document.getElementById('batchList').innerHTML = '';
  batchDocCount = 0;
  addBatchDoc(); addBatchDoc();
}

function addBatchDoc() {
  batchDocCount++;
  const n    = batchDocCount;
  const list = document.getElementById('batchList');
  const item = document.createElement('div');
  item.className = 'batch-item';
  item.id = `bdoc-${n}`;
  item.innerHTML = `
    <div class="batch-num">${n}</div>
    <textarea class="batch-textarea" placeholder="Paste document ${n} here…" rows="4"></textarea>
    <button class="batch-remove" title="Remove" onclick="removeBatchDoc('bdoc-${n}')">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>`;
  list.appendChild(item);
}

function removeBatchDoc(id) {
  document.getElementById(id)?.remove();
}

/* ══════════════════════════════════════════════════════════════
   LOADING STATE MACHINE
══════════════════════════════════════════════════════════════ */
const STAGES = [
  { id: 's1', sub: 'Preprocessing & cleaning text…'    },
  { id: 's2', sub: 'Analyzing complexity & picking model…' },
  { id: 's3', sub: 'Generating summary with AI…'       },
  { id: 's4', sub: 'Extracting keywords & finalizing…' },
];

function showLoading(title = 'Analyzing your document…') {
  document.getElementById('loadingTitle').textContent = title;
  hide('panel-single'); hide('panel-batch'); hide('resultsWrap');
  show('loadingWrap');
  document.querySelector('.tabs').style.pointerEvents = 'none';
  STAGES.forEach(s => { document.getElementById(s.id).className = 'stage'; });
  let step = 0;
  activateStage(0);
  stageTimer = setInterval(() => { step++; if (step < STAGES.length) activateStage(step); }, 900);
}

function activateStage(i) {
  if (i > 0) document.getElementById(STAGES[i - 1].id).className = 'stage done';
  document.getElementById(STAGES[i].id).className = 'stage active';
  document.getElementById('loadingSub').textContent = STAGES[i].sub;
}

function hideLoading() {
  clearInterval(stageTimer);
  STAGES.forEach(s => { document.getElementById(s.id).className = 'stage done'; });
  setTimeout(() => {
    hide('loadingWrap');
    show(currentMode === 'single' ? 'panel-single' : 'panel-batch');
    show('resultsWrap');
    document.querySelector('.tabs').style.pointerEvents = '';
    const rw = document.getElementById('resultsWrap');
    rw.classList.add('fade-up');
    setTimeout(() => rw.classList.remove('fade-up'), 500);
  }, 400);
}

/* ══════════════════════════════════════════════════════════════
   SINGLE DOCUMENT SUMMARIZE  →  /auto-summarize  +  /keywords
══════════════════════════════════════════════════════════════ */
async function summarize() {
  const doc = document.getElementById('docInput').value.trim();
  if (!doc) { toast('Please enter a document first', 'error'); return; }

  const intent  = document.getElementById('intentSel').value;
  const lang    = document.getElementById('langSel').value;
  const level   = document.getElementById('levelSel').value;
  const quality = document.getElementById('qualSel').value;

  const btn = document.getElementById('summarizeBtn');
  btn.disabled = true;
  showLoading('Analyzing your document…');

  try {
    /* ── 1. Auto-summarize (gets model metadata too) ── */
    const sumRes = await fetch(`${API}/auto-summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document: doc,
        intent,
        language: lang,
        quality_preference: quality,
        summary_level: level,
      }),
    });
    if (!sumRes.ok) {
      const err = await sumRes.json().catch(() => ({ detail: `HTTP ${sumRes.status}` }));
      throw new Error(err.detail);
    }
    const data = await sumRes.json();

    /* ── 2. Keyword extraction (real server-side) ── */
    let keywords = [], phrases = [];
    try {
      const kwRes = await fetch(`${API}/keywords`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: data.summary, keywords_k: 8, phrases_k: 4 }),
      });
      if (kwRes.ok) {
        const kd = await kwRes.json();
        keywords = kd.keywords  || [];
        phrases  = kd.key_phrases || [];
      }
    } catch { /* fallback: leave empty — non-critical */ }

    lastResult = { ...data, keywords, phrases };
    hideLoading();
    renderResults(data, keywords, phrases, level);
    toast('Summary generated!', 'success');

  } catch (err) {
    clearInterval(stageTimer);
    hide('loadingWrap');
    show('panel-single');
    document.querySelector('.tabs').style.pointerEvents = '';
    toast(`Error: ${err.message}`, 'error');
    console.error(err);
  } finally {
    btn.disabled = false;
  }
}

/* ══════════════════════════════════════════════════════════════
   BATCH SUMMARIZE  →  /batch-summarize
══════════════════════════════════════════════════════════════ */
async function batchSummarize() {
  const textareas = document.querySelectorAll('#batchList .batch-textarea');
  const docs = Array.from(textareas).map(t => t.value.trim()).filter(Boolean);
  if (!docs.length) { toast('Add at least one document', 'error'); return; }

  const intent = document.getElementById('bIntentSel').value;
  const lang   = document.getElementById('bLangSel').value;

  const btn = document.getElementById('batchBtn');
  btn.disabled = true;
  showLoading(`Summarizing ${docs.length} document${docs.length > 1 ? 's' : ''}…`);

  try {
    const res = await fetch(`${API}/batch-summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ documents: docs, intent, language: lang }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
      throw new Error(err.detail);
    }
    const data = await res.json();
    hideLoading();
    renderBatchResults(data.summaries);
    toast(`${data.count} summaries generated!`, 'success');
  } catch (err) {
    clearInterval(stageTimer);
    hide('loadingWrap');
    show('panel-batch');
    document.querySelector('.tabs').style.pointerEvents = '';
    toast(`Error: ${err.message}`, 'error');
    console.error(err);
  } finally {
    btn.disabled = false;
  }
}

/* ══════════════════════════════════════════════════════════════
   RENDER — SINGLE RESULT
══════════════════════════════════════════════════════════════ */
function renderResults(data, keywords, phrases, level) {
  level = level || 'brief';   // safe fallback
  /* Clear any previous batch results */
  document.getElementById('batchResults').innerHTML = '';

  /* ── Summary text — handle bullet-point format ── */
  const rawSummary = data.summary || '—';
  const summaryEl  = document.getElementById('summaryText');
  if (rawSummary.includes('\n• ') || rawSummary.startsWith('• ')) {
    // Render as a proper bullet list
    const headerMatch = rawSummary.match(/^\[([^\]]+)\]\n/);
    const header = headerMatch ? `<div class="summary-label">[${headerMatch[1]}]</div>` : '';
    const body   = headerMatch ? rawSummary.slice(headerMatch[0].length) : rawSummary;
    const items  = body.split(/\n/).filter(l => l.trim());
    summaryEl.innerHTML = header + '<ul class="summary-bullets">' +
      items.map(i => `<li>${escHtml(i.replace(/^•\s*/, ''))}</li>`).join('') +
      '</ul>';
  } else if (rawSummary.includes('\n1. ') || rawSummary.match(/\n\d+\./)) {
    // Render numbered list (methodology intent)
    const headerMatch = rawSummary.match(/^\[([^\]]+)\]\n/);
    const header = headerMatch ? `<div class="summary-label">[${headerMatch[1]}]</div>` : '';
    const body   = headerMatch ? rawSummary.slice(headerMatch[0].length) : rawSummary;
    const items  = body.split(/\n/).filter(l => l.trim());
    summaryEl.innerHTML = header + '<ol class="summary-numbered">' +
      items.map(i => `<li>${escHtml(i.replace(/^\d+\.\s*/, ''))}</li>`).join('') +
      '</ol>';
  } else {
    // Plain text (with intent label)
    summaryEl.textContent = rawSummary;
  }

  /* ── Meta chips ── */
  const intentLabel = (data.intent || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
  const levelLabel  = (level || 'brief').replace(/\b\w/g, c => c.toUpperCase());
  const langLabel   = (data.language || 'English').replace(/\b\w/g, c => c.toUpperCase());
  document.getElementById('summaryMeta').innerHTML = `
    <span class="meta-chip">🎯 ${intentLabel}</span>
    <span class="meta-chip">📏 ${levelLabel}</span>
    <span class="meta-chip">🌐 ${langLabel}</span>
    <span class="meta-chip">📝 ${data.length ?? '—'} words</span>
    <span class="meta-chip q-chip-${(data.quality||'medium').toLowerCase()}">
      ${qIcon(data.quality)} ${cap(data.quality ?? 'N/A')} Quality
    </span>`;

  /* ── Keywords (from /keywords endpoint) ── */
  const tagsWrap = document.getElementById('keywordTags');
  if (keywords.length || phrases.length) {
    tagsWrap.innerHTML =
      keywords.map(k => `<span class="tag tag-keyword">${escHtml(k)}</span>`).join('') +
      phrases.map(p  => `<span class="tag tag-phrase">${escHtml(p)}</span>`).join('');
  } else {
    tagsWrap.innerHTML = '<span style="color:var(--text-dim);font-size:.82rem;">No keywords extracted</span>';
  }

  /* ── Quality Metrics ── */
  const conf     = data.quality === 'high' ? 0.88 : data.quality === 'medium' ? 0.62 : 0.38;
  const lenScore = Math.min((data.length || 0) / 120, 1);
  const ragScore = data.use_rag ? 1.0 : 0.5;
  document.getElementById('qualityMetrics').innerHTML = `
    <div class="q-metric">
      <div class="q-label"><span>Confidence Score</span><span>${Math.round(conf * 100)}%</span></div>
      <div class="q-bar"><div class="q-fill" style="width:${conf * 100}%"></div></div>
    </div>
    <div class="q-metric">
      <div class="q-label"><span>Length Coverage</span><span>${Math.round(lenScore * 100)}%</span></div>
      <div class="q-bar"><div class="q-fill" style="width:${lenScore * 100}%"></div></div>
    </div>
    <div class="q-metric">
      <div class="q-label"><span>Context Depth (RAG)</span><span>${data.use_rag ? 'Full RAG' : 'Standard'}</span></div>
      <div class="q-bar"><div class="q-fill" style="width:${ragScore * 100}%"></div></div>
    </div>
    <div class="q-badge ${(data.quality||'medium').toLowerCase()}">
      ${qIcon(data.quality)} ${cap(data.quality ?? 'Medium')} Quality
    </div>`;

  /* ── Model Info (real data from /auto-summarize) ── */
  const ragClass = data.use_rag ? 'rag-yes' : 'rag-no';
  const ragText  = data.use_rag ? '✅ Yes (RAG active)' : '❌ No (direct inference)';
  document.getElementById('modelInfo').innerHTML = `
    <div class="m-row">
      <span class="m-row-label">Model Used</span>
      <span class="m-row-val">${data.model || 'unknown'}</span>
    </div>
    <div class="m-row">
      <span class="m-row-label">Complexity</span>
      <span class="m-row-val">${data.complexity || 'unknown'}</span>
    </div>
    <div class="m-row">
      <span class="m-row-label">RAG Pipeline</span>
      <span class="m-row-val ${ragClass}">${ragText}</span>
    </div>
    <div class="m-row">
      <span class="m-row-label">Est. Time</span>
      <span class="m-row-val">${data.estimated_time || 'N/A'}</span>
    </div>
    <div class="m-row">
      <span class="m-row-label">Reason</span>
      <span class="m-row-val" style="white-space:normal;max-width:200px;text-align:right">${data.reason || '—'}</span>
    </div>`;
}

/* ══════════════════════════════════════════════════════════════
   RENDER — BATCH RESULTS
══════════════════════════════════════════════════════════════ */
function renderBatchResults(summaries) {
  /* Clear single-doc result areas */
  ['summaryText','summaryMeta','keywordTags','qualityMetrics','modelInfo']
    .forEach(id => { document.getElementById(id).innerHTML = ''; });
  document.getElementById('summaryText').textContent = '';

  const container = document.getElementById('batchResults');
  container.innerHTML = `<div class="card">` +
    summaries.map((s, i) => `
      <div class="batch-result-item">
        <div class="batch-result-label">Document ${i + 1}</div>
        <div class="batch-result-text">${escHtml(s)}</div>
      </div>`).join('') +
    `</div>`;
}

/* ══════════════════════════════════════════════════════════════
   COPY SUMMARY
══════════════════════════════════════════════════════════════ */
function copySummary() {
  const text = document.getElementById('summaryText').textContent;
  if (!text || text === '—') { toast('Nothing to copy', 'error'); return; }
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.getElementById('copyBtn');
    btn.classList.add('copied');
    btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
    setTimeout(() => {
      btn.classList.remove('copied');
      btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`;
    }, 2000);
    toast('Copied to clipboard!', 'success');
  }).catch(() => toast('Copy failed', 'error'));
}

/* ══════════════════════════════════════════════════════════════
   EXPORT  (client-side download)
══════════════════════════════════════════════════════════════ */
function exportAs(fmt) {
  const summary = document.getElementById('summaryText').textContent;
  if (!summary || summary === '—') { toast('No summary to export', 'error'); return; }

  const now = new Date().toISOString();
  let content, mime, ext;

  if (fmt === 'txt') {
    content = summary; mime = 'text/plain'; ext = 'txt';
  } else if (fmt === 'md') {
    content = `# Document Summary\n\n**Generated:** ${now}\n\n**Intent:** ${lastResult?.intent ?? ''}\n**Language:** ${lastResult?.language ?? ''}\n**Model:** ${lastResult?.model ?? ''}\n\n## Summary\n\n${summary}`;
    mime = 'text/markdown'; ext = 'md';
  } else if (fmt === 'json') {
    content = JSON.stringify({
      summary,
      generated_at:   now,
      intent:         lastResult?.intent         ?? 'unknown',
      language:       lastResult?.language       ?? 'unknown',
      model:          lastResult?.model          ?? 'unknown',
      complexity:     lastResult?.complexity     ?? 'unknown',
      use_rag:        lastResult?.use_rag        ?? false,
      estimated_time: lastResult?.estimated_time ?? 'N/A',
      length:         lastResult?.length         ?? 0,
      quality:        lastResult?.quality        ?? 'unknown',
      keywords:       lastResult?.keywords       ?? [],
      key_phrases:    lastResult?.phrases        ?? [],
    }, null, 2);
    mime = 'application/json'; ext = 'json';
  }

  const blob = new Blob([content], { type: mime });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), { href: url, download: `synthtext_summary.${ext}` });
  a.click();
  URL.revokeObjectURL(url);
  toast(`Exported as .${ext}`, 'success');
}

/* ══════════════════════════════════════════════════════════════
   RESET
══════════════════════════════════════════════════════════════ */
function resetAll() {
  hide('resultsWrap');
  show(currentMode === 'single' ? 'panel-single' : 'panel-batch');
  lastResult = null;
}

/* ══════════════════════════════════════════════════════════════
   TOAST NOTIFICATIONS
══════════════════════════════════════════════════════════════ */
function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  document.getElementById('toastContainer').appendChild(el);
  setTimeout(() => el.remove(), 3100);
}

/* ══════════════════════════════════════════════════════════════
   UTILITIES
══════════════════════════════════════════════════════════════ */
function show(id) { document.getElementById(id)?.classList.remove('hidden'); }
function hide(id) { document.getElementById(id)?.classList.add('hidden'); }
function cap(s)   { return s ? s.charAt(0).toUpperCase() + s.slice(1) : ''; }
function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function qIcon(q) {
  return q === 'high' ? '✅' : q === 'medium' ? '⚠️' : '❌';
}
