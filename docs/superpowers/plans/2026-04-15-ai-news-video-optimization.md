# AI News Video 优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 对 ai-news-video 工具进行整体优化，涵盖文案质量提升、视觉主题系统（4套）、模板库扩充（5→13种）、图片采集集成四个方向。

**Architecture:** SKILL.md 控制 Agent 行为（文案规则、图片采集、主题推断、模板选用），`assets/templates.json` 存放所有 13 种 HTML 模板（升级为 CSS 变量驱动），`scripts/generate_video.py` 新增 `--style` 参数支持。图片采集由 Agent 在搜索阶段用 Playwright 完成，保存到 `output/{slug}/images/`。

**Tech Stack:** Python 3, Playwright (已有), Reveal.js 5.0.4 (CDN), edge-tts (已有), ffmpeg (已有)

---

## 文件变更地图

| 文件 | 操作 | 说明 |
|------|------|------|
| `SKILL.md` | 修改 | 新增图片采集步骤、主题系统说明、13种模板说明、文案质检规则、TTS节奏规范 |
| `assets/templates.json` | 修改 | 升级5种原有模板为CSS变量版；新增8种模板（quote/timeline/pros-cons/ranking/person/alert/image-caption/split-image）|
| `scripts/generate_video.py` | 修改 | 新增 `--style` 参数；`write_run_readme` 记录使用的主题 |

---

## Task 1: 升级 templates.json — 原有5种模板改用CSS变量

**Files:**
- Modify: `assets/templates.json`

将5种原有模板的配色从硬编码（`#0071e3`、`#a1a1a6` 等）改为 CSS 变量，并在每个模板 `<html>` 标签加 `data-theme` 属性占位符 `{{THEME}}`（Agent 生成 HTML 时替换为实际主题名）。

- [ ] **Step 1: 定义主题 CSS 变量块（所有模板共用）**

所有模板的 `<style>` 标签开头都需要插入以下 CSS 变量定义块（替换原有硬编码色值）：

```css
/* ── 主题变量 ─────────────────────────────── */
[data-theme="apple"] {
  --bg: #000000; --accent: #0071e3; --muted: #a1a1a6; --text: #f5f5f7;
  --card-bg: rgba(255,255,255,0.05); --card-border: rgba(255,255,255,0.08);
}
[data-theme="cyber"] {
  --bg: #050510; --accent: #00ff88; --muted: #7aff7a; --text: #e0ffe0;
  --card-bg: rgba(0,255,136,0.05); --card-border: rgba(0,255,136,0.2);
}
[data-theme="media"] {
  --bg: #1a1a1a; --accent: #f59e0b; --muted: #d1d1d1; --text: #f5f5f5;
  --card-bg: rgba(245,158,11,0.08); --card-border: rgba(245,158,11,0.3);
}
[data-theme="light"] {
  --bg: #f8f8f8; --accent: #e84393; --muted: #555555; --text: #111111;
  --card-bg: rgba(232,67,147,0.06); --card-border: rgba(232,67,147,0.2);
}
```

- [ ] **Step 2: 改写 cover 模板**

`cover` 模板改为：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal,.reveal h1,.reveal h2,.reveal h3{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;text-transform:none;letter-spacing:-0.02em}
.reveal{background:var(--bg)!important;color:var(--text)}
.reveal h1{font-size:3.6em;font-weight:800;line-height:1.15;color:var(--text)}
.reveal h2{font-size:2.6em;font-weight:700;color:var(--text)}
.reveal p{font-size:1.2em;font-weight:300;color:var(--muted)}
.hl{color:var(--accent)}
.badge{display:inline-block;padding:0.3em 0.9em;background:var(--card-bg);border:1px solid var(--card-border);border-radius:999px;font-size:0.9em;color:var(--accent);font-weight:600;margin-bottom:0.6em}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <div class="badge">{{CATEGORY}}</div>
  <h1>{{TITLE}}<br><span class="hl">{{HIGHLIGHT}}</span></h1>
  <p>{{SUBTITLE}}</p>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

- [ ] **Step 3: 改写 features 模板（同样注入主题变量块，替换硬编码色值为变量）**

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal,.reveal h1,.reveal h2,.reveal h3{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;text-transform:none;letter-spacing:-0.02em}
.reveal{background:var(--bg)!important;color:var(--text)}
.reveal h2{font-size:2.2em;font-weight:700;margin-bottom:0.6em;color:var(--text)}
.reveal ul{list-style:none;padding:0;font-size:1.1em;line-height:2.2;color:var(--muted)}
.reveal li{margin-bottom:8px;display:flex;align-items:center;gap:0.5em}
.reveal li strong{color:var(--text)}
.hl{color:var(--accent);font-weight:600}
.icon-wrap{color:var(--accent);display:inline-flex}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <h2>{{HEADER}}</h2>
  <ul>
    <li class="fragment"><span class="icon-wrap"><i data-lucide="{{ICON1}}" style="width:28px;height:28px"></i></span> {{POINT1}}</li>
    <li class="fragment"><span class="icon-wrap"><i data-lucide="{{ICON2}}" style="width:28px;height:28px"></i></span> {{POINT2}}</li>
    <li class="fragment"><span class="icon-wrap"><i data-lucide="{{ICON3}}" style="width:28px;height:28px"></i></span> {{POINT3}}</li>
    <li class="fragment"><span class="icon-wrap"><i data-lucide="{{ICON4}}" style="width:28px;height:28px"></i></span> {{POINT4}}</li>
  </ul>
