import os


def _time_to_sec(t):
    """将 00:00:33,000 格式转换为秒数"""
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def srt2txt(i_dir, o_dir="nan", cuthead=0, cuttail=0):
    """
    将标准SRT字幕转换为TXT。

    参数
    ----------
    i_dir : str
        输入srt文件路径。

    o_dir : str, default="nan"
        输出txt路径。
        若为"nan"，则保存在输入文件同目录，仅扩展名改为txt。
    cuthead/cuttail : float, default=0
        丢弃头/尾多久的内容
        单位是min

    """
    if not os.path.isfile(i_dir):
        raise FileNotFoundError(f"找不到文件：{i_dir}")

    # 检查扩展名
    if os.path.splitext(i_dir)[1].lower() != ".srt":
        raise ValueError("输入文件必须是 .srt 文件")

    # 确定输出路径
    if o_dir == "nan":
        base = os.path.splitext(i_dir)[0]
        o_path = base + ".txt"
    else:
        o_path = o_dir

    # 读取文件
    with open(i_dir, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 先算总时长（用最后一个时间行的结束时间）
    total_duration = 0
    for idx, line in enumerate(lines):
        if idx % 4 == 1 and "-->" in line:
            _, end_t = line.strip().split(" --> ")
            total_duration = _time_to_sec(end_t)

    head_cut_sec = cuthead * 60
    tail_cut_sec = total_duration - cuttail * 60

    result = []
    keep = True  # 当前这一块字幕是否保留

    for idx, line in enumerate(lines):
        mod = idx % 4
        if mod == 1 and "-->" in line:
            # 第4n-2行：时间行，判断是否在保留区间内
            start_t, end_t = line.strip().split(" --> ")
            start_sec = _time_to_sec(start_t)
            end_sec = _time_to_sec(end_t)
            # 只要字幕块与保留区间有重叠即保留
            keep = (end_sec > head_cut_sec) and (start_sec < tail_cut_sec)
        elif mod == 2 and keep:
            # 第4n-1行（文本行）：去掉换行，加空格
            result.append(line.rstrip("\r\n") + " ")

    # 写入txt
    with open(o_path, "w", encoding="utf-8") as f:
        f.writelines(result)

    print(f"已保存：{o_path}")
    return o_path