import os
import re
import subprocess
import json
from time import sleep

from .mp32srt import mp32srt


def get_duration_ms(audio_path):
    """用 ffprobe 获取音频时长（毫秒）"""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(result.stdout)
    return int(float(info["format"]["duration"]) * 1000)


def detect_silence(audio_path, start_ms, end_ms, min_silence_ms=500, silence_db=-30):
    """
    用 ffmpeg silencedetect 检测 [start_ms, end_ms] 区间内的静音段。
    返回 [(silence_start_ms, silence_end_ms), ...] 列表。
    """
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_ms / 1000),
        "-t", str((end_ms - start_ms) / 1000),
        "-i", audio_path,
        "-af", f"silencedetect=n={silence_db}dB:d={min_silence_ms / 1000}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    # 解析 ffmpeg 输出: silence_start: X, silence_end: Y
    gaps = []
    silence_start = None
    for line in stderr.splitlines():
        m_start = re.search(r"silence_start:\s*([\d.]+)", line)
        m_end = re.search(r"silence_end:\s*([\d.]+)", line)
        if m_start:
            silence_start = float(m_start.group(1)) * 1000  # 转为 ms
        elif m_end and silence_start is not None:
            silence_end = float(m_end.group(1)) * 1000
            # 这些值是相对于 ss 的偏移，需要加回 start_ms
            gaps.append((start_ms + silence_start, start_ms + silence_end))
            silence_start = None

    return gaps


def find_split_point(silence_gaps, preferred_ms, margin_ms):
    """
    在 preferred_ms ± margin_ms 范围内找最大的静音空档，返回其中点。
    找不到则返回 preferred_ms（硬切）。
    """
    if margin_ms==0:
        return preferred_ms
    candidates = [
        (s, e) for s, e in silence_gaps
        if preferred_ms - margin_ms <= s and e <= preferred_ms + margin_ms
    ]
    if not candidates:
        return preferred_ms

    # 选最长的静音段
    best = max(candidates, key=lambda x: x[1] - x[0])
    return (best[0] + best[1]) // 2


def split_audio(audio_path, chunk_dir, duration_ms, margin_ms=0):
    """
    将音频按 ~15min 切分，存入 chunk_dir。
    只对每个边界附近做局部静音检测，避免全音频扫描。
    返回 [(chunk_path, offset_ms), ...]。
    """
    CHUNK_TARGET_MS = 15 * 60 * 1000   # 15 min

    os.makedirs(chunk_dir, exist_ok=True)

    split_points = [0]  # int
    current = 0
    while current + CHUNK_TARGET_MS < duration_ms:
        preferred = current + CHUNK_TARGET_MS

        if margin_ms > 0:
            # 只对边界附近的窗口检测静音
            search_start = max(0, preferred - margin_ms)
            search_end = min(duration_ms, preferred + margin_ms)
            local_silence = detect_silence(audio_path, search_start, search_end)
            split = int(find_split_point(local_silence, preferred, margin_ms))
        else:
            split = preferred

        split = int(max(current + 1000, min(duration_ms, split)))  # 至少切 1 秒
        split_points.append(split)
        current = split

    chunks = []
    for i in range(len(split_points)):
        start = split_points[i]
        end = split_points[i + 1] if i + 1 < len(split_points) else duration_ms
        chunk_name = f"{start}.mp3"
        chunk_path = os.path.join(chunk_dir, chunk_name)

        # ffmpeg 切分（-acodec copy 极快，不走编码器）
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start / 1000),
            "-t", str((end - start) / 1000),
            "-i", audio_path,
            "-acodec", "copy",
            chunk_path
        ]
        subprocess.run(cmd, capture_output=True)
        chunks.append((chunk_path, start))
        print(f"  chunk {len(chunks)}: {start / 1000:.0f}s – {end / 1000:.0f}s")

    return chunks



def merge_srt(chunks_srt, offset_ms_list, output_path):
    """
    合并多个 SRT 文件，加上对应的时间偏移，重新编号后写入 output_path。
    """
    all_entries = []

    for srt_path, offset in zip(chunks_srt, offset_ms_list):
        if not os.path.exists(srt_path):
            continue
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 SRT 条目
        blocks = content.strip().split("\n\n")
        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) < 2:
                continue
            # lines[0] = index, lines[1] = timestamp, lines[2:] = text
            ts_line = lines[1]
            m = re.match(
                r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*"
                r"(\d{2}):(\d{2}):(\d{2}),(\d{3})",
                ts_line
            )
            if not m:
                continue
            start_ms = (int(m.group(1)) * 3600 + int(m.group(2)) * 60 +
                        int(m.group(3))) * 1000 + int(m.group(4))
            end_ms = (int(m.group(5)) * 3600 + int(m.group(6)) * 60 +
                      int(m.group(7))) * 1000 + int(m.group(8))

            start_ms += offset
            end_ms += offset

            # 重新格式化时间戳
            def _ms_to_ts(ms):
                h = ms // 3600000
                m = (ms % 3600000) // 60000
                s = (ms % 60000) // 1000
                rem = ms % 1000
                return f"{h:02d}:{m:02d}:{s:02d},{rem:03d}"

            new_ts = f"{_ms_to_ts(start_ms)} --> {_ms_to_ts(end_ms)}"
            new_block = "\n".join([str(len(all_entries) + 1), new_ts] + lines[2:])
            all_entries.append(new_block)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_entries) + "\n")