</section>
</div></div>
<script>
lucide.createIcons();
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

- [ ] **Step 4: 改写 compare 模板**

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal,.reveal h1,.reveal h2{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;text-transform:none;letter-spacing:-0.02em}
.reveal{background:var(--bg)!important;color:var(--text)}
.reveal h2{font-size:2em;font-weight:700;margin-bottom:0.8em;color:var(--text)}
.cols{display:flex;gap:1.2em;justify-content:center}
.col{flex:1;padding:1.4em 1em;border-radius:24px;text-align:center;border:1px solid var(--card-border);background:var(--card-bg)}
.col.hi{border-color:var(--accent);background:var(--card-bg)}
.col-label{font-size:0.85em;color:var(--muted);margin-bottom:0.4em}
.col-value{font-size:2.2em;font-weight:800;color:var(--text)}
.col.hi .col-value{color:var(--accent)}
.col-desc{font-size:0.75em;color:var(--muted);margin-top:0.4em}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <h2>{{HEADER}}</h2>
  <div class="cols">
    <div class="col fragment">
      <div class="col-label">{{LABEL1}}</div>
      <div class="col-value">{{VALUE1}}</div>
      <div class="col-desc">{{DESC1}}</div>
    </div>
    <div class="col hi fragment">
      <div class="col-label">{{LABEL2}}</div>
      <div class="col-value">{{VALUE2}}</div>
      <div class="col-desc">{{DESC2}}</div>
    </div>
    <div class="col fragment">
      <div class="col-label">{{LABEL3}}</div>
      <div class="col-value">{{VALUE3}}</div>
      <div class="col-desc">{{DESC3}}</div>
    </div>
  </div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

- [ ] **Step 5: 改写 stats 模板**

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal,.reveal h1,.reveal h2{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;text-transform:none;letter-spacing:-0.02em}
.reveal{background:var(--bg)!important;color:var(--text)}
.reveal h2{font-size:2em;font-weight:700;color:var(--text)}
.big-num{font-size:5.5em;font-weight:900;color:var(--accent);line-height:1}
.unit{font-size:0.4em;color:var(--muted);font-weight:400}
.desc{font-size:1.1em;color:var(--muted);margin-top:0.5em}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <h2>{{HEADER}}</h2>
  <div class="big-num fragment">
    <span data-count="{{NUMBER}}">0</span><span class="unit">{{UNIT}}</span>
  </div>
  <div class="desc fragment">{{DESCRIPTION}}</div>
</section>
</div></div>
<script>
function countUp(el,target,ms){ms=ms||1200;const t0=performance.now();const go=now=>{const p=Math.min((now-t0)/ms,1);el.textContent=Math.floor((1-Math.pow(1-p,3))*target).toLocaleString();if(p<1)requestAnimationFrame(go);};requestAnimationFrame(go);}
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
Reveal.on('fragmentshown',e=>{e.fragment.querySelectorAll('[data-count]').forEach(el=>countUp(el,+el.dataset.count));});
</script>
</body></html>
```

- [ ] **Step 6: 改写 ending 模板**

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal,.reveal h1,.reveal h2{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;text-transform:none;letter-spacing:-0.02em}
.reveal{background:var(--bg)!important;color:var(--text)}
.reveal h2{font-size:2.2em;font-weight:700;color:var(--text)}
.reveal ul{list-style:none;padding:0;font-size:1em;line-height:2;color:var(--muted)}
.reveal li::before{content:'✓ ';color:var(--accent);font-weight:700}
.question{margin-top:1.2em;padding:1em 1.2em;background:var(--card-bg);border:1px solid var(--card-border);border-radius:16px;font-size:1.1em;color:var(--text);line-height:1.6}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <h2>{{TITLE}}</h2>
  <ul>
    <li class="fragment">{{POINT1}}</li>
    <li class="fragment">{{POINT2}}</li>
    <li class="fragment">{{POINT3}}</li>
  </ul>
  <div class="question fragment">{{QUESTION}}</div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

- [ ] **Step 7: 将5个改写后的模板写入 assets/templates.json**

打开 `assets/templates.json`，将 `cover`、`features`、`compare`、`stats`、`ending` 字段的值替换为上述 Step 2~6 的 HTML 字符串（转义换行为 `\n`，引号为 `\"`）。

注意：JSON 中 HTML 必须是单行字符串，用 `\n` 表示换行，用 `\"` 表示双引号。

- [ ] **Step 8: 验证 JSON 格式合法**

```bash
python3 -c "import json; d=json.load(open('assets/templates.json')); print('OK, keys:', list(d.keys()))"
```

Expected output:
```
OK, keys: ['_note', 'cover', 'features', 'compare', 'stats', 'ending']
```

- [ ] **Step 9: Commit**

