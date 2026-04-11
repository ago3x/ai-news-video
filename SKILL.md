---
name: ai-news-video
description: |
  AI新闻短视频全自动生成工具。从新闻主题到成品视频的一键生成。
  
  **适用场景**：
  - 用户要求制作AI/科技类短视频
  - 需要从新闻生成竖屏视频内容
  - 批量生成资讯类视频
  - 用户提到"短视频制作"、"生成视频"、"AI视频"
  - 用户提到"新闻视频"、"资讯短视频"、"科技资讯"、"做个视频"
  - 用户想批量产出内容矩阵、自媒体素材
  
  **功能**：
  - 自动搜索AI新闻热点
  - Agent生成口播脚本（分镜文案）
  - Agent根据脚本编写对应数量的HTML页面（3~6个，由内容决定）
  - HTML页面 + Playwright录制
  - TTS配音生成（edge-tts）
  - 音视频智能同步
  - 输出完整竖屏视频（1080×1920）
---

# AI新闻短视频生成器

## 架构分工

```
┌─────────────────────────────────────┐
│            Agent 负责               │
│  1. 搜索新闻 / 理解主题              │
│  2. 生成口播文稿（N段，由内容决定）   │
│  3. 根据文稿编写N个HTML页面          │
└──────────────┬──────────────────────┘
               │ 口播文稿 + HTML文件
               ▼
┌─────────────────────────────────────┐
│         Python 脚本负责              │
│  4. TTS生成配音                     │
│  5. 按静音点切分配音                 │
│  6. Playwright录制HTML              │
│  7. 音视频合并 + 拼接输出            │
└─────────────────────────────────────┘
```

---

## Agent 工作流程

### Step 1：搜索/理解新闻

用搜索工具获取该主题的最新信息，整理出：
- 核心事件（一句话）
- 关键数据（数字、价格、参数等）
- 主要特性/变化（3~4条）
- 对比信息（新旧/竞品对比）
- 意义/影响

> 也可直接调用辅助脚本批量抓取：`python scripts/search_news.py "搜索关键词"`

---

### Step 2：生成口播文稿

根据新闻内容决定镜头数量，以"每段讲清一个点、节奏不拖沓"为准。

---

#### 第一步：先定镜头数量

在写任何文案之前，先用以下决策树确定本次需要几个镜头：

```
新闻信息量评估
│
├── 只有 1 个核心事件，无需对比、无复杂背景
│   → 3 个镜头（钩子 + 核心信息 + 共鸣）
│
├── 有 1~2 个核心亮点 + 简单背景或价格信息
│   → 4 个镜头（钩子 + 亮点 + 数据/价格 + 共鸣）
│
├── 有 3+ 个维度（功能 + 对比 + 背景 + 影响）
│   → 5 个镜头（钩子 + 背景 + 亮点 + 对比 + 共鸣）
│
└── 深度报道：有时间线、多方角色、复杂影响
    → 6 个镜头（可拆分亮点或背景为 2 个镜头）
```

**硬性约束**：
- **最少 3 个**：钩子 + 至少一个信息镜头 + 共鸣，再少就撑不起节奏
- **最多 6 个**：单条视频总时长不超过 60 秒，超过观众会划走
- **不要凑数**：内容只够 3 个镜头，绝不硬拆成 4 个；内容可以讲 5 个点，不要压缩成 3 个

---

#### ⚠️ 文案核心原则：讲故事，不写说明书

**禁止** 这样写（产品说明书风格）：
> "GPT-5带来四大升级：推理能力提升10倍、多模态全面增强、响应速度快3倍、上下文扩展到100万token！"

**应该** 这样写（有钩子、有冲突、有情绪）：
> "等了整整一年，发布会结束那一刻，所有人都沉默了——不是因为太震撼，是因为看到了那个价格。"

两者信息量相同，但后者让人停住、想看下去。

---

#### 故事骨架（四个叙事环节，≠ 四个镜头）

> ⚠️ 这里的①②③④是**叙事功能**，不是镜头数量。3 个镜头的视频同样覆盖四个环节，中间两个环节可以合并在一个镜头里讲。

