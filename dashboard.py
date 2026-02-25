"""
dashboard.py — Flask server para Polymarket Basket Bot.
Rutas:
  GET /          → Dashboard HTML en vivo
  GET /api/state → JSON con estado actual
  GET /download/csv → Descarga CSV de trades
"""

import json, os
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

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BASKET // LIVE</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Barlow:wght@300;400;600;700;900&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:     #080808;
  --bg2:    #0e0e0e;
  --bg3:    #141414;
  --line:   #1f1f1f;
  --line2:  #2a2a2a;
  --white:  #f0f0f0;
  --dim:    #555;
  --dimmer: #333;
  --green:  #e8ff47;
  --red:    #ff2d55;
  --blue:   #00d4ff;
  --mono:   'DM Mono', monospace;
  --sans:   'Barlow', sans-serif;
}

html { font-size: 13px; }

body {
  background: var(--bg);
  color: var(--white);
  font-family: var(--mono);
  min-height: 100vh;
  overflow-x: hidden;
}

body::after {
  content: '';
  position: fixed; inset: 0;
  background: repeating-linear-gradient(
    0deg, transparent, transparent 2px,
    rgba(0,0,0,0.07) 2px, rgba(0,0,0,0.07) 4px
  );
  pointer-events: none;
  z-index: 9999;
}

.container { max-width: 1440px; margin: 0 auto; padding: 0 24px 40px; }

/* HEADER */
header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 0; border-bottom: 1px solid var(--line2);
  margin-bottom: 24px; gap: 16px; flex-wrap: wrap;
}
.logo { font-family: var(--sans); font-weight: 900; font-size: 20px; letter-spacing: 6px; text-transform: uppercase; color: var(--white); }
.logo em { color: var(--green); font-style: normal; }
.logo-sub { font-size: 9px; letter-spacing: 4px; color: var(--dim); text-transform: uppercase; margin-top: 3px; }

.header-right { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
#ts { font-size: 10px; color: var(--dim); letter-spacing: 1px; }

#phase-badge {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 5px 16px; border: 1px solid var(--line2);
  font-size: 10px; letter-spacing: 3px; text-transform: uppercase; color: var(--dim);
  transition: all 0.3s;
}
#phase-badge.active  { border-color: var(--green); color: var(--green); }
#phase-badge.sleeping{ border-color: var(--blue);  color: var(--blue); }
#phase-badge.error   { border-color: var(--red);   color: var(--red); }

.dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; animation: blink 1.4s infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }

.btn {
  font-family: var(--mono); font-size: 10px; letter-spacing: 3px; text-transform: uppercase;
  padding: 6px 18px; border: 1px solid var(--line2); background: transparent;
  color: var(--dim); cursor: pointer; text-decoration: none; transition: all 0.15s;
}
.btn:hover { border-color: var(--white); color: var(--white); }

/* KPI ROW */
.kpi-row {
  display: grid; grid-template-columns: repeat(8, 1fr);
  gap: 1px; background: var(--line); border: 1px solid var(--line2); margin-bottom: 24px;
}
@media (max-width: 1100px) { .kpi-row { grid-template-columns: repeat(4,1fr); } }
@media (max-width: 600px)  { .kpi-row { grid-template-columns: repeat(2,1fr); } }

.kpi { background: var(--bg2); padding: 18px 16px 14px; position: relative; overflow: hidden; }
.kpi::after {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: var(--line2); transition: background 0.3s;
}
.kpi.up::after   { background: var(--green); }
.kpi.down::after { background: var(--red); }
.kpi.info::after { background: var(--blue); }

