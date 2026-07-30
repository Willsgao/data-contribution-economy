"""
黄金样例验证 — 对 core/calculator.py 做断言
"""

import sys
sys.path.insert(0, "..")

from calculator import calc_scarcity, calc_contribution, enrich_contributor, calculate_once, simulate_calls

# ============================================================
# 默认参数
# ============================================================
K = 0.01
PROFIT = 20000.0
PLATFORM_SHARE = 0.30
CAP_MULTIPLIER = 300.0
TRADITIONAL_RATE = 5.0

# ============================================================
# 贡献者
# ============================================================
contributors = [
    {"name": "张医生-罕见病", "hours": 40, "accuracy": 0.96, "complexity": 5, "pool_size": 3},
    {"name": "李标注-常见病", "hours": 80, "accuracy": 0.94, "complexity": 2, "pool_size": 10000},
    {"name": "王工程师-影像", "hours": 60, "accuracy": 0.98, "complexity": 4, "pool_size": 500},
]

# ============================================================
# 中间量验证
# ============================================================
print("=== 中间量验证 ===")

s_zhang = calc_scarcity(3, K)
s_li = calc_scarcity(10000, K)
s_wang = calc_scarcity(500, K)

assert s_zhang == 0.9709, f"张稀缺性: expected 0.9709, got {s_zhang}"
assert s_li == 0.0099, f"李稀缺性: expected 0.0099, got {s_li}"
assert s_wang == 0.1667, f"王稀缺性: expected 0.1667, got {s_wang}"
print("  S 值: ✓")

c_zhang = calc_contribution(40, 0.96, 5, s_zhang)
c_li = calc_contribution(80, 0.94, 2, s_li)
c_wang = calc_contribution(60, 0.98, 4, s_wang)

assert c_zhang == 186.41, f"张贡献值: expected 186.41, got {c_zhang}"
assert c_li == 1.49, f"李贡献值: expected 1.49, got {c_li}"
assert c_wang == 39.21, f"王贡献值: expected 39.21, got {c_wang}"
print("  贡献值: ✓")

total_contrib = c_zhang + c_li + c_wang
assert round(total_contrib, 2) == 227.11, f"总贡献值: expected 227.11, got {round(total_contrib, 2)}"
print("  总贡献值 227.11: ✓")

cap_zhang = round(c_zhang * CAP_MULTIPLIER, 2)
assert cap_zhang == 55923.00, f"张上限: expected 55923.00, got {cap_zhang}"
cap_li = round(c_li * CAP_MULTIPLIER, 2)
assert cap_li == 447.00, f"李上限: expected 447.00, got {cap_li}"
cap_wang = round(c_wang * CAP_MULTIPLIER, 2)
assert cap_wang == 11763.00, f"王上限: expected 11763.00, got {cap_wang}"
print("  上限: ✓")

# 传统收入
assert 40 * TRADITIONAL_RATE == 200, f"张 trad: expected 200"
assert 80 * TRADITIONAL_RATE == 400, f"李 trad: expected 400"
assert 60 * TRADITIONAL_RATE == 300, f"王 trad: expected 300"
print("  传统收入: ✓")

# ============================================================
# calculate_once 验证
# ============================================================
print("\n=== calculate_once 验证 ===")
result = calculate_once(contributors, profit=PROFIT, platform_share=PLATFORM_SHARE,
                        k=K, cap_multiplier=CAP_MULTIPLIER, traditional_rate=TRADITIONAL_RATE)

assert result["total_contribution"] == 227.11, f"total_contrib: {result['total_contribution']}"
assert result["distributable"] == 14000.00, f"distributable: {result['distributable']}"
assert result["platform_profit"] == 6000.00, f"platform: {result['platform_profit']}"
assert result["total_traditional"] == 900.00, f"trad total: {result['total_traditional']}"
print("  distributable=14000, platform=6000, trad=900: ✓")

