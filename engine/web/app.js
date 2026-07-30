/**
 * 数据要素贡献值分配 Demo — 前端交互
 */

// ============================================================
// State
// ============================================================
const state = {
  calculateResult: null,
  simulateResult: null,
  selectedCallIdx: null,
  chartInstance: null,
  chartView: 'contribution',
};

const DEFAULT_CONTRIBUTORS = [
  { name: '张医生-罕见病', hours: 40, accuracy: 0.96, complexity: 5, pool_size: 3 },
  { name: '李标注-常见病', hours: 80, accuracy: 0.94, complexity: 2, pool_size: 10000 },
  { name: '王工程师-影像', hours: 60, accuracy: 0.98, complexity: 4, pool_size: 500 },
];

// ============================================================
// DOM helpers
// ============================================================
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);
const fmtInt = (n) => Math.round(n).toLocaleString('zh-CN');
const fmtYuan = (n) => '¥' + fmtInt(n);

// ============================================================
// Form collection
// ============================================================
function collectForm() {
  const rows = $$('#contributorList .contributor-row');
  const contributors = [];
  rows.forEach(row => {
    const name = row.querySelector('.ctr-name').value.trim();
    const hours = parseFloat(row.querySelector('.ctr-hours').value);
    const accuracy = parseFloat(row.querySelector('.ctr-accuracy').value);
    const complexity = parseInt(row.querySelector('.ctr-complexity').value);
    const pool_size = parseInt(row.querySelector('.ctr-pool').value);
    if (name && !isNaN(hours) && !isNaN(accuracy) && !isNaN(complexity) && !isNaN(pool_size)) {
      contributors.push({ name, hours, accuracy, complexity, pool_size });
    }
  });
  return contributors;
}

function collectGlobalParams() {
  return {
    k: parseFloat($('#gk').value) || 0.01,
    profit_per_call: parseFloat($('#gProfit').value) || 20000,
    platform_share: parseFloat($('#gShare').value) || 0.3,
    cap_multiplier: parseFloat($('#gCapMul').value) || 300,
    traditional_rate: parseFloat($('#gTradRate').value) || 5,
    timeline_calls: parseInt($('#gTimeline').value) || 5,
    projection_calls: parseInt($('#gProjection').value) || 50,
  };
}

// ============================================================
// API calls
// ============================================================
async function apiCalculate() {
  const contributors = collectForm();
  const params = collectGlobalParams();
  const body = {
    contributors,
    profit: params.profit_per_call,
    k: params.k,
    platform_share: params.platform_share,
    cap_multiplier: params.cap_multiplier,
    traditional_rate: params.traditional_rate,
  };
  const resp = await fetch('/api/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || '请求失败');
  }
  return resp.json();
}

async function apiSimulate() {
  const contributors = collectForm();
  const params = collectGlobalParams();
  const body = { contributors, ...params };
  const resp = await fetch('/api/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json();
    throw new Error(err.detail || '请求失败');
  }
  return resp.json();
}

// ============================================================
// Render: Detail Table
// ============================================================
function renderDetailTable(data) {
  const tbody = $('#detailTable tbody');
  tbody.innerHTML = '';
  data.results.forEach(r => {
    tbody.innerHTML += `
      <tr>
        <td>${r.name}</td>
        <td>${r.hours}h</td>
        <td>${(r.accuracy * 100).toFixed(0)}%</td>
        <td>L${r.complexity}</td>
        <td>${r.pool_size.toLocaleString()}</td>
        <td>${r.scarcity}</td>
        <td>${r.contribution.toFixed(2)}</td>
        <td>${r.share_pct}%</td>
        <td>¥${r.profit.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</td>
        <td>¥${fmtInt(r.cap)}</td>
        <td>¥${fmtInt(r.traditional_income)}</td>
      </tr>`;
  });
  // 汇总行
  tbody.innerHTML += `
    <tr style="font-weight:600;background:#fafaf8">
      <td>合计</td>
      <td></td><td></td><td></td><td></td><td></td>
      <td>${data.total_contribution.toFixed(2)}</td>
      <td>100%</td>
      <td>¥${data.distributable.toLocaleString()}</td>
      <td></td>
      <td>¥${fmtInt(data.total_traditional)}</td>
    </tr>
    <tr>
      <td>公共服务</td>
      <td colspan="9"></td>
      <td>¥${data.platform_profit.toLocaleString()}</td>
    </tr>`;
  $('#detailSection').style.display = '';
}