.kpi-label {
  font-size: 8px; letter-spacing: 2.5px; text-transform: uppercase;
  color: var(--dim); margin-bottom: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.kpi-val {
  font-family: var(--sans); font-weight: 700; font-size: 20px; line-height: 1;
  color: var(--white); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.kpi-val.green { color: var(--green); }
.kpi-val.red   { color: var(--red); }
.kpi-val.blue  { color: var(--blue); }
.kpi-val.dim   { color: var(--dim); }

/* MAIN GRID */
.main-grid {
  display: grid; grid-template-columns: 1fr 1fr 320px;
  gap: 1px; background: var(--line); border: 1px solid var(--line2); margin-bottom: 24px;
}
@media (max-width: 1000px) { .main-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px)  { .main-grid { grid-template-columns: 1fr; } }

/* CHARTS ROW */
.charts-row {
  display: grid; grid-template-columns: 2fr 1fr;
  gap: 1px; background: var(--line); border: 1px solid var(--line2); margin-bottom: 24px;
}
@media (max-width: 640px) { .charts-row { grid-template-columns: 1fr; } }

/* PANEL */
.panel { background: var(--bg2); display: flex; flex-direction: column; }
.panel-head {
  padding: 11px 16px; border-bottom: 1px solid var(--line);
  font-size: 8px; letter-spacing: 3px; text-transform: uppercase; color: var(--dim);
  display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;
}
.panel-body { padding: 16px; flex: 1; }

canvas { display: block; width: 100% !important; }

/* MARKETS */
.mkt-row {
  display: grid; grid-template-columns: 48px 1fr 1fr 56px;
  gap: 10px; align-items: center; padding: 11px 0; border-bottom: 1px solid var(--line);
}
.mkt-row:last-child { border-bottom: none; }
.sym {
  font-family: var(--sans); font-weight: 700; font-size: 11px; letter-spacing: 2px;
  color: var(--dim); border: 1px solid var(--line2); padding: 4px 0; text-align: center;
}
.sym.active { color: var(--green); border-color: var(--green); }
.px-group { display: flex; flex-direction: column; gap: 2px; }
.px-lbl { font-size: 8px; letter-spacing: 2px; color: var(--dimmer); }
.px-val { font-family: var(--sans); font-weight: 600; font-size: 16px; }
.px-val.g { color: var(--green); }
.px-val.r { color: var(--red); }
.tleft { font-size: 11px; color: var(--blue); text-align: right; font-weight: 500; }

/* SIGNAL */
.signal-wrap {
  border: 1px solid var(--line2); padding: 20px; text-align: center;
  transition: border-color 0.4s, background 0.4s;
}
.signal-wrap.UP   { border-color: var(--green); background: rgba(232,255,71,0.03); }
.signal-wrap.DOWN { border-color: var(--red);   background: rgba(255,45,85,0.03); }
.signal-wrap.WINDOW { animation: pulse-brd 0.9s ease-in-out infinite alternate; }
@keyframes pulse-brd { from{box-shadow:0 0 0 rgba(232,255,71,0)} to{box-shadow:0 0 16px rgba(232,255,71,0.2)} }

.sig-main {
  font-family: var(--sans); font-weight: 900; font-size: 36px;
  letter-spacing: 2px; color: var(--dimmer); transition: color 0.3s;
}
.sig-main.UP   { color: var(--green); }
.sig-main.DOWN { color: var(--red); }
.sig-info { margin-top: 12px; font-size: 10px; color: var(--dim); line-height: 2; letter-spacing: 1px; }
.sig-info .hl { color: var(--white); }
.sig-info .gl { color: var(--green); }
.sig-info .bl { color: var(--blue); }

/* POSITION */
.pos-wrap { border: 1px solid var(--green); padding: 14px 16px; background: rgba(232,255,71,0.025); margin-top: 12px; }
.pos-lbl { font-size: 8px; letter-spacing: 3px; text-transform: uppercase; color: var(--green); margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.pos-line { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid var(--line); font-size: 11px; }
.pos-line:last-child { border-bottom: none; }
.pos-line .k { color: var(--dim); }

/* HARMONY */
.harm-row { display: flex; align-items: center; gap: 10px; padding: 7px 0; }
.harm-lbl { font-size: 9px; letter-spacing: 2px; color: var(--dim); width: 32px; }
.harm-track { flex: 1; height: 4px; background: var(--bg3); }
.harm-fill { height: 100%; transition: width 0.7s cubic-bezier(.16,1,.3,1); }
.harm-fill.g { background: var(--green); }
.harm-fill.r { background: var(--red); }
.harm-num { font-size: 11px; width: 52px; text-align: right; }

/* CONSENSUS */
.con-tag { padding: 2px 10px; font-size: 9px; letter-spacing: 2px; text-transform: uppercase; border: 1px solid var(--line2); color: var(--dim); }
.con-tag.FULL { border-color: var(--green); color: var(--green); }
.con-tag.SOFT { border-color: var(--blue);  color: var(--blue); }

/* EVENTS */
#events-log { font-size: 10px; line-height: 1.9; letter-spacing: 0.5px; max-height: 200px; overflow-y: auto; color: var(--dim); }
#events-log::-webkit-scrollbar { width: 2px; }
#events-log::-webkit-scrollbar-thumb { background: var(--line2); }
.ev-g { color: var(--green) !important; }
.ev-r { color: var(--red)   !important; }
.ev-w { color: var(--white) !important; }

/* TRADES */
.t-wrap { overflow-x: auto; max-height: 360px; overflow-y: auto; }
.t-wrap::-webkit-scrollbar { width: 2px; height: 2px; }
.t-wrap::-webkit-scrollbar-thumb { background: var(--line2); }
table { width: 100%; border-collapse: collapse; font-size: 10px; }
thead th {
  background: var(--bg3); color: var(--dim); font-weight: 400;
  font-size: 8px; letter-spacing: 2px; text-transform: uppercase;
  padding: 9px 10px; text-align: left; border-bottom: 1px solid var(--line2);
  position: sticky; top: 0; z-index: 2; white-space: nowrap;
}
tbody td { padding: 7px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }
tbody tr:hover td { background: rgba(255,255,255,0.02); }
tbody tr.r-win  { border-left: 1px solid rgba(232,255,71,0.4); }
tbody tr.r-loss { border-left: 1px solid rgba(255,45,85,0.4); }

.tag { display: inline-block; padding: 1px 7px; font-size: 8px; letter-spacing: 1px; text-transform: uppercase; font-weight: 600; }
.tag-win  { color: var(--green); border: 1px solid rgba(232,255,71,0.25); }
.tag-loss { color: var(--red);   border: 1px solid rgba(255,45,85,0.25); }
.tag-up   { color: var(--green); }
.tag-dn   { color: var(--red); }
.g { color: var(--green); font-weight: 600; }
.r { color: var(--red);   font-weight: 600; }
.d { color: var(--dim); }

/* ZZZ */
.zzz { text-align: center; padding: 30px 20px; }
.zzz-txt { font-family: var(--sans); font-weight: 900; font-size: 36px; letter-spacing: 8px; color: var(--line2); animation: breathe 3s ease-in-out infinite; }
@keyframes breathe { 0%,100%{opacity:.2} 50%{opacity:.6} }
.zzz-sub { font-size: 9px; letter-spacing: 3px; color: var(--dimmer); margin-top: 10px; }
</style>
</head>
<body>
<div class="container">

<header>
  <div>
    <div class="logo">BASKET // <em>LIVE</em></div>
    <div class="logo-sub">ETH · SOL · BTC &mdash; Polymarket 5m Binary</div>
  </div>
  <div class="header-right">
    <span id="ts">––:––:––</span>
    <a href="/download/csv" class="btn">↓ CSV</a>
    <div id="phase-badge"><span class="dot"></span> ––</div>
  </div>
</header>

<!-- KPIs -->
<div class="kpi-row">
  <div class="kpi" id="kpi-cap">
    <div class="kpi-label">Capital</div>
    <div class="kpi-val" id="v-cap">–</div>
  </div>
  <div class="kpi" id="kpi-pnl">
    <div class="kpi-label">PnL Total</div>
    <div class="kpi-val" id="v-pnl">–</div>
  </div>
  <div class="kpi" id="kpi-roi">
    <div class="kpi-label">ROI</div>
    <div class="kpi-val" id="v-roi">–</div>
  </div>
  <div class="kpi" id="kpi-wr">
    <div class="kpi-label">Win Rate</div>
    <div class="kpi-val" id="v-wr">–</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">W / L</div>
    <div class="kpi-val dim" id="v-wl">–</div>
  </div>
  <div class="kpi down">
    <div class="kpi-label">Max DD</div>
    <div class="kpi-val red" id="v-dd">–</div>
  </div>
  <div class="kpi info">
    <div class="kpi-label">Ciclo</div>
    <div class="kpi-val blue" id="v-cycle">–</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Skipped</div>
    <div class="kpi-val dim" id="v-skip">–</div>
  </div>
</div>

<!-- MAIN ROW -->
<div class="main-grid">

  <div class="panel">
    <div class="panel-head">Mercados <span id="con-tag" class="con-tag">––</span></div>
    <div class="panel-body" id="mkt-body"><div class="d" style="font-size:10px">Cargando...</div></div>
  </div>

  <div class="panel">
    <div class="panel-head">Señal de Divergencia</div>
    <div class="panel-body" style="display:flex;flex-direction:column;gap:12px">
      <div>
        <div style="font-size:8px;letter-spacing:3px;color:var(--dim);margin-bottom:8px">ARMÓNICOS</div>
        <div class="harm-row">
          <div class="harm-lbl">UP</div>
          <div class="harm-track"><div class="harm-fill g" id="h-up" style="width:50%"></div></div>
          <div class="harm-num" id="h-up-v">–</div>
        </div>
        <div class="harm-row">
          <div class="harm-lbl">DOWN</div>
          <div class="harm-track"><div class="harm-fill r" id="h-dn" style="width:50%"></div></div>
          <div class="harm-num" id="h-dn-v">–</div>
        </div>
      </div>
      <div id="sig-box" class="signal-wrap">
        <div class="sig-main" id="sig-main">––</div>
        <div class="sig-info" id="sig-info">Sin divergencia detectada</div>
      </div>
      <div id="pos-wrap" style="display:none" class="pos-wrap">
        <div class="pos-lbl"><span class="dot"></span> Posición Abierta</div>
        <div id="pos-body"></div>
      </div>
    </div>
  </div>

  <div class="panel">
    <div class="panel-head">Log de Eventos</div>
    <div class="panel-body"><div id="events-log">Esperando...</div></div>
  </div>

</div>

<!-- CHARTS -->
<div class="charts-row">
  <div class="panel">
    <div class="panel-head">Curva de Capital <span id="eq-lbl" style="font-family:'Barlow',sans-serif;font-weight:700;font-size:11px"></span></div>
    <div class="panel-body" style="padding:12px 16px"><canvas id="eq-chart" height="140"></canvas></div>
  </div>
  <div class="panel">
    <div class="panel-head">Win / Loss <span id="wr-lbl" style="color:var(--white);font-size:10px"></span></div>
    <div class="panel-body" style="display:flex;align-items:center;justify-content:center;padding:12px">
      <canvas id="donut-chart" height="180" style="max-width:180px"></canvas>
    </div>
  </div>
</div>

<!-- TRADES -->
<div class="panel" style="border:1px solid var(--line2)">
  <div class="panel-head">Todos los Trades del Día <span id="t-count" style="color:var(--white);font-size:10px;letter-spacing:1px"></span></div>
  <div class="panel-body" style="padding:0">
    <div class="t-wrap">
      <table>
        <thead><tr>
          <th>ID</th><th>Hora</th><th>Asset</th><th>Lado</th>
          <th>Ask</th><th>Gap</th><th>Secs</th>
          <th>PnL</th><th>Resultado</th><th>Salida</th>
        </tr></thead>
        <tbody id="t-body">
          <tr><td colspan="10" style="color:var(--dim);padding:18px 10px;text-align:center;font-size:10px">Sin trades aún</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
const f = (v, d=2) => v != null ? Number(v).toFixed(d) : '–';
Chart.defaults.color = '#555';
Chart.defaults.borderColor = '#1f1f1f';
Chart.defaults.font.family = "'DM Mono', monospace";

let eqChart = null, donutChart = null;

function initEquity() {
  const ctx = document.getElementById('eq-chart').getContext('2d');
  eqChart = new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ data: [], borderColor: '#e8ff47', borderWidth: 1.5, pointRadius: 0, tension: 0.3, fill: true,
      backgroundColor: ctx => {
        const g = ctx.chart.ctx.createLinearGradient(0,0,0,160);
        g.addColorStop(0,'rgba(232,255,71,0.12)'); g.addColorStop(1,'rgba(232,255,71,0.01)'); return g;
      }
    }]},
    options: {
      responsive: true, animation: false,
      plugins: { legend:{display:false}, tooltip:{
        backgroundColor:'#0e0e0e', borderColor:'#2a2a2a', borderWidth:1, bodyColor:'#f0f0f0',
        callbacks:{ label: c => '$'+c.parsed.y.toFixed(4) }
      }},
      scales: {
        x: { display: false },
        y: { grid:{color:'#1f1f1f'}, border:{color:'#1f1f1f'},
          ticks:{ color:'#555', font:{size:9}, callback: v => '$'+v.toFixed(2) }
        }
      }
    }
  });
}

