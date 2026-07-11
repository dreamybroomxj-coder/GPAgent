import os
import shutil
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.config import DATA_DIR

def clean_cache(mode):
    """
    清理缓存文件。

    参数：
        mode (int): 清理模式。
                    1 - 删除 data/ 下所有 .mp4 文件以及所有 chunk/ 目录中的文件。
                    2 - 在 mode=1 的基础上，再删除所有 .txt 和 .mp3 文件。
                    3 - 直接清空整个 data/ 目录。

    抛出：
        ValueError: mode 不是 1、2 或 3 时抛出。
    """

    if mode not in (1, 2, 3):
        raise ValueError(f"mode 必须为 1、2 或 3，当前值：{mode}")

    data_dir = DATA_DIR

    if not os.path.isdir(data_dir):
        print(f"data/ 目录不存在：{data_dir}")
        return

    if mode == 3:
        # 直接清空整个 data/ 目录（保留 data/ 本身）
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path) or os.path.islink(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        print("mode=3：已清空 data/ 目录。")
        return

    # mode == 1 或 mode == 2
    for root, dirs, files in os.walk(data_dir, topdown=False):
        rel_path = os.path.relpath(root, data_dir)

        for filename in files:
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()

            # mode=1 & mode=2 共同操作：删除 mp4 和 chunk/ 中的文件
            if ext == ".mp4":
                os.remove(filepath)
                print(f"已删除 mp4：{filepath}")

            # chunk/ 目录中的文件全部删除
            if os.path.basename(root) == "chunk" or "chunk" in rel_path.split(os.sep):
                os.remove(filepath)
                print(f"已删除 chunk 文件：{filepath}")

            # mode=2 额外操作：删除 txt 和 mp3
            if mode == 2 and ext in (".txt", ".mp3"):
                os.remove(filepath)
                print(f"已删除 {ext}：{filepath}")

        # 删除空的 chunk 目录（mode=1 或 mode=2 后清理）
        if os.path.basename(root) == "chunk":
            try:
                os.rmdir(root)
                print(f"已删除空 chunk 目录：{root}")
            except OSError:
                # 目录非空则跳过
                pass

    print(f"mode={mode}：缓存清理完成。")
