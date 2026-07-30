# 贡献值分配系统 Demo — 实现规格书（给实现 LLM 用）

> 本文是可执行的实现规格，不是概念介绍。  
> 实现目标：复现并可视化 `engine/simulate.py` 的经济机制叙事。  
> 对照仓库方案文档（`docs/01–05`）时请记住：**本 Demo 是机制演示，不是全方案工程 MVP。**

---

## 0. 给实现者的硬约束

1. **只改 / 只新增 `engine/` 下本规格列出的文件**；不要改 `docs/`、不要做区块链、数据库、登录。
2. **计算逻辑必须与 `engine/simulate.py` 数值一致**（见第 8 节黄金样例）。有冲突时以 `simulate.py` 为准，不以正式文档里的 A 因子表 / L 权重表为准。
3. **代码风格**：简洁、可读、少抽象；前端零构建工具。
4. **完成定义**：本机启动后，浏览器打开 `http://localhost:8000`，预填三人样例，一点「计算 / 模拟」就能看到与第 8 节一致的数字。
5. 读完本文件后，再读 `engine/simulate.py`；实现时把其中的计算抽成纯函数，CLI 打印逻辑可暂不重构。

---

## 1. 定位与叙事目标

### 1.1 这是什么

面试 / 讲解用的 **单机 Web Demo**：

- 用户输入若干贡献者（工时、准确率、复杂度、类型存量 N）
- 后端按轨道 A 简化公式算贡献值
- 展示：单次分配、多轮持续分润、收入上限、超额入公共池
- 对比：工业时代一次性买断 vs AI 时代持续收入

### 1.2 这不是什么

| 全方案能力 | 本 Demo |
|---|---|
| L1 真实数据价值链 / OCR / 标注流水线 | ❌ |
| 轨道 B–E（Shapley、AI 增益、合成衰减、历史贡献） | ❌ |
| 联盟链 / 智能合约 / DID / 数字人民币 | ❌ |
| SPV、三层税收、消费者池 | ❌ |
| 正式轨道 A 的 A 因子表、L1–L5 权重表、S 地板 | ❌（刻意简化） |

### 1.3 必须讲清的三句话（UI 文案也要体现）

1. **工业时代**：按工时一次性买断，后面数据被调用多少次都与劳动者无关。  
2. **AI 时代**：终端每次调用产生利润 → 先扣公共服务份额 → 余额按贡献值比例持续分润。  
3. **共同富裕调节**：个人累计收入超过「贡献值 × 上限倍数」后，超额进入公共基金池。

### 1.4 「平台 30%」口径（禁止写错）

`platform_share` 表示：**公共服务平台扣除（税收 + 基础设施运营），归入公共财政**。  
**禁止**写成「私有平台抽成 30%」。UI 标签用「公共服务 / 公共财政」，不要用「平台抽成」。

---

## 2. 系统结构

```
浏览器 (web/index.html + style.css + app.js + Chart.js CDN)
    │
    │  POST /api/calculate   贡献值 + 单次分配 + 工业时代对照
    │  POST /api/simulate    多轮分润（含上限 / 入池）+ 长期对比数字
    │  GET  /                静态页
    │  GET  /style.css /app.js 等
    ▼
FastAPI (api/main.py)
    ├── api/models.py        Pydantic 模型
    └── core/calculator.py   纯函数计算（唯一真相源）
```

运行目录：`engine/`（保证 `python -m api.main` 能找到包）。

---

## 3. 目标文件结构

实现后应出现：

```
engine/
├── simulate.py                 # 已有 CLI；本阶段默认不强制改造
├── ARCHITECTURE.md             # 本文件
├── core/
│   ├── __init__.py             # 可空，或导出公开函数
│   └── calculator.py           # 必须实现
├── api/
│   ├── __init__.py
│   ├── models.py               # 必须实现
│   ├── main.py                 # 必须实现
│   └── requirements.txt        # fastapi, uvicorn, pydantic
└── web/
    ├── index.html              # 必须实现
    ├── style.css               # 必须实现
    └── app.js                  # 必须实现
```

可选（加分，非必须）：

- `core/test_calculator.py`：用第 8 节黄金样例做断言
- 让 `simulate.py` 改为调用 `core.calculator`（行为与数字不变）

---

## 4. 计算公式（必须逐字实现）

以下与 `simulate.py` 对齐。金额统一 **元**，浮点先算再 `round`，位数如下。

