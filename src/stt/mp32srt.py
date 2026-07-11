import os
import whisper
from whisper.utils import get_writer
from src.config import MODELS_DIR
"""model = whisper.load_model(
    "base.en",
    download_root="src/stt/model"
)

result = model.transcribe("src/stt/audio/moon.mp3")

writer = get_writer("srt", "src/stt/output")
writer(result, "src/stt/audio/moon.mp3")
"""

def mp32srt(i_dir,o_dir="nan",modelname="tiny.en"):

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

    model = whisper.load_model(
        modelname,
        download_root=MODELS_DIR
    )

    result = model.transcribe(i_dir)
    #writer = get_writer("srt", "src/stt/output")
    #writer(result, "src/stt/audio/moon.mp3")



    # 识别
    result = model.transcribe(
        i_dir,       
        verbose=False           #显示进度
    )

    # 输出目录
    output_dir = os.path.dirname(o_path)
    if output_dir == "":
        output_dir = "."

    # 文件名（无扩展名）
    output_name = os.path.splitext(os.path.basename(o_path))[0]

    writer = get_writer("srt", output_dir)
    writer(result, output_name)

    return o_path
    