```bash
git add assets/templates.json
git commit -m "feat: upgrade templates to CSS variable theme system"
```

---

## Task 2: 新增 8 种模板到 templates.json

**Files:**
- Modify: `assets/templates.json`

新增 `quote`、`timeline`、`pros-cons`、`ranking`、`person`、`alert`、`image-caption`、`split-image` 8 个字段。

- [ ] **Step 1: 新增 quote 模板（金句引言）**

在 `assets/templates.json` 中新增 `"quote"` 字段，值为以下 HTML（转义为单行 JSON 字符串）：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--bg)!important;color:var(--text)}
.q-mark{font-size:8em;line-height:0.8;color:var(--accent);font-family:Georgia,serif;opacity:0.6;margin-bottom:0.1em}
.q-text{font-size:1.8em;font-weight:700;line-height:1.4;color:var(--text);margin:0 0.5em}
.q-source{font-size:0.9em;color:var(--muted);margin-top:1em}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section style="text-align:left;padding:0 0.5em">
  <div class="q-mark fragment">"</div>
  <div class="q-text fragment">{{QUOTE}}</div>
  <div class="q-source fragment">— {{SOURCE}}</div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:false});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符说明：`{{THEME}}` `{{QUOTE}}` `{{SOURCE}}`

- [ ] **Step 2: 新增 timeline 模板（竖向时间轴）**

新增 `"timeline"` 字段：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--bg)!important;color:var(--text)}
.reveal h2{font-size:2em;font-weight:700;margin-bottom:0.6em;color:var(--text)}
.timeline{position:relative;padding-left:2.5em}
.timeline::before{content:'';position:absolute;left:0.8em;top:0;bottom:0;width:2px;background:var(--card-border)}
.tl-item{position:relative;margin-bottom:1.4em}
.tl-dot{position:absolute;left:-1.7em;top:0.3em;width:12px;height:12px;border-radius:50%;background:var(--accent);border:2px solid var(--bg)}
.tl-time{font-size:0.75em;color:var(--accent);font-weight:600;margin-bottom:0.2em}
.tl-text{font-size:0.95em;color:var(--text);line-height:1.5}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section style="text-align:left">
  <h2>{{HEADER}}</h2>
  <div class="timeline">
    <div class="tl-item fragment"><div class="tl-dot"></div><div class="tl-time">{{TIME1}}</div><div class="tl-text">{{EVENT1}}</div></div>
    <div class="tl-item fragment"><div class="tl-dot"></div><div class="tl-time">{{TIME2}}</div><div class="tl-text">{{EVENT2}}</div></div>
    <div class="tl-item fragment"><div class="tl-dot"></div><div class="tl-time">{{TIME3}}</div><div class="tl-text">{{EVENT3}}</div></div>
    <div class="tl-item fragment"><div class="tl-dot"></div><div class="tl-time">{{TIME4}}</div><div class="tl-text">{{EVENT4}}</div></div>
  </div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:false});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符：`{{THEME}}` `{{HEADER}}` `{{TIME1~4}}` `{{EVENT1~4}}`

- [ ] **Step 3: 新增 pros-cons 模板（两列对比）**