### 4.1 稀缺性

```
S = round(1 / (1 + k * N), 4)
```

- `N` = `pool_size`（该类型数据全局存量）
- 默认 `k = 0.01`
- **不要**实现正式文档里的 `N < 100 → S ≥ 0.5` 地板

### 4.2 基础贡献值（轨道 A 简化版）

```
contribution = round(T * A * C * S, 2)
```

| 符号 | 字段 | 含义 | Demo 用法 |
|---|---|---|---|
| T | `hours` | 工时 | 直接相乘 |
| A | `accuracy` | 准确率 | **直接用 0–1 小数**，不做因子表映射 |
| C | `complexity` | 复杂度 | **直接用整数 1–5 当乘数**，不用 1.0/1.5/2.5/4.0/6.0 权重表 |
| S | 由上式算 | 稀缺性 | |

### 4.3 工业时代一次性收入

```
traditional_income = hours * traditional_rate
```

默认 `traditional_rate = 5`（元/工时）。

### 4.4 收入上限

```
cap = round(contribution * cap_multiplier, 2)
```

默认 `cap_multiplier = 300`。

### 4.5 单次调用可分配利润

```
distributable = round(profit_per_call * (1 - platform_share), 2)
platform_profit_one_call = round(profit_per_call * platform_share, 2)
```

默认：`profit_per_call = 20000`，`platform_share = 0.30`。

### 4.6 单人单次应分（未考虑上限）

```
share = contribution / total_contribution
raw_profit = round(share * distributable, 2)
```

`total_contribution = sum(all contributions)`。若为 0，API 返回 400。

### 4.7 多轮模拟 + 上限截断（核心算法）

对每个贡献者维护 `cumulative = 0`、`excess = 0`。  
对 `call_index = 0 .. num_calls-1`：

```
raw = 该人当轮 raw_profit（每轮贡献值占比不变）
available = max(0, cap - cumulative)

if raw <= available:
    credited = raw
    to_pool = 0
elif available > 0:
    credited = available
    to_pool = raw - available
else:
    credited = 0
    to_pool = raw

cumulative += credited
excess += to_pool
```

注意：

- **时间轴上展示的「本轮金额」**：建议同时返回 `raw`（应分）与 `credited`（实际入账）、`to_pool`（本轮入池），便于 UI 标 ⚠。
- 与 `simulate.py` 打印一致时：行内打印的是 `raw`；累计列是截断后的 `cumulative`。
- 平台总收入：`total_platform = round(profit_per_call * platform_share * num_calls, 2)`
- 公共池总额：`total_pool = sum(各人 excess)`

### 4.8 对比卡片数字怎么来（前端必须遵守）

对比区三张卡：

| 卡片 | 含义 | 取数 |
|---|---|---|
| 工业时代 | 全体劳动者一次性收入合计 | `sum(traditional_income)` |
| AI 时代 | 全体劳动者在**长期推演**下的累计入账合计（已截断） | 见下 |
| 公共池 | 长期推演下超额入池合计 | 见下 |

**长期推演默认 `projection_calls = 50`**（与 `simulate.py` 后半段一致），不是时间轴的 5 次。

推荐做法（二选一，推荐 A）：

- **A（推荐）**：`POST /api/simulate` 一次算完  
  - `timeline_calls`（默认 5）→ 时间轴  
  - `projection_calls`（默认 50）→ 对比卡片的 AI / 公共池  
- **B**：前端连发两次 simulate（5 次 + 50 次）——能跑但不优雅

**禁止**：只用单次 `/api/calculate` 的结果去填「AI 时代 / 公共池」两张卡。

个人金句（页面可单独展示）：

- 张医生样例：工业 `¥200` → AI 入账上限/累计 `¥55,923`

---

## 5. `core/calculator.py` 规格

### 5.1 设计原则

- 纯函数，无 I/O，无 FastAPI / 无全局可变状态
- 标准库即可（可不依赖 `math`）
- 输入用 `list[dict]` 或 TypedDict；输出用 `dict`（API 层再转 Pydantic）

### 5.2 必须实现的函数

