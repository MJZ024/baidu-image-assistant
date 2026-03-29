"""
百度 AI API 调用模块
包含：图像识别、OCR文字识别、语音合成
"""
import os
import json
import base64
import requests
import config


# ---------------------------------------------------------------
# 1. Access Token 获取（语音合成需要）
# ---------------------------------------------------------------

def get_access_token():
    """获取百度 API Access Token（有效期 30 天）"""
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": config.BAIDU_AK,
        "client_secret": config.BAIDU_SK,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    return result.get("access_token")


# ---------------------------------------------------------------
# 2. 通用物体和场景识别
# ---------------------------------------------------------------

def detect_objects(image_path: str) -> dict:
    """
    调用百度通用物体和场景识别 API
    返回: {"result": [{"keyword": "猫", "score": 0.98}, ...]}
    """
    with open(image_path, "rb") as f:
        img_bytes = base64.b64encode(f.read()).decode("utf-8")

    url = "https://aip.baidubce.com/rest/2.0/image-classify/v2/advanced_general"
    params = {"access_token": get_access_token()}
    data = {"image": img_bytes, "baike_num": 1}
    resp = requests.post(url, params=params, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------
# 3. 车辆检测
# ---------------------------------------------------------------

def detect_vehicle(image_path: str) -> dict:
    """车辆检测"""
    with open(image_path, "rb") as f:
        img_bytes = base64.b64encode(f.read()).decode("utf-8")

    url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/vehicle_detect"
    params = {"access_token": get_access_token()}
    data = {"image": img_bytes}
    resp = requests.post(url, params=params, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------
# 4. 花卉识别
# ---------------------------------------------------------------

def detect_flower(image_path: str) -> dict:
    """花卉识别"""
    with open(image_path, "rb") as f:
        img_bytes = base64.b64encode(f.read()).decode("utf-8")

    url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/flower"
    params = {"access_token": get_access_token()}
    data = {"image": img_bytes, "top_num": 5}
    resp = requests.post(url, params=params, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------
# 5. 动物识别
# ---------------------------------------------------------------

def detect_animal(image_path: str) -> dict:
    """动物识别"""
    with open(image_path, "rb") as f:
        img_bytes = base64.b64encode(f.read()).decode("utf-8")

    url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/animal"
    params = {"access_token": get_access_token()}
    data = {"image": img_bytes, "top_num": 5}
    resp = requests.post(url, params=params, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------
# 6. OCR 文字识别
# ---------------------------------------------------------------

def detect_text(image_path: str) -> dict:
    """
    通用文字识别（高精度）
    返回: {"words_result": [{"words": "识别出的文字"}, ...]}
    """
    with open(image_path, "rb") as f:
        img_bytes = base64.b64encode(f.read()).decode("utf-8")

    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"
    params = {"access_token": get_access_token()}
    data = {"image": img_bytes}
    resp = requests.post(url, params=params, data=data, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ---------------------------------------------------------------
# 7. 语音合成（TTS）
# ---------------------------------------------------------------

def text_to_speech(text: str, output_path: str = "output.mp3"):
    """
    调用百度语音合成 API，将文字转为音频文件
    text: 要朗读的文字
    output_path: 输出音频文件路径
    """
    token = get_access_token()
    url = f"https://tsn.baidu.com/text2audio?access_token={token}"
    data = {
        "tex": text,
        "per": config.TTS_PER,
        "spd": config.TTS_SPD,
        "pit": config.TTS_PIT,
        "vol": config.TTS_VOL,
        "aue": config.TTS_AUE,
        "cuid": "baidu_image_assistant",
        "lan": "zh",
        "ctp": 1,
    }
    resp = requests.post(url, data=data, timeout=15)
    # 如果返回的是音频流（MP3），写入文件
    content_type = resp.headers.get("Content-Type", "")
    if "audio" in content_type or resp.content[:2] == b"ID3":
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return output_path
    else:
        # 返回了错误信息
        return resp.text


# ---------------------------------------------------------------
# 8. 综合分析（整合所有 API 结果生成解说词）
# ---------------------------------------------------------------

def analyze_image(image_path: str) -> dict:
    """
    综合调用多个百度 API 分析图片，返回结构化结果
    """
    results = {
        "objects": [],
        "texts": [],
        "vehicle": None,
        "flower": None,
        "animal": None,
    }

    # 通用物体识别（必做）
    try:
        obj_data = detect_objects(image_path)
        if "result" in obj_data:
            results["objects"] = [
                {"keyword": item.get("keyword", ""), "score": round(item.get("score", 0) * 100, 1)}
                for item in obj_data["result"][:8]
            ]
    except Exception as e:
        results["objects_error"] = str(e)

    # OCR 文字识别
    try:
        text_data = detect_text(image_path)
        if "words_result" in text_data:
            results["texts"] = [
                item.get("words", "") for item in text_data["words_result"]
            ]
    except Exception as e:
        results["texts_error"] = str(e)

    # 动物识别（尝试）
    try:
        animal_data = detect_animal(image_path)
        if "result" in animal_data and animal_data["result"]:
            top = animal_data["result"][0]
            results["animal"] = {
                "name": top.get("name", ""),
                "score": round(top.get("score", 0) * 100, 1)
            }
    except Exception:
        pass

    # 花卉识别（尝试）
    try:
        flower_data = detect_flower(image_path)
        if "result" in flower_data and flower_data["result"]:
            top = flower_data["result"][0]
            results["flower"] = {
                "name": top.get("name", ""),
                "score": round(top.get("score", 0) * 100, 1)
            }
    except Exception:
        pass

    return results


# ---------------------------------------------------------------
# 9. 根据分析结果生成解说词
# ---------------------------------------------------------------

def generate_narration(analysis_result: dict) -> str:
    """根据 API 返回结果生成自然语言解说词"""
    parts = []
    student_name = config.STUDENT_NAME

    objects = analysis_result.get("objects", [])
    texts = analysis_result.get("texts", [])
    animal = analysis_result.get("animal")
    flower = analysis_result.get("flower")

    # 动物优先
    if animal and animal["name"]:
        parts.append(f"图片中检测到一只{animal['name']}，置信度{animal['score']}%。")

    # 花卉其次
    if flower and flower["name"]:
        parts.append(f"图中有一朵{flower['name']}，识别置信度{flower['score']}%。")

    # 通用物体
    if objects:
        keywords = [o["keyword"] for o in objects[:5] if o["keyword"]]
        if keywords:
            if animal or flower:
                parts.append(f"同时，图中还包含：{''.join(keywords[:4])}等元素。")
            else:
                items = "、".join(keywords[:5])
                parts.append(f"经过百度AI图像识别技术分析，这张图片中的主要内容包括：{items}。")

    # 文字
    if texts:
        text_preview = "、".join(texts[:3])
        if len(text_preview) > 50:
            text_preview = text_preview[:50] + "……"
        parts.append(f"图中还检测到文字内容：{text_preview}。")

    # 兜底
    if not parts:
        parts.append("这张图片的内容分析已完成，具体信息请查看右侧详情面板。")

    narration = "欢迎使用图片内容分析与解说系统。我是" + student_name + "。" + "".join(parts)
    narration += "感谢观看。"

    return narration


# ---------------------------------------------------------------
# 10. 一键分析+解说（主流程）
# ---------------------------------------------------------------

def full_analysis(image_path: str, audio_output: str = "narration.mp3") -> dict:
    """
    完整流程：分析图片 + 生成解说词 + 合成语音
    返回: {"narration": 解说词, "audio": 音频文件路径, "analysis": 分析结果}
    """
    # 1. 分析
    analysis = analyze_image(image_path)

    # 2. 生成解说词
    narration = generate_narration(analysis)

    # 3. 语音合成
    audio_file = text_to_speech(narration, audio_output)
    if not audio_file or audio_file.startswith("{"):
        audio_file = None  # 合成失败

    return {
        "narration": narration,
        "audio": audio_file,
        "analysis": analysis,
        "student_name": config.STUDENT_NAME,
        "student_id": config.STUDENT_ID,
    }