新增 `"pros-cons"` 字段：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--bg)!important;color:var(--text)}
.reveal h2{font-size:2em;font-weight:700;margin-bottom:0.6em;color:var(--text)}
.pc-wrap{display:flex;gap:1em}
.pc-col{flex:1;padding:1em;border-radius:16px;background:var(--card-bg);border:1px solid var(--card-border)}
.pc-header{font-size:1.1em;font-weight:700;margin-bottom:0.6em}
.pc-col.pros .pc-header{color:#34d399}
.pc-col.cons .pc-header{color:#f87171}
.pc-item{font-size:0.85em;color:var(--text);margin-bottom:0.5em;line-height:1.4}
.pc-item::before{font-weight:700;margin-right:0.4em}
.pc-col.pros .pc-item::before{content:'✓';color:#34d399}
.pc-col.cons .pc-item::before{content:'✗';color:#f87171}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <h2>{{HEADER}}</h2>
  <div class="pc-wrap">
    <div class="pc-col pros fragment">
      <div class="pc-header">{{PRO_TITLE}}</div>
      <div class="pc-item">{{PRO1}}</div>
      <div class="pc-item">{{PRO2}}</div>
      <div class="pc-item">{{PRO3}}</div>
    </div>
    <div class="pc-col cons fragment">
      <div class="pc-header">{{CON_TITLE}}</div>
      <div class="pc-item">{{CON1}}</div>
      <div class="pc-item">{{CON2}}</div>
      <div class="pc-item">{{CON3}}</div>
    </div>
  </div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符：`{{THEME}}` `{{HEADER}}` `{{PRO_TITLE}}` `{{CON_TITLE}}` `{{PRO1~3}}` `{{CON1~3}}`

- [ ] **Step 4: 新增 ranking 模板（排行榜）**

新增 `"ranking"` 字段：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--bg)!important;color:var(--text)}
.reveal h2{font-size:2em;font-weight:700;margin-bottom:0.6em;color:var(--text)}
.rank-item{display:flex;align-items:center;gap:0.8em;padding:0.8em 1em;border-radius:16px;background:var(--card-bg);border:1px solid var(--card-border);margin-bottom:0.8em}
.rank-num{font-size:2.2em;font-weight:900;color:var(--muted);min-width:1.2em;text-align:center}
.rank-item.first .rank-num{color:#fbbf24;font-size:2.5em}
.rank-item.second .rank-num{color:#94a3b8}
.rank-item.third .rank-num{color:#cd7c3a}
.rank-name{font-size:1.1em;font-weight:700;color:var(--text)}
.rank-desc{font-size:0.8em;color:var(--muted);margin-top:0.2em}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section style="text-align:left">
  <h2>{{HEADER}}</h2>
  <div class="rank-item first fragment">
    <div class="rank-num">1</div>
    <div><div class="rank-name">{{NAME1}}</div><div class="rank-desc">{{DESC1}}</div></div>
  </div>
  <div class="rank-item second fragment">
    <div class="rank-num">2</div>
    <div><div class="rank-name">{{NAME2}}</div><div class="rank-desc">{{DESC2}}</div></div>
  </div>
  <div class="rank-item third fragment">
    <div class="rank-num">3</div>
    <div><div class="rank-name">{{NAME3}}</div><div class="rank-desc">{{DESC3}}</div></div>
  </div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:false});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符：`{{THEME}}` `{{HEADER}}` `{{NAME1~3}}` `{{DESC1~3}}`

- [ ] **Step 5: 新增 person 模板（人物聚焦）**

新增 `"person"` 字段：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--bg)!important;color:var(--text)}
.avatar{width:180px;height:180px;border-radius:50%;background:var(--card-bg);border:3px solid var(--accent);margin:0 auto 0.8em;display:flex;align-items:center;justify-content:center;font-size:4em;overflow:hidden}
.avatar img{width:100%;height:100%;object-fit:cover}
.person-name{font-size:2.2em;font-weight:800;color:var(--text)}
.person-title{font-size:1em;color:var(--accent);margin:0.3em 0}
.person-org{font-size:0.9em;color:var(--muted)}
.person-quote{margin-top:1.2em;padding:1em;background:var(--card-bg);border:1px solid var(--card-border);border-radius:16px;font-size:1em;color:var(--text);line-height:1.6;font-style:italic}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <div class="avatar fragment">
    <!-- 若有本地图片：<img src="images/{{IMG}}"> 否则显示 emoji -->
    {{AVATAR_EMOJI}}
  </div>
  <div class="person-name fragment">{{NAME}}</div>
  <div class="person-title fragment">{{TITLE}}</div>
  <div class="person-org fragment">{{ORG}}</div>
  <div class="person-quote fragment">{{QUOTE}}</div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符：`{{THEME}}` `{{AVATAR_EMOJI}}` `{{NAME}}` `{{TITLE}}` `{{ORG}}` `{{QUOTE}}`（若有本地图片可用 `<img src="images/xxx.jpg">` 替换 emoji）

- [ ] **Step 6: 新增 alert 模板（冲击帧）**

新增 `"alert"` 字段：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--accent)!important;color:#fff}
.alert-icon{font-size:4em;margin-bottom:0.2em}
.alert-label{font-size:1em;font-weight:600;opacity:0.8;letter-spacing:0.15em;text-transform:uppercase}
.alert-main{font-size:3.5em;font-weight:900;line-height:1.2;margin:0.2em 0}
.alert-sub{font-size:1.1em;opacity:0.85;margin-top:0.5em}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <div class="alert-icon fragment">{{ICON}}</div>
  <div class="alert-label fragment">{{LABEL}}</div>
  <div class="alert-main fragment">{{MAIN_TEXT}}</div>
  <div class="alert-sub fragment">{{SUB_TEXT}}</div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:true});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符：`{{THEME}}` `{{ICON}}` `{{LABEL}}` `{{MAIN_TEXT}}` `{{SUB_TEXT}}`

- [ ] **Step 7: 新增 image-caption 模板（图片+说明）**

新增 `"image-caption"` 字段：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--bg)!important;color:var(--text)}
.img-wrap{width:100%;height:60vh;overflow:hidden;border-radius:20px;background:var(--card-bg);border:1px solid var(--card-border)}
.img-wrap img{width:100%;height:100%;object-fit:cover}
.caption-title{font-size:1.8em;font-weight:800;color:var(--text);margin-top:0.6em;line-height:1.3}
.caption-sub{font-size:1em;color:var(--muted);margin-top:0.4em}
.caption-accent{color:var(--accent)}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <div class="img-wrap fragment">
    <img src="{{IMG_PATH}}" alt="{{IMG_ALT}}">
  </div>
  <div class="caption-title fragment">{{TITLE}}</div>
  <div class="caption-sub fragment"><span class="caption-accent">{{ACCENT_WORD}}</span> {{SUBTITLE}}</div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:false});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符：`{{THEME}}` `{{IMG_PATH}}`（如 `images/img-001.jpg`）`{{IMG_ALT}}` `{{TITLE}}` `{{ACCENT_WORD}}` `{{SUBTITLE}}`