function initDonut() {
  const ctx = document.getElementById('donut-chart').getContext('2d');
  donutChart = new Chart(ctx, {
    type: 'doughnut',
    data: { labels: ['WIN','LOSS'], datasets: [{
      data: [1,1],
      backgroundColor: ['rgba(232,255,71,0.85)','rgba(255,45,85,0.85)'],
      borderColor: ['rgba(232,255,71,0.15)','rgba(255,45,85,0.15)'],
      borderWidth: 1, hoverOffset: 4
    }]},
    options: {
      responsive: true, cutout: '72%', animation:{ duration:600 },
      plugins: {
        legend:{ position:'bottom', labels:{ color:'#555', font:{size:9}, padding:14, boxWidth:8 } },
        tooltip:{ backgroundColor:'#0e0e0e', borderColor:'#2a2a2a', borderWidth:1, bodyColor:'#f0f0f0' }
      }
    },
    plugins: [{
      id:'center',
      afterDraw(chart) {
        const {ctx, chartArea:{width,height,top}} = chart;
        const cx = width/2, cy = top+height/2;
        ctx.save();
        ctx.textAlign='center'; ctx.textBaseline='middle';
        ctx.font = "700 22px 'Barlow',sans-serif";
        ctx.fillStyle = '#f0f0f0';
        ctx.fillText((chart._wr||'–')+'%', cx, cy-6);
        ctx.font = "9px 'DM Mono',monospace";
        ctx.fillStyle = '#555';
        ctx.fillText('WIN RATE', cx, cy+14);
        ctx.restore();
      }
    }]
  });
}