```python
def calc_scarcity(pool_size: int, k: float = 0.01) -> float:
    """S = round(1 / (1 + k * pool_size), 4)"""

def calc_contribution(hours: float, accuracy: float,
                      complexity: int, scarcity: float) -> float:
    """round(hours * accuracy * complexity * scarcity, 2)"""

def enrich_contributor(raw: dict, *, k: float, cap_multiplier: float,
                       traditional_rate: float) -> dict:
    """
    输入 raw 至少含: name, hours, accuracy, complexity, pool_size
    输出追加: scarcity, contribution, cap, traditional_income
    """

def calculate_once(
    contributors: list[dict],
    *,
    profit: float = 20000.0,
    platform_share: float = 0.30,
    k: float = 0.01,
    cap_multiplier: float = 300.0,
    traditional_rate: float = 5.0,
) -> dict:
    """
    返回:
    {
      "contributors": [  # 每人 enrichment + share_pct + profit(单次应分)
        {
          "name", "hours", "accuracy", "complexity", "pool_size",
          "scarcity", "contribution", "cap", "traditional_income",
          "share_pct",  # 0-100，保留1位小数即可
          "profit"      # 单次 raw 应分（不考虑上限）
        }, ...
      ],
      "total_contribution": float,
      "distributable": float,
      "platform_profit": float,          # 单次
      "total_traditional": float,       # sum(traditional_income)
    }
    """

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
    """
    返回:
    {
      "contributors_meta": [... enrichment 字段 ...],
      "total_contribution": float,
      "calls": [
        {
          "call_index": 1-based int,
          "platform_profit": float,
          "items": [
            {
              "name": str,
              "raw_profit": float,
              "credited": float,
              "to_pool": float,
            }, ...
          ]
        }, ...
      ],
      "cumulative_by_contributor": {name: float, ...},  # 截断后累计入账
      "excess_to_pool": {name: float, ...},
      "cap_by_contributor": {name: float, ...},
      "traditional_by_contributor": {name: float, ...},
      "total_platform": float,
      "total_pool": float,
      "total_worker_income": float,  # sum(cumulative)
      "total_traditional": float,
    }
    """
```

函数名可微调，但 **I/O 语义必须等价**。`api/main.py` 只做校验与编排，不重写公式。

### 5.3 `share_pct` 计算

```
share_pct = round(contribution / total_contribution * 100, 1)
```

---

## 6. API 规格

### 6.1 依赖 `api/requirements.txt`

```
fastapi>=0.110
uvicorn>=0.27
pydantic>=2
```

### 6.2 模型 `api/models.py`（Pydantic v2）

必须包含的字段（可增减校验，不可缺默认业务字段）：

```python
from pydantic import BaseModel, Field, field_validator

class ContributorInput(BaseModel):
    name: str = Field(min_length=1)
    hours: float = Field(gt=0)
    accuracy: float = Field(gt=0, le=1)      # 0-1
    complexity: int = Field(ge=1, le=5)      # 1-5 整数乘数
    pool_size: int = Field(ge=0)

class GlobalParams(BaseModel):
    k: float = 0.01
    profit_per_call: float = 20000.0
    platform_share: float = Field(default=0.30, ge=0, le=1)
    cap_multiplier: float = 300.0
    traditional_rate: float = 5.0

class CalculateRequest(BaseModel):
    contributors: list[ContributorInput] = Field(min_length=1)
    profit: float = 20000.0                 # 单次利润，语义=profit_per_call
    k: float = 0.01
    platform_share: float = 0.30
    cap_multiplier: float = 300.0
    traditional_rate: float = 5.0

class ContributorCalcItem(BaseModel):
    name: str
    hours: float
    accuracy: float
    complexity: int
    pool_size: int
    scarcity: float
    contribution: float
    share_pct: float
    profit: float                 # 单次应分
    cap: float
    traditional_income: float

class CalculateResponse(BaseModel):
    results: list[ContributorCalcItem]
    total_contribution: float
    distributable: float
    platform_profit: float
    total_traditional: float

class SimulateRequest(BaseModel):
    contributors: list[ContributorInput] = Field(min_length=1)
    profit_per_call: float = 20000.0
    timeline_calls: int = Field(default=5, ge=1, le=200)      # 时间轴
    projection_calls: int = Field(default=50, ge=1, le=500)   # 对比卡片
    k: float = 0.01
    platform_share: float = 0.30
    cap_multiplier: float = 300.0
    traditional_rate: float = 5.0

class CallItem(BaseModel):
    name: str
    raw_profit: float
    credited: float
    to_pool: float

class PerCallResult(BaseModel):
    call_index: int
    platform_profit: float
    items: list[CallItem]

class ContributorSimSummary(BaseModel):
    name: str
    contribution: float
    share_pct: float
    cap: float
    traditional_income: float
    cumulative_income: float      # timeline 段累计
    excess_to_pool: float         # timeline 段入池
    projection_income: float      # projection 段累计（对比卡用）
    projection_excess: float      # projection 段入池

class SimulateResponse(BaseModel):
    calls: list[PerCallResult]                 # 仅 timeline_calls
    summaries: list[ContributorSimSummary]
    total_platform_timeline: float
    total_pool_timeline: float
    total_worker_income_timeline: float
    # 对比卡片用（projection）
    total_traditional: float
    total_worker_income_projection: float
    total_pool_projection: float
    total_platform_projection: float
    projection_calls: int
    timeline_calls: int
```

