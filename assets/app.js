const DATA_PATHS = {
  records: 'data/evidence_records.json',
  products: 'data/products.json',
  domains: 'data/evidence_domains.json',
  types: 'data/evidence_types.json',
  gaps: 'data/evidence_gaps.json',
  sourceGroups: 'data/source_groups.json'
};

const state = {
  records: [],
  products: [],
  domains: [],
  types: [],
  gaps: [],
  sourceGroups: [],
  visibleRecords: []
};

const $ = (id) => document.getElementById(id);

function escapeHtml(value = '') {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function unique(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => String(a).localeCompare(String(b)));
}

function flatten(values) {
  return values.flatMap((value) => Array.isArray(value) ? value : [value]);
}

function priorityClass(priority = '') {
  const p = priority.toLowerCase();
  if (p === 'high') return 'high';
  if (p === 'medium') return 'medium';
  if (p === 'watchlist') return 'watchlist';
  return '';
}

function verificationClass(value = '') {
  if (value.includes('gap')) return 'gap';
  if (value.includes('manual')) return 'manual';
  return '';
}

function populateSelect(selectId, values) {
  const select = $(selectId);
  const previous = select.value;
  select.innerHTML = '<option value="">All</option>' + values.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join('');
  if (values.includes(previous)) select.value = previous;
}

function setupFilters() {
  populateSelect('filter-product', unique([...state.products.map(p => p.name), ...state.records.map(r => r.product)]));
  populateSelect('filter-domain', state.domains.map(d => d.label));
  populateSelect('filter-type', state.types.map(t => t.label));
  populateSelect('filter-jurisdiction', unique(flatten(state.records.map(r => r.jurisdictions))));
  populateSelect('filter-stage', unique(state.records.map(r => r.development_stage)));
  populateSelect('filter-source', unique(state.records.map(r => r.source_group)));
  populateSelect('filter-priority', unique(state.records.map(r => r.priority)));

  [
    'filter-search', 'filter-product', 'filter-domain', 'filter-type', 'filter-jurisdiction',
    'filter-stage', 'filter-source', 'filter-priority', 'filter-date', 'date-basis'
  ].forEach(id => $(id).addEventListener('input', renderAll));

  $('reset-filters').addEventListener('click', () => {
    ['filter-search', 'filter-product', 'filter-domain', 'filter-type', 'filter-jurisdiction', 'filter-stage', 'filter-source', 'filter-priority', 'filter-date'].forEach(id => $(id).value = '');
    $('date-basis').value = 'source_date';
    renderAll();
  });

  $('export-csv').addEventListener('click', exportVisibleCsv);
  $('copy-record-ids').addEventListener('click', copyVisibleRecordIds);
  $('copy-source-list').addEventListener('click', copySourceGroups);
}

function recordText(record) {
  return [
    record.id, record.title, record.product, record.developer, record.platform,
    record.development_stage, record.evidence_domain, record.evidence_type,
    record.population, record.summary, record.source_title,
    ...(record.tags || []), ...(record.outcomes || []), ...(record.jurisdictions || [])
  ].join(' ').toLowerCase();
}

function passesFilters(record) {
  const query = $('filter-search').value.trim().toLowerCase();
  const product = $('filter-product').value;
  const domain = $('filter-domain').value;
  const type = $('filter-type').value;
  const jurisdiction = $('filter-jurisdiction').value;
  const stage = $('filter-stage').value;
  const source = $('filter-source').value;
  const priority = $('filter-priority').value;
  const dateBasis = $('date-basis').value;
  const since = $('filter-date').value;

  if (query && !recordText(record).includes(query)) return false;
  if (product && record.product !== product) return false;
  if (domain && record.evidence_domain !== domain) return false;
  if (type && record.evidence_type !== type) return false;
  if (jurisdiction && !(record.jurisdictions || []).includes(jurisdiction)) return false;
  if (stage && record.development_stage !== stage) return false;
  if (source && record.source_group !== source) return false;
  if (priority && record.priority !== priority) return false;
  if (since) {
    const dateValue = record[dateBasis];
    if (!dateValue || new Date(dateValue) < new Date(since)) return false;
  }
  return true;
}

function updateStats() {
  $('stat-records').textContent = state.records.length;
  $('stat-visible').textContent = state.visibleRecords.length;
  $('stat-products').textContent = state.products.length;
  $('stat-gaps').textContent = state.gaps.filter(g => g.severity === 'High').length;
}