function updateEquity(trades) {
  if (!eqChart) return;
  let cap = 100;
  const labels = ['0'], data = [100];
  trades.forEach(t => {
    cap += parseFloat(t.pnl_usd||0);
    labels.push(t.trade_id);
    data.push(parseFloat(cap.toFixed(4)));
  });
  eqChart.data.labels = labels;
  eqChart.data.datasets[0].data = data;
  eqChart.update('none');
  const last = data[data.length-1];
  const diff = last - 100;
  const el = document.getElementById('eq-lbl');
  el.textContent = `$${last.toFixed(4)}  (${diff>=0?'+':''}${diff.toFixed(4)})`;
  el.style.color = diff >= 0 ? 'var(--green)' : 'var(--red)';
}

function updateDonut(wins, losses) {
  if (!donutChart) return;
  wins = wins||0; losses = losses||0;
  donutChart.data.datasets[0].data = [wins, losses];
  const tot = wins+losses;
  donutChart._wr = tot > 0 ? ((wins/tot)*100).toFixed(1) : '–';
  document.getElementById('wr-lbl').textContent = `${wins}W · ${losses}L`;
  donutChart.update();
}

function updateKPIs(s) {
  document.getElementById('v-cap').textContent = '$'+f(s.capital,4);

  const pnl = s.total_pnl||0;
  const pe = document.getElementById('v-pnl');
  pe.textContent = (pnl>=0?'+':'')+'$'+f(pnl,4);
  pe.className = 'kpi-val '+(pnl>=0?'green':'red');
  document.getElementById('kpi-pnl').className = 'kpi '+(pnl>=0?'up':'down');

  const roi = s.roi||0;
  const re = document.getElementById('v-roi');
  re.textContent = (roi>=0?'+':'')+f(roi,2)+'%';
  re.className = 'kpi-val '+(roi>=0?'green':'red');
  document.getElementById('kpi-roi').className = 'kpi '+(roi>=0?'up':'down');

  const wr = s.win_rate||0;
  const we = document.getElementById('v-wr');
  we.textContent = f(wr,1)+'%';
  we.className = 'kpi-val '+(wr>=65?'green':wr>=50?'blue':'red');
  document.getElementById('kpi-wr').className = 'kpi '+(wr>=65?'up':wr>=50?'info':'down');

  document.getElementById('v-wl').textContent    = `${s.wins||0} / ${s.losses||0}`;
  document.getElementById('v-dd').textContent    = '-$'+f(s.max_drawdown,4);
  document.getElementById('v-cycle').textContent = s.cycle||'–';
  document.getElementById('v-skip').textContent  = s.skipped||'0';
}

