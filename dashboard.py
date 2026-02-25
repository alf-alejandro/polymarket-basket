"""
dashboard.py — Servidor Flask para el dashboard en tiempo real.

Lee STATE_FILE (/data/state.json) escrito por basket.py y lo sirve
como API + interfaz HTML espectacular.

Rutas:
  GET /             → Dashboard HTML (single page, polling cada 1.5s)
  GET /api/state    → Estado actual en JSON
  GET /download/csv → Descarga el CSV de trades
"""

import json
import os
from flask import Flask, jsonify, render_template_string, send_file, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

STATE_FILE = os.environ.get("STATE_FILE", "/data/state.json")
CSV_FILE   = os.environ.get("CSV_FILE",   "/data/basket_trades.csv")


def read_state() -> dict:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"error": "Bot no iniciado aún. Esperando state.json..."}
    except Exception as e:
        return {"error": str(e)}


@app.route("/api/state")
def api_state():
    return jsonify(read_state())


@app.route("/download/csv")
def download_csv():
    if not os.path.isfile(CSV_FILE):
        abort(404, description="No hay trades aún.")
    return send_file(CSV_FILE, mimetype="text/csv", as_attachment=True, download_name="basket_trades.csv")


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BASKET — Divergencia Armónica</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #050810;
    --bg2: #0a0f1e;
    --bg3: #0f1729;
    --border: #1a2540;
    --accent: #00f5c4;
    --accent2: #7b61ff;
    --win: #00f5c4;
    --loss: #ff3b6b;
    --gold: #ffd166;
    --blue: #4488ff;
    --text: #e2e8f0;
    --muted: #4a5568;
    --dim: #2d3748;
    --font: 'Space Mono', monospace;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 13px;
    min-height: 100vh;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,245,196,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,245,196,0.025) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .wrap {
    position: relative;
    z-index: 1;
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
  }

  /* ── HEADER ── */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 20px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
    gap: 12px;
  }

  .logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 24px;
    letter-spacing: -1px;
    color: var(--accent);
    text-shadow: 0 0 24px rgba(0,245,196,0.35);
  }
  .logo span { color: var(--text); opacity: 0.4; font-weight: 400; }
  .subtitle { font-size: 10px; color: var(--muted); letter-spacing: 2px; text-transform: uppercase; margin-top: 3px; }

  .header-right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }

  #last-update { font-size: 10px; color: var(--muted); }

  #phase-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 14px;
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    border: 1px solid var(--accent);
    background: rgba(0,245,196,0.08);
    color: var(--accent);
    transition: all 0.3s;
  }
  #phase-badge.sleeping { border-color: var(--blue); background: rgba(68,136,255,0.08); color: var(--blue); }
  #phase-badge.error    { border-color: var(--loss); background: rgba(255,59,107,0.08); color: var(--loss); }

  .pulse-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: currentColor;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.4; transform:scale(0.8); }
  }

  .btn-csv {
    padding: 6px 16px;
    font-family: var(--font);
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    background: rgba(0,245,196,0.08);
    border: 1px solid rgba(0,245,196,0.35);
    color: var(--accent);
    text-decoration: none;
    cursor: pointer;
    transition: all 0.15s;
  }
  .btn-csv:hover { background: rgba(0,245,196,0.18); }

  /* ── KPI GRID ── */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
    margin-bottom: 16px;
  }

  .kpi {
    background: var(--bg2);
    border: 1px solid var(--border);
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
  }
  .kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
    opacity: 0.5;
  }
  .kpi.red::before  { background: var(--loss); }
  .kpi.gold::before { background: var(--gold); }
  .kpi.blue::before { background: var(--blue); }

  .kpi-label {
    font-size: 9px; color: var(--muted);
    letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 7px;
  }
  .kpi-value {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 22px;
    line-height: 1;
    color: var(--accent);
    transition: color 0.3s;
  }
  .kpi-value.red    { color: var(--loss); }
  .kpi-value.gold   { color: var(--gold); }
  .kpi-value.blue   { color: var(--blue); }
  .kpi-value.neutral{ color: var(--text); }

  /* ── MAIN GRID ── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 12px; }

  @media (max-width: 900px) {
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
  }

  /* ── PANEL ── */
  .panel {
    background: var(--bg2);
    border: 1px solid var(--border);
    overflow: hidden;
  }
  .panel-head {
    padding: 10px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .panel-body { padding: 14px 16px; }

  /* ── MARKETS ── */
  .market-row {
    display: grid;
    grid-template-columns: 52px 1fr 1fr 64px;
    gap: 8px;
    align-items: center;
    padding: 9px 0;
    border-bottom: 1px solid var(--border);
  }
  .market-row:last-child { border-bottom: none; }

  .sym-badge {
    font-weight: 700; font-size: 12px;
    background: rgba(68,136,255,0.12);
    border: 1px solid rgba(68,136,255,0.25);
    color: var(--blue);
    padding: 3px 8px;
    text-align: center;
  }
  .price-group { display: flex; flex-direction: column; gap: 2px; }
  .price-label { font-size: 9px; color: var(--muted); letter-spacing: 1px; }
  .price-value { font-size: 15px; font-weight: 700; transition: color 0.3s; }
  .price-value.up   { color: var(--win); }
  .price-value.down { color: var(--loss); }
  .time-left { font-size: 11px; color: var(--gold); text-align: right; }

  /* ── SIGNAL BOX ── */
  .signal-box {
    border: 1px solid var(--border);
    padding: 20px;
    text-align: center;
    transition: all 0.4s;
    background: var(--bg2);
  }
  .signal-box.UP   { border-color: var(--win);  background: rgba(0,245,196,0.06); }
  .signal-box.DOWN { border-color: var(--loss); background: rgba(255,59,107,0.06); }

  .sig-asset {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 32px;
    letter-spacing: -1px;
    transition: color 0.3s;
    color: var(--muted);
  }
  .sig-asset.UP   { color: var(--win); text-shadow: 0 0 20px rgba(0,245,196,0.4); }
  .sig-asset.DOWN { color: var(--loss); text-shadow: 0 0 20px rgba(255,59,107,0.4); }

  .sig-meta { margin-top: 10px; font-size: 11px; color: var(--muted); line-height: 1.9; }
  .sig-meta .hl { color: var(--text); }
  .sig-meta .gold { color: var(--gold); }

  /* ── POSITION BOX ── */
  .pos-box {
    border: 1px solid var(--gold);
    background: rgba(255,209,102,0.05);
    padding: 14px 16px;
  }
  .pos-head {
    font-size: 10px; letter-spacing: 2px; text-transform: uppercase;
    color: var(--gold); margin-bottom: 10px;
    display: flex; align-items: center; gap: 6px;
  }
  .pos-row {
    display: flex; justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px solid rgba(255,209,102,0.1);
    font-size: 12px;
  }
  .pos-row:last-child { border-bottom: none; }
  .pos-row .k { color: var(--muted); }

  /* ── HARMONY BARS ── */
  .harm-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
  .harm-label { font-size: 10px; color: var(--muted); width: 32px; }
  .harm-bg { flex: 1; background: var(--bg3); height: 8px; border-radius: 1px; overflow: hidden; }
  .harm-fill { height: 100%; transition: width 0.6s cubic-bezier(0.16,1,0.3,1); border-radius: 1px; }
  .harm-fill.up   { background: var(--win); }
  .harm-fill.down { background: var(--loss); }
  .harm-val { font-size: 12px; width: 52px; text-align: right; }

  /* ── CONSENSUS BADGE ── */
  .con-badge {
    display: inline-block;
    padding: 2px 10px; font-size: 10px; font-weight: 700; letter-spacing: 1px;
  }
  .con-badge.FULL { background: rgba(0,245,196,0.12); color: var(--win);  border: 1px solid rgba(0,245,196,0.3); }
  .con-badge.SOFT { background: rgba(255,209,102,0.12); color: var(--gold); border: 1px solid rgba(255,209,102,0.3); }
  .con-badge.NONE { background: rgba(255,255,255,0.04); color: var(--muted); border: 1px solid var(--border); }

  /* ── EVENTS LOG ── */
  #events-log {
    font-size: 11px; line-height: 1.8;
    max-height: 220px; overflow-y: auto;
    color: var(--muted);
  }
  #events-log::-webkit-scrollbar { width: 3px; }
  #events-log::-webkit-scrollbar-thumb { background: var(--dim); }
  .ev-win  { color: var(--win) !important; }
  .ev-loss { color: var(--loss) !important; }
  .ev-last { color: var(--text) !important; }

  /* ── TRADES TABLE ── */
  .trades-tbl { width: 100%; border-collapse: collapse; font-size: 11px; }
  .trades-tbl th {
    color: var(--muted); font-size: 9px; letter-spacing: 1.5px; text-transform: uppercase;
    padding: 6px 8px; border-bottom: 1px solid var(--border); text-align: left;
    font-weight: normal;
  }
  .trades-tbl td { padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.03); }
  .trades-tbl tr:hover td { background: rgba(255,255,255,0.02); }

  .badge { display: inline-block; padding: 1px 7px; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
  .badge-win  { background: rgba(0,245,196,0.12);  color: var(--win);  }
  .badge-loss { background: rgba(255,59,107,0.12); color: var(--loss); }
  .badge-up   { background: rgba(0,245,196,0.08);  color: var(--win);  }
  .badge-dn   { background: rgba(255,59,107,0.08); color: var(--loss); }
  .pnl-pos { color: var(--win);  font-weight: 700; }
  .pnl-neg { color: var(--loss); font-weight: 700; }

  /* ── SLEEPING ── */
  .sleeping-panel {
    text-align: center; padding: 32px 20px;
    color: var(--blue);
  }
  .sleeping-panel .zzz {
    font-family: 'Syne', sans-serif;
    font-size: 40px; font-weight: 800;
    opacity: 0.4;
    animation: breathe 3s ease-in-out infinite;
  }
  @keyframes breathe {
    0%,100% { opacity:0.3; } 50% { opacity:0.7; }
  }
  .sleeping-panel .wake { font-size: 11px; color: var(--muted); margin-top: 10px; }

  /* ── ENTRY WINDOW FLASH ── */
  .entry-active {
    animation: flash-border 0.8s ease-in-out infinite alternate;
  }
  @keyframes flash-border {
    from { border-color: var(--gold); box-shadow: 0 0 0 rgba(255,209,102,0); }
    to   { border-color: var(--gold); box-shadow: 0 0 12px rgba(255,209,102,0.25); }
  }
</style>
</head>
<body>
<div class="wrap">

  <!-- HEADER -->
  <header>
    <div>
      <div class="logo">BASKET <span>/ Divergencia Armónica</span></div>
      <div class="subtitle">ETH · SOL · BTC — Polymarket 5m · EN VIVO</div>
    </div>
    <div class="header-right">
      <span id="last-update">–</span>
      <a href="/download/csv" class="btn-csv">↓ CSV</a>
      <div id="phase-badge"><span class="pulse-dot"></span> –</div>
    </div>
  </header>

  <!-- KPIs -->
  <div class="kpi-grid">
    <div class="kpi">
      <div class="kpi-label">Capital</div>
      <div class="kpi-value neutral" id="k-capital">–</div>
    </div>
    <div class="kpi" id="kpi-pnl">
      <div class="kpi-label">PnL Total</div>
      <div class="kpi-value" id="k-pnl">–</div>
    </div>
    <div class="kpi" id="kpi-roi">
      <div class="kpi-label">ROI</div>
      <div class="kpi-value" id="k-roi">–</div>
    </div>
    <div class="kpi" id="kpi-wr">
      <div class="kpi-label">Win Rate</div>
      <div class="kpi-value" id="k-wr">–</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Trades W/L</div>
      <div class="kpi-value neutral" id="k-trades">–</div>
    </div>
    <div class="kpi red">
      <div class="kpi-label">Max Drawdown</div>
      <div class="kpi-value red" id="k-dd">–</div>
    </div>
    <div class="kpi blue">
      <div class="kpi-label">Ciclo</div>
      <div class="kpi-value blue" id="k-cycle">–</div>
    </div>
    <div class="kpi">
      <div class="kpi-label">Skipped</div>
      <div class="kpi-value neutral" id="k-skipped">–</div>
    </div>
  </div>

  <!-- ROW 1: Mercados + Señal/Posición -->
  <div class="grid-2">

    <!-- Mercados -->
    <div class="panel">
      <div class="panel-head">
        Mercados
        <span id="con-badge" class="con-badge NONE">NONE</span>
      </div>
      <div class="panel-body" id="markets-body">
        <div style="color:var(--muted); font-size:11px;">Cargando...</div>
      </div>
    </div>

    <!-- Señal + Armónicos + Posición -->
    <div style="display:flex; flex-direction:column; gap:10px;">

      <!-- Armónicos -->
      <div class="panel">
        <div class="panel-head">Promedios Armónicos</div>
        <div class="panel-body">
          <div class="harm-row">
            <div class="harm-label">UP</div>
            <div class="harm-bg"><div class="harm-fill up" id="h-up-bar" style="width:50%"></div></div>
            <div class="harm-val" id="h-up-val">–</div>
          </div>
          <div class="harm-row">
            <div class="harm-label">DOWN</div>
            <div class="harm-bg"><div class="harm-fill down" id="h-dn-bar" style="width:50%"></div></div>
            <div class="harm-val" id="h-dn-val">–</div>
          </div>
        </div>
      </div>

      <!-- Señal -->
      <div id="signal-box" class="signal-box">
        <div class="sig-asset" id="sig-asset">–</div>
        <div class="sig-meta" id="sig-meta">Sin señal activa</div>
      </div>

      <!-- Posición abierta -->
      <div id="pos-panel" style="display:none" class="pos-box">
        <div class="pos-head"><span class="pulse-dot" style="color:var(--gold)"></span> POSICIÓN ABIERTA</div>
        <div id="pos-body"></div>
      </div>

    </div>
  </div>

  <!-- ROW 2: Eventos + Trades -->
  <div class="grid-2">
    <div class="panel">
      <div class="panel-head">Log de Eventos</div>
      <div class="panel-body">
        <div id="events-log">Esperando eventos...</div>
      </div>
    </div>
    <div class="panel">
      <div class="panel-head">Últimos Trades</div>
      <div class="panel-body" style="padding:0">
        <table class="trades-tbl">
          <thead>
            <tr>
              <th>ID</th><th>Asset</th><th>Lado</th><th>Ask</th>
              <th>Gap</th><th>PnL</th><th>Resultado</th>
            </tr>
          </thead>
          <tbody id="trades-body">
            <tr><td colspan="7" style="color:var(--muted); padding:14px 8px; text-align:center;">Sin trades aún</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

</div><!-- /wrap -->

<script>
const POLL_MS = 1500;
const fmt = (v, d=2) => v != null ? Number(v).toFixed(d) : '–';

// ── KPIs ──
function updateKPIs(s) {
  document.getElementById('k-capital').textContent = '$' + fmt(s.capital, 4);

  const pnl = s.total_pnl || 0;
  const pnlEl = document.getElementById('k-pnl');
  pnlEl.textContent = (pnl >= 0 ? '+' : '') + '$' + fmt(pnl, 4);
  pnlEl.className = 'kpi-value ' + (pnl >= 0 ? '' : 'red');
  document.getElementById('kpi-pnl').className = 'kpi' + (pnl >= 0 ? '' : ' red');

  const roi = s.roi || 0;
  const roiEl = document.getElementById('k-roi');
  roiEl.textContent = (roi >= 0 ? '+' : '') + fmt(roi, 2) + '%';
  roiEl.className = 'kpi-value ' + (roi >= 0 ? '' : 'red');
  document.getElementById('kpi-roi').className = 'kpi' + (roi >= 0 ? '' : ' red');

  const wr = s.win_rate || 0;
  const wrEl = document.getElementById('k-wr');
  wrEl.textContent = fmt(wr, 1) + '%';
  wrEl.className = 'kpi-value ' + (wr >= 75 ? '' : wr >= 60 ? 'gold' : 'red');
  document.getElementById('kpi-wr').className = 'kpi' + (wr >= 75 ? '' : wr >= 60 ? ' gold' : ' red');

  document.getElementById('k-trades').textContent  = `${s.wins || 0}W / ${s.losses || 0}L`;
  document.getElementById('k-dd').textContent      = '-$' + fmt(s.max_drawdown, 4);
  document.getElementById('k-cycle').textContent   = s.cycle || '–';
  document.getElementById('k-skipped').textContent = s.skipped || '0';
}

// ── PHASE ──
function updatePhase(s) {
  const b = document.getElementById('phase-badge');
  const phase = (s.phase || '').toUpperCase();
  b.innerHTML = `<span class="pulse-dot"></span> ${phase}`;
  b.className = '';
  if (phase === 'DURMIENDO') b.classList.add('sleeping');
  else if (s.error) b.classList.add('error');
}

// ── MARKETS ──
function updateMarkets(s) {
  const body = document.getElementById('markets-body');
  if (!s.markets) { body.innerHTML = '<div style="color:var(--loss);font-size:11px">Sin datos</div>'; return; }
  let html = '';
  ['ETH','SOL','BTC'].forEach(sym => {
    const m = s.markets[sym];
    if (!m) return;
    const isSig = sym === s.signal_asset;
    const upArrow = isSig && s.signal_side === 'UP'   ? ' ◀' : '';
    const dnArrow = isSig && s.signal_side === 'DOWN'  ? ' ◀' : '';
    if (m.up_mid > 0) {
      const upD = m.up_mid >= 0.98 ? '1.000' : m.up_mid <= 0.02 ? '0.000' : fmt(m.up_mid, 4);
      const dnD = m.dn_mid >= 0.98 ? '1.000' : m.dn_mid <= 0.02 ? '0.000' : fmt(m.dn_mid, 4);
      html += `<div class="market-row">
        <div class="sym-badge">${sym}</div>
        <div class="price-group">
          <div class="price-label">UP${upArrow}</div>
          <div class="price-value up">${upD}</div>
        </div>
        <div class="price-group">
          <div class="price-label">DOWN${dnArrow}</div>
          <div class="price-value down">${dnD}</div>
        </div>
        <div class="time-left">${m.time_left || 'N/A'}</div>
      </div>`;
    } else {
      html += `<div class="market-row">
        <div class="sym-badge">${sym}</div>
        <div style="grid-column:2/5; font-size:11px; color:var(--loss)">${m.error || 'sin datos'}</div>
      </div>`;
    }
  });
  body.innerHTML = html || '<div style="color:var(--muted);font-size:11px">Sin datos</div>';

  const cb = document.getElementById('con-badge');
  const con = s.consensus || 'NONE';
  cb.textContent = con;
  cb.className = 'con-badge ' + con;
}

// ── HARMONIC ──
function updateHarmonic(s) {
  const up = s.harm_up || 0.5;
  const dn = s.harm_dn || 0.5;
  document.getElementById('h-up-bar').style.width = (up * 100) + '%';
  document.getElementById('h-dn-bar').style.width = (dn * 100) + '%';
  document.getElementById('h-up-val').textContent = fmt(up, 4);
  document.getElementById('h-dn-val').textContent = fmt(dn, 4);
}

// ── SIGNAL ──
function updateSignal(s) {
  const box  = document.getElementById('signal-box');
  const asset = document.getElementById('sig-asset');
  const meta  = document.getElementById('sig-meta');
  const phase = (s.phase || '').toUpperCase();

  if (phase === 'DURMIENDO') {
    box.className = 'signal-box';
    box.innerHTML = `
      <div class="sleeping-panel">
        <div class="zzz">ZZZ</div>
        <div class="wake">${s.next_wake || 'Esperando próximo ciclo...'}</div>
      </div>`;
    return;
  }

  const div = Math.abs(s.signal_div || 0);
  if (!s.signal_asset || div < 0.04) {
    box.className = 'signal-box';
    asset.className = 'sig-asset';
    asset.textContent = '–';
    meta.innerHTML = 'Sin divergencia detectada';
    return;
  }

  const side = s.signal_side || '';
  box.className = 'signal-box ' + side + (s.entry_window ? ' entry-active' : '');
  asset.className = 'sig-asset ' + side;
  asset.textContent = `${s.signal_asset} ${side === 'UP' ? '▲' : '▼'}`;

  const divPts = (div * 100).toFixed(1);
  const ewHtml = s.entry_window
    ? '<span class="gold">⚡ VENTANA ACTIVA — PUEDE ENTRAR</span>'
    : '<span>Fuera de ventana de entrada</span>';
  meta.innerHTML = `
    Div: <span class="hl">${divPts} pts</span> vs armónico<br>
    Consenso: <span class="hl">${s.consensus || '–'}</span><br>
    ${ewHtml}
  `;
}

// ── POSITION ──
function updatePosition(s) {
  const panel = document.getElementById('pos-panel');
  const body  = document.getElementById('pos-body');
  const pos = s.position;
  if (!pos) { panel.style.display = 'none'; return; }
  panel.style.display = 'block';
  body.innerHTML = `
    <div class="pos-row"><span class="k">Asset / Lado</span><span>${pos.asset} ${pos.side}</span></div>
    <div class="pos-row"><span class="k">Entry Ask</span><span>${fmt(pos.entry_price, 4)}</span></div>
    <div class="pos-row"><span class="k">Shares</span><span>${fmt(pos.shares, 4)}</span></div>
    <div class="pos-row"><span class="k">Invertido</span><span>$${fmt(pos.entry_usd, 2)}</span></div>
    <div class="pos-row"><span class="k">Consenso entrada</span><span>${pos.consensus_entry}</span></div>
    <div class="pos-row"><span class="k">Secs en entrada</span><span>${fmt(pos.secs_left_entry, 0)}s</span></div>
    <div class="pos-row"><span class="k">Gap entrada</span><span>${((pos.gap_entry||0)*100).toFixed(1)} pts</span></div>
  `;
}

// ── EVENTS ──
function updateEvents(s) {
  const el = document.getElementById('events-log');
  const evs = (s.events || []).slice().reverse();
  if (!evs.length) { el.innerHTML = 'Sin eventos aún'; return; }
  el.innerHTML = evs.map((e, i) => {
    let cls = '';
    if (e.includes('WIN') || e.includes('ENTRADA')) cls = 'ev-win';
    else if (e.includes('LOSS') || e.includes('Error') || e.includes('WARN') || e.includes('STOP')) cls = 'ev-loss';
    else if (i === 0) cls = 'ev-last';
    return `<div class="${cls}">${e}</div>`;
  }).join('');
}

// ── TRADES ──
function updateTrades(s) {
  const tbody = document.getElementById('trades-body');
  const trades = (s.recent_trades || []).slice().reverse();
  if (!trades.length) {
    tbody.innerHTML = '<tr><td colspan="7" style="color:var(--muted);padding:14px 8px;text-align:center">Sin trades aún</td></tr>';
    return;
  }
  tbody.innerHTML = trades.map(t => {
    const pnl = parseFloat(t.pnl_usd || 0);
    const pnlStr = (pnl >= 0 ? '+' : '') + '$' + pnl.toFixed(4);
    const gap = parseFloat(t.gap_pts || 0);
    return `<tr>
      <td style="color:var(--muted)">${t.trade_id}</td>
      <td>${t.asset}</td>
      <td><span class="badge badge-${(t.side||'').toLowerCase()}">${t.side}</span></td>
      <td>${fmt(t.entry_ask, 4)}</td>
      <td style="color:var(--muted)">${gap.toFixed(1)}pts</td>
      <td class="${pnl >= 0 ? 'pnl-pos' : 'pnl-neg'}">${pnlStr}</td>
      <td><span class="badge badge-${(t.outcome||'').toLowerCase()}">${t.outcome}</span></td>
    </tr>`;
  }).join('');
}

// ── POLL ──
async function poll() {
  try {
    const r = await fetch('/api/state');
    const s = await r.json();

    if (s.error) {
      document.getElementById('phase-badge').innerHTML = '<span class="pulse-dot"></span> SIN DATOS';
      document.getElementById('phase-badge').className = 'error';
      document.getElementById('markets-body').innerHTML = `<div style="color:var(--loss);font-size:11px">${s.error}</div>`;
      return;
    }

    updatePhase(s);
    updateKPIs(s);
    updateMarkets(s);
    updateHarmonic(s);
    updateSignal(s);
    updatePosition(s);
    updateEvents(s);
    updateTrades(s);

    document.getElementById('last-update').textContent =
      'Actualizado: ' + new Date().toLocaleTimeString('es-CL');

  } catch(e) {
    document.getElementById('last-update').textContent = 'Error de conexión';
  }
}

poll();
setInterval(poll, POLL_MS);
</script>
</body>
</html>"""


@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
