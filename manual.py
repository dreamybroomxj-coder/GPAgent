import os
from datetime import datetime

from src.get.get import fetch_mp4_url_and_download
from src.utils.mp42mp3 import mp42mp3
from src.stt.stt import stt
from src.utils.srt2txt import srt2txt
from src.ai.skills import abstract, takeaway, queslist, inte
# 最简单的手动版本，跑通了之后再加复杂的功能
print("这个程序比较不鲁棒，请确定网页端视频能播放之后再运行")
url = input("输入TRMS播放页面url: ")
course_name = input("输入课程名称(方便为主，同名的课会统一存放): ")
strip_time = input("视频开头到老师开始讲课有多久？有些课会录到前一节课的老师(单位:min，默认0): ")
if strip_time == "":
    strip_time = 0
else:
    strip_time = float(strip_time)
print("准备开始爬取")
video_path = fetch_mp4_url_and_download(url, course_name)
print(f"下载完成：{video_path}")

print("开始转mp3")
audio_path = mp42mp3(video_path)
print(f"转音频完成：{audio_path}")


print("开始分块、转写")
srt_path = stt(audio_path,"nan","tiny.en",10)
print(f"转写完成：{srt_path}")

print("开始转txt")
txt_path = srt2txt(srt_path, "nan", cuthead=strip_time)
print(f"转txt完成：{txt_path}")

# 读取转写文本
print("读取转录文本……")
with open(txt_path, "r", encoding="utf-8") as f:
    transcript = f.read()

print(f"\n转录文本共 {len(transcript)} 字符，开始 AI 处理...")

# 调用 AI 生成四部分内容
print("  [1/4] 生成摘要...")
sec_abstract = abstract(transcript)
print("  [2/4] 生成问题清单...")
sec_queslist = queslist(transcript)
print("  [3/4] 整理知识点...")
sec_takeaway = takeaway(transcript)
print("  [4/4] 提取考试/作业情报...")
sec_inte = inte(transcript)

# 组装 Markdown 文件
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join("export", course_name)
os.makedirs(output_dir, exist_ok=True)
md_path = os.path.join(output_dir, f"{timestamp}.md")

md_content = f"""# 摘要

{sec_abstract}

# 问题清单

{sec_queslist}

# 知识点

{sec_takeaway}

# 情报

{sec_inte}
"""

with open(md_path, "w", encoding="utf-8") as f:
    f.write(md_content)

print(f"\n✅ 笔记已保存至：{md_path}")
