"""
multimodal/_common.py — 多模态示例共享配置与工具

everos_cloud 的 client.v1.memories.add() 被 lib 层重写为「透明多模态上传」：
content item 的 type != "text" 且带 uri 时，SDK 自动：
  - uri 是本地文件路径   → object.sign 签名 → 上传 → 替换为 object_key
  - uri 是 http(s) URL   → 下载 → 签名 → 上传 → 替换为 object_key
  - uri 已是 object_key   → 原样透传

支持的 content type：text / image / audio / doc / pdf / html / email
"""
import os
import time
import base64
import tempfile

API_KEY = os.getenv("EVEROS_API_KEY", "ddcf3ffb-df31-4c9c-9d30-fb2ee67aed26")
BASE_URL = os.getenv("EVER_OS_BASE_URL", "https://dev-gateway.aws.evermind.ai")


def now_ms() -> int:
    return int(time.time() * 1000)


def make_test_image() -> str:
    """生成一张 1x1 PNG 测试图，返回本地路径（演示本地文件自动上传）。

    注意：1x1 空白图 OCR/VLM 提取不到语义内容（dev 会得到空 episode）。
    需要验证图片记忆提取时，请用 SAMPLE_IMAGE_URL（含真实场景的公网图）。
    """
    png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M8AAAMBAQDJ/IhBAAAAAElFTkSuQmCC"
    )
    path = os.path.join(tempfile.gettempdir(), "everos_mm_demo.png")
    with open(path, "wb") as f:
        f.write(png)
    return path


def make_test_audio() -> str:
    """生成一个 1 秒静音 WAV 测试音频（16kHz / 16-bit / mono），返回本地路径。"""
    import wave

    path = os.path.join(tempfile.gettempdir(), "everos_mm_demo.wav")
    sample_rate = 16000
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * sample_rate)  # 1 秒静音
    return path


# 公网图片 URL（演示 http(s) 自动下载+上传；含真实场景，OCR/VLM 可提取语义）
# 内容：3D 卡通风格，戴眼镜的年轻人在书房自拍，背景有电脑代码/书架/绿植，含中文「我的书房」
SAMPLE_IMAGE_URL = "https://i.ibb.co/vvChVsdS/Wechat-IMG175.png"
