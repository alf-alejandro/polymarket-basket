"""
basket.py — Backtesting EN VIVO de Divergencia Armónica ETH/SOL/BTC
Lee precios REALES del order book de Polymarket — SIN ejecutar órdenes reales.

LOGICA BINARIA CORRECTA:
  Los tokens de Polymarket resuelven en 0 o 1 (todo o nada).
  Cada entrada cuesta exactamente $1.00 (el 1% del capital de $100).
  Shares comprados = $1.00 / precio_ask

CAMBIOS v3:
  - Rutas en /data (volumen persistente Railway)
  - Dashboard Flask en hilo secundario (un solo servicio)
  - restore_state_from_csv() al arrancar
  - Resolución por Gamma API con reintentos (hasta 6x cada 5min)
  - CONSENSUS_FULL = 0.80 (ambos peers deben superar 0.80)
  - Solo entra con consenso FULL
  - Precio mínimo de entrada 0.65
  - Umbral de resolución por precio: 0.98 / 0.02
"""

import asyncio
import os
import sys
import time
import json
import csv
import logging
import threading
from collections import deque
from datetime import datetime

from strategy_core import (
    find_active_market,
    get_order_book_metrics,
    seconds_remaining,
    fetch_market_resolution,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("basket")

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ═══════════════════════════════════════════════════════
#  PARÁMETROS
# ═══════════════════════════════════════════════════════
POLL_INTERVAL        = 0.5
DIVERGENCE_THRESHOLD = 0.04
WAKE_UP_SECS         = 90
ENTRY_WINDOW_SECS    = 90
ENTRY_CLOSE_SECS     = 30   # no entrar en los últimos 30 segundos

CAPITAL_TOTAL        = 100.0
ENTRY_PCT            = 0.01
ENTRY_USD            = CAPITAL_TOTAL * ENTRY_PCT

RESOLVED_UP_THRESH   = 0.98
RESOLVED_DN_THRESH   = 0.02

CONSENSUS_FULL       = 0.80
CONSENSUS_SOFT       = 0.80

ENTRY_MIN_PRICE      = 0.65

STOP_LOSS_PRICE      = 0.33   # SL fijo: se activa si el bid cae a este precio

LOG_FILE   = os.environ.get("LOG_FILE",   "/data/basket_log.json")
CSV_FILE   = os.environ.get("CSV_FILE",   "/data/basket_trades.csv")
STATE_FILE = os.environ.get("STATE_FILE", "/data/state.json")

# ═══════════════════════════════════════════════════════
#  ESTADO DE LOS 3 MERCADOS
# ═══════════════════════════════════════════════════════
SYMBOLS = ["ETH", "SOL", "BTC"]

markets = {
    s: {
        "info":      None,
        "up_bid":    0.0, "up_ask": 0.0, "up_mid": 0.0,
        "dn_bid":    0.0, "dn_ask": 0.0, "dn_mid": 0.0,
        "time_left": "N/A",
        "error":     None,
    }
    for s in SYMBOLS
}

bt = {
    "harm_up":      0.0,
    "harm_dn":      0.0,
    "signal_asset": None,
    "signal_side":  None,
    "signal_div":   0.0,
    "entry_window": False,
    "position":     None,
    "pending_resolution": None,
    "traded_this_cycle": False,
    "capital":      CAPITAL_TOTAL,
    "total_pnl":    0.0,
    "peak_capital": CAPITAL_TOTAL,
    "max_drawdown": 0.0,
    "wins":         0,
    "losses":       0,
    "consensus":    "NONE",
    "skipped":      0,
    "trades":       [],
    "cycle":        0,
    "phase":        "DURMIENDO",
    "next_wake":    "N/A",
}

recent_events = deque(maxlen=50)

CSV_COLUMNS = [
    "trade_id", "entry_ts", "exit_ts", "duration_s",
    "asset", "side", "consensus",
    "entry_ask", "entry_bid", "entry_mid", "entry_usd", "shares",
    "secs_left_entry", "harm_entry", "gap_pts",
    "peer1_sym", "peer1_side_mid", "peer1_opp_mid",
    "peer2_sym", "peer2_side_mid", "peer2_opp_mid",
    "sl_price", "exit_type", "exit_price", "resolved", "binary_win",
    "pnl_usd", "pnl_pct_entry", "max_possible_win", "outcome",
    "capital_before", "capital_after", "cumulative_pnl", "trade_number",
]


# ═══════════════════════════════════════════════════════
#  UTILIDADES
# ═══════════════════════════════════════════════════════

def log_event(msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    recent_events.append(entry)
    log.info(msg)


def harmonic_mean(values: list) -> float:
    if not values or any(v <= 0 for v in values):
        return 0.0
    return len(values) / sum(1.0 / v for v in values)


def find_cheapest(mids: dict, h_avg: float):
    if h_avg == 0:
        return None, 0.0
    cheapest_name, cheapest_diff = None, 0.0
    for name, mid in mids.items():
        diff = mid - h_avg
        if diff < cheapest_diff:
            cheapest_diff, cheapest_name = diff, name
    return cheapest_name, cheapest_diff


def min_secs_remaining() -> float | None:
    result = None
    for sym in SYMBOLS:
        info = markets[sym]["info"]
        if info:
            secs = seconds_remaining(info)
            if secs is not None:
                result = secs if result is None else min(result, secs)
    return result


def update_drawdown():
    cap = bt["capital"]
    if cap > bt["peak_capital"]:
        bt["peak_capital"] = cap
    dd = bt["peak_capital"] - cap
    if dd > bt["max_drawdown"]:
        bt["max_drawdown"] = dd


# ═══════════════════════════════════════════════════════
#  ESCRITURA DE ESTADO PARA DASHBOARD
# ═══════════════════════════════════════════════════════

def write_state():
    total_trades = bt["wins"] + bt["losses"]
    win_rate = (bt["wins"] / total_trades * 100) if total_trades > 0 else 0.0
    roi = (bt["capital"] - CAPITAL_TOTAL) / CAPITAL_TOTAL * 100

    state = {
        "ts": datetime.now().isoformat(),
        "phase": bt["phase"],
        "cycle": bt["cycle"],
        "capital": round(bt["capital"], 4),
        "total_pnl": round(bt["total_pnl"], 4),
        "roi": round(roi, 2),
        "peak_capital": round(bt["peak_capital"], 4),
        "max_drawdown": round(bt["max_drawdown"], 4),
        "wins": bt["wins"],
        "losses": bt["losses"],
        "win_rate": round(win_rate, 1),
        "skipped": bt["skipped"],
        "consensus": bt["consensus"],
        "entry_window": bt["entry_window"],
        "next_wake": bt["next_wake"],
        "harm_up": round(bt["harm_up"], 4),
        "harm_dn": round(bt["harm_dn"], 4),
        "signal_asset": bt["signal_asset"],
        "signal_side": bt["signal_side"],
        "signal_div": round(bt["signal_div"], 4),
        "position": bt["position"],
        "pending_resolution": bt["pending_resolution"],
        "markets": {
            sym: {
                "up_mid": round(markets[sym]["up_mid"], 4),
                "dn_mid": round(markets[sym]["dn_mid"], 4),
                "up_ask": round(markets[sym]["up_ask"], 4),
                "dn_ask": round(markets[sym]["dn_ask"], 4),
                "time_left": markets[sym]["time_left"],
                "error": markets[sym]["error"],
            }
            for sym in SYMBOLS
        },
        "events": list(recent_events)[-30:],
        "recent_trades": bt["trades"][-10:],
    }
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        log.warning(f"write_state error: {e}")


# ═══════════════════════════════════════════════════════
#  RESTAURAR ESTADO DESDE CSV
# ═══════════════════════════════════════════════════════

def restore_state_from_csv():
    if not os.path.isfile(CSV_FILE):
        log.info("No hay CSV previo — iniciando desde cero.")
        return
    try:
        with open(CSV_FILE, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return
        last = rows[-1]
        bt["capital"]      = float(last["capital_after"])
        bt["total_pnl"]    = float(last["cumulative_pnl"])
        bt["wins"]         = sum(1 for r in rows if r["outcome"] == "WIN")
        bt["losses"]       = sum(1 for r in rows if r["outcome"] == "LOSS")
        bt["trades"]       = [dict(r) for r in rows]
        peak = CAPITAL_TOTAL
        for r in rows:
            cap = float(r["capital_after"])
            if cap > peak:
                peak = cap
            dd = peak - cap
            if dd > bt["max_drawdown"]:
                bt["max_drawdown"] = dd
        bt["peak_capital"] = peak
        total = bt["wins"] + bt["losses"]
        log.info(f"Estado restaurado — {total} trades | Capital: ${bt['capital']:.4f} | "
                 f"PnL: ${bt['total_pnl']:+.4f} | W:{bt['wins']} L:{bt['losses']}")
    except Exception as e:
        log.warning(f"No se pudo restaurar estado desde CSV: {e}")


# ═══════════════════════════════════════════════════════
#  DISCOVERY Y FETCH
# ═══════════════════════════════════════════════════════

async def discover_all():
    loop = asyncio.get_event_loop()
    for sym in SYMBOLS:
        try:
            info = await loop.run_in_executor(None, find_active_market, sym)
            if info:
                markets[sym]["info"]  = info
                markets[sym]["error"] = None
                log_event(f"{sym}: mercado encontrado — {info.get('question','')[:50]}")
            else:
                markets[sym]["info"]  = None
                markets[sym]["error"] = "sin mercado activo"
                log_event(f"{sym}: no se encontró mercado activo")
        except Exception as e:
            markets[sym]["info"]  = None
            markets[sym]["error"] = str(e)
            log_event(f"{sym}: error en discovery — {e}")
    bt["traded_this_cycle"] = False
    write_state()


async def fetch_one(sym: str):
    info = markets[sym]["info"]
    if not info:
        return
    loop = asyncio.get_event_loop()
    try:
        up_metrics, err_up = await loop.run_in_executor(
            None, get_order_book_metrics, info["up_token_id"]
        )
        dn_metrics, err_dn = await loop.run_in_executor(
            None, get_order_book_metrics, info["down_token_id"]
        )

        if up_metrics and dn_metrics:
            markets[sym]["up_bid"] = up_metrics["best_bid"]
            markets[sym]["up_ask"] = up_metrics["best_ask"]
            markets[sym]["dn_bid"] = dn_metrics["best_bid"]
            markets[sym]["dn_ask"] = dn_metrics["best_ask"]

            # Calcular mid correctamente cuando el mercado ya resolvió
            # (el ask desaparece en el lado ganador y el bid en el perdedor)
            def calc_mid(bid, ask):
                if bid > 0 and ask > 0:
                    return round((bid + ask) / 2, 4)
                elif bid > 0:
                    return round(bid, 4)   # solo bid disponible → usar bid
                elif ask > 0:
                    return round(ask, 4)   # solo ask disponible → usar ask
                return 0.0

            markets[sym]["up_mid"] = calc_mid(up_metrics["best_bid"], up_metrics["best_ask"])
            markets[sym]["dn_mid"] = calc_mid(dn_metrics["best_bid"], dn_metrics["best_ask"])
            secs = seconds_remaining(info)
            if secs is not None:
                markets[sym]["time_left"] = f"{int(secs)}s"
                if secs <= 0:
                    markets[sym]["info"] = None
            else:
                markets[sym]["time_left"] = "N/A"
            markets[sym]["error"] = None
        else:
            markets[sym]["error"] = err_up or err_dn or "error ob"
    except Exception as e:
        markets[sym]["error"] = str(e)


async def fetch_all():
    await asyncio.gather(*[fetch_one(sym) for sym in SYMBOLS])


# ═══════════════════════════════════════════════════════
#  SEÑALES Y LÓGICA DE TRADING
# ═══════════════════════════════════════════════════════

def compute_signals():
    # Si un activo ya resolvió (precio >= 0.98 o <= 0.02), lo normalizamos a 1.0 / 0.0
    # para que cuente correctamente como peer en el armónico y consenso
    def normalized_up(s):
        mid = markets[s]["up_mid"]
        if mid >= RESOLVED_UP_THRESH:
            return 1.0
        if mid <= RESOLVED_DN_THRESH:
            return 0.0
        return mid

    def normalized_dn(s):
        mid = markets[s]["dn_mid"]
        if mid >= RESOLVED_UP_THRESH:
            return 1.0
        if mid <= RESOLVED_DN_THRESH:
            return 0.0
        return mid

    up_mids = {s: normalized_up(s) for s in SYMBOLS if markets[s]["up_mid"] > 0}
    dn_mids = {s: normalized_dn(s) for s in SYMBOLS if markets[s]["dn_mid"] > 0}

    if len(up_mids) < 2:
        bt["signal_asset"] = None
        return

    harm_up = harmonic_mean(list(up_mids.values()))
    harm_dn = harmonic_mean(list(dn_mids.values()))
    bt["harm_up"] = harm_up
    bt["harm_dn"] = harm_dn

    cheapest_up, div_up = find_cheapest(up_mids, harm_up)
    cheapest_dn, div_dn = find_cheapest(dn_mids, harm_dn)

    if abs(div_up) >= abs(div_dn) and cheapest_up:
        bt["signal_asset"] = cheapest_up
        bt["signal_side"]  = "UP"
        bt["signal_div"]   = div_up
    elif cheapest_dn:
        bt["signal_asset"] = cheapest_dn
        bt["signal_side"]  = "DOWN"
        bt["signal_div"]   = div_dn
    else:
        bt["signal_asset"] = None

    if bt["signal_asset"] and bt["signal_side"]:
        peers = [s for s in SYMBOLS if s != bt["signal_asset"]]
        if bt["signal_side"] == "UP":
            peer_vals = [markets[p]["up_mid"] for p in peers if markets[p]["up_mid"] > 0]
        else:
            peer_vals = [markets[p]["dn_mid"] for p in peers if markets[p]["dn_mid"] > 0]

        if len(peer_vals) == 2 and all(v > CONSENSUS_FULL for v in peer_vals):
            bt["consensus"] = "FULL"
        elif len(peer_vals) >= 1 and sum(1 for v in peer_vals if v > CONSENSUS_SOFT) >= 1:
            bt["consensus"] = "SOFT"
        else:
            bt["consensus"] = "NONE"


def check_entry():
    if bt["traded_this_cycle"]:
        return
    if not bt["entry_window"]:
        return
    # Solo entra con consenso FULL (ambos peers > 0.80)
    if bt["consensus"] != "FULL":
        bt["skipped"] += 1
        return
    if not bt["signal_asset"]:
        return
    if abs(bt["signal_div"]) < DIVERGENCE_THRESHOLD:
        return

    sym  = bt["signal_asset"]
    side = bt["signal_side"]

    if side == "UP":
        entry_ask = markets[sym]["up_ask"]
        entry_bid = markets[sym]["up_bid"]
        entry_mid = markets[sym]["up_mid"]
    else:
        entry_ask = markets[sym]["dn_ask"]
        entry_bid = markets[sym]["dn_bid"]
        entry_mid = markets[sym]["dn_mid"]

    if entry_ask <= 0 or entry_ask >= 1:
        return

    # Excluir activos que ya resolvieron — no pueden ser el activo a comprar
    up_mid = markets[sym]["up_mid"]
    dn_mid = markets[sym]["dn_mid"]
    if up_mid >= RESOLVED_UP_THRESH or up_mid <= RESOLVED_DN_THRESH or \
       dn_mid >= RESOLVED_UP_THRESH or dn_mid <= RESOLVED_DN_THRESH:
        log_event(f"SKIP {side} {sym} — activo ya resuelto (up={up_mid:.4f} dn={dn_mid:.4f})")
        bt["skipped"] += 1
        return

    # El activo rezagado debe estar sobre ENTRY_MIN_PRICE (0.65)
    if entry_ask < ENTRY_MIN_PRICE:
        log_event(
            f"SKIP {side} {sym} — ask={entry_ask:.4f} bajo mínimo {ENTRY_MIN_PRICE}"
        )
        bt["skipped"] += 1
        return

    shares = round(ENTRY_USD / entry_ask, 6)
    secs   = min_secs_remaining() or 0

    peers        = [s for s in SYMBOLS if s != sym]
    peer_snaps   = {p: {"up_mid": markets[p]["up_mid"], "dn_mid": markets[p]["dn_mid"]} for p in peers}
    harm_entry   = bt["harm_up"] if side == "UP" else bt["harm_dn"]
    gap_entry    = bt["signal_div"]
    capital_before = bt["capital"]

    bt["capital"] -= ENTRY_USD
    bt["traded_this_cycle"] = True

    bt["position"] = {
        "asset":         sym,
        "side":          side,
        "entry_price":   entry_ask,
        "entry_bid":     entry_bid,
        "entry_mid":     entry_mid,
        "entry_usd":     ENTRY_USD,
        "shares":        shares,
        "secs_left_entry": secs,
        "harm_entry":    harm_entry,
        "gap_entry":     gap_entry,
        "entry_ts":      datetime.now().isoformat(),
        "consensus_entry": bt["consensus"],
        "peer_snaps":    peer_snaps,
        "capital_before": capital_before,
        "market_info_snapshot": {
            "condition_id": markets[sym]["info"].get("condition_id") if markets[sym]["info"] else None,
        },
    }

    log_event(
        f"ENTRADA {side} {sym} @ ask={entry_ask:.4f} | "
        f"div={gap_entry*100:+.1f}pts | arm={harm_entry:.4f} | "
        f"shares={shares:.4f} | capital=${bt['capital']:.2f}"
    )
    write_state()


def check_stop_loss():
    pos  = bt["position"]
    if not pos:
        return
    sym  = pos["asset"]
    side = pos["side"]
    current_bid = markets[sym]["up_bid"] if side == "UP" else markets[sym]["dn_bid"]
    if current_bid <= STOP_LOSS_PRICE and current_bid > 0:
        pnl = round(pos["shares"] * current_bid - ENTRY_USD, 6)
        bt["capital"]   += ENTRY_USD + pnl
        bt["total_pnl"] += pnl
        bt["losses"]    += 1
        update_drawdown()
        log_event(f"STOP LOSS {side} {sym} @ bid={current_bid:.4f} | PnL=${pnl:+.4f}")
        _record_trade_sl(pos, current_bid, pnl)
        bt["position"] = None
        write_state()


def _apply_resolution(pos, resolved):
    sym  = pos["asset"]
    side = pos["side"]
    if resolved == side:
        pnl     = round((pos["shares"] - 1) * ENTRY_USD, 6)
        outcome = "WIN"
        bt["wins"] += 1
    else:
        pnl     = -ENTRY_USD
        outcome = "LOSS"
        bt["losses"] += 1
    bt["capital"]   += ENTRY_USD + pnl
    bt["total_pnl"] += pnl
    update_drawdown()
    log_event(
        f"RESOLUCIÓN {outcome} {side} {sym} → {resolved} | "
        f"PnL=${pnl:+.4f} | Capital=${bt['capital']:.4f}"
    )
    _record_trade(pos, resolved, outcome, pnl)
    write_state()


def check_resolution():
    pos = bt["position"]
    if not pos:
        return
    sym    = pos["asset"]
    up_mid = markets[sym]["up_mid"]

    # 1. Resolución por precio (0.98 / 0.02)
    resolved = None
    if up_mid >= RESOLVED_UP_THRESH:
        resolved = "UP"
    elif up_mid <= RESOLVED_DN_THRESH:
        resolved = "DOWN"

    if resolved:
        _apply_resolution(pos, resolved)
        bt["position"] = None
        return

    # 2. Mercado expirado sin precio concluyente → consultar Gamma
    if markets[sym]["info"] is None:
        condition_id = (pos.get("market_info_snapshot") or {}).get("condition_id")
        if not condition_id:
            log_event(f"WARN: sin condition_id para {sym}, descartando posición")
            bt["capital"] += pos["entry_usd"]
            bt["position"] = None
            write_state()
            return

        resolved = fetch_market_resolution(condition_id)
        if resolved:
            log_event(f"Gamma resolvió {sym} → {resolved} (intento inmediato)")
            _apply_resolution(pos, resolved)
            bt["position"] = None
        else:
            log_event(f"Gamma sin resultado para {sym} — reintentando cada 5min (0/6)")
            bt["pending_resolution"] = {
                "pos":          pos,
                "condition_id": condition_id,
                "attempts":     0,
                "next_check":   time.time() + 300,
            }
            bt["position"] = None
        write_state()


async def check_pending_resolution():
    pr = bt["pending_resolution"]
    if not pr:
        return
    if time.time() < pr["next_check"]:
        return

    pr["attempts"] += 1
    condition_id = pr["condition_id"]
    pos          = pr["pos"]
    sym          = pos["asset"]

    log_event(f"Consultando Gamma para {sym} — intento {pr['attempts']}/6")
    loop     = asyncio.get_event_loop()
    resolved = await loop.run_in_executor(None, fetch_market_resolution, condition_id)

    if resolved:
        log_event(f"Gamma confirmó {sym} → {resolved} (intento {pr['attempts']})")
        _apply_resolution(pos, resolved)
        bt["pending_resolution"] = None
    elif pr["attempts"] >= 6:
        log_event(f"WARN: Gamma no resolvió {sym} tras 6 intentos — capital devuelto")
        bt["capital"]   += pos["entry_usd"]
        bt["pending_resolution"] = None
        write_state()
    else:
        pr["next_check"] = time.time() + 300
        log_event(f"{sym} sin resultado — próximo intento en 5min ({pr['attempts']}/6)")
        write_state()


# ═══════════════════════════════════════════════════════
#  PERSISTENCIA
# ═══════════════════════════════════════════════════════

def _build_trade_record(pos, exit_type, exit_price, resolved, outcome, pnl):
    exit_ts    = datetime.now().isoformat()
    duration_s = round((datetime.fromisoformat(exit_ts) - datetime.fromisoformat(pos["entry_ts"])).total_seconds(), 1)
    trade_number = bt["wins"] + bt["losses"]

    peers      = [s for s in SYMBOLS if s != pos["asset"]]
    peer_snaps = pos.get("peer_snaps", {})

    def peer_mids(p):
        snap = peer_snaps.get(p, {})
        side = pos["side"]
        if side == "UP":
            return snap.get("up_mid", 0.0), snap.get("dn_mid", 0.0)
        else:
            return snap.get("dn_mid", 0.0), snap.get("up_mid", 0.0)

    p1_side_mid, p1_opp_mid = peer_mids(peers[0]) if len(peers) > 0 else (0.0, 0.0)
    p2_side_mid, p2_opp_mid = peer_mids(peers[1]) if len(peers) > 1 else (0.0, 0.0)

    sl_price = STOP_LOSS_PRICE
    max_win  = round((1.0 - pos["entry_price"]) / pos["entry_price"] * pos["entry_usd"], 6)

    binary_win = 1 if outcome == "WIN" and exit_type == "RESOLUTION" else \
                 0 if outcome == "LOSS" and exit_type == "RESOLUTION" else -1

    return {
        "trade_id":         f"T{trade_number:04d}",
        "entry_ts":         pos["entry_ts"],
        "exit_ts":          exit_ts,
        "duration_s":       duration_s,
        "asset":            pos["asset"],
        "side":             pos["side"],
        "consensus":        pos["consensus_entry"],
        "entry_ask":        round(pos["entry_price"], 6),
        "entry_bid":        round(pos["entry_bid"], 6),
        "entry_mid":        round(pos["entry_mid"], 6),
        "entry_usd":        round(pos["entry_usd"], 4),
        "shares":           round(pos["shares"], 6),
        "secs_left_entry":  round(pos["secs_left_entry"], 1),
        "harm_entry":       round(pos["harm_entry"], 6),
        "gap_pts":          round(pos["gap_entry"] * 100, 2),
        "peer1_sym":        peers[0] if len(peers) > 0 else "",
        "peer1_side_mid":   round(p1_side_mid, 6),
        "peer1_opp_mid":    round(p1_opp_mid, 6),
        "peer2_sym":        peers[1] if len(peers) > 1 else "",
        "peer2_side_mid":   round(p2_side_mid, 6),
        "peer2_opp_mid":    round(p2_opp_mid, 6),
        "sl_price":         sl_price,
        "exit_type":        exit_type,
        "exit_price":       round(exit_price, 6),
        "resolved":         resolved or "",
        "binary_win":       binary_win,
        "pnl_usd":          round(pnl, 6),
        "pnl_pct_entry":    round(pnl / pos["entry_usd"] * 100, 2),
        "max_possible_win": max_win,
        "outcome":          outcome,
        "capital_before":   round(pos["capital_before"], 4),
        "capital_after":    round(bt["capital"], 4),
        "cumulative_pnl":   round(bt["total_pnl"], 6),
        "trade_number":     trade_number,
    }


def _save_csv(record: dict):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def _record_trade(pos, resolved, outcome, pnl):
    exit_price = 1.0 if resolved == pos["side"] else 0.0
    record = _build_trade_record(pos, "RESOLUTION", exit_price, resolved, outcome, pnl)
    bt["trades"].append(record)
    _save_csv(record)
    _save_log()


def _record_trade_sl(pos, exit_bid, pnl):
    record = _build_trade_record(pos, "STOP_LOSS", exit_bid, None, "LOSS", pnl)
    bt["trades"].append(record)
    _save_csv(record)
    _save_log()


def _save_log():
    total = bt["wins"] + bt["losses"]
    with open(LOG_FILE, "w") as f:
        json.dump({
            "summary": {
                "capital_inicial": CAPITAL_TOTAL,
                "capital_actual":  round(bt["capital"], 4),
                "total_pnl_usd":   round(bt["total_pnl"], 4),
                "roi_pct":         round((bt["capital"] - CAPITAL_TOTAL) / CAPITAL_TOTAL * 100, 2),
                "max_drawdown":    round(bt["max_drawdown"], 4),
                "wins":            bt["wins"],
                "losses":          bt["losses"],
                "win_rate":        round(bt["wins"] / total * 100, 1) if total else 0,
                "skipped":         bt["skipped"],
                "entry_usd":       ENTRY_USD,
            },
            "trades": bt["trades"],
        }, f, indent=2)


# ═══════════════════════════════════════════════════════
#  LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════

async def main_loop():
    log_event("basket.py iniciado — SIMULACION BINARIA")
    log_event(f"Capital: ${CAPITAL_TOTAL:.0f} | Entrada: ${ENTRY_USD:.2f} ({ENTRY_PCT*100:.0f}%)")
    log_event(f"div>={DIVERGENCE_THRESHOLD:.0%} | Entra en ultimo {ENTRY_WINDOW_SECS}s")

    restore_state_from_csv()

    bt["phase"] = "ACTIVO"
    write_state()
    await discover_all()

    while True:
        try:
            secs = min_secs_remaining()

            if secs is not None and secs > WAKE_UP_SECS and not bt["position"]:
                sleep_duration = secs - WAKE_UP_SECS
                wake_at = datetime.fromtimestamp(time.time() + sleep_duration).strftime("%H:%M:%S")
                bt["phase"]        = "DURMIENDO"
                bt["entry_window"] = False

                slept = 0
                while slept < sleep_duration:
                    chunk = min(5.0, sleep_duration - slept)
                    await asyncio.sleep(chunk)
                    slept += chunk
                    bt["next_wake"] = f"{wake_at} (en {int(max(0, sleep_duration - slept))}s)"
                    write_state()

                bt["phase"] = "ACTIVO"
                log_event(f"Despertando — faltan ~{WAKE_UP_SECS}s")
                await discover_all()
                continue

            bt["phase"] = "ACTIVO"
            bt["cycle"] += 1

            await fetch_all()

            # Verificar posición pendiente de resolución Gamma
            await check_pending_resolution()

            secs = min_secs_remaining()
            bt["entry_window"] = (
                secs is not None and
                secs <= ENTRY_WINDOW_SECS and
                secs > ENTRY_CLOSE_SECS
            )

            if bt["position"]:
                check_stop_loss()
            if bt["position"]:
                check_resolution()

            if all(markets[s]["info"] is None for s in SYMBOLS):
                if bt["position"]:
                    log_event("Mercado expirado con posicion abierta — consultando Gamma...")
                    check_resolution()
                if not bt["pending_resolution"]:
                    log_event("Ciclo expirado — buscando nuevo ciclo...")
                    await discover_all()
                continue

            if not bt["position"]:
                compute_signals()
                check_entry()

            write_state()

        except Exception as e:
            log_event(f"Error en loop: {e}")
            write_state()

        await asyncio.sleep(POLL_INTERVAL)


# ═══════════════════════════════════════════════════════
#  DASHBOARD EN HILO SECUNDARIO
# ═══════════════════════════════════════════════════════

def run_dashboard():
    import importlib.util
    spec = importlib.util.spec_from_file_location("dashboard", "dashboard.py")
    dash = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dash)
    port = int(os.environ.get("PORT", 5000))
    log.info(f"Dashboard iniciando en puerto {port}")
    dash.app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# ═══════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    log.info("=" * 54)
    log.info("  BASKET — DIVERGENCIA ARMONICA  [BINARIO]")
    log.info(f"  Capital: ${CAPITAL_TOTAL:.0f}  |  Entrada: ${ENTRY_USD:.2f} ({ENTRY_PCT*100:.0f}%)")
    log.info("  SIMULACION — SIN DINERO REAL")
    log.info("=" * 54)
    log.info(f"State -> {STATE_FILE} | Log -> {LOG_FILE}")

    t = threading.Thread(target=run_dashboard, daemon=True)
    t.start()

    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        log.info("Basket detenido.")
        total = bt["wins"] + bt["losses"]
        roi   = (bt["capital"] - CAPITAL_TOTAL) / CAPITAL_TOTAL * 100
        log.info(f"Capital final: ${bt['capital']:.4f}  (ROI: {roi:+.2f}%)")
        log.info(f"P&L total: ${bt['total_pnl']:+.4f}")
        log.info(f"Trades: {total}  (WIN: {bt['wins']}  LOSS: {bt['losses']})")