> 若实现者合并模型字段名，前端与第 8 节验收数字仍须对得上。

### 6.3 路由 `api/main.py`

| 方法 | 路径 | 行为 |
|---|---|---|
| `POST` | `/api/calculate` | 调 `calculate_once`，返回 `CalculateResponse` |
| `POST` | `/api/simulate` | 分别按 `timeline_calls`、`projection_calls` 调 `simulate_calls`，组装 `SimulateResponse` |
| `GET` | `/` | 返回 `web/index.html` |
| `GET` | `/health` | `{"status":"ok"}`（便于自检） |

静态资源（必须）：

```python
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")
```

前端引用：

```html
<link rel="stylesheet" href="/static/style.css" />
<script src="/static/app.js" defer></script>
```

也可把 `style.css` / `app.js` 直接挂在根路径；**必须保证这三个 URL 都能 200**。

启动方式（写在 `main.py` 底部）：

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
```

用户命令：

```bash
cd engine
pip install -r api/requirements.txt
python -m api.main
# 打开 http://127.0.0.1:8000
```

CORS：同域托管静态页即可，**不必**上复杂 CORS；若要单独用 `file://` 打开 HTML，再加 `CORSMiddleware`（非必须）。

### 6.4 请求 / 响应示例

#### `POST /api/calculate`

请求：

```json
{
  "contributors": [
    {"name": "张医生-罕见病", "hours": 40, "accuracy": 0.96, "complexity": 5, "pool_size": 3},
    {"name": "李标注-常见病", "hours": 80, "accuracy": 0.94, "complexity": 2, "pool_size": 10000},
    {"name": "王工程师-影像", "hours": 60, "accuracy": 0.98, "complexity": 4, "pool_size": 500}
  ],
  "profit": 20000,
  "k": 0.01,
  "platform_share": 0.3,
  "cap_multiplier": 300,
  "traditional_rate": 5
}
```

响应关键断言（允许浮点 ±0.02）：

| 人 | scarcity | contribution | share_pct | traditional | 单次 profit |
|---|---|---|---|---|---|
| 张医生 | 0.9709 | 186.41 | 82.1 | 200 | ≈11491.08 |
| 李标注 | 0.0099 | 1.49 | 0.7 | 400 | ≈91.85 |
| 王工程师 | 0.1667 | 39.21 | 17.3 | 300 | ≈2417.07 |

- `total_contribution ≈ 227.11`
- `distributable = 14000`
- `platform_profit = 6000`
- `total_traditional = 900`

#### `POST /api/simulate`（默认 timeline=5, projection=50）

响应关键断言：

**timeline（5 次）后：**

| 人 | cumulative | excess |
|---|---|---|
| 张医生 | 55923.00 | ≈1532.40 |
| 李标注 | 447.00 | ≈12.25 |
| 王工程师 | 11763.00 | ≈322.35 |

- `total_worker_income_timeline = 68133.00`
- `total_pool_timeline ≈ 1867.00`
- `total_platform_timeline = 30000.00`

**projection（50 次）——对比卡片：**

| 字段 | 值 |
|---|---|
| `total_traditional` | 900 |
| `total_worker_income_projection` | 68133.00 |
| `total_pool_projection` | 631867.00 |
| `total_platform_projection` | 300000.00 |
| 张医生 `projection_income` | 55923.00 |

---

## 7. 前端规格 `web/`

### 7.1 技术约束

| 项 | 选择 |
|---|---|
| 框架 | 原生 HTML/CSS/JS，**禁止** React/Vue/打包器 |
| 图表 | Chart.js 4.x CDN |
| 请求 | `fetch` + `JSON` |
| 动画 | CSS transition + 少量 `setTimeout`；禁止引入动画库 |