function updatePhase(s) {
  const b = document.getElementById('phase-badge');
  const p = (s.phase||'').toUpperCase();
  b.innerHTML = `<span class="dot"></span> ${p}`;
  b.className = s.error ? 'error' : p==='DURMIENDO' ? 'sleeping' : 'active';
}

function updateMarkets(s) {
  const body = document.getElementById('mkt-body');
  if (!s.markets) { body.innerHTML='<div class="d" style="font-size:10px">Sin datos</div>'; return; }
  let html = '';
  ['ETH','SOL','BTC'].forEach(sym => {
    const m = s.markets[sym]; if (!m) return;
    const isSig = sym===s.signal_asset;
    if (m.up_mid > 0) {
      const upD = m.up_mid>=0.98?'1.0000':m.up_mid<=0.02?'0.0000':f(m.up_mid,4);
      const dnD = m.dn_mid>=0.98?'1.0000':m.dn_mid<=0.02?'0.0000':f(m.dn_mid,4);
      html += `<div class="mkt-row">
        <div class="sym${isSig?' active':''}">${sym}</div>
        <div class="px-group"><div class="px-lbl">UP</div><div class="px-val g">${upD}</div></div>
        <div class="px-group"><div class="px-lbl">DOWN</div><div class="px-val r">${dnD}</div></div>
        <div class="tleft">${m.time_left||'–'}</div>
      </div>`;
    } else {
      html += `<div class="mkt-row">
        <div class="sym">${sym}</div>
        <div style="grid-column:2/5;font-size:10px;color:var(--red)">${m.error||'sin datos'}</div>
      </div>`;
    }
  });
  body.innerHTML = html||'<div class="d">Sin datos</div>';
  const ct = document.getElementById('con-tag');
  const con = s.consensus||'NONE';
  ct.textContent = con; ct.className = 'con-tag '+con;
}

