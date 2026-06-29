// ── CONFIG ────────────────────────────────────────────────
// Change this to your Render backend URL after deploying
const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:5000'
  : 'https://futureflow-uux9.onrender.com'; 

// ── STATE ─────────────────────────────────────────────────
let sessionOrders = [];
let currentSide = 'BUY';
let tradeSide = 'BUY';

// ── INIT ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupNav();
  setupQuickTrade();
  setupTradeForm();
  setupBalance();
  setupMisc();
  fetchBTCPrice();
  fetchBalanceStats();
  setInterval(fetchBTCPrice, 15000);
});

// ── NAVIGATION ────────────────────────────────────────────
function setupNav() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', e => {
      e.preventDefault();
      const page = item.dataset.page;
      navigateTo(page);
      document.querySelector('.sidebar').classList.remove('open');
    });
  });

  document.getElementById('menuToggle').addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
  });
}

function navigateTo(page) {
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelector(`[data-page="${page}"]`).classList.add('active');
  document.getElementById(`page-${page}`).classList.add('active');
  document.getElementById('pageTitle').textContent = {
    dashboard: 'Dashboard', trade: 'Place Order',
    history: 'Order History', balance: 'Balance'
  }[page];

  if (page === 'balance') fetchBalance();
}

// ── BTC PRICE ─────────────────────────────────────────────
async function fetchBTCPrice() {
  try {
    const r = await fetch('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT');
    const d = await r.json();
    const price = parseFloat(d.price).toLocaleString('en-US', { maximumFractionDigits: 0 });
    document.getElementById('btcPrice').textContent = `$${price}`;
  } catch {
    document.getElementById('btcPrice').textContent = '—';
  }
}

// ── BALANCE (STATS) ───────────────────────────────────────
async function fetchBalanceStats() {
  try {
    const r = await fetch(`${API_BASE}/balance`);
    const d = await r.json();
    if (d.success) {
      document.getElementById('stat-total').textContent =
        parseFloat(d.data.balance).toLocaleString('en-US', { maximumFractionDigits: 2 });
      document.getElementById('stat-available').textContent =
        parseFloat(d.data.availableBalance).toLocaleString('en-US', { maximumFractionDigits: 2 });
    }
  } catch {
    document.getElementById('stat-total').textContent = '—';
    document.getElementById('stat-available').textContent = '—';
  }
}

// ── QUICK TRADE ───────────────────────────────────────────
function setupQuickTrade() {
  const buyBtn = document.getElementById('q-buy');
  const sellBtn = document.getElementById('q-sell');

  buyBtn.addEventListener('click', () => {
    currentSide = 'BUY';
    buyBtn.classList.add('active');
    sellBtn.classList.remove('active');
  });
  sellBtn.addEventListener('click', () => {
    currentSide = 'SELL';
    sellBtn.classList.add('active');
    buyBtn.classList.remove('active');
  });

  document.getElementById('q-market').addEventListener('click', () => placeQuickOrder(false));
  document.getElementById('q-dryrun').addEventListener('click', () => placeQuickOrder(true));
}

