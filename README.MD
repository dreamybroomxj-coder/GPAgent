# GPAgent

> [English Version](docs/README(EN).MD)

自动化课堂笔记工具。从 HKUST-GZ 的 TRMS 平台爬取课程回放视频，转为音频后用 Whisper 转写成文字，再通过 LLM 自动生成摘要、知识点、自测题和考试/作业情报等笔记，输出到 Markdown 文件。

## Setup

### 1. 环境依赖

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/)（用于音视频转换和静音检测，需加入 PATH）

### 2. 安装

```bash
git clone https://github.com/dreamybroomxj-coder/GPAgent
cd GPAgent
```

使用conda创建虚拟环境

```bash
conda create -n gpagent python=3.10
conda activate gpagent
pip install -r requirements.txt
# 安装 Playwright 浏览器（Chromium）
playwright install chromium
```


### 3. 配置文件

把`config`文件夹下的`example_api.json`和`example_config.json`改名为`api.json`和`config.json`，填入LLM链接和APIkey，你的学校邮箱账号密码，不带@connect.hkust-gz.edu.cn（用于自动登录）

### 4. 运行

运行手动模式测试全流程：

```bash
python manual.py
```

按提示输入 TRMS 播放页 URL、课程名称等，程序会依次完成爬取 → 转音频 → 转写 → AI 生成笔记。

自动值守模式仍在开发中……

## 文件结构

```
GPAgent/
├── config/                     # 配置文件目录
│   ├── example_config.json     # 账号/课程配置模板
│   ├── example_api.json        # API 配置模板
│   ├── config.json             # 实际账号配置（gitignore）
│   ├── api.json                # 实际 API 配置（gitignore）
│   └── state.json              # 浏览器登录状态（gitignore）
├── src/
│   ├── config.py               # 配置读取函数
│   ├── get/
│   │   ├── get.py              # Playwright 爬取 MP4 直链并下载
│   │   └── getschedule.py      # 读取课程表
│   ├── stt/
│   │   ├── stt.py              # 语音转文字主流程（分块→转写→合并）
│   │   └── mp32srt.py          # 单段 MP3→SRT 转写
│   ├── ai/
│   │   ├── askai.py            # LLM API 调用封装（ask / ask_json / ask_reason）
│   │   └── skills.py           # AI 笔记生成（摘要/知识点/自测题/情报/配图推荐）
│   └── utils/
│       ├── mp42mp3.py          # MP4→MP3 音频提取（ffmpeg）
│       ├── srt2txt.py          # SRT 字幕→纯文本（去时间戳）
│       └── clean.py            # 缓存清理（按模式删除 data/ 中的文件）
├── data/                       # 运行时数据目录（gitignore）
│   └── <课程名>/               # 按课程分目录存放 mp4/mp3/srt/txt/chunk/
├── export/                     # AI 生成的笔记输出目录（gitignore）
├── manual.py                   # 手动模式入口，交互式运行完整流程
├── ideas.MD                    # 功能规划与想法
└── README.MD
```

## TODO
- [ ] 基于提示词让AI生成课程内容可能的专业词汇列表，作为语音识别的prompt

- [ ] 自动值守模式：读取课程主页面的时间表，按照这个每次一下课自动去进行爬取和处理

- [ ] 多媒体感知：AI判断文稿的哪部分最需要配图，由此定位时间戳，获取原视频对应帧画面，插入笔记