| 叙事环节 | 功能 | 镜头映射规则 |
|---------|------|------------|
| **① 钩子** | 制造悬念 / 反差 / 震惊，让观众停住 | 永远是第 1 个镜头，独占一个镜头 |
| **② 冲突** | 揭示矛盾、落差、意外，让观众代入 | 简单新闻可并入③；内容足够时独立一个镜头 |
| **③ 爆料** | 核心数据 / 事实集中引爆 | 数据多时可拆成 2 个镜头（功能 + 价格），数据少时与②合并 |
| **④ 共鸣** | 与观众产生连接，引导互动 | 永远是最后一个镜头，独占一个镜头 |

**示例映射**：
- 3 镜头：① → ②③合并 → ④
- 4 镜头：① → ② → ③ → ④
- 5 镜头：① → ② → ③功能 → ③价格 → ④
- 6 镜头：① → ②背景 → ③功能 → ③数据 → ③对比 → ④

---

#### 钩子公式（第一镜必须用其中一种）

**公式1 — 数字炸弹**（用一个让人说"不可能"的数字开场）
> "刚刚，这家公司宣布：用了不到 3 天，把竞争对手逼到停止更新。"

**公式2 — 反差冲击**（先给出普通认知，再颠覆）
> "所有人都以为这次只是小更新，直到打开参数表的那一秒……"

**公式3 — 身份代入**（让观众感到"这说的是我"）
> "如果你现在还在用免费版，这条视频可能改变你的想法。"

**公式4 — 悬念设置**（抛出问题，答案藏在后面）
> "为什么全球最顶尖的实验室，同一天集体噤声了？"

---

#### 冲突设计（每条文案至少要有一处"意料之外"）

| 冲突类型 | 写法模板 |
|---------|---------|
| 期望 vs 现实 | "以为只是升级，结果是颠覆" / "说好的降价，账单却……" |
| 新 vs 旧 | "过去需要一个团队做的事，现在一个人10分钟搞定" |
| 大 vs 小 | "一个参数的差距，性能天壤之别" |
| 快 vs 慢 | "竞争对手还在开发布会，它已经开始收费了" |
| 官方 vs 真相 | "官方没说，但数据已经说明一切" |

---

#### 情绪词库（让文案有温度，避免干燥罗列）

- **紧迫感**：刚刚 / 突然 / 悄悄 / 正在 / 已经 / 今天凌晨
- **震惊**：炸了 / 颠覆 / 疯了 / 没想到 / 惊呆 / 沉默了
- **悬念**：背后 / 真相 / 原来 / 没人说 / 直到……
- **代入**：如果你 / 你还在 / 你用过吗 / 这就是为什么你
- **对比**：整整 / 相比之下 / 而它 / 但问题是 / 代价是

---

#### 技术参数

- **语言**：口语化短句，单句不超过15字，适合TTS朗读
- **每段时长**：5~10秒（约50~100字）
- **节奏节拍**：钩子快→冲突快→爆料中→共鸣慢，有呼吸感

---

**输出目录规则**：

在 Step 2 开始前，先根据主题生成一个英文短标识（slug），格式为 `{关键词}-{YYYYMMDD}`，例如：
- "OpenAI 发布 GPT-5" → `openai-gpt5-20260410`
- "A股今日行情" → `a-stock-20260410`
- "小米 MiMo 模型" → `xiaomi-mimo-20260410`

所有文件（script.json、shot*.html、生成的 mp3/mp4）都保存到 `output/{slug}/` 子目录下。

**输出格式**（保存为 `output/{slug}/script.json`）：

```json
{
  "topic": "OpenAI 发布 GPT-5",
  "shots": [
    {
      "id": "shot1",
      "type": "cover",
      "narration": "等了整整一年，发布会结束那一刻，所有人都沉默了——不是因为太震撼，是因为看到了那个价格。"
    },
    {
      "id": "shot2",
      "type": "stats",
      "narration": "推理能力提升10倍，这不是吹牛——数学竞赛满分，代码测试第一，GPT-4做不到的，它全做到了。"
    },
    {
      "id": "shot3",
      "type": "compare",
      "narration": "但代价呢？免费版有限制，Plus还是20美元，Pro版直接飙到200美元一个月——是Plus的整整10倍。"
    },
    {
      "id": "shot4",
      "type": "ending",
      "narration": "所以问题来了：你愿意为真正的智能，每个月多付多少钱？还是继续凑合用免费版？评论区说说你的想法。"
    }
  ]
}
```

