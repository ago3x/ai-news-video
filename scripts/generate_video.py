#!/usr/bin/env python3
"""
AI新闻短视频技术管道
输入：output/{slug}/script.json + shot*.html
输出：
  output/{slug}/shot*.mp3        TTS 配音
  output/{slug}/final.mp4        成品视频
  output/{slug}/README.md        本次生成说明
  output/README.md               总目录（追加记录）
"""

import asyncio
import subprocess
import sys
import json
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

DEFAULT_FPS = 20
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
DEFAULT_CRF = "18"


def _log(tag: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{tag}] {msg}", flush=True)


def _elapsed(start: float) -> str:
    s = time.time() - start
    return f"{s:.1f}s"


def _ffmpeg():
    import shutil
    ff = shutil.which("ffmpeg")
    if ff:
        _log("ENV", f"使用系统 ffmpeg: {ff}")
        return ff
    try:
        import imageio_ffmpeg
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        _log("ENV", f"使用 imageio-ffmpeg: {ff}")
        return ff
    except ImportError:
        raise RuntimeError("找不到 ffmpeg，请安装 ffmpeg 或运行: pip install imageio-ffmpeg")


def _ffprobe():
    import shutil
    fp = shutil.which("ffprobe")
    if fp:
        return fp
    try:
        import imageio_ffmpeg
        ff_path = Path(imageio_ffmpeg.get_ffmpeg_exe())
        fp_candidate = ff_path.parent / ff_path.name.replace("ffmpeg", "ffprobe")
        if fp_candidate.exists():
            return str(fp_candidate)
    except ImportError:
        pass
    return None


# ── Markdown 工具 ──────────────────────────────────────────────────────────────