- [ ] **Step 8: 新增 split-image 模板（上图下文）**

新增 `"split-image"` 字段：

```html
<!DOCTYPE html>
<html data-theme="{{THEME}}">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reset.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.0.4/dist/reveal.min.js"></script>
<style>
[data-theme="apple"]{--bg:#000;--accent:#0071e3;--muted:#a1a1a6;--text:#f5f5f7;--card-bg:rgba(255,255,255,0.05);--card-border:rgba(255,255,255,0.08)}
[data-theme="cyber"]{--bg:#050510;--accent:#00ff88;--muted:#7aff7a;--text:#e0ffe0;--card-bg:rgba(0,255,136,0.05);--card-border:rgba(0,255,136,0.2)}
[data-theme="media"]{--bg:#1a1a1a;--accent:#f59e0b;--muted:#d1d1d1;--text:#f5f5f5;--card-bg:rgba(245,158,11,0.08);--card-border:rgba(245,158,11,0.3)}
[data-theme="light"]{--bg:#f8f8f8;--accent:#e84393;--muted:#555;--text:#111;--card-bg:rgba(232,67,147,0.06);--card-border:rgba(232,67,147,0.2)}
.reveal{font-family:-apple-system,'PingFang SC','Noto Sans SC',sans-serif;background:var(--bg)!important;color:var(--text)}
.top-img{width:100%;height:50vh;overflow:hidden;border-radius:20px 20px 0 0;background:var(--card-bg)}
.top-img img{width:100%;height:100%;object-fit:cover}
.bottom-text{padding:1.2em 0.5em;text-align:left}
.split-badge{display:inline-block;padding:0.25em 0.8em;background:var(--card-bg);border:1px solid var(--card-border);border-radius:999px;font-size:0.8em;color:var(--accent);font-weight:600;margin-bottom:0.5em}
.split-title{font-size:1.9em;font-weight:800;color:var(--text);line-height:1.3;margin-bottom:0.4em}
.split-body{font-size:0.95em;color:var(--muted);line-height:1.6}
</style>
</head>
<body>
<div class="reveal"><div class="slides">
<section>
  <div class="top-img fragment">
    <img src="{{IMG_PATH}}" alt="{{IMG_ALT}}">
  </div>
  <div class="bottom-text">
    <div class="split-badge fragment">{{BADGE}}</div>
    <div class="split-title fragment">{{TITLE}}</div>
    <div class="split-body fragment">{{BODY}}</div>
  </div>
</section>
</div></div>
<script>
Reveal.initialize({controls:false,progress:false,transition:'fade',transitionSpeed:'fast',backgroundTransition:'none',width:1080,height:1920,margin:0.06,center:false});
Reveal.on('ready',()=>{const dur=parseFloat(new URLSearchParams(location.search).get('dur')||'8');const frags=document.querySelectorAll('.fragment');if(!frags.length)return;const step=(dur-2)*0.9/frags.length;frags.forEach((_,i)=>setTimeout(()=>Reveal.nextFragment(),(1+step*i)*1000));});
</script>
</body></html>
```

占位符：`{{THEME}}` `{{IMG_PATH}}` `{{IMG_ALT}}` `{{BADGE}}` `{{TITLE}}` `{{BODY}}`

- [ ] **Step 9: 验证 JSON 格式合法**

```bash
python3 -c "import json; d=json.load(open('assets/templates.json')); print('OK, keys:', list(d.keys()))"
```

Expected output:
```
OK, keys: ['_note', 'cover', 'features', 'compare', 'stats', 'ending', 'quote', 'timeline', 'pros-cons', 'ranking', 'person', 'alert', 'image-caption', 'split-image']
```

- [ ] **Step 10: Commit**

```bash
git add assets/templates.json
git commit -m "feat: add 8 new HTML templates (quote/timeline/pros-cons/ranking/person/alert/image-caption/split-image)"
```

---

## Task 3: 更新 generate_video.py — 支持 --style 参数

**Files:**
- Modify: `scripts/generate_video.py`

新增 `--style` 命令行参数。若传入，覆盖 `script.json` 中的 `style` 字段；若两者都没有，默认 `apple`。`write_run_readme` 在摘要行记录实际使用的主题。

- [ ] **Step 1: 在 main() 中新增 --style 参数解析**

在 `scripts/generate_video.py` 的 `main()` 函数中，找到 `voice` / `rate` 参数解析的循环（约第 464 行），在其后新增：

```python
    style = None  # None 表示由 script.json 决定
    for i, arg in enumerate(args):
        if arg == "--voice" and i + 1 < len(args):
            voice = args[i + 1]
        elif arg == "--rate" and i + 1 < len(args):
            rate = args[i + 1]
        elif arg == "--style" and i + 1 < len(args):
            style = args[i + 1]

    # 命令行 --style 覆盖 script.json 中的 style 字段
    if style:
        script["style"] = style
    elif "style" not in script:
        script["style"] = "apple"  # 默认主题

    _log("INIT", f"参数  voice={voice}  rate={rate}  style={script['style']}  run_dir={run_dir}")
```