> 此示例为 4 镜头版（有功能亮点 + 价格对比，信息量适中）。如果新闻内容更简单，应该用 3 个镜头；如果有更多维度（时间线、多模型对比、生态影响），应该用 5~6 个镜头。**不要默认复制这个结构**，先做镜头数量决策再写文案。`shots` 数组可多可少，Python 脚本自动处理。

---

### Step 3：根据口播文稿编写HTML页面

**关键原则**：每个HTML页面的视觉内容必须与对应段口播文案完全匹配——口播提到什么数字、什么功能、什么对比，页面就显示什么。

为 `script.json` 中的**每一个** shot 生成对应的HTML文件，保存到 `output/{slug}/` 目录（与 script.json 同级），文件名与 `id` 字段一致（如 `shot1.html`、`shot2.html`……）。

镜头数量由 Step 2 的口播文稿决定，常见版式参考：

| type 建议值 | 适用场景 | 版式示意 |
|------------|---------|---------|
| `cover` | 开篇钩子 | 大标题 + 核心数字 + 副标题 |
| `features` | 功能/特性列举 | 网格卡片，每格对应口播一个要点 |
| `compare` | 数据/版本对比 | 多栏对比表，数据与口播完全对应 |
| `timeline` | 事件时间线 | 纵向时间轴 |
| `quote` | 引用/金句 | 大字居中引用 + 来源 |
| `stats` | 数据可视化 | 大数字 + 说明文字 |
| `ending` | 总结互动 | 要点摘要 + 互动问题 |

> type 仅作版式参考，实际根据口播内容自行选择最合适的版式，也可自创。

---

#### ⚠️ 视觉强制要求：禁止纯文字卡片

**纯文字列表 = 不合格**。每个镜头都必须有让人眼前一亮的视觉元素。

**按镜头内容的强制规则**：

| 镜头内容 | 强制要求 | 禁止 |
|---------|---------|------|
| 封面 / 钩子 | 超大字（h1 ≥ 3.6em）+ 背景光晕动画 `.glow` | 普通文字居中 |
| 包含具体数字 | **必须** countUp 滚动动画，数字从 0 跑到目标值 | 静态写死数字 |
| 3+ 组对比数据 | **必须** SVG 柱状图或多栏布局，色彩区分高低 | 纯文字列表 |
| 占比 / 进度 | **必须** 进度条或环形图动画 | 用文字写"占 X%" |
| 功能列举 | lucide 图标 + 文字，fragment 逐条入场 | 无图标的纯文字列表 |
| 结尾 | 互动问题放入醒目边框卡片，背景有装饰色块 | 白底黑字纯文本 |

**全视频强制**：每条视频必须有至少一个"**数字炸弹镜头**"——用 `font-size: 5em+` 展示最震撼的核心数字，配 countUp 动画，这是全片最强视觉冲击点，通常放在 shot2 或 shot3。

**每个镜头必须有动态元素**：要么 fragment 逐条入场，要么 CSS animation，两者都没有的镜头是不合格的。

---

**HTML规范**：

#### 框架：Reveal.js（竖屏 PPT）

每个 shot HTML 使用 **Reveal.js** 构建，像 PPT 一样逐条展示要点，配合配音节奏自动推进。

**CDN 引入**（优先用 jsDelivr，国内访问更稳定）：
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/theme/black.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
```

> jsDelivr 如不可用，备用：`https://cdnjs.cloudflare.com/ajax/libs/reveal.js/5.0.4/`

**初始化配置**（竖屏 + 无控件 + 自动推进 fragment）：
```js
Reveal.initialize({
  controls: false,           // 隐藏 <> 导航按钮
  progress: false,           // 隐藏底部进度条
  transition: 'fade',
  transitionSpeed: 'fast',
  backgroundTransition: 'none',
  width: 1080,
  height: 1920,
  margin: 0.06,
  center: true,
});

// 自动推进 fragment：从 URL ?dur=N 读取配音时长，均匀分配每条要点的出现时机
Reveal.on('ready', () => {
  const dur = parseFloat(new URLSearchParams(location.search).get('dur') || '8');
  const frags = document.querySelectorAll('.fragment');
  if (!frags.length) return;
  // 留出片头 1s 展示标题，片尾 1s 留白，中间均匀分配
  const available = (dur - 2) * 0.9;
  const step = available / frags.length;
  frags.forEach((_, i) => {
    setTimeout(() => Reveal.nextFragment(), (1 + step * i) * 1000);
  });
});
```

