"""
dashboard.py — Servidor web Flask para el dashboard en tiempo real.

Lee STATE_FILE (/tmp/state.json) escrito por basket.py y lo sirve
como API + interfaz HTML.

Rutas:
  GET /          → Dashboard HTML (single page)
  GET /api/state → Estado actual en JSON (para polling)
"""

import json
import os
import redis
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

REDIS_URL = os.environ.get("REDIS_URL") or os.environ.get("REDIS_PRIVATE_URL")
_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


def read_state() -> dict:
    if not REDIS_URL:
        return {"error": "REDIS_URL no configurada. Agrega el plugin Redis en Railway."}
    try:
        raw = get_redis().get("basket:state")
        if raw is None:
            return {"error": "Bot no iniciado aún. Esperando datos del bot..."}
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


@app.route("/api/state")
def api_state():
    return jsonify(read_state())


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Basket Dashboard — Polymarket</title>
<style>
  :root {
    --bg: #0d0d0d;
    --surface: #161616;
    --border: #2a2a2a;
    --accent: #00ff88;
    --red: #ff4466;
    --yellow: #ffd600;
    --blue: #4488ff;
    --text: #e0e0e0;
    --muted: #666;
    --font: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 13px;
    min-height: 100vh;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
  }
  header h1 { font-size: 15px; letter-spacing: 0.08em; color: var(--accent); }
  #phase-badge {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    background: #1a2a1a;
    color: var(--accent);
    border: 1px solid var(--accent);
    transition: all 0.3s;
  }
  #phase-badge.sleeping { background: #1a1a2a; color: var(--blue); border-color: var(--blue); }
  #phase-badge.error    { background: #2a1a1a; color: var(--red);  border-color: var(--red); }
  #last-update { color: var(--muted); font-size: 11px; }

  main { padding: 20px 24px; display: grid; gap: 16px; }

  /* ── Stats Row ── */
  .stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 10px;
  }
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
  }
  .stat-card .label { color: var(--muted); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
  .stat-card .value { font-size: 20px; font-weight: 700; }
  .stat-card .value.pos { color: var(--accent); }
  .stat-card .value.neg { color: var(--red); }
  .stat-card .value.neutral { color: var(--text); }

  /* ── Two column ── */
  .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 768px) { .two-col { grid-template-columns: 1fr; } }

  /* ── Panel ── */
  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
  }
  .panel-header {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .panel-body { padding: 14px 16px; }

  /* ── Markets table ── */
  .market-row {
    display: grid;
    grid-template-columns: 52px 1fr 1fr 72px;
    gap: 8px;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
  }
  .market-row:last-child { border-bottom: none; }
  .sym-badge {
    font-weight: 700;
    font-size: 13px;
    color: var(--blue);
    background: #0a1a2a;
    border: 1px solid #1a3a5a;
    border-radius: 4px;
    padding: 3px 8px;
    text-align: center;
  }
  .price-group { display: flex; flex-direction: column; gap: 3px; }
  .price-label { font-size: 9px; color: var(--muted); letter-spacing: 0.08em; }
  .price-value { font-size: 14px; font-weight: 600; }
  .price-value.up   { color: var(--accent); }
  .price-value.down { color: var(--red); }
  .signal-arrow { font-size: 18px; }
  .time-badge {
    font-size: 11px;
    color: var(--yellow);
    text-align: right;
  }
  .error-row { color: var(--red); font-size: 11px; padding: 6px 0; }

  /* ── Signal box ── */
  .signal-box {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px;
    text-align: center;
    transition: border-color 0.3s, background 0.3s;
  }
  .signal-box.UP     { border-color: var(--accent); background: #001a0d; }
  .signal-box.DOWN   { border-color: var(--red);    background: #1a0008; }
  .signal-box.NONE   { border-color: var(--border); background: var(--surface); }
  .signal-dir { font-size: 28px; font-weight: 900; letter-spacing: 0.1em; }
  .signal-dir.UP   { color: var(--accent); }
  .signal-dir.DOWN { color: var(--red); }
  .signal-dir.NONE { color: var(--muted); }
  .signal-meta { margin-top: 8px; color: var(--muted); font-size: 11px; line-height: 1.8; }
  .signal-meta span { color: var(--text); }

  /* ── Position box ── */
  .position-box {
    border: 1px solid var(--yellow);
    border-radius: 6px;
    padding: 14px;
    background: #1a1500;
  }
  .position-box .pos-header { color: var(--yellow); font-weight: 700; margin-bottom: 10px; font-size: 12px; }
  .pos-row { display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid #2a2000; font-size: 12px; }
  .pos-row:last-child { border-bottom: none; }
  .pos-row .key { color: var(--muted); }

  /* ── Harmony bar ── */
  .harm-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
  .harm-label { color: var(--muted); font-size: 10px; width: 30px; }
  .harm-bar-wrap { flex: 1; background: #1a1a1a; border-radius: 3px; height: 6px; }
  .harm-bar { height: 100%; border-radius: 3px; transition: width 0.5s; }
  .harm-bar.up-bar   { background: var(--accent); }
  .harm-bar.down-bar { background: var(--red); }
  .harm-val { font-size: 12px; width: 50px; text-align: right; }

  /* ── Events log ── */
  #events-log {
    font-size: 11px;
    line-height: 1.7;
    max-height: 220px;
    overflow-y: auto;
    color: var(--muted);
  }
  #events-log .ev-entry:last-child { color: var(--text); }
  #events-log .ev-win  { color: var(--accent); }
  #events-log .ev-loss { color: var(--red); }
  #events-log .ev-entry { color: var(--muted); }

  /* ── Trades table ── */
  .trades-table { width: 100%; border-collapse: collapse; font-size: 11px; }
  .trades-table th { color: var(--muted); text-align: left; padding: 4px 8px; border-bottom: 1px solid var(--border); font-weight: normal; font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; }
  .trades-table td { padding: 6px 8px; border-bottom: 1px solid #1a1a1a; }
  .trades-table tr:last-child td { border-bottom: none; }
  .badge-win  { color: var(--accent); font-weight: 700; }
  .badge-loss { color: var(--red);    font-weight: 700; }

  /* ── PnL sparkline ── */
  #sparkline { width: 100%; height: 60px; }

  .consensus-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
  }
  .consensus-badge.FULL { background: #001a0d; color: var(--accent); border: 1px solid var(--accent); }
  .consensus-badge.SOFT { background: #1a1500; color: var(--yellow); border: 1px solid var(--yellow); }
  .consensus-badge.NONE { background: #1a1a1a; color: var(--muted);  border: 1px solid var(--border); }

  .sleeping-overlay {
    text-align: center;
    padding: 20px;
    color: var(--blue);
  }
  .sleeping-overlay .zzz { font-size: 28px; margin-bottom: 8px; }
  .sleeping-overlay .wake { color: var(--muted); font-size: 11px; margin-top: 6px; }
</style>
</head>
<body>

<header>
  <h1>⬡ BASKET — DIVERGENCIA ARMÓNICA</h1>
  <div style="display:flex; align-items:center; gap:16px;">
    <span id="last-update">–</span>
    <span id="phase-badge">–</span>
  </div>
</header>

<main>
  <!-- Stats -->
  <div class="stats-row">
    <div class="stat-card">
      <div class="label">Capital</div>
      <div class="value neutral" id="s-capital">–</div>
    </div>
    <div class="stat-card">
      <div class="label">P&L Total</div>
      <div class="value" id="s-pnl">–</div>
    </div>
    <div class="stat-card">
      <div class="label">ROI</div>
      <div class="value" id="s-roi">–</div>
    </div>
    <div class="stat-card">
      <div class="label">Win Rate</div>
      <div class="value" id="s-winrate">–</div>
    </div>
    <div class="stat-card">
      <div class="label">Trades W/L</div>
      <div class="value neutral" id="s-trades">–</div>
    </div>
    <div class="stat-card">
      <div class="label">Max Drawdown</div>
      <div class="value neg" id="s-dd">–</div>
    </div>
    <div class="stat-card">
      <div class="label">Ciclo</div>
      <div class="value neutral" id="s-cycle">–</div>
    </div>
    <div class="stat-card">
      <div class="label">Skipped</div>
      <div class="value neutral" id="s-skipped">–</div>
    </div>
  </div>

  <!-- Markets + Signal -->
  <div class="two-col">

    <!-- Markets -->
    <div class="panel">
      <div class="panel-header">
        <span>Mercados</span>
        <span id="consensus-badge" class="consensus-badge NONE">NONE</span>
      </div>
      <div class="panel-body" id="markets-body">
        <div class="error-row">Cargando...</div>
      </div>
    </div>

    <!-- Signal + Position -->
    <div style="display:flex; flex-direction:column; gap:12px;">

      <!-- Harmonic averages -->
      <div class="panel">
        <div class="panel-header">Promedios Armónicos</div>
        <div class="panel-body">
          <div class="harm-row">
            <div class="harm-label">UP</div>
            <div class="harm-bar-wrap"><div class="harm-bar up-bar" id="harm-up-bar" style="width:50%"></div></div>
            <div class="harm-val" id="harm-up-val">–</div>
          </div>
          <div class="harm-row">
            <div class="harm-label">DOWN</div>
            <div class="harm-bar-wrap"><div class="harm-bar down-bar" id="harm-dn-bar" style="width:50%"></div></div>
            <div class="harm-val" id="harm-dn-val">–</div>
          </div>
        </div>
      </div>

      <!-- Signal -->
      <div id="signal-box" class="signal-box NONE">
        <div class="signal-dir NONE" id="sig-dir">–</div>
        <div class="signal-meta" id="sig-meta">Sin señal</div>
      </div>

      <!-- Position -->
      <div id="position-panel" style="display:none;" class="position-box">
        <div class="pos-header">⚡ POSICIÓN ABIERTA</div>
        <div id="position-body"></div>
      </div>

    </div>
  </div>

  <!-- Events + Trades -->
  <div class="two-col">

    <div class="panel">
      <div class="panel-header">Log de Eventos</div>
      <div class="panel-body">
        <div id="events-log">Esperando eventos...</div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header">Últimos Trades</div>
      <div class="panel-body">
        <table class="trades-table">
          <thead>
            <tr>
              <th>ID</th><th>Asset</th><th>Side</th><th>Ask</th><th>PnL</th><th>Resultado</th>
            </tr>
          </thead>
          <tbody id="trades-body">
            <tr><td colspan="6" style="color:var(--muted); padding:10px 8px;">Sin trades aún</td></tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>

</main>

<script>
const POLL_MS = 1500;

function fmt(v, decimals=2) {
  return v != null ? Number(v).toFixed(decimals) : '–';
}

function colorClass(v) {
  if (v == null) return 'neutral';
  return parseFloat(v) >= 0 ? 'pos' : 'neg';
}

function updateStats(s) {
  document.getElementById('s-capital').textContent  = '$' + fmt(s.capital, 4);
  const pnlEl = document.getElementById('s-pnl');
  pnlEl.textContent = (s.total_pnl >= 0 ? '+' : '') + '$' + fmt(s.total_pnl, 4);
  pnlEl.className = 'value ' + colorClass(s.total_pnl);

  const roiEl = document.getElementById('s-roi');
  roiEl.textContent = (s.roi >= 0 ? '+' : '') + fmt(s.roi, 2) + '%';
  roiEl.className = 'value ' + colorClass(s.roi);

  const wrEl = document.getElementById('s-winrate');
  wrEl.textContent = fmt(s.win_rate, 1) + '%';
  wrEl.className = 'value ' + (s.win_rate >= 50 ? 'pos' : 'neg');

  document.getElementById('s-trades').textContent  = `${s.wins}W / ${s.losses}L`;
  document.getElementById('s-dd').textContent      = '-$' + fmt(s.max_drawdown, 4);
  document.getElementById('s-cycle').textContent   = s.cycle || '–';
  document.getElementById('s-skipped').textContent = s.skipped || '0';
}

function updatePhase(s) {
  const badge = document.getElementById('phase-badge');
  const phase = (s.phase || '').toUpperCase();
  badge.textContent = phase;
  badge.className = '';
  if (phase === 'DURMIENDO') badge.classList.add('sleeping');
  else if (s.error) badge.classList.add('error');
}

function updateMarkets(s) {
  const body = document.getElementById('markets-body');
  if (!s.markets) { body.innerHTML = '<div class="error-row">Sin datos de mercado</div>'; return; }
  let html = '';
  ['ETH', 'SOL', 'BTC'].forEach(sym => {
    const m = s.markets[sym];
    if (!m) return;
    const isSig = sym === s.signal_asset;
    const upArrow  = (isSig && s.signal_side === 'UP')   ? '◀' : '';
    const dnArrow  = (isSig && s.signal_side === 'DOWN')  ? '◀' : '';
    if (m.up_mid > 0) {
      html += `<div class="market-row">
        <div class="sym-badge">${sym}</div>
        <div class="price-group">
          <div class="price-label">UP ${upArrow}</div>
          <div class="price-value up">${fmt(m.up_mid, 4)}</div>
        </div>
        <div class="price-group">
          <div class="price-label">DOWN ${dnArrow}</div>
          <div class="price-value down">${fmt(m.dn_mid, 4)}</div>
        </div>
        <div class="time-badge">${m.time_left || 'N/A'}</div>
      </div>`;
    } else {
      html += `<div class="market-row">
        <div class="sym-badge">${sym}</div>
        <div class="error-row" style="grid-column:2/5">${m.error || 'sin datos'}</div>
      </div>`;
    }
  });
  body.innerHTML = html || '<div class="error-row">Sin datos</div>';

  // Consensus badge
  const cb = document.getElementById('consensus-badge');
  cb.textContent = s.consensus || 'NONE';
  cb.className = 'consensus-badge ' + (s.consensus || 'NONE');
}

function updateHarmonic(s) {
  const up = s.harm_up || 0.5;
  const dn = s.harm_dn || 0.5;
  document.getElementById('harm-up-bar').style.width = (up * 100) + '%';
  document.getElementById('harm-dn-bar').style.width = (dn * 100) + '%';
  document.getElementById('harm-up-val').textContent = fmt(up, 4);
  document.getElementById('harm-dn-val').textContent = fmt(dn, 4);
}

function updateSignal(s) {
  const box  = document.getElementById('signal-box');
  const dir  = document.getElementById('sig-dir');
  const meta = document.getElementById('sig-meta');

  const phase = (s.phase || '').toUpperCase();

  if (phase === 'DURMIENDO') {
    box.className = 'signal-box NONE';
    dir.className = 'signal-dir NONE';
    dir.textContent = '💤';
    meta.innerHTML = `<span>DURMIENDO</span><br>${s.next_wake || ''}`;
    return;
  }

  if (!s.signal_asset || Math.abs(s.signal_div || 0) < 0.04) {
    box.className = 'signal-box NONE';
    dir.className = 'signal-dir NONE';
    dir.textContent = '–';
    meta.innerHTML = 'Sin divergencia detectada';
    return;
  }

  const side = s.signal_side;
  box.className = `signal-box ${side}`;
  dir.className = `signal-dir ${side}`;
  dir.textContent = `${s.signal_asset} ${side === 'UP' ? '▲' : '▼'}`;
  const divPts = ((s.signal_div || 0) * 100).toFixed(1);
  const ew = s.entry_window ? '<span style="color:var(--yellow)">⚡ VENTANA ACTIVA</span>' : '<span>Fuera de ventana</span>';
  meta.innerHTML = `Div: <span>${divPts} pts</span> vs armónico<br>${ew}`;
}

function updatePosition(s) {
  const panel = document.getElementById('position-panel');
  const body  = document.getElementById('position-body');
  const pos = s.position;
  if (!pos) { panel.style.display = 'none'; return; }
  panel.style.display = 'block';
  body.innerHTML = `
    <div class="pos-row"><span class="key">Asset</span><span>${pos.asset} ${pos.side}</span></div>
    <div class="pos-row"><span class="key">Entry Ask</span><span>${fmt(pos.entry_price, 4)}</span></div>
    <div class="pos-row"><span class="key">Shares</span><span>${fmt(pos.shares, 4)}</span></div>
    <div class="pos-row"><span class="key">Invertido</span><span>$${fmt(pos.entry_usd, 2)}</span></div>
    <div class="pos-row"><span class="key">Consenso</span><span>${pos.consensus_entry}</span></div>
    <div class="pos-row"><span class="key">Secs entrada</span><span>${fmt(pos.secs_left_entry, 0)}s</span></div>
  `;
}

function updateEvents(s) {
  const el = document.getElementById('events-log');
  const evs = (s.events || []).slice().reverse();
  if (!evs.length) { el.innerHTML = 'Sin eventos aún'; return; }
  el.innerHTML = evs.map(e => {
    let cls = 'ev-entry';
    if (e.includes('WIN') || e.includes('ENTRADA')) cls = 'ev-win';
    else if (e.includes('LOSS') || e.includes('Error') || e.includes('WARN')) cls = 'ev-loss';
    return `<div class="${cls}">${e}</div>`;
  }).join('');
}

function updateTrades(s) {
  const tbody = document.getElementById('trades-body');
  const trades = (s.recent_trades || []).slice().reverse();
  if (!trades.length) {
    tbody.innerHTML = '<tr><td colspan="6" style="color:var(--muted); padding:10px 8px;">Sin trades aún</td></tr>';
    return;
  }
  tbody.innerHTML = trades.map(t => {
    const cls = t.outcome === 'WIN' ? 'badge-win' : 'badge-loss';
    const pnl = parseFloat(t.pnl_usd || 0);
    const pnlStr = (pnl >= 0 ? '+' : '') + '$' + pnl.toFixed(4);
    return `<tr>
      <td>${t.trade_id}</td>
      <td>${t.asset}</td>
      <td>${t.side}</td>
      <td>${fmt(t.entry_ask, 4)}</td>
      <td style="color:${pnl>=0?'var(--accent)':'var(--red)'}">${pnlStr}</td>
      <td class="${cls}">${t.outcome}</td>
    </tr>`;
  }).join('');
}

async function poll() {
  try {
    const r = await fetch('/api/state');
    const s = await r.json();

    if (s.error) {
      document.getElementById('phase-badge').textContent = 'SIN DATOS';
      document.getElementById('phase-badge').className = 'error';
      document.getElementById('markets-body').innerHTML = `<div class="error-row">${s.error}</div>`;
      return;
    }

    updatePhase(s);
    updateStats(s);
    updateMarkets(s);
    updateHarmonic(s);
    updateSignal(s);
    updatePosition(s);
    updateEvents(s);
    updateTrades(s);

    const now = new Date();
    document.getElementById('last-update').textContent =
      'Actualizado: ' + now.toLocaleTimeString('es-CL');

  } catch(e) {
    document.getElementById('last-update').textContent = 'Error de conexión';
  }
}

poll();
setInterval(poll, POLL_MS);
</script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
