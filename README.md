# 百度图片内容分析与解说助手

> 学号：423830107 | 姓名：毛坚再

基于百度AI开放平台实现的图片内容智能分析系统，支持图像识别、OCR文字识别、语音合成三大功能。

## 功能特性

- 🖼️ **图片上传预览** - 支持 JPG/PNG/BMP/GIF 等常见格式
- 🔍 **百度图像识别** - 通用物体、动物、花卉识别
- 📝 **OCR文字识别** - 自动提取图片中的文字内容
- 🔊 **语音合成解说** - 根据分析结果自动生成并朗读解说词
- 🖥️ **tkinter 图形界面** - 无需安装额外 GUI 库

## 技术栈

| 模块 | 技术 |
|------|------|
| 开发环境 | PyCharm 社区版 |
| 编程语言 | Python 3 |
| 图形界面 | tkinter（内置） |
| AI 接口 | 百度AI开放平台 |
| HTTP | requests |

## 百度 AI 接口使用

- 通用物体和场景识别
- 动物识别
- 花卉识别
- 通用文字识别（高精度）
- 语音合成

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 密钥

编辑 `config.py`，填入你的百度 AI 密钥：

```python
API_KEY = "你的API Key"
SECRET_KEY = "你的Secret Key"
```

### 3. 运行程序

```bash
python main.py
```

## 使用方法

1. 点击「上传图片」选择要分析的图片
2. 点击「开始分析」，系统自动调用百度AI接口
3. 查看右侧分析结果和解说词
4. 点击「朗读解说」播放语音解说

## 项目结构

```
baidu-image-assistant/
├── config.py        # 配置文件（API密钥）
├── baidu_api.py     # 百度API调用模块
├── main.py          # 主程序（tkinter GUI）
├── requirements.txt # 依赖列表
└── README.md        # 项目说明
```
