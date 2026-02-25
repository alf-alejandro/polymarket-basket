<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BASKET — Divergencia Armónica</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;700;800&display=swap" rel="stylesheet">
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
    --text: #e2e8f0;
    --muted: #4a5568;
    --dim: #2d3748;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* GRID BACKGROUND */
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,245,196,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,245,196,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
  }

  .container {
    position: relative;
    z-index: 1;
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px 20px;
  }

  /* HEADER */
  header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border);
  }

  .logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 28px;
    letter-spacing: -1px;
    color: var(--accent);
    text-shadow: 0 0 30px rgba(0,245,196,0.4);
  }

  .logo span {
    color: var(--text);
    opacity: 0.4;
    font-weight: 400;
  }

  .subtitle {
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
    letter-spacing: 2px;
    text-transform: uppercase;
  }

  .header-right {
    text-align: right;
  }

  .live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,245,196,0.1);
    border: 1px solid rgba(0,245,196,0.3);
    padding: 4px 12px;
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--accent);
    text-transform: uppercase;
  }

  .live-dot {
    width: 6px; height: 6px;
    background: var(--accent);
    border-radius: 50%;
    animation: pulse 1.5s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
  }

  /* FILTER BAR */
  .filter-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    align-items: center;
  }

  .filter-label {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-right: 4px;
  }

  .filter-btn {
    background: var(--bg3);
    border: 1px solid var(--border);
    color: var(--muted);
    padding: 6px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    cursor: pointer;
    transition: all 0.15s;
    letter-spacing: 1px;
  }

  .filter-btn:hover, .filter-btn.active {
    background: rgba(0,245,196,0.1);
    border-color: var(--accent);
    color: var(--accent);
  }

  .filter-btn.active-gold {
    background: rgba(255,209,102,0.1);
    border-color: var(--gold);
    color: var(--gold);
  }

  /* KPI GRID */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
  }

  .kpi {
    background: var(--bg2);
    border: 1px solid var(--border);
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }

  .kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
    opacity: 0.5;
  }

  .kpi.red::before { background: var(--loss); }
  .kpi.gold::before { background: var(--gold); }
  .kpi.purple::before { background: var(--accent2); }

  .kpi-label {
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .kpi-value {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 26px;
    line-height: 1;
    color: var(--accent);
  }

  .kpi-value.red { color: var(--loss); }
  .kpi-value.gold { color: var(--gold); }
  .kpi-value.neutral { color: var(--text); }
  .kpi-value.purple { color: var(--accent2); }

  .kpi-sub {
    font-size: 10px;
    color: var(--muted);
    margin-top: 4px;
  }

  /* CHARTS GRID */
  .charts-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }

  .charts-grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin-bottom: 12px;
  }

  .panel {
    background: var(--bg2);
    border: 1px solid var(--border);
    padding: 20px;
  }

  .panel-title {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .panel-title-accent {
    color: var(--accent);
    font-size: 11px;
  }

  canvas {
    display: block;
    width: 100% !important;
  }

  /* HEATMAP */
  .heatmap-grid {
    display: grid;
    grid-template-columns: repeat(25, 1fr);
    gap: 2px;
  }

  .hm-cell {
    aspect-ratio: 1;
    border-radius: 1px;
    cursor: pointer;
    transition: transform 0.1s;
    position: relative;
  }

  .hm-cell:hover {
    transform: scale(1.5);
    z-index: 10;
  }

  .hm-cell .tooltip {
    display: none;
    position: absolute;
    bottom: calc(100% + 6px);
    left: 50%;
    transform: translateX(-50%);
    background: var(--bg3);
    border: 1px solid var(--border);
    padding: 6px 10px;
    font-size: 10px;
    white-space: nowrap;
    color: var(--text);
    z-index: 100;
    pointer-events: none;
  }

  .hm-cell:hover .tooltip { display: block; }

  /* SCATTER */
  #scatterWrap {
    position: relative;
  }

  /* TRADES TABLE */
  .trades-table-wrap {
    overflow-x: auto;
    max-height: 360px;
    overflow-y: auto;
  }

  .trades-table-wrap::-webkit-scrollbar { width: 4px; height: 4px; }
  .trades-table-wrap::-webkit-scrollbar-track { background: var(--bg); }
  .trades-table-wrap::-webkit-scrollbar-thumb { background: var(--dim); }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
  }

  thead th {
    background: var(--bg3);
    color: var(--muted);
    font-size: 9px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 8px 10px;
    text-align: left;
    position: sticky;
    top: 0;
    z-index: 5;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
  }

  thead th:hover { color: var(--accent); }
  thead th.sorted { color: var(--accent); }

  tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.1s;
  }

  tbody tr:hover { background: rgba(255,255,255,0.03); }
  tbody tr.win-row { border-left: 2px solid var(--win); }
  tbody tr.loss-row { border-left: 2px solid var(--loss); }

  td {
    padding: 7px 10px;
    white-space: nowrap;
    color: var(--text);
  }

  .badge {
    display: inline-block;
    padding: 2px 8px;
    font-size: 9px;
    letter-spacing: 1px;
    font-weight: 700;
  }

  .badge-win { background: rgba(0,245,196,0.15); color: var(--win); }
  .badge-loss { background: rgba(255,59,107,0.15); color: var(--loss); }
  .badge-eth { background: rgba(123,97,255,0.2); color: #a78bfa; }
  .badge-sol { background: rgba(153,69,255,0.2); color: #c084fc; }
  .badge-btc { background: rgba(255,209,102,0.2); color: var(--gold); }
  .badge-up { background: rgba(0,245,196,0.1); color: var(--accent); }
  .badge-dn { background: rgba(255,59,107,0.1); color: var(--loss); }
  .badge-sl { background: rgba(255,100,0,0.15); color: #ff9f43; }
  .badge-res { background: rgba(0,200,100,0.15); color: #2ecc71; }

  .pnl-pos { color: var(--win); font-weight: 700; }
  .pnl-neg { color: var(--loss); font-weight: 700; }

  /* WIN STREAK */
  .streak-bars {
    display: flex;
    gap: 3px;
    flex-wrap: wrap;
    margin-top: 4px;
  }

  .streak-bar {
    width: 8px;
    height: 28px;
    border-radius: 1px;
  }

  /* DISTRIBUTION */
  .dist-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }

  .dist-label {
    font-size: 10px;
    color: var(--muted);
    width: 32px;
    text-align: right;
  }

  .dist-bar-bg {
    flex: 1;
    height: 14px;
    background: var(--bg3);
    position: relative;
    overflow: hidden;
  }

  .dist-bar-fill {
    height: 100%;
    transition: width 0.8s cubic-bezier(0.16,1,0.3,1);
  }

  .dist-count {
    font-size: 10px;
    color: var(--muted);
    width: 24px;
    text-align: left;
  }

  /* LEGEND */
  .legend {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10px;
    color: var(--muted);
  }

  .legend-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
  }

  /* SEPARATOR */
  .section-sep {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
  }

  /* RESPONSIVE */
  @media (max-width: 900px) {
    .charts-grid, .charts-grid-2 { grid-template-columns: 1fr; }
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  }

  /* ANIMATED ENTRY */
  .panel, .kpi {
    animation: fadeUp 0.4s ease both;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .kpi:nth-child(1) { animation-delay: 0.05s; }
  .kpi:nth-child(2) { animation-delay: 0.10s; }
  .kpi:nth-child(3) { animation-delay: 0.15s; }
  .kpi:nth-child(4) { animation-delay: 0.20s; }
  .kpi:nth-child(5) { animation-delay: 0.25s; }
  .kpi:nth-child(6) { animation-delay: 0.30s; }
  .kpi:nth-child(7) { animation-delay: 0.35s; }
  .kpi:nth-child(8) { animation-delay: 0.40s; }

  .no-data {
    color: var(--muted);
    font-size: 11px;
    text-align: center;
    padding: 24px;
  }
</style>
</head>
<body>

<div class="container">

  <!-- HEADER -->
  <header>
    <div>
      <div class="logo">BASKET <span>/ Divergencia Armónica</span></div>
      <div class="subtitle">ETH · SOL · BTC — Polymarket 5m · Backtest histórico</div>
    </div>
    <div class="header-right">
      <div class="live-badge">
        <span class="live-dot"></span>
        BACKTEST DATA
      </div>
      <div style="margin-top:6px; font-size:10px; color:var(--muted);">175 trades — Feb 24-25, 2026</div>
    </div>
  </header>

  <!-- FILTER BAR -->
  <div class="filter-bar">
    <span class="filter-label">Filtro:</span>
    <button class="filter-btn active" onclick="setFilter('all')">TODOS (175)</button>
    <button class="filter-btn active-gold" onclick="setFilter('gold')" id="btn-gold">ZONA DORADA 60-85s / -14÷-5pts</button>
    <button class="filter-btn" onclick="setFilter('eth')">ETH</button>
    <button class="filter-btn" onclick="setFilter('sol')">SOL</button>
    <button class="filter-btn" onclick="setFilter('btc')">BTC</button>
    <button class="filter-btn" onclick="setFilter('win')">WINS</button>
    <button class="filter-btn" onclick="setFilter('loss')">LOSSES</button>
  </div>

  <!-- KPIs -->
  <div class="kpi-grid" id="kpi-grid"></div>

  <!-- EQUITY + WIN RATE RING -->
  <div class="charts-grid">
    <div class="panel" style="animation-delay:0.1s">
      <div class="panel-title">
        CURVA DE CAPITAL
        <span class="panel-title-accent" id="equity-label">$100 → $96.73</span>
      </div>
      <canvas id="equityChart" height="160"></canvas>
    </div>
    <div class="panel" style="animation-delay:0.15s">
      <div class="panel-title">WIN RATE<span class="panel-title-accent" id="wr-label"></span></div>
      <canvas id="donutChart" height="180"></canvas>
    </div>
  </div>

  <!-- HEATMAP + GAP DIST -->
  <div class="charts-grid-2">
    <div class="panel" style="animation-delay:0.2s">
      <div class="panel-title">HEATMAP DE TRADES <span class="panel-title-accent">verde=WIN · rojo=LOSS</span></div>
      <div class="heatmap-grid" id="heatmap"></div>
    </div>
    <div class="panel" style="animation-delay:0.25s">
      <div class="panel-title">DISTRIBUCIÓN POR GAP (pts)</div>
      <div id="gapDist"></div>
    </div>
    <div class="panel" style="animation-delay:0.3s">
      <div class="panel-title">PnL ACUMULADO POR ASSET</div>
      <canvas id="assetBar" height="160"></canvas>
    </div>
  </div>

  <!-- SCATTER + PNL DIST -->
  <div class="charts-grid">
    <div class="panel" style="animation-delay:0.35s">
      <div class="panel-title">
        SCATTER: GAP vs PnL
        <div class="legend">
          <span class="legend-item"><span class="legend-dot" style="background:var(--win)"></span>WIN</span>
          <span class="legend-item"><span class="legend-dot" style="background:var(--loss)"></span>LOSS</span>
          <span class="legend-item"><span class="legend-dot" style="background:rgba(255,209,102,0.7)"></span>ZONA DORADA</span>
        </div>
      </div>
      <canvas id="scatterChart" height="200"></canvas>
    </div>
    <div class="panel" style="animation-delay:0.4s">
      <div class="panel-title">SECS RESTANTES EN ENTRADA</div>
      <canvas id="secsChart" height="200"></canvas>
    </div>
  </div>

  <!-- STREAK VISUAL -->
  <div class="panel" style="margin-bottom:12px; animation-delay:0.45s">
    <div class="panel-title">SECUENCIA DE TRADES <span class="panel-title-accent" id="streak-label"></span></div>
    <div class="streak-bars" id="streakBars"></div>
  </div>

  <!-- TABLA -->
  <div class="panel" style="animation-delay:0.5s">
    <div class="panel-title">
      TRADES LOG
      <span style="font-size:10px; color:var(--muted)" id="table-count"></span>
    </div>
    <div class="trades-table-wrap">
      <table id="tradesTable">
        <thead>
          <tr>
            <th onclick="sortTable('id')">ID</th>
            <th onclick="sortTable('entry_ts')">HORA ENTRADA</th>
            <th onclick="sortTable('asset')">ASSET</th>
            <th onclick="sortTable('side')">LADO</th>
            <th onclick="sortTable('entry_ask')">ASK ENTRADA</th>
            <th onclick="sortTable('gap_pts')">GAP (pts)</th>
            <th onclick="sortTable('secs_left')">SECS LEFT</th>
            <th onclick="sortTable('pnl')">PnL USD</th>
            <th onclick="sortTable('outcome')">RESULTADO</th>
            <th onclick="sortTable('exit_type')">TIPO SALIDA</th>
            <th onclick="sortTable('duration_s')">DURACIÓN</th>
          </tr>
        </thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </div>

</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<script>
// ═══════════════════════════════════════
//  DATA
// ═══════════════════════════════════════
const ALL_TRADES = [{"id":"T0001","entry_ts":"2026-02-24T13:38:31.548650","exit_ts":"2026-02-24T13:39:25.420008","duration_s":53.9,"asset":"SOL","side":"UP","entry_ask":0.78,"gap_pts":-9.07,"secs_left":88.5,"pnl":0.282051,"outcome":"WIN","capital_after":100.2821,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0002","entry_ts":"2026-02-24T13:53:37.215758","exit_ts":"2026-02-24T13:54:44.854251","duration_s":67.6,"asset":"BTC","side":"UP","entry_ask":0.67,"gap_pts":-9.01,"secs_left":82.8,"pnl":0.492537,"outcome":"WIN","capital_after":100.7746,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0003","entry_ts":"2026-02-24T14:03:36.508128","exit_ts":"2026-02-24T14:04:45.920895","duration_s":69.4,"asset":"ETH","side":"DOWN","entry_ask":0.79,"gap_pts":-6.91,"secs_left":83.5,"pnl":0.265823,"outcome":"WIN","capital_after":101.0404,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0004","entry_ts":"2026-02-24T14:08:31.562363","exit_ts":"2026-02-24T14:09:46.365352","duration_s":74.8,"asset":"ETH","side":"UP","entry_ask":0.84,"gap_pts":-6.61,"secs_left":88.4,"pnl":0.190476,"outcome":"WIN","capital_after":101.2309,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0005","entry_ts":"2026-02-24T14:18:38.553060","exit_ts":"2026-02-24T14:19:37.543708","duration_s":59.0,"asset":"ETH","side":"DOWN","entry_ask":0.87,"gap_pts":-4.7,"secs_left":81.4,"pnl":0.149425,"outcome":"WIN","capital_after":101.3803,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0006","entry_ts":"2026-02-24T14:43:38.825302","exit_ts":"2026-02-24T14:44:23.123402","duration_s":44.3,"asset":"SOL","side":"UP","entry_ask":0.7,"gap_pts":-9.16,"secs_left":81.2,"pnl":0.428571,"outcome":"WIN","capital_after":101.8089,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0007","entry_ts":"2026-02-24T14:53:31.691041","exit_ts":"2026-02-24T14:53:48.385904","duration_s":16.7,"asset":"SOL","side":"UP","entry_ask":0.68,"gap_pts":-14.39,"secs_left":88.3,"pnl":-0.529412,"outcome":"LOSS","capital_after":101.2795,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0008","entry_ts":"2026-02-24T15:03:38.926845","exit_ts":"2026-02-24T15:04:55.023475","duration_s":76.1,"asset":"BTC","side":"DOWN","entry_ask":0.74,"gap_pts":-8.41,"secs_left":81.1,"pnl":0.351351,"outcome":"WIN","capital_after":101.6308,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0009","entry_ts":"2026-02-24T15:09:08.277187","exit_ts":"2026-02-24T15:09:38.431456","duration_s":30.2,"asset":"BTC","side":"UP","entry_ask":0.73,"gap_pts":-6.51,"secs_left":51.7,"pnl":0.369863,"outcome":"WIN","capital_after":102.0007,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0010","entry_ts":"2026-02-24T15:14:09.734354","exit_ts":"2026-02-24T15:14:34.882227","duration_s":25.1,"asset":"BTC","side":"UP","entry_ask":0.77,"gap_pts":-8.26,"secs_left":50.3,"pnl":0.298701,"outcome":"WIN","capital_after":102.2994,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0011","entry_ts":"2026-02-24T15:19:12.541973","exit_ts":"2026-02-24T15:19:44.729820","duration_s":32.2,"asset":"SOL","side":"UP","entry_ask":0.87,"gap_pts":-6.2,"secs_left":47.5,"pnl":0.149425,"outcome":"WIN","capital_after":102.4488,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0012","entry_ts":"2026-02-24T15:24:08.432739","exit_ts":"2026-02-24T15:24:55.316518","duration_s":46.9,"asset":"SOL","side":"UP","entry_ask":0.65,"gap_pts":-16.52,"secs_left":51.6,"pnl":0.538462,"outcome":"WIN","capital_after":102.9873,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0013","entry_ts":"2026-02-24T15:29:24.738686","exit_ts":"2026-02-24T15:29:39.895505","duration_s":15.2,"asset":"BTC","side":"DOWN","entry_ask":0.86,"gap_pts":-4.06,"secs_left":35.3,"pnl":-0.651163,"outcome":"LOSS","capital_after":102.3361,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0014","entry_ts":"2026-02-24T15:34:06.769096","exit_ts":"2026-02-24T15:34:56.248545","duration_s":49.5,"asset":"BTC","side":"DOWN","entry_ask":0.75,"gap_pts":-5.76,"secs_left":53.2,"pnl":0.333333,"outcome":"WIN","capital_after":102.6694,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0015","entry_ts":"2026-02-24T15:38:31.728615","exit_ts":"2026-02-24T15:39:29.601680","duration_s":57.9,"asset":"ETH","side":"DOWN","entry_ask":0.87,"gap_pts":-4.23,"secs_left":88.3,"pnl":0.149425,"outcome":"WIN","capital_after":102.8189,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0016","entry_ts":"2026-02-24T15:43:31.679116","exit_ts":"2026-02-24T15:44:11.994119","duration_s":40.3,"asset":"SOL","side":"DOWN","entry_ask":0.82,"gap_pts":-4.19,"secs_left":88.3,"pnl":-0.707317,"outcome":"LOSS","capital_after":102.1115,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0017","entry_ts":"2026-02-24T15:48:40.336565","exit_ts":"2026-02-24T15:49:32.969900","duration_s":52.6,"asset":"ETH","side":"UP","entry_ask":0.88,"gap_pts":-4.38,"secs_left":79.7,"pnl":0.136364,"outcome":"WIN","capital_after":102.2479,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0018","entry_ts":"2026-02-24T15:53:50.241797","exit_ts":"2026-02-24T15:54:46.677391","duration_s":56.4,"asset":"ETH","side":"DOWN","entry_ask":0.73,"gap_pts":-10.15,"secs_left":69.8,"pnl":0.369863,"outcome":"WIN","capital_after":102.6178,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0019","entry_ts":"2026-02-24T16:08:31.651174","exit_ts":"2026-02-24T16:09:30.948526","duration_s":59.3,"asset":"SOL","side":"DOWN","entry_ask":0.87,"gap_pts":-4.58,"secs_left":88.3,"pnl":-0.724138,"outcome":"LOSS","capital_after":101.8936,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0020","entry_ts":"2026-02-24T16:18:32.475165","exit_ts":"2026-02-24T16:18:50.140871","duration_s":17.7,"asset":"SOL","side":"DOWN","entry_ask":0.65,"gap_pts":-16.18,"secs_left":87.5,"pnl":-0.492308,"outcome":"LOSS","capital_after":101.4013,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0021","entry_ts":"2026-02-24T16:23:33.209453","exit_ts":"2026-02-24T16:24:26.563266","duration_s":53.4,"asset":"SOL","side":"DOWN","entry_ask":0.77,"gap_pts":-8.56,"secs_left":86.8,"pnl":0.298701,"outcome":"WIN","capital_after":101.7,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0022","entry_ts":"2026-02-24T16:28:32.133185","exit_ts":"2026-02-24T16:29:24.086114","duration_s":52.0,"asset":"SOL","side":"DOWN","entry_ask":0.67,"gap_pts":-16.58,"secs_left":87.9,"pnl":-0.597015,"outcome":"LOSS","capital_after":101.103,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0023","entry_ts":"2026-02-24T16:38:37.650407","exit_ts":"2026-02-24T16:38:47.830854","duration_s":10.2,"asset":"ETH","side":"UP","entry_ask":0.92,"gap_pts":-4.37,"secs_left":82.3,"pnl":0.086957,"outcome":"WIN","capital_after":101.19,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0024","entry_ts":"2026-02-24T16:48:49.499732","exit_ts":"2026-02-24T16:49:31.461114","duration_s":42.0,"asset":"BTC","side":"DOWN","entry_ask":0.77,"gap_pts":-5.99,"secs_left":70.5,"pnl":0.298701,"outcome":"WIN","capital_after":101.4887,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0025","entry_ts":"2026-02-24T17:04:26.804293","exit_ts":"2026-02-24T17:04:55.293739","duration_s":28.5,"asset":"BTC","side":"UP","entry_ask":0.7,"gap_pts":-15.02,"secs_left":33.2,"pnl":-0.642857,"outcome":"LOSS","capital_after":100.8458,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0026","entry_ts":"2026-02-24T17:09:07.584358","exit_ts":"2026-02-24T17:09:36.909801","duration_s":29.3,"asset":"ETH","side":"UP","entry_ask":0.91,"gap_pts":-5.77,"secs_left":52.4,"pnl":-0.637363,"outcome":"LOSS","capital_after":100.2084,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0027","entry_ts":"2026-02-24T17:28:31.738425","exit_ts":"2026-02-24T17:29:28.092898","duration_s":56.4,"asset":"SOL","side":"DOWN","entry_ask":0.84,"gap_pts":-8.2,"secs_left":88.3,"pnl":0.190476,"outcome":"WIN","capital_after":100.3989,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0028","entry_ts":"2026-02-24T17:38:58.904852","exit_ts":"2026-02-24T17:39:53.900028","duration_s":55.0,"asset":"ETH","side":"UP","entry_ask":0.86,"gap_pts":-5.45,"secs_left":61.1,"pnl":0.162791,"outcome":"WIN","capital_after":100.5617,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0029","entry_ts":"2026-02-24T17:43:39.808385","exit_ts":"2026-02-24T17:44:48.872317","duration_s":69.1,"asset":"SOL","side":"DOWN","entry_ask":0.73,"gap_pts":-10.42,"secs_left":80.2,"pnl":0.369863,"outcome":"WIN","capital_after":100.9316,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0030","entry_ts":"2026-02-24T17:58:31.660621","exit_ts":"2026-02-24T17:59:21.065943","duration_s":49.4,"asset":"SOL","side":"UP","entry_ask":0.78,"gap_pts":-13.94,"secs_left":88.3,"pnl":-0.589744,"outcome":"LOSS","capital_after":100.3418,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0031","entry_ts":"2026-02-24T18:03:31.793532","exit_ts":"2026-02-24T18:04:13.420841","duration_s":41.6,"asset":"ETH","side":"UP","entry_ask":0.9,"gap_pts":-4.86,"secs_left":88.2,"pnl":-0.633333,"outcome":"LOSS","capital_after":99.7085,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0032","entry_ts":"2026-02-24T18:08:31.785501","exit_ts":"2026-02-24T18:09:11.258211","duration_s":39.5,"asset":"BTC","side":"DOWN","entry_ask":0.85,"gap_pts":-7.48,"secs_left":88.2,"pnl":0.176471,"outcome":"WIN","capital_after":99.885,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0033","entry_ts":"2026-02-24T18:18:31.777200","exit_ts":"2026-02-24T18:19:05.512630","duration_s":33.7,"asset":"ETH","side":"UP","entry_ask":0.9,"gap_pts":-5.94,"secs_left":88.2,"pnl":0.111111,"outcome":"WIN","capital_after":99.9961,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0034","entry_ts":"2026-02-24T18:28:38.988199","exit_ts":"2026-02-24T18:29:29.894865","duration_s":50.9,"asset":"BTC","side":"DOWN","entry_ask":0.7,"gap_pts":-13.05,"secs_left":81.0,"pnl":-0.528572,"outcome":"LOSS","capital_after":99.4675,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0035","entry_ts":"2026-02-24T18:33:31.729570","exit_ts":"2026-02-24T18:34:18.739861","duration_s":47.0,"asset":"SOL","side":"UP","entry_ask":0.87,"gap_pts":-8.08,"secs_left":88.3,"pnl":0.149425,"outcome":"WIN","capital_after":99.6169,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0036","entry_ts":"2026-02-24T18:43:55.823464","exit_ts":"2026-02-24T18:44:40.393660","duration_s":44.6,"asset":"ETH","side":"UP","entry_ask":0.88,"gap_pts":-4.07,"secs_left":64.2,"pnl":-0.670454,"outcome":"LOSS","capital_after":98.9465,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0037","entry_ts":"2026-02-24T18:48:31.909428","exit_ts":"2026-02-24T18:49:53.211013","duration_s":81.3,"asset":"SOL","side":"UP","entry_ask":0.83,"gap_pts":-7.56,"secs_left":88.1,"pnl":0.204819,"outcome":"WIN","capital_after":99.1513,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0038","entry_ts":"2026-02-24T18:53:55.379794","exit_ts":"2026-02-24T18:54:56.918462","duration_s":61.5,"asset":"SOL","side":"DOWN","entry_ask":0.66,"gap_pts":-11.25,"secs_left":64.6,"pnl":0.515152,"outcome":"WIN","capital_after":99.6664,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0039","entry_ts":"2026-02-24T18:59:11.142584","exit_ts":"2026-02-24T18:59:38.475344","duration_s":27.3,"asset":"SOL","side":"DOWN","entry_ask":0.7,"gap_pts":-13.16,"secs_left":48.9,"pnl":0.428571,"outcome":"WIN","capital_after":100.095,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0040","entry_ts":"2026-02-24T19:03:36.353803","exit_ts":"2026-02-24T19:04:52.023003","duration_s":75.7,"asset":"SOL","side":"UP","entry_ask":0.85,"gap_pts":-4.23,"secs_left":83.6,"pnl":0.176471,"outcome":"WIN","capital_after":100.2715,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0041","entry_ts":"2026-02-24T19:28:42.013271","exit_ts":"2026-02-24T19:29:41.757953","duration_s":59.7,"asset":"SOL","side":"DOWN","entry_ask":0.66,"gap_pts":-13.98,"secs_left":78.0,"pnl":0.515152,"outcome":"WIN","capital_after":100.7866,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0042","entry_ts":"2026-02-24T19:33:33.091462","exit_ts":"2026-02-24T19:34:47.470089","duration_s":74.4,"asset":"SOL","side":"UP","entry_ask":0.82,"gap_pts":-5.45,"secs_left":86.9,"pnl":0.219512,"outcome":"WIN","capital_after":101.0062,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0043","entry_ts":"2026-02-24T19:43:51.483910","exit_ts":"2026-02-24T19:44:50.107622","duration_s":58.6,"asset":"SOL","side":"UP","entry_ask":0.75,"gap_pts":-9.68,"secs_left":68.5,"pnl":0.333333,"outcome":"WIN","capital_after":101.3395,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0044","entry_ts":"2026-02-24T19:54:01.441193","exit_ts":"2026-02-24T19:54:33.109528","duration_s":31.7,"asset":"ETH","side":"DOWN","entry_ask":0.76,"gap_pts":-7.19,"secs_left":58.6,"pnl":0.315789,"outcome":"WIN","capital_after":101.6553,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0045","entry_ts":"2026-02-24T19:58:31.737114","exit_ts":"2026-02-24T19:59:07.388093","duration_s":35.7,"asset":"ETH","side":"UP","entry_ask":0.91,"gap_pts":-5.64,"secs_left":88.3,"pnl":-0.637363,"outcome":"LOSS","capital_after":101.0179,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0046","entry_ts":"2026-02-24T20:08:33.316093","exit_ts":"2026-02-24T20:09:17.011030","duration_s":43.7,"asset":"SOL","side":"DOWN","entry_ask":0.91,"gap_pts":-4.07,"secs_left":86.7,"pnl":0.098901,"outcome":"WIN","capital_after":101.1168,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0047","entry_ts":"2026-02-24T20:19:13.576780","exit_ts":"2026-02-24T20:19:51.590479","duration_s":38.0,"asset":"SOL","side":"UP","entry_ask":0.89,"gap_pts":-6.25,"secs_left":46.4,"pnl":0.123596,"outcome":"WIN","capital_after":101.2404,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0048","entry_ts":"2026-02-24T20:23:31.824022","exit_ts":"2026-02-24T20:24:34.858265","duration_s":63.0,"asset":"SOL","side":"UP","entry_ask":0.67,"gap_pts":-15.06,"secs_left":88.2,"pnl":0.492537,"outcome":"WIN","capital_after":101.7329,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0049","entry_ts":"2026-02-24T20:29:24.703789","exit_ts":"2026-02-24T20:29:31.869681","duration_s":7.2,"asset":"BTC","side":"UP","entry_ask":0.68,"gap_pts":-9.57,"secs_left":35.3,"pnl":-0.661765,"outcome":"LOSS","capital_after":101.0712,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0050","entry_ts":"2026-02-24T20:33:31.936475","exit_ts":"2026-02-24T20:34:59.987753","duration_s":88.1,"asset":"SOL","side":"UP","entry_ask":0.86,"gap_pts":-6.69,"secs_left":88.1,"pnl":0.162791,"outcome":"WIN","capital_after":101.234,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0051","entry_ts":"2026-02-24T20:39:13.798480","exit_ts":"2026-02-24T20:39:53.756021","duration_s":40.0,"asset":"ETH","side":"DOWN","entry_ask":0.7,"gap_pts":-11.84,"secs_left":46.2,"pnl":0.428571,"outcome":"WIN","capital_after":101.6625,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0052","entry_ts":"2026-02-24T20:43:31.691931","exit_ts":"2026-02-24T20:44:49.243852","duration_s":77.6,"asset":"BTC","side":"UP","entry_ask":0.68,"gap_pts":-15.59,"secs_left":88.3,"pnl":0.470588,"outcome":"WIN","capital_after":102.1331,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0053","entry_ts":"2026-02-24T20:48:32.585348","exit_ts":"2026-02-24T20:49:25.239282","duration_s":52.7,"asset":"ETH","side":"DOWN","entry_ask":0.72,"gap_pts":-10.23,"secs_left":87.4,"pnl":0.388889,"outcome":"WIN","capital_after":102.522,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0054","entry_ts":"2026-02-24T20:53:54.757530","exit_ts":"2026-02-24T20:54:47.898648","duration_s":53.1,"asset":"ETH","side":"UP","entry_ask":0.71,"gap_pts":-8.27,"secs_left":65.2,"pnl":0.408451,"outcome":"WIN","capital_after":102.9305,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0055","entry_ts":"2026-02-24T21:08:32.451494","exit_ts":"2026-02-24T21:09:43.998025","duration_s":71.5,"asset":"ETH","side":"UP","entry_ask":0.84,"gap_pts":-4.46,"secs_left":87.5,"pnl":0.190476,"outcome":"WIN","capital_after":103.1209,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0056","entry_ts":"2026-02-24T21:14:15.973005","exit_ts":"2026-02-24T21:14:57.138047","duration_s":41.2,"asset":"BTC","side":"UP","entry_ask":0.77,"gap_pts":-9.03,"secs_left":44.0,"pnl":0.298701,"outcome":"WIN","capital_after":103.4197,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0057","entry_ts":"2026-02-24T21:23:31.820372","exit_ts":"2026-02-24T21:24:21.559381","duration_s":49.7,"asset":"SOL","side":"UP","entry_ask":0.83,"gap_pts":-5.12,"secs_left":88.2,"pnl":0.204819,"outcome":"WIN","capital_after":103.6245,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0058","entry_ts":"2026-02-24T21:28:56.948178","exit_ts":"2026-02-24T21:29:25.584017","duration_s":28.6,"asset":"SOL","side":"DOWN","entry_ask":0.79,"gap_pts":-12.81,"secs_left":63.1,"pnl":0.265823,"outcome":"WIN","capital_after":103.8903,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0059","entry_ts":"2026-02-24T21:33:43.878737","exit_ts":"2026-02-24T21:34:50.457561","duration_s":66.6,"asset":"BTC","side":"DOWN","entry_ask":0.73,"gap_pts":-6.67,"secs_left":76.1,"pnl":0.369863,"outcome":"WIN","capital_after":104.2602,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0060","entry_ts":"2026-02-24T21:44:10.398517","exit_ts":"2026-02-24T21:44:36.655506","duration_s":26.3,"asset":"SOL","side":"UP","entry_ask":0.74,"gap_pts":-11.11,"secs_left":49.6,"pnl":-0.567568,"outcome":"LOSS","capital_after":103.6926,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0061","entry_ts":"2026-02-24T21:59:01.009566","exit_ts":"2026-02-24T21:59:55.631086","duration_s":54.6,"asset":"SOL","side":"UP","entry_ask":0.8,"gap_pts":-9.69,"secs_left":59.0,"pnl":0.25,"outcome":"WIN","capital_after":103.9426,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0062","entry_ts":"2026-02-24T22:08:31.725893","exit_ts":"2026-02-24T22:09:59.414885","duration_s":87.7,"asset":"SOL","side":"DOWN","entry_ask":0.69,"gap_pts":-14.19,"secs_left":88.3,"pnl":0.449275,"outcome":"WIN","capital_after":104.3919,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0063","entry_ts":"2026-02-24T22:13:46.234484","exit_ts":"2026-02-24T22:14:34.410414","duration_s":48.2,"asset":"BTC","side":"UP","entry_ask":0.66,"gap_pts":-18.67,"secs_left":73.8,"pnl":0.515152,"outcome":"WIN","capital_after":104.907,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0064","entry_ts":"2026-02-24T22:24:26.293175","exit_ts":"2026-02-24T22:24:55.628320","duration_s":29.3,"asset":"SOL","side":"UP","entry_ask":0.77,"gap_pts":-10.85,"secs_left":33.7,"pnl":-0.584416,"outcome":"LOSS","capital_after":104.3226,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0065","entry_ts":"2026-02-24T22:28:42.785554","exit_ts":"2026-02-24T22:29:39.971931","duration_s":57.2,"asset":"BTC","side":"UP","entry_ask":0.65,"gap_pts":-16.27,"secs_left":77.2,"pnl":-0.492308,"outcome":"LOSS","capital_after":103.8303,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0066","entry_ts":"2026-02-24T22:33:37.559829","exit_ts":"2026-02-24T22:34:58.152544","duration_s":80.6,"asset":"SOL","side":"DOWN","entry_ask":0.92,"gap_pts":-4.22,"secs_left":82.4,"pnl":0.086957,"outcome":"WIN","capital_after":103.9172,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0067","entry_ts":"2026-02-24T22:39:22.304865","exit_ts":"2026-02-24T22:39:38.318537","duration_s":16.0,"asset":"SOL","side":"UP","entry_ask":0.8,"gap_pts":-19.64,"secs_left":37.7,"pnl":-0.6375,"outcome":"LOSS","capital_after":103.2797,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0068","entry_ts":"2026-02-24T22:43:58.076622","exit_ts":"2026-02-24T22:44:50.151485","duration_s":52.1,"asset":"SOL","side":"DOWN","entry_ask":0.69,"gap_pts":-18.3,"secs_left":61.9,"pnl":0.449275,"outcome":"WIN","capital_after":103.729,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0069","entry_ts":"2026-02-24T22:49:03.177825","exit_ts":"2026-02-24T22:49:30.661719","duration_s":27.5,"asset":"BTC","side":"UP","entry_ask":0.86,"gap_pts":-4.06,"secs_left":56.8,"pnl":0.162791,"outcome":"WIN","capital_after":103.8918,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0070","entry_ts":"2026-02-24T22:54:27.026143","exit_ts":"2026-02-24T22:54:45.531274","duration_s":18.5,"asset":"ETH","side":"DOWN","entry_ask":0.84,"gap_pts":-8.76,"secs_left":33.0,"pnl":0.190476,"outcome":"WIN","capital_after":104.0823,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0071","entry_ts":"2026-02-24T22:58:41.367945","exit_ts":"2026-02-24T22:58:54.845610","duration_s":13.5,"asset":"SOL","side":"UP","entry_ask":0.97,"gap_pts":-4.24,"secs_left":78.6,"pnl":0.030928,"outcome":"WIN","capital_after":104.1132,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0072","entry_ts":"2026-02-24T23:03:36.012453","exit_ts":"2026-02-24T23:03:53.057015","duration_s":17.0,"asset":"SOL","side":"DOWN","entry_ask":0.65,"gap_pts":-19.51,"secs_left":84.0,"pnl":-0.492308,"outcome":"LOSS","capital_after":103.6209,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0073","entry_ts":"2026-02-24T23:08:31.906983","exit_ts":"2026-02-24T23:09:24.818967","duration_s":52.9,"asset":"SOL","side":"DOWN","entry_ask":0.9,"gap_pts":-6.09,"secs_left":88.1,"pnl":0.111111,"outcome":"WIN","capital_after":103.732,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0074","entry_ts":"2026-02-24T23:13:32.406907","exit_ts":"2026-02-24T23:14:11.086713","duration_s":38.7,"asset":"ETH","side":"UP","entry_ask":0.94,"gap_pts":-4.55,"secs_left":87.6,"pnl":0.06383,"outcome":"WIN","capital_after":103.7959,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0075","entry_ts":"2026-02-24T23:24:13.191736","exit_ts":"2026-02-24T23:24:51.163713","duration_s":38.0,"asset":"BTC","side":"UP","entry_ask":0.88,"gap_pts":-5.86,"secs_left":46.8,"pnl":0.136364,"outcome":"WIN","capital_after":103.9322,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0076","entry_ts":"2026-02-24T23:28:41.209424","exit_ts":"2026-02-24T23:29:08.057002","duration_s":26.8,"asset":"SOL","side":"UP","entry_ask":0.69,"gap_pts":-12.84,"secs_left":78.8,"pnl":0.449275,"outcome":"WIN","capital_after":104.3815,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0077","entry_ts":"2026-02-24T23:33:56.260270","exit_ts":"2026-02-24T23:34:25.415590","duration_s":29.2,"asset":"SOL","side":"DOWN","entry_ask":0.67,"gap_pts":-17.86,"secs_left":63.7,"pnl":-0.552239,"outcome":"LOSS","capital_after":103.8293,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0078","entry_ts":"2026-02-24T23:38:38.555549","exit_ts":"2026-02-24T23:39:31.895173","duration_s":53.3,"asset":"SOL","side":"UP","entry_ask":0.92,"gap_pts":-5.18,"secs_left":81.4,"pnl":0.086957,"outcome":"WIN","capital_after":103.9162,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0079","entry_ts":"2026-02-24T23:48:35.731621","exit_ts":"2026-02-24T23:49:16.378883","duration_s":40.6,"asset":"BTC","side":"DOWN","entry_ask":0.93,"gap_pts":-4.87,"secs_left":84.3,"pnl":0.075269,"outcome":"WIN","capital_after":103.9915,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0080","entry_ts":"2026-02-24T23:53:31.726239","exit_ts":"2026-02-24T23:54:05.370128","duration_s":33.6,"asset":"ETH","side":"DOWN","entry_ask":0.79,"gap_pts":-6.71,"secs_left":88.3,"pnl":-0.64557,"outcome":"LOSS","capital_after":103.3459,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0081","entry_ts":"2026-02-24T23:58:47.384996","exit_ts":"2026-02-24T23:59:07.158324","duration_s":19.8,"asset":"ETH","side":"UP","entry_ask":0.65,"gap_pts":-16.41,"secs_left":72.6,"pnl":-0.923077,"outcome":"LOSS","capital_after":102.4228,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0082","entry_ts":"2026-02-25T00:03:31.607981","exit_ts":"2026-02-25T00:04:56.638244","duration_s":85.0,"asset":"BTC","side":"DOWN","entry_ask":0.75,"gap_pts":-8.16,"secs_left":88.4,"pnl":0.333333,"outcome":"WIN","capital_after":102.7562,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0083","entry_ts":"2026-02-25T00:08:35.142845","exit_ts":"2026-02-25T00:09:46.439770","duration_s":71.3,"asset":"SOL","side":"UP","entry_ask":0.75,"gap_pts":-7.13,"secs_left":84.9,"pnl":-0.733333,"outcome":"LOSS","capital_after":102.0228,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0084","entry_ts":"2026-02-25T00:18:35.887829","exit_ts":"2026-02-25T00:19:04.415837","duration_s":28.5,"asset":"SOL","side":"UP","entry_ask":0.95,"gap_pts":-4.06,"secs_left":84.1,"pnl":0.052632,"outcome":"WIN","capital_after":102.0755,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0085","entry_ts":"2026-02-25T00:23:31.805448","exit_ts":"2026-02-25T00:23:56.031751","duration_s":24.2,"asset":"BTC","side":"DOWN","entry_ask":0.88,"gap_pts":-5.49,"secs_left":88.2,"pnl":0.136364,"outcome":"WIN","capital_after":102.2118,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0086","entry_ts":"2026-02-25T00:49:11.417908","exit_ts":"2026-02-25T00:49:49.128251","duration_s":37.7,"asset":"SOL","side":"DOWN","entry_ask":0.94,"gap_pts":-4.55,"secs_left":48.6,"pnl":0.06383,"outcome":"WIN","capital_after":102.2757,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0087","entry_ts":"2026-02-25T00:54:24.014108","exit_ts":"2026-02-25T00:54:40.084234","duration_s":16.1,"asset":"ETH","side":"UP","entry_ask":0.74,"gap_pts":-17.42,"secs_left":36.0,"pnl":-0.621622,"outcome":"LOSS","capital_after":101.654,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0088","entry_ts":"2026-02-25T01:18:52.432672","exit_ts":"2026-02-25T01:19:53.258845","duration_s":60.8,"asset":"ETH","side":"UP","entry_ask":0.66,"gap_pts":-16.72,"secs_left":67.6,"pnl":0.515152,"outcome":"WIN","capital_after":102.1692,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0089","entry_ts":"2026-02-25T01:23:38.349471","exit_ts":"2026-02-25T01:24:06.479205","duration_s":28.1,"asset":"SOL","side":"UP","entry_ask":0.66,"gap_pts":-14.61,"secs_left":81.7,"pnl":-0.515151,"outcome":"LOSS","capital_after":101.654,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0090","entry_ts":"2026-02-25T01:38:31.726179","exit_ts":"2026-02-25T01:39:54.997402","duration_s":83.3,"asset":"SOL","side":"UP","entry_ask":0.75,"gap_pts":-13.07,"secs_left":88.3,"pnl":0.333333,"outcome":"WIN","capital_after":101.9874,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0091","entry_ts":"2026-02-25T01:43:31.696437","exit_ts":"2026-02-25T01:44:11.541150","duration_s":39.8,"asset":"SOL","side":"DOWN","entry_ask":0.83,"gap_pts":-10.73,"secs_left":88.3,"pnl":0.204819,"outcome":"WIN","capital_after":102.1922,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0092","entry_ts":"2026-02-25T01:53:31.680197","exit_ts":"2026-02-25T01:54:10.177680","duration_s":38.5,"asset":"ETH","side":"DOWN","entry_ask":0.84,"gap_pts":-6.97,"secs_left":88.3,"pnl":0.190476,"outcome":"WIN","capital_after":102.3827,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0093","entry_ts":"2026-02-25T01:58:31.721432","exit_ts":"2026-02-25T02:00:00.031943","duration_s":88.3,"asset":"SOL","side":"UP","entry_ask":0.8,"gap_pts":-5.83,"secs_left":88.3,"pnl":0.25,"outcome":"WIN","capital_after":102.6327,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0094","entry_ts":"2026-02-25T02:03:31.576063","exit_ts":"2026-02-25T02:04:57.174211","duration_s":85.6,"asset":"ETH","side":"UP","entry_ask":0.68,"gap_pts":-15.06,"secs_left":88.4,"pnl":0.470588,"outcome":"WIN","capital_after":103.1033,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0095","entry_ts":"2026-02-25T02:13:31.680963","exit_ts":"2026-02-25T02:14:34.384752","duration_s":62.7,"asset":"ETH","side":"UP","entry_ask":0.83,"gap_pts":-8.67,"secs_left":88.3,"pnl":0.204819,"outcome":"WIN","capital_after":103.3081,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0096","entry_ts":"2026-02-25T02:28:31.604206","exit_ts":"2026-02-25T02:29:01.344896","duration_s":29.7,"asset":"SOL","side":"UP","entry_ask":0.81,"gap_pts":-8.67,"secs_left":88.4,"pnl":-0.62963,"outcome":"LOSS","capital_after":102.6784,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0097","entry_ts":"2026-02-25T02:33:31.656211","exit_ts":"2026-02-25T02:34:06.684798","duration_s":35.0,"asset":"SOL","side":"DOWN","entry_ask":0.84,"gap_pts":-7.71,"secs_left":88.3,"pnl":0.190476,"outcome":"WIN","capital_after":102.8689,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0098","entry_ts":"2026-02-25T02:38:31.674574","exit_ts":"2026-02-25T02:39:06.801509","duration_s":35.1,"asset":"SOL","side":"UP","entry_ask":0.74,"gap_pts":-9.04,"secs_left":88.3,"pnl":-0.635135,"outcome":"LOSS","capital_after":102.2338,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0099","entry_ts":"2026-02-25T02:48:31.652508","exit_ts":"2026-02-25T02:49:32.321358","duration_s":60.7,"asset":"BTC","side":"UP","entry_ask":0.67,"gap_pts":-13.59,"secs_left":88.3,"pnl":0.492537,"outcome":"WIN","capital_after":102.7263,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0100","entry_ts":"2026-02-25T02:59:05.598560","exit_ts":"2026-02-25T02:59:57.218540","duration_s":51.6,"asset":"SOL","side":"DOWN","entry_ask":0.7,"gap_pts":-17.52,"secs_left":54.4,"pnl":0.428571,"outcome":"WIN","capital_after":103.1549,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0101","entry_ts":"2026-02-25T03:03:31.856554","exit_ts":"2026-02-25T03:04:41.725957","duration_s":69.9,"asset":"BTC","side":"DOWN","entry_ask":0.91,"gap_pts":-6.12,"secs_left":88.1,"pnl":0.098901,"outcome":"WIN","capital_after":103.2538,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0102","entry_ts":"2026-02-25T03:13:31.580139","exit_ts":"2026-02-25T03:14:37.824624","duration_s":66.2,"asset":"SOL","side":"DOWN","entry_ask":0.74,"gap_pts":-12.77,"secs_left":88.4,"pnl":0.351351,"outcome":"WIN","capital_after":103.6051,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0103","entry_ts":"2026-02-25T03:23:41.553510","exit_ts":"2026-02-25T03:24:28.914641","duration_s":47.4,"asset":"SOL","side":"DOWN","entry_ask":0.66,"gap_pts":-15.51,"secs_left":78.4,"pnl":0.515152,"outcome":"WIN","capital_after":104.1203,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0104","entry_ts":"2026-02-25T03:33:54.332911","exit_ts":"2026-02-25T03:34:17.216171","duration_s":22.9,"asset":"SOL","side":"DOWN","entry_ask":0.68,"gap_pts":-14.87,"secs_left":65.7,"pnl":-0.720588,"outcome":"LOSS","capital_after":103.3997,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0105","entry_ts":"2026-02-25T03:39:15.222125","exit_ts":"2026-02-25T03:39:57.322195","duration_s":42.1,"asset":"SOL","side":"DOWN","entry_ask":0.8,"gap_pts":-12.13,"secs_left":44.8,"pnl":0.25,"outcome":"WIN","capital_after":103.6497,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0106","entry_ts":"2026-02-25T03:59:00.271738","exit_ts":"2026-02-25T03:59:50.419746","duration_s":50.1,"asset":"SOL","side":"DOWN","entry_ask":0.72,"gap_pts":-12.56,"secs_left":59.7,"pnl":-0.569444,"outcome":"LOSS","capital_after":103.0803,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0107","entry_ts":"2026-02-25T04:09:18.840078","exit_ts":"2026-02-25T04:09:55.642518","duration_s":36.8,"asset":"SOL","side":"UP","entry_ask":0.79,"gap_pts":-4.81,"secs_left":41.2,"pnl":0.265823,"outcome":"WIN","capital_after":103.3461,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0108","entry_ts":"2026-02-25T04:18:31.828016","exit_ts":"2026-02-25T04:19:23.453425","duration_s":51.6,"asset":"ETH","side":"DOWN","entry_ask":0.77,"gap_pts":-6.88,"secs_left":88.2,"pnl":-0.961039,"outcome":"LOSS","capital_after":102.385,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0109","entry_ts":"2026-02-25T04:23:31.555087","exit_ts":"2026-02-25T04:24:26.247442","duration_s":54.7,"asset":"SOL","side":"UP","entry_ask":0.89,"gap_pts":-8.98,"secs_left":88.4,"pnl":0.123596,"outcome":"WIN","capital_after":102.5086,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0110","entry_ts":"2026-02-25T04:44:07.631885","exit_ts":"2026-02-25T04:44:50.046200","duration_s":42.4,"asset":"SOL","side":"UP","entry_ask":0.65,"gap_pts":-14.52,"secs_left":52.4,"pnl":0.538462,"outcome":"WIN","capital_after":103.0471,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0111","entry_ts":"2026-02-25T04:58:45.607944","exit_ts":"2026-02-25T04:59:52.653910","duration_s":67.0,"asset":"BTC","side":"DOWN","entry_ask":0.81,"gap_pts":-5.25,"secs_left":74.4,"pnl":0.234568,"outcome":"WIN","capital_after":103.2817,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0112","entry_ts":"2026-02-25T05:19:25.179497","exit_ts":"2026-02-25T05:19:51.190936","duration_s":26.0,"asset":"SOL","side":"DOWN","entry_ask":0.89,"gap_pts":-8.0,"secs_left":34.8,"pnl":0.123596,"outcome":"WIN","capital_after":103.4053,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0113","entry_ts":"2026-02-25T05:28:32.385285","exit_ts":"2026-02-25T05:29:01.371224","duration_s":29.0,"asset":"SOL","side":"UP","entry_ask":0.66,"gap_pts":-11.79,"secs_left":87.6,"pnl":-0.590909,"outcome":"LOSS","capital_after":102.8144,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0114","entry_ts":"2026-02-25T05:48:41.467747","exit_ts":"2026-02-25T05:49:00.336849","duration_s":18.9,"asset":"BTC","side":"UP","entry_ask":0.93,"gap_pts":-4.04,"secs_left":78.5,"pnl":0.075269,"outcome":"WIN","capital_after":102.8896,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0115","entry_ts":"2026-02-25T05:54:22.736864","exit_ts":"2026-02-25T05:54:57.822823","duration_s":35.1,"asset":"BTC","side":"DOWN","entry_ask":0.81,"gap_pts":-4.99,"secs_left":37.3,"pnl":0.234568,"outcome":"WIN","capital_after":103.1242,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0116","entry_ts":"2026-02-25T06:03:31.498245","exit_ts":"2026-02-25T06:05:00.747779","duration_s":89.2,"asset":"SOL","side":"UP","entry_ask":0.7,"gap_pts":-17.74,"secs_left":88.5,"pnl":0.428571,"outcome":"WIN","capital_after":103.5528,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0117","entry_ts":"2026-02-25T06:09:16.258065","exit_ts":"2026-02-25T06:09:45.298022","duration_s":29.0,"asset":"ETH","side":"DOWN","entry_ask":0.71,"gap_pts":-11.6,"secs_left":43.7,"pnl":-0.535211,"outcome":"LOSS","capital_after":103.0176,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0118","entry_ts":"2026-02-25T06:13:50.170678","exit_ts":"2026-02-25T06:14:22.358681","duration_s":32.2,"asset":"ETH","side":"DOWN","entry_ask":0.81,"gap_pts":-5.72,"secs_left":69.8,"pnl":-0.604938,"outcome":"LOSS","capital_after":102.4126,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0119","entry_ts":"2026-02-25T06:18:31.504161","exit_ts":"2026-02-25T06:19:42.762099","duration_s":71.3,"asset":"SOL","side":"DOWN","entry_ask":0.81,"gap_pts":-9.55,"secs_left":88.5,"pnl":-0.617284,"outcome":"LOSS","capital_after":101.7953,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0120","entry_ts":"2026-02-25T06:33:31.461275","exit_ts":"2026-02-25T06:34:16.662990","duration_s":45.2,"asset":"ETH","side":"UP","entry_ask":0.8,"gap_pts":-6.08,"secs_left":88.5,"pnl":-0.5875,"outcome":"LOSS","capital_after":101.2078,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0121","entry_ts":"2026-02-25T06:38:34.577650","exit_ts":"2026-02-25T06:39:42.067477","duration_s":67.5,"asset":"SOL","side":"UP","entry_ask":0.82,"gap_pts":-4.19,"secs_left":85.4,"pnl":0.219512,"outcome":"WIN","capital_after":101.4273,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0122","entry_ts":"2026-02-25T06:49:12.859878","exit_ts":"2026-02-25T06:49:39.996828","duration_s":27.1,"asset":"SOL","side":"DOWN","entry_ask":0.93,"gap_pts":-4.04,"secs_left":47.1,"pnl":0.075269,"outcome":"WIN","capital_after":101.5026,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0123","entry_ts":"2026-02-25T07:08:31.586878","exit_ts":"2026-02-25T07:08:53.994979","duration_s":22.4,"asset":"SOL","side":"DOWN","entry_ask":0.79,"gap_pts":-12.68,"secs_left":88.4,"pnl":-0.594937,"outcome":"LOSS","capital_after":100.9077,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0124","entry_ts":"2026-02-25T07:13:38.212671","exit_ts":"2026-02-25T07:14:51.333824","duration_s":73.1,"asset":"ETH","side":"UP","entry_ask":0.89,"gap_pts":-4.35,"secs_left":81.8,"pnl":0.123596,"outcome":"WIN","capital_after":101.0313,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0125","entry_ts":"2026-02-25T07:23:33.820689","exit_ts":"2026-02-25T07:24:41.416116","duration_s":67.6,"asset":"ETH","side":"DOWN","entry_ask":0.74,"gap_pts":-8.32,"secs_left":86.2,"pnl":0.351351,"outcome":"WIN","capital_after":101.3826,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0126","entry_ts":"2026-02-25T07:28:34.041074","exit_ts":"2026-02-25T07:29:49.060628","duration_s":75.0,"asset":"SOL","side":"UP","entry_ask":0.75,"gap_pts":-8.15,"secs_left":86.0,"pnl":0.333333,"outcome":"WIN","capital_after":101.716,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0127","entry_ts":"2026-02-25T07:33:31.479359","exit_ts":"2026-02-25T07:34:43.149668","duration_s":71.7,"asset":"BTC","side":"UP","entry_ask":0.75,"gap_pts":-13.22,"secs_left":88.5,"pnl":0.333333,"outcome":"WIN","capital_after":102.0493,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0128","entry_ts":"2026-02-25T07:43:31.464314","exit_ts":"2026-02-25T07:43:58.100185","duration_s":26.6,"asset":"ETH","side":"DOWN","entry_ask":0.79,"gap_pts":-10.56,"secs_left":88.5,"pnl":0.265823,"outcome":"WIN","capital_after":102.3151,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0129","entry_ts":"2026-02-25T07:53:32.128966","exit_ts":"2026-02-25T07:54:15.443658","duration_s":43.3,"asset":"SOL","side":"UP","entry_ask":0.92,"gap_pts":-4.02,"secs_left":87.9,"pnl":0.086957,"outcome":"WIN","capital_after":102.4021,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0130","entry_ts":"2026-02-25T07:58:31.423824","exit_ts":"2026-02-25T07:58:50.225812","duration_s":18.8,"asset":"BTC","side":"UP","entry_ask":0.77,"gap_pts":-10.22,"secs_left":88.6,"pnl":-0.571429,"outcome":"LOSS","capital_after":101.8306,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0131","entry_ts":"2026-02-25T08:03:56.960273","exit_ts":"2026-02-25T08:04:36.736621","duration_s":39.8,"asset":"SOL","side":"DOWN","entry_ask":0.91,"gap_pts":-4.97,"secs_left":63.0,"pnl":0.098901,"outcome":"WIN","capital_after":101.9295,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0132","entry_ts":"2026-02-25T08:08:48.018715","exit_ts":"2026-02-25T08:08:55.511871","duration_s":7.5,"asset":"SOL","side":"UP","entry_ask":0.68,"gap_pts":-14.7,"secs_left":72.0,"pnl":-0.529412,"outcome":"LOSS","capital_after":101.4001,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0133","entry_ts":"2026-02-25T08:48:38.149995","exit_ts":"2026-02-25T08:49:02.143504","duration_s":24.0,"asset":"SOL","side":"UP","entry_ask":0.65,"gap_pts":-16.43,"secs_left":81.9,"pnl":-0.661538,"outcome":"LOSS","capital_after":100.7386,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0134","entry_ts":"2026-02-25T08:53:36.846379","exit_ts":"2026-02-25T08:54:34.620547","duration_s":57.8,"asset":"SOL","side":"UP","entry_ask":0.9,"gap_pts":-4.5,"secs_left":83.2,"pnl":0.111111,"outcome":"WIN","capital_after":100.8497,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0135","entry_ts":"2026-02-25T08:58:31.471136","exit_ts":"2026-02-25T08:59:40.058950","duration_s":68.6,"asset":"ETH","side":"DOWN","entry_ask":0.69,"gap_pts":-11.72,"secs_left":88.5,"pnl":0.449275,"outcome":"WIN","capital_after":101.299,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0136","entry_ts":"2026-02-25T09:04:14.326923","exit_ts":"2026-02-25T09:04:39.571704","duration_s":25.2,"asset":"SOL","side":"UP","entry_ask":0.89,"gap_pts":-4.51,"secs_left":45.7,"pnl":0.123596,"outcome":"WIN","capital_after":101.4226,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0137","entry_ts":"2026-02-25T09:08:31.493727","exit_ts":"2026-02-25T09:09:45.130854","duration_s":73.6,"asset":"SOL","side":"DOWN","entry_ask":0.88,"gap_pts":-8.09,"secs_left":88.5,"pnl":0.136364,"outcome":"WIN","capital_after":101.5589,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0138","entry_ts":"2026-02-25T09:13:31.427418","exit_ts":"2026-02-25T09:14:50.988957","duration_s":79.6,"asset":"SOL","side":"UP","entry_ask":0.88,"gap_pts":-6.53,"secs_left":88.6,"pnl":-0.840909,"outcome":"LOSS","capital_after":100.718,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0139","entry_ts":"2026-02-25T09:28:46.857748","exit_ts":"2026-02-25T09:29:54.533100","duration_s":67.7,"asset":"SOL","side":"DOWN","entry_ask":0.65,"gap_pts":-12.07,"secs_left":73.1,"pnl":-0.492308,"outcome":"LOSS","capital_after":100.2257,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0140","entry_ts":"2026-02-25T09:33:31.520501","exit_ts":"2026-02-25T09:34:45.982998","duration_s":74.5,"asset":"SOL","side":"DOWN","entry_ask":0.79,"gap_pts":-6.97,"secs_left":88.5,"pnl":-0.594937,"outcome":"LOSS","capital_after":99.6308,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0141","entry_ts":"2026-02-25T09:48:44.486866","exit_ts":"2026-02-25T09:49:41.024249","duration_s":56.5,"asset":"ETH","side":"UP","entry_ask":0.85,"gap_pts":-7.45,"secs_left":75.5,"pnl":0.176471,"outcome":"WIN","capital_after":99.8073,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0142","entry_ts":"2026-02-25T09:53:31.445270","exit_ts":"2026-02-25T09:54:16.839940","duration_s":45.4,"asset":"BTC","side":"UP","entry_ask":0.86,"gap_pts":-7.79,"secs_left":88.6,"pnl":-0.616279,"outcome":"LOSS","capital_after":99.191,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0143","entry_ts":"2026-02-25T09:58:36.627484","exit_ts":"2026-02-25T09:58:46.631013","duration_s":10.0,"asset":"ETH","side":"UP","entry_ask":0.71,"gap_pts":-13.61,"secs_left":83.4,"pnl":-0.605634,"outcome":"LOSS","capital_after":98.5853,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0144","entry_ts":"2026-02-25T10:08:56.986070","exit_ts":"2026-02-25T10:09:39.808475","duration_s":42.8,"asset":"BTC","side":"UP","entry_ask":0.74,"gap_pts":-13.19,"secs_left":63.0,"pnl":0.351351,"outcome":"WIN","capital_after":98.9367,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0145","entry_ts":"2026-02-25T10:13:32.933127","exit_ts":"2026-02-25T10:14:02.187766","duration_s":29.3,"asset":"SOL","side":"DOWN","entry_ask":0.85,"gap_pts":-6.03,"secs_left":87.1,"pnl":-0.705882,"outcome":"LOSS","capital_after":98.2308,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0146","entry_ts":"2026-02-25T10:19:17.960792","exit_ts":"2026-02-25T10:19:27.754089","duration_s":9.8,"asset":"ETH","side":"DOWN","entry_ask":0.75,"gap_pts":-20.09,"secs_left":42.0,"pnl":-0.693333,"outcome":"LOSS","capital_after":97.5375,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0147","entry_ts":"2026-02-25T10:23:31.605207","exit_ts":"2026-02-25T10:24:14.317505","duration_s":42.7,"asset":"SOL","side":"DOWN","entry_ask":0.87,"gap_pts":-8.39,"secs_left":88.4,"pnl":0.149425,"outcome":"WIN","capital_after":97.6869,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0148","entry_ts":"2026-02-25T10:33:50.518797","exit_ts":"2026-02-25T10:34:45.208443","duration_s":54.7,"asset":"BTC","side":"DOWN","entry_ask":0.68,"gap_pts":-11.3,"secs_left":69.5,"pnl":-0.617647,"outcome":"LOSS","capital_after":97.0693,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0149","entry_ts":"2026-02-25T10:38:36.708291","exit_ts":"2026-02-25T10:39:40.684111","duration_s":64.0,"asset":"BTC","side":"UP","entry_ask":0.71,"gap_pts":-11.9,"secs_left":83.3,"pnl":0.408451,"outcome":"WIN","capital_after":97.4777,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0150","entry_ts":"2026-02-25T10:48:48.852241","exit_ts":"2026-02-25T10:49:50.021218","duration_s":61.2,"asset":"ETH","side":"UP","entry_ask":0.75,"gap_pts":-13.87,"secs_left":71.1,"pnl":0.333333,"outcome":"WIN","capital_after":97.811,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0151","entry_ts":"2026-02-25T10:58:31.527442","exit_ts":"2026-02-25T10:59:57.918791","duration_s":86.4,"asset":"BTC","side":"DOWN","entry_ask":0.89,"gap_pts":-5.8,"secs_left":88.5,"pnl":0.123596,"outcome":"WIN","capital_after":97.9346,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0152","entry_ts":"2026-02-25T11:03:31.555190","exit_ts":"2026-02-25T11:04:27.068036","duration_s":55.5,"asset":"ETH","side":"DOWN","entry_ask":0.84,"gap_pts":-6.16,"secs_left":88.4,"pnl":-0.666667,"outcome":"LOSS","capital_after":97.268,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0153","entry_ts":"2026-02-25T11:13:32.249772","exit_ts":"2026-02-25T11:14:31.983651","duration_s":59.7,"asset":"BTC","side":"UP","entry_ask":0.66,"gap_pts":-17.38,"secs_left":87.8,"pnl":-0.545454,"outcome":"LOSS","capital_after":96.7225,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0154","entry_ts":"2026-02-25T11:28:38.975061","exit_ts":"2026-02-25T11:29:54.171219","duration_s":75.2,"asset":"ETH","side":"UP","entry_ask":0.65,"gap_pts":-13.94,"secs_left":81.0,"pnl":0.538462,"outcome":"WIN","capital_after":97.261,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0155","entry_ts":"2026-02-25T11:33:31.638082","exit_ts":"2026-02-25T11:34:46.851333","duration_s":75.2,"asset":"BTC","side":"UP","entry_ask":0.67,"gap_pts":-15.17,"secs_left":88.4,"pnl":0.492537,"outcome":"WIN","capital_after":97.7535,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0156","entry_ts":"2026-02-25T11:43:31.582077","exit_ts":"2026-02-25T11:44:55.216127","duration_s":83.6,"asset":"SOL","side":"DOWN","entry_ask":0.82,"gap_pts":-11.25,"secs_left":88.4,"pnl":0.219512,"outcome":"WIN","capital_after":97.973,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0157","entry_ts":"2026-02-25T11:58:31.514929","exit_ts":"2026-02-25T11:58:59.266471","duration_s":27.8,"asset":"SOL","side":"DOWN","entry_ask":0.65,"gap_pts":-15.07,"secs_left":88.5,"pnl":-0.584615,"outcome":"LOSS","capital_after":97.3884,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0158","entry_ts":"2026-02-25T12:04:09.585206","exit_ts":"2026-02-25T12:04:56.300707","duration_s":46.7,"asset":"BTC","side":"DOWN","entry_ask":0.65,"gap_pts":-18.51,"secs_left":50.4,"pnl":0.538462,"outcome":"WIN","capital_after":97.9269,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0159","entry_ts":"2026-02-25T12:18:53.824427","exit_ts":"2026-02-25T12:19:14.721213","duration_s":20.9,"asset":"ETH","side":"UP","entry_ask":0.67,"gap_pts":-11.52,"secs_left":66.2,"pnl":0.492537,"outcome":"WIN","capital_after":98.4194,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0160","entry_ts":"2026-02-25T12:23:58.337121","exit_ts":"2026-02-25T12:24:39.073782","duration_s":40.7,"asset":"ETH","side":"UP","entry_ask":0.94,"gap_pts":-4.24,"secs_left":61.7,"pnl":-0.797872,"outcome":"LOSS","capital_after":97.6215,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0161","entry_ts":"2026-02-25T12:28:41.687160","exit_ts":"2026-02-25T12:29:56.687242","duration_s":75.0,"asset":"BTC","side":"UP","entry_ask":0.65,"gap_pts":-13.25,"secs_left":78.3,"pnl":0.538462,"outcome":"WIN","capital_after":98.16,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"SOL"},{"id":"T0162","entry_ts":"2026-02-25T13:08:31.662446","exit_ts":"2026-02-25T13:09:03.791205","duration_s":32.1,"asset":"SOL","side":"UP","entry_ask":0.68,"gap_pts":-14.56,"secs_left":88.3,"pnl":-0.514706,"outcome":"LOSS","capital_after":97.6453,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0163","entry_ts":"2026-02-25T13:18:31.609560","exit_ts":"2026-02-25T13:20:00.768955","duration_s":89.2,"asset":"ETH","side":"UP","entry_ask":0.7,"gap_pts":-9.32,"secs_left":88.4,"pnl":0.428571,"outcome":"WIN","capital_after":98.0739,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0164","entry_ts":"2026-02-25T13:23:31.587288","exit_ts":"2026-02-25T13:24:15.042119","duration_s":43.5,"asset":"BTC","side":"UP","entry_ask":0.67,"gap_pts":-14.98,"secs_left":88.4,"pnl":-0.537314,"outcome":"LOSS","capital_after":97.5366,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"SOL"},{"id":"T0165","entry_ts":"2026-02-25T13:34:03.671449","exit_ts":"2026-02-25T13:34:37.476145","duration_s":33.8,"asset":"ETH","side":"DOWN","entry_ask":0.78,"gap_pts":-4.51,"secs_left":56.3,"pnl":-0.576923,"outcome":"LOSS","capital_after":96.9596,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0166","entry_ts":"2026-02-25T13:38:31.754236","exit_ts":"2026-02-25T13:39:33.333562","duration_s":61.6,"asset":"ETH","side":"UP","entry_ask":0.9,"gap_pts":-5.3,"secs_left":88.2,"pnl":0.111111,"outcome":"WIN","capital_after":97.0707,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0167","entry_ts":"2026-02-25T13:44:21.719307","exit_ts":"2026-02-25T13:44:54.091228","duration_s":32.4,"asset":"ETH","side":"UP","entry_ask":0.72,"gap_pts":-15.07,"secs_left":38.3,"pnl":-0.625,"outcome":"LOSS","capital_after":96.4457,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0168","entry_ts":"2026-02-25T14:08:31.816636","exit_ts":"2026-02-25T14:09:15.669786","duration_s":43.9,"asset":"ETH","side":"UP","entry_ask":0.66,"gap_pts":-16.22,"secs_left":88.2,"pnl":-0.545454,"outcome":"LOSS","capital_after":95.9003,"exit_type":"STOP_LOSS","peer1":"SOL","peer2":"BTC"},{"id":"T0169","entry_ts":"2026-02-25T14:13:35.754834","exit_ts":"2026-02-25T14:14:07.157907","duration_s":31.4,"asset":"SOL","side":"UP","entry_ask":0.65,"gap_pts":-14.73,"secs_left":84.2,"pnl":-0.584615,"outcome":"LOSS","capital_after":95.3157,"exit_type":"STOP_LOSS","peer1":"ETH","peer2":"BTC"},{"id":"T0170","entry_ts":"2026-02-25T14:23:44.127556","exit_ts":"2026-02-25T14:24:10.191003","duration_s":26.1,"asset":"SOL","side":"UP","entry_ask":0.9,"gap_pts":-4.07,"secs_left":75.9,"pnl":0.111111,"outcome":"WIN","capital_after":95.4268,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0171","entry_ts":"2026-02-25T14:38:31.732268","exit_ts":"2026-02-25T14:39:27.379126","duration_s":55.6,"asset":"SOL","side":"DOWN","entry_ask":0.83,"gap_pts":-8.89,"secs_left":88.3,"pnl":0.204819,"outcome":"WIN","capital_after":95.6316,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0172","entry_ts":"2026-02-25T14:43:32.665841","exit_ts":"2026-02-25T14:44:00.843706","duration_s":28.2,"asset":"SOL","side":"UP","entry_ask":0.66,"gap_pts":-11.94,"secs_left":87.3,"pnl":0.515152,"outcome":"WIN","capital_after":96.1468,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0173","entry_ts":"2026-02-25T14:54:19.217728","exit_ts":"2026-02-25T14:54:49.864661","duration_s":30.6,"asset":"ETH","side":"DOWN","entry_ask":0.69,"gap_pts":-12.67,"secs_left":40.8,"pnl":0.449275,"outcome":"WIN","capital_after":96.596,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"},{"id":"T0174","entry_ts":"2026-02-25T14:58:31.792256","exit_ts":"2026-02-25T14:59:36.963571","duration_s":65.2,"asset":"SOL","side":"UP","entry_ask":0.93,"gap_pts":-4.87,"secs_left":88.2,"pnl":0.075269,"outcome":"WIN","capital_after":96.6713,"exit_type":"RESOLUTION","peer1":"ETH","peer2":"BTC"},{"id":"T0175","entry_ts":"2026-02-25T15:08:31.734262","exit_ts":"2026-02-25T15:08:54.809089","duration_s":23.1,"asset":"ETH","side":"DOWN","entry_ask":0.94,"gap_pts":-4.24,"secs_left":88.3,"pnl":0.06383,"outcome":"WIN","capital_after":96.7351,"exit_type":"RESOLUTION","peer1":"SOL","peer2":"BTC"}];

// ═══════════════════════════════════════
//  STATE
// ═══════════════════════════════════════
let currentFilter = 'all';
let sortKey = 'id';
let sortAsc = true;
let charts = {};

function isGold(t) {
  return t.secs_left >= 60 && t.secs_left <= 85 && t.gap_pts >= -14 && t.gap_pts <= -5;
}

function getFiltered() {
  return ALL_TRADES.filter(t => {
    if (currentFilter === 'gold') return isGold(t);
    if (currentFilter === 'eth') return t.asset === 'ETH';
    if (currentFilter === 'sol') return t.asset === 'SOL';
    if (currentFilter === 'btc') return t.asset === 'BTC';
    if (currentFilter === 'win') return t.outcome === 'WIN';
    if (currentFilter === 'loss') return t.outcome === 'LOSS';
    return true;
  });
}

function setFilter(f) {
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => {
    b.classList.remove('active', 'active-gold');
  });
  const idx = ['all','gold','eth','sol','btc','win','loss'].indexOf(f);
  const btns = document.querySelectorAll('.filter-btn');
  if (f === 'gold') btns[1].classList.add('active-gold');
  else btns[idx].classList.add('active');
  renderAll();
}

// ═══════════════════════════════════════
//  STATS
// ═══════════════════════════════════════
function calcStats(trades) {
  const n = trades.length;
  if (n === 0) return null;
  const wins = trades.filter(t => t.outcome === 'WIN');
  const losses = trades.filter(t => t.outcome === 'LOSS');
  const pnl = trades.reduce((s, t) => s + t.pnl, 0);
  const pnlW = wins.reduce((s, t) => s + t.pnl, 0);
  const pnlL = losses.reduce((s, t) => s + t.pnl, 0);
  const wr = wins.length / n * 100;
  const pf = Math.abs(pnlL) > 0 ? pnlW / Math.abs(pnlL) : 999;
  const avgW = wins.length > 0 ? pnlW / wins.length : 0;
  const avgL = losses.length > 0 ? pnlL / losses.length : 0;

  // Max drawdown sobre el subconjunto filtrado
  let cap = 100, peak = 100, maxDD = 0;
  trades.forEach(t => {
    cap += t.pnl;
    if (cap > peak) peak = cap;
    const dd = peak - cap;
    if (dd > maxDD) maxDD = dd;
  });

  // Max consecutive wins/losses
  let maxStreak = 0, curStreak = 0, lastOut = null;
  let maxLStreak = 0, curLStreak = 0;
  trades.forEach(t => {
    if (t.outcome === 'WIN') {
      curStreak++; curLStreak = 0;
      if (curStreak > maxStreak) maxStreak = curStreak;
    } else {
      curLStreak++; curStreak = 0;
      if (curLStreak > maxLStreak) maxLStreak = curLStreak;
    }
  });

  return { n, wins: wins.length, losses: losses.length, pnl, pnlW, pnlL, wr, pf, avgW, avgL, maxDD, maxStreak, maxLStreak };
}

// ═══════════════════════════════════════
//  KPIs
// ═══════════════════════════════════════
function renderKPIs(st) {
  const g = document.getElementById('kpi-grid');
  if (!st) { g.innerHTML = '<div class="no-data">Sin datos</div>'; return; }
  const pnlClass = st.pnl >= 0 ? '' : ' red';
  const pnlSign = st.pnl >= 0 ? '+' : '';
  const wr = st.wr.toFixed(1);
  const pfClass = st.pf >= 2 ? '' : st.pf >= 1.3 ? ' gold' : ' red';

  g.innerHTML = `
    <div class="kpi"><div class="kpi-label">Capital Final</div><div class="kpi-value neutral">$${(100+st.pnl).toFixed(2)}</div><div class="kpi-sub">inicio $100.00</div></div>
    <div class="kpi${pnlClass}"><div class="kpi-label">PnL Total</div><div class="kpi-value${pnlClass}">${pnlSign}$${st.pnl.toFixed(4)}</div><div class="kpi-sub">${st.n} trades</div></div>
    <div class="kpi${wr>=75?' ':wr>=60?' gold':' red'}"><div class="kpi-label">Win Rate</div><div class="kpi-value${wr>=75?' ':wr>=60?' gold':' red'}">${wr}%</div><div class="kpi-sub">${st.wins}W · ${st.losses}L</div></div>
    <div class="kpi${pfClass}"><div class="kpi-label">Profit Factor</div><div class="kpi-value${pfClass}">${st.pf > 10 ? '∞' : st.pf.toFixed(2)}</div><div class="kpi-sub">PnL+/PnL-</div></div>
    <div class="kpi red"><div class="kpi-label">Max Drawdown</div><div class="kpi-value red">-$${st.maxDD.toFixed(4)}</div><div class="kpi-sub">peak-to-trough</div></div>
    <div class="kpi"><div class="kpi-label">Avg Win</div><div class="kpi-value">+$${st.avgW.toFixed(4)}</div><div class="kpi-sub">por trade ganado</div></div>
    <div class="kpi red"><div class="kpi-label">Avg Loss</div><div class="kpi-value red">$${st.avgL.toFixed(4)}</div><div class="kpi-sub">por trade perdido</div></div>
    <div class="kpi purple"><div class="kpi-label">Max Win Streak</div><div class="kpi-value purple">${st.maxStreak}</div><div class="kpi-sub">racha máx victorias</div></div>
  `;
}

// ═══════════════════════════════════════
//  EQUITY CHART
// ═══════════════════════════════════════
function renderEquity(trades) {
  const ctx = document.getElementById('equityChart').getContext('2d');
  if (charts.equity) charts.equity.destroy();

  let cap = 100;
  const labels = ['0'];
  const data = [100];
  const colors = [];

  trades.forEach((t, i) => {
    cap += t.pnl;
    labels.push(t.id);
    data.push(parseFloat(cap.toFixed(4)));
    colors.push(t.pnl >= 0 ? 'rgba(0,245,196,0.8)' : 'rgba(255,59,107,0.8)');
  });

  const isGoldFilter = currentFilter === 'gold';
  document.getElementById('equity-label').textContent = `$100 → $${data[data.length-1].toFixed(2)}`;

  charts.equity = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data,
        borderColor: 'rgba(0,245,196,0.9)',
        borderWidth: 1.5,
        pointRadius: 0,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgba(0,245,196,1)',
        fill: true,
        backgroundColor: (ctx) => {
          const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 200);
          gradient.addColorStop(0, 'rgba(0,245,196,0.15)');
          gradient.addColorStop(1, 'rgba(0,245,196,0.01)');
          return gradient;
        },
        tension: 0.3,
      }]
    },
    options: {
      responsive: true,
      animation: { duration: 600, easing: 'easeOutCubic' },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f1729',
          borderColor: '#1a2540',
          borderWidth: 1,
          titleColor: '#4a5568',
          bodyColor: '#e2e8f0',
          callbacks: {
            label: (ctx) => `Capital: $${ctx.parsed.y.toFixed(4)}`
          }
        }
      },
      scales: {
        x: {
          display: false,
          grid: { display: false }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            color: '#4a5568',
            font: { family: 'Space Mono', size: 10 },
            callback: v => '$' + v.toFixed(1)
          },
          border: { color: '#1a2540' }
        }
      }
    }
  });
}