> Python 脚本录制时会自动在 URL 末尾附加 `?dur=实际配音时长`，无需手动填写。

**要点逐条出现的写法**（用 `.fragment` 类）：
```html
<section>
  <h2>MiMo-V2-<span class="highlight">Pro</span></h2>
  <p>旗舰基座模型，专为 Agent 时代打造。</p>
  <ul>
    <li class="fragment">参数量突破 <strong>1 万亿</strong>，激活参数 42B</li>
    <li class="fragment">支持 <strong>100 万</strong> token 超长上下文</li>
    <li class="fragment">全球综合智能榜 <strong>前列</strong></li>
  </ul>
</section>
```

fragment 的动画默认是淡入，如需上移入场可加自定义 CSS：
```css
.reveal .fragment {
  transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.16,1,0.3,1);
}
.reveal .fragment.visible {
  transform: translateY(0) !important;
}
.reveal .fragment:not(.visible) {
  transform: translateY(20px);
}
```

---

#### 整体风格：苹果风 PPT
- 风格参考 Apple Keynote / WWDC：大留白、克制排版、信息分层清晰
- 每屏只表达**一个核心信息**，文字精简，视觉呼吸感强
- 避免堆砌文字，关键数字和词汇做大号强调

#### 背景与配色
- 背景：纯黑 `#000000`（Reveal.js black 主题默认，苹果风）
- 主文字：`#f5f5f7`（苹果白，非纯白，更柔和）
- 辅助强调色：从以下选 1~2 种，与内容基调匹配
  - 科技蓝 `#0071e3`（苹果官方蓝）
  - 活力青 `#00d4ff`
  - 警示红 `#ff453a`（苹果系统红）
  - 暖橙 `#ff9f0a`（苹果橙）
  - 次要文字 `#a1a1a6`（苹果灰）
- 卡片/分割线用 `rgba(255,255,255,0.06)` 半透明白

#### ⚠️ 语义配色：颜色必须符合领域常识

**配色不是纯美学决策，颜色承载语义。** 在动手选色前，先判断内容所在的领域约定：

| 领域 | 正面/上涨/好 | 负面/下跌/差 | 说明 |
|------|------------|------------|------|
| **A股 / 港股 / 中国股市** | 🔴 红色 `#ff453a` | 🟢 绿色 `#30d158` | 中国惯例：红涨绿跌 |
| **美股 / 欧股 / 国际市场** | 🟢 绿色 `#30d158` | 🔴 红色 `#ff453a` | 国际惯例：绿涨红跌 |
| **健康 / 医疗数据** | 🟢 绿色（正常）| 🔴 红色（异常）| 通用医学惯例 |
| **环保 / 碳排放** | 🟢 绿色（低碳）| 🔴 红色（高排）| 环保领域通识 |
| **危险 / 警告** | 🟢 绿色（安全）| 🔴 红色（危险）| 交通/工业通识 |

**规则**：
1. 制作金融/股市类视频时，**必须先确认市场归属**（中国 A 股还是美股），再选涨跌色
2. 不确定领域惯例时，优先查一查，不要默认用"绿色=好、红色=危险"的西方直觉
3. **同一个视频内颜色语义必须统一**，不能一处红涨、另一处绿涨

#### 字体（免费无版权）

> **国内网络说明**：`fonts.googleapis.com` 在大陆被屏蔽，Playwright 录制时会导致字体加载失败。请使用以下镜像或直接回退到系统字体。

```html
<!-- 国内镜像（推荐） -->
<link rel="preconnect" href="https://fonts.loli.net">
<link href="https://fonts.loli.net/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
```

若网络环境无法访问任何外部字体，去掉上面两行，`-apple-system / PingFang SC` 回退字体会自动生效，不影响画面效果。
覆盖 Reveal.js 默认字体：
```css
.reveal, .reveal h1, .reveal h2, .reveal h3 {
  font-family: 'Inter', -apple-system, 'PingFang SC', 'Noto Sans SC', sans-serif;
  text-transform: none;
  letter-spacing: -0.02em;
}
.reveal h1 { font-size: 3.6em; font-weight: 800; }
.reveal h2 { font-size: 2.6em; font-weight: 700; }
.reveal p  { font-size: 1.2em; font-weight: 300; color: #a1a1a6; }
.reveal ul { font-size: 1.15em; line-height: 2; color: #d2d2d7; }
.reveal li { margin-bottom: 12px; }
```