// ============================================================
// Render: Bar Chart
// ============================================================
function renderChart(data) {
  $('#chartSection').style.display = '';
  const canvas = $('#mainChart');
  const ctx = canvas.getContext('2d');

  const labels = [...data.results.map(r => r.name), '公共服务扣除'];

  let dataset;
  if (state.chartView === 'contribution') {
    dataset = {
      label: '贡献值',
      data: [...data.results.map(r => r.contribution), data.platform_profit],
      backgroundColor: [
        '#2e6edf', '#4a90d9', '#6baed6', '#f0a050',
      ],
    };
  } else {
    dataset = {
      label: '单次分润 (¥)',
      data: [...data.results.map(r => r.profit), data.platform_profit],
      backgroundColor: [
        '#2e6edf', '#4a90d9', '#6baed6', '#f0a050',
      ],
    };
  }

  if (state.chartInstance) state.chartInstance.destroy();

  state.chartInstance = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: [dataset] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => state.chartView === 'contribution'
              ? ` ${ctx.raw.toFixed(2)}`
              : ` ¥${ctx.raw.toLocaleString('zh-CN')}`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (v) => state.chartView === 'contribution'
              ? v.toFixed(0)
              : '¥' + (v / 1000).toFixed(0) + 'k',
          },
        },
      },
    },
  });
}

// ============================================================
// Render: Compare Cards
// ============================================================
function renderCompareCards(simData) {
  $('#cardIndustry').textContent = fmtYuan(simData.total_traditional);
  $('#cardAI').textContent = fmtYuan(simData.total_worker_income_projection);
  $('#cardPool').textContent = fmtYuan(simData.total_pool_projection);
  $('#compareCards').style.display = '';
}

// ============================================================
// Render: Highlight Quote
// ============================================================
function renderHighlight(simData) {
  const summaries = simData.summaries;
  if (!summaries || summaries.length === 0) return;
  // 找传统收入最低、AI 收入最高的那个人（典型是张医生）
  let best = summaries[0];
  for (const s of summaries) {
    if (s.projection_income / Math.max(s.traditional_income, 1) > best.projection_income / Math.max(best.traditional_income, 1)) {
      best = s;
    }
  }
  $('#quoteText').textContent =
    `${best.name}：工业时代 ${fmtYuan(best.traditional_income)} → AI 时代 ${fmtYuan(best.projection_income)}`;
  $('#highlightQuote').style.display = '';
}

// ============================================================
// Render: Timeline
// ============================================================
function renderTimeline(simData) {
  $('#timelineSection').style.display = '';
  const bar = $('#timelineBar');
  bar.innerHTML = '';

  const calls = simData.calls;
  state.selectedCallIdx = null;
  $('#timelineDetail').style.display = 'none';

  calls.forEach((call, i) => {
    const node = document.createElement('div');
    node.className = 'timeline-node';
    node.textContent = i + 1;
    // 检查是否有 people hit cap
    const hasOverflow = call.items.some(it => it.to_pool > 0);
    if (hasOverflow) node.classList.add('has-overflow');

    node.addEventListener('click', () => showTimelineDetail(call, i, simData));

    // 入场动画
    setTimeout(() => {
      node.classList.add('appear');
    }, i * 200);

    bar.appendChild(node);
  });
}