// ═══════════════════════════════════════
//  DONUT
// ═══════════════════════════════════════
function renderDonut(st) {
  const ctx = document.getElementById('donutChart').getContext('2d');
  if (charts.donut) charts.donut.destroy();
  if (!st) return;

  document.getElementById('wr-label').textContent = ` ${st.wr.toFixed(1)}%`;

  charts.donut = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['WIN', 'LOSS'],
      datasets: [{
        data: [st.wins, st.losses],
        backgroundColor: ['rgba(0,245,196,0.85)', 'rgba(255,59,107,0.85)'],
        borderColor: ['rgba(0,245,196,0.3)', 'rgba(255,59,107,0.3)'],
        borderWidth: 1,
        hoverOffset: 6,
      }]
    },
    options: {
      responsive: true,
      cutout: '70%',
      animation: { duration: 800, easing: 'easeOutQuart' },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#4a5568',
            font: { family: 'Space Mono', size: 10 },
            padding: 12,
            boxWidth: 10,
          }
        },
        tooltip: {
          backgroundColor: '#0f1729',
          borderColor: '#1a2540',
          borderWidth: 1,
          bodyColor: '#e2e8f0',
        }
      }
    },
    plugins: [{
      id: 'centerText',
      afterDraw(chart) {
        const { ctx, chartArea: { width, height, top } } = chart;
        ctx.save();
        ctx.font = "bold 22px 'Syne', sans-serif";
        ctx.fillStyle = '#00f5c4';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const cx = width / 2;
        const cy = top + height / 2;
        ctx.fillText(st.wr.toFixed(1) + '%', cx, cy - 8);
        ctx.font = "11px 'Space Mono', monospace";
        ctx.fillStyle = '#4a5568';
        ctx.fillText('win rate', cx, cy + 14);
        ctx.restore();
      }
    }]
  });
}