def write_run_readme(run_dir: Path, script: dict, final_video: Path, durations: list):
    """在本次执行目录下生成 README.md"""
    topic = script.get("topic", "未命名")
    shots = script["shots"]
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_dur = sum(durations)

    lines = [
        f"# {topic}",
        f"",
        f"> 生成时间：{now}　|　总时长：{total_dur:.1f}s　|　共 {len(shots)} 个镜头",
        f"",
        f"## 成品视频",
        f"",
        f"[{final_video.name}]({final_video.name})",
        f"",
        f"## 分镜脚本",
        f"",
        f"| 镜头 | 类型 | 时长 | 口播文稿 |",
        f"|------|------|------|---------|",
    ]
    for shot, dur in zip(shots, durations):
        narration = shot["narration"].replace("|", "｜")
        lines.append(f"| [{shot['id']}]({shot['id']}.html) | `{shot['type']}` | {dur:.1f}s | {narration} |")

    lines += [
        f"",
        f"## 分镜 HTML 预览",
        f"",
    ]
    for shot in shots:
        lines.append(f"- [{shot['id']}.html]({shot['id']}.html)")

    lines += [
        f"",
        f"## 配音文件",
        f"",
    ]
    for shot in shots:
        lines.append(f"- [{shot['id']}.mp3]({shot['id']}.mp3)")

    (run_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def update_index_readme(output_dir: Path, run_dir: Path, script: dict,
                        final_video: Path, total_dur: float):
    """更新 output/README.md 总目录，追加本次记录"""
    index_path = output_dir / "README.md"
    topic = script.get("topic", "未命名")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rel_link = f"{run_dir.name}/README.md"
    video_link = f"{run_dir.name}/{final_video.name}"
    row = f"| {now} | {topic} | {total_dur:.1f}s | [详情]({rel_link}) | [下载]({video_link}) |"

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        if "| ---" in content:
            content = content.rstrip() + "\n" + row + "\n"
        else:
            content += "\n" + row + "\n"
    else:
        content = "\n".join([
            "# AI 新闻视频生成记录",
            "",
            "每次执行自动追加一条记录。",
            "",
            "| 时间 | 主题 | 时长 | 详情 | 视频 |",
            "| ---- | ---- | ---- | ---- | ---- |",
            row,
            "",
        ])

    index_path.write_text(content, encoding="utf-8")


# ── 主管道 ─────────────────────────────────────────────────────────────────────

class VideoPipeline:

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.tmp = run_dir / ".tmp"
        self.tmp.mkdir(parents=True, exist_ok=True)

    async def tts_async(self, text: str, out: Path,
                        voice: str = DEFAULT_VOICE, rate: str = "+0%"):
        """TTS 异步方法，支持并行调用；已存在则跳过"""
        if out.exists():
            _log("TTS", f"跳过（已存在）: {out.name}")
            return

        try:
            import edge_tts
        except ImportError:
            _log("TTS", "edge-tts 未安装，正在自动安装...")
            subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "-q"],
                           capture_output=True)
            _log("TTS", "edge-tts 安装完成")
            import edge_tts

        t0 = time.time()
        _log("TTS", f"合成中 voice={voice} rate={rate} | {text[:40]}{'...' if len(text) > 40 else ''}")
        comm = edge_tts.Communicate(text, voice, rate=rate)
        await comm.save(str(out))
        if not out.exists():
            raise RuntimeError(f"TTS 生成失败: {out}")
        size_kb = out.stat().st_size / 1024
        _log("TTS", f"完成 -> {out.name} ({size_kb:.1f}KB) 耗时 {_elapsed(t0)}")

    def audio_duration(self, f: Path) -> float:
        fp = _ffprobe()
        if fp:
            r = subprocess.run([
                fp, "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(f)
            ], capture_output=True, text=True)
            dur = float(r.stdout.strip())
            _log("DUR", f"{f.name} -> {dur:.2f}s")
            return dur
        r = subprocess.run([_ffmpeg(), "-i", str(f), "-f", "null", "-"],
                           capture_output=True, text=True)
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
        if m:
            h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            dur = h * 3600 + mi * 60 + s
            _log("DUR", f"{f.name} -> {dur:.2f}s (ffmpeg fallback)")
            return dur
        raise RuntimeError(f"无法获取音频时长: {f}")

    async def record_html(self, html_file: Path, duration: float) -> Path:
        from playwright.async_api import async_playwright

        frames_dir = self.tmp / f"frames_{html_file.stem}"
        frames_dir.mkdir(exist_ok=True)
        total_frames = int(DEFAULT_FPS * duration)

        # as_uri() 在 Windows/Mac/Linux 均能正确生成 file:///... 格式
        url = f"{html_file.absolute().as_uri()}?dur={duration:.2f}"

        _log("REC", f"开始录制 {html_file.name}  时长={duration:.2f}s  帧数={total_frames}")
        t0 = time.time()

        frame_interval = 1.0 / DEFAULT_FPS

        async with async_playwright() as p:
            _log("REC", "启动 Chromium headless 1080×1920...")
            browser = await p.chromium.launch(headless=True)
            ctx = await browser.new_context(viewport={"width": 1080, "height": 1920})
            page = await ctx.new_page()
            _log("REC", f"加载页面: {url}")
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(0.3)

            _log("REC", f"截帧中 0/{total_frames}...")
            for i in range(total_frames):
                frame_t = time.monotonic()
                await page.screenshot(path=str(frames_dir / f"f{i:04d}.png"))
                # 计入截图本身耗时，保持帧间隔精准
                elapsed = time.monotonic() - frame_t
                sleep_time = max(0.0, frame_interval - elapsed)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                if (i + 1) % max(1, total_frames // 5) == 0 or i + 1 == total_frames:
                    pct = (i + 1) * 100 // total_frames
                    _log("REC", f"截帧进度 {i+1}/{total_frames} ({pct}%)  已用 {_elapsed(t0)}")

            await ctx.close()
            await browser.close()
            _log("REC", f"截帧完成，共 {total_frames} 帧，耗时 {_elapsed(t0)}")

        video_file = self.tmp / f"{html_file.stem}_silent.mp4"
        _log("REC", f"编码为无声 MP4: {video_file.name}")
        t1 = time.time()
        r = subprocess.run([
            _ffmpeg(), "-y", "-framerate", str(DEFAULT_FPS),
            "-i", str(frames_dir / "f%04d.png"),
            "-c:v", "libx264", "-preset", "fast",
            "-crf", DEFAULT_CRF, "-pix_fmt", "yuv420p",
            str(video_file)
        ], capture_output=True)
        if r.returncode != 0:
            err = r.stderr.decode("utf-8", errors="replace")[-500:]
            raise RuntimeError(f"ffmpeg 编码失败:\n{err}")
        size_mb = video_file.stat().st_size / 1024 / 1024
        _log("REC", f"编码完成 {video_file.name} ({size_mb:.1f}MB) 耗时 {_elapsed(t1)}")

        for f in frames_dir.glob("*.png"):
            f.unlink()
        frames_dir.rmdir()
        _log("REC", "临时帧目录已清理")
        return video_file

    def merge(self, video: Path, audio: Path, out: Path,
              duration: Optional[float] = None):
        """合并音视频；传入 duration 可跳过重复 ffprobe 查询"""
        dur = duration if duration is not None else self.audio_duration(audio)
        _log("MRG", f"合并 {video.name} + {audio.name} -> {out.name} (音频 {dur:.2f}s)")
        t0 = time.time()
        r = subprocess.run([
            _ffmpeg(), "-y",
            "-i", str(video), "-i", str(audio),
            "-c:v", "copy", "-c:a", "aac",
            "-af", f"afade=t=in:st=0:d=0.2,afade=t=out:st={dur - 0.3:.3f}:d=0.3",
            "-shortest", str(out)
        ], capture_output=True)
        if r.returncode != 0:
            err = r.stderr.decode("utf-8", errors="replace")[-500:]
            raise RuntimeError(f"音视频合并失败:\n{err}")
        size_mb = out.stat().st_size / 1024 / 1024
        _log("MRG", f"完成 {out.name} ({size_mb:.1f}MB) 耗时 {_elapsed(t0)}")

    def concat(self, videos: list, out: Path):
        _log("CAT", f"拼接 {len(videos)} 个片段 -> {out.name}")
        for i, v in enumerate(videos):
            _log("CAT", f"  [{i+1}] {Path(v).name}")
        list_file = self.tmp / "concat.txt"
        lines = "\n".join(f"file '{Path(v).absolute().as_posix()}'" for v in videos)
        list_file.write_text(lines, encoding="utf-8")
        t0 = time.time()
        r = subprocess.run([
            _ffmpeg(), "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file.absolute()), "-c", "copy", str(out)
        ], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"concat 失败:\n{r.stderr.decode('utf-8', errors='replace')}")
        size_mb = out.stat().st_size / 1024 / 1024
        _log("CAT", f"拼接完成 {out.name} ({size_mb:.1f}MB) 耗时 {_elapsed(t0)}")

    def cleanup(self):
        _log("CLN", f"清理临时目录: {self.tmp}")
        count = 0
        for f in self.tmp.iterdir():
            if f.is_file():
                f.unlink()
                count += 1
            elif f.is_dir():
                for sub in f.iterdir():
                    sub.unlink()
                    count += 1
                f.rmdir()
        self.tmp.rmdir()
        _log("CLN", f"已删除 {count} 个临时文件")

    async def run(self, script: dict,
                  voice: str = DEFAULT_VOICE, rate: str = "+0%") -> Path:
        shots = script["shots"]
        topic = script.get("topic", "video")
        total_start = time.time()

        print(f"\n{'='*60}")
        print(f"  AI 新闻视频生成管道")
        print(f"  主题: {topic}")
        print(f"  镜头数: {len(shots)}  输出目录: {self.run_dir}")
        print(f"{'='*60}\n")

        # ── 1. 并行 TTS ──────────────────────────────────────────────
        _log("STEP", f"1/4 TTS 配音  共 {len(shots)} 个镜头（并行）")
        audio_files = [self.run_dir / f"{shot['id']}.mp3" for shot in shots]
        await asyncio.gather(*[
            self.tts_async(shot["narration"], audio_out, voice=voice, rate=rate)
            for shot, audio_out in zip(shots, audio_files)
        ])
        durations = [self.audio_duration(f) for f in audio_files]
        _log("STEP", f"TTS 完成  总时长={sum(durations):.1f}s\n")

        # ── 2. 录制 HTML ─────────────────────────────────────────────
        _log("STEP", f"2/4 录制 HTML  共 {len(shots)} 个镜头")
        video_files = []
        for idx, (shot, duration) in enumerate(zip(shots, durations), 1):
            html_file = self.run_dir / f"{shot['id']}.html"
            if not html_file.exists():
                raise FileNotFoundError(f"找不到 {html_file}，请确认 Agent 已生成该 HTML")
            _log("REC", f"[{idx}/{len(shots)}] {shot['id']}.html  时长={duration:.1f}s")
            video_files.append(await self.record_html(html_file, duration))
        _log("STEP", "录制完成\n")

        # ── 3. 音视频合并（复用已有 duration，跳过重复 ffprobe）────────
        _log("STEP", f"3/4 音视频合并  共 {len(shots)} 个片段")
        synced = []
        for idx, (shot, video, audio, dur) in enumerate(
                zip(shots, video_files, audio_files, durations), 1):
            out = self.tmp / f"{shot['id']}_synced.mp4"
            _log("MRG", f"[{idx}/{len(shots)}] {shot['id']}")
            self.merge(video, audio, out, duration=dur)
            synced.append(out)
        _log("STEP", "合并完成\n")

        # ── 4. 拼接成品 ───────────────────────────────────────────────
        _log("STEP", "4/4 拼接最终视频")
        final = self.run_dir / "final.mp4"
        self.concat(synced, final)
        self.cleanup()

        size_mb = final.stat().st_size / 1024 / 1024
        total_elapsed = _elapsed(total_start)

        print(f"\n{'='*60}")
        _log("DONE", f"成品视频: {final}")
        _log("DONE", f"文件大小: {size_mb:.1f}MB  总耗时: {total_elapsed}")
        print(f"{'='*60}\n")

        # ── 5. 生成 Markdown ─────────────────────────────────────────
        write_run_readme(self.run_dir, script, final, durations)
        update_index_readme(self.run_dir.parent, self.run_dir, script, final, sum(durations))
        _log("DOC", f"本次报告: {self.run_dir / 'README.md'}")
        _log("DOC", f"总目录更新: {self.run_dir.parent / 'README.md'}\n")

        return final


def main():
    if len(sys.argv) < 2:
        print("用法: python generate_video.py <output/{slug}/script.json> [--voice <音色>] [--rate <语速>]")
        print("示例: python generate_video.py output/openai-news-20260410/script.json")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    if not script_path.exists():
        _log("ERR", f"找不到脚本文件: {script_path}")
        sys.exit(1)

    _log("INIT", f"读取脚本: {script_path}")
    script = json.loads(script_path.read_text(encoding="utf-8"))
    run_dir = script_path.parent

    voice = DEFAULT_VOICE
    rate = "+0%"
    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg == "--voice" and i + 1 < len(args):
            voice = args[i + 1]
        elif arg == "--rate" and i + 1 < len(args):
            rate = args[i + 1]

    if not re.match(r'^[+-]\d+%$', rate):
        _log("ERR", f"--rate 格式错误: '{rate}'，正确格式如 '+0%' 或 '-10%'")
        sys.exit(1)

    _log("INIT", f"参数  voice={voice}  rate={rate}  run_dir={run_dir}")

    pipeline = VideoPipeline(run_dir=run_dir)
    asyncio.run(pipeline.run(script, voice=voice, rate=rate))


if __name__ == "__main__":
    main()