async function placeQuickOrder(dryRun) {
  const symbol = document.getElementById('q-symbol').value;
  const qty = parseFloat(document.getElementById('q-qty').value);
  const resultEl = document.getElementById('q-result');

  if (!qty || qty <= 0) { showToast('Enter a valid quantity', 'error'); return; }

  const payload = { symbol, side: currentSide, type: 'MARKET', quantity: qty, dry_run: dryRun };

  resultEl.classList.remove('hidden', 'success', 'error');
  resultEl.textContent = 'Placing order...';

  try {
    const r = await fetch(`${API_BASE}/order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const d = await r.json();

    if (d.success) {
      if (dryRun) {
        resultEl.classList.add('info');
        resultEl.innerHTML = `🔍 DRY RUN\nSymbol: ${symbol}\nSide: ${currentSide}\nQty: ${qty}`;
        showToast('Dry run preview ready', 'info');
      } else {
        resultEl.classList.add('success');
        resultEl.innerHTML = `✅ ORDER PLACED\nID: ${d.data.orderId}\nStatus: ${d.data.status}\nExec Qty: ${d.data.executedQty}`;
        addToHistory({ ...payload, ...d.data, dry_run: false });
        updateOrderCount();
        showToast('Market order placed!', 'success');
      }
    } else {
      resultEl.classList.add('error');
      resultEl.textContent = `❌ ${d.error}`;
      showToast(d.error, 'error');
    }
  } catch (err) {
    resultEl.classList.add('error');
    resultEl.textContent = `❌ Cannot reach backend API`;
    showToast('Backend unreachable', 'error');
  }
}

// ── TRADE FORM ────────────────────────────────────────────
function setupTradeForm() {
  const buyBtn  = document.getElementById('t-buy');
  const sellBtn = document.getElementById('t-sell');
  const typeEl  = document.getElementById('t-type');

  buyBtn.addEventListener('click',  () => { tradeSide = 'BUY';  buyBtn.classList.add('active'); sellBtn.classList.remove('active'); updateSummary(); });
  sellBtn.addEventListener('click', () => { tradeSide = 'SELL'; sellBtn.classList.add('active'); buyBtn.classList.remove('active'); updateSummary(); });

  typeEl.addEventListener('change', () => {
    const t = typeEl.value;
    document.getElementById('price-group').classList.toggle('hidden', t !== 'LIMIT');
    document.getElementById('stop-group').classList.toggle('hidden', !['STOP_MARKET','TAKE_PROFIT_MARKET'].includes(t));
    updateSummary();
  });

  ['t-symbol','t-qty','t-price','t-stop'].forEach(id => {
    document.getElementById(id).addEventListener('input', updateSummary);
  });

  document.getElementById('placeOrderBtn').addEventListener('click', placeTradeOrder);
  updateSummary();
}

function updateSummary() {
  const symbol = document.getElementById('t-symbol').value;
  const type   = document.getElementById('t-type').value;
  const qty    = document.getElementById('t-qty').value;
  const price  = document.getElementById('t-price').value;
  const stop   = document.getElementById('t-stop').value;

  document.getElementById('s-symbol').textContent = symbol || '—';
  document.getElementById('s-side').textContent   = tradeSide;
  document.getElementById('s-type').textContent   = type;
  document.getElementById('s-qty').textContent    = qty || '—';

  const priceRow = document.getElementById('s-price-row');
  if (type === 'LIMIT') {
    priceRow.classList.remove('hidden');
    document.getElementById('s-price').textContent = price ? `$${price}` : '—';
  } else if (['STOP_MARKET','TAKE_PROFIT_MARKET'].includes(type)) {
    priceRow.classList.remove('hidden');
    document.getElementById('s-price').textContent = stop ? `$${stop} (trigger)` : '—';
  } else {
    priceRow.classList.add('hidden');
  }

  const isDry = document.getElementById('dryRunToggle').checked;
  document.getElementById('placeOrderBtn').textContent = isDry ? '🔍 Preview Order (Dry Run)' : 'Place Order';
}

async function placeTradeOrder() {
  const symbol   = document.getElementById('t-symbol').value;
  const type     = document.getElementById('t-type').value;
  const qty      = parseFloat(document.getElementById('t-qty').value);
  const price    = parseFloat(document.getElementById('t-price').value) || null;
  const stop     = parseFloat(document.getElementById('t-stop').value) || null;
  const dryRun   = document.getElementById('dryRunToggle').checked;
  const resultEl = document.getElementById('t-result');

  if (!qty || qty <= 0) { showToast('Enter a valid quantity', 'error'); return; }

  const payload = {
    symbol, side: tradeSide, type, quantity: qty,
    price, stop_price: stop, dry_run: dryRun
  };

  const btn = document.getElementById('placeOrderBtn');
  btn.textContent = 'Placing...';
  btn.disabled = true;
  resultEl.classList.add('hidden');

  try {
    const r = await fetch(`${API_BASE}/order`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const d = await r.json();

    resultEl.classList.remove('hidden', 'success', 'error', 'info');

    if (d.success) {
      if (dryRun) {
        resultEl.classList.add('info');
        const p = d.order_preview;
        resultEl.innerHTML = `🔍 DRY RUN — Order not sent\n\nSymbol : ${p.symbol}\nSide   : ${p.side}\nType   : ${p.type}\nQty    : ${p.quantity}${p.price ? `\nPrice  : $${p.price}` : ''}${p.stop_price ? `\nStop   : $${p.stop_price}` : ''}`;
        showToast('Dry run preview ready', 'info');
        addToHistory({ ...p, status: 'DRY_RUN', dry_run: true });
      } else {
        resultEl.classList.add('success');
        resultEl.innerHTML = `✅ ORDER PLACED\n\nOrder ID : ${d.data.orderId}\nStatus   : ${d.data.status}\nExec Qty : ${d.data.executedQty}\nAvg Price: $${d.data.avgPrice}`;
        showToast(`${type} order placed!`, 'success');
        addToHistory({ ...payload, ...d.data, dry_run: false });
        updateOrderCount();
        fetchBalanceStats();
      }
    } else {
      resultEl.classList.add('error');
      resultEl.innerHTML = `❌ ${d.error}`;
      showToast(d.error, 'error');
    }
  } catch {
    resultEl.classList.remove('hidden');
    resultEl.classList.add('error');
    resultEl.textContent = '❌ Cannot reach backend API';
    showToast('Backend unreachable', 'error');
  } finally {
    btn.disabled = false;
    updateSummary();
  }
}

// ── BALANCE PAGE ──────────────────────────────────────────
function setupBalance() {
  document.getElementById('refreshBalance').addEventListener('click', fetchBalance);
}

async function fetchBalance() {
  const el = document.getElementById('balanceDisplay');
  el.innerHTML = '<div class="balance-loading">Fetching balance...</div>';
  try {
    const r = await fetch(`${API_BASE}/balance`);
    const d = await r.json();
    if (d.success) {
      const b = d.data;
      el.innerHTML = `
        <div class="balance-row highlight">
          <div><div class="balance-asset">Total Balance</div><div class="balance-sub">USDT</div></div>
          <div class="balance-amount">${parseFloat(b.balance).toLocaleString('en-US', { maximumFractionDigits: 2 })}</div>
        </div>
        <div class="balance-row">
          <div><div class="balance-asset">Available Balance</div><div class="balance-sub">USDT — free to trade</div></div>
          <div class="balance-amount">${parseFloat(b.availableBalance).toLocaleString('en-US', { maximumFractionDigits: 2 })}</div>
        </div>
        <div class="balance-row">
          <div><div class="balance-asset">In Use</div><div class="balance-sub">USDT — in open positions/orders</div></div>
          <div class="balance-amount">${(parseFloat(b.balance) - parseFloat(b.availableBalance)).toLocaleString('en-US', { maximumFractionDigits: 2 })}</div>
        </div>`;
      showToast('Balance refreshed', 'success');
    } else {
      el.innerHTML = `<div class="balance-loading" style="color:var(--red)">❌ ${d.error}</div>`;
    }
  } catch {
    el.innerHTML = `<div class="balance-loading" style="color:var(--red)">❌ Cannot reach backend API</div>`;
  }
}

// ── ORDER HISTORY ─────────────────────────────────────────
function addToHistory(order) {
  const now = new Date().toLocaleTimeString();
  sessionOrders.unshift({ ...order, time: now });
  renderHistory();
  renderDashOrders();
}

function renderHistory() {
  const tbody = document.getElementById('historyBody');
  if (!sessionOrders.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty-td">No orders yet.</td></tr>';
    return;
  }
  tbody.innerHTML = sessionOrders.map(o => `
    <tr>
      <td>${o.time}</td>
      <td>${o.symbol}</td>
      <td class="${o.side === 'BUY' ? 'td-buy' : 'td-sell'}">${o.side}</td>
      <td>${o.type}</td>
      <td>${o.quantity}</td>
      <td>${o.price ? '$' + o.price : o.stop_price ? '$' + o.stop_price : 'MKT'}</td>
      <td class="${o.dry_run ? 'td-dry' : 'td-filled'}">${o.status || (o.dry_run ? 'DRY_RUN' : '—')}</td>
      <td>${o.orderId || '—'}</td>
    </tr>`).join('');
}

function renderDashOrders() {
  const el = document.getElementById('dash-orders');
  const recent = sessionOrders.slice(0, 5);
  if (!recent.length) { el.innerHTML = '<div class="empty-state">No orders placed yet this session.</div>'; return; }
  el.innerHTML = recent.map(o => `
    <div class="order-pill">
      <div class="pill-left">
        <span class="pill-badge ${o.side === 'BUY' ? 'buy' : 'sell'}">${o.side}</span>
        <span class="pill-symbol">${o.symbol}</span>
        <span class="pill-type">${o.type}</span>
      </div>
      <span class="pill-status" style="color:${o.dry_run ? 'var(--blue)' : 'var(--green)'}">${o.dry_run ? 'DRY RUN' : o.status || 'PLACED'}</span>
    </div>`).join('');
}

function updateOrderCount() {
  const real = sessionOrders.filter(o => !o.dry_run).length;
  document.getElementById('stat-orders').textContent = real;
}

// ── MISC ──────────────────────────────────────────────────
function setupMisc() {
  document.getElementById('clearHistory').addEventListener('click', () => {
    sessionOrders = [];
    renderHistory();
    renderDashOrders();
    updateOrderCount();
    showToast('History cleared', 'info');
  });

  document.getElementById('refreshBtn').addEventListener('click', async () => {
    const btn = document.getElementById('refreshBtn');
    btn.classList.add('spinning');
    await Promise.all([fetchBTCPrice(), fetchBalanceStats()]);
    setTimeout(() => btn.classList.remove('spinning'), 600);
    showToast('Data refreshed', 'success');
  });
}

// ── TOAST ─────────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = 'info') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = `toast ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add('hidden'), 3000);
}