function updateHarmonic(s) {
  const up=s.harm_up||0.5, dn=s.harm_dn||0.5;
  document.getElementById('h-up').style.width=(up*100)+'%';
  document.getElementById('h-dn').style.width=(dn*100)+'%';
  document.getElementById('h-up-v').textContent=f(up,4);
  document.getElementById('h-dn-v').textContent=f(dn,4);
}

function updateSignal(s) {
  const box  = document.getElementById('sig-box');
  const main = document.getElementById('sig-main');
  const info = document.getElementById('sig-info');
  const phase = (s.phase||'').toUpperCase();

  if (phase==='DURMIENDO') {
    box.className='signal-wrap';
    box.innerHTML=`<div class="zzz"><div class="zzz-txt">ZZZ</div><div class="zzz-sub">${s.next_wake||'próximo ciclo'}</div></div>`;
    return;
  }
  // rebuild if was zzz
  if (!document.getElementById('sig-main')) {
    box.innerHTML=`<div class="sig-main" id="sig-main">––</div><div class="sig-info" id="sig-info">Sin señal</div>`;
  }

  const div=Math.abs(s.signal_div||0);
  if (!s.signal_asset||div<0.04) {
    box.className='signal-wrap';
    document.getElementById('sig-main').className='sig-main';
    document.getElementById('sig-main').textContent='––';
    document.getElementById('sig-info').innerHTML='Sin divergencia detectada';
    return;
  }
  const side=s.signal_side||'', ew=s.entry_window;
  box.className='signal-wrap '+side+(ew?' WINDOW':'');
  document.getElementById('sig-main').className='sig-main '+side;
  document.getElementById('sig-main').textContent=`${s.signal_asset} ${side==='UP'?'▲':'▼'}`;
  document.getElementById('sig-info').innerHTML=`
    DIV <span class="hl">${(div*100).toFixed(1)} pts</span> &nbsp;·&nbsp;
    <span class="bl">${s.consensus||'–'}</span><br>
    ${ew?'<span class="gl">⚡ VENTANA ACTIVA</span>':'<span>fuera de ventana</span>'}
  `;
}

