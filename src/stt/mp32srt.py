import os
from faster_whisper import WhisperModel

from src.config import MODELS_DIR


def _format_srt_timestamp(seconds):
    """将秒数转换为 SRT 使用的 HH:MM:SS,mmm 格式。"""
    total_ms = round(seconds * 1000)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def mp32srt(i_dir,o_dir="nan",modelname="tiny.en",usedevice="cpu"):

    if not os.path.isfile(i_dir):
        raise FileNotFoundError(f"找不到文件：{i_dir}")

    # 检查扩展名
    if os.path.splitext(i_dir)[1].lower() != ".mp3":
        raise ValueError("输入文件必须是 .mp3 文件")

    # 确定输出路径
    if o_dir == "nan":
        base = os.path.splitext(i_dir)[0]
        o_path = base + ".srt"
    else:
        o_path = o_dir

    if usedevice == "cpu":
        compute_type = "int8"
    elif usedevice == "cuda":
        compute_type = "float16"
    else:
        compute_type = "default"

    model = WhisperModel(
        modelname,
        device=usedevice,
        compute_type=compute_type,
        download_root=str(MODELS_DIR)
    )

    segments, _ = model.transcribe(i_dir, beam_size=5)

    # 输出目录
    output_dir = os.path.dirname(o_path)
    if output_dir == "":
        output_dir = "."
    os.makedirs(output_dir, exist_ok=True)

    with open(o_path, "w", encoding="utf-8") as srt_file:
        for index, segment in enumerate(segments, start=1):
            start = _format_srt_timestamp(segment.start)
            end = _format_srt_timestamp(segment.end)
            text = segment.text.strip()
            srt_file.write(f"{index}\n{start} --> {end}\n{text}\n\n")

    return o_path