// ═══════════════════════════════════════
//  HEATMAP
// ═══════════════════════════════════════
function renderHeatmap(trades) {
  const wrap = document.getElementById('heatmap');
  wrap.innerHTML = '';
  trades.forEach((t, i) => {
    const cell = document.createElement('div');
    cell.className = 'hm-cell';
    const intensity = Math.min(1, Math.abs(t.pnl) / 0.6);
    if (t.outcome === 'WIN') {
      const g = Math.round(180 + intensity * 75);
      cell.style.background = `rgba(0,${g},${Math.round(150+intensity*100)},${0.5+intensity*0.4})`;
    } else {
      const r = Math.round(180 + intensity * 75);
      cell.style.background = `rgba(${r},${Math.round(30+intensity*40)},80,${0.5+intensity*0.4})`;
    }
    const hour = new Date(t.entry_ts).getHours();
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = `${t.id} · ${t.asset} ${t.side} · ${t.pnl >= 0 ? '+' : ''}$${t.pnl.toFixed(3)} · ${hour}h`;
    cell.appendChild(tooltip);
    wrap.appendChild(cell);
  });
}

// ═══════════════════════════════════════
//  GAP DISTRIBUTION
// ═══════════════════════════════════════
function renderGapDist(trades) {
  const wrap = document.getElementById('gapDist');
  const buckets = [
    { label: '-4 a -6', min: -6, max: -4 },
    { label: '-6 a -8', min: -8, max: -6 },
    { label: '-8 a -10', min: -10, max: -8 },
    { label: '-10 a -12', min: -12, max: -10 },
    { label: '-12 a -14', min: -14, max: -12 },
    { label: '<-14', min: -99, max: -14 },
  ];
  const results = buckets.map(b => {
    const ts = trades.filter(t => t.gap_pts >= b.min && t.gap_pts < b.max);
    const wins = ts.filter(t => t.outcome === 'WIN').length;
    return { ...b, total: ts.length, wins, losses: ts.length - wins };
  });
  const maxTotal = Math.max(...results.map(r => r.total), 1);

  wrap.innerHTML = results.map(r => {
    const wPct = r.total > 0 ? (r.wins / r.total * 100).toFixed(0) : 0;
    return `
    <div class="dist-row">
      <div class="dist-label">${r.label}</div>
      <div class="dist-bar-bg">
        <div class="dist-bar-fill" style="width:${r.wins/maxTotal*100}%; background:rgba(0,245,196,0.7)"></div>
        <div class="dist-bar-fill" style="width:${r.losses/maxTotal*100}%; background:rgba(255,59,107,0.7); margin-top:1px"></div>
      </div>
      <div class="dist-count">${r.total}</div>
      <div style="font-size:9px; color:${wPct>=70?'var(--win)':wPct>=50?'var(--gold)':'var(--loss)'}; width:30px">${wPct}%W</div>
    </div>`;
  }).join('');
}

