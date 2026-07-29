# 贡献值分配系统 Demo — 代码架构方案

## 一、系统概览

```
浏览器 (HTML/CSS/JS + Chart.js)
    │
    │  POST /api/calculate      贡献值计算
    │  POST /api/simulate       多轮调用模拟
    │
    ▼
FastAPI 后端 (Python)
    │
    ├── calculator.py           核心计算引擎（从 simulate.py 抽离）
    ├── models.py              请求/响应数据模型 (Pydantic)
    └── main.py                路由 & 服务入口
```

**一句话**：用户在 Web 页面填入贡献者数据 → 后端跑公式 → 前端画分配图表 + 时间轴动画。

---

## 二、文件结构

```
engine/
├── simulate.py              # 现有 CLI 脚本，保留不动
├── core/
│   ├── __init__.py
│   └── calculator.py        # 纯函数计算引擎（无副作用，可独立测试）
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app，定义路由
│   ├── models.py            # Pydantic 请求/响应模型
│   └── requirements.txt     # fastapi, uvicorn, pydantic
├── web/
│   ├── index.html           # 单页应用入口
│   ├── style.css            # 全局样式
│   └── app.js               # 前端逻辑（表单提交、图表渲染、动画）
└── ARCHITECTURE.md          # 本文件
```

---

## 三、核心计算引擎 `core/calculator.py`

**设计原则**：所有计算逻辑从 `simulate.py` 抽离为纯函数，不依赖任何框架，接受输入 → 返回结果。

```python
# 函数签名（示例）

def calc_scarcity(pool_size: int, k: float = 0.01) -> float:
    """稀缺性系数 S = 1/(1 + k * N)"""
    ...

def calc_contribution(hours: float, accuracy: float,
                      complexity: int, scarcity: float) -> float:
    """轨道A: 贡献值 = T × A × C × S"""
    ...

def calc_distribution(contributors: list[dict],
                       profit: float,
                       platform_share: float = 0.30) -> dict:
    """单次利润分配，返回每人分多少 + 平台拿多少"""
    ...

def simulate_calls(contributors: list[dict],
                   profit_per_call: float,
                   num_calls: int,
                   cap_multiplier: float = 300,
                   platform_share: float = 0.30) -> dict:
    """多轮调用模拟，返回累计收入 + 超额入池 + 平台收入"""
    ...
```

**产出**：`calculator.py` 约 80 行，纯 Python，零依赖，可直接被 `simulate.py` 和 `api/main.py` 共同引用。

---

## 四、后端 API 设计 `api/`

### 4.1 数据模型 `models.py`

```python
from pydantic import BaseModel

class ContributorInput(BaseModel):
    name: str           # 贡献者名称
    hours: float        # 工时
    accuracy: float     # 准确率 (0-1)
    complexity: int     # 复杂度等级 L1-L5
    pool_size: int      # 数据类型存量 N

class CalculateRequest(BaseModel):
    contributors: list[ContributorInput]
    profit: float = 20000.0
    platform_share: float = 0.30
    cap_multiplier: float = 300.0

class ContributorResult(BaseModel):
    name: str
    contribution: float
    share_pct: float
    profit: float

class CalculateResponse(BaseModel):
    results: list[ContributorResult]
    total_contribution: float
    platform_profit: float

class SimulateRequest(BaseModel):
    contributors: list[ContributorInput]
    profit_per_call: float = 20000.0
    num_calls: int = 5
    cap_multiplier: float = 300.0
    platform_share: float = 0.30

class PerCallResult(BaseModel):
    call_index: int
    distribution: list[ContributorResult]
    platform_profit: float

class SimulateResponse(BaseModel):
    calls: list[PerCallResult]            # 每轮分配明细
    cumulative_by_contributor: dict      # 每人累计收入
    excess_to_pool: dict                 # 每人超额入池
    total_platform: float                # 平台总收益
    total_pool: float                    # 公共池总积累
```

### 4.2 路由 `main.py`