function updatePosition(s) {
  const w=document.getElementById('pos-wrap'), b=document.getElementById('pos-body');
  if (!s.position) { w.style.display='none'; return; }
  w.style.display='block';
  const p=s.position;
  b.innerHTML=`
    <div class="pos-line"><span class="k">Asset / Lado</span><span>${p.asset} ${p.side}</span></div>
    <div class="pos-line"><span class="k">Entry Ask</span><span>${f(p.entry_price,4)}</span></div>
    <div class="pos-line"><span class="k">Shares</span><span>${f(p.shares,4)}</span></div>
    <div class="pos-line"><span class="k">Invertido</span><span>$${f(p.entry_usd,2)}</span></div>
    <div class="pos-line"><span class="k">Gap entrada</span><span>${((p.gap_entry||0)*100).toFixed(1)} pts</span></div>
    <div class="pos-line"><span class="k">Secs left</span><span>${f(p.secs_left_entry,0)}s</span></div>
  `;
}

function updateEvents(s) {
  const el=document.getElementById('events-log');
  const evs=(s.events||[]).slice().reverse();
  if (!evs.length) { el.innerHTML='Sin eventos aún'; return; }
  el.innerHTML=evs.map((e,i)=>{
    let c='';
    if (e.includes('WIN')||e.includes('ENTRADA')) c='ev-g';
    else if (e.includes('LOSS')||e.includes('STOP')||e.includes('Error')) c='ev-r';
    else if (i===0) c='ev-w';
    return `<div class="${c}">${e}</div>`;
  }).join('');
}

function updateTrades(s) {
  const tbody=document.getElementById('t-body');
  const trades=(s.recent_trades||[]).slice().reverse();
  document.getElementById('t-count').textContent=trades.length?`${trades.length} trades`:'';
  if (!trades.length) {
    tbody.innerHTML='<tr><td colspan="10" style="color:var(--dim);padding:18px 10px;text-align:center;font-size:10px">Sin trades aún</td></tr>';
    return;
  }
  tbody.innerHTML=trades.map(t=>{
    const pnl=parseFloat(t.pnl_usd||0);
    const pnlStr=(pnl>=0?'+':'')+'$'+pnl.toFixed(4);
    const ts=new Date(t.entry_ts);
    const timeStr=isNaN(ts)?'–':ts.toLocaleTimeString('es-CL',{hour:'2-digit',minute:'2-digit',second:'2-digit'});
    const gap=parseFloat(t.gap_pts||0);
    return `<tr class="${t.outcome==='WIN'?'r-win':'r-loss'}">
      <td class="d">${t.trade_id}</td>
      <td class="d">${timeStr}</td>
      <td>${t.asset}</td>
      <td><span class="tag tag-${(t.side||'').toLowerCase()}">${t.side}</span></td>
      <td>${f(t.entry_ask,4)}</td>
      <td class="d">${gap.toFixed(1)}</td>
      <td class="d">${f(t.secs_left_entry,0)}s</td>
      <td class="${pnl>=0?'g':'r'}">${pnlStr}</td>
      <td><span class="tag tag-${(t.outcome||'').toLowerCase()}">${t.outcome}</span></td>
      <td class="d" style="font-size:9px">${t.exit_type==='STOP_LOSS'?'SL':'RES'}</td>
    </tr>`;
  }).join('');
  updateEquity(trades);
  updateDonut(s.wins, s.losses);
}

async function poll() {
  try {
    const r=await fetch('/api/state');
    const s=await r.json();
    if (s.error) {
      document.getElementById('phase-badge').innerHTML='<span class="dot"></span> SIN DATOS';
      document.getElementById('phase-badge').className='error';
      document.getElementById('mkt-body').innerHTML=`<div style="color:var(--red);font-size:10px">${s.error}</div>`;
      return;
    }
    updatePhase(s); updateKPIs(s); updateMarkets(s); updateHarmonic(s);
    updateSignal(s); updatePosition(s); updateEvents(s); updateTrades(s);
    document.getElementById('ts').textContent=new Date().toLocaleTimeString('es-CL');
  } catch(e) {
    document.getElementById('ts').textContent='error de conexión';
  }
}

initEquity(); initDonut();
poll();
setInterval(poll, 1500);
</script>
</body>
</html>"""


@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
