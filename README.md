# ai-news-video — Agent Skill

AI新闻短视频全自动生成工具，适用于任何支持 Agent Skills 的 AI 编辑器/工具。

从一个新闻主题，到成品竖屏短视频（1080×1920），全程 Agent 驱动：

```
新闻主题 → 搜索 → 口播文稿 → HTML 分镜 → TTS 配音 → 录制 → 成品 MP4
```

## 支持的平台

| 平台 | 安装路径 |
|------|---------|
| [Cursor](https://cursor.sh) | `~/.cursor/skills/ai-news-video/` 或 `.cursor/skills/ai-news-video/` |
| [Claude Code](https://claude.ai/code) | `~/.claude/skills/ai-news-video/` |
| 其他支持 SKILL.md 的 Agent | 放入对应的 skills 目录即可 |

## 安装

克隆到对应平台的 skills 目录：

```bash
# Cursor — 个人全局
git clone https://github.com/ago3x/ai-news-video ~/.cursor/skills/ai-news-video

# Cursor — 项目级
git clone https://github.com/ago3x/ai-news-video .cursor/skills/ai-news-video

# Claude Code — 个人全局
git clone https://github.com/ago3x/ai-news-video ~/.claude/skills/ai-news-video
```

## 依赖

```bash
pip install edge-tts playwright
playwright install chromium
# ffmpeg 需系统安装：https://ffmpeg.org/download.html
```

## 使用方法

在支持的 Agent 中直接对话：

```
/ai-news-video 帮我做一个关于今日 A 股行情的短视频
/ai-news-video 查下 OpenAI 最新发布，生成视频
```

Agent 会自动完成搜索 → 脚本 → HTML → 视频全流程，成品保存在 `output/` 目录。

## 目录结构

```
ai-news-video/
├── SKILL.md                  # Agent 工作流程指令（核心）
├── README.md                 # 本文件
├── scripts/
│   ├── generate_video.py     # 技术管道：TTS + 录制 + 合并
│   └── search_news.py        # 新闻搜索辅助脚本
└── assets/
    └── templates.json        # HTML 模板参考
```

## 视频规格

| 项目 | 规格 |
|------|------|
| 分辨率 | 1080 × 1920（9:16 竖屏）|
| 帧率 | 20fps |
| 格式 | MP4 / AAC |
| 单段时长 | 5～15 秒 |
| 风格 | 苹果 Keynote 风，黑底高亮 |

## 输出目录结构

每次执行后，所有产物保存在 `output/{slug}/` 子目录下：

```
output/
├── README.md                        ← 总目录（每次自动追加一条记录）
└── {slug}/                          ← 本次生成目录，如 claude-mythos/
    ├── script.json                  ← 口播脚本（Agent 生成）
    ├── shot1.html ~ shotN.html      ← 分镜页面（Agent 生成）
    ├── shot1.mp3 ~ shotN.mp3        ← TTS 配音（脚本生成）
    ├── final.mp4                    ← 成品视频（脚本生成）
    └── README.md                    ← 本次生成说明（脚本生成）
```

其中 `output/{slug}/README.md` 记录了本次生成的主题、时长、分镜脚本和文件链接；`output/README.md` 是历次生成的汇总索引。

## License

MIT