| 方法 | 路径 | 功能 | 前端使用场景 |
|------|------|------|------------|
| POST | `/api/calculate` | 单次分配计算 | 用户填完表单点"计算" |
| POST | `/api/simulate` | 多轮调用模拟 | 展示时间轴动画 |
| GET  | `/` | 静态文件服务 | 返回 `web/index.html` |

### 4.3 运行方式

```bash
cd engine
pip install fastapi uvicorn
python -m api.main
# 浏览器打开 http://localhost:8000
```

---

## 五、前端设计 `web/`

### 5.1 页面布局

```
┌─────────────────────────────────────────────┐
│  数据要素贡献值分配 Demo                       │
├──────────────────────┬──────────────────────┤
│                      │                      │
│  贡献者输入表单        │  分配结果柱状图        │
│  ┌────────────────┐  │  (Chart.js Bar)      │
│  │ 姓名: [____]   │  │                      │
│  │ 工时: [____]   │  │  ████████ 张医生      │
│  │ 准确率: [__]   │  │  ██ 李标注           │
│  │ 复杂度: [L1-L5]│  │  ████ 王工程师       │
│  │ 存量N: [____]  │  │  ██ 公共服务平台      │
│  │ [+ 添加贡献者] │  │                      │
│  │ [提交计算]     │  │                      │
│  └────────────────┘  │                      │
│                      ├──────────────────────┤
│                      │                      │
│                      │  持续调用时间轴        │
│                      │ ★─第1次→★─第2次→...  │
│                      │ (点击每次查看分配明细)  │
│                      │                      │
├──────────────────────┴──────────────────────┤
│  底部：传统 vs AI 时代 对比卡片               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ 工业时代  │  │ AI 时代  │  │ 公共池   │  │
│  │ ¥  900   │  │ ¥68,133 │  │ ¥631,867│  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────┘
```

### 5.2 核心交互

| 用户操作 | 前端行为 | API 调用 |
|---------|---------|---------|
| 填完表单 → 点"计算" | 发请求 → 渲染柱状图 + 对比卡片 | POST `/api/calculate` |
| 点"模拟多轮调用" | 发请求 → 渲染时间轴 + 每轮明细 | POST `/api/simulate` |
| 点时间轴上某一轮 | 弹出该轮三人分配明细 | 本地缓存，不发请求 |
| 调整全局参数（k, 平台比例, 上限倍数） | 重新计算，图实时刷新 | POST `/api/calculate` |

### 5.3 技术选型

| 层 | 选择 | 理由 |
|---|---|---|
| 框架 | 原生 HTML/CSS/JS | 零构建工具，一个文件就够，面试官一眼看穿 |
| 图表 | Chart.js CDN | 三条 bar 的柱状图，不配用 ECharts |
| 动画 | CSS transition + JS `setTimeout` | 时间轴呼吸动效，不引入动画库 |
| 请求 | `fetch()` | 原生，不需要 axios |

---

## 六、实施步骤（按优先级）

| 步骤 | 产出 | 预估 |
|------|------|------|
| 1 | 从 `simulate.py` 抽 `core/calculator.py` 纯函数 | 1h |
| 2 | `api/models.py` + `api/main.py` 后端接口 | 1h |
| 3 | `web/index.html` 静态页面骨架 + 表单 | 1h |
| 4 | `web/app.js` 柱状图 + 对比卡片 | 1h |
| 5 | 时间轴动画 + 每轮明细弹窗 | 1.5h |
| 6 | `web/style.css` 样式美化 | 1h |
| — | **总计** | **~7h** |

---

## 七、不做的事（明确边界）

- ❌ 不做用户登录/注册
- ❌ 不做数据持久化（不接数据库）
- ❌ 不做区块链/智能合约
- ❌ 不做响应式移动端适配
- ❌ 不做 Docker 部署

Demo 的唯一目的：**面试官打开浏览器，填三个人的数据，点一下按钮，三十秒内看到"工业时代 ¥200 → AI 时代 ¥55,923"。**