Chart.js CDN 示例：

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
```

### 7.2 页面信息架构（一块屏讲完）

```
┌──────────────────────────────────────────────────────────┐
│ 标题：数据要素贡献值分配 Demo                               │
│ 副标题：一次劳动，N 次增值 — 工业买断 vs AI 持续分润           │
├─────────────────────────┬────────────────────────────────┤
│ 左：输入区               │ 右上：贡献占比 / 单次分配柱状图     │
│ 1) 全局参数              │      (Chart.js bar)             │
│    k, 单次利润, 公共服务比例, │                              │
│    上限倍数, 传统单价,     │ 右下：多轮时间轴                 │
│    时间轴轮数, 长期推演轮数 │   ●─1─●─2─●─3─...              │
│ 2) 贡献者列表（可增删）    │   点击某轮 → 明细面板/弹层        │
│ 3) [计算贡献值]           │                              │
│    [模拟持续调用]         │                              │
├─────────────────────────┴────────────────────────────────┤
│ 对比卡片 ×3：工业时代合计 | AI时代劳动者合计 | 公共基金池      │
│ 可选金句：张医生 ¥200 → ¥55,923                            │
└──────────────────────────────────────────────────────────┘
```

### 7.3 预填默认数据

页面加载时预填与 `simulate.py` 相同的三人 + 默认全局参数，打开就能点，不必先手填。

### 7.4 交互流程（必须按此接线）

| 用户操作 | 前端行为 | API |
|---|---|---|
| 点击「计算贡献值」 | 调 calculate → 更新柱状图（贡献值或单次分润）+ 显示每人稀缺性/贡献值表；**对比卡的工业合计可更新，但 AI/池两卡不要用这次结果假装填满** | `POST /api/calculate` |
| 点击「模拟持续调用」 | 调 simulate → 渲染时间轴；用 **projection** 字段更新三张对比卡；缓存 `calls` 供点击 | `POST /api/simulate` |
| 点击时间轴第 N 轮 | 展示该轮每人 `raw_profit / credited / to_pool` | 本地缓存 |
| 修改全局参数后重算 | 按当前按钮语义重新请求 | 同上 |
| 添加/删除贡献者 | 至少支持 1–8 人；删除到 0 人时按钮禁用 | — |

建议：第一次进入页面自动跑一次 `simulate`（或 calculate+simulate），直接展示完整故事；若嫌吵，至少自动 `calculate`。

### 7.5 柱状图内容

推荐两组切换或并排一种即可：

1. **贡献值**（张/李/王）  
2. **单次分润**（三人 + 公共服务扣款）

公共服务扣款金额 = `platform_profit`（单次）。

### 7.6 时间轴 UX

- 节点数 = `timeline_calls`（默认 5）
- 入场可用依次点亮（`setTimeout` 间隔 200–400ms）
- 若某轮某人 `to_pool > 0`，该节点或明细标「触达上限」
- 明细用简单面板即可，不必模态库

### 7.7 文案要点（中文）

- 标题不要空泛「智能分配平台」；点明「贡献值 / 持续分润 / 公共池」
- 参数旁短说明：
  - `k`：稀缺性衰减；N 越大 S 越小
  - 公共服务比例：税收+基础设施，归公共财政
  - 上限倍数：累计收入 > 贡献值×倍数 → 超额入公共池
- 页脚一行小字：「本页为机制演示 Demo，非完整生产系统（无链、无登录、无持久化）」

### 7.8 UI 风格（简洁务实）

- 单栏/双栏清晰排版，偏演示文档风，不要花哨仪表盘
- 不要紫色科技风、不要过量玻璃拟态
- 对比卡片数字要大、可读
- 桌面宽度优先（≥1200px 舒适）；不做完整移动端适配（边界允许）

### 7.9 `app.js` 模块划分建议

```
- state: 表单数据、上次 calculate/simulate 响应
- collectForm(): 序列化为 API body
- apiCalculate() / apiSimulate()
- renderTable() / renderChart() / renderTimeline() / renderCompareCards()
- bindEvents()
```

不要上 TypeScript。

---

## 8. 黄金验收样例（实现完成后必须自测）

默认参数：

```
k=0.01, profit=20000, platform_share=0.30,
cap_multiplier=300, traditional_rate=5,
timeline_calls=5, projection_calls=50
```

贡献者：

```
张医生-罕见病: 40h, 0.96, C=5, N=3
李标注-常见病: 80h, 0.94, C=2, N=10000
王工程师-影像: 60h, 0.98, C=4, N=500
```

中间量：

```
张: S=0.9709, contrib=186.41, cap=55923.00, trad=200
李: S=0.0099, contrib=1.49,   cap=447.00,   trad=400
王: S=0.1667, contrib=39.21,  cap=11763.00, trad=300
total_contrib=227.11
```

最终演示数字（页面上必须能看到）：

| 展示位 | 期望 |
|---|---|
| 工业时代卡片 | ¥900 |
| AI 时代卡片（50 次推演劳动者合计） | ¥68,133 |
| 公共池卡片（50 次） | ¥631,867 |
| 个人金句（张医生） | ¥200 → ¥55,923 |

允许展示格式化为千分位；数值四舍五入到整数展示时须与上表一致。

**自动化建议**：对 `calculator.py` 写 3–5 个 assert；或用 `curl` 打两个 API 对比 JSON。

---

## 9. 实施顺序（按此提交）

| 步骤 | 产出 | 完成标准 |
|---|---|---|
| 1 | `core/calculator.py` | 黄金样例纯函数断言通过 |
| 2 | `api/models.py` + `api/main.py` + `requirements.txt` | curl 两接口数字正确；`/` 与静态资源 200 |
| 3 | `web/index.html` 骨架 + 预填表单 | 浏览器能看到表单 |
| 4 | `web/app.js`：calculate → 表 + 柱状图 | 数字与第 8 节 calculate 一致 |
| 5 | `web/app.js`：simulate → 时间轴 + 对比卡 | 三张卡为 900 / 68133 / 631867 |
| 6 | `web/style.css` | 桌面可读、对比数字突出 |
| 7 | README 片段（可写在 `engine/README.md` 或本文件末尾） | 含启动命令 |

预估总工时约 6–8 小时。

---

## 10. 明确不做

- ❌ 用户系统 / JWT / OAuth  
- ❌ 数据库 / Redis / 文件持久化  
- ❌ 区块链、合约、钱包  
- ❌ Docker / K8s / Nginx 配置（本机 uvicorn 即可）  
- ❌ 完整移动端响应式  
- ❌ 轨道 B–E、消费者池、历史贡献回流 UI  
- ❌ 正式文档 A 因子表 / L 权重表（除非另开任务）  
- ❌ 改仓库根 README 大结构（除非需要加一行启动说明）  
- ❌ 提交密钥、`.env` 机密  

---

## 11. 与全方案文档的关系（实现者勿混淆）

| 文档 | 用途 |
|---|---|
| `docs/01–05` | 完整制度与架构；**不要在本 Demo 实现其全部** |
| `engine/simulate.py` | **本 Demo 数值与算法的唯一对齐源** |
| 本 `ARCHITECTURE.md` | **本 Demo 的实现规格** |

若正式文档与 `simulate.py` 冲突（例如准确率因子表），**本任务跟 `simulate.py`**。

---

## 12. 交付检查清单（PR / 交卷前打勾）

- [ ] `cd engine && pip install -r api/requirements.txt && python -m api.main` 可启动  
- [ ] 打开 `http://127.0.0.1:8000` 有预填三人  
- [ ] `/api/calculate` 与第 8 节中间量一致  
- [ ] `/api/simulate` 对比卡三数：900 / 68133 / 631867  
- [ ] 时间轴可点开每轮 `raw/credited/to_pool`  
- [ ] 文案中公共服务份额被描述为公共财政，而非私有抽成  
- [ ] 无构建步骤、无多余框架  
- [ ] 计算集中在 `core/calculator.py`，路由内无复制公式  

---

## 13. 给实现 LLM 的最终提示词（可原样粘贴）

```
请严格按 engine/ARCHITECTURE.md 实现该 Demo。
算法与数值对齐 engine/simulate.py，以 ARCHITECTURE 第 8 节黄金样例为验收标准。
只新增/修改 engine/core、engine/api、engine/web 下文件；不要实现区块链/数据库/登录。
完成后在本地启动并用默认样例证明：工业时代 ¥900、AI 时代 ¥68,133、公共池 ¥631,867，
以及张医生 ¥200 → ¥55,923。
```
