"""
配置文件 - 存放百度 API 密钥
"""

# 百度 AI 开放平台应用密钥
API_KEY = "XG9Va6EexJ7uAGzysnPJo8hb"
SECRET_KEY = "JG5ygCODlNaKAaMkyCPPXQm0rHQTbYdf"

# 与百度 AK/SK 对应（语音合成用）
BAIDU_AK = API_KEY
BAIDU_SK = SECRET_KEY

# 语音合成参数
TTS_PER = 0   # 发音人：0 女声，1 男声，3 情感男声，4 情感女声
TTS_SPD = 5   # 语速：0-15，数字越大越快
TTS_PIT = 5   # 音调：0-15
TTS_VOL = 5   # 音量：0-15
TTS_AUE = 3   # 格式：3=mp3-16k（推荐）, 5=pcm-16k

# 学生信息
STUDENT_NAME = "毛坚再"
STUDENT_ID = "423830107"