// ═══════════════════════════════════════
//  ASSET BAR
// ═══════════════════════════════════════
function renderAssetBar(trades) {
  const ctx = document.getElementById('assetBar').getContext('2d');
  if (charts.assetBar) charts.assetBar.destroy();

  const assets = ['ETH', 'SOL', 'BTC'];
  const pnls = assets.map(a => {
    const ts = trades.filter(t => t.asset === a);
    return ts.reduce((s, t) => s + t.pnl, 0);
  });
  const colors = pnls.map(p => p >= 0 ? 'rgba(0,245,196,0.8)' : 'rgba(255,59,107,0.8)');

  charts.assetBar = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: assets,
      datasets: [{
        data: pnls,
        backgroundColor: colors,
        borderColor: colors.map(c => c.replace('0.8', '1')),
        borderWidth: 1,
        borderRadius: 2,
      }]
    },
    options: {
      responsive: true,
      animation: { duration: 600 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f1729',
          borderColor: '#1a2540',
          borderWidth: 1,
          bodyColor: '#e2e8f0',
          callbacks: { label: c => `PnL: ${c.parsed.y >= 0 ? '+' : ''}$${c.parsed.y.toFixed(4)}` }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#4a5568', font: { family: 'Space Mono', size: 11 } },
          border: { color: '#1a2540' }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#4a5568', font: { family: 'Space Mono', size: 10 }, callback: v => '$'+v.toFixed(2) },
          border: { color: '#1a2540' }
        }
      }
    }
  });
}