function renderSourceGroups() {
  $('source-groups').innerHTML = state.sourceGroups.map(group => `
    <article class="source-card">
      <h3>${escapeHtml(group.name)}</h3>
      <p>${escapeHtml(group.description)}</p>
      <span class="badge">${escapeHtml(group.automation)}</span>
    </article>
  `).join('');
}

function renderMatrix() {
  const matrix = $('evidence-matrix');
  const domains = state.domains.map(d => d.label);
  const types = state.types.map(t => t.label);

  const counts = new Map();
  let max = 0;
  for (const record of state.visibleRecords) {
    const key = `${record.evidence_domain}||${record.evidence_type}`;
    const count = (counts.get(key) || 0) + 1;
    counts.set(key, count);
    if (count > max) max = count;
  }

  const header = `<thead><tr><th class="row-label">Domain</th>${types.map(type => `<th>${escapeHtml(type)}</th>`).join('')}</tr></thead>`;
  const rows = domains.map(domain => {
    const cells = types.map(type => {
      const count = counts.get(`${domain}||${type}`) || 0;
      const level = count === 0 ? 0 : Math.max(1, Math.ceil((count / Math.max(max, 1)) * 4));
      const disabled = count === 0 ? 'disabled' : '';
      const zeroClass = count === 0 ? 'zero' : '';
      return `<td class="level-${level}"><button class="${zeroClass}" ${disabled} data-domain="${escapeHtml(domain)}" data-type="${escapeHtml(type)}" aria-label="${count} records for ${escapeHtml(domain)} and ${escapeHtml(type)}">${count}</button></td>`;
    }).join('');
    return `<tr><th class="row-label">${escapeHtml(domain)}</th>${cells}</tr>`;
  }).join('');

  matrix.innerHTML = `${header}<tbody>${rows}</tbody>`;
  matrix.querySelectorAll('button:not([disabled])').forEach(button => {
    button.addEventListener('click', () => {
      $('filter-domain').value = button.dataset.domain;
      $('filter-type').value = button.dataset.type;
      renderAll();
      $('records').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

function renderProducts() {
  const relevantProductNames = new Set(state.visibleRecords.map(r => r.product));
  const cards = state.products.map(product => {
    const recordCount = state.records.filter(r => r.product_id === product.id).length;
    const visibleCount = state.visibleRecords.filter(r => r.product_id === product.id).length;
    const faded = relevantProductNames.size && visibleCount === 0 ? ' style="opacity:.52"' : '';
    return `
      <article class="product-card"${faded}>
        <div class="product-meta">
          <span class="badge ${priorityClass(product.priority)}">${escapeHtml(product.priority)}</span>
          <span class="badge">${escapeHtml(product.platform)}</span>
          <span class="badge">${visibleCount}/${recordCount} visible</span>
        </div>
        <h3>${escapeHtml(product.name)}</h3>
        <p><strong>${escapeHtml(product.developer)}</strong> · ${escapeHtml(product.category)}</p>
        <p>${escapeHtml(product.current_stage)}</p>
        <p>${escapeHtml(product.availability_signal)}</p>
        <p class="muted"><strong>Target:</strong> ${escapeHtml(product.target_population)}</p>
        <p>${(product.target_geographies || []).map(g => `<span class="badge">${escapeHtml(g)}</span>`).join(' ')}</p>
      </article>
    `;
  }).join('');
  $('product-grid').innerHTML = cards;
}

function renderRecords() {
  const container = $('records-list');
  if (!state.visibleRecords.length) {
    container.innerHTML = '<div class="empty-state">No records match the current filters. Reset filters or broaden the search.</div>';
    return;
  }

  container.innerHTML = state.visibleRecords.map(record => {
    const url = record.source_url ? `<a class="record-link" href="${escapeHtml(record.source_url)}" target="_blank" rel="noopener">Open source</a>` : '<span class="muted">No external source: curator-defined gap</span>';
    return `
      <article class="record-card" data-priority="${escapeHtml(record.priority)}">
        <div class="record-meta">
          <span class="badge ${priorityClass(record.priority)}">${escapeHtml(record.priority)}</span>
          <span class="badge ${verificationClass(record.verification)}">${escapeHtml(record.verification)}</span>
          <span class="badge">${escapeHtml(record.evidence_domain)}</span>
          <span class="badge">${escapeHtml(record.evidence_type)}</span>
          <span class="badge">${escapeHtml(record.source_group)}</span>
        </div>
        <h3>${escapeHtml(record.title)}</h3>
        <p><strong>${escapeHtml(record.product)}</strong> · ${escapeHtml(record.developer)} · ${escapeHtml(record.platform)}</p>
        <p>${escapeHtml(record.summary)}</p>
        <p class="muted"><strong>Population:</strong> ${escapeHtml(record.population)}<br><strong>Outcomes:</strong> ${escapeHtml((record.outcomes || []).join(', '))}</p>
        <p>${(record.jurisdictions || []).map(j => `<span class="badge">${escapeHtml(j)}</span>`).join(' ')}</p>
        <footer>
          <span class="record-id">${escapeHtml(record.id)} · source ${escapeHtml(record.source_date)} · map ${escapeHtml(record.map_updated)}</span>
          ${url}
        </footer>
      </article>
    `;
  }).join('');
}

function renderGaps() {
  $('gap-list').innerHTML = state.gaps.map(gap => `
    <article class="gap-card">
      <span class="badge ${priorityClass(gap.severity)}">${escapeHtml(gap.severity)}</span>
      <span class="badge">${escapeHtml(gap.domain)}</span>
      <h3>${escapeHtml(gap.title)}</h3>
      <p>${escapeHtml(gap.detail)}</p>
    </article>
  `).join('');
}

function renderActiveFilterText() {
  const entries = [
    ['search', $('filter-search').value],
    ['product', $('filter-product').value],
    ['domain', $('filter-domain').value],
    ['type', $('filter-type').value],
    ['geography', $('filter-jurisdiction').value],
    ['stage', $('filter-stage').value],
    ['source', $('filter-source').value],
    ['priority', $('filter-priority').value],
    ['since', $('filter-date').value]
  ].filter(([, value]) => value);
  $('active-filter-text').textContent = entries.length ? `Active filters: ${entries.map(([key, value]) => `${key}=${value}`).join(' · ')}` : 'No active filters.';
}

function renderAll() {
  state.visibleRecords = state.records.filter(passesFilters);
  updateStats();
  renderMatrix();
  renderProducts();
  renderRecords();
  renderActiveFilterText();
}

function toCsvCell(value) {
  const text = Array.isArray(value) ? value.join('; ') : (value ?? '');
  return `"${String(text).replace(/"/g, '""')}"`;
}

function exportVisibleCsv() {
  const headers = ['id','title','product','developer','platform','development_stage','jurisdictions','evidence_domain','evidence_type','population','outcomes','source_group','source_title','source_url','source_date','map_updated','verification','priority','summary','tags'];
  const rows = state.visibleRecords.map(record => headers.map(h => toCsvCell(record[h])).join(','));
  const csv = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `influenza-evidence-records-${new Date().toISOString().slice(0,10)}.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

async function writeClipboard(text, successLabel) {
  try {
    await navigator.clipboard.writeText(text);
    const previous = successLabel.textContent;
    successLabel.textContent = 'Copied';
    setTimeout(() => { successLabel.textContent = previous; }, 1200);
  } catch (error) {
    console.warn('Clipboard failed', error);
  }
}

function copyVisibleRecordIds() {
  writeClipboard(state.visibleRecords.map(r => r.id).join('\n'), $('copy-record-ids'));
}

function copySourceGroups() {
  writeClipboard(state.sourceGroups.map(s => `${s.name}: ${s.description}`).join('\n'), $('copy-source-list'));
}

async function loadData() {
  const [records, products, domains, types, gaps, sourceGroups] = await Promise.all([
    fetch(DATA_PATHS.records).then(r => r.json()),
    fetch(DATA_PATHS.products).then(r => r.json()),
    fetch(DATA_PATHS.domains).then(r => r.json()),
    fetch(DATA_PATHS.types).then(r => r.json()),
    fetch(DATA_PATHS.gaps).then(r => r.json()),
    fetch(DATA_PATHS.sourceGroups).then(r => r.json())
  ]);
  state.records = records;
  state.products = products;
  state.domains = domains;
  state.types = types;
  state.gaps = gaps;
  state.sourceGroups = sourceGroups;
  setupFilters();
  renderSourceGroups();
  renderGaps();
  renderAll();
}

loadData().catch(error => {
  console.error(error);
  document.body.insertAdjacentHTML('afterbegin', `<div class="empty-state">Dashboard data failed to load. Serve this folder over HTTP, for example with <code>python3 -m http.server 8000</code>.</div>`);
});
