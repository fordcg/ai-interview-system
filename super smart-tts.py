# -*- coding:utf-8 -*-

import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
import os

#本demo示例是单次上传文本的示例，如果用在对时效要求高的交互场景，需要流式上传文本
# STATUS_FIRST_FRAME = 0  # 第一帧的标识
# STATUS_CONTINUE_FRAME = 1  # 中间帧标识
# STATUS_LAST_FRAME = 2  # 最后一帧的标识


class Ws_Param(object):
    # 初始化 - 修复为正确的超拟人TTS格式
    def __init__(self, APPID, APIKey, APISecret, Text):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        # 修复：确保Text不为None
        self.Text = Text if Text and isinstance(Text, str) else "测试文本"

        # 协议头部 - 超拟人TTS格式
        self.CommonArgs = {
            "app_id": self.APPID,
            "status": 2  # 请求状态：0开始, 1中间, 2结束
        }

        # 能力参数 - 超拟人TTS格式（x5系列发音人不支持oral配置）
        self.BusinessArgs = {
            "tts": {
                "vcn": "x5_lingyuyan_flow",  # 发音人参数，更换不同的发音人会有不同的音色效果
                "volume": 50,    # 设置音量大小
                "rhy": 0,        # 是否返回拼音标注 0:不返回拼音, 1:返回拼音（纯文本格式，utf8编码）
                "speed": 50,     # 设置合成语速，值越大，语速越快
                "pitch": 50,     # 设置振幅高低，可通过该参数调整效果
                "bgs": 0,        # 背景音 0:无背景音, 1:内置背景音1, 2:内置背景音2
                "reg": 0,        # 英文发音方式 0:自动判断处理，如果不确定将按照英文词语拼写处理（缺省）, 1:所有英文按字母发音, 2:自动判断处理，如果不确定将按照字母朗读
                "rdn": 0,        # 合成音频数字发音方式 0:自动判断, 1:完全数值, 2:完全字符串, 3:字符串优先
                "audio": {
                    "encoding": "lame",      # 合成音频格式， lame 合成音频格式为mp3
                    "sample_rate": 24000,    # 合成音频采样率， 16000, 8000, 24000
                    "channels": 1,           # 音频声道数
                    "bit_depth": 16,         # 合成音频位深 ：16, 8
                    "frame_size": 0
                }
            }
        }

        # 输入数据段 - 超拟人TTS格式
        try:
            # 修复：确保文本不为空并正确编码
            text_to_encode = self.Text
            if not text_to_encode or not isinstance(text_to_encode, str):
                text_to_encode = "测试文本"

            encoded_text = str(base64.b64encode(text_to_encode.encode('utf-8')), "UTF8")

            self.Data = {
                "text": {
                    "encoding": "utf8",     # 文本编码
                    "compress": "raw",      # 文本压缩格式
                    "format": "plain",      # 文本格式
                    "status": 2,            # 数据状态：0开始, 1中间, 2结束
                    "seq": 0,               # 数据序号
                    "text": encoded_text    # 待合成文本base64格式
                }
            }
        except Exception as e:
            print(f"文本编码失败: {e}")
            # 使用默认文本
            self.Data = {
                "text": {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 2,
                    "seq": 0,
                    "text": "5rWL6K+V5paH5pys"  # "测试文本"的base64编码
                }
            }


class AssembleHeaderException(Exception):
    def __init__(self, msg):
        self.message = msg


class Url:
    def __init__(this, host, path, schema):
        this.host = host
        this.path = path
        this.schema = schema
        pass


# calculate sha256 and encode to base64
def sha256base64(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    digest = base64.b64encode(sha256.digest()).decode(encoding='utf-8')
    return digest


def parse_url(requset_url):
    stidx = requset_url.index("://")
    host = requset_url[stidx + 3:]
    schema = requset_url[:stidx + 3]
    edidx = host.index("/")
    if edidx <= 0:
        raise AssembleHeaderException("invalid request url:" + requset_url)
    path = host[edidx:]
    host = host[:edidx]
    u = Url(host, path, schema)
    return u


# build websocket auth request url
def assemble_ws_auth_url(requset_url, method="GET", api_key="", api_secret=""):
    u = parse_url(requset_url)
    host = u.host
    path = u.path
    now = datetime.now()
    date = format_date_time(mktime(now.timetuple()))
    print(date)
    # date = "Thu, 12 Dec 2019 01:57:27 GMT"
    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
    # print(signature_origin)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    # print(authorization_origin)
    values = {
        "host": host,
        "date": date,
        "authorization": authorization
    }

    return requset_url + "?" + urlencode(values)

def on_message(ws, message):
    """处理WebSocket消息 - 修复为超拟人TTS格式"""
    try:
        print(f"收到原始消息: {message}")
        message = json.loads(message)

        # 超拟人TTS响应格式：header + payload
        header = message.get("header", {})
        payload = message.get("payload", {})

        code = header.get("code", 0)
        sid = header.get("sid", "")
        message_text = header.get("message", "")

        print(f"解析消息: code={code}, sid={sid}")

        if code != 0:
            print("sid:%s call error:%s code is:%s" % (sid, message_text, code))
            ws.close()
            return

        # 处理音频数据
        if "audio" in payload:
            audio_info = payload["audio"]
            audio_data = audio_info.get("audio", "")
            status = audio_info.get("status", 0)

            print(f"音频状态: {status}")

            if audio_data:
                try:
                    audio = base64.b64decode(audio_data)
                    with open('./demo.mp3', 'ab') as f:    # 这里文件后缀名，需要和业务参数audio.encoding 对应
                        f.write(audio)
                    print(f"写入音频数据: {len(audio)} bytes")
                except Exception as decode_e:
                    print(f"音频解码失败: {decode_e}")

            if status == 2:
                print("TTS合成完成，关闭连接")
                ws.close()
        else:
            print(f"收到非音频消息: {message}")

    except Exception as e:
        print("receive msg,but parse exception:", e)



# 收到websocket错误的处理
def on_error(ws, error):
    # return 0
    print("### error:", error)




# 收到websocket关闭的处理
def on_close(ws,ts,end):
    return 0
    # print("### closed ###")


# 收到websocket连接建立的处理 - 修复为超拟人TTS格式
def on_open(ws):
    def run(*args):
        # 超拟人TTS请求格式：header + parameter + payload
        d = {
            "header": wsParam.CommonArgs,
            "parameter": wsParam.BusinessArgs,
            "payload": wsParam.Data,
        }
        request_json = json.dumps(d)
        print("------>开始发送超拟人TTS文本数据")
        print(f"请求数据: {request_json[:200]}...")
        ws.send(request_json)

        # 清理之前的音频文件
        if os.path.exists('./demo.mp3'):
            os.remove('./demo.mp3')

    thread.start_new_thread(run, ())


if __name__ == "__main__":

    # 从控制台页面获取以下密钥信息，控制台地址：https://console.xfyun.cn/app/myapp
    appid = 'XXXXXXXX'
    apisecret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    apikey = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

    wsParam = Ws_Param(APPID=appid, APISecret=apisecret,
                       APIKey=apikey,
                       Text="全红婵，2007年3月28日出生于广东省湛江市，中国国家跳水队女运动员，主项为女子10米跳台。")
    websocket.enableTrace(False)
    # wsUrl = wsParam.create_url()
    requrl = 'wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6'
    wsUrl = assemble_ws_auth_url(requrl,"GET",apikey,apisecret)
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