注意：把原有的 `for i, arg in enumerate(args):` 循环整体替换为上面这段，保留原有 `voice` / `rate` 分支。

- [ ] **Step 2: 在 write_run_readme 中记录主题**

在 `write_run_readme` 函数（约第 74 行）的 `lines` 列表里，找到：

```python
    lines = [
        f"# {topic}",
        f"",
        f"> 生成时间：{now}　|　总时长：{total_dur:.1f}s　|　共 {len(shots)} 个镜头",
```

替换为（新增 style 字段）：

```python
    style = script.get("style", "apple")
    lines = [
        f"# {topic}",
        f"",
        f"> 生成时间：{now}　|　总时长：{total_dur:.1f}s　|　共 {len(shots)} 个镜头　|　主题：{style}",
```

- [ ] **Step 3: 更新 main() 用法提示**

找到（约第 448 行）：

```python
        print("用法: python generate_video.py <output/{slug}/script.json> [--voice <音色>] [--rate <语速>]")
        print("示例: python generate_video.py output/openai-news-20260410/script.json")
```

替换为：

```python
        print("用法: python generate_video.py <output/{slug}/script.json> [--voice <音色>] [--rate <语速>] [--style <主题>]")
        print("主题可选: apple | cyber | media | light（默认 apple，可在 script.json 中设置，命令行参数优先）")
        print("示例: python generate_video.py output/openai-news-20260410/script.json --style cyber")
```

- [ ] **Step 4: 验证脚本语法正确**

```bash
python3 -c "import py_compile; py_compile.compile('scripts/generate_video.py'); print('syntax OK')"
```

Expected: `syntax OK`

- [ ] **Step 5: 验证 --style 参数被正确解析（用 --help 触发用法信息）**

```bash
python3 scripts/generate_video.py 2>&1 | head -5
```

Expected output contains:
```
用法: python generate_video.py <output/{slug}/script.json> [--voice <音色>] [--rate <语速>] [--style <主题>]
```

- [ ] **Step 6: Commit**

```bash
git add scripts/generate_video.py
git commit -m "feat: add --style param to generate_video.py, log theme in README"
```

---

## Task 4: 更新 SKILL.md — 图片采集步骤

**Files:**
- Modify: `SKILL.md`

在 Step 1（搜索/理解新闻）之后、Step 2（撰写详细文案）之前，插入新的 **Step 1.5：图片采集**。

- [ ] **Step 1: 在 SKILL.md 的 Step 1 结尾后插入新步骤**

找到 `SKILL.md` 中 Step 1 结尾处（含 `> 也可直接调用辅助脚本批量抓取` 的那一行之后），在其后插入以下内容：

```markdown
---

### Step 1.5：图片采集（搜索完成后立即执行）

在写 `article.md` 之前，对主要信息来源页面执行图片采集，将素材保存到 `output/{slug}/images/`。

#### 采集方式

**方式一：全页截图**

用 Playwright 对目标 URL（新闻原文、GitHub 仓库主页等）截取全屏快照：

```python
# 示例（在 Agent 工具调用或脚本中执行）
from playwright.sync_api import sync_playwright
from pathlib import Path