// ═══════════════════════════════════════
//  SCATTER
// ═══════════════════════════════════════
function renderScatter(trades) {
  const ctx = document.getElementById('scatterChart').getContext('2d');
  if (charts.scatter) charts.scatter.destroy();

  const winsData = trades.filter(t => t.outcome === 'WIN').map(t => ({ x: t.gap_pts, y: t.pnl, id: t.id }));
  const lossData = trades.filter(t => t.outcome === 'LOSS').map(t => ({ x: t.gap_pts, y: t.pnl, id: t.id }));
  const goldData = trades.filter(t => isGold(t)).map(t => ({ x: t.gap_pts, y: t.pnl }));

  charts.scatter = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: 'WIN',
          data: winsData,
          backgroundColor: 'rgba(0,245,196,0.6)',
          borderColor: 'rgba(0,245,196,0.8)',
          borderWidth: 1,
          pointRadius: 4,
          pointHoverRadius: 6,
        },
        {
          label: 'LOSS',
          data: lossData,
          backgroundColor: 'rgba(255,59,107,0.6)',
          borderColor: 'rgba(255,59,107,0.8)',
          borderWidth: 1,
          pointRadius: 4,
          pointHoverRadius: 6,
        }
      ]
    },
    options: {
      responsive: true,
      animation: { duration: 500 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f1729',
          borderColor: '#1a2540',
          borderWidth: 1,
          bodyColor: '#e2e8f0',
          callbacks: {
            label: c => `Gap: ${c.parsed.x.toFixed(1)}pts  PnL: ${c.parsed.y >= 0 ? '+' : ''}$${c.parsed.y.toFixed(3)}`
          }
        }
      },
      scales: {
        x: {
          title: { display: true, text: 'Gap (pts)', color: '#4a5568', font: { family: 'Space Mono', size: 10 } },
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#4a5568', font: { family: 'Space Mono', size: 10 } },
          border: { color: '#1a2540' }
        },
        y: {
          title: { display: true, text: 'PnL ($)', color: '#4a5568', font: { family: 'Space Mono', size: 10 } },
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#4a5568', font: { family: 'Space Mono', size: 10 }, callback: v => '$'+v.toFixed(2) },
          border: { color: '#1a2540' }
        }
      }
    },
    plugins: [{
      id: 'goldZone',
      beforeDraw(chart) {
        const { ctx, scales: { x, y } } = chart;
        if (!x || !y) return;
        const x1 = x.getPixelForValue(-14);
        const x2 = x.getPixelForValue(-5);
        ctx.save();
        ctx.fillStyle = 'rgba(255,209,102,0.06)';
        ctx.fillRect(x1, y.top, x2 - x1, y.bottom - y.top);
        ctx.strokeStyle = 'rgba(255,209,102,0.2)';
        ctx.setLineDash([4, 4]);
        ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(x1, y.top); ctx.lineTo(x1, y.bottom); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x2, y.top); ctx.lineTo(x2, y.bottom); ctx.stroke();
        ctx.restore();
      }
    }]
  });
}

