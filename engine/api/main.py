"""
FastAPI app for data contribution allocation demo.
"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.models import (
    CalculateRequest, CalculateResponse,
    ContributorCalcItem,
    SimulateRequest, SimulateResponse,
    CallItem, PerCallResult,
    ContributorSimSummary,
)
from core.calculator import calculate_once, simulate_calls

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = FastAPI(title="Data Contribution Allocator Demo", version="0.1.0")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/calculate", response_model=CalculateResponse)
def api_calculate(req: CalculateRequest):
    raw = [
        {
            "name": c.name, "hours": c.hours,
            "accuracy": c.accuracy, "complexity": c.complexity,
            "pool_size": c.pool_size,
        }
        for c in req.contributors
    ]
    result = calculate_once(
        raw,
        profit=req.profit,
        platform_share=req.platform_share,
        k=req.k,
        cap_multiplier=req.cap_multiplier,
        traditional_rate=req.traditional_rate,
    )
    if result["total_contribution"] == 0:
        raise HTTPException(status_code=400, detail="Total contribution is zero")
    items = [ContributorCalcItem(**c) for c in result["contributors"]]
    return CalculateResponse(
        results=items,
        total_contribution=result["total_contribution"],
        distributable=result["distributable"],
        platform_profit=result["platform_profit"],
        total_traditional=result["total_traditional"],
    )


@app.post("/api/simulate", response_model=SimulateResponse)
def api_simulate(req: SimulateRequest):
    raw = [
        {
            "name": c.name, "hours": c.hours,
            "accuracy": c.accuracy, "complexity": c.complexity,
            "pool_size": c.pool_size,
        }
        for c in req.contributors
    ]
    common = dict(
        profit_per_call=req.profit_per_call,
        platform_share=req.platform_share,
        k=req.k,
        cap_multiplier=req.cap_multiplier,
        traditional_rate=req.traditional_rate,
    )
    timeline = simulate_calls(raw, num_calls=req.timeline_calls, **common)
    projection = simulate_calls(raw, num_calls=req.projection_calls, **common)

    summaries = []
    for meta in timeline["contributors_meta"]:
        name = meta["name"]
        summaries.append(ContributorSimSummary(
            name=name,
            contribution=meta["contribution"],
            share_pct=meta["share_pct"],
            cap=meta["cap"],
            traditional_income=meta["traditional_income"],
            cumulative_income=timeline["cumulative_by_contributor"].get(name, 0.0),
            excess_to_pool=timeline["excess_to_pool"].get(name, 0.0),
            projection_income=projection["cumulative_by_contributor"].get(name, 0.0),
            projection_excess=projection["excess_to_pool"].get(name, 0.0),
        ))

    calls = []
    for c in timeline["calls"]:
        items = [
            CallItem(
                name=it["name"],
                raw_profit=it["raw_profit"],
                credited=it["credited"],
                to_pool=it["to_pool"],
            )
            for it in c["items"]
        ]
        calls.append(PerCallResult(
            call_index=c["call_index"],
            platform_profit=c["platform_profit"],
            items=items,
        ))

    return SimulateResponse(
        calls=calls,
        summaries=summaries,
        total_platform_timeline=timeline["total_platform"],
        total_pool_timeline=timeline["total_pool"],
        total_worker_income_timeline=timeline["total_worker_income"],
        total_traditional=projection["total_traditional"],
        total_worker_income_projection=projection["total_worker_income"],
        total_pool_projection=projection["total_pool"],
        total_platform_projection=projection["total_platform"],
        projection_calls=req.projection_calls,
        timeline_calls=req.timeline_calls,
    )