#### 图标
```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<i data-lucide="brain" style="width:56px;height:56px;color:#0071e3"></i>
<script>lucide.createIcons();</script>
```

常用图标参考：

| 场景 | 推荐图标 |
|------|---------|
| AI / 智能 | `brain`, `bot`, `sparkles`, `cpu` |
| 速度 / 性能 | `zap`, `rocket`, `gauge` |
| 价格 / 费用 | `dollar-sign`, `trending-up`, `trending-down` |
| 功能特性 | `layers`, `star`, `check-circle`, `shield` |
| 对比 | `git-compare`, `bar-chart-2`, `scale` |
| 结尾互动 | `message-circle`, `heart`, `share-2` |

#### 动画工具箱（按上方强制规则选用，均不影响 fragment 机制）

**数字计数**——数字从 0 滚动到目标值，配合 fragment 出现时触发：
```js
function countUp(el, target, ms = 1200) {
  const t0 = performance.now();
  const go = now => {
    const p = Math.min((now - t0) / ms, 1);
    el.textContent = Math.floor((1 - Math.pow(1 - p, 3)) * target).toLocaleString();
    if (p < 1) requestAnimationFrame(go);
  };
  requestAnimationFrame(go);
}
// 在 Reveal fragment 显示时触发
Reveal.on('fragmentshown', e => {
  e.fragment.querySelectorAll('[data-count]').forEach(el =>
    countUp(el, +el.dataset.count)
  );
});
```
用法：`<span data-count="1000000">0</span>`

**进度条**——适合能力评分、对比：
```css
@keyframes growBar {
  from { width: 0; }
  to   { width: var(--w); }
}
.bar { height: 10px; border-radius: 5px; background: #0071e3;
       animation: growBar 1s cubic-bezier(0.16,1,0.3,1) 0.3s both; }
```

**光晕脉冲**——背景装饰，增加科技感：
```css
@keyframes pulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50%       { opacity: 0.8; transform: scale(1.1); }
}
.glow { filter: blur(80px); animation: pulse 4s ease-in-out infinite; }
```

**扫光文字**——标题/数字强调：
```css
@keyframes shimmer {
  from { background-position: -200% center; }
  to   { background-position:  200% center; }
}
.shimmer {
  background: linear-gradient(90deg, #fff 30%, #0071e3 50%, #fff 70%);
  background-size: 200% auto;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  animation: shimmer 2.5s linear 0.5s both;
}
```

#### 图表（含数据时强制使用，内联 SVG / Canvas）

**选型规则**：
- 3+ 组对比数据 → SVG 柱状图（**强制**，不能用纯文字替代）
- 占比数据 → Canvas 环形图（**强制**）
- 趋势数据 → SVG 折线图
- 单一核心数字 → countUp 大数字（**强制**，配合数字炸弹镜头）

**SVG 柱状图**（从底部升起动画）：
```html
<svg viewBox="0 0 600 320" width="100%" style="max-width:700px">
  <rect x="50"  y="40"  width="100" height="240" rx="10" fill="#0071e3"
        style="transform-origin:50% 280px; animation:barRise 0.8s cubic-bezier(0.16,1,0.3,1) 0.4s both"/>
  <rect x="220" y="120" width="100" height="160" rx="10" fill="rgba(255,255,255,0.12)"
        style="transform-origin:50% 280px; animation:barRise 0.8s cubic-bezier(0.16,1,0.3,1) 0.6s both"/>
  <text x="100"  y="28" text-anchor="middle" fill="#fff" font-size="22" font-weight="700">1T</text>
  <text x="270" y="108" text-anchor="middle" fill="#a1a1a6" font-size="22">42B</text>
</svg>
<style>
@keyframes barRise { from { transform: scaleY(0); opacity:0; } to { transform: scaleY(1); opacity:1; } }
</style>
```