// ═══════════════════════════════════════
//  SECS CHART
// ═══════════════════════════════════════
function renderSecs(trades) {
  const ctx = document.getElementById('secsChart').getContext('2d');
  if (charts.secs) charts.secs.destroy();

  const buckets = [[30,40],[40,50],[50,60],[60,70],[70,80],[80,90]];
  const labels = buckets.map(b => `${b[0]}-${b[1]}s`);
  const winsArr = buckets.map(b => trades.filter(t => t.secs_left >= b[0] && t.secs_left < b[1] && t.outcome === 'WIN').length);
  const lossArr = buckets.map(b => trades.filter(t => t.secs_left >= b[0] && t.secs_left < b[1] && t.outcome === 'LOSS').length);

  charts.secs = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'WIN', data: winsArr, backgroundColor: 'rgba(0,245,196,0.75)', borderColor: 'rgba(0,245,196,1)', borderWidth: 1, borderRadius: 2, stack: 'a' },
        { label: 'LOSS', data: lossArr, backgroundColor: 'rgba(255,59,107,0.75)', borderColor: 'rgba(255,59,107,1)', borderWidth: 1, borderRadius: 2, stack: 'a' }
      ]
    },
    options: {
      responsive: true,
      animation: { duration: 600 },
      plugins: {
        legend: {
          labels: { color: '#4a5568', font: { family: 'Space Mono', size: 10 }, boxWidth: 10 }
        },
        tooltip: {
          backgroundColor: '#0f1729',
          borderColor: '#1a2540',
          borderWidth: 1,
          bodyColor: '#e2e8f0',
        }
      },
      scales: {
        x: {
          stacked: true,
          grid: { display: false },
          ticks: { color: '#4a5568', font: { family: 'Space Mono', size: 9 } },
          border: { color: '#1a2540' }
        },
        y: {
          stacked: true,
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { color: '#4a5568', font: { family: 'Space Mono', size: 10 } },
          border: { color: '#1a2540' }
        }
      }
    },
    plugins: [{
      id: 'goldBand',
      beforeDraw(chart) {
        const { ctx, scales: { x, y } } = chart;
        if (!x || !y) return;
        const x1 = x.getPixelForValue(2.5);
        const x2 = x.getPixelForValue(4.5);
        ctx.save();
        ctx.fillStyle = 'rgba(255,209,102,0.08)';
        ctx.fillRect(x1, y.top, x2 - x1, y.bottom - y.top);
        ctx.restore();
      }
    }]
  });
}