function showTimelineDetail(call, idx, simData) {
  // 更新 timeline 高亮
  const nodes = $$('.timeline-node');
  nodes.forEach((n, i) => {
    n.classList.toggle('active', i === idx);
  });
  state.selectedCallIdx = idx;

  $('#tlCallIdx').textContent = idx + 1;
  const tbody = $('#tlDetailBody');
  tbody.innerHTML = '';

  // 获取 contribution 数据用于显示占比
  const calculateData = state.calculateResult;
  const contribMap = {};
  if (calculateData) {
    calculateData.results.forEach(r => { contribMap[r.name] = r.share_pct; });
  }

  call.items.forEach(it => {
    const shareInfo = contribMap[it.name] !== undefined ? ` (${contribMap[it.name]}%)` : '';
    const overflowClass = it.to_pool > 0 ? ' style="color:#b85c00;font-weight:600"' : '';
    tbody.innerHTML += `
      <tr>
        <td>${it.name}${shareInfo}</td>
        <td${overflowClass}>¥${it.raw_profit.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</td>
        <td>¥${it.credited.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</td>
        <td${it.to_pool > 0 ? ' style="color:#c62828"' : ''}>${it.to_pool > 0 ? '⚠ ' : ''}¥${it.to_pool.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</td>
      </tr>`;
  });

  tbody.innerHTML += `
    <tr style="font-weight:600;background:#fafaf8">
      <td>公共服务平台</td>
      <td colspan="2"></td>
      <td>¥${call.platform_profit.toLocaleString()}</td>
    </tr>`;

  $('#timelineDetail').style.display = '';
}

// ============================================================
// Event handlers
// ============================================================
async function handleCalculate() {
  try {
    state.calculateResult = await apiCalculate();
    renderDetailTable(state.calculateResult);
    renderChart(state.calculateResult);
    $('#cardIndustry').textContent = fmtYuan(state.calculateResult.total_traditional);
    $('#compareCards').style.display = '';
  } catch (e) {
    alert('计算失败: ' + e.message);
  }
}

async function handleSimulate() {
  try {
    // 先跑 calculate 拿到贡献值表
    state.calculateResult = await apiCalculate();
    renderDetailTable(state.calculateResult);
    renderChart(state.calculateResult);

    // 再跑 simulate
    state.simulateResult = await apiSimulate();
    renderCompareCards(state.simulateResult);
    renderHighlight(state.simulateResult);
    renderTimeline(state.simulateResult);
  } catch (e) {
    alert('模拟失败: ' + e.message);
  }
}

function handleChartTabSwitch(view) {
  state.chartView = view;
  $$('.chart-tab').forEach(t => t.classList.toggle('active', t.dataset.view === view));
  if (state.calculateResult) {
    renderChart(state.calculateResult);
  }
}

function addContributorRow(data) {
  const list = $('#contributorList');
  const tmpl = $('#tmplContributor');
  const clone = tmpl.content.cloneNode(true);
  const row = clone.querySelector('.contributor-row');

  if (data) {
    row.querySelector('.ctr-name').value = data.name;
    row.querySelector('.ctr-hours').value = data.hours;
    row.querySelector('.ctr-accuracy').value = data.accuracy;
    row.querySelector('.ctr-complexity').value = data.complexity;
    row.querySelector('.ctr-pool').value = data.pool_size;
  }

  row.querySelector('.btn-remove').addEventListener('click', () => {
    row.remove();
    updateRemoveButtons();
  });

  list.appendChild(clone);
  updateRemoveButtons();
}

function updateRemoveButtons() {
  const rows = $$('#contributorList .contributor-row');
  rows.forEach(row => {
    row.querySelector('.btn-remove').style.display = rows.length > 1 ? '' : 'none';
  });
}

function bindEvents() {
  $('#btnCalculate').addEventListener('click', handleCalculate);
  $('#btnSimulate').addEventListener('click', handleSimulate);
  $('#btnAddContributor').addEventListener('click', () => addContributorRow(null));

  $$('.chart-tab').forEach(tab => {
    tab.addEventListener('click', () => handleChartTabSwitch(tab.dataset.view));
  });
}

// ============================================================
// Init
// ============================================================
function init() {
  bindEvents();
  // 预填默认贡献者
  DEFAULT_CONTRIBUTORS.forEach(c => addContributorRow(c));
  // 自动运行一次 simulate 展示完整故事
  setTimeout(() => handleSimulate(), 300);
}

document.addEventListener('DOMContentLoaded', init);
