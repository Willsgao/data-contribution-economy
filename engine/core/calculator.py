"""
数据要素贡献值计算引擎
所有公式与 engine/simulate.py 严格对齐
"""
from typing import Any


def calc_scarcity(pool_size: int, k: float = 0.01) -> float:
    """S = round(1 / (1 + k * N), 4)"""
    return round(1 / (1 + k * pool_size), 4)


def calc_contribution(hours: float, accuracy: float,
                      complexity: int, scarcity: float) -> float:
    """round(hours * accuracy * complexity * scarcity, 2)"""
    return round(hours * accuracy * complexity * scarcity, 2)


def enrich_contributor(raw: dict, *, k: float, cap_multiplier: float,
                       traditional_rate: float) -> dict:
    s = calc_scarcity(raw["pool_size"], k)
    contrib = calc_contribution(raw["hours"], raw["accuracy"],
                                raw["complexity"], s)
    cap = round(contrib * cap_multiplier, 2)
    trad = raw["hours"] * traditional_rate
    return {
        **raw,
        "scarcity": s,
        "contribution": contrib,
        "cap": cap,
        "traditional_income": trad,
    }


def calculate_once(
    contributors: list[dict],
    *,
    profit: float = 20000.0,
    platform_share: float = 0.30,
    k: float = 0.01,
    cap_multiplier: float = 300.0,
    traditional_rate: float = 5.0,
) -> dict:
    enriched = [
        enrich_contributor(c, k=k, cap_multiplier=cap_multiplier,
                           traditional_rate=traditional_rate)
        for c in contributors
    ]
    total_contrib = sum(c["contribution"] for c in enriched)
    distributable = round(profit * (1 - platform_share), 2)
    platform_profit = round(profit * platform_share, 2)
    total_traditional = sum(c["traditional_income"] for c in enriched)

    results = []
    for c in enriched:
        if total_contrib > 0:
            share_pct = round(c["contribution"] / total_contrib * 100, 1)
            raw_profit = round(c["contribution"] / total_contrib * distributable, 2)
        else:
            share_pct = 0.0
            raw_profit = 0.0
        results.append({
            "name": c["name"],
            "hours": c["hours"],
            "accuracy": c["accuracy"],
            "complexity": c["complexity"],
            "pool_size": c["pool_size"],
            "scarcity": c["scarcity"],
            "contribution": c["contribution"],
            "share_pct": share_pct,
            "profit": raw_profit,
            "cap": c["cap"],
            "traditional_income": c["traditional_income"],
        })

    return {
        "contributors": results,
        "total_contribution": round(total_contrib, 2),
        "distributable": distributable,
        "platform_profit": platform_profit,
        "total_traditional": round(total_traditional, 2),
    }


def simulate_calls(
    contributors: list[dict],
    *,
    profit_per_call: float = 20000.0,
    num_calls: int = 5,
    platform_share: float = 0.30,
    k: float = 0.01,
    cap_multiplier: float = 300.0,
    traditional_rate: float = 5.0,
) -> dict:
    enriched = [
        enrich_contributor(c, k=k, cap_multiplier=cap_multiplier,
                           traditional_rate=traditional_rate)
        for c in contributors
    ]
    total_contrib = sum(c["contribution"] for c in enriched)
    distributable = round(profit_per_call * (1 - platform_share), 2)

    cumulative = {c["name"]: 0.0 for c in enriched}
    excess = {c["name"]: 0.0 for c in enriched}
    caps = {c["name"]: c["cap"] for c in enriched}
    trad = {c["name"]: c["traditional_income"] for c in enriched}

    calls = []
    for call_idx in range(num_calls):
        items = []
        for c in enriched:
            if total_contrib > 0:
                share = c["contribution"] / total_contrib
            else:
                share = 0.0
            raw = round(share * distributable, 2)
            available = max(0.0, caps[c["name"]] - cumulative[c["name"]])

            if raw <= available:
                credited = raw
                to_pool = 0.0
            elif available > 0:
                credited = available
                to_pool = round(raw - available, 2)
            else:
                credited = 0.0
                to_pool = raw

            cumulative[c["name"]] = round(cumulative[c["name"]] + credited, 2)
            excess[c["name"]] = round(excess[c["name"]] + to_pool, 2)

            items.append({
                "name": c["name"],
                "raw_profit": raw,
                "credited": credited,
                "to_pool": to_pool,
            })

        calls.append({
            "call_index": call_idx + 1,
            "platform_profit": round(profit_per_call * platform_share, 2),
            "items": items,
        })

    total_platform = round(profit_per_call * platform_share * num_calls, 2)
    total_pool = round(sum(excess.values()), 2)
    total_worker_income = round(sum(cumulative.values()), 2)
    total_traditional = round(sum(trad.values()), 2)

    meta = []
    for c in enriched:
        if total_contrib > 0:
            share_pct = round(c["contribution"] / total_contrib * 100, 1)
        else:
            share_pct = 0.0
        meta.append({
            "name": c["name"],
            "hours": c["hours"],
            "accuracy": c["accuracy"],
            "complexity": c["complexity"],
            "pool_size": c["pool_size"],
            "scarcity": c["scarcity"],
            "contribution": c["contribution"],
            "share_pct": share_pct,
            "cap": c["cap"],
            "traditional_income": c["traditional_income"],
        })

    return {
        "contributors_meta": meta,
        "total_contribution": round(total_contrib, 2),
        "calls": calls,
        "cumulative_by_contributor": {k: round(v, 2) for k, v in cumulative.items()},
        "excess_to_pool": {k: round(v, 2) for k, v in excess.items()},
        "cap_by_contributor": caps,
        "traditional_by_contributor": trad,
        "total_platform": total_platform,
        "total_pool": total_pool,
        "total_worker_income": total_worker_income,
        "total_traditional": total_traditional,
    }