// ═══════════════════════════════════════
//  STREAK VISUAL
// ═══════════════════════════════════════
function renderStreak(trades, st) {
  const wrap = document.getElementById('streakBars');
  wrap.innerHTML = '';
  trades.forEach(t => {
    const bar = document.createElement('div');
    bar.className = 'streak-bar';
    const h = Math.min(60, 8 + Math.abs(t.pnl) / 0.6 * 50);
    bar.style.height = h + 'px';
    bar.style.background = t.outcome === 'WIN'
      ? `rgba(0,245,196,${0.4 + Math.abs(t.pnl)/0.6 * 0.5})`
      : `rgba(255,59,107,${0.4 + Math.abs(t.pnl)/0.6 * 0.5})`;
    bar.style.alignSelf = 'flex-end';
    bar.title = `${t.id} · ${t.outcome} · $${t.pnl.toFixed(3)}`;
    wrap.appendChild(bar);
  });
  if (st) {
    document.getElementById('streak-label').textContent =
      `${trades.length} trades — max racha WIN: ${st.maxStreak} · max racha LOSS: ${st.maxLStreak}`;
  }
}

// ═══════════════════════════════════════
//  TABLE
// ═══════════════════════════════════════
function sortTable(key) {
  if (sortKey === key) sortAsc = !sortAsc;
  else { sortKey = key; sortAsc = true; }
  document.querySelectorAll('thead th').forEach(th => th.classList.remove('sorted'));
  renderTable(getFiltered());
}

