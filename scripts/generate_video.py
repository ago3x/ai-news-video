#!/usr/bin/env python3
"""
AI新闻短视频技术管道
输入：script.json（口播文稿）+ shot1~4.html（Agent已生成）
输出：完整竖屏视频
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path

DEFAULT_FPS = 20
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


def _ffmpeg():
    """返回 ffmpeg 可执行路径，优先用系统 PATH，找不到则用 imageio-ffmpeg 内置版本"""
    import shutil
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise RuntimeError("找不到 ffmpeg，请安装 ffmpeg 或运行: pip install imageio-ffmpeg")


def _ffprobe():
    """返回 ffprobe 可执行路径，找不到则用 ffmpeg 同目录的 ffprobe"""
    import shutil
    fp = shutil.which("ffprobe")
    if fp:
        return fp
    # imageio-ffmpeg 自带的 ffmpeg 二进制同目录可能有 ffprobe
    try:
        import imageio_ffmpeg
        ff_path = Path(imageio_ffmpeg.get_ffmpeg_exe())
        fp_candidate = ff_path.parent / ff_path.name.replace("ffmpeg", "ffprobe")
        if fp_candidate.exists():
            return str(fp_candidate)
    except ImportError:
        pass
    # 降级：用 ffmpeg 解析时长
    return None


class VideoPipeline:
    """技术管道：TTS → 录制 → 合并 → 输出"""

    def __init__(self, output_dir: Path, temp_dir: Path):
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    # ── TTS ──────────────────────────────────────────────────────────────────

    def tts(self, text: str, out: Path, voice: str = DEFAULT_VOICE, rate: str = "+0%"):
        """调用 edge-tts 生成配音"""
        try:
            import edge_tts
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts", "-q"],
                           capture_output=True)
            import edge_tts

        async def _run():
            comm = edge_tts.Communicate(text, voice, rate=rate)
            await comm.save(str(out))

        asyncio.run(_run())
        if not out.exists():
            raise RuntimeError(f"TTS 生成失败: {out}")

    # ── 音频工具 ──────────────────────────────────────────────────────────────

    def audio_duration(self, f: Path) -> float:
        fp = _ffprobe()
        if fp:
            r = subprocess.run([
                fp, "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(f)
            ], capture_output=True, text=True)
            return float(r.stdout.strip())
        # fallback：用 ffmpeg 的 stderr 解析时长
        r = subprocess.run([
            _ffmpeg(), "-i", str(f), "-f", "null", "-"
        ], capture_output=True, text=True)
        import re
        m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", r.stderr)
        if m:
            h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + mi * 60 + s
        raise RuntimeError(f"无法获取音频时长: {f}")

    # ── HTML 录制 ─────────────────────────────────────────────────────────────

    async def record_html(self, html_file: Path, duration: float) -> Path:
        """用 Playwright 逐帧录制 HTML，生成静音视频"""
        from playwright.async_api import async_playwright

        frames_dir = self.temp_dir / f"frames_{html_file.stem}"
        frames_dir.mkdir(exist_ok=True)
        total_frames = int(DEFAULT_FPS * duration)

        # 将配音时长注入 URL，供 Reveal.js 自动推进 fragment 使用
        url = f"file://{html_file.absolute()}?dur={duration:.2f}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            ctx = await browser.new_context(viewport={"width": 1080, "height": 1920})
            page = await ctx.new_page()
            await page.goto(url, wait_until="networkidle")
            await asyncio.sleep(0.3)

            for i in range(total_frames):
                await page.screenshot(path=str(frames_dir / f"f{i:04d}.png"))
                await asyncio.sleep(1 / DEFAULT_FPS)

            await ctx.close()
            await browser.close()

        video_file = self.temp_dir / f"{html_file.stem}_silent.mp4"
        subprocess.run([
            _ffmpeg(), "-y", "-framerate", str(DEFAULT_FPS),
            "-i", str(frames_dir / "f%04d.png"),
            "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
            str(video_file)
        ], capture_output=True, check=True)

        for f in frames_dir.glob("*.png"):
            f.unlink()
        frames_dir.rmdir()

        return video_file

    # ── 合并 ──────────────────────────────────────────────────────────────────

    def merge(self, video: Path, audio: Path, out: Path):
        """音视频合并，带淡入淡出"""
        dur = self.audio_duration(audio)
        subprocess.run([
            _ffmpeg(), "-y",
            "-i", str(video), "-i", str(audio),
            "-c:v", "copy", "-c:a", "aac",
            "-af", f"afade=t=in:st=0:d=0.2,afade=t=out:st={dur - 0.3:.3f}:d=0.3",
            "-shortest", str(out)
        ], capture_output=True, check=True)

    def concat(self, videos: list, out: Path):
        """拼接多段视频"""
        list_file = self.temp_dir / "concat.txt"
        # 使用绝对路径，避免 Windows 相对路径问题
        lines = "\n".join(f"file '{Path(v).absolute().as_posix()}'" for v in videos)
        list_file.write_text(lines, encoding="utf-8")
        r = subprocess.run([
            _ffmpeg(), "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file.absolute()), "-c", "copy", str(out)
        ], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"concat 失败:\n{r.stderr.decode('utf-8', errors='replace')}")

    def cleanup(self):
        for f in self.temp_dir.iterdir():
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                for sub in f.iterdir():
                    sub.unlink()
                f.rmdir()

    # ── 主流程 ────────────────────────────────────────────────────────────────

    def run(self, script: dict, voice: str = DEFAULT_VOICE, rate: str = "+0%") -> Path:
        """
        执行完整技术管道

        Args:
            script: script.json 内容（含 shots[].narration 和 shots[].id）
            voice:  TTS音色
            rate:   TTS语速（如 "-10%" 减速）

        Returns:
            最终视频路径
        """
        shots = script["shots"]
        topic = script.get("topic", "video")
        print(f"\n[开始] 主题: {topic}\n")

        # 1. TTS：为每段口播生成配音
        print("[1/4] TTS 配音...")
        audio_files = []
        for shot in shots:
            audio_out = self.temp_dir / f"{shot['id']}.mp3"
            print(f"   {shot['id']}: {shot['narration'][:30]}...")
            self.tts(shot["narration"], audio_out, voice=voice, rate=rate)
            dur = self.audio_duration(audio_out)
            print(f"   -> {dur:.1f}s")
            audio_files.append(audio_out)
        print()

        # 2. 录制：按配音时长录制对应 HTML
        print("[2/4] 录制 HTML...")
        video_files = []
        for shot, audio in zip(shots, audio_files):
            html_file = self.output_dir / f"{shot['id']}.html"
            if not html_file.exists():
                raise FileNotFoundError(
                    f"找不到 {html_file}，请确认 Agent 已生成该 HTML 文件"
                )
            duration = self.audio_duration(audio)
            print(f"   {shot['id']}.html -> {duration:.1f}s")
            video = asyncio.run(self.record_html(html_file, duration))
            video_files.append(video)
        print()

        # 3. 合并：每段视频 + 对应配音
        print("[3/4] 音视频合并...")
        synced = []
        for shot, video, audio in zip(shots, video_files, audio_files):
            out = self.temp_dir / f"{shot['id']}_synced.mp4"
            self.merge(video, audio, out)
            synced.append(out)

        # 4. 拼接成品
        print("[4/4] 拼接输出...")
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        final = self.output_dir / f"output_{ts}.mp4"
        self.concat(synced, final)
        self.cleanup()

        size_mb = final.stat().st_size / 1024 / 1024
        print(f"\n[完成] 输出: {final}  ({size_mb:.1f}MB)\n")
        return final


def main():
    if len(sys.argv) < 2:
        print("用法: python generate_video.py <script.json> [--voice <音色>] [--rate <语速>] [--output <输出路径>]")
        print("示例: python generate_video.py output/script.json --voice zh-CN-YunxiNeural --rate -10%")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    if not script_path.exists():
        print(f"❌ 找不到脚本文件: {script_path}")
        sys.exit(1)

    script = json.loads(script_path.read_text(encoding="utf-8"))

    # 解析可选参数
    voice = DEFAULT_VOICE
    rate = "+0%"
    output_dir = script_path.parent

    args = sys.argv[2:]
    for i, arg in enumerate(args):
        if arg == "--voice" and i + 1 < len(args):
            voice = args[i + 1]
        elif arg == "--rate" and i + 1 < len(args):
            rate = args[i + 1]
        elif arg == "--output" and i + 1 < len(args):
            output_dir = Path(args[i + 1]).parent

    temp_dir = output_dir / ".tmp"
    pipeline = VideoPipeline(output_dir=output_dir, temp_dir=temp_dir)
    pipeline.run(script, voice=voice, rate=rate)


if __name__ == "__main__":
    main()