def stt(i_dir, o_dir="nan", modelname="tiny.en", cooldown=0,margin_ms=0):
    """
    将 MP3 转写为 SRT，自动处理长音频的分割。

    参数
    ----------
    i_dir : str
        输入 mp3 文件路径。
    o_dir : str, default="nan"
        输出 srt 文件路径，"nan" 则与输入同目录、同名、改扩展名为 .srt。
    modelname : str, default="tiny.en"
        Whisper 模型名。
    cooldown : float, default=0
        每个分片处理间的冷却时间（秒），让 GPU 休息。
    """
    if not os.path.isfile(i_dir):
        raise FileNotFoundError(f"找不到文件：{i_dir}")

    if os.path.splitext(i_dir)[1].lower() != ".mp3":
        raise ValueError("输入文件必须是 .mp3 文件")

    if o_dir == "nan":
        o_path = os.path.splitext(i_dir)[0] + ".srt"
    else:
        o_path = o_dir

    duration_ms = get_duration_ms(i_dir)
    CHUNK_TARGET_MS = 15 * 60 * 1000
    MARGIN_MS = 1 * 60 * 1000

    # 时长在阈值内 → 直接转写
    if duration_ms <= CHUNK_TARGET_MS + MARGIN_MS:
        return mp32srt(i_dir, o_path, modelname)

    # 需要切分
    input_dir = os.path.dirname(i_dir)
    chunk_dir = os.path.join(input_dir, "chunk")
    chunks = split_audio(i_dir, chunk_dir, duration_ms,margin_ms)
    print(f"音频长度 {duration_ms / 60000:.1f} min，切分为 {len(chunks)} 个片段")

    chunk_srt_paths = []
    offsets = []
    for idx, (chunk_path, offset_ms) in enumerate(chunks):
        print(f"  转写片段 {idx + 1}/{len(chunks)} (偏移 {offset_ms / 1000:.0f}s)...")
        chunk_srt = os.path.splitext(chunk_path)[0] + ".srt"
        mp32srt(chunk_path, chunk_srt, modelname)
        chunk_srt_paths.append(chunk_srt)
        offsets.append(offset_ms)
        if cooldown > 0 and idx < len(chunks) - 1:
            sleep(cooldown)

    # 合并 SRT
    merge_srt(chunk_srt_paths, offsets, o_path)
    print(f"合并 SRT 完成：{o_path}")

    return o_path


def merge_chunks(chunk_dir, output_path=None):
    """
    直接从 chunk 文件夹合并已识别好的 SRT 文件，用于 stt() 已切分识别完毕但拼接出错时补救。

    参数
    ----------
    chunk_dir : str
        chunk 文件夹路径，其中应包含 {start_ms}.mp3 和 {start_ms}.srt 文件。
    output_path : str, optional
        输出 srt 路径，默认与 chunk_dir 的父目录同名 .srt。
    """
    if not os.path.isdir(chunk_dir):
        raise FileNotFoundError(f"找不到文件夹：{chunk_dir}")

    # 扫 chunk 文件：找所有 {start_ms}.mp3，配对同名 .srt
    chunks = []
    for fname in os.listdir(chunk_dir):
        if not fname.endswith(".mp3"):
            continue
        name = fname[:-4]  # 去掉 .mp3
        if name.endswith(".0"):
            name=name[:-2]
        chunk_path = os.path.join(chunk_dir, fname)
        srt_path = os.path.join(chunk_dir, name + ".srt")
        try:
            offset_ms = int(name)  # 文件名就是起始毫秒数
        except ValueError:
            print(f"⚠️ 跳过无法解析偏移量的文件: {fname}")
            continue
        chunks.append((offset_ms, srt_path))

    if not chunks:
        print("❌ 未在 chunk 文件夹中找到有效的 mp3/srt 配对")
        return

    # 按偏移量排序
    chunks.sort(key=lambda x: x[0])
    srt_paths = [c[1] for c in chunks]
    offsets = [c[0] for c in chunks]

    # 确定输出路径
    if output_path is None:
        parent_dir = os.path.dirname(chunk_dir)
        base = os.path.basename(parent_dir)
        output_path = os.path.join(parent_dir, base + ".srt")

    merge_srt(srt_paths, offsets, output_path)
    print(f"合并完成：{output_path}")
    return output_path