function renderTable(trades) {
  const sorted = [...trades].sort((a, b) => {
    let va = a[sortKey], vb = b[sortKey];
    if (typeof va === 'string') return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
    return sortAsc ? va - vb : vb - va;
  });

  document.getElementById('table-count').textContent = `${sorted.length} trades`;

  const body = document.getElementById('tableBody');
  body.innerHTML = sorted.map(t => {
    const ts = new Date(t.entry_ts);
    const timeStr = ts.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const dateStr = ts.toLocaleDateString('es-CL', { day: '2-digit', month: '2-digit' });
    const assetBadge = `<span class="badge badge-${t.asset.toLowerCase()}">${t.asset}</span>`;
    const sideBadge = `<span class="badge badge-${t.side.toLowerCase()}">${t.side}</span>`;
    const outBadge = `<span class="badge badge-${t.outcome.toLowerCase()}">${t.outcome}</span>`;
    const exitBadge = `<span class="badge badge-${t.exit_type === 'STOP_LOSS' ? 'sl' : 'res'}">${t.exit_type === 'STOP_LOSS' ? 'SL' : 'RES'}</span>`;
    const goldMark = isGold(t) ? '<span style="color:var(--gold);margin-left:4px">★</span>' : '';
    return `
      <tr class="${t.outcome === 'WIN' ? 'win-row' : 'loss-row'}">
        <td>${t.id}${goldMark}</td>
        <td><span style="color:var(--muted)">${dateStr}</span> ${timeStr}</td>
        <td>${assetBadge}</td>
        <td>${sideBadge}</td>
        <td>${t.entry_ask.toFixed(2)}</td>
        <td style="color:var(--muted)">${t.gap_pts.toFixed(2)}</td>
        <td>${t.secs_left.toFixed(0)}s</td>
        <td class="${t.pnl >= 0 ? 'pnl-pos' : 'pnl-neg'}">${t.pnl >= 0 ? '+' : ''}$${t.pnl.toFixed(4)}</td>
        <td>${outBadge}</td>
        <td>${exitBadge}</td>
        <td style="color:var(--muted)">${t.duration_s.toFixed(0)}s</td>
      </tr>`;
  }).join('');
}

// ═══════════════════════════════════════
//  RENDER ALL
// ═══════════════════════════════════════
function renderAll() {
  const trades = getFiltered();
  const st = calcStats(trades);
  renderKPIs(st);
  renderEquity(trades);
  renderDonut(st);
  renderHeatmap(trades);
  renderGapDist(trades);
  renderAssetBar(trades);
  renderScatter(trades);
  renderSecs(trades);
  renderStreak(trades, st);
  renderTable(trades);
}

// INIT
document.addEventListener('DOMContentLoaded', () => {
  renderAll();
  // Default to gold view after a beat
  setTimeout(() => setFilter('gold'), 800);
});
</script>
</body>
</html>