def capture_page(url: str, out_path: Path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.screenshot(path=str(out_path), full_page=False)
        browser.close()

# 保存为：output/{slug}/images/page-screenshot.png
```

**方式二：提取页面图片**

从页面中筛选有实质内容的 `<img>`，过滤掉图标（宽高 < 100px）、SVG、data URI，下载前 3～5 张到 `images/img-001.jpg` 等：

```python
import urllib.request, re

def extract_images(page, out_dir: Path, max_count: int = 5):
    imgs = page.query_selector_all('img')
    saved = 0
    for img in imgs:
        src = img.get_attribute('src') or ''
        w = img.get_attribute('width') or '0'
        h = img.get_attribute('height') or '0'
        # 跳过小图（图标/埋点）、data URI、SVG
        if src.startswith('data:') or src.endswith('.svg'):
            continue
        if int(w or 0) < 100 or int(h or 0) < 100:
            continue
        ext = 'jpg' if 'jpg' in src or 'jpeg' in src else 'png'
        dest = out_dir / f"img-{saved+1:03d}.{ext}"
        try:
            urllib.request.urlretrieve(src, dest)
            saved += 1
        except Exception:
            continue
        if saved >= max_count:
            break
```

#### 失败处理

- 若目标页面截图失败（超时、反爬、登录墙），跳过截图，不中断后续流程
- 若图片提取为 0，后续 HTML 改用纯文字模板，不使用 `image-caption` / `split-image`
- 采集失败时在日志中注明：`[IMAGES] 采集失败，降级为纯文字模板`

#### 输出结构

```
output/{slug}/images/
  ├── page-screenshot.png    # 全页截图（可选）
  ├── img-001.jpg            # 提取图片 1
  ├── img-002.jpg            # 提取图片 2
  └── ...
```
```

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "feat(skill): add Step 1.5 image capture with Playwright"
```

---

## Task 5: 更新 SKILL.md — 视觉主题系统

**Files:**
- Modify: `SKILL.md`

在 Step 2（撰写详细文案）结束后、Step 3（生成口播文稿）之前，插入主题推断步骤；并在 Step 4（HTML生成）中补充主题使用说明。

- [ ] **Step 1: 在 Step 2 结尾后插入主题推断说明**

找到 Step 2 末尾的 `---` 分隔线（Step 3 开始前），在其前插入：

```markdown
#### 视觉主题选择

写完 `article.md` 后，根据文案的**主题性质、情感基调和目标受众**，自主判断最合适的视觉主题，写入 `script.json` 的 `style` 字段。

| 主题值 | 适合的内容感觉 |
|--------|--------------|
| `apple` | 科技感、产品发布、冷静专业、AI/大模型类；默认选项 |
| `cyber` | 极客/黑客感、开源社区、GitHub项目、编程工具、赛博朋克调性 |
| `media` | 严肃资讯、财经市场、政策法规、社会事件、有温度的新闻报道 |
| `light` | 轻松生活、消费测评、小红书风格、面向大众的科普内容 |

**判断方式**：不做关键词匹配，基于对文案整体调性的理解作出判断。用户可在命令行加 `--style <主题>` 覆盖此选择。
```

- [ ] **Step 2: 在 Step 4（HTML生成）中补充 data-theme 使用说明**

找到 Step 4 中关于 HTML 规范的部分，在 Reveal.js CDN 引入说明之后补充：

```markdown
#### 主题注入

每个 shot HTML 的 `<html>` 标签必须带 `data-theme` 属性，值取自 `script.json` 的 `style` 字段：

```html
<html data-theme="apple">   <!-- 或 cyber / media / light -->
```

所有模板已内置 CSS 变量定义块（`[data-theme="apple"]` 等），切换主题只需修改此属性，无需改动其他样式。同一次生成的所有 shot HTML 使用相同主题（即 `script.json` 中的 `style` 值）。
```

- [ ] **Step 3: 更新模板种类说明表格**

找到 Step 4 中列出 `type` 建议值的表格（cover/features/compare/timeline/quote/stats/ending），将其替换为完整的 13 种模板说明：

```markdown
| type 值 | 适用场景 | 核心视觉元素 |
|---------|---------|------------|
| `cover` | 封面/开篇 | 大标题 + badge + 副标题 |
| `features` | 功能/特性列举 | Lucide图标 + 逐条入场列表 |
| `compare` | 数据对比 | 多栏卡片，中间列高亮 |
| `stats` | 核心数字 | 超大数字 + countUp动画 |
| `ending` | 总结互动 | 要点回顾 + 互动问题卡 |
| `quote` | 金句/钩子 | 大号引号 + 震撼一句话 |
| `timeline` | 事件时间线 | 竖向时间轴，节点逐条出现 |
| `pros-cons` | 优劣对比 | 两列 ✓/✗ 逐行出现 |
| `ranking` | 排行榜 | 1-2-3名次，金银铜配色 |
| `person` | 人物聚焦 | 圆形头像 + 姓名/职位 |
| `alert` | 冲击帧/重磅 | 全屏强调色背景 + 极大字号 |
| `image-caption` | 图片主体 | 图片占60% + 下方说明文字 |
| `split-image` | 图文各半 | 上图下文，badge + 标题 + 正文 |

**图片类模板（image-caption / split-image）**：仅在 `output/{slug}/images/` 目录中有可用图片时使用。`alert` 模板仅用于钩子镜头（shot1）或强调关键数字时。不同镜头尽量使用不同模板，避免连续重复。
```

- [ ] **Step 4: Commit**

```bash
git add SKILL.md
git commit -m "feat(skill): add visual theme system and expand template catalog to 13 types"
```

---

## Task 6: 更新 SKILL.md — 文案质量提升

**Files:**
- Modify: `SKILL.md`

加强文案核心原则（对照示例）、新增钩子自检清单、TTS节奏规范、社媒文案质检。

- [ ] **Step 1: 在"文案核心原则"部分新增对照改写示例**

找到 SKILL.md 中标题 `#### ⚠️ 文案核心原则：讲故事，不写说明书` 下的现有示例（坏/好各一条），在其后补充两组对照：

```markdown
**对照组 2 — 财经资讯**

> ❌ 坏（数据罗列）：A股今日三大指数全线下跌，上证综指跌0.8%，深证成指跌1.2%，创业板指跌1.5%，成交量较昨日萎缩。
>
> ✅ 好（情绪带入）：今天开盘，很多人的手还没到键盘上，账户就已经绿了——而且是那种越看越绿的绿。

**对照组 3 — GitHub项目发布**

> ❌ 坏（功能列举）：该项目支持多模态输入、RAG检索增强、工具调用、流式输出，star数已达10k，支持Docker一键部署。
>
> ✅ 好（场景代入）：昨晚，一个 GitHub 项目的 star 数，在 12 小时内从两千涨到了一万——没有发布会，没有公司背书，只有一个人写的 README。
```

- [ ] **Step 2: 在"钩子公式"后新增钩子自检清单**

找到 `#### 钩子公式（第一镜必须用其中一种）` 小节末尾，在其后插入：

```markdown
#### 钩子自检清单（写完 shot1 narration 后必过）

写完第一镜口播后，逐项检查：

- [ ] 这句话能在 **1.5 秒内**让人停住手指吗？
- [ ] 有没有「数字」、「反差」、「悬念」中的至少一种？
- [ ] 有没有让观众感觉"说的是我"的代入感？

任何一项不满足 → **重写钩子**，重新过一遍。不要跳过这一步。
```

- [ ] **Step 3: 更新"技术参数"部分，新增 TTS 节奏规范**

找到 `#### 技术参数` 小节，将原有内容：

```markdown
- **语言**：口语化短句，单句不超过15字，适合TTS朗读
- **每段时长**：5~10秒（约50~100字）
- **节奏节拍**：钩子快→冲突快→爆料中→共鸣慢，有呼吸感
```

替换为：

```markdown
- **语言**：口语化短句，单句不超过 15 字，适合 TTS 朗读
- **每段时长**：5～10 秒（建议 40～80 字；字数少于 40 时画面会过短，超过 80 时观众会走神）
- **节奏节拍**：钩子快→冲突快→爆料中→共鸣慢，有呼吸感

**TTS 节奏规范**（影响听感，必须遵守）：

| 规则 | 写法 | 禁止 |
|------|------|------|
| 停顿标记 | 用 `……` 表示 0.5s 停顿，情绪词后、数字后必加 | 用逗号代替停顿 |
| 断句 | 两个完整意思之间用句号，不用逗号连接 | 一句话超过 15 字 |
| 数字读法 | 大数字后跟单位（"十亿""万倍"），不写"1,000,000,000" | 纯数字无单位 |

**示例**：

> ❌ 坏：GPT-5今天正式发布，推理能力提升了10倍，价格却出乎所有人的预料。
>
> ✅ 好：GPT-5……今天发布了。推理能力，提升十倍。但价格……出乎所有人意料。
```

- [ ] **Step 4: 在社媒文案说明后新增质检清单**

找到社媒发布文案部分的 `**注意**：社媒正文可与口播相似但不必逐句相同……` 那一行，在其后插入：

```markdown
**社媒文案质检清单**（写完 `social` 字段后必过）：

抖音标题：
- [ ] 每条 ≤30 字
- [ ] 至少含一个悬念词或具体数字
- [ ] 不含"震惊"、"重磅"、"史上最"、"第一"等平台限流敏感词

小红书标题：
- [ ] 含 emoji（1～3 个，不密集堆砌）
- [ ] 有痛点词（"还在…？"）或利益词（"一文搞懂"、"省了XX元"）

正文通用：
- [ ] 结尾有互动引导（"你怎么看？"/"评论区聊聊"/"你会选哪个？"）
- [ ] 话题标签 3～6 个，不堆砌超过 8 个
```

- [ ] **Step 5: Commit**

```bash
git add SKILL.md
git commit -m "feat(skill): improve copy quality — add rewrite examples, hook checklist, TTS rhythm rules, social QC"
```

---

## Task 7: 更新 README.md 和 .gitignore

**Files:**
- Modify: `README.md`
- Modify: `.gitignore`（若无则创建）

- [ ] **Step 1: 在 README.md 的"视频规格"表格后新增主题说明**

找到 README.md 中"视频规格"表格，在其后插入：

```markdown
## 视觉主题

生成时 Agent 会根据内容自动选择主题，也可通过命令行指定：

```bash
python scripts/generate_video.py output/xxx/script.json --style cyber
```

| 主题 | 适用场景 |
|------|---------|
| `apple`（默认）| AI/科技/产品发布，黑底蓝点缀 |
| `cyber` | 开源/编程/极客，深色底绿描边 |
| `media` | 财经/资讯，深灰底琥珀强调 |
| `light` | 生活/消费/小红书，白底粉点缀 |
```

- [ ] **Step 2: 确认 .gitignore 包含 .superpowers/**

检查 `.gitignore` 是否已有 `.superpowers/`：

```bash
grep -q "superpowers" .gitignore && echo "already there" || echo ".superpowers/" >> .gitignore
```

- [ ] **Step 3: Commit**

```bash
git add README.md .gitignore
git commit -m "docs: add theme system docs to README, add .superpowers to .gitignore"
```

---

## 自检：Spec 覆盖确认

| Spec 要求 | 覆盖任务 |
|-----------|---------|
| 图片采集 — Playwright截图 + 图片提取 | Task 4 (SKILL.md Step 1.5) |
| 视觉主题系统 — 4套CSS变量 | Task 1 (templates.json 升级) |
| 主题 LLM 自动推断说明 | Task 5 (SKILL.md 主题描述) |
| --style 命令行参数覆盖 | Task 3 (generate_video.py) |
| 原有5种模板升级 | Task 1 |
| 新增8种模板 | Task 2 |
| 文案对照改写示例 ≥3组 | Task 6 Step 1 |
| 钩子自检清单 | Task 6 Step 2 |
| TTS节奏规范 | Task 6 Step 3 |
| 社媒文案质检清单 | Task 6 Step 4 |
| README 更新 | Task 7 |