r = {c["name"]: c for c in result["contributors"]}
assert r["张医生-罕见病"]["share_pct"] == 82.1, f"张 share: {r['张医生-罕见病']['share_pct']}"
assert r["李标注-常见病"]["share_pct"] == 0.7, f"李 share: {r['李标注-常见病']['share_pct']}"
assert r["王工程师-影像"]["share_pct"] == 17.3, f"王 share: {r['王工程师-影像']['share_pct']}"
print("  share_pct: ✓")

assert abs(r["张医生-罕见病"]["profit"] - 11491.08) < 0.02, f"张 profit: {r['张医生-罕见病']['profit']}"
assert abs(r["李标注-常见病"]["profit"] - 91.85) < 0.02, f"李 profit: {r['李标注-常见病']['profit']}"
assert abs(r["王工程师-影像"]["profit"] - 2417.07) < 0.02, f"王 profit: {r['王工程师-影像']['profit']}"
print("  单次 profit: ✓")

# ============================================================
# simulate_calls 验证 — 5 次
# ============================================================
print("\n=== simulate_calls (5次) 验证 ===")
sim = simulate_calls(contributors, profit_per_call=PROFIT, num_calls=5,
                     platform_share=PLATFORM_SHARE, k=K, cap_multiplier=CAP_MULTIPLIER,
                     traditional_rate=TRADITIONAL_RATE)

assert sim["cumulative_by_contributor"]["张医生-罕见病"] == 55923.00, \
    f"张 cumulative: {sim['cumulative_by_contributor']['张医生-罕见病']}"
assert sim["cumulative_by_contributor"]["李标注-常见病"] == 447.00, \
    f"李 cumulative: {sim['cumulative_by_contributor']['李标注-常见病']}"
assert sim["cumulative_by_contributor"]["王工程师-影像"] == 11763.00, \
    f"王 cumulative: {sim['cumulative_by_contributor']['王工程师-影像']}"
print("  5次 cumulative: ✓")

# 张医生 excess 应为 ~1532.40
zhang_excess = sim["excess_to_pool"]["张医生-罕见病"]
assert abs(zhang_excess - 1532.40) < 0.1, f"张 excess: {zhang_excess}"
li_excess = sim["excess_to_pool"]["李标注-常见病"]
assert abs(li_excess - 12.25) < 0.1, f"李 excess: {li_excess}"
wang_excess = sim["excess_to_pool"]["王工程师-影像"]
assert abs(wang_excess - 322.35) < 0.1, f"王 excess: {wang_excess}"
print("  5次 excess: ✓")

assert sim["total_worker_income"] == 68133.00, f"worker total: {sim['total_worker_income']}"
assert abs(sim["total_pool"] - 1867.00) < 1, f"total pool: {sim['total_pool']}"
assert sim["total_platform"] == 30000.00, f"total platform: {sim['total_platform']}"
print("  worker=68133, pool≈1867, platform=30000: ✓")

# ============================================================
# simulate_calls 验证 — 50 次
# ============================================================
print("\n=== simulate_calls (50次) 验证 ===")
sim50 = simulate_calls(contributors, profit_per_call=PROFIT, num_calls=50,
                       platform_share=PLATFORM_SHARE, k=K, cap_multiplier=CAP_MULTIPLIER,
                       traditional_rate=TRADITIONAL_RATE)

assert sim50["total_worker_income"] == 68133.00, \
    f"50次 worker total: {sim50['total_worker_income']}"
assert sim50["total_pool"] == 631867.00, \
    f"50次 pool: {sim50['total_pool']}"
assert sim50["total_platform"] == 300000.00, \
    f"50次 platform: {sim50['total_platform']}"
print("  worker=68133, pool=631867, platform=300000: ✓")

# 张医生 50次
zhang50 = sim50["cumulative_by_contributor"]["张医生-罕见病"]
assert zhang50 == 55923.00, f"50次张 cumulative: {zhang50}"
print("  张医生: ¥200 → ¥55,923: ✓")

print("\n" + "=" * 50)
print("  全部金色样例验证通过！")
print("=" * 50)