**Canvas 环形图**（动态绘制）：
```html
<canvas id="ring" width="360" height="360"></canvas>
<script>
const c = document.getElementById('ring').getContext('2d');
let p = 0;
(function draw() {
  c.clearRect(0,0,360,360);
  // 背景圆
  c.beginPath(); c.arc(180,180,130,-Math.PI/2,Math.PI*2-Math.PI/2);
  c.lineWidth=32; c.strokeStyle='rgba(255,255,255,0.08)'; c.stroke();
  // 进度弧
  c.beginPath(); c.arc(180,180,130,-Math.PI/2,-Math.PI/2+Math.PI*2*Math.min(p,1));
  c.lineWidth=32; c.strokeStyle='#0071e3';
  c.lineCap='round'; c.stroke();
  if(p<0.72){p+=0.018; requestAnimationFrame(draw);}
})();
</script>
```

#### 排版细节
- Reveal.js 的 `margin: 0.06` 提供足够留白，内容不要撑满
- 重要数字单独一行，在 Reveal 中用 `font-size: 4~6em` 大号展示
- 卡片圆角 `border-radius: 24px`，边框 `1px solid rgba(255,255,255,0.08)`
- 高亮文字用 `.highlight { color: #0071e3; font-weight: 600; }` 类统一

---

### Step 4：调用Python脚本完成技术管道

所有HTML写好后，调用（注意路径是子目录下的 script.json）：

```bash
python scripts/generate_video.py output/{slug}/script.json
```

例如：
```bash
python scripts/generate_video.py output/openai-gpt5-20260410/script.json
```

脚本会自动完成：TTS → 录制HTML → 音视频合并 → 拼接输出，并生成两个 Markdown：
- `output/{slug}/README.md`：本次生成说明（脚本、时长、视频链接）
- `output/README.md`：总目录，追加本次记录

---

## Python 脚本说明

脚本 `scripts/generate_video.py` 只负责技术管道，**不生成任何内容**。

**输入**：`output/{slug}/script.json` + `output/{slug}/shot*.html`（Agent 已写好）

**流程**：

```
1. 读取 script.json，提取每段口播文本
   ↓
2. TTS 生成配音 → output/{slug}/shot*.mp3
   ↓
3. Playwright 录制对应 HTML（时长 = 配音时长）
   ↓
4. 音视频逐段合并（淡入淡出）
   ↓
5. 拼接 → output/{slug}/final.mp4
   ↓
6. 生成 output/{slug}/README.md（本次说明）
   ↓
7. 追加更新 output/README.md（总目录）
```

**输出目录结构**：

```
output/
├── README.md                        ← 总目录（自动追加）
└── openai-gpt5-20260410/
    ├── script.json
    ├── shot1.html ~ shotN.html
    ├── shot1.mp3 ~ shotN.mp3
    ├── final.mp4                    ← 成品视频
    └── README.md                    ← 本次说明
```

**命令行**：

```bash
# 标准用法
python scripts/generate_video.py output/openai-gpt5-20260410/script.json

# 指定TTS语音
python scripts/generate_video.py output/openai-gpt5-20260410/script.json --voice zh-CN-YunxiNeural

# 指定语速
python scripts/generate_video.py output/openai-gpt5-20260410/script.json --rate -10%
```

---

## 依赖安装

```bash
pip install edge-tts playwright
playwright install chromium
# ffmpeg 需系统安装
```

---

## 视频规格

- **分辨率**：1080×1920（9:16竖屏）
- **帧率**：20fps
- **音频**：AAC，淡入淡出处理
- **格式**：MP4

---

## 常见问题

**Q: 口播和画面内容对不上？**  
A: 检查Step 3是否严格按照口播文稿来写HTML，每段口播的关键词必须在对应HTML中有对应的视觉元素。

**Q: 配音节奏太快/太慢？**  
A: 调整口播文稿字数（50字≈5秒，100字≈10秒），或在调用脚本时加 `--rate -10%` 减速。

**Q: 动画没有完全展示？**  
A: 增加HTML中最后一个动画元素的延迟时间，确保在配音结束前完成展示。

**Q: 中途某个镜头失败，想重跑怎么办？**  
A: 直接重新运行同一条命令，已生成的 `.mp3` 会自动跳过，只重新处理失败的部分。

**Q: 字体显示为方块/乱码？**  
A: Google Fonts 在国内被屏蔽，Playwright 无法加载。改用 `fonts.loli.net` 镜像或直接移除字体 CDN 引用（系统字体 PingFang SC 会自动兜底）。

**Q: Windows 上页面录制出来全黑？**  
A: 确认已更新到最新版脚本（`file://` URL 已修复为 `as_uri()` 格式）。旧版脚本在 Windows 生成的路径格式不正确。
