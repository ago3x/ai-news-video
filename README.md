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

## 常见问题

**Q: 生成的 `README.md` 里能直接播放视频吗？**

不能。标准 Markdown 不支持内嵌视频播放，生成的 README 使用普通链接 `[final.mp4](final.mp4)` 形式。点击后由系统默认播放器打开。

若需要播放器，可在支持 HTML 的渲染环境（如本地 HTTP 服务器、GitHub Pages）中将链接手动替换为：

```html
<video width="100%" controls>
  <source src="final.mp4" type="video/mp4">
</video>
```

> VS Code Markdown 预览默认屏蔽本地视频加载，`<video>` 标签在预览里也不会播放，直接用链接更简洁。

---

## License

MIT
