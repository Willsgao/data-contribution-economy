#!/usr/bin/env python3
"""
数据要素贡献值模拟引擎 — 完整三阶段演示

  阶段一: 工业时代一次性买断（IT时代现状）
  阶段二: AI时代持续版税（数据被反复调用，每次都分润）
  阶段三: 超额回流公共基金池（上限调节，共同富裕）

公式:
  贡献值 = 工时(T) × 准确率(A) × 复杂度(C) × 稀缺性(S)
  稀缺性: S = 1 / (1 + k × N_type)

用法: python simulate.py
"""

import math

# ============================================================
# 全局参数 — 修改这里改变模拟结果
# ============================================================

K = 0.01                       # 稀缺性衰减系数
PROFIT_PER_CALL = 20000        # 模型每次调用数据产生的利润 (元)
MODEL_CALLS = 5                # 模拟数据被模型调用的总次数（模拟时间轴）
CAP_MULTIPLIER = 300           # 收入上限倍数：累计收入 > 基础贡献值 × 此倍数 → 超额入池
TRADITIONAL_RATE = 5           # 工业时代计件单价 (元/工时)

# ============================================================
# 贡献者数据 — 修改这里测试不同场景
# ============================================================

contributors = [
    # (姓名,         工时h, 准确率%, 复杂度L1-L5, 类型存量N)
    ("张医生-罕见病",      40,  0.96,   5,      3),
    ("李标注-常见病",      80,  0.94,   2,  10000),
    ("王工程师-影像",      60,  0.98,   4,    500),
]

# ============================================================
# 计算引擎
# ============================================================

def calc_scarcity(N, k=K):
    return round(1 / (1 + k * N), 4)

def calc_contribution(T, A, C, S):
    return round(T * A * C * S, 2)

# 初始化贡献者
state = []
for name, hours, accuracy, complexity, pool_size in contributors:
    S = calc_scarcity(pool_size)
    contrib = calc_contribution(hours, accuracy, complexity, S)
    cap = round(contrib * CAP_MULTIPLIER, 2)
    state.append({
        "name": name,
        "hours": hours,
        "accuracy": accuracy,
        "complexity": complexity,
        "pool_size": pool_size,
        "scarcity": S,
        "contribution": contrib,
        "cap": cap,
        "traditional_income": hours * TRADITIONAL_RATE,  # 工业时代一次性收入
        "cumulative_income": 0.0,   # 累计持续收入
        "excess_to_pool": 0.0,      # 超额部分流入公共池
    })

total_contrib = sum(s["contribution"] for s in state)
public_pool = 0.0

# ============================================================
# 输出
# ============================================================

SEP = "─" * 88
EQ  = "=" * 88

# ---- 标题 ----
print(EQ)
print("    数据要素贡献值模拟引擎 — 从一次性买断到持续共同富裕")
print(EQ)
print(f"    稀缺性衰减系数 k = {K}  |  模型单次调用利润 = ¥{PROFIT_PER_CALL:,}  |  调用次数 = {MODEL_CALLS}")
print(f"    收入上限 = 基础贡献值 × {CAP_MULTIPLIER}")
print()

# ============================================================
# 阶段一：工业时代 — 一次性买断
# ============================================================
print(EQ)
print("  【阶段一】工业时代：一次性买断（IT时代现状）")
print(EQ)
print()
print("  规则: 按工时计件，干完结算。数据调用次数再多，跟劳动者无关。")
print()

print(SEP)
print(f"  {'贡献者':<18} {'工时h':>6} {'计件单价':>8} {'一次性收入':>12}")
print(SEP)
for s in state:
    print(f"  {s['name']:<18} {s['hours']:>6}h  ¥{TRADITIONAL_RATE:>6}/h  ¥{s['traditional_income']:>10,.2f}")
total_traditional = sum(s["traditional_income"] for s in state)
print(SEP)
print(f"  {'合计':<18} {'':>6}  {'':>8}  ¥{total_traditional:>10,.2f}")
print()
print(f"  ★ 平台拿走全部后续利润。数据被100个模型调用了100次，跟标注员没有一分钱关系。")
print()

# ============================================================
# 阶段二：贡献值计算（一次性计算结果，为持续分润提供比例基础）
# ============================================================
print(EQ)
print("  【阶段二】贡献值计量：决定\"每次分多少\"的比例基础")
print(EQ)
print()
print(f"  公式: 贡献值 = 工时 × 准确率 × 复杂度 × 稀缺性")
print(f"  稀缺性: S = 1 / (1 + {K} × N_type)")
print()

print(SEP)
print(f"  {'贡献者':<18} {'工时':>5} {'准确率':>7} {'复杂度':>5} {'存量N':>7} {'稀缺性S':>7} {'贡献值':>10} {'占比':>7}")
print(SEP)
for s in state:
    print(f"  {s['name']:<18} {s['hours']:>4}h  {s['accuracy']:>6.0%}  L{s['complexity']:<4}  {s['pool_size']:>6,}  {s['scarcity']:>7.4f}  {s['contribution']:>10.2f}  {s['contribution']/total_contrib*100:>6.1f}%")
print(SEP)
print(f"  {'合计':<18} {'':>5}  {'':>7}  {'':>5}  {'':>7}  {'':>7}  {total_contrib:>10.2f}  {'100.0%'}")
print()

