import os
import subprocess


def mp42mp3(i_dir, o_dir="nan"):
    """
    将 MP4 文件转换为 MP3。

    参数：
        i_dir (str): 输入 MP4 文件路径。
        o_dir (str): 输出目录，默认为 "nan"。
                     如果为 "nan"，则保存在输入文件所在目录。

    返回：
        str: 输出 MP3 文件路径。
    """

    # 检查输入文件是否存在
    if not os.path.isfile(i_dir):
        raise FileNotFoundError(f"找不到文件：{i_dir}")

    # 检查扩展名
    if os.path.splitext(i_dir)[1].lower() != ".mp4":
        raise ValueError("输入文件必须是 .mp4 文件")

    # 获取文件名（无扩展名）
    if o_dir == "nan":
        base = os.path.splitext(i_dir)[0]
        o_path = base + ".mp3"
    else:
        o_path = o_dir



    # ffmpeg 命令
    cmd = [
        "ffmpeg",
        "-y",              # 覆盖已有文件
        "-i", i_dir,       # 输入文件
        "-vn",             # 不处理视频流
        "-acodec", "libmp3lame",
        "-q:a", "2",       # VBR，高质量（0最好，9最差）
        o_path
    ]

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        raise RuntimeError("未找到 ffmpeg，请确认 ffmpeg 已安装并加入 PATH。")
    except subprocess.CalledProcessError:
        raise RuntimeError("ffmpeg 转换失败。")

    return o_path