rare = state[0]
common = state[1]
print(f"  ★ 罕见病(N={rare['pool_size']}) vs 常见病(N={common['pool_size']:,})：稀缺性差 {rare['scarcity']/common['scarcity']:.0f} 倍")
print(f"    贡献值差 {rare['contribution']/common['contribution']:.0f} 倍。不靠人工判断，数学自动为稀缺劳动定价。")
print()

# ============================================================
# 阶段三：持续分润 — 模型反复调用数据，每次分一次
# ============================================================
print(EQ)
print("  【阶段三】AI时代：持续版税 — 数据被反复调用，每次都分润")
print(EQ)
print()
print(f"  规则: 每个模型调用数据并产生 ¥{PROFIT_PER_CALL:,} 利润后，按贡献值比例自动分润。")
print(f"        收入上限 = 基础贡献值 × {CAP_MULTIPLIER}。超出部分 → 公共基金池。")
print()

print(SEP)
header = f"  {'':<18}" + "".join(f"  {'第'+str(i+1)+'次':>10}" for i in range(MODEL_CALLS)) + f"  {'累计收入':>12}  {'上限':>12}  {'入池':>10}"
print(header)
print(SEP)

for s in state:
    cumulative = 0.0
    excess = 0.0
    row = f"  {s['name']:<18}"
    for call_idx in range(MODEL_CALLS):
        share = s["contribution"] / total_contrib
        call_profit = round(share * PROFIT_PER_CALL, 2)
        # 上限检查：当前累计还没超上限，这笔收入正常入账
        available_cap = max(0, s["cap"] - cumulative)
        if call_profit <= available_cap:
            cumulative += call_profit
            row += f"  ¥{call_profit:>8,.2f}"
        elif available_cap > 0:
            # 部分入账，部分入池
            cumulative += available_cap
            excess += call_profit - available_cap
            row += f"  ¥{call_profit:>8,.2f}⚠"
        else:
            # 全入池
            excess += call_profit
            row += f"  ¥{call_profit:>8,.2f}⚡"
    s["cumulative_income"] = round(cumulative, 2)
    s["excess_to_pool"] = round(excess, 2)
    public_pool += excess
    row += f"  ¥{cumulative:>10,.2f}  ¥{s['cap']:>10,.2f}  ¥{excess:>8,.2f}"
    print(row)

print(SEP)
print()

# 公共基金池
print(EQ)
print("  【公共基金池】超额回流 — 防撑死，最终实现共同富裕")
print(EQ)
print()
print(f"  公共基金池累计: ¥{public_pool:,.2f}")
print()
print("  资金用途:")
print("    · 低技能岗位下限保障（罕见病患者无法工作但仍能维持基本生活）")
print("    · 全民数字技能培训（老年群体、待业劳动力再教育）")
print("    · 全民基本算力（每人每月免费调用AI基础额度）")
print("    · AI安全研究（对抗攻击检测、偏见审计、伦理审查）")
print()

# ============================================================
# 阶段四：数据被50个模型反复调用的放大效应
# ============================================================
print(EQ)
print("  【长期推演】如果数据被50个模型反复调用……")
print(EQ)
print()

FUTURE_CALLS = 50
print(f"  模拟 {FUTURE_CALLS} 次模型调用，每次利润 ¥{PROFIT_PER_CALL:,}，总利润 ¥{FUTURE_CALLS * PROFIT_PER_CALL:,}")
print()

# 重置累计
for s in state:
    s["future_total"] = 0.0
    s["future_pool"] = 0.0

future_pool = 0.0
for call_idx in range(FUTURE_CALLS):
    for s in state:
        share = s["contribution"] / total_contrib
        cp = round(share * PROFIT_PER_CALL, 2)
        available = max(0, s["cap"] - s["future_total"])
        if cp <= available:
            s["future_total"] += cp
        elif available > 0:
            s["future_total"] += available
            s["future_pool"] += cp - available
            future_pool += cp - available
        else:
            s["future_pool"] += cp
            future_pool += cp

print(SEP)
print(f"  {'贡献者':<18} {'个人累计收入':>14} {'流入公共池':>14} {'传统一次性':>14} {'旧vs新':>10}")
print(SEP)
for s in state:
    multiple = s["future_total"] / s["traditional_income"] if s["traditional_income"] > 0 else 0
    print(f"  {s['name']:<18} ¥{s['future_total']:>12,.2f}  ¥{s['future_pool']:>12,.2f}  ¥{s['traditional_income']:>12,.2f}  {multiple:>8.0f}x")
print(SEP)
print(f"  {'公共基金池':<18} {'':>14} ¥{future_pool:>12,.2f}")
print()
print(f"  ★ 工业时代: 张医生一次拿 ¥{state[0]['traditional_income']:,.0f}，平台拿走剩余 ¥{FUTURE_CALLS*PROFIT_PER_CALL - total_traditional:,}。")
print(f"  ★ AI时代:   张医生持续拿 ¥{state[0]['future_total']:,.0f}（{state[0]['future_total']/state[0]['traditional_income']:.0f}x），")
print(f"             超额 ¥{state[0]['future_pool']:,.0f} 入公共池滋养全社会。")
print(f"  ★ 共同富裕: 公共池积累 ¥{future_pool:,.0f}，保障罕见病患者等弱势群体，")
print(f"             让\"多劳多得\"和\"不漏一人\"在同一个系统里共存。")
print